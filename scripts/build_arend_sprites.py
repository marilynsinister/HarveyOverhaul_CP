"""Портрет, спрайт и иконки Аренда (отец Харви) из нарисованных исходников.

Исходники (рисунок автора мода) лежат в art/arend/:
  portraits.webp — 12 портретов сеткой 2×6 на прозрачном фоне;
  sprites.webp   — спрайт-лист 4×14 (крупный пиксель-арт).

Результат:
  assets/Character/Arend/Portrait.png  128×384 — 12 портретов по 64×64 (ванильный размер);
  assets/Character/Arend/Sprite.png    64×448  — 14 рядов по 4 кадра 16×32;
  *_Winter.png — те же картинки (зимнего наряда пока нет);
  art/arend/Arend_HD.png 512×1536 — HD-портрет 256×256 для Portraiture (deploy.sh кладёт в активный пак);
  assets/Items/arendItems.png — иконки: шкатулка, чай «номер семь», чашка Элин.

Портреты ($N в репликах): 0 спокойный, 1 улыбка, 2 грусть, 3 задумчивый, 4 тёплый, 5 строгий,
6 слушает, 7 удивлён, 8 встревожен (говорит), 9 наушники, 10 наушники (говорит), 11 мягкая улыбка.

Кадры спрайта (номер = ряд × 4 + столбец), анимации — Data/animationDescriptions в build_arend.py:
  0–3 вниз, 4–7 вправо, 8–11 вверх, 12–15 влево (зеркало ряда «вправо»);
  16–19 стоит / портфель, 20–23 рука у груди, рука у подбородка, портфель;
  24 книга, 25 стоит, 26 спиной, 27 стоит; 28–29 читает книгу, 30 объясняет (рука вверх), 31 думает сбоку;
  32 стоит, 33 смотрит в сторону, 34 рука у подбородка, 35 чашка сбоку;
  36–38 спиной (в кресле), 39 чашка; 40–43 в кресле (спокоен, руки, думает, вполоборота);
  44–45 стоит, 46 руки скрещены, 47 пьёт чай; 48 чашка в руках, 49 ладони вместе, 50 жест сбоку;
  52–55 разговор вполоборота (жестикулирует, лицом влево).

В исходнике 24–27, 36–39, 48–50 и 52–55 укорочены (24–27 px вместо 29–31).
51 пуст. Эти кадры сохраняют индексы, но не используются в стоячих анимациях:
растягивание бюста до полного роста исказило бы пропорции. Безопасные чтение —
28/29, чай — 47, отдых стоя — 44, птицы — 33. Кадры кресла 40–43 — только дома.

Запуск:  python -I scripts/build_arend_sprites.py
"""
import os
import shutil

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'art', 'arend')
OUT = os.path.join(ROOT, 'assets', 'Character', 'Arend')

# Сетка спрайт-листа sprites.webp (границы найдены по альфе; ряды 9/10 и 12/13 соприкасаются).
S_COLS = [(186, 271), (271, 357), (357, 443), (443, 532)]
S_ROWS = [(0, 155), (155, 299), (299, 448), (448, 599), (599, 748), (748, 897), (897, 1031),
          (1031, 1178), (1178, 1330), (1330, 1460), (1460, 1604), (1604, 1760), (1760, 1879), (1879, 2000)]
# Сетка портретов portraits.webp: 2 столбца × 6 рядов.
P_COLS = [(0, 334), (334, 667)]
P_ROWS = [(0, 340), (340, 673), (673, 1006), (1006, 1339), (1339, 1671), (1671, 2000)]

FIGURE_PX = 29      # рост стоящей фигуры в кадре 16×32 (как у ванильных NPC)
PALETTE_SIZE = 40   # общий палитровый набор — чтобы после уменьшения пиксели были чёткими


def alpha_bbox(cell, threshold=128):
    a = np.array(cell)[..., 3]
    ys, xs = np.nonzero(a >= threshold)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def sprite_cells(src):
    cells = {}
    for r, (y0, y1) in enumerate(S_ROWS):
        for c, (x0, x1) in enumerate(S_COLS):
            cell = src.crop((x0, y0, x1, y1))
            box = alpha_bbox(cell)
            if box and (box[2] - box[0]) * (box[3] - box[1]) > 1500:
                cells[(r, c)] = cell.crop(box)
    return cells


def standing_scale(cells):
    heights = sorted(cells[(r, c)].height for r in range(3) for c in range(4))
    return FIGURE_PX / heights[len(heights) // 2]


def to_frame(fig, scale):
    w = max(1, round(fig.width * scale))
    h = max(1, round(fig.height * scale))
    small = fig.resize((w, h), Image.BOX)
    frame = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    # Ноги — на нижней строке кадра, фигура по центру; шире 16 px (кресло) — обрезается по краям.
    frame.alpha_composite(small, ((16 - w) // 2, 32 - h)) if w <= 16 else frame.alpha_composite(
        small.crop(((w - 16) // 2, 0, (w - 16) // 2 + 16, h)), (0, 32 - h))
    px = np.array(frame).astype(float)
    solid = px[..., 3] >= 110
    # Чуть больше контраста: после уменьшения средние тона сливаются.
    rgb = px[..., :3]
    rgb[:] = np.clip((rgb - 110) * 1.18 + 116, 0, 255)
    # Тёмный контур по краю силуэта, как у ванильных спрайтов.
    pad = np.pad(solid, 1)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    edge = solid & ~inner
    rgb[edge] = rgb[edge] * 0.42
    px[..., 3] = np.where(solid, 255, 0)
    return Image.fromarray(px.astype(np.uint8))


def unify_palette(frames):
    """Общая палитра для всех кадров: убирает «мыло» от уменьшения, пиксели становятся чёткими."""
    strip = Image.new('RGBA', (16 * len(frames), 32))
    for i, f in enumerate(frames):
        strip.paste(f, (16 * i, 0))
    rgb = strip.convert('RGB')
    pal = rgb.quantize(colors=PALETTE_SIZE, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = []
    for f in frames:
        q = f.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE).convert('RGBA')
        qa = np.array(q)
        qa[..., 3] = np.array(f)[..., 3]
        qa[qa[..., 3] == 0] = 0
        out.append(Image.fromarray(qa))
    return out


def build_sprite():
    src = Image.open(os.path.join(ART, 'sprites.webp')).convert('RGBA')
    cells = sprite_cells(src)
    scale = standing_scale(cells)
    rows = len(S_ROWS)
    order = []
    for r in range(rows):
        for c in range(4):
            if r == 3:
                key = (1, c)   # влево — зеркало «вправо»: в исходном ряду 3 кадры смотрят по-разному
            else:
                key = (r, c)
            order.append((key, r == 3))
    blank = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    frames = []
    for key, mirror in order:
        if key not in cells:
            frames.append(blank)
            continue
        fig = cells[key].transpose(Image.Transpose.FLIP_LEFT_RIGHT) if mirror else cells[key]
        frames.append(to_frame(fig, scale))
    frames = unify_palette(frames)
    sheet = Image.new('RGBA', (64, 32 * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % 4) * 16, (i // 4) * 32))
    os.makedirs(OUT, exist_ok=True)
    for name in ('Sprite.png', 'Sprite_Winter.png'):
        sheet.save(os.path.join(OUT, name))
    print('ok Sprite', sheet.size, f'scale={scale:.3f}')


def build_portraits():
    src = Image.open(os.path.join(ART, 'portraits.webp')).convert('RGBA')
    sd = Image.new('RGBA', (128, 64 * len(P_ROWS)), (0, 0, 0, 0))
    hd = Image.new('RGBA', (512, 256 * len(P_ROWS)), (0, 0, 0, 0))
    for r, (y0, y1) in enumerate(P_ROWS):
        for c, (x0, x1) in enumerate(P_COLS):
            cell = src.crop((x0, y0, x1, y1))
            bx0, by0, bx1, by1 = alpha_bbox(cell, threshold=40)
            # Квадрат по нижнему краю бюста, лицо по центру.
            side = max(bx1 - bx0, by1 - by0)
            cx = (bx0 + bx1) // 2
            square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
            square.alpha_composite(cell.crop((bx0, by0, bx1, by1)), (side // 2 - (cx - bx0), side - (by1 - by0)))
            hd.alpha_composite(square.resize((256, 256), Image.LANCZOS), (256 * c, 256 * r))
            sd.alpha_composite(square.resize((64, 64), Image.LANCZOS), (64 * c, 64 * r))
    for name in ('Portrait.png', 'Portrait_Winter.png'):
        sd.save(os.path.join(OUT, name))
    hd.save(os.path.join(ART, 'Arend_HD.png'))
    print('ok Portrait', sd.size, 'HD', hd.size)


# Иконки предметов 16×16: шкатулка, жестянка чая «номер семь», чашка Элин.
ICONS = [
    # шкатулка: дерево, латунный крючок
    ['................',
     '................',
     '................',
     '...oooooooooo...',
     '..oLLLLLLLLLLo..',
     '..oLWWWWWWWWLo..',
     '..oooooooooooo..',
     '..oDDDDggDDDDo..',
     '..oWWWWgyWWWWo..',
     '..oWWWWWWWWWWo..',
     '..oWWWWWWWWWWo..',
     '..oDDDDDDDDDDo..',
     '..oooooooooooo..',
     '................',
     '................',
     '................'],
    # жестянка чая: зелёная, бумажная этикетка с «7»
    ['................',
     '.....oooooo.....',
     '....oSSSSSSo....',
     '....oooooooo....',
     '....oGGGGGGo....',
     '....oGppppGo....',
     '....oGp77pGo....',
     '....oGpp7pGo....',
     '....oGpp7pGo....',
     '....oGppppGo....',
     '....oGGGGGGo....',
     '....oKKKKKKo....',
     '....oooooooo....',
     '................',
     '................',
     '................'],
    # чашка: белый фарфор, синие колокольчики
    ['................',
     '................',
     '................',
     '..oooooooooo....',
     '..oCCCCCCCCo....',
     '..oCbCCbCCbooo..',
     '..oCCCCCCCCo.o..',
     '..oCCbCCbCCo.o..',
     '...oCCCCCCooo...',
     '...oCCCCCCo.....',
     '....oooooo......',
     '..oooooooooo....',
     '..ossssssssso...',
     '...oooooooooo...',
     '................',
     '................'],
]
PALETTE = {
    'o': (52, 30, 24), 'L': (176, 116, 64), 'W': (140, 86, 46), 'D': (104, 62, 34), 'g': (210, 170, 60),
    'y': (250, 222, 120), 'S': (190, 196, 200), 'G': (58, 120, 72), 'p': (236, 222, 186), '7': (120, 40, 40),
    'K': (40, 80, 50), 'C': (246, 244, 236), 'b': (70, 100, 190), 's': (214, 210, 200),
}


def build_icons():
    path = os.path.join(ROOT, 'assets', 'Items', 'arendItems.png')
    curated = os.path.join(ROOT, 'art', 'items-stardew', 'exports', 'arendItems.png')
    if os.path.isfile(curated):
        shutil.copy2(curated, path)
        print('ok', path, '(curated Stardew sprites)')
        return
    im = Image.new('RGBA', (16 * len(ICONS), 16), (0, 0, 0, 0))
    for i, rows in enumerate(ICONS):
        assert len(rows) == 16 and all(len(r) == 16 for r in rows), i
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != '.':
                    im.putpixel((16 * i + x, y), (*PALETTE[ch], 255))
    im.save(path)
    print('ok', path)


def main():
    build_icons()
    build_portraits()
    build_sprite()


if __name__ == '__main__':
    main()
