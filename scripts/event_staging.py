"""Keep event motion deterministic when authors combine poses and asynchronous moves."""
import re
from validate_event_coords import split_commands


def finish_motion(commands, pending=None, loops=None):
    pending = set() if pending is None else set(pending)
    loops = set() if loops is None else set(loops)
    result = []

    def wait_for_motion():
        # ProceedPosition is for NPCControllers (advancedMove), not a barrier for
        # ordinary move. It sets continueAfterMove=true even while stationary;
        # an ensuing implicit move can then run twice. Wait for controllers and
        # drain actorPositionsAfterMove using the game's explicit move barrier.
        result.extend(('waitForAllStationary', 'move false'))
        pending.clear()

    for raw in commands:
        t = raw.split()
        if not t:
            continue
        cmd = t[0].lower()
        if cmd == 'quickquestion' and '(break)' in raw:
            head, *branches = raw.split('(break)')
            fixed, next_pending, next_loops = [], set(), set()
            for branch in branches:
                parts, bp, bl = finish_motion(split_commands(branch.replace('\\', '/')), pending, loops)
                fixed.append('\\'.join(parts))
                next_pending.update(bp)
                next_loops.update(bl)
            raw = head + ''.join('(break)' + b for b in fixed)
            pending, loops = next_pending, next_loops
        elif cmd in ('move', 'advancedmove'):
            if cmd == 'move' and len(t) == 2:
                if t[1].lower() == 'false':
                    pending.clear()
                result.append(raw)
                continue
            actors = [t[1]] if cmd == 'advancedmove' else [t[i] for i in range(1, len(t) - 3, 4)]
            if pending.intersection(actors):
                wait_for_motion()
            for actor in actors:
                if actor in loops:
                    result.append('stopAnimation ' + actor)
                    loops.discard(actor)
            if cmd == 'advancedmove' or t[-1].lower() == 'true':
                pending.update(actors)
            elif t[-1].lower() != 'false':
                raw += ' false'
            if cmd == 'move' and raw.split()[-1].lower() == 'false':
                pending.clear()
        elif cmd == 'proceedposition':
            wait_for_motion()
            continue
        elif cmd in ('stopadvancedmoves', 'waitforallstationary'):
            pending.clear()
        elif cmd == 'halt':
            pending.clear()
        elif cmd == 'warp':
            if t[1] in pending:
                wait_for_motion()
        elif cmd in ('changelocation', 'changetotemporarymap'):
            if pending:
                wait_for_motion()
        elif cmd == 'animate':
            loops.discard(t[1])
            if t[3].lower() == 'true': loops.add(t[1])
        elif cmd == 'showframe':
            actor = 'farmer' if len(t) == 2 else t[1]
            if actor in loops:
                result.append('stopAnimation ' + actor)
            if actor == 'farmer': loops.add(actor)
        elif cmd == 'stopanimation':
            loops.discard(t[1])
        elif cmd == 'end':
            # Finish movement before fading/ending; don't leave a held pose on the player.
            if pending:
                wait_for_motion()
            result.extend('stopAnimation ' + actor for actor in sorted(loops))
            loops.clear()
        result.append(raw)
    return result, pending, loops


def stage_script(script):
    cmds = split_commands(script)
    has_header = len(cmds) >= 3 and re.fullmatch(r'-?\d+ -?\d+|\{\{HO_.*', cmds[1])
    if has_header:
        head, body = cmds[:3], cmds[3:]
        # Farm tokens already contain absolute coordinates for the selected map.
        if '{{HO_Farm' in cmds[2] and body[:1] != ['ignoreEventTileOffset']:
            body.insert(0, 'ignoreEventTileOffset')
    else:
        head, body = [], cmds
    body, _, _ = finish_motion(body)
    return '/'.join(head + body)
