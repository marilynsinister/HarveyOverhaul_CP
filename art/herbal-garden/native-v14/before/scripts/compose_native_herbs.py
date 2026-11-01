"""Author botanical pixels at 16x32 / 16x16. No image sampling or resizing.

Each glyph character is one native pixel. Integer placement composes the
editable final pixel maps in art/herbal-garden/native-v13/pixels.json.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[1]
REVIEW = PACK / 'art/herbal-garden/native-v13'
NAMES = ('glass-dewberry', 'moonvelvet', 'amber-heartleaf', 'silver-seamleaf')
LABELS = ('Стеклянная росница', 'Лунная бархатница', 'Янтарный сердцелист', 'Серебряный шовник')
ASSETS = ('seed', 'sprout', 'juvenile', 'buds', 'mature', 'picked', 'harvest', 'packet')
COMMON = dict(q='593924', z='ac7435', Z='dcad5e', P='f6d9a0',
              b='233756', B='288fc9', C='77c9d6', h='46aebf', W='f5e7bb', S='285da2',
              p='4c2e50', F='cc8fda', v='ad60c6', V='773d94', Q='5e3a60',
              a='644027', Y='efd457', A='e4a839', s='bd752e', o='a7612f',
              f='574334', w='d8bd82', c='e89624', r='593b37')
RAMPS = (
    dict(g='1e3d2a', D='24692f', m='3c9e3a', L='83ce45', l='a8d55d', t='438f3b'),
    dict(g='2e4130', D='31663b', m='5d9440', L='a2c458', l='bbd281', t='658d3c'),
    dict(g='2b4128', D='2b702a', m='55a934', L='9ed14f', l='bfdc67', t='c45e39'),
    dict(g='244b40', D='25876b', m='46b78b', L='82dca2', l='aad9b1', t='5c9d52'),
)

# Contours are drawn into these glyphs, rather than expanded after rendering.
# Unequal tips, a curled edge and broken veins avoid repeated glossy diamonds.
# Every character is still a native pixel, including each dark material edge.
LEAVES = (
    ('.....gg', '...ggLg', '.ggLLmg', 'gLmlmDg', 'gmmDDg.', '.gDDg..', '..gg...'),
    ('...gg..', '..gLLg.', '.gLmlmg', 'gLmDDmg', 'gmmDDg.', '.gDDg..', '..gg...'),
    ('..ggg..', '.gLmmgg', 'gLmlmmg', 'gmmDDmg', '.gDDDg.', '..ggDg.', '....g..'),
    ('.....gg', '...ggLg', '..gLlmg', '.gLmDDg', 'gmmDDg.', 'gDDgg..', '.gg....'),
)
SMALL_LEAVES = (('..ggg', 'ggLmg', 'gmmgg', '.gg..'),
                ('..gg.', '.gLmg', 'gmDgg', '.gg..'))
BERRIES = (
    ('..bbb..', '.bhBBb.', 'bChBBBb', 'bhBBBSb', 'bBBSSSb', '.bSSSb.', '..bbb..'),
    ('...bb..', '.bbBBb.', 'bChBBBb', 'bhBBSSb', 'bBBSSSb', '.bSSSb.', '..bbb..'),
    ('..bbb..', '.bhhBb.', 'bChBBBb', 'bBBBSSb', '.bSSSbb', '..bbb..', '.......'),
)
CALYX = ('.g.', 'gmg', '.g.')
BELLS = (
    ('..ppp..', '..pvp..', '.pFFvp.', '.pFvVp.', 'pFvvVVp', 'pVQvQVp', 'pVpppVp', '.p...p.'),
    ('...pp..', '..pFvp.', '.pFFvp.', '.pFvVVp', 'pFvvVVp', 'pVvQQVp', 'pVpppp.', '.p.....'),
    ('..ppp..', '.pFvVp.', '.pFvvVp', 'pFvvVVp', 'pVvQQVp', 'pVpppVp', '.p...p.', '.......'),
)
HEARTS = (
    ('.aa.aa.', 'aYYaAAa', 'aYAAsAa', '.aAAoa.', '.aAosa.', '..asa..', '...a...'),
    ('.aa....', 'aYYaaa.', 'aYAAAYa', '.aAAosa', '.aAosa.', '..asa..', '...a...'),
    ('....aa.', '.aaaAYa', 'aYAAAYa', '.aAosa.', '.aAosa.', '..asa..', '...a...'),
)
FLOWERS = (
    ('....f....', '...fWf...', '..fWWwf..', 'ffWWwWWff', 'fWWwcwWWf', '.fwcccwf.', '..fWfWf..', '..fWfWf..', '...f.f...'),
    ('...ff....', '..fWWf...', '..fWwwf..', '.fWWwWWff', 'fWWwcwWWf', '.fwcccwf.', '..fWfwf..', '..fwfWf..', '...f.f...'),
)
BUDS = (
    ('.bbb.', 'bCBBb', 'bCBBb', 'bBSSb', '.bbb.'),
    ('..p..', '.pvp.', 'pFFVp', 'pvVVp', '.pVp.', '..p..'),
    ('..a..', '.aYa.', 'aYAAa', 'aAAsa', '.asa.', '..a..'),
    ('..f..', '.fWf.', 'fWWwf', 'fWwwf', '.fwf.', '..f..'),
)
HEAD_VARIANTS = (BERRIES, BELLS, HEARTS, FLOWERS)
HEADS = tuple(variants[0] for variants in HEAD_VARIANTS)


def grid(height=32):
    return [['.']*16 for _ in range(height)]


def stamp(target, glyph, x, y, mirror=False):
    width = len(glyph[0])
    assert all(len(row) == width for row in glyph), glyph
    for dy, row in enumerate(glyph):
        for dx, char in enumerate(row[::-1] if mirror else row):
            if char != '.':
                assert 0 <= x+dx < 16 and 0 <= y+dy < len(target), (x, y, glyph)
                target[y+dy][x+dx] = char


def line_points(a, b):
    x, y = a
    xx, yy = b
    dx, dy = abs(xx-x), -abs(yy-y)
    sx, sy = 1 if x < xx else -1, 1 if y < yy else -1
    error = dx+dy
    while True:
        yield x, y
        if (x, y) == (xx, yy):
            return
        twice = 2*error
        if twice >= dy:
            error += dy
            x += sx
        if twice <= dx:
            error += dx
            y += sy


def stem(target, points, kind):
    core = set()
    for a, b in zip(points, points[1:]):
        core.update(line_points(a, b))
    ink = 'r' if kind == 2 else 'g'
    for x, y in core:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                assert 0 <= x+dx < 16 and 0 <= y+dy < len(target)
                target[y+dy][x+dx] = ink
    for x, y in core:
        target[y][x] = 't'


def leaf(target, x, y, left=False, small=False, variant=0):
    glyphs = SMALL_LEAVES if small else LEAVES
    stamp(target, glyphs[variant % len(glyphs)], x, y, mirror=left)


def head(target, kind, x, y, variant=0):
    variants = HEAD_VARIANTS[kind]
    stamp(target, variants[variant % len(variants)], x, y)


def mature(kind):
    result = grid()
    stem(result, ((8, 5), (8, 9), (7, 13), (8, 17), (7, 21), (8, 25), (7, 29)), kind)
    if kind in (0, 1):
        if kind == 0:
            branches = (((8, 7), (7, 4), (6, 3)), ((7, 16), (9, 13)), ((8, 26), (7, 23), (6, 23)))
        else:
            branches = (((8, 8), (8, 5), (6, 2), (5, 2)), ((7, 16), (10, 11), (11, 12)), ((8, 26), (6, 22), (5, 22)))
        for branch in branches:
            stem(result, branch, kind)
        leaf(result, 8, 5, variant=3 if kind == 0 else 1)
        leaf(result, 1, 14, left=True, variant=2 if kind == 0 else 3)
        leaf(result, 8, 24, variant=0 if kind == 0 else 2)
        for variant, (x, y) in enumerate(((1, 3), (8, 13), (1, 23))):
            if kind == 1:
                y -= 1
            head(result, kind, x, y, variant)
            if kind == 0:
                stamp(result, CALYX, x+4 if x == 1 else x, y-1)
    elif kind == 2:
        stem(result, ((8, 9), (10, 3), (11, 3)), kind)
        stem(result, ((8, 17), (6, 13), (4, 13)), kind)
        stem(result, ((7, 26), (10, 23), (11, 23)), kind)
        leaf(result, 1, 4, left=True)
        leaf(result, 8, 14, variant=3)
        leaf(result, 1, 24, left=True, variant=2)
        for variant, (x, y) in enumerate(((8, 2), (1, 12), (8, 22))):
            head(result, kind, x, y, variant)
    else:
        stem(result, ((8, 9), (8, 5)), kind)
        stem(result, ((8, 20), (5, 15), (4, 15)), kind)
        stem(result, ((7, 25), (11, 19), (12, 18)), kind)
        leaf(result, 8, 9, variant=3)
        leaf(result, 1, 23, left=True, variant=3)
        leaf(result, 8, 24, variant=2)
        head(result, kind, 5, 1)
        head(result, kind, 1, 12, variant=1)
        stamp(result, BUDS[3], 10, 17)
    return result


def stages(kind):
    seed = grid()
    stamp(seed, ('.qqq.', 'qZZzq', 'qZzzq', '.qqq.'), 5, 27)
    sprout = grid()
    stem(sprout, ((7, 26), (7, 29)), kind)
    leaf(sprout, 3, 24, left=True, small=True)
    leaf(sprout, 8, 24, small=True, variant=1)
    young = grid()
    stem(young, ((8, 18), (7, 23), (7, 29)), kind)
    leaf(young, 8, 15, variant=3 if kind == 3 else 1)
    leaf(young, 1, 20, left=True, variant=3 if kind == 3 else 0)
    leaf(young, 8, 24, variant=2)
    buds = grid()
    stem(buds, ((8, 9), (7, 17), (8, 23), (7, 29)), kind)
    for branch in (((8, 12), (6, 8), (4, 8)), ((7, 19), (11, 17), (12, 17)), ((8, 26), (5, 24), (4, 24))):
        stem(buds, branch, kind)
    leaf(buds, 8, 11, variant=3 if kind == 3 else 1)
    leaf(buds, 1, 17, left=True, variant=3)
    leaf(buds, 8, 24, variant=2)
    for x, y in ((2, 6), (10, 15), (2, 23)):
        stamp(buds, BUDS[kind], x, y)
    picked = grid()
    stem(picked, ((8, 10), (7, 18), (8, 24), (7, 29)), kind)
    stem(picked, ((8, 15), (5, 11), (4, 11)), kind)
    stem(picked, ((8, 24), (11, 20)), kind)
    leaf(picked, 8, 9, variant=3 if kind == 3 else 1)
    leaf(picked, 1, 17, left=True, variant=3)
    leaf(picked, 8, 24, variant=2)
    picked[11][4] = 'z'
    picked[20][11] = 'z'
    return (seed, sprout, young, buds, mature(kind), picked)


def harvest(kind):
    result = grid(16)
    if kind == 0:
        stem(result, ((5, 12), (8, 9), (10, 4)), kind)
        leaf(result, 9, 1, small=True, variant=1)
        head(result, kind, 2, 3)
        stamp(result, CALYX, 6, 2)
        head(result, kind, 7, 7, variant=1)
        stamp(result, CALYX, 7, 6)
    elif kind == 1:
        stem(result, ((6, 7), (6, 3), (9, 3), (11, 7)), kind)
        leaf(result, 8, 1, small=True, variant=1)
        head(result, kind, 1, 4, variant=1)
        head(result, kind, 8, 6, variant=2)
    elif kind == 2:
        stem(result, ((5, 12), (8, 8), (10, 4)), kind)
        leaf(result, 3, 1, left=True, small=True)
        head(result, kind, 7, 4, variant=1)
        head(result, kind, 1, 7, variant=2)
    else:
        stem(result, ((4, 13), (8, 8), (9, 5)), kind)
        leaf(result, 1, 1, left=True, variant=3)
        leaf(result, 1, 10, left=True, small=True, variant=1)
        head(result, kind, 5, 4, variant=1)
    return result


def packet(kind):
    result = grid(16)
    for y in range(1, 15):
        for x in range(2, 14):
            result[y][x] = 'q' if x in (2, 13) or y in (1, 14) else 'P'
    for x in range(3, 13):
        result[2][x] = 'Z'
        result[3][x] = 'z'
        result[4][x] = 'q'
    stamp(result, HEADS[kind], 4 if kind == 3 else 5, 5 if kind in (1, 3) else 6)
    return result


def compose():
    maps = {}
    colors = []
    for kind, name in enumerate(NAMES):
        ramp = COMMON | RAMPS[kind]
        for asset, tile in zip(ASSETS, (*stages(kind), harvest(kind), packet(kind))):
            rows = []
            for row in tile:
                values = []
                for char in row:
                    color = ramp[char] if char != '.' else None
                    if color is not None and color not in colors:
                        colors.append(color)
                    values.append(color)
                rows.append(values)
            maps[f'{name}/{asset}'] = rows
    symbols = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#'
    assert len(colors) <= 64, len(colors)
    encoded = {color: symbols[i] for i, color in enumerate(colors)}
    return {'method': 'native pixel maps; one character = one output pixel; no resampling, quantization or automatic outline',
            'cropCell': [16, 32], 'itemCell': [16, 16],
            'palette': {encoded[color]: '#'+color for color in colors},
            'sprites': {name: [''.join(encoded[c] if c is not None else '.' for c in row) for row in rows]
                        for name, rows in maps.items()}}


def decode(data, key):
    rows = data['sprites'][key]
    palette = {key: tuple(bytes.fromhex(color[1:]))+(255,) for key, color in data['palette'].items()}
    im = Image.new('RGBA', (16, len(rows)))
    im.putdata([palette[c] if c != '.' else (0, 0, 0, 0) for row in rows for c in row])
    return im


def write_draft(data):
    folder = REVIEW / 'tiles'
    folder.mkdir(parents=True, exist_ok=True)
    for key in data['sprites']:
        decode(data, key).save(folder / (key.replace('/', '-')+'.png'))
    before = Image.open(REVIEW/'before/assets/Crops/herbalCrops.png').convert('RGBA')
    board = Image.new('RGB', (1040, 444), '#eee2c8')
    d = ImageDraw.Draw(board)
    font = lambda n: ImageFont.truetype('C:/Windows/Fonts/arial.ttf', n)
    d.text((24, 20), 'АПТЕКАРСКИЙ САД · НАТИВНЫЕ ПИКСЕЛИ', font=font(27), fill='#354636')
    d.text((24, 58), 'Рисунок сразу 16×32 · одинаковое увеличение ×6 · без уменьшения исходников', font=font(17), fill='#645d54')
    for kind, name in enumerate(NAMES):
        x = 16+kind*256
        d.rounded_rectangle((x, 94, x+246, 425), radius=10, fill='#ded1b3')
        first, second = LABELS[kind].split(' ', 1)
        d.text((x+13, 107), first, font=font(20), fill='#354636')
        d.text((x+13, 131), second, font=font(20), fill='#354636')
        d.rectangle((x+10, 166, x+236, 358), fill='#995b3b')
        d.rectangle((x+10, 308, x+236, 358), fill='#704134')
        xx, yy = kind%2*128+80, kind//2*32
        for im, pos in ((before.crop((xx, yy, xx+16, yy+32)), (x+15, 168)),
                        (decode(data, name+'/mature'), (x+135, 168))):
            im = im.resize((96, 192), Image.Resampling.NEAREST)
            board.paste(im, pos, im)
        d.text((x+30, 379), 'Было', font=font(17), fill='#645d54')
        d.text((x+142, 379), '16×32', font=font(17), fill='#354636')
    board.save(REVIEW/'comparison.png')


if __name__ == '__main__':
    data = compose()
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW/'pixels.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    write_draft(data)
    print(f'Native botanical source: {len(data["sprites"])} maps, {len(data["palette"])} colors, no downsampling.')
