"""Reduce the image_gen botanical source paintings, then ink the game pixels.

python scripts/painted_herbal_garden.py --install
Sources are project-local RGBA PNGs; rebuilding never calls an image service.
"""
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from refine_herbal_pixels import render as palette_images

PACK = Path(__file__).resolve().parents[1]
ART = PACK / 'art/herbal-garden'
REVIEW = ART / 'painted-v10'
SOURCE = REVIEW / 'sources'
MATURE = REVIEW / 'mature-portraits'
NAMES = ('glass-dewberry', 'moonvelvet', 'amber-heartleaf', 'silver-seamleaf')
LABELS = ('Стеклянная росница', 'Лунная бархатница', 'Янтарный сердцелист', 'Серебряный шовник')
ASSETS = ('seed', 'sprout', 'juvenile', 'buds', 'mature', 'picked', 'harvest', 'packet')
INK = (78, 98, 76, 255)  # Legacy import compatibility; edges now retain their material colors.
DETAIL_SAMPLE_SCALE = 3
FRAME_MAP = (0, 0, 1, 2, 3, 4, 4, 5)
SOURCE_COLUMNS = 2


def canvas(size):
    return Image.new('RGBA', size)


def source_boxes(im):
    """Find eight separate paintings, even when they overhang nominal grid cells."""
    # A small mask connects subpixel edge gaps without blurring the source art.
    mask = im.getchannel('A').resize((im.width//4, im.height//4), Image.Resampling.BOX)
    mask = mask.point(lambda a: 255 if a >= 128 else 0).filter(ImageFilter.MaxFilter(3))
    w, h = mask.size
    pixels = bytearray(mask.tobytes())
    boxes = []
    for pos in range(w*h):
        if not pixels[pos]:
            continue
        pixels[pos] = 0
        queue = [pos]
        x0 = x1 = pos % w
        y0 = y1 = pos // w
        count = 0
        component = []
        while queue:
            k = queue.pop()
            component.append(k)
            x, y = k % w, k // w
            count += 1
            x0, x1 = min(x0, x), max(x1, x)
            y0, y1 = min(y0, y), max(y1, y)
            for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                if 0 <= xx < w and 0 <= yy < h and pixels[yy*w+xx]:
                    pixels[yy*w+xx] = 0
                    queue.append(yy*w+xx)
        if count > 25:
            box = (max(0, x0*4-4), max(0, y0*4-4),
                   min(im.width, (x1+1)*4+4), min(im.height, (y1+1)*4+4))
            ownership = bytearray(w*h)
            for k in component:
                ownership[k] = 255
            selection = Image.frombytes('L', (w, h), bytes(ownership)).resize(im.size, Image.Resampling.NEAREST)
            boxes.append((box, selection.crop(box)))
    assert len(boxes) == 8, f'Expected eight separate source paintings, found {len(boxes)}'
    # Portrait source sheets: two columns, four rows, in ASSETS order. Sort
    # by row centers so bottom-aligned tiny seeds need no hard crop boxes.
    vertical = sorted(boxes, key=lambda b: b[0][1]+b[0][3])
    ordered = []
    for start in range(0, 8, SOURCE_COLUMNS):
        ordered.extend(sorted(vertical[start:start+SOURCE_COLUMNS], key=lambda b: b[0][0]+b[0][2]))
    return ordered


@lru_cache(maxsize=4)
def paintings(kind):
    with Image.open(SOURCE / (NAMES[kind]+'.png')) as source:
        im = source.convert('RGBA')
    result = []
    for box, selection in source_boxes(im):
        crop = im.crop(box)
        crop.putalpha(ImageChops.multiply(crop.getchannel('A'), selection))
        # Discard only the faint extraction fringe, keeping generated alpha.
        crop.putalpha(crop.getchannel('A').point(lambda a: a if a >= 128 else 0))
        result.append(crop.crop(crop.getbbox()))
    # Mature plants are separate portrait paintings: this leaves enough
    # vertical stem spacing for the larger flowers/fruit at 16x32, while the
    # other seven source assets retain their own lifecycle/packet designs.
    with Image.open(MATURE / (NAMES[kind]+'.png')) as portrait_source:
        portrait = portrait_source.convert('RGBA')
    portrait.putalpha(portrait.getchannel('A').point(lambda a: a if a >= 128 else 0))
    assert portrait.getbbox(), (NAMES[kind], 'empty mature portrait')
    result[4] = portrait.crop(portrait.getbbox())
    return result


def reduce_painting(im, size, limit, baseline):
    """Keep the area-filtered silhouette; sample finer color detail separately."""
    scale = min(limit[0]/im.width, limit[1]/im.height)
    target = (max(1, round(im.width*scale)), max(1, round(im.height*scale)))
    reduced = im.resize(target, Image.Resampling.LANCZOS)
    detail_size = tuple(edge*DETAIL_SAMPLE_SCALE for edge in target)
    details = im.resize(detail_size, Image.Resampling.LANCZOS).resize(target, Image.Resampling.NEAREST)
    alpha = reduced.getchannel('A').point(lambda a: 255 if a >= 112 else 0)
    # Color no longer averages across as much of a leaf/berry boundary. Keep
    # the original color wherever the detail sample falls outside the plant.
    reduced.putdata([d[:3]+(a,) if a and d[3] >= 128 else b[:3]+(a,)
                     for b, d, a in zip(reduced.get_flattened_data(), details.get_flattened_data(), alpha.get_flattened_data())])
    reduced = reduced.crop(reduced.getbbox())
    result = canvas(size)
    result.alpha_composite(reduced, ((size[0]-reduced.width)//2, baseline-reduced.height))
    return result



@lru_cache(maxsize=1)
def reduced_assets():
    raw = []
    # Use the crop cell's height for open branches. The inner edge leaves all
    # 14 available pixels for the painting, with a transparent 1px gutter.
    limits = ((5, 4), (7, 8), (11, 15), (13, 22), (14, 26), (13, 21))
    for kind in range(4):
        source = paintings(kind)
        raw.extend(reduce_painting(source[stage], (16, 32), limits[stage], 31) for stage in range(6))
        raw.append(reduce_painting(source[6], (16, 16), (14, 14), 15))
        raw.append(reduce_painting(source[7], (16, 16), (13, 14), 15))
    final = palette_images(raw)
    return raw, final


def crop_stages(kind):
    return [im.copy() for im in reduced_assets()[1][kind*8:kind*8+6]]


def herb(kind):
    return reduced_assets()[1][kind*8+6].copy()


def seed_packet(kind):
    return reduced_assets()[1][kind*8+7].copy()


def build_items():
    sheet = canvas((128, 16))
    for index, im in enumerate([herb(k) for k in range(4)] + [seed_packet(k) for k in range(4)]):
        sheet.paste(im, (index*16, 0))
    return sheet


def build_crops():
    sheet = canvas((256, 64))
    plants = [crop_stages(k) for k in range(4)]
    for kind, stages in enumerate(plants):
        for frame, stage in enumerate(FRAME_MAP):
            sheet.paste(stages[stage], ((kind%2)*128+frame*16, (kind//2)*32))
    return sheet, plants


def remember_before(target):
    if target.is_file():
        backup = REVIEW / 'before' / target.relative_to(PACK)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target, backup)


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)


def paste_scaled(target, im, xy, scale):
    large = im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)
    target.paste(large, xy, large)


def fit_painting(target, im, box):
    scale = min((box[2]-box[0])/im.width, (box[3]-box[1])/im.height)
    large = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
    target.paste(large, ((box[0]+box[2]-large.width)//2, box[3]-large.height), large)


def preview(items, plants):
    board = Image.new('RGB', (1400, 840), '#eee2c8')
    d = ImageDraw.Draw(board)
    d.text((28, 20), 'АПТЕКАРСКИЙ САД · НОВАЯ ПЕРЕРИСОВКА', font=font(29), fill='#252a30')
    d.text((28, 61), 'Широкие изгибы листьев · открытые боковые веточки · чёткий цветной контур', font=font(19), fill='#645d54')
    for k in range(4):
        x = 20+k*346
        d.rounded_rectangle((x, 104, x+332, 813), radius=12, fill='#ded1b3')
        first, second = LABELS[k].split(' ', 1)
        d.text((x+16, 120), first, font=font(23), fill='#252a30')
        d.text((x+16, 148), second, font=font(23), fill='#252a30')
        fit_painting(board, paintings(k)[4], (x+32, 190, x+300, 421))
        d.text((x+18, 438), 'Крупный исходник', font=font(16), fill='#645d54')
        d.text((x+18, 477), 'Игровой спрайт 16×32 · ×8', font=font(17), fill='#252a30')
        d.rectangle((x+18, 505, x+314, 718), fill='#879b64')
        d.rectangle((x+18, 645, x+165, 718), fill='#995b3b')
        d.rectangle((x+166, 645, x+314, 718), fill='#704134')
        paste_scaled(board, plants[k][4], (x+26, 469), 8)
        paste_scaled(board, plants[k][4], (x+174, 469), 8)
        for i, caption in ((k, 'Урожай'), (k+4, 'Семена')):
            xx = x+30+(i//4)*155
            icon = items.crop((i*16, 0, i*16+16, 16))
            paste_scaled(board, icon, (xx, 725), 4)
            board.paste(icon, (xx+77, 767), icon)
            d.text((xx, 791), caption, font=font(15), fill='#645d54')
    board.save(REVIEW / 'reduction-preview.png')

    stages = Image.new('RGB', (1160, 822), '#eee2c8')
    sd = ImageDraw.Draw(stages)
    sd.text((28, 20), 'АПТЕКАРСКИЙ САД · ВСЕ СТАДИИ', font=font(29), fill='#252a30')
    sd.text((28, 61), 'Игровые PNG ×4 · урожай и семена 16×16 · культуры 16×32 · прозрачный фон', font=font(18), fill='#645d54')
    for x, label in zip((346, 478, 610, 742, 874, 1006), ('Посев', 'Росток', 'Молодое', 'Бутоны', 'Зрелое', 'После сбора')):
        sd.text((x, 102), label, font=font(15), fill='#645d54')
    for k in range(4):
        y = 134+k*164
        sd.rounded_rectangle((18, y-5, 1140, y+150), radius=9, fill='#ded1b3')
        sd.text((32, y+6), LABELS[k], font=font(18), fill='#252a30')
        for x, index, caption in ((40, k, 'Урожай'), (144, k+4, 'Семена')):
            icon = items.crop((index*16, 0, index*16+16, 16))
            paste_scaled(stages, icon, (x, y+42), 4)
            sd.text((x, y+115), caption, font=font(14), fill='#645d54')
            stages.paste(icon, (x+72, y+90), icon)
        for stage, im in enumerate(plants[k]):
            xx = 344+stage*132
            sd.rectangle((xx-8, y+32, xx+77, y+137), fill='#879b64')
            sd.rectangle((xx-8, y+112, xx+77, y+137), fill='#995b3b')
            paste_scaled(stages, im, (xx+2, y+4), 4)
    stages.save(REVIEW / 'preview.png')
    stages.save(ART / 'preview.png')

    garden = Image.new('RGB', (752, 358), '#eee2c8')
    gd = ImageDraw.Draw(garden)
    gd.text((24, 18), 'ЗРЕЛЫЕ РАСТЕНИЯ · ИГРОВОЙ МАСШТАБ ×4', font=font(22), fill='#252a30')
    for row, soil in enumerate(('#995b3b', '#704134')):
        yy = 76+row*136
        gd.rectangle((20, yy+30, 731, yy+120), fill=soil)
        for k in range(4):
            for repeat in range(2):
                paste_scaled(garden, plants[k][4], (36+k*176+repeat*64, yy-10), 4)
    garden.save(REVIEW / 'garden-preview.png')

    before_path = REVIEW / 'before/assets/Crops/herbalCrops.png'
    if before_path.is_file():
        old = Image.open(before_path).convert('RGBA')
        comparison = Image.new('RGB', (1040, 444), '#eee2c8')
        cd = ImageDraw.Draw(comparison)
        cd.text((24, 20), 'АПТЕКАРСКИЙ САД · БЫЛО / СТАЛО', font=font(27), fill='#354636')
        cd.text((24, 58), 'Одинаковый масштаб ×6 · размашистее листва · чётче цветной контур', font=font(18), fill='#645d54')
        for k in range(4):
            x = 16+k*256
            cd.rounded_rectangle((x, 94, x+246, 425), radius=10, fill='#ded1b3')
            first, second = LABELS[k].split(' ', 1)
            cd.text((x+13, 107), first, font=font(20), fill='#354636')
            cd.text((x+13, 131), second, font=font(20), fill='#354636')
            cd.rectangle((x+10, 166, x+236, 358), fill='#995b3b')
            cd.rectangle((x+10, 308, x+236, 358), fill='#704134')
            xx, yy = (k%2)*128+5*16, (k//2)*32
            before = old.crop((xx, yy, xx+16, yy+32))
            paste_scaled(comparison, before, (x+15, 168), 6)
            paste_scaled(comparison, plants[k][4], (x+135, 168), 6)
            cd.text((x+35, 379), 'Было', font=font(17), fill='#645d54')
            cd.text((x+151, 379), 'Стало', font=font(17), fill='#354636')
        comparison.save(REVIEW / 'comparison.png')


def export(install=False):
    REVIEW.mkdir(parents=True, exist_ok=True)
    out = ART / 'exports'
    out.mkdir(exist_ok=True)
    items = build_items()
    field, plants = build_crops()
    for im in (items, field):
        assert set(im.getchannel('A').get_flattened_data()) == {0, 255}
        assert len({p for p in im.get_flattened_data() if p[3]}) <= 64
    # Keep the large isolated assets AND the reduced unoutlined intermediates.
    for folder in ('isolated', 'reduced-before-outline'):
        (REVIEW / folder).mkdir(exist_ok=True)
    for kind, name in enumerate(NAMES):
        for stage, asset in enumerate(ASSETS):
            paintings(kind)[stage].save(REVIEW / 'isolated' / f'{name}-{asset}.png')
            reduced_assets()[0][kind*8+stage].save(REVIEW / 'reduced-before-outline' / f'{name}-{asset}.png')
        for index in (kind, kind+4):
            path = out / (name+('-seeds' if index >= 4 else '')+'.png')
            remember_before(path)
            items.crop((index*16, 0, index*16+16, 16)).save(path)
        for stage, im in enumerate(plants[kind]):
            path = out / f'{name}-stage-{stage}.png'
            remember_before(path)
            im.save(path)
    for name, im in (('herbalItems.png', items), ('herbalCrops.png', field)):
        remember_before(out / name)
        im.save(out / name)
    if install:
        for relative, im in (('assets/Items/herbalItems.png', items), ('assets/Crops/herbalCrops.png', field),
                             ('art/native-16/exports/herbalItems.png', items)):
            path = PACK / relative
            remember_before(path)
            im.save(path)
        report_path = PACK / 'art/native-16/report.json'
        if report_path.is_file():
            remember_before(report_path)
            report = json.loads(report_path.read_text(encoding='utf-8'))
            report['sheets']['herbalItems.png']['sha256'] = hashlib.sha256(items.tobytes()).hexdigest()
            report['herbalGarden'] = {'source': '../../scripts/painted_herbal_garden.py',
                                      'method': 'v10 broad sweeping mature foliage; large produce; 3x intermediate color sampling; saturated pixel bands',
                                      'outline': 'directional material-colored inner edge; no expansion',
                                      'colorSource': '../../scripts/refine_herbal_pixels.py', 'sources': '../herbal-garden/painted-v10/sources',
                                      'matureSource': '../herbal-garden/painted-v10/mature-portraits'}
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    remember_before(ART / 'preview.png')
    preview(items, plants)
    report = {'source': '../../../scripts/painted_herbal_garden.py', 'generation': 'built-in image_gen',
              'method': 'v9 lifecycle sheets + v10 broad sweeping mature foliage portraits -> area-filtered alpha -> 3x intermediate color detail sampled with NEAREST -> opaque-neighbor sharpening -> richer foliage value bands -> directional inner contour -> 48 interior + 16 material edge colors',
              'detailSampleScale': DETAIL_SAMPLE_SCALE,
              'sourceLayout': [SOURCE_COLUMNS, 8//SOURCE_COLUMNS],
              'colorSource': '../../../scripts/refine_herbal_pixels.py',
              'outline': 'directional material-colored inner edge; edge luminance >=60/255; no expansion', 'cropCell': [16, 32], 'itemCell': [16, 16],
              'frameMap': list(FRAME_MAP), 'installedInWorkspace': install,
              'sources': {name: {'size': list(Image.open(SOURCE / (name+'.png')).size),
                                 'sha256File': hashlib.sha256((SOURCE / (name+'.png')).read_bytes()).hexdigest()}
                          for name in NAMES},
              'maturePortraits': {name: {'size': list(Image.open(MATURE / (name+'.png')).size),
                                       'sha256File': hashlib.sha256((MATURE / (name+'.png')).read_bytes()).hexdigest()}
                                 for name in NAMES},
              'sheets': {name: {'size': list(im.size), 'colors': len({p for p in im.get_flattened_data() if p[3]}),
                                 'sha256Pixels': hashlib.sha256(im.tobytes()).hexdigest()}
                         for name, im in (('herbalItems.png', items), ('herbalCrops.png', field))}}
    (REVIEW / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Painted herbal garden: 4 large source sheets, 32 isolated paintings, 8 inventory icons, 24 crop stages.')
    print('Reduced to 16x16 / 16x32; saturated pixel bands, opaque-neighbor sharpening; binary alpha; <=64 colors.')
    print('Workspace assets installed.' if install else 'Exports only; --install updates workspace assets.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    export(parser.parse_args().install)
