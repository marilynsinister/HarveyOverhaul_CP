"""Иконки предметов линии «Позывной» (16×16, палитра памятных вещей из generate_keepsake_sprites.py).

  0 — рация Харви, 1–3 — записки для Харви («Спасибо», «Скучаю», «Приходи на ужин»),
  4 — корзина для пикника, 5 — квитанция за воздушный шар.

Запуск:  python scripts/generate_courtship_sprites.py   → assets/Items/courtshipItems.png, art/courtship-items-preview.png
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
INK = '#493729'
WOOD = '#96623f'
LIGHT = '#d7a46b'
PAPER = '#fff1ca'
SHADE = '#d9c49a'
BLUE = '#668aa6'
RED = '#bd665a'
GREEN = '#77905b'
GOLD = '#e8b84a'
METAL = '#8a929e'
DARK = '#3c4250'


def note(draw, x, mark):
    """Сложенный листок с сургучной меткой: цвет и знак отличают три записки."""
    draw.polygon([(x + 2, 4), (x + 13, 3), (x + 14, 13), (x + 3, 14)], fill=INK)
    draw.polygon([(x + 3, 5), (x + 12, 4), (x + 13, 12), (x + 4, 13)], fill=PAPER)
    draw.line((x + 4, 7, x + 11, 6), fill=SHADE)
    draw.line((x + 4, 9, x + 10, 8), fill=SHADE)
    color, shape = mark
    draw.ellipse((x + 8, 9, x + 13, 14), fill=INK)
    draw.ellipse((x + 9, 10, x + 12, 13), fill=color)
    if shape == 'heart':
        draw.point((x + 10, 11), fill=PAPER)
        draw.point((x + 11, 11), fill=PAPER)
    elif shape == 'dot':
        draw.point((x + 10, 11), fill=PAPER)
    else:  # чашка: ужин
        draw.line((x + 10, 11, x + 11, 11), fill=PAPER)
        draw.point((x + 10, 12), fill=PAPER)


def build():
    sheet = Image.new('RGBA', (96, 16))
    draw = ImageDraw.Draw(sheet)
    # 0. Рация: тёмный корпус, антенна, сетка динамика и зелёный огонёк «канал семь».
    draw.line((10, 0, 10, 4), fill=INK)
    draw.point((10, 0), fill=RED)
    draw.rectangle((4, 4, 12, 15), fill=INK)
    draw.rectangle((5, 5, 11, 14), fill=DARK)
    draw.rectangle((6, 6, 10, 8), fill=GREEN)
    draw.point((7, 7), fill=PAPER)
    for y in (10, 12):
        draw.line((6, y, 10, y), fill=METAL)
    draw.line((5, 5, 5, 13), fill=METAL)
    # 1–3. Записки: «Спасибо» — сердце, «Скучаю» — синяя точка, «Ужин» — чашка.
    note(draw, 16, (RED, 'heart'))
    note(draw, 32, (BLUE, 'dot'))
    note(draw, 48, (GOLD, 'cup'))
    # 4. Корзина для пикника: плетёнка, клетчатая салфетка, ручка.
    x = 64
    draw.arc((x + 3, 1, x + 12, 11), 180, 360, fill=INK)
    draw.arc((x + 4, 2, x + 11, 10), 180, 360, fill=WOOD)
    draw.polygon([(x + 1, 7), (x + 14, 7), (x + 13, 15), (x + 2, 15)], fill=INK)
    draw.polygon([(x + 2, 8), (x + 13, 8), (x + 12, 14), (x + 3, 14)], fill=WOOD)
    for yy in (10, 12):
        draw.line((x + 3, yy, x + 12, yy), fill=LIGHT)
    for xx in (x + 3, x + 7, x + 11):
        draw.rectangle((xx, 6, xx + 1, 7), fill=RED)
    for xx in (x + 5, x + 9):
        draw.rectangle((xx, 6, xx + 1, 7), fill=PAPER)
    # 5. Квитанция: бланк с печатью и маленьким шаром.
    x = 80
    draw.rectangle((x + 2, 2, x + 13, 14), fill=INK)
    draw.rectangle((x + 3, 3, x + 12, 13), fill=PAPER)
    draw.ellipse((x + 4, 4, x + 9, 9), fill=RED)
    draw.line((x + 5, 5, x + 6, 5), fill=GOLD)
    draw.line((x + 6, 9, x + 6, 10), fill=INK)
    draw.line((x + 7, 9, x + 7, 10), fill=INK)
    draw.rectangle((x + 5, 10, x + 8, 11), fill=WOOD)
    draw.line((x + 4, 12, x + 11, 12), fill=SHADE)
    draw.ellipse((x + 9, 9, x + 12, 12), outline=BLUE)
    path = ROOT / 'assets/Items/courtshipItems.png'
    sheet.save(path)
    preview = ROOT / 'art/courtship-items-preview.png'
    sheet.resize((576, 96), Image.Resampling.NEAREST).save(preview)
    print('written', path)


if __name__ == '__main__':
    build()
