"""Отдельные карты для праздника и района Зузу из штатных игровых тайлов.

Не копирует и не патчит Farm/FarmHouse. Геометрия, двери и декор принадлежат
только этому паку. PNG в art — превью TMX, а не игровые ресурсы.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
from collections import deque

ROOT = Path(__file__).resolve().parents[1]
GAME_MAPS = Path(r'D:\Games\Steam\steamapps\common\Stardew Valley\Content (unpacked)\Maps')
OUT = ROOT / 'assets/Maps'
PREVIEW = ROOT / 'art/outings'
SHEETS = {
    'town': (1, 'spring_town', 32),
    'inside': (10001, 'townInterior', 32),
    'objects': (20001, '../Maps/springobjects', 24),
    'walls': (40001, 'walls_and_floors', 16),
    'signs': (60001, 'outingSigns', 16),
}


class Map:
    def __init__(self, name, width, height, outside=False):
        self.name, self.width, self.height = name, width, height
        self.layers = {key: [0] * (width * height) for key in ('Back', 'Buildings', 'Front', 'AlwaysFront')}
        self.properties = {'Outdoors': 'T'} if outside else {'Light': '4 12 8'}
        self.actions = {}
        self.passable = set()
        self.warps = []

    def tile(self, layer, x, y, sheet, index):
        assert 0 <= x < self.width and 0 <= y < self.height
        self.layers[layer][y * self.width + x] = SHEETS[sheet][0] + index

    def clear(self, layer, x, y):
        self.layers[layer][y * self.width + x] = 0

    def stamp(self, layer, x, y, sheet, sx, sy, width, height, connected=False):
        columns = SHEETS[sheet][2]
        source = texture(sheet)
        component = None
        if connected:
            alpha = source.crop((sx*16, sy*16, (sx+width)*16, (sy+height)*16)).getchannel('A')
            remaining = {(px, py) for py in range(alpha.height) for px in range(alpha.width) if alpha.getpixel((px, py))}
            component = set()
            while remaining:
                seed = remaining.pop()
                part, pending = {seed}, deque([seed])
                while pending:
                    px, py = pending.popleft()
                    for point in ((px-1, py), (px+1, py), (px, py-1), (px, py+1)):
                        if point in remaining:
                            remaining.remove(point); part.add(point); pending.append(point)
                if len(part) > len(component): component = part
        for dy in range(height):
            for dx in range(width):
                index = (sy + dy) * columns + sx + dx
                tile = source.crop(((sx + dx)*16, (sy + dy)*16, (sx + dx+1)*16, (sy + dy+1)*16))
                if tile.getbbox() and (component is None or any((px, py) in component
                    for py in range(dy*16, (dy+1)*16) for px in range(dx*16, (dx+1)*16))):
                    self.tile(layer, x + dx, y + dy, sheet, index)

    def action(self, x, y, action):
        self.actions[(x, y)] = action
        if not self.layers['Buildings'][y * self.width + x]:
            # Прозрачный Back-action не всегда обрабатывается игрой: даём табличке реальный тайл.
            self.tile('Buildings', x, y, 'inside', 208)

    def warp(self, x, y, target, tx, ty):
        if self.properties.get('Outdoors') == 'T' and self.layers['Buildings'][y*self.width+x]:
            self.passable.add((x, y))
        else:
            self.clear('Buildings', x, y)
        self.warps.append((x, y, target, tx, ty))

    def save(self):
        node = ET.Element('map', version='1.4', tiledversion='1.4.2', orientation='orthogonal',
                          renderorder='right-down', width=str(self.width), height=str(self.height),
                          tilewidth='16', tileheight='16', infinite='0')
        props = ET.SubElement(node, 'properties')
        if self.warps:
            self.properties['Warp'] = ' '.join(' '.join(map(str, warp)) for warp in self.warps)
        for key, value in self.properties.items():
            ET.SubElement(props, 'property', name=key, value=value)
        used = {key for key, (first, _, _) in SHEETS.items()
                if any(first <= gid < first + 2500 for layer in self.layers.values() for gid in layer if gid)}
        for key, (first, asset, columns) in SHEETS.items():
            if key not in used:
                continue
            source = texture(key)
            sheet = ET.SubElement(node, 'tileset', firstgid=str(first), name=key,
                                  tilewidth='16', tileheight='16', tilecount=str(source.width*source.height//256),
                                  columns=str(columns))
            # Точка перед именем: SMAPI использует штатную текстуру игры, а не ищет её в паке.
            asset_name = ('outingSigns.png' if key == 'signs' else '.springobjects.png'
                          if key == 'objects' else '.' + asset + '.png')
            ET.SubElement(sheet, 'image', source=asset_name, width=str(source.width), height=str(source.height))
        for index, (name, values) in enumerate(self.layers.items(), 1):
            layer = ET.SubElement(node, 'layer', id=str(index), name=name, width=str(self.width), height=str(self.height))
            data = ET.SubElement(layer, 'data', encoding='csv')
            data.text = '\n' + ',\n'.join(','.join(str(v) for v in values[y*self.width:(y+1)*self.width])
                                          for y in range(self.height)) + '\n'
        if self.actions or self.passable:
            objects = ET.SubElement(node, 'objectgroup', name='Buildings', visible='0')
            for index, (x, y) in enumerate(sorted(set(self.actions) | self.passable), 1):
                item = ET.SubElement(objects, 'object', id=str(index), name='TileData',
                                     x=str(x*16), y=str(y*16), width='16', height='16')
                properties = ET.SubElement(item, 'properties')
                if (x, y) in self.actions:
                    ET.SubElement(properties, 'property', name='Action', value=self.actions[x,y])
                if (x, y) in self.passable:
                    ET.SubElement(properties, 'property', name='Passable', value='T')
        ET.indent(node, space='  ')
        ET.ElementTree(node).write(OUT / (self.name + '.tmx'), encoding='utf-8', xml_declaration=True)
        canvas = Image.new('RGBA', (self.width*16, self.height*16), '#141923')
        for values in self.layers.values():
            for pos, gid in enumerate(values):
                if not gid:
                    continue
                sheet_key = max((key for key, value in SHEETS.items() if value[0] <= gid), key=lambda key: SHEETS[key][0])
                first, _, columns = SHEETS[sheet_key]
                index = gid - first
                source = texture(sheet_key)
                sx, sy = index % columns*16, index // columns*16
                canvas.alpha_composite(source.crop((sx, sy, sx+16, sy+16)), (pos % self.width*16, pos // self.width*16))
        canvas.resize((canvas.width*2, canvas.height*2), Image.Resampling.NEAREST).save(PREVIEW / (self.name + '.png'))


_textures = {}


def texture(key):
    if key not in _textures:
        asset = 'springobjects' if key == 'objects' else SHEETS[key][1]
        path = OUT / 'outingSigns.png' if key == 'signs' else GAME_MAPS / (asset + '.png')
        _textures[key] = Image.open(path).convert('RGBA')
    return _textures[key]


def interior(name, kind, destination, dx, dy):
    room = Map(name, 24, 18)
    for y in range(1, 18):
        for x in range(1, 23):
            room.tile('Back', x, y, 'inside', (231, 232, 263, 264)[(x % 2) + (y % 2)*2])
    for x in range(24):
        for y in (1, 2, 3):
            room.tile('Back', x, y, 'walls', (11 + (11+y)*16))
            room.tile('Buildings', x, y, 'walls', (11 + (11+y)*16))
        room.tile('Front', x, 3, 'inside', 197)
        room.tile('Buildings', x, 17, 'inside', 197)
    for y in range(4, 17):
        room.tile('Buildings', 0, y, 'inside', 68)
        room.tile('Buildings', 23, y, 'inside', 68)
    for x in (3, 18):
        room.stamp('Front', x, 1, 'inside', 4, 7, 1, 2)
    # Центр комнаты остаётся свободным для актёров и прохода от двери.
    if kind in ('cafe', 'party'):
        for x, y in [(5, 7), (17, 7), (5, 12), (17, 12)]:
            room.stamp('Buildings', x, y, 'inside', 9, 13, 3, 2)
        room.stamp('Buildings', 4, 4, 'inside', 1, 18, 3, 3)
        if kind == 'party':
            room.tile('Front', 6, 7, 'objects', 221)
            room.action(12, 3, 'HarveyOuting BirthdayCard')
        else:
            room.action(8, 5, 'Shop marilynsinister.HarveyOverhaul_ZuzuCafe')
            room.action(18, 5, 'HarveyOuting CafeMenu')
    elif kind in ('books', 'campus'):
        for x in (3, 8, 17):
            room.stamp('Buildings', x, 4, 'inside', 1, 18, 3, 3)
        room.stamp('Buildings', 4, 12, 'inside', 9, 13, 3, 2)
        room.action(5, 6, 'HarveyOuting PilotBooks' if kind == 'books' else 'HarveyOuting UniversityBoard')
        room.action(19, 6, 'HarveyOuting GardenBooks' if kind == 'books' else 'HarveyOuting UniversityLetter')
    else:
        room.stamp('Buildings', 4, 5, 'inside', 2, 24, 4, 4)
        room.stamp('Buildings', 17, 5, 'inside', 2, 24, 4, 4)
        room.action(5, 8, 'HarveyOuting Sleep')
        room.action(18, 8, 'HarveyOuting Sleep')
        room.action(12, 3, 'HarveyOuting HotelWindow')
    room.warp(12, 17, destination, dx, dy)
    return room


def build():
    OUT.mkdir(exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    signs = Image.new('RGBA', (256, 16))
    draw = ImageDraw.Draw(signs)
    font = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 9)
    for index, label in enumerate(('КОФЕ', 'КНИГИ', 'ЗУЗУ', 'ГОСТИНИЦА')):
        x = index*64
        draw.rectangle((x, 0, x+63, 15), fill='#334450', outline='#b4945e')
        bounds = draw.textbbox((0,0), label, font=font)
        draw.text((x+(64-bounds[2])/2, 1), label, font=font, fill='#fff0c3')
    signs.save(OUT / 'outingSigns.png')
    square = Map('HarveyZuzuSquare', 40, 30, outside=True)
    square.properties['Music'] = 'spring_day_ambient'
    for y in range(30):
        for x in range(40):
            square.tile('Back', x, y, 'town', 1000)
    square.stamp('Buildings', 3, 1, 'town', 8, 0, 8, 11, connected=True)
    square.stamp('Buildings', 14, 1, 'town', 16, 0, 9, 11, connected=True)
    square.stamp('Buildings', 25, 1, 'town', 0, 41, 12, 9, connected=True)
    square.stamp('Buildings', 26, 18, 'town', 0, 0, 8, 9, connected=True)
    square.stamp('Buildings', 15, 16, 'town', 16, 32, 5, 5)
    for index, x, y in [(0, 5, 5), (1, 16, 5), (2, 32, 5), (3, 28, 22)]:
        square.stamp('Buildings', x, y, 'signs', index*4, 0, 4, 1)
    square.tile('Buildings', 36, 5, 'signs', 11)
    for x, y in [(4, 15), (34, 14), (4, 25)]:
        square.stamp('Buildings', x, y, 'town', 27, 33, 3, 1)
    square.warp(6, 11, 'HarveyZuzuCafe', 12, 15)
    square.warp(18, 11, 'HarveyZuzuBooks', 12, 15)
    square.warp(31, 9, 'HarveyZuzuCampus', 12, 15)
    square.warp(27, 26, 'HarveyZuzuInn', 12, 15)
    square.warp(18, 29, 'BusStop', 23, 23)
    square.action(20, 27, 'HarveyOuting Return')
    square.action(9, 11, 'HarveyOuting CafeSign')
    square.action(21, 11, 'HarveyOuting BookSign')
    square.action(35, 9, 'HarveyOuting CampusSign')
    square.action(31, 26, 'HarveyOuting InnSign')
    rooms = [
        interior('HarveyCelebrationRoom', 'party', 'Hospital', 10, 19),
        interior('HarveyZuzuCafe', 'cafe', 'HarveyZuzuSquare', 6, 12),
        interior('HarveyZuzuBooks', 'books', 'HarveyZuzuSquare', 18, 12),
        interior('HarveyZuzuCampus', 'campus', 'HarveyZuzuSquare', 31, 10),
        interior('HarveyZuzuInn', 'inn', 'HarveyZuzuSquare', 27, 27),
    ]
    for item in [square, *rooms]:
        item.save()
    print('written 6 outing maps and previews')


if __name__ == '__main__':
    build()
