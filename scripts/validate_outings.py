"""Проверить календарную интеграцию, собственные карты и доступность дверей/интерактивных мест."""
import json
from collections import deque
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image
from validate_event_coords import TileMap, strip_jsonc, MAP_FILES

ROOT = Path(__file__).resolve().parents[1]
GAME_MAPS = Path(r'D:\Games\Steam\steamapps\common\Stardew Valley\Content (unpacked)\Maps')
MAP_NAMES = {'HarveyCelebrationRoom', 'HarveyZuzuSquare', 'HarveyZuzuCafe',
             'HarveyZuzuBooks', 'HarveyZuzuCampus', 'HarveyZuzuInn'}
COMPANIONS = {'HarveyZuzuSquare': (18, 14), 'HarveyZuzuCafe': (13, 10),
              'HarveyZuzuBooks': (13, 10), 'HarveyZuzuCampus': (13, 10), 'HarveyZuzuInn': (13, 10)}


def read(path):
    return json.loads(strip_jsonc(path.read_text(encoding='utf-8-sig')), strict=False)


def merge(changes, target):
    result = {}
    for change in changes:
        if change.get('Target') == target:
            result.update(change.get('Entries', {}))
    return result


def reachable(tmap, start):
    assert tmap.problem(*start) is None, ('blocked arrival', start)
    visited, pending = {start}, deque([start])
    while pending:
        x, y = pending.popleft()
        for xy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if xy not in visited and tmap.problem(*xy) is None:
                visited.add(xy); pending.append(xy)
    return visited


def main():
    root = read(ROOT / 'content.json')
    changes = read(ROOT / 'assets/Code/outings.json')['Changes']
    includes = [change for change in root['Changes'] if change.get('FromFile') == 'assets/Code/outings.json']
    assert len(includes) == 1 and includes[0]['When']['HasMod'] == 'marilynsinister.HarveyOverhaul.Core'
    assert not any(change.get('Target', '').startswith(('Data/Events/Farm', 'Maps/Farm')) for change in changes)
    locations = merge(changes, 'Data/Locations')
    assert set(locations) == MAP_NAMES
    # Карты остаются в данных при выключении новых поездок: сохранение в гостинице остаётся читаемым.
    location_patch = next(change for change in changes if change.get('Target') == 'Data/Locations')
    assert 'When' not in location_patch
    maps = {name: TileMap(ROOT / 'assets/Maps' / (name + '.tmx')) for name in MAP_NAMES}
    graph = {name: set() for name in MAP_NAMES}
    paths = {}
    loads = {change.get('Target'): change.get('FromFile') for change in changes if change['Action'] == 'Load'}
    objects_checked = 0
    for name, data in locations.items():
        assert data['CreateOnLoad']['MapPath'] == 'Maps/' + name
        assert loads['Maps/' + name] == 'assets/Maps/' + name + '.tmx'
        tmap = maps[name]
        start = data['DefaultArrivalTile']
        paths[name] = reachable(tmap, (start['X'], start['Y']))
        if name in COMPANIONS:
            assert COMPANIONS[name] in paths[name], (name, 'unreachable companion')
        node = ET.parse(ROOT / loads['Maps/' + name]).getroot()
        sheet_ranges = []
        for sheet in node.findall('tileset'):
            image = sheet.find('image')
            source = image.get('source')
            asset = source.lstrip('.') if source.startswith('.') else source
            image_path = ROOT / 'assets/Maps' / source if source == 'outingSigns.png' else GAME_MAPS / asset
            assert image_path.is_file(), (name, source)
            width, height = Image.open(image_path).size
            assert (width, height) == (int(image.get('width')), int(image.get('height')))
            assert int(sheet.get('columns')) == width // 16
            count = width // 16 * (height // 16)
            assert int(sheet.get('tilecount')) == count
            first = int(sheet.get('firstgid'))
            sheet_ranges.append((first, first + count))
        sheet_ranges.sort()
        assert all(end <= following for (_, end), (following, _) in zip(sheet_ranges, sheet_ranges[1:])), name
        assert all(any(first <= gid < end for first, end in sheet_ranges)
                   for layer in tmap.layers.values() for gid in layer if gid), ('unknown tile', name)
        props = {prop.get('name'): prop.get('value') for prop in node.findall('./properties/property')}
        warp_tokens = props.get('Warp', '').split()
        assert len(warp_tokens) % 5 == 0
        for offset in range(0, len(warp_tokens), 5):
            x, y, target, tx, ty = warp_tokens[offset:offset+5]
            assert (int(x), int(y)) in paths[name], (name, 'unreachable exit', x, y)
            target_map = maps[target] if target in maps else TileMap(MAP_FILES[target])
            assert target_map.problem(int(tx), int(ty)) is None, (name, 'bad destination', target, tx, ty)
            graph[name].add(target)
        for group in node.findall('objectgroup'):
            for obj in group.findall('object'):
                action = next((prop.get('value') for prop in obj.findall('./properties/property') if prop.get('name') == 'Action'), '')
                if not action:
                    continue
                assert obj.get('name') == 'TileData', ('game parser ignores unnamed tile properties', name)
                x, y = int(obj.get('x'))//16, int(obj.get('y'))//16
                assert any(xy in paths[name] for xy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))), (name, action, 'unreachable')
                if action.startswith('Shop '):
                    assert action.removeprefix('Shop ').replace('marilynsinister.HarveyOverhaul', '{{ModId}}') in merge(changes, 'Data/Shops')
                else:
                    assert action.startswith('HarveyOuting '), action
                    place = action.split()[1]
                    if place not in ('Sleep', 'Return'):
                        assert 'Place_'+place in merge(changes, 'Mods/{{ModId}}/Outings')
                objects_checked += 1
    for start in MAP_NAMES:
        pending, visited, escaped = [start], set(), False
        while pending:
            name = pending.pop()
            if name in ('BusStop', 'Hospital'):
                escaped = True; break
            if name not in visited:
                visited.add(name); pending.extend(graph[name])
        assert escaped, ('no return path', start)

    events = [(change, key, body) for change in changes if change.get('Target', '').startswith('Data/Events/')
              for key, body in change['Entries'].items()]
    assert len(events) == 19
    ids = {key.split('/')[0] for _, key, _ in events}
    assert len(ids) == 14
    # Поездка на день рождения Харви (выезд 13 зимы): свой вечер и утро вместо Z5/Z6; сцены второй поездки — после первой.
    his_birthday = 'PLAYER_HAS_MAIL Current HarveyZuzu_HisBirthday Received'
    for _, key, _ in events:
        eid = key.split('/')[0]
        if eid.startswith('HarveyOverhaulZuzu.ZB'):
            assert his_birthday in key and '!' + his_birthday not in key, eid
        if eid in ('HarveyOverhaulZuzu.Z5_HotelEvening', 'HarveyOverhaulZuzu.Z6_SundayMorning', 'HarveyOverhaulZuzu.Z11_Rooftop'):
            assert '!' + his_birthday in key, eid
        if eid in ('HarveyOverhaulZuzu.Z8_Familiar', 'HarveyOverhaulZuzu.Z9_Regulars',
                   'HarveyOverhaulZuzu.Z10_Lecture', 'HarveyOverhaulZuzu.Z11_Rooftop'):
            assert 'PLAYER_HAS_MAIL Current HarveyZuzu_Visited Received' in key, eid
    for change, key, body in events:
        assert change['Target'].removeprefix('Data/Events/') in MAP_NAMES
        assert 'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married' in key
        if key.startswith('HarveyOverhaulBirthday.'):
            assert 'PLAYER_HAS_MAIL Current HarveyBirthday_Pending Received' in key
            assert 'marilynsinister.HarveyOverhaul.Core_BirthdayComplete' in body.split('/')[4]
            assert 'AddItem (O)221 1' in body.split('/')[4]
        else:
            assert 'PLAYER_HAS_MAIL Current HarveyZuzu_Active Received' in key
        setup = body.split('/')[2].split()
        points = [(int(setup[n+1]), int(setup[n+2])) for n in range(0, len(setup), 4)]
        assert len(set(points)) == len(points), (key, 'overlapping actors')
        assert all(point in paths[change['Target'].split('/')[-1]] for point in points), key
    birthday = [change for change, key, _ in events if key.startswith('HarveyOverhaulBirthday.')]
    assert len(birthday) == 5
    imported = [change for change in changes if 'Omegasis.HappyBirthday/IsPlayersBirthday' in str(change)]
    assert len(imported) == 1
    assert imported[0]['When']['HasMod'] == 'Omegasis.HappyBirthday'
    assert imported[0]['When']['HasValue:{{Omegasis.HappyBirthday/IsPlayersBirthday}}'] == 'true'
    deps = read(ROOT/'manifest.json')['Dependencies']
    assert any(dep['UniqueID'] == 'Omegasis.HappyBirthday' and dep['IsRequired'] is False for dep in deps)
    journal = merge(read(ROOT/'assets/Code/storyJournal.json')['Changes'],
                    'Mods/marilynsinister.HarveyOverhaul/StoryJournal')
    journal_ids = {event for entry in journal.values() for event in entry['EventIds'].split()}
    assert ids <= journal_ids
    print(f'Outings: all checks passed. {len(maps)} maps, {len(events)} scene variants, {objects_checked} reachable interactions.')


if __name__ == '__main__':
    main()
