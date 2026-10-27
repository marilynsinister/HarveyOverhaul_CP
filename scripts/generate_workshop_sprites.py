"""Иконки «мастерской трав» (16×16, палитра памятных вещей из generate_keepsake_sprites.py).

  0 — сушёные травы (пучок, перевязанный бечёвкой), 1 — согревающий чай (кружка с имбирём),
  2 — травяной бальзам (баночка с серебряной крышкой).

Запуск:  python scripts/generate_workshop_sprites.py   → assets/Items/workshopItems.png, art/workshop-items-preview.png
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
INK = '#493729'
WOOD = '#96623f'
LIGHT = '#d7a46b'
PAPER = '#fff1ca'
SHADE = '#d9c49a'
GREEN = '#77905b'
DRY = '#a3a05a'
LILAC = '#9b84b5'
GOLD = '#e8b84a'
RED = '#bd665a'
METAL = '#b8c0cc'


def build():
    sheet = Image.new('RGBA', (48, 16))
    draw = ImageDraw.Draw(sheet)
    # 0. Пучок сушёных трав: стебли веером, бечёвка, сиреневые колокольчики.
    for x0, x1 in [(4, 7), (6, 7), (8, 8), (10, 9), (12, 9)]:
        draw.line((x0, 2, x1, 11), fill=INK)
    for x0, x1 in [(5, 7), (7, 8), (9, 8), (11, 9)]:
        draw.line((x0, 3, x1, 10), fill=DRY)
    for x, y in [(4, 2), (8, 1), (12, 2)]:
        draw.rectangle((x - 1, y, x + 1, y + 2), fill=LILAC)
    draw.point((6, 4), fill=GREEN)
    draw.point((10, 4), fill=GREEN)
    draw.rectangle((6, 10, 10, 11), fill=WOOD)
    draw.line((7, 12, 7, 15), fill=INK)
    draw.line((9, 12, 9, 15), fill=INK)
    draw.line((8, 12, 8, 15), fill=DRY)
    # 1. Согревающий чай: кружка, пар, ломтик имбиря на блюдце.
    x = 16
    for dx in (5, 8):
        draw.line((x + dx, 1, x + dx + 1, 3), fill=SHADE)
        draw.line((x + dx + 1, 3, x + dx, 5), fill=SHADE)
    draw.rectangle((x + 3, 6, x + 11, 13), fill=INK)
    draw.rectangle((x + 4, 7, x + 10, 12), fill=RED)
    draw.line((x + 4, 7, x + 10, 7), fill=GOLD)
    draw.rectangle((x + 11, 8, x + 13, 11), outline=INK)
    draw.line((x + 2, 14, x + 13, 14), fill=INK)
    draw.line((x + 3, 15, x + 12, 15), fill=SHADE)
    draw.ellipse((x + 6, 9, x + 8, 11), fill=GOLD)
    # 2. Травяной бальзам: стеклянная баночка, серебряная крышка, зелёная мазь, этикетка.
    x = 32
    draw.rectangle((x + 4, 3, x + 11, 5), fill=INK)
    draw.rectangle((x + 5, 4, x + 10, 4), fill=METAL)
    draw.rectangle((x + 3, 6, x + 12, 14), fill=INK)
    draw.rectangle((x + 4, 7, x + 11, 13), fill=GREEN)
    draw.line((x + 4, 7, x + 11, 7), fill=PAPER)
    draw.rectangle((x + 5, 9, x + 10, 12), fill=PAPER)
    draw.line((x + 6, 10, x + 9, 10), fill=LIGHT)
    draw.point((x + 7, 11), fill=LILAC)
    draw.line((x + 4, 15, x + 11, 15), fill=SHADE)
    path = ROOT / 'assets/Items/workshopItems.png'
    sheet.save(path)
    sheet.resize((288, 96), Image.Resampling.NEAREST).save(ROOT / 'art/workshop-items-preview.png')
    print('written', path)


if __name__ == '__main__':
    build()
