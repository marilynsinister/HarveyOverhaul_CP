"""Проверка кадров, высоты стоячих анимаций и точек расписания Аренда.

Можно передать путь к другому CP-паку (например, установленному).
Карты читаются из установленной игры; сохранения не изменяются.
"""
from collections import deque
import json
from pathlib import Path
import sys

from PIL import Image
from validate_event_coords import MAP_FILES, UNPACKED, SVE, load_path, strip_jsonc

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
STANDING = {'arend_read', 'arend_tea', 'arend_birds', 'arend_think'}
EMPTY_FRAMES = set()


def read(relative):
    return json.loads(strip_jsonc((ROOT / relative).read_text(encoding='utf-8-sig')), strict=False)


def frames(description):
    parts = description.split('/')
    assert len(parts) == 3
    return [int(n) for part in parts for n in part.split()]


def main():
    data = read('assets/Code/arend.json')
    animations = next(c['Entries'] for c in data['Changes'] if c.get('Target') == 'Data/animationDescriptions')
    schedule = read('assets/Code/dialogues/arend_schedule.json')
    sprite = Image.open(ROOT / 'assets/Character/Arend/Sprite.png').convert('RGBA')
    winter = Image.open(ROOT / 'assets/Character/Arend/Sprite_Winter.png').convert('RGBA')
    assert sprite.size == winter.size == (64, 704)
    assert sprite.tobytes() == winter.tobytes(), 'Winter uses the same reviewed frame layout'
    boxes = [sprite.crop(((i % 4) * 16, (i // 4) * 32, (i % 4 + 1) * 16, (i // 4 + 1) * 32)).getbbox()
             for i in range(88)]
    assert {i for i, box in enumerate(boxes) if box is None} == EMPTY_FRAMES, 'Every reviewed cell, including the cup return in 51, must be populated'
    for i in range(16):
        assert boxes[i] and 29 <= boxes[i][3] - boxes[i][1] <= 31 and boxes[i][3] == 32, ('walking', i, boxes[i])
    for start in (0, 8):
        cycle = [sprite.crop((c * 16, start // 4 * 32, c * 16 + 16, start // 4 * 32 + 32)) for c in range(4)]
        assert cycle[0].tobytes() == cycle[2].tobytes(), ('Contact pose must return without sideways drift', start)
        for phase in (1, 3):
            assert cycle[phase].crop((0, 0, 16, 13)).tobytes() == cycle[0].crop((0, 1, 16, 14)).tobytes(), ('Head must rise one pixel without moving sideways', start, phase)
            assert cycle[phase].crop((3, 14, 12, 20)).tobytes() == cycle[0].crop((3, 15, 12, 21)).tobytes(), ('Shoulders must follow the step', start, phase)
        assert len({f.crop((0, 24, 16, 32)).tobytes() for f in cycle}) == 3, ('Need contact and two distinct steps', start)
        floors = [[f.crop((x0, 24, x1, 32)).getbbox()[3] for x0, x1 in ((2, 7), (8, 13))] for f in cycle]
        assert floors == [[8, 8], [8, 6], [8, 8], [6, 8]], ('Need two opposite planted/lifted boot poses', start, floors)
        for f in cycle:
            for y in range(26, 32):
                for x in (7,):
                    pixel = f.getpixel((x, y))
                    assert pixel[3] == 255 and max(pixel[:3]) <= 31, ('Need a dark seam, not a wide transparent slot', start, x, y)
            assert all(f.getpixel((x, 19))[3] for x in (1, 13)), ('Sleeves must stay connected during arm swing', start)
        left = cycle[1].crop((0, 24, 15, 32)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        assert left.tobytes() == cycle[3].crop((0, 24, 15, 32)).tobytes(), ('Steps must be mirrored about the body centre', start)
    for i in list(range(16, 40)) + list(range(44, 64)) + list(range(68, 88)):
        assert boxes[i] and boxes[i][1] in (1, 2, 3) and boxes[i][3] == 32, ('Full standing figure', i, boxes[i])
        for x0, x1 in ((2, 7), (8, 13)):
            foot = sprite.crop((i % 4 * 16 + x0, i // 4 * 32 + 30, i % 4 * 16 + x1, i // 4 * 32 + 32))
            assert foot.getbbox(), ('Missing shoe', i, x0)
    def cell(index):
        return sprite.crop((index % 4 * 16, index // 4 * 32, index % 4 * 16 + 16, index // 4 * 32 + 32))
    for index in list(range(16, 40)) + list(range(44, 64)) + list(range(68, 88)):
        legs = cell(index).crop((0, 24, 15, 32))
        assert legs.tobytes() == legs.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), ('Neutral legs must be centred and symmetrical', index)
    for start in (40, 44, 48, 52):
        cycle = [cell(i) for i in range(start, start + 4)]
        head_bottom = 12 if start in (44, 48) else 14
        assert len({f.crop((0, 0, 16, head_bottom)).tobytes() for f in cycle}) == 1, ('Head/facing must stay anchored', start)
        assert len({f.crop((0, 24, 16, 32)).tobytes() for f in cycle}) == 1, ('Feet and shoes must not change', start)
    for start in (24, 28, 32, 36):
        assert len({cell(i).crop((0, 24, 16, 32)).tobytes() for i in range(start, start + 4)}) == 1, ('Idle/action must keep both feet anchored', start)
    for start in (36, 68):
        assert len({cell(i).tobytes() for i in range(start, start + 4)}) >= 3, ('Breathing needs rest, inhale and exhale', start)
        for i in range(start, start + 4):
            assert cell(i).crop((0, 0, 16, 17)).tobytes() == cell(start).crop((0, 0, 16, 17)).tobytes(), ('Breathing must keep head, neck and collar fixed', i)
            assert cell(i).crop((0, 22, 16, 32)).tobytes() == cell(start).crop((0, 22, 16, 32)).tobytes(), ('Breathing must keep hands and pelvis fixed', i)
            assert cell(i).getchannel('A').tobytes() == cell(start).getchannel('A').tobytes(), ('Breathing must not thin the arms or change the outline', i)
    assert len({cell(i).tobytes() for i in (28, 56, 57, 29, 58, 30, 59)}) == 7, 'Seven distinct page phases'
    page_frames = (28, 56, 57, 29, 58, 30, 59, 31)
    for index in tuple(range(24, 28)) + page_frames:
        assert cell(index).crop((0, 18, 16, 32)).tobytes() == cell(28).crop((0, 18, 16, 32)).tobytes(), ('Page must stay hidden behind the original front cover; hands/body cannot change', index)
        changed = [(x, y) for y in range(32) for x in range(16) if cell(index).getpixel((x, y)) != cell(28).getpixel((x, y))]
        assert all(4 <= x <= 10 and 15 <= y < 18 for x, y in changed), ('Only the turning page may differ from the preferred reader pose', index)
    for index in range(41, 44):
        a, b = cell(40), cell(index)
        changed = [(x, y) for y in range(32) for x in range(16) if a.getpixel((x, y)) != b.getpixel((x, y))]
        assert all(4 <= x < 12 and 18 <= y < 24 for x, y in changed), ('Chair must remain fixed; only hands may move', index)
    for index in range(64, 68):
        for y in range(14, 32):
            for x in range(16):
                if y >= 24 or x < 2 or x >= 14:
                    assert cell(index).getpixel((x, y)) == cell(40).getpixel((x, y)), ('Furniture must remain fixed during entry/exit', index, x, y)
    cup_shape = ('CCCCC..', 'CSSSCCC', 'CSSSC.C', 'CSSSCCC', '.SSSS..')
    for index, cup_y in zip((44, 60, 61, 45, 62, 63, 46, 47), (18, 17, 16, 15, 14, 13, 12, 15)):
        for y, row in enumerate(cup_shape):
            for x, char in enumerate(row):
                if char != '.':
                    assert cell(index).getpixel((4 + x, cup_y + y)) == cell(44).getpixel((4 + x, 18 + y)), ('The same cup must move from chest to mouth', index)
    for index, cup_y in zip(range(48, 52), (18, 17, 16, 17)):
        for y, row in enumerate(cup_shape):
            for x, char in enumerate(row):
                if char != '.':
                    assert cell(index).getpixel((4 + x, cup_y + y)) == cell(44).getpixel((4 + x, 18 + y)), ('Cup must stay visible during the small two-handed lift', index)
    allowed = {
        'arend_read': set(range(28, 32)) | set(range(56, 60)),
        'arend_armchair': set(range(40, 44)) | set(range(64, 68)),
        'arend_tea': set(range(44, 48)) | set(range(60, 64)),
        'arend_birds': set(range(68, 72)),
        'arend_think': set(range(32, 36)) | set(range(72, 76)),
    }
    for name, description in animations.items():
        used = frames(description)
        assert set(used) <= allowed[name], (name, 'Incoherent facing/action in schedule cycle', used)
        assert all(0 <= i < len(boxes) and boxes[i] is not None for i in used), (name, used)
        if name in STANDING:
            heights = [boxes[i][3] - boxes[i][1] for i in used]
            assert min(heights) >= 29 and max(heights) - min(heights) <= 1, (name, heights)
            assert all(boxes[i][3] == 32 for i in used), (name, 'feet must stay on the same floor line')
        elif name == 'arend_armchair':
            assert {int(n) for n in description.split('/')[1].split()} <= {40, 41, 42, 43}
            assert set(used) & set(range(64, 68)), 'Use intermediate poses for entry/exit'
    assert set(animations) == STANDING | {'arend_armchair'}
    bird_frames = frames(animations['arend_birds'])
    assert len({cell(i).tobytes() for i in bird_frames}) >= 3, 'Bird watching must include subtle chest breathing'
    assert len({cell(i).tobytes() for i in frames(animations['arend_think'])}) >= 7, 'Thinking needs gradual hand movement'
    for sequence in ((16, 76, 17, 77, 18, 78, 19, 79), (20, 80, 23, 21, 81, 82, 83, 22), (32, 72, 73, 33, 74, 75, 34, 35), (52, 84, 53, 85, 54, 86, 55, 87)):
        assert len({cell(i).tobytes() for i in sequence}) >= (5 if sequence[0] == 52 else 7), ('Articulated gesture needs intermediate hand positions', sequence)
        assert len({cell(i).crop((0, 24, 16, 32)).tobytes() for i in sequence}) == 1, ('Gestures must not move the legs', sequence)
        for i in sequence:
            opaque = {(x, y) for y in range(32) for x in range(16) if cell(i).getpixel((x, y))[3]}
            seen, pending = set(), [next(iter(opaque))]
            while pending:
                point = pending.pop()
                if point in seen:
                    continue
                seen.add(point)
                x, y = point
                pending.extend(p for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)) if p in opaque and p not in seen)
            assert seen == opaque, ('Detached hand or broken sleeve', i, opaque - seen)

    maps = {name: [(name, load_path(MAP_FILES[name]))] for name in ('Hospital', 'Town', 'Forest', 'Beach')}
    maps['HarveyRoom'] = [
        ('vanilla', load_path(str(Path(UNPACKED) / 'HarveyRoom.tmx'))),
        ('SVE', load_path(str(Path(SVE) / 'Locations/HarveyRoom.tbin'))),
    ]
    points = {}
    stops = 0
    for day, route in schedule.items():
        previous_time = 0
        for stop in route.split('/'):
            time, location, x, y, direction, *behavior = stop.split()
            time, x, y, direction = int(time), int(x), int(y), int(direction)
            assert time > previous_time and 0 <= time % 100 < 60, (day, stop)
            previous_time = time
            assert direction in range(4)
            assert location in maps, (day, location)
            for label, tile_map in maps[location]:
                assert tile_map is not None, ('Missing map', location, label)
                assert tile_map.problem(x, y) is None, (day, stop, label, tile_map.problem(x, y))
            if behavior:
                assert len(behavior) == 1 and behavior[0] in animations
                assert (behavior[0] == 'arend_armchair') == (location == 'HarveyRoom'), (day, stop)
            points.setdefault(location, set()).add((x, y))
            stops += 1
        assert location == 'HarveyRoom', (day, 'NPC must return home')

    # Все точки на одной карте должны сообщаться: стоять на свободном тайле
    # недостаточно, если он отрезан от другой точки маршрута стеной.
    for location, destinations in points.items():
        for label, tile_map in maps[location]:
            origin = next(iter(destinations))
            visited, queue = {origin}, deque([origin])
            while queue:
                x, y = queue.popleft()
                for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if point not in visited and tile_map.problem(*point) is None:
                        visited.add(point)
                        queue.append(point)
            assert destinations <= visited, (location, label, 'Disconnected schedule stops', destinations - visited)
    print(f'Arend behaviour: all checks passed. 88 frames, {len(animations)} animations, {stops} schedule stops.')


if __name__ == '__main__':
    main()
