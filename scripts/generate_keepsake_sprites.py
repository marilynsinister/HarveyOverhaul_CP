"""Пять памятных вещей в пиксельной палитре существующих предметов (16 px на тайл)."""
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


def frame(draw, x):
    draw.rectangle((x + 2, 2, x + 29, 30), fill=INK)
    draw.rectangle((x + 3, 3, x + 28, 29), fill=WOOD)
    draw.line((x + 3, 3, x + 28, 3), fill=LIGHT)
    draw.line((x + 3, 3, x + 3, 28), fill=LIGHT)
    draw.rectangle((x + 5, 5, x + 26, 26), fill=PAPER)
    draw.line((x + 5, 27, x + 26, 27), fill=SHADE)


def person(draw, x, y, color, small=False):
    draw.rectangle((x, y, x + 3, y + 3), fill='#dfa477')
    draw.line((x, y, x + 3, y), fill=INK)
    draw.rectangle((x, y + 4, x + 3, y + (7 if small else 9)), fill=color)
    draw.point((x, y + (8 if small else 10)), fill=INK)
    draw.point((x + 3, y + (8 if small else 10)), fill=INK)


def build():
    sheet = Image.new('RGBA', (160, 32))
    draw = ImageDraw.Draw(sheet)
    # 0. Детский рисунок: люди, большой дом и кривая птица.
    frame(draw, 0)
    draw.line((7, 23, 24, 23), fill=GREEN, width=2)
    draw.line((7, 10, 10, 7, 13, 10), fill=RED)
    draw.rectangle((8, 10, 12, 12), outline=RED)
    person(draw, 7, 13, WOOD)
    person(draw, 12, 13, GREEN)
    person(draw, 17, 13, RED)
    person(draw, 22, 16, BLUE, True)
    draw.line((18, 8, 20, 9, 22, 8), fill=BLUE)
    # 2. Самолёт: отдельная модель 2x1 с деревянной подставкой.
    x = 32
    draw.rectangle((x + 5, 13, x + 26, 14), fill=INK)
    draw.line((x + 7, 12, x + 24, 12), fill=LIGHT)
    draw.line((x + 15, 10, x + 15, 12), fill=WOOD, width=2)
    draw.polygon([(x + 2, 7), (x + 10, 6), (x + 15, 1), (x + 18, 1),
                  (x + 17, 6), (x + 25, 6), (x + 27, 3), (x + 29, 3),
                  (x + 28, 8), (x + 17, 9), (x + 18, 11), (x + 15, 11),
                  (x + 11, 9), (x + 3, 9)], fill=INK)
    draw.line((x + 4, 7, x + 26, 7), fill=PAPER, width=2)
    draw.line((x + 12, 6, x + 16, 2), fill=BLUE, width=2)
    draw.point((x + 7, 7), fill=BLUE)
    draw.point((x + 10, 7), fill=BLUE)
    draw.point((x + 27, 5), fill=RED)
    # 4. Засушенный цветок под стеклом.
    x = 64
    frame(draw, x)
    draw.line((x + 17, 21, x + 15, 12), fill=GREEN)
    draw.polygon([(x + 16, 18), (x + 12, 15), (x + 12, 18)], fill=GREEN)
    draw.polygon([(x + 17, 20), (x + 21, 16), (x + 21, 19)], fill=GREEN)
    draw.rectangle((x + 12, 8, x + 18, 12), fill=RED)
    draw.rectangle((x + 14, 6, x + 16, 14), fill=RED)
    draw.rectangle((x + 14, 9, x + 16, 11), fill=LIGHT)
    draw.line((x + 10, 24, x + 21, 24), fill=SHADE)
    # 6. Записка: два почерка, скреплённые маленьким сердцем.
    x = 96
    frame(draw, x)
    for y, end in [(9, 22), (12, 21), (15, 23), (18, 18)]:
        draw.line((x + 8, y, x + end, y), fill=BLUE)
    draw.line((x + 8, 23, x + 13, 21, x + 15, 23), fill=INK)
    draw.polygon([(x + 19, 21), (x + 21, 19), (x + 23, 21), (x + 21, 24)], fill=RED)
    # 8. Семейная фотография: четыре фигуры на фоне неба.
    x = 128
    frame(draw, x)
    draw.rectangle((x + 6, 6, x + 25, 24), fill='#b5c5bd')
    draw.rectangle((x + 6, 21, x + 25, 24), fill=GREEN)
    person(draw, x + 7, 11, WOOD)
    person(draw, x + 13, 10, BLUE)
    person(draw, x + 20, 12, RED)
    person(draw, x + 15, 17, PAPER, True)
    path = ROOT / 'assets/Furniture/keepsakes.png'
    path.parent.mkdir(exist_ok=True)
    sheet.save(path)
    preview = ROOT / 'art/keepsakes-preview.png'
    preview.parent.mkdir(exist_ok=True)
    sheet.resize((960, 192), Image.Resampling.NEAREST).save(preview)
    print('written', path)


if __name__ == '__main__':
    build()
