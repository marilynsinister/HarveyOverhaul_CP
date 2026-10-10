"""Генерирует иконки медицинских предметов и баффов мелких неприятностей (16x16, пиксель-арт).

    python scripts/generate_medical_item_sprites.py            # assets/Items/*.png
    python scripts/generate_medical_item_sprites.py --preview  # + увеличенные превью в scripts/_preview_*.png
"""
import sys

from PIL import Image

PALETTE = {
    ".": (0, 0, 0, 0),
    # контуры
    "o": (74, 48, 40, 255),      # тёплый тёмно-коричневый
    "O": (44, 60, 92, 255),      # холодный контур (лёд, металл)
    # белое / ткань
    "W": (255, 252, 242, 255),
    "w": (232, 224, 206, 255),
    "s": (196, 182, 160, 255),
    "S": (150, 134, 116, 255),
    # красный
    "r": (222, 64, 64, 255),
    "R": (166, 36, 50, 255),
    "L": (246, 120, 110, 255),
    "D": (110, 26, 40, 255),
    # янтарное стекло
    "A": (178, 104, 42, 255),
    "a": (128, 70, 30, 255),
    "h": (244, 190, 118, 255),
    # пробка
    "C": (214, 170, 116, 255),
    "c": (164, 120, 76, 255),
    # фольга
    "F": (188, 196, 212, 255),
    "f": (138, 146, 164, 255),
    "e": (96, 102, 118, 255),
    # таблетки
    "P": (255, 255, 255, 255),
    "p": (196, 214, 240, 255),
    # кружка / чай
    "M": (246, 236, 218, 255),
    "m": (206, 190, 166, 255),
    "g": (126, 168, 84, 255),
    "G": (82, 128, 58, 255),
    "t": (176, 150, 70, 255),
    "T": (138, 110, 46, 255),
    "v": (236, 240, 246, 170),
    # кожа
    "k": (244, 196, 150, 255),
    "K": (214, 154, 108, 255),
    "n": (176, 116, 78, 255),
    # дерево
    "b": (122, 82, 46, 255),
    # жёлтый / оранжевый
    "y": (255, 222, 82, 255),
    "Y": (236, 170, 40, 255),
    "z": (200, 110, 30, 255),
    "x": (40, 34, 36, 255),      # чёрные полоски пчелы
    # синий / лёд
    "i": (214, 238, 255, 255),
    "I": (140, 196, 240, 255),
    "j": (84, 140, 212, 255),
    "q": (110, 180, 255, 255),   # капля пота
    # серый
    "H": (88, 84, 92, 255),
}

ITEMS = [
    # 0 — чистый бинт
    [
        "................",
        "................",
        "....oooooo......",
        "...oWWWWWWo.....",
        "..oWWwwwwWWo....",
        ".oWWwooooWWwo...",
        ".oWwoSSSSowWo...",
        ".oWwoSnnSowWo...",
        ".oWwoSSSSowWoooo",
        ".oWWwooooWWwWWWo",
        ".owWWwwwwWWwwwwo",
        "..owWWWWWWwosSso",
        "..osswwwwssoooo.",
        "...oSssssSo.....",
        "....oooooo......",
        "................",
    ],
    # 1 — антисептик
    [
        "......oooo......",
        "......oCco......",
        "......oCco......",
        ".....oooooo.....",
        "......oAAo......",
        ".....oAhAAo.....",
        "....oAhAAAao....",
        "....oAhAAAao....",
        "....oWWWWWwo....",
        "....oWWrrWwo....",
        "....oWrrrrwo....",
        "....oWWrrWwo....",
        "....oWWWWWwo....",
        "....oAhAAAao....",
        ".....oaaaao.....",
        "......oooo......",
    ],
    # 2 — обезболивающее (блистер, одна таблетка выдавлена)
    [
        "................",
        ".oooooooooooooo.",
        ".oFFFFFFFFFFFfo.",
        ".oFooooFFoooofo.",
        ".oFoPPoFFoPPofo.",
        ".oFoppoFFoppofo.",
        ".oFooooFFoooofo.",
        ".oFFFFFFFFFFFfo.",
        ".oFooooFFoooofo.",
        ".oFoPPoFFoeeofo.",
        ".oFoppoFFoeeofo.",
        ".oFooooFFoooofo.",
        ".oFFFFFFFFFFFfo.",
        ".offfffffffffo..",
        ".ooooooooooooo..",
        "................",
    ],
    # 3 — травяной сбор (кружка)
    [
        ".....v...v......",
        "....v...v.......",
        ".....v...v......",
        "....v...v.......",
        "..oooooooooo....",
        ".oMMMMMMMMMMo...",
        ".oMttggtttTMo...",
        ".omTtGgttTTmoooo",
        ".oMMMMMMMMMMoMMo",
        ".oMMgGMMMMMmo.mo",
        ".oMgGGgMMMMmo.mo",
        ".oMMgGMMMMMmoMmo",
        ".oMMMMMMMMmmoooo",
        "..omMMMMMmmo....",
        "...oooooooo.....",
        "................",
    ],
    # 4 — аптечка
    [
        "................",
        "................",
        "......oooo......",
        ".....oHHHHo.....",
        ".....oHooHo.....",
        "..oooooooooooo..",
        "..oLLLLLLLLLLo..",
        "..orrrrrrrrrRo..",
        "..orrrrWWrrrRo..",
        "..orrrrWWrrrRo..",
        "..orrWWWWWWrRo..",
        "..orrWWWWWWrRo..",
        "..orrrrWWrrrRo..",
        "..orrrrWWrrrRo..",
        "..oRRRRRRRRRDo..",
        "..oooooooooooo..",
    ],
]

BUFF_ICONS = [
    # 0 — закалка (сердце с пластырем)
    [
        "................",
        "................",
        "..ooo....ooo....",
        ".oLLro..oLrro...",
        "oLLrrrooLrrrro..",
        "oLrrrrrrrrrrRo..",
        "orrrrrrrwwrrRo..",
        "orrrrrrwWWwrRo..",
        ".orrrrwWWwrRo...",
        ".oRrrwWWwrrRo...",
        "..oRrrwwrrRo....",
        "...oRrrrrRo.....",
        "....oRrRRo......",
        ".....oRRo.......",
        "......oo........",
        "................",
    ],
    # 1 — заноза (палец с щепкой)
    [
        "................",
        "................",
        "...........b....",
        "..........bb....",
        ".........bb.....",
        "..ooooooobooooo.",
        ".okkkkkkbkkoWWo.",
        "okkkkkkkrkkowwKo",
        "okkkkkkkkkkoooKo",
        "oKkkkkkkkkkkKKno",
        ".oKKKKKKKKKKKno.",
        "..ooooooooooooo.",
        "................",
        "................",
        "................",
        "................",
    ],
    # 2 — укус пчелы
    [
        "................",
        "....ooo..ooo....",
        "...oiiio.oiiio..",
        "...oiIIiooIIio..",
        "....oiIIoIIio...",
        ".....ooooooo....",
        "....oyyxxyyxo...",
        "...oyyyxxyyxYo..",
        "..ooyyyxxyyxYzo.",
        "..oxoyyxxyyxYzo.",
        "...ooYYxxYYxzo..",
        ".....oozzzzoo...",
        ".......oooo.....",
        "................",
        "................",
        "................",
    ],
    # 3 — солнечный удар (солнце и капля пота)
    [
        ".......Y........",
        "...Y...Y...Y....",
        "....Y.....Y.....",
        "......ooo.......",
        ".....oyyyo......",
        "YY..oyyyyyo..YY.",
        "....oyyyyYo.....",
        ".....oYYYo......",
        "....Y.ooo.Y.....",
        "...Y...Y...Y....",
        ".......Y..oo....",
        "..........oqo...",
        ".........oqiqo..",
        ".........oqqjo..",
        "..........ojo...",
        "...........o....",
    ],
    # 4 — обморожение (снежинка)
    [
        "................",
        ".......O........",
        "....O..i..O.....",
        ".....OIiIO......",
        "...O..IiI..O....",
        "....OI.i.IO.....",
        ".OiiiiiiiiiiiO..",
        "....OI.i.IO.....",
        "...O..IiI..O....",
        ".....OIiIO......",
        "....O..i..O.....",
        ".......O........",
        "................",
        "................",
        "................",
        "................",
    ],
]


def render(icons):
    sheet = Image.new("RGBA", (16 * len(icons), 16), (0, 0, 0, 0))
    for index, rows in enumerate(icons):
        assert len(rows) == 16, index
        for y, row in enumerate(rows):
            assert len(row) == 16, (index, y, row)
            for x, ch in enumerate(row):
                sheet.putpixel((index * 16 + x, y), PALETTE[ch])
    return sheet


def preview(sheet, path):
    bg = Image.new("RGBA", sheet.size, (120, 120, 140, 255))
    bg.alpha_composite(sheet)
    bg.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(path)


def main():
    items = render(ITEMS)
    buffs = render(BUFF_ICONS)
    items.save("assets/Items/medicalItems.png")
    buffs.save("assets/Items/mishapBuffIcons.png")
    if "--preview" in sys.argv:
        preview(items, "scripts/_preview_items.png")
        preview(buffs, "scripts/_preview_buffs.png")


if __name__ == "__main__":
    main()
