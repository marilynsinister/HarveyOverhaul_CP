"""Native 16x16 pixel sources. No sampling, downscaling or image-generation input.

python scripts/draw_native_icons.py --install
All runtime icons are authored at 16 pixels. Only preview() enlarges them.
Existing buff recipes supply the subject vocabulary, not rendered bitmaps.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image, ImageDraw, ImageFont
import generate_buff_icons as buffs
from native_anatomy import replacements as anatomy_replacements

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK.parent
ART = PACK / "art/native-16"
OUT = ART / "exports"
BACKUP = ART / "before"
INK = (48, 30, 37, 255)
COLORS = {
    ".": (0, 0, 0, 0), "o": INK,
    "W": "fff3d3", "w": "e6d5ae", "s": "b7a184", "S": "776477",
    "r": "dd574a", "R": "9e3544", "p": "f39179", "d": "652940",
    "g": "78a34d", "G": "467344", "l": "bbcf72", "D": "304e3c",
    "b": "9d603f", "B": "643e35", "h": "d79a59", "H": "f0c17d",
    "y": "ffdf7d", "a": "e9a54d", "A": "b36b3c",
    "i": "bce3e5", "I": "79b9cd", "j": "4d81af", "J": "354e7b",
    "v": "b19aca", "V": "786491", "n": "4f3f6e", "N": "35304f",
    "k": "efba88", "K": "cb8b68", "t": "a96253",
    "f": "bbc5c5", "F": "eff0d9", "e": "82939f",
    "q": "54a7a2", "Q": "356978",
}
COLORS = {key: tuple(bytes.fromhex(value)) + (255,) if isinstance(value, str) else value
          for key, value in COLORS.items()}


def pixels(text):
    """One source character is exactly one output pixel, including transparency."""
    rows = text.strip().split()
    assert len(rows) == 16 and all(len(row) == 16 for row in rows), [len(row) for row in rows]
    image = Image.new("RGBA", (16, 16))
    image.putdata([COLORS[char] for row in rows for char in row])
    # Handles and other one-pixel holes also need ink on their inner edges.
    source = image.copy()
    for y in range(16):
        for x in range(16):
            if source.getpixel((x, y))[3] and any(
                not (0 <= nx < 16 and 0 <= ny < 16) or not source.getpixel((nx, ny))[3]
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
            ):
                image.putpixel((x, y), INK)
    return image


# Medical inventory. Explicit internal contour separates rolled gauze, glass,
# metal, pottery and leather. Each design has its own silhouette at actual 16px.
MEDICAL = [pixels(source) for source in [
    """
    ................
    ................
    ....oooooo......
    ...oWWWWWWo.....
    ..oWWWwwwWWo....
    .oWWwoooowWwo...
    .oWwoSSSSowwo...
    .oWwoSooSowwo...
    .oWwoSooSowwo...
    .oWWwoSSowwwooo.
    ..oWWwooWWWwWWo.
    ..oswWWWWwwsWwo.
    ...oswwwwssooo..
    ....oooooo......
    ................
    ................
    """,
    """
    ................
    ......oooo......
    .....ohhhho.....
    .....obbbbo.....
    ......oooo......
    .....oHaAAo.....
    ....oHaaAAAo....
    ....oHaAAAbo....
    ....oWWwwwwo....
    ....oWWrrwwo....
    ....oWrrrrwo....
    ....oWWrrwwo....
    ....oHaaAAbo....
    .....oAAAbo.....
    ......oooo......
    ................
    """,
    """
    ................
    ................
    ....ooooooo.....
    ...oFFFFFFfo....
    ..oFoooFooofo...
    ..oFoWwoWwofo...
    ..oFowsoWsofo...
    ..oFeooeooefo...
    ..oFFFFFFFFfo...
    ..oFoooFooofo...
    ..oFoWwoSoofo...
    ..oFowsoSoofo...
    ..oFeooeooefo...
    ...oeeeeeeeo....
    ....ooooooo.....
    ................
    """,
    """
    ................
    .....oo..oo.....
    ....owo.owo.....
    .....oo..oo.....
    ................
    ...oooooooo.....
    ..oWagGGgaWo....
    ..oWAAggAAwooo..
    ..oWWWWWWwwoWwo.
    ..oWWgWWWwwo.wo.
    ..oWgGgWWwwo.wo.
    ..owWgWWwwwooo..
    ...owWWwwwo.....
    ....oooooo......
    ................
    ................
    """,
    """
    ................
    .....oooooo.....
    ....oSeeeSSo....
    ....oSo..oSo....
    ..oooooooooooo..
    .opppppppppRRRo.
    .orrrrrrrrrRRRo.
    .orrrWWrrrrRRRo.
    .orrWWWWrrrRRRo.
    .orrWWWWrrrRRRo.
    .orrrWWrrrrRRRo.
    .orrrrrrrrrRRRo.
    .oRRRRRRRRRRRdo.
    ..oooooooooooo..
    ................
    ................
    """,
    """
    ................
    ................
    ....oooooooo....
    ...oFFFFFFeeo...
    ..oFffffffeeSo..
    ..oeeeeeeeeSSo..
    ..oooooooooooo..
    ..oWWWWWWwwsSo..
    ..oWWgWWWgwsSo..
    ..oWgGgWgGgsSo..
    ..oWWgWWWgwsSo..
    ..oWWWWWWwwsSo..
    ..owwwwwwwssSo..
    ...oooooooooo...
    ................
    ................
    """,
    """
    ................
    ......oooo......
    .....ob..bo.....
    .....ob..bo.....
    ......oooo......
    .....ohhhbo.....
    ....oHaaaAbo....
    ....oooooooo....
    ....obyWWybo....
    ....obyWyaBo....
    ....obyayaBo....
    ....obyaAaBo....
    ....oooooooo....
    ....oHaaaAbo....
    .....oooooo.....
    ................
    """,
    """
    ................
    .....oooooo.....
    ....ohhhhBBo....
    ....oBooooBo....
    ....oB....Bo....
    ..oooooooooooo..
    .ohhhhhhhhhhBBo.
    .ohbbbyybbbBBBo.
    .obbbbyAbbbBBBo.
    .oooooooooooooo.
    .ohbbbrbbbbBBBo.
    .obbbrrrbbbBBBo.
    .obbbbrbbbbBBBo.
    ..oBBBBBBBBBBo..
    ...oooooooooo...
    ................
    """,
    """
    ................
    ......oo........
    .....owo.oo.....
    ......ooowo.....
    .........oo.....
    ....oooooooo....
    ..ooHyygyyaaoo..
    .oWyyaagyAaaAWo.
    .oWWooooooooWwo.
    ..oWWWWWWWWWwo..
    ..oWWWWWWWWwso..
    ...owWWWWwwso...
    ....owwwwsso....
    .....oooooo.....
    ................
    ................
    """,
]]

AREND = [pixels(source) for source in [
    """
    ................
    ................
    ....oooooooo....
    ...ohhhhhhhho...
    ..ohHhhhhhhAbo..
    .oHhhhhhhhhhABo.
    .oooooooooooooo.
    .obbbbByyBbbbBo.
    ..obbbByABbbBo..
    ..oBBBBooBBBBo..
    ..ohbbbbbbBBBo..
    ..obbbbbbbBBBo..
    ..oBBBBBBBBBBo..
    ...oooooooooo...
    ................
    ................
    """,
    """
    ................
    .....oooooo.....
    ....oFffffeo....
    ....oeeeeeeo....
    ...oooooooooo...
    ...olggggGGGo...
    ...ogWWWWwsGo...
    ...ogWRRRwsGo...
    ...ogWWWRwsGo...
    ...ogWWRwwsGo...
    ...ogWWRwwsGo...
    ...ogWWwwwsGo...
    ...oGGGGGGGGo...
    ....oooooooo....
    ................
    ................
    """,
    """
    ................
    ................
    .....oooooo.....
    ...ooWbbbbWoo...
    ..oWWWWWWWWwo...
    ..oooooooooooo..
    ..oWWWWWWwwoWwo.
    ..oWWjWWWwwo.wo.
    ..oWjijWWwwo.wo.
    ..oWWjWjWwwoWwo.
    ...oWWjwwwoooo..
    ....owwwwo......
    ..oooooooooo....
    ...owWWwwwo.....
    ....oooooo......
    ................
    """,
]]


def book(green=False):
    source = """
    ................
    ................
    ....ooooooooo...
    ...oHhhhhhhABo..
    ..oHWWWWWWWoBo..
    ..ooooooooooBo..
    ..ojiiiiijjJBo..
    ..ojiiiiijjJBo..
    ..ojiWWiijjJBo..
    ..ojWWWWijjJBo..
    ..ojiWWiijjJBo..
    ..ojiiiiijjJBo..
    ..ojjjjjjjJJo...
    ...ooooooooo....
    ................
    ................
    """
    if green:
        source = source.translate(str.maketrans({"j": "G", "i": "g", "J": "D"}))
    return pixels(source)


def outline(image):
    """A constant, opaque 1px contour around the native silhouette; no blur."""
    source = image.copy()
    width, height = source.size
    for y in range(height):
        for x in range(width):
            if source.getpixel((x, y))[3]:
                continue
            if any(0 <= nx < width and 0 <= ny < height and source.getpixel((nx, ny))[3]
                   for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))):
                image.putpixel((x, y), INK)
    return image


def herb(kind):
    image = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(image)
    def poly(points, color): d.polygon(points, fill=COLORS[color])
    d.line([(6, 12), (10, 3)], fill=COLORS["G"])
    poly([(7, 10), (3, 9), (3, 6), (6, 7)], "g")
    d.point((3, 6), fill=COLORS["l"])
    poly([(8, 9), (10, 7), (12, 7), (11, 10), (8, 11)], "g")
    if kind == 0:
        for x, y in ((8, 3), (5, 6), (9, 8)):
            d.ellipse((x-1, y-1, x+2, y+2), fill=COLORS["j"])
            d.rectangle((x, y-1, x+1, y), fill=COLORS["I"])
            d.point((x, y-1), fill=COLORS["F"])
    elif kind == 1:
        for x, y in ((9, 3), (5, 5)):
            poly([(x, y-1), (x+2, y), (x+2, y+2), (x+3, y+3), (x-2, y+3), (x-1, y+1)], "V")
            d.line((x, y, x, y+2), fill=COLORS["v"])
            d.point((x+1, y+3), fill=COLORS["W"])
    elif kind == 2:
        for x, y in ((8, 3), (4, 7), (10, 8)):
            poly([(x-1, y-1), (x, y), (x+1, y-1), (x+2, y), (x+2, y+1), (x, y+3), (x-2, y+1), (x-2, y)], "a")
            d.line((x-1, y, x, y+1), fill=COLORS["y"])
            d.point((x+1, y+1), fill=COLORS["A"])
    else:
        for x, y in ((7, 5), (4, 7), (10, 8)):
            poly([(x-1, y+2), (x, y-2), (x+2, y-3), (x+2, y), (x, y+3)], "i")
            d.line((x, y+1, x+1, y-1), fill=COLORS["q"])
            d.point((x+1, y-2), fill=COLORS["F"])
    # An outline for each leaf/flower cluster keeps adjacent materials separate.
    return outline(image)


def seed_packet(kind):
    image = pixels("""
    ................
    ................
    ....oooooooo....
    ...oHhhhhhhho...
    ...oooooooooo...
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHWWWWWWwAbo..
    ..oHwwwwwwwAbo..
    ...oAAAAAAAbo...
    ....oooooooo....
    ................
    """)
    d = ImageDraw.Draw(image)
    color, light, dark = [("j", "i", "J"), ("V", "v", "n"), ("a", "y", "A"), ("q", "i", "Q")][kind]
    if kind == 0:
        d.ellipse((6, 6, 9, 9), fill=INK)
        d.rectangle((7, 7, 8, 8), fill=COLORS[color]); d.point((7, 7), fill=COLORS[light])
    elif kind == 1:
        d.polygon([(7, 6), (9, 6), (9, 8), (10, 9), (6, 9), (7, 8)], fill=INK)
        d.line((8, 7, 8, 8), fill=COLORS[light])
    elif kind == 2:
        for x, y in ((6, 6), (8, 6), (7, 8)):
            d.rectangle((x, y, x+1, y+1), fill=INK)
        d.point((7, 7), fill=COLORS[light]); d.point((8, 7), fill=COLORS[color])
    else:
        d.polygon([(6, 9), (7, 6), (10, 6), (9, 9)], fill=INK)
        d.line((7, 8, 9, 7), fill=COLORS[light])
    d.line((6, 11, 9, 11), fill=COLORS[dark])
    return image


def pack(icons, columns, rows=None):
    sheet = Image.new("RGBA", (columns*16, (rows or ((len(icons)+columns-1)//columns))*16))
    for index, icon in enumerate(icons):
        assert icon.size == (16, 16)
        sheet.paste(icon, (index % columns*16, index // columns*16))
    return sheet


def configure_buff_drawing():
    # Three explicit tones per material replace the former per-pixel multiplied
    # colors. Constant dark ink keeps every silhouette equally legible.
    mapping = {
        "SKIN": "k", "SKIN_D": "K", "BONE": "w", "WHITE": "W", "CREAM": "w",
        "RED": "r", "DRED": "R", "PINK": "p", "BLUE": "j", "LBLUE": "i", "DBLUE": "J",
        "GREEN": "g", "LGREEN": "l", "DGREEN": "G", "YELLOW": "y", "GOLD": "a", "ORANGE": "a",
        "PURPLE": "V", "DPURP": "n", "LPURP": "v", "BROWN": "b", "LBROWN": "h",
        "GREY": "e", "LGREY": "f", "DGREY": "S", "TEAL": "q", "NIGHT": "N", "INK": "o",
    }
    for name, key in mapping.items():
        setattr(buffs, name, COLORS[key][:3])
    ramps = ["Wws", "kKt", "prR", "lgG",
             "iIj", "IjJ", "vVn", "Hhb", "yaA", "Ffe", "iqQ"]
    shadow = {}
    light = {}
    for ramp in ramps:
        a, b, c = [COLORS[key] for key in ramp]
        shadow[a] = b; shadow[b] = c
        light[b] = a; light[c] = b
    def finish(image):
        source = image.copy()
        for y in range(16):
            for x in range(16):
                color = source.getpixel((x, y))
                if not color[3] or color == INK:
                    continue
                # A few solid edge clusters, never dithering or gradients.
                below = y == 15 or source.getpixel((x, y+1))[3] == 0
                right = x == 15 or source.getpixel((x+1, y))[3] == 0
                above = y == 0 or source.getpixel((x, y-1))[3] == 0
                if below or right:
                    image.putpixel((x, y), shadow.get(color, color))
                elif above and x <= 8:
                    image.putpixel((x, y), light.get(color, color))
        outline(image)
        # Native shapes can reach the edge of the cell: the final perimeter is
        # still dark, so neighboring cells never create a bright clipped edge.
        for i in range(16):
            for xy in ((i, 0), (i, 15), (0, i), (15, i)):
                if image.getpixel(xy)[3]: image.putpixel(xy, INK)
    buffs.shade_and_outline = finish
    # Treatment plus and phase dots fit the lower-right 5x5 area. The old
    # 8x8 badges hid most of the underlying condition.
    def plus(c, color=None):
        color = color or buffs.GREEN
        c.rect(12, 10, 12, 14, color); c.rect(10, 12, 14, 12, color)
    def phase(c, n, total=3):
        color = {1: buffs.RED, 2: buffs.GOLD, 3: buffs.GREEN}[min(n, 3)]
        # A vertical sequence preserves the whole central injury silhouette.
        for i in range(total):
            c.px(14, 8+i*2, color if i < n else buffs.DGREY)
    buffs.b_plus = plus
    buffs.b_level = phase


def build_sheets():
    configure_buff_drawing()
    recipes = buffs.build_recipes()
    recipes["buffStressClearMind"] = buffs.R(buffs.head, lambda c: c.rect(3, 3, 12, 5, buffs.LBLUE), buffs.B(buffs.b_star))
    recipes["buffStressFireMemory"] = buffs.R(buffs.flame, lambda c: c.rect(6, 8, 9, 9, buffs.NIGHT))
    index = json.loads((PACK / "assets/Tilesheets/harveyBuffIcons.json").read_text(encoding="utf-8-sig"))
    assert set(recipes) == set(index), "Update native recipes when adding/removing a buff"

    # Native mishap drawings use the same subject vocabulary, without reading
    # the old rendered sheet. The six cell identities are kept exactly.
    def splinter(c):
        buffs.skin_patch(c); c.line([(8, 5), (6, 9)], buffs.BROWN, 2); c.px(5, 10, buffs.RED)
    def bee(c):
        c.oval(3, 3, 7, 7, buffs.LBLUE); c.oval(8, 3, 12, 7, buffs.LBLUE)
        c.oval(3, 7, 12, 12, buffs.GOLD)
        c.rect(6, 7, 7, 12, buffs.INK); c.rect(10, 8, 11, 11, buffs.INK)
        c.px(12, 9, buffs.INK); c.px(2, 10, buffs.INK)
    def sunstroke(c):
        c.oval(4, 3, 11, 10, buffs.GOLD); c.oval(5, 4, 9, 8, buffs.YELLOW)
        for xy in ((2, 2), (12, 2), (1, 7), (13, 7), (7, 1), (3, 12)):
            c.px(*xy, buffs.ORANGE)
        buffs.b_drop(c)
    mishaps = [buffs.R(buffs.heart, buffs.band), buffs.R(splinter), buffs.R(bee),
               buffs.R(sunstroke), buffs.R(buffs.snowflake, buffs.B(buffs.b_bang, buffs.RED)),
               buffs.R(buffs.wound_line, buffs.stitches, buffs.B(buffs.b_drop))]
    mishap_images = [recipe() for recipe in mishaps]
    for key, image in zip(["HarveyMod_Resilience", "HarveyMod_Splinter", "HarveyMod_BeeSting", "HarveyMod_Sunstroke", "HarveyMod_Frostbite"], mishap_images):
        recipes[key] = lambda image=image: image.copy()
    # Shared inventory motifs match their care effects.
    recipes["HarveyMod_CleanBandage"] = lambda: MEDICAL[0].copy()
    recipes["buffCalmTeaEffect"] = lambda: MEDICAL[3].copy()
    recipes["buffHarveyLantern"] = lambda: MEDICAL[6].copy()
    anatomy, anatomy_legacy, anatomy_bases, anatomy_badge = anatomy_replacements(COLORS)
    for key, image in anatomy.items():
        recipes[key] = lambda image=image: image.copy()
    mishap_images[1] = anatomy['HarveyMod_Splinter'].copy()
    mishap_images[5] = anatomy_badge(anatomy_bases['stitched'], 'drop')
    images = {key: recipes[key]() for key in index}
    atlas = pack([images[key] for key in sorted(index, key=index.get)], 16)

    # Handbook order follows stressIcons.json and HandbookManager.cs.
    handbook = [images["buffStressOverwork"], buffs.R(buffs.person, buffs.B(buffs.b_bang))(),
                images["buffStressThunder"], buffs.R(buffs.moon_crescent)(),
                buffs.R(lambda c: c.poly([(2, 13), (4, 6), (7, 2), (11, 4), (13, 13)], buffs.GREY),
                        lambda c: c.oval(6, 7, 10, 14, buffs.NIGHT))(),
                images["buffStressLonely"], buffs.R(buffs.rx)(),
                buffs.R(buffs.vial)(), buffs.R(buffs.ice_cube, buffs.crack)(),
                buffs.R(buffs.clipboard, buffs.B(buffs.b_bang))(), buffs.R(buffs.rx, buffs.B(buffs.b_star))(),
                images["buffStressTooCold"], images["buffStressNoSleep"], images["buffStressNumbness"],
                images["buffStressPanic"], images["buffHarveyCare"], MEDICAL[3],
                buffs.R(lambda c: c.poly([(3, 7), (6, 4), (10, 4), (13, 7), (10, 10), (6, 10)], buffs.BLUE),
                        lambda c: c.poly([(3, 7), (1, 4), (1, 10)], buffs.LBLUE),
                        lambda c: c.px(10, 6, buffs.INK))(),
                buffs.R(buffs.candle)(), anatomy_badge(anatomy_bases['hand'], 'heart'),
                images["buffStressShadowParanoia"]]
    # Preserve the infection glyph (not an anatomical illustration).
    anatomy_legacy[8] = buffs.R(buffs.germ)()
    sheets = {
        "medicalItems.png": pack(MEDICAL, 9), "arendItems.png": pack(AREND, 3),
        "herbalItems.png": pack([herb(i) for i in range(4)] + [seed_packet(i) for i in range(4)], 8),
        "injury-book.png": book(), "stress-handbook.png": book(True),
        "harveyBuffIcons.png": atlas, "mishapBuffIcons.png": pack(mishap_images, 6),
        "stressIcons.png": pack(handbook, 7), "injuryIcon.png": pack(anatomy_legacy, 4),
    }
    return sheets, index


TARGETS = {
    "medicalItems.png": ["HarveyOverhaul [CP]/assets/Items/medicalItems.png", "HarveyOverhaulCore/assets/sprites/planItems.png"],
    "arendItems.png": ["HarveyOverhaul [CP]/assets/Items/arendItems.png"],
    "herbalItems.png": ["HarveyOverhaul [CP]/assets/Items/herbalItems.png"],
    "injury-book.png": ["HarveyOverhaulInjury/assets/sprites/book.png", "HarveyOverhaulCore/assets/sprites/planBook.png"],
    "stress-handbook.png": ["HarveyStressMeter/assets/sprites/handbook.png", "HarveyStressMeter/assets/sprites/ui.png"],
    "harveyBuffIcons.png": ["HarveyOverhaul [CP]/assets/Tilesheets/harveyBuffIcons.png"],
    "mishapBuffIcons.png": ["HarveyOverhaul [CP]/assets/Items/mishapBuffIcons.png"],
    "stressIcons.png": ["HarveyOverhaul [CP]/assets/Tilesheets/stressIcon.png", "HarveyStressMeter/assets/sprites/stressIcons.png"],
    "injuryIcon.png": ["HarveyOverhaul [CP]/assets/Tilesheets/injuryIcon.png"],
}


def backup(path):
    relative = path.relative_to(ROOT)
    destination = BACKUP / relative
    if path.is_file() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)


def preview(sheets):
    # Enlargement is exclusively for viewing. Runtime assets never use resize.
    font_path = "C:/Windows/Fonts/arial.ttf"
    title = ImageFont.truetype(font_path, 24)
    font = ImageFont.truetype(font_path, 15)
    small = ImageFont.truetype(font_path, 12)
    image = Image.new("RGB", (1120, 600), "#e9dcba")
    d = ImageDraw.Draw(image)
    d.text((24, 14), "ХАРВИ · ПРЕДМЕТЫ 16×16", font=title, fill="#301e25")
    d.text((24, 49), "Нативные пиксели · тёмная обводка · без уменьшения и сглаживания", font=font, fill="#655363")
    groups = [("Медицина", "medicalItems.png", ["Бинт", "Антисептик", "Таблетки", "Травяной чай", "Аптечка", "Мазь", "Фонарь", "Сумка", "Бульон"]),
              ("Аренд и справочники", None, ["Шкатулка", "Чай №7", "Чашка Элин", "План", "Справочник"]),
              ("Травы и семена", "herbalItems.png", ["Росница", "Бархатница", "Сердцелист", "Шовник", "Семена", "Семена", "Семена", "Семена"])]
    for row, (label, name, labels) in enumerate(groups):
        y = 88 + row*162
        d.text((24, y), label, font=font, fill="#655363")
        icons = [sheets[name].crop((i*16, 0, i*16+16, 16)) for i in range(len(labels))] if name else \
                [*AREND, sheets["injury-book.png"], sheets["stress-handbook.png"]]
        for i, (icon, label) in enumerate(zip(icons, labels)):
            x = 24 + i*120
            # Warm inventory background, native 1x sample and dark background.
            d.rectangle((x, y+27, x+79, y+106), fill="#ba9976")
            image.paste(icon.resize((80, 80), Image.Resampling.NEAREST), (x, y+27), icon.resize((80, 80), Image.Resampling.NEAREST))
            image.paste(icon, (x+87, y+30), icon)
            d.rectangle((x+85, y+58, x+104, y+77), fill="#35404b")
            image.paste(icon, (x+87, y+60), icon)
            d.text((x, y+111), label, font=small, fill="#301e25")
    image.save(ART / "preview-items.png")
    all_icons = Image.new("RGB", (1120, 1600), "#e9dcba")
    draw = ImageDraw.Draw(all_icons)
    draw.text((24, 12), "ХАРВИ · ЭФФЕКТЫ И СПРАВОЧНИК", font=title, fill="#301e25")
    y = 58
    for label, name, count, columns in [("Эффекты · прежние индексы 0–165", "harveyBuffIcons.png", 166, 16),
                                        ("Справочник стресса", "stressIcons.png", 21, 7),
                                        ("Травмы", "injuryIcon.png", 12, 4),
                                        ("Мелкие неприятности", "mishapBuffIcons.png", 6, 6)]:
        draw.text((24, y), label, font=font, fill="#655363"); y += 24
        sheet = sheets[name]
        for i in range(count):
            icon = sheet.crop((i%columns*16, i//columns*16, i%columns*16+16, i//columns*16+16))
            x, cy = 24 + i%16*68, y + i//16*78
            draw.rectangle((x, cy, x+63, cy+63), fill="#ba9976")
            scaled = icon.resize((64, 64), Image.Resampling.NEAREST)
            all_icons.paste(scaled, (x, cy), scaled)
            draw.text((x, cy+64), str(i), font=small, fill="#655363")
        y += ((count+15)//16)*78+15
    all_icons.crop((0, 0, 1120, y)).save(ART / "preview-effects.png")
    anatomy_preview(sheets)


def anatomy_preview(sheets):
    before_path = ART / 'anatomy-before/harveyBuffIcons.png'
    latest_before = ART / 'anatomy-v3/before/harveyBuffIcons.png'
    if latest_before.is_file():
        before_path = latest_before
    if not before_path.is_file():
        return
    with Image.open(before_path) as source:
        before = source.convert('RGBA')
    after = sheets['harveyBuffIcons.png']
    index = json.loads((PACK / 'assets/Tilesheets/harveyBuffIcons.json').read_text(encoding='utf-8-sig'))
    examples = [
        ('Надрыв мышцы', 'buffTornMuscles'), ('Лодыжка', 'buffSprainedAnkle'),
        ('Ушиб рёбер', 'buffBruisedRibs'), ('Растяжение спины', 'buffBackStrain'),
        ('Сотрясение', 'buffConcussion'), ('Перевязка', 'HarveyMod_DeepCuts_Healing'),
        ('После операции', 'buffSurgicalWound'), ('Намокшие швы', 'HarveyMod_WetStitches'),
        ('Слабость мышцы', 'HarveyMod_MuscleAtrophy'), ('Онемение', 'buffStressNumbness'),
        ('Дыхание', 'HarveyMod_BreathingDifficulty'), ('Заноза', 'HarveyMod_Splinter'),
    ]
    path = 'C:/Windows/Fonts/arial.ttf'
    title = ImageFont.truetype(path, 25)
    font = ImageFont.truetype(path, 17)
    small = ImageFont.truetype(path, 13)
    canvas = Image.new('RGB', (1040, 690), '#e9dcba')
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 15), 'ЧАСТИ ТЕЛА · НОВАЯ ПЕРЕРИСОВКА', fill='#301e25', font=title)
    draw.text((24, 52), '16×16 · ручные пиксельные рисунки · объём, кожа и ткань · тёмный контур', fill='#655363', font=font)
    for pos, (label, key) in enumerate(examples):
        x, y = 24+pos%4*256, 101+pos//4*194
        draw.text((x, y), label, fill='#301e25', font=font)
        i = index[key]
        box = (i%16*16, i//16*16, i%16*16+16, i//16*16+16)
        for offset, atlas, caption in ((0, before, 'Было'), (126, after, 'Стало')):
            icon = atlas.crop(box)
            draw.rectangle((x+offset, y+29, x+offset+79, y+108), fill='#ba9976')
            scaled = icon.resize((80, 80), Image.Resampling.NEAREST)
            canvas.paste(scaled, (x+offset, y+29), scaled)
            draw.text((x+offset, y+114), caption, fill='#655363', font=small)
            canvas.paste(icon, (x+offset, y+142), icon)
            draw.text((x+offset+23, y+142), '16 px', fill='#655363', font=small)
        draw.text((x+92, y+58), '→', fill='#655363', font=font)
    canvas.save(ART / 'anatomy-comparison.png')


def main(install=False):
    OUT.mkdir(parents=True, exist_ok=True)
    sheets, index = build_sheets()
    for name, sheet in sheets.items():
        sheet.save(OUT / name)
        if install:
            for relative in TARGETS[name]:
                target = ROOT / relative
                backup(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                sheet.save(target)
    (OUT / "harveyBuffIcons.json").write_text(json.dumps(index, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    # Keep existing generators/installers' curated exports current. Their big
    # generated source art remains archived; default builds consume these PNGs.
    if install:
        for name in sheets:
            family = "items-stardew" if name in ("medicalItems.png", "arendItems.png", "injury-book.png", "stress-handbook.png") else \
                     "herbal-garden" if name == "herbalItems.png" else "buffs-stardew"
            target = PACK / "art" / family / "exports" / name
            backup(target)
            shutil.copyfile(OUT / name, target)
        herbs = sheets["herbalItems.png"]
        for i, name in enumerate(["glass-dewberry", "moonvelvet", "amber-heartleaf", "silver-seamleaf"]*2):
            target = PACK / "art/herbal-garden/exports" / (name + ("-seeds" if i >= 4 else "") + ".png")
            backup(target)
            herbs.crop((i*16, 0, i*16+16, 16)).save(target)
    preview(sheets)
    report = {"cellSize": [16, 16], "method": "native integer pixel drawing; no resampling",
              "outline": "#301e25, opaque 1px", "buffCount": len(index),
              "anatomy": {"source": "../../scripts/native_anatomy.py",
                          "concept": "anatomy-v3/concept.png",
                          "prompt": "anatomy-v3/concept-prompt.txt",
                          "conceptMethod": "built-in image_gen, art direction only",
                          "runtimeMethod": "integer pixel sources on 16x16 canvas; no bitmap sampling"},
              "sheets": {name: {"size": list(sheet.size), "sha256": hashlib.sha256(sheet.tobytes()).hexdigest(),
                                 "targets": TARGETS[name]} for name, sheet in sheets.items()}}
    (ART / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Native 16x16: 20 inventory, 2 books, 166 buffs, 21 stress, 12 injury, 6 mishap cells.")
    print("Installed into workspace." if install else "Exports only; use --install for workspace assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    main(parser.parse_args().install)
