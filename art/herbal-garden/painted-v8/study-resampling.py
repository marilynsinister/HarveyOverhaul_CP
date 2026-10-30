from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PACK / 'scripts'))
import painted_herbal_garden as g
from refine_herbal_pixels import render


def reduce(im, size, limit, baseline, factor):
    scale = min(limit[0]/im.width, limit[1]/im.height)
    target = (max(1, round(im.width*scale)), max(1, round(im.height*scale)))
    base = im.resize(target, Image.Resampling.LANCZOS)
    if factor:
        details = im.resize((target[0]*factor, target[1]*factor), Image.Resampling.LANCZOS).resize(target, Image.Resampling.NEAREST)
    else:
        details = im.resize(target, Image.Resampling.NEAREST)
    alpha = base.getchannel('A').point(lambda a: 255 if a >= 112 else 0)
    base.putdata([d[:3]+(a,) if a and d[3] >= 128 else b[:3]+(a,)
                  for b, d, a in zip(base.get_flattened_data(), details.get_flattened_data(), alpha.get_flattened_data())])
    base = base.crop(base.getbbox())
    result = Image.new('RGBA', size)
    result.alpha_composite(base, ((size[0]-base.width)//2, baseline-base.height))
    return result


def candidate(factor):
    raw = []
    limits = ((5, 4), (7, 8), (11, 15), (13, 22), (14, 26), (13, 21))
    for kind in range(4):
        source = g.paintings(kind)
        raw.extend(reduce(source[i], (16, 32), limits[i], 31, factor) for i in range(6))
        raw.append(reduce(source[6], (16, 16), (14, 14), 15, factor))
        raw.append(reduce(source[7], (16, 16), (13, 14), 15, factor))
    return raw, render(raw)


original_raw, original = g.reduced_assets()
variants = [('CURRENT', original)]
for factor in (3, 2, 0):
    raw, sprites = candidate(factor)
    assert all(a.getchannel('A').tobytes() == b.getchannel('A').tobytes() for a, b in zip(raw, original_raw))
    variants.append((f'DETAIL SAMPLES {factor or "NEAREST"}', sprites))
board = Image.new('RGB', (1040, 980), '#eadcbb')
d = ImageDraw.Draw(board)
f = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
for row, (label, sprites) in enumerate(variants):
    y = row*240
    d.text((20, y+10), label, font=f, fill='#354530')
    for kind in range(4):
        x = 16+kind*256
        d.rectangle((x+6, y+42, x+246, y+232), fill='#995b3b')
        im = sprites[kind*8+4].resize((96, 192), Image.Resampling.NEAREST)
        board.paste(im, (x+80, y+42), im)
board.save(Path(__file__).with_name('sampling-study.png'))
print('All candidate alpha masks match current crops/icons.')
