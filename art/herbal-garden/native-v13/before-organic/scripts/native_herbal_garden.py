"""Render native botanical pixel maps. No crop/item resizing or added outline.

One source character is one PNG pixel. Only review previews are enlarged,
using integer nearest-neighbor magnification.
"""
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[1]
ART = PACK / 'art/herbal-garden'
REVIEW = ART / 'native-v13'
SOURCE = REVIEW / 'pixels.json'
NAMES = ('glass-dewberry', 'moonvelvet', 'amber-heartleaf', 'silver-seamleaf')
LABELS = ('Стеклянная росница', 'Лунная бархатница', 'Янтарный сердцелист', 'Серебряный шовник')
ASSETS = ('seed', 'sprout', 'juvenile', 'buds', 'mature', 'picked', 'harvest', 'packet')
FRAME_MAP = (0, 0, 1, 2, 3, 4, 4, 5)
INK = (30, 61, 42, 255)  # Compatibility; each material has its authored ink.


@lru_cache(maxsize=1)
def source_data():
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    assert len(data['palette']) <= 64 and len(data['sprites']) == 32
    assert data['cropCell'] == [16, 32] and data['itemCell'] == [16, 16]
    return data


@lru_cache(maxsize=32)
def tile(kind, asset):
    data = source_data()
    rows = data['sprites'][NAMES[kind]+'/'+asset]
    expected_height = 16 if asset in ('harvest', 'packet') else 32
    assert len(rows) == expected_height and all(len(row) == 16 for row in rows)
    palette = {char: tuple(bytes.fromhex(color[1:]))+(255,) for char, color in data['palette'].items()}
    image = Image.new('RGBA', (16, expected_height))
    image.putdata([palette[c] if c != '.' else (0, 0, 0, 0) for row in rows for c in row])
    return image


def crop_stages(kind):
    return [tile(kind, asset).copy() for asset in ASSETS[:6]]


def herb(kind):
    return tile(kind, 'harvest').copy()


def seed_packet(kind):
    return tile(kind, 'packet').copy()


def build_items():
    sheet = Image.new('RGBA', (128, 16))
    for index, im in enumerate([herb(k) for k in range(4)]+[seed_packet(k) for k in range(4)]):
        sheet.paste(im, (index*16, 0))
    return sheet


def build_crops():
    sheet = Image.new('RGBA', (256, 64))
    plants = [crop_stages(k) for k in range(4)]
    for kind, stages in enumerate(plants):
        for frame, stage in enumerate(FRAME_MAP):
            sheet.paste(stages[stage], (kind%2*128+frame*16, kind//2*32))
    return sheet, plants


def metadata():
    return {'source': '../../scripts/native_herbal_garden.py',
            'method': 'native-v13: one source character = one game pixel; direct palette lookup and packing',
            'outline': 'authored into native glyphs; no automatic expansion',
            'pixelSource': '../herbal-garden/native-v13/pixels.json',
            'authoringSource': '../../scripts/compose_native_herbs.py'}


def remember_before(target):
    if target.is_file():
        backup = REVIEW/'before'/target.relative_to(PACK)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target, backup)


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)


def magnify(target, im, xy, scale):
    assert isinstance(scale, int) and scale >= 1
    if scale > 1:
        im = im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)
    target.paste(im, xy, im)


def preview(items, plants):
    stages = Image.new('RGB', (1160, 822), '#eee2c8')
    d = ImageDraw.Draw(stages)
    d.text((28, 20), 'АПТЕКАРСКИЙ САД · НАТИВНЫЕ ПИКСЕЛИ', font=font(29), fill='#252a30')
    d.text((28, 61), 'Рисунок сразу 16×32 / 16×16 · PNG увеличены ×4 · без уменьшения и сглаживания', font=font(18), fill='#645d54')
    for x, label in zip((346, 478, 610, 742, 874, 1006), ('Посев', 'Росток', 'Молодое', 'Бутоны', 'Зрелое', 'После сбора')):
        d.text((x, 102), label, font=font(15), fill='#645d54')
    for kind, name in enumerate(NAMES):
        y = 134+kind*164
        d.rounded_rectangle((18, y-5, 1140, y+150), radius=9, fill='#ded1b3')
        d.text((32, y+6), LABELS[kind], font=font(18), fill='#252a30')
        for x, im, caption in ((40, herb(kind), 'Урожай'), (144, seed_packet(kind), 'Семена')):
            magnify(stages, im, (x, y+42), 4)
            magnify(stages, im, (x+72, y+90), 1)
            d.text((x, y+115), caption, font=font(14), fill='#645d54')
        for stage, im in enumerate(plants[kind]):
            xx = 344+stage*132
            d.rectangle((xx-8, y+4, xx+77, y+137), fill='#879b64')
            d.rectangle((xx-8, y+112, xx+77, y+137), fill='#995b3b')
            magnify(stages, im, (xx+2, y+4), 4)
    stages.save(REVIEW/'preview.png')
    stages.save(ART/'preview.png')

    garden = Image.new('RGB', (752, 358), '#eee2c8')
    d = ImageDraw.Draw(garden)
    d.text((24, 18), 'НАТИВНЫЕ РАСТЕНИЯ · ГОТОВЫЕ PNG ×4', font=font(22), fill='#252a30')
    for row, soil in enumerate(('#995b3b', '#383052')):
        y = 76+row*136
        d.rectangle((20, y+10, 731, y+120), fill=soil)
        for kind in range(4):
            for repeat in range(2):
                magnify(garden, plants[kind][4], (36+kind*176+repeat*64, y-10), 4)
    garden.save(REVIEW/'garden-preview.png')

    old = Image.open(REVIEW/'before/assets/Crops/herbalCrops.png').convert('RGBA')
    comparison = Image.new('RGB', (1040, 444), '#eee2c8')
    d = ImageDraw.Draw(comparison)
    d.text((24, 20), 'АПТЕКАРСКИЙ САД · НАТИВНЫЕ ПИКСЕЛИ', font=font(27), fill='#354636')
    d.text((24, 58), 'Рисунок сразу 16×32 · одинаковое увеличение ×6 · без уменьшения исходников', font=font(17), fill='#645d54')
    for kind in range(4):
        x = 16+kind*256
        d.rounded_rectangle((x, 94, x+246, 425), radius=10, fill='#ded1b3')
        first, second = LABELS[kind].split(' ', 1)
        d.text((x+13, 107), first, font=font(20), fill='#354636')
        d.text((x+13, 131), second, font=font(20), fill='#354636')
        d.rectangle((x+10, 166, x+236, 358), fill='#995b3b')
        d.rectangle((x+10, 308, x+236, 358), fill='#704134')
        xx, yy = kind%2*128+80, kind//2*32
        magnify(comparison, old.crop((xx, yy, xx+16, yy+32)), (x+15, 168), 6)
        magnify(comparison, plants[kind][4], (x+135, 168), 6)
        d.text((x+30, 379), 'Было', font=font(17), fill='#645d54')
        d.text((x+142, 379), '16×32', font=font(17), fill='#354636')
    comparison.save(REVIEW/'comparison.png')


def export(install=False):
    REVIEW.mkdir(parents=True, exist_ok=True)
    out = ART/'exports'
    out.mkdir(exist_ok=True)
    items = build_items()
    field, plants = build_crops()
    for im in (items, field):
        assert set(im.getchannel('A').get_flattened_data()) == {0, 255}
        assert len({p[:3] for p in im.get_flattened_data() if p[3]}) <= 64
    for kind, name in enumerate(NAMES):
        for asset in ASSETS:
            (REVIEW/'tiles').mkdir(exist_ok=True)
            tile(kind, asset).save(REVIEW/'tiles'/f'{name}-{asset}.png')
        for suffix, im in (('', herb(kind)), ('-seeds', seed_packet(kind))):
            path = out/(name+suffix+'.png')
            remember_before(path)
            im.save(path)
        for stage, im in enumerate(plants[kind]):
            path = out/f'{name}-stage-{stage}.png'
            remember_before(path)
            im.save(path)
    for name, im in (('herbalItems.png', items), ('herbalCrops.png', field)):
        remember_before(out/name)
        im.save(out/name)
    if install:
        for relative, im in (('assets/Items/herbalItems.png', items), ('assets/Crops/herbalCrops.png', field),
                             ('art/native-16/exports/herbalItems.png', items)):
            path = PACK/relative
            remember_before(path)
            im.save(path)
        report_path = PACK/'art/native-16/report.json'
        remember_before(report_path)
        report = json.loads(report_path.read_text(encoding='utf-8'))
        report['sheets']['herbalItems.png']['sha256'] = hashlib.sha256(items.tobytes()).hexdigest()
        report['herbalGarden'] = metadata()
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    remember_before(ART/'preview.png')
    preview(items, plants)
    report = {'source': '../../../scripts/native_herbal_garden.py',
              'pixelSource': 'pixels.json', 'authoringSource': '../../../scripts/compose_native_herbs.py',
              'method': source_data()['method'], 'nativeSize': True, 'downsampling': False,
              'automaticOutline': False, 'paletteColors': len(source_data()['palette']),
              'cropCell': [16, 32], 'itemCell': [16, 16], 'frameMap': list(FRAME_MAP),
              'installedInWorkspace': install,
              'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'sheets': {name: {'size': list(im.size), 'colors': len({p[:3] for p in im.get_flattened_data() if p[3]}),
                                 'sha256Pixels': hashlib.sha256(im.tobytes()).hexdigest()}
                         for name, im in (('herbalItems.png', items), ('herbalCrops.png', field))}}
    (REVIEW/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Native herbal garden: 32 pixel maps; crop cells 16x32; inventory 16x16; direct packing.')
    print('No downsampling, smoothing, palette quantization or automatic outline.')
    print('Workspace assets installed.' if install else 'Exports only; --install updates workspace assets.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    export(parser.parse_args().install)
