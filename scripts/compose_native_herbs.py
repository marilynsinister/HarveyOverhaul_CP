"""Author botanical pixels at 16x32 / 16x16. No image sampling or resizing.

Each glyph character is one native pixel. Integer placement composes the
editable final pixel maps in art/herbal-garden/native-v14/pixels.json.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[1]
REVIEW = PACK / 'art/herbal-garden/native-v14'
NAMES = ('glass-dewberry', 'moonvelvet', 'amber-heartleaf', 'silver-seamleaf')
LABELS = ('Стеклянная росница', 'Лунная бархатница', 'Янтарный сердцелист', 'Серебряный шовник')
ASSETS = ('seed', 'sprout', 'juvenile', 'buds', 'mature', 'picked', 'harvest', 'packet')
COMMON = dict(q='593924', z='ac7435', Z='dcad5e', P='f6d9a0',
              b='202e53', B='1597e8', C='62e0ff', h='32bdf0', I='dffaff', S='2459b4', U='263e86',
              p='48264e', F='e89af0', v='ba59d5', V='743ba6', Q='432d64',
              a='684126', Y='ffda48', A='f6a529', s='c77427', o='a6532b',
              f='5d4836', W='fff0cf', J='fffce9', w='dcbd81', c='ee9d20', r='593332')
RAMPS = (
    dict(g='173d2a', D='1a6036', m='32983b', L='83d53c', l='d0ee73', t='589d35'),
    dict(g='263d2a', D='2b5d30', m='539d39', L='a1cf4d', l='dfec89', t='6e9d3b'),
    dict(g='254326', D='286a2c', m='59ad30', L='a7d939', l='e6ef7a', t='d8713f'),
    dict(g='194335', D='196d51', m='32b77e', L='86e29d', l='daf6bb', t='63a24c'),
)

# Contours are drawn into these glyphs, rather than expanded after rendering.
# Broad diagonal blades and a curled silhouette are drawn at their final size.
# Light planes, veins and glints are individual pixels, never sampled from art.
LEAVES = (
    ('.......gg', '.....ggLg', '...ggLLmg', '..gLLlmDg', '.gLLlmDDg', 'gLmlmDDg.', 'gmmDDDg..', '.gDDgg...', '..gg.....'),
    ('...gggg..', '.ggLLllg.', 'gLLlmDDgg', 'gLmmDDmDg', 'gmmDDDgDg', '.gDDgg.g.', '..gg.....', '.........'),
    ('.......gg', '....gggLg', '..ggLLlmg', '.gLLlmDDg', 'gLmlDDgg.', 'gmmDDg...', '.gDDg....', '..gg.....'),
    ('.......gg', '......gLg', '.....gLlg', '....gLlmg', '...gLlmDg', '..gLlmDg.', '.gLlmDg..', 'gLmmDg...', 'gDDgg....', '.gg......'),
)
SMALL_LEAVES = (('..ggg', 'ggLmg', 'gmmgg', '.gg..'),
                ('..gg.', '.gLmg', 'gmDgg', '.gg..'))
BERRIES = (
    ('...bbb...', '.bbCCBbb.', '.bCIhBBb.', 'bBCIhBBBb', 'bBhBBBBBb', 'bBBBBSSSb', '.bBBSSSb.', '.bbSUSbb.', '...bbb...'),
    ('...bbb...', '..bCCBbb.', '.bCIhBBb.', 'bBCIhBBBb', 'bBhBBBBBb', 'bBBBBSSSb', 'bBBSSUSb.', '.bbSSbb..', '...bb....'),
    ('...bbb...', '.bbhCBbb.', '.bCIBBBb.', 'bBChBBBBb', 'bBBBBBSSb', 'bBBBSSSSb', '.bBSSUSb.', '.bbSSSbb.', '...bbb...'),
)
CALYX = ('.g.', 'gmg', '.g.')
BELLS = (
    ('....pp...', '...pFvp..', '..pFFvVp.', '..pFWvvVp', '.pFFvvVVp', 'pFFvvVVVp', 'pFvQQvVVp', '.pFpppVVp', '..p..pVp.', '......p..'),
    ('...pp....', '..pFvp...', '.pFFWvp..', 'pFFWvvVp.', 'pFvvvVVp.', 'pFvQQVVVp', 'pFpppvVVp', '.p...pVp.', '......p..', '.........'),
    ('....pp...', '...pFvp..', '..pFFWVp.', '..pFWvvVp', '.pFFvvVVp', 'pFvvQVVVp', '.pFpppVVp', '..p..pVp.', '......p..', '.........'),
)
HEARTS = (
    ('.aaa.aaa.', 'aYYYaYYAa', 'aYWYAAAsa', 'aYYAoAAsa', '.aYAoAsa.', '.aAAoAsa.', '..aAosa..', '...asa...', '....a....'),
    ('.aaa.....', 'aYYYaaaa.', 'aYWYaYYAa', 'aYYAoAAsa', '.aYAoAsa.', '.aAAoAsa.', '..aAosa..', '...asa...', '....a....'),
    ('.....aaa.', '.aaaaYYAa', 'aYYYAWYAa', 'aYYAoAAsa', '.aYAoAsa.', '.aAAoAsa.', '..aAosa..', '...asa...', '....a....'),
)
FLOWERS = (
    ('.....f.....', '....fJf....', '...fJWWf...', '..ffWWwff..', 'ffJWwWWwWff', 'fJWWwccWWWf', '.fWwYccWWf.', '..fWwcfWf..', '..fWWfWWf..', '..fWf.fWf..', '...f...f...'),
    ('....ff.....', '...fJWf....', '..fJWWwf...', '.ffWWwWff..', 'fJWwwWJWf..', 'fWWWcYcwWff', '.fWwcccWWWf', '..fWwcfWWf.', '..fWWfWwf..', '...ff.fWf..', '.......f...'),
)
BUDS = (
    ('.bbb.', 'bCBBb', 'bCBBb', 'bBSSb', '.bbb.'),
    ('..p..', '.pvp.', 'pFFVp', 'pvVVp', '.pVp.', '..p..'),
    ('..a..', '.aYa.', 'aYAAa', 'aAAsa', '.asa.', '..a..'),
    ('..f..', '.fWf.', 'fWWwf', 'fWwwf', '.fwf.', '..f..'),
)
HEAD_VARIANTS = (BERRIES, BELLS, HEARTS, FLOWERS)
EMBLEMS = (
    ('..bbb..', '.bCBBb.', 'bCIBBBb', 'bCBBBBb', 'bBBSSSb', '.bSSSb.', '..bbb..'),
    ('..ppp..', '..pFp..', '.pFFvp.', '.pFvVp.', 'pFvvVVp', 'pVQWQVp', 'pVpppVp', '.p...p.'),
    ('.aa.aa.', 'aYYaYYa', 'aYAAAAa', '.aAAsa.', '.aAssa.', '..asa..', '...a...'),
    ('....f....', '...fWf...', '..fWWwf..', 'ffWWwWWff', 'fWWwcwWWf', '.fwcccwf.', '..fWfWf..', '..fWfWf..', '...f.f...'),
)


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
    if kind == 0:
        stem(result, ((8, 4), (7, 9), (9, 15), (6, 22), (8, 26), (7, 29)), kind)
        stem(result, ((8, 14), (5, 10), (4, 10)), kind)
        stem(result, ((7, 22), (10, 17)), kind)
        leaf(result, 1, 3, left=True, variant=2)
        leaf(result, 6, 9, variant=0)
        leaf(result, 1, 21, left=True, variant=2)
        leaf(result, 6, 24, variant=1)
        for variant, (x, y, cx, cy) in enumerate(((5, 2, 8, 1), (1, 10, 4, 9), (6, 16, 10, 15))):
            head(result, kind, x, y, variant)
            stamp(result, CALYX, cx, cy)
    elif kind == 1:
        stem(result, ((7, 29), (8, 25), (7, 20), (9, 13), (9, 5), (7, 2), (5, 2), (4, 5)), kind)
        stem(result, ((8, 14), (10, 10)), kind)
        stem(result, ((8, 22), (5, 19)), kind)
        leaf(result, 6, 3, variant=1)
        leaf(result, 1, 12, left=True, variant=0)
        leaf(result, 6, 22, variant=0)
        leaf(result, 1, 23, left=True, variant=1)
        for variant, (x, y) in enumerate(((1, 4), (6, 11), (1, 18))):
            head(result, kind, x, y, variant)
    elif kind == 2:
        stem(result, ((7, 29), (9, 25), (7, 21), (8, 17), (10, 10), (8, 4), (5, 3)), kind)
        stem(result, ((9, 14), (11, 11)), kind)
        stem(result, ((8, 23), (5, 19)), kind)
        leaf(result, 6, 1, variant=1)
        leaf(result, 1, 12, left=True, variant=2)
        leaf(result, 6, 22, variant=0)
        leaf(result, 1, 23, left=True, variant=1)
        for variant, (x, y) in enumerate(((1, 3), (6, 11), (1, 19))):
            head(result, kind, x, y, variant)
    else:
        stem(result, ((7, 29), (8, 25), (6, 20), (8, 14), (8, 6)), kind)
        stem(result, ((7, 21), (11, 17), (12, 14)), kind)
        leaf(result, 1, 5, left=True, variant=3)
        leaf(result, 6, 11, variant=3)
        leaf(result, 1, 21, left=True, variant=1)
        leaf(result, 6, 21, variant=3)
        head(result, kind, 4, 1)
        head(result, kind, 1, 13, variant=1)
        stamp(result, BUDS[3], 10, 12)
    return result


def stages(kind):
    seed = grid()
    stamp(seed, ('.qqq.', 'qZZzq', 'qZzzq', '.qqq.'), 5, 27)
    sprout = grid()
    stem(sprout, ((7, 26), (7, 29)), kind)
    leaf(sprout, 3, 24, left=True, small=True)
    leaf(sprout, 8, 24, small=True, variant=1)
    young = grid()
    stem(young, ((8, 16), (7, 21), (8, 25), (7, 29)), kind)
    leaf(young, 6, 12, variant=3 if kind == 3 else 0)
    leaf(young, 1, 18, left=True, variant=3 if kind == 3 else 2)
    leaf(young, 6, 23, variant=1)
    buds = grid()
    stem(buds, ((8, 9), (7, 17), (8, 23), (7, 29)), kind)
    for branch in (((8, 12), (6, 8), (4, 8)), ((7, 19), (11, 17), (12, 17)), ((8, 26), (5, 24), (4, 24))):
        stem(buds, branch, kind)
    leaf(buds, 6, 9, variant=3 if kind == 3 else 0)
    leaf(buds, 1, 16, left=True, variant=2)
    leaf(buds, 6, 21 if kind == 3 else 22, variant=3 if kind == 3 else 0)
    leaf(buds, 1, 23, left=True, variant=1)
    for x, y in ((2, 6), (10, 15), (2, 23)):
        stamp(buds, BUDS[kind], x, y)
    picked = grid()
    stem(picked, ((8, 10), (7, 18), (8, 24), (7, 29)), kind)
    stem(picked, ((8, 15), (5, 11), (4, 11)), kind)
    stem(picked, ((8, 24), (11, 20)), kind)
    leaf(picked, 6, 9, variant=3 if kind == 3 else 0)
    leaf(picked, 1, 17, left=True, variant=2)
    leaf(picked, 6, 21 if kind == 3 else 22, variant=3 if kind == 3 else 0)
    leaf(picked, 1, 23, left=True, variant=1)
    picked[11][4] = 'z'
    picked[20][11] = 'z'
    return (seed, sprout, young, buds, mature(kind), picked)


def harvest(kind):
    result = grid(16)
    if kind == 0:
        stem(result, ((5, 12), (8, 9), (10, 4)), kind)
        leaf(result, 9, 1, small=True, variant=1)
        head(result, kind, 1, 2)
        stamp(result, CALYX, 4, 1)
        head(result, kind, 6, 6, variant=1)
        stamp(result, CALYX, 9, 5)
    elif kind == 1:
        stem(result, ((6, 7), (6, 3), (9, 3), (11, 7)), kind)
        leaf(result, 8, 1, small=True, variant=1)
        head(result, kind, 1, 2, variant=1)
        head(result, kind, 6, 5, variant=2)
    elif kind == 2:
        stem(result, ((5, 12), (8, 8), (10, 4)), kind)
        leaf(result, 3, 1, left=True, small=True)
        head(result, kind, 6, 2, variant=1)
        head(result, kind, 1, 6, variant=2)
    else:
        stem(result, ((4, 13), (8, 8), (9, 5)), kind)
        leaf(result, 1, 1, left=True, variant=0)
        leaf(result, 1, 10, left=True, small=True, variant=1)
        head(result, kind, 4, 4, variant=1)
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
    stamp(result, EMBLEMS[kind], 4 if kind == 3 else 5, 5 if kind in (1, 3) else 6)
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
    d.text((24, 20), 'КРУПНЫЕ ПЛОДЫ · РАЗМАШИСТАЯ ЛИСТВА', font=font(27), fill='#354636')
    d.text((24, 58), 'Было и стало · одинаковое увеличение ×6 · рабочие спрайты 16×32', font=font(17), fill='#645d54')
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
        d.text((x+142, 379), 'Стало', font=font(17), fill='#354636')
    board.save(REVIEW/'comparison.png')


if __name__ == '__main__':
    data = compose()
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW/'pixels.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    write_draft(data)
    print(f'Native botanical source: {len(data["sprites"])} maps, {len(data["palette"])} colors, no downsampling.')
