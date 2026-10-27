"""Walk every included event, including answer branches and inherited forks.

Uses the installed SVE/Alchemistry maps, all three Off The Clock room variants,
and farm/house variants from validate_event_coords. This is static staging QA;
save-specific furniture, live NPC schedules and animation timing need in-game QA.
Run: python scripts/validate_event_staging.py [Mods directory] [--report path]
"""
from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path
import re
import shlex
import sys
from PIL import Image

import validate_event_coords as c

ROOT = Path(c.CP_ROOT)
MODS = Path(c.MODS)
SVE = Path(c.SVE)
GAME = MODS.parent
# DefaultCommands reflected from the installed Stardew Valley assembly. Custom
# event commands must be registered here; CP/i18n command fragments expand later.
KNOWN_COMMANDS = {name.lower() for name in (Path(__file__).with_name('event_commands.txt'))
                  .read_text(encoding='utf-8-sig').splitlines() if name.strip()}
c.MAP_FILES.update({
    'Custom_SpriteSpring2': str(SVE / 'NewLocations/SpriteSpring2.tmx'),
    'Custom_ShearwaterBridge': str(SVE / 'NewLocations/ShearwaterBridge.tbin'),
    'Custom_GrampletonFields_Small': str(SVE / 'NewLocations/GrampletonFields_Small.tbin'),
    'Saloon': str(SVE / 'Locations/Saloon.tbin'),
    'SeedShop': str(SVE / 'Locations/SeedShop.tbin'),
    'HarveyRoom': str(SVE / 'Locations/HarveyRoom.tbin'),
})
for name in ('SeedShop', 'HarveyRoom'):
    if not Path(c.MAP_FILES[name]).exists():
        c.MAP_FILES[name] = str(GAME / 'Content (unpacked)/Maps' / (name + '.tmx'))


def variants(location, fname, eid):
    if location == 'HarveyRoom':
        folder = MODS / 'Harvey - Off The Clock 1.0.0/assets/maps'
        rooms = [(f'Off The Clock SVE {i}', c.load_path(str(folder / f'HarveyRoomSVE{i}.tmx')), {})
                 for i in range(1, 4)]
        return [('', c.load_map(location), {}), *rooms]
    return c.map_variants(location, fname, eid)


def words(raw):
    # POSIX shlex would consume event branch backslashes; those are split first.
    return shlex.split(raw, posix=False)


def header(cmds):
    return (len(cmds) >= 3 and re.fullmatch(r'-?\d+ -?\d+', cmds[1]) is not None
            and re.fullmatch(r'(?:\S+ -?\d+ -?\d+ [0-3](?: |$))+', cmds[2]) is not None)


def split_branch(raw):
    # Backslash is a command separator only outside dialogue quotes.
    return c.split_commands(raw.replace('\\', '/'))


def fork_ids(entries):
    return {t[1] for _, _, _, s in entries for cmd in c.split_commands(s)
            for piece in re.split(r'\(break\)|\\', cmd)
            if len(t := piece.split()) >= 2 and t[0].lower() in ('fork', 'switchevent')}


class Audit:
    def __init__(self, entries):
        self.entries = entries
        self.forks = fork_ids(entries)
        self.by_id = {(loc, key.split('/')[0]): s for _, loc, key, s in entries}
        self.issues = set()
        self.coverage = Counter()
        self.maps = set()
        self.sprite_cache = {}
        self.fn = self.eid = self.label = ''

    def issue(self, kind, raw, detail):
        self.issues.add((self.fn, self.eid, self.label, kind, raw[:130], detail))

    def check_frame(self, who, frame, raw):
        if who.startswith('farmer'):
            return  # FarmerSprite has its own frame layout, unlike the NPC 16x32 grid.
        if who not in self.sprite_cache:
            paths = [GAME / 'Content (unpacked)/Characters' / (who + '.png')]
            if who == 'Harvey':
                paths += [GAME / 'Content (unpacked)/Characters/Harvey_Winter.png',
                          ROOT.parent / 'HarveyWhiteCoat [CP]/assets/Harvey_WhiteCoat.png']
            elif who == 'Arend':
                paths += [ROOT / 'assets/Character/Arend/Sprite.png']
            self.sprite_cache[who] = [(p, Image.open(p).convert('RGBA')) for p in paths if p.is_file()]
        for path, img in self.sprite_cache[who]:
            cols = img.width // 16
            if frame < 0 or frame >= cols * (img.height // 32):
                self.issue('FRAME', raw, f'{who} frame {frame} is outside {path.name}')
            elif img.crop((frame % cols * 16, frame // cols * 32,
                           frame % cols * 16 + 16, frame // cols * 32 + 32)).getchannel('A').getbbox() is None:
                self.issue('FRAME', raw, f'{who} frame {frame} is transparent in {path.name}')

    def check_overlap(self, st, raw):
        positions = {}
        for who, (x, y) in st['actors'].items():
            if min(x, y) < 0 or max(x, y) >= c.OFFSCREEN:
                continue
            ox, oy = st['offset'].get(who, (0, 0))
            point = (x * 64 + ox, y * 64 + oy)
            if point in positions:
                self.issue('OVERLAP', raw, f'{who} and {positions[point]} share {point} @ {st["loc"]}')
            positions[point] = who

    def map_for(self, state):
        if state['loc'] == state['origin']:
            return state['map']
        return variants(state['loc'], self.fn, self.eid)[0][1]

    def check_tile(self, state, who, xy, raw, posed=False, walking=False):
        x, y = xy
        if min(x, y) < 0 or max(x, y) >= c.OFFSCREEN:
            return
        tmap = self.map_for(state)
        self.maps.add(state['loc'])
        if tmap is None:
            self.issue('MAP', raw, f"No map for {state['loc']}")
            return
        problem = tmap.problem(math.floor(x), math.floor(y))
        if problem and not (posed or (not walking and who in state['ignore'] and 'Buildings' in problem)):
            self.issue('TILE', raw, f"{who} {xy} @ {state['loc']}: {problem}")

    def move(self, st, who, dx, dy, raw):
        if who not in st['actors']:
            self.issue('ACTOR', raw, f'{who} not declared')
            return
        if who in st['pending']:
            self.issue('RACE', raw, f'{who}: previous asynchronous movement has no completion barrier')
        if who in st['loop']:
            self.issue('POSE', raw, f'{who} moves with an active looping animation')
        if st['offset'].get(who, (0, 0)) != (0, 0):
            self.issue('OFFSET', raw, f"{who} moves with pixel offset {st['offset'][who]}")
        x, y = st['actors'][who]
        if min(x, y) < 0 or max(x, y) >= c.OFFSCREEN:
            return
        if dx and dy:
            self.issue('AXIS', raw, 'move must have one zero component')
        for sx, sy, count in (((dx > 0) - (dx < 0), 0, abs(dx)), (0, (dy > 0) - (dy < 0), abs(dy))):
            for _ in range(count):
                x, y = x + sx, y + sy
                self.check_tile(st, who, (x, y), raw, walking=True)
        st['actors'][who] = (x, y)

    def run_commands(self, commands, state, stack=()):
        states = [state]
        for ix, raw in enumerate(commands):
            if not raw:
                continue
            out = []
            for st in states:
                t = words(raw)
                if not t:
                    continue
                cmd = t[0].lower()
                self.coverage[cmd] += 1
                # Animate advances immediately in the game, even when loop=false.
                # Catch replacements before a pause or player-controlled dialogue can show it.
                if cmd in ('animate', 'showframe', 'stopanimation'):
                    who = 'farmer' if cmd == 'showframe' and len(t) == 2 else t[1]
                    if who in st['animation']:
                        remaining, source = st['animation'][who]
                        self.issue('TIMING', raw, f'{who}: {source} still needs {remaining} ms')
                    st['animation'].pop(who, None)
                if cmd in ('speak', 'message', 'quickquestion', 'question'):
                    # Reading/answer time is unknown; don't guess a dialogue duration.
                    st['animation'].clear()
                elif cmd in ('pause', 'precisepause') and len(t) > 1 and t[1].isdigit():
                    elapsed = int(t[1])
                    st['animation'] = {who: (left - elapsed, source)
                                       for who, (left, source) in st['animation'].items() if left > elapsed}
                if cmd in ('speak', 'message', 'quickquestion'):
                    self.check_overlap(st, raw)
                if cmd in ('speak', 'emote', 'animate', 'facedirection', 'stopanimation', 'positionoffset', 'speed') and len(t) > 1:
                    if t[1] not in st['actors'] and not t[1].startswith('farmer'):
                        self.issue('ACTOR', raw, f'{t[1]} not declared')
                if cmd not in KNOWN_COMMANDS and not cmd.startswith('{{'):
                    self.issue('COMMAND', raw, f'Unknown event command: {t[0]}')
                if cmd == 'quickquestion' and '(break)' in raw:
                    head, *branches = raw.split('(break)')
                    if len(head.split('#')) - 1 != len(branches):
                        self.issue('BRANCH', raw, 'Answer and branch counts differ')
                    for branch in branches:
                        out.extend(self.run_commands(split_branch(branch), deepcopy(st), stack))
                    continue
                if cmd in ('fork', 'switchevent'):
                    ref = t[1]
                    body = self.by_id.get((st['origin'], ref))
                    if body is None:
                        self.issue('FORK', raw, f'Unresolved {ref}')
                    elif ref not in stack:
                        self.run_commands(c.split_commands(body), deepcopy(st), (*stack, ref))
                    # fork is conditional; the non-fork path continues here.
                    if cmd == 'switchevent':
                        continue
                try:
                    if cmd in ('changelocation', 'changetotemporarymap'):
                        if st['pending']:
                            self.issue('RACE', raw, 'Changing maps with unfinished movement')
                        st['loc'] = t[1]
                    elif cmd == 'ignorecollisions':
                        st['ignore'].add(t[1])
                    elif cmd == 'addtemporaryactor':
                        who = t[9] if len(t) > 9 else t[1]
                        st['actors'][who] = (int(t[4]), int(t[5]))
                        self.check_tile(st, who, st['actors'][who], raw)
                    elif cmd == 'warp':
                        who = t[1]
                        if who in st['pending']:
                            self.issue('RACE', raw, f'{who}: warp does not clear the ordinary move target')
                        if who not in st['actors']:
                            self.issue('ACTOR', raw, f'{who} not declared')
                        st['actors'][who] = (int(t[2]), int(t[3]))
                        st['offset'][who] = (0, 0)
                        st['pending'].discard(who)
                        self.check_tile(st, who, st['actors'][who], raw,
                                        c.is_posed_after(commands, ix, who))
                    elif cmd == 'move':
                        body = t[1:]
                        if len(body) == 1 and body[0].lower() in ('true', 'false'):
                            st['continue_move'] = body[0].lower() == 'true'
                            if not st['continue_move']:
                                st['pending'].clear()
                            out.append(st)
                            continue
                        async_move = body[-1].lower() == 'true'
                        explicit_mode = body[-1].lower() in ('true', 'false')
                        if not explicit_mode and st['continue_move']:
                            self.issue('MOTION', raw, 'Implicit move inherits continueAfterMove=true and can repeat or advance early')
                        if body[-1].lower() in ('true', 'false'):
                            body = body[:-1]
                        if len(body) % 4:
                            self.issue('SYNTAX', raw, 'move requires actor dx dy facing groups')
                        for i in range(0, len(body) - 3, 4):
                            self.move(st, body[i], int(body[i+1]), int(body[i+2]), raw)
                            if async_move:
                                st['pending'].add(body[i])
                        if explicit_mode:
                            st['continue_move'] = async_move
                        if not async_move:
                            st['pending'].clear()
                            st['continue_move'] = False
                    elif cmd == 'advancedmove':
                        who = t[1]
                        for i in range(3, len(t) - 1, 2):
                            dx, dy = int(t[i]), int(t[i+1])
                            if dx and dy:  # facing + pause in ms
                                continue
                            self.move(st, who, dx, dy, raw)
                        st['pending'].add(who)
                    elif cmd == 'proceedposition':
                        self.issue('MOTION', raw, 'ProceedPosition sets continueAfterMove=true; use move false for ordinary movement')
                        st['continue_move'] = True
                    elif cmd in ('waitforallstationary', 'stopadvancedmoves'):
                        st['pending'].clear()
                    elif cmd == 'halt':
                        st['pending'].clear()
                        st['continue_move'] = False
                    elif cmd == 'positionoffset':
                        old = st['offset'].get(t[1], (0, 0))
                        st['offset'][t[1]] = (old[0] + int(t[2]), old[1] + int(t[3]))
                    elif cmd == 'animate':
                        if len(t) < 6 or any(v.lower() not in ('true', 'false') for v in t[2:4]):
                            self.issue('SYNTAX', raw, 'animate actor flip loop duration frames')
                        elif t[3].lower() == 'true':
                            st['loop'].add(t[1])
                        else:
                            st['loop'].discard(t[1])
                            st['animation'][t[1]] = (int(t[4]) * len(t[5:]), raw)
                        for frame in t[5:]:
                            self.check_frame(t[1], int(frame), raw)
                    elif cmd == 'showframe':
                        who, frame = ('farmer', t[1]) if len(t) == 2 else (t[1], t[2])
                        if who in st['loop']:
                            self.issue('POSE', raw, f'{who}: showFrame does not stop the previous looping animation')
                        if not re.fullmatch(r'\d+', frame):
                            self.issue('SYNTAX', raw, 'Expected numeric frame before optional flip')
                        elif who == 'farmer':
                            st['loop'].add(who)
                        if frame.isdigit():
                            self.check_frame(who, int(frame), raw)
                    elif cmd == 'stopanimation':
                        st['loop'].discard(t[1])
                        if len(t) > 2:
                            self.check_frame(t[1], int(t[2]), raw)
                    elif cmd == 'end':
                        if st['pending']:
                            self.issue('RACE', raw, f'Exit before movement completes: {sorted(st["pending"])}')
                        if any(who.startswith('farmer') for who in st['loop']):
                            self.issue('POSE', raw, 'Player still has a held animation at the exit')
                        if len(t) >= 4 and t[1].lower() == 'position':
                            # end position changes positionBeforeEvent, on the
                            # original return map, not the last cutscene map.
                            exit_state = {**st, 'loc': st['origin']}
                            self.check_tile(exit_state, 'farmer', (int(t[2]), int(t[3])), raw,
                                            # Existing hospital bed exits are intentional poses.
                                            st['origin'] == 'Hospital' and t[2:4] == ['20', '5'])
                        continue
                except (ValueError, IndexError) as exc:
                    self.issue('SYNTAX', raw, str(exc))
                out.append(st)
            # Dialogue-only choices need not multiply every later check.
            states = list({repr((s['loc'], s['actors'], s['ignore'], s['offset'], s['loop'], s['pending'], s['animation'], s['continue_move'])): s
                           for s in out}.values())
            if not states:
                break
        return states

    def run(self):
        for fn, loc, key, script in self.entries:
            eid = key.split('/')[0]
            if eid in self.forks:
                continue
            self.fn, self.eid = fn, eid
            for label, tmap, tokens in variants(loc, fn, eid):
                self.label = label
                cmds = c.split_commands(c.apply_tokens(script, tokens))
                if not header(cmds):
                    self.issue('HEADER', '/'.join(cmds[:3]), 'Expected music/view/actor setup')
                    continue
                if '{{HO_Farm' in script and 'ignoreEventTileOffset' not in cmds[3:]:
                    self.issue('OFFSET', 'setup', 'Absolute farm tokens require ignoreEventTileOffset')
                if tmap is None:
                    self.issue('MAP', '', f'No map for {loc}')
                st = dict(loc=loc, origin=loc, map=tmap, actors={}, ignore=set(), offset={}, loop=set(), pending=set(), animation={}, continue_move=False)
                setup = cmds[2].split()
                for i in range(0, len(setup), 4):
                    who, x, y = setup[i], int(setup[i+1]), int(setup[i+2])
                    st['actors'][who] = (x, y)
                    self.check_tile(st, who, (x, y), 'setup')
                self.run_commands(cmds[3:], st)
        return sorted(self.issues)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    audit = Audit(list(c.iter_event_entries()))
    issues = audit.run()
    lines = [f'{fn} | {eid} [{label}] | {kind} | {raw} | {detail}'
             for fn, eid, label, kind, raw, detail in issues]
    if '--report' in sys.argv:
        path = Path(sys.argv[sys.argv.index('--report') + 1])
        path.write_text('\n'.join(lines), encoding='utf-8')
    else:
        print('\n'.join(lines))
    print(f'Events: {len(audit.entries)}; inherited forks: {len(audit.forks)}; maps: {len(audit.maps)}; issues: {len(issues)}')
    print(dict(Counter(row[3] for row in issues)))
    return int(bool(issues))


if __name__ == '__main__':
    sys.exit(main())
