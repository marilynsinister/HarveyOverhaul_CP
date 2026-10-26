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
TRUNCATED = set(range(24, 28)) | set(range(36, 40)) | set(range(48, 56))


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
    assert sprite.size == winter.size == (64, 448)
    assert sprite.tobytes() == winter.tobytes(), 'Winter uses the same reviewed frame layout'
    boxes = [sprite.crop(((i % 4) * 16, (i // 4) * 32, (i % 4 + 1) * 16, (i // 4 + 1) * 32)).getbbox()
             for i in range(56)]
    for i in range(16):
        assert boxes[i] and 29 <= boxes[i][3] - boxes[i][1] <= 31 and boxes[i][3] == 32, ('walking', i, boxes[i])
    for name, description in animations.items():
        used = frames(description)
        assert all(0 <= i < len(boxes) and boxes[i] is not None for i in used), (name, used)
        if name in STANDING:
            assert not set(used) & TRUNCATED, (name, 'cropped torso in a standing animation')
            heights = [boxes[i][3] - boxes[i][1] for i in used]
            assert min(heights) >= 29 and max(heights) - min(heights) <= 1, (name, heights)
            assert all(boxes[i][3] == 32 for i in used), (name, 'feet must stay on the same floor line')
        elif name == 'arend_armchair':
            assert {int(n) for n in description.split('/')[1].split()} <= {40, 41, 42, 43}
            assert boxes[used[-1]][3] - boxes[used[-1]][1] >= 29, 'Stand up before leaving the armchair'
    assert set(animations) == STANDING | {'arend_armchair'}

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
    print(f'Arend behaviour: all checks passed. 56 frames, {len(animations)} animations, {stops} schedule stops.')


if __name__ == '__main__':
    main()
