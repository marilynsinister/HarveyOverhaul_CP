"""Генерирует assets/Items/medicalItems.png (16x16 иконки медицинских предметов).

    python scripts/generate_medical_item_sprites.py
"""
from PIL import Image

PALETTE = {
    ".": (0, 0, 0, 0),
    "k": (58, 38, 42, 255),      # контур
    "w": (250, 246, 236, 255),   # белый
    "c": (226, 216, 196, 255),   # кремовая тень
    "s": (190, 176, 152, 255),   # тень бинта
    "r": (214, 52, 60, 255),     # красный
    "R": (150, 30, 44, 255),     # тёмно-красный
    "b": (150, 92, 44, 255),     # коричневое стекло
    "B": (100, 58, 30, 255),     # тёмное стекло
    "h": (212, 150, 88, 255),    # блик стекла
    "o": (196, 150, 104, 255),   # пробка
    "g": (196, 204, 212, 255),   # блистер
    "G": (140, 150, 162, 255),   # тень блистера
    "p": (255, 255, 255, 255),   # таблетка
    "u": (120, 170, 230, 255),   # голубая таблетка
    "l": (110, 170, 70, 255),    # чай / лист
    "L": (60, 120, 50, 255),     # тёмный лист
    "v": (232, 236, 240, 160),   # пар
    "m": (236, 228, 214, 255),   # кружка
    "M": (180, 164, 146, 255),   # тень кружки
}

ICONS = [
    # 0 — чистый бинт
    [
        "................",
        "................",
        "................",
        "....kkkkkk......",
        "...kwwwwwwk.....",
        "..kwcckkccwk....",
        "..kwckssskwk....",
        "..kwcksssk.kkkkk",
        "..kwckssskwwwwwk",
        "..kwcckkccwccwck",
        "..kcwwwwwwcwwwck",
        "..kscccccsckkkk.",
        "...ksssssk......",
        "....kkkkkk......",
        "................",
        "................",
    ],
    # 1 — антисептик
    [
        "......kkkk......",
        "......kook......",
        "......kook......",
        ".....kkkkkk.....",
        "......kbbk......",
        ".....kbhbbk.....",
        "....kbhbbbBk....",
        "....kwwwwwwk....",
        "....kwwrrwwk....",
        "....kwrrrrwk....",
        "....kwwrrwwk....",
        "....kwwwwwwk....",
        "....kbhbbbBk....",
        "....kbbbbbBk....",
        ".....kkkkkk.....",
        "................",
    ],
    # 2 — обезболивающее (блистер)
    [
        "................",
        "................",
        "..kkkkkkkkkkkk..",
        "..kggggggggggk..",
        "..kgkkgkkgkkgk..",
        "..kkppkuukppkk..",
        "..kkppkuukppkk..",
        "..kgkkgkkgkkgk..",
        "..kggggggggggk..",
        "..kgkkgkkgkkgk..",
        "..kkuukppkuukk..",
        "..kkuukppkuukk..",
        "..kgkkgkkgkkgk..",
        "..kGGGGGGGGGGk..",
        "..kkkkkkkkkkkk..",
        "................",
    ],
    # 3 — травяной сбор (кружка)
    [
        "......v...v.....",
        ".....v...v......",
        "......v...v.....",
        ".....v...v......",
        "...kkkkkkkk.....",
        "..kllllllllk....",
        "..kmLlllLlmkkk..",
        "..kmmmmmmmmk.mk.",
        "..kmmmllmmmk.mk.",
        "..kmmlLLlmmk.mk.",
        "..kmmmllmmmkkk..",
        "..kmmmmmmmMk....",
        "...kMMMMMMk.....",
        "....kkkkkk......",
        "................",
        "................",
    ],
    # 4 — аптечка
    [
        "................",
        "......kkkk......",
        ".....k....k.....",
        ".....k....k.....",
        "..kkkkkkkkkkkk..",
        "..krrrrrrrrrrk..",
        "..krrrrwwrrrrk..",
        "..krrrrwwrrrrk..",
        "..krrwwwwwwrrk..",
        "..krrwwwwwwrrk..",
        "..krrrrwwrrrrk..",
        "..krrrrwwrrrrk..",
        "..kRRRRRRRRRRk..",
        "..kkkkkkkkkkkk..",
        "................",
        "................",
    ],
]


def main():
    sheet = Image.new("RGBA", (16 * len(ICONS), 16), (0, 0, 0, 0))
    for index, rows in enumerate(ICONS):
        assert len(rows) == 16, index
        for y, row in enumerate(rows):
            assert len(row) == 16, (index, y, row)
            for x, ch in enumerate(row):
                sheet.putpixel((index * 16 + x, y), PALETTE[ch])
    sheet.save("assets/Items/medicalItems.png")
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save("scripts/_medicalItems_preview.png")


if __name__ == "__main__":
    main()
