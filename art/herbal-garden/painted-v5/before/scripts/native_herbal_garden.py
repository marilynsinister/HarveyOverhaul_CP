"""Apothecary garden, drawn directly on 16x32 / 16x16 pixel canvases.

Every motif character and every stem coordinate is a game pixel. There are
no input bitmaps, reductions, antialiasing, palette conversions or randomness.
Only the labelled review images are enlarged, using integer nearest neighbour.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[1]
ART = PACK / "art/herbal-garden"
REVIEW = ART / "native-v4"
NAMES = ("glass-dewberry", "moonvelvet", "amber-heartleaf", "silver-seamleaf")
LABELS = ("Стеклянная росница", "Лунная бархатница", "Янтарный сердцелист", "Серебряный шовник")
INK = (38, 62, 49, 255)
PALETTE = {
    ".": (0, 0, 0, 0), "o": INK,
    # Foliage: forest, teal, sage; glass: blue with a small opaque reflection.
    "O": "365d45", "d": "3c7052", "g": "548e58", "m": "7ca863", "h": "b2cc78",
    "t": "30685e", "j": "4e8c70", "k": "7eb68a", "l": "b7d79a", "H": "dce9a7",
    "z": "345579", "B": "4777aa", "b": "64a7d1", "c": "9adce9", "C": "d0f2ec", "W": "fff8da",
    "i": "80bfd7",
    # Velvet flowers and the soft sage undersides of leaves.
    "V": "735d91", "v": "a18bc1", "p": "c8b4de", "P": "e8d8ed", "K": "fff1e4",
    "s": "6e9981", "S": "a4c59c", "L": "d7e6b5",
    # Warm heart-shaped leaves, red stems and pearl-white seamleaf flowers.
    "r": "75544b", "R": "a07c50", "A": "b07842", "a": "dda44f",
    "y": "f3ca70", "Y": "ffe49b", "Q": "fff4cb", "e": "577f75", "f": "91b79b",
    "F": "c3d9af", "x": "8eafa7", "w": "e4e6ce", "D": "b1b9a6", "q": "e5c278",
    # Parchment seed envelopes.
    "u": "704835", "U": "ae7548", "n": "d69c60", "N": "f0c890",
    "E": "fce5b7",
}
PALETTE = {key: tuple(bytes.fromhex(value)) + (255,) if isinstance(value, str) else value
           for key, value in PALETTE.items()}


def canvas(size=(16, 32)):
    return Image.new("RGBA", size)


def motif(rows):
    rows = rows.strip().split()
    assert len({len(row) for row in rows}) == 1, rows
    result = canvas((len(rows[0]), len(rows)))
    result.putdata([PALETTE[c] for row in rows for c in row])
    return result


def stamp(image, tile, x, y, flip=False, edge=None):
    if flip:
        tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if edge is not None:
        tile = tile.copy()
        tile.putdata([PALETTE[edge] if p == INK else p for p in tile.get_flattened_data()])
    assert 0 <= x and x + tile.width <= image.width
    assert 0 <= y and y + tile.height <= image.height
    image.alpha_composite(tile, (x, y))


def twig(image, points, color="g"):
    draw = ImageDraw.Draw(image)
    # Outline and the single-pixel stem are drawn at their final coordinates.
    draw.line(points, fill=INK, width=3)
    draw.line(points, fill=PALETTE[color], width=1)


def complete_contour(image):
    """Keep one dark outside edge; overlapping leaf edges stay coloured."""
    source = image.copy()
    for y in range(image.height):
        for x in range(image.width):
            pixel = source.getpixel((x, y))
            if pixel[3] and any(
                not (0 <= xx < image.width and 0 <= yy < image.height)
                or not source.getpixel((xx, yy))[3]
                for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
            ):
                image.putpixel((x, y), INK)
    return image


# Native pixel paintings: round leaf clusters and small warm highlights.
# Material-coloured edges separate overlapping forms; only the silhouette has
# the common dark green contour. No pixels are sampled from the reference.
TEAL_LEAF = motif("""
    ...oo..
    .ooHho.
    oHhmggo
    ohmgdgo
    .ogddo.
    ..ooo..
""")
TEAL_LOW = motif("""
    .ooo...
    ohhmoo.
    ohmgdgo
    .ogddgo
    ..oooo.
""")
SAGE_LEAF = motif("""
    ...oo..
    .ooLSo.
    oLSSsso
    oSSstso
    .ostto.
    ..ooo..
""")
SAGE_LOW = motif("""
    .ooo...
    oLSsoo.
    oSSstso
    .osttso
    ..oooo.
""")
HEART = motif("""
    ..oo.oo..
    .oYyoYao.
    oQYyyyAAo
    oYyyyAaAo
    .oyyaAAo.
    ..oyAAo..
    ...oAo...
    ....o....
""")
HEART_MID = motif("""
    .oo.oo.
    oYyoYao
    oQyyaAo
    .oyyAo.
    ..oAo..
    ...o...
""")
HEART_SMALL = motif("""
    .o.o.
    oYyao
    oyaao
    .oAo.
    ..o..
""")
SILVER_LEAF = motif("""
    ....oo.
    ...oLWo
    ..oLFFo
    .oLFfeo
    oLFxfeo
    .offeo.
    ..ooo..
""")
SILVER_LOW = motif("""
    .ooo...
    oLFfoo.
    oFfxeeo
    .offeeo
    ..oooo.
""")
BERRY = motif("""
    ..ooo..
    .oCCco.
    oCWccbo
    oCccbbo
    ocbbBBo
    .oicco.
    ..ooo..
""")
BERRY_SMALL = motif("""
    .ooo.
    oWCbo
    oCbBo
    .occo
    ..oo.
""")
BUD_BLUE = motif("""
    .oo.
    oCbo
    obBo
    .oo.
""")
BELL = motif("""
    ..ooo..
    .oPPvo.
    oPKpvVo
    oPpvvVo
    opvvVVo
    ooPqPoo
    .ooVoo.
""")
BELL_SMALL = motif("""
    .ooo.
    oPpVo
    oPvvo
    opvVo
    ooPoo
    ..o..
""")
BUD_PURPLE = motif("""
    .oo.
    oPvo
    ovVo
    .oo.
""")
BUD_PEARL = motif("""
    .oo.
    oWFo
    oFeo
    .oo.
""")
FLOWER = motif("""
    ..oo...
    .oWWoo.
    ooWwWWo
    oWWqwwo
    .oWwwDo
    .oWWoo.
    ..oo...
""")
FLOWER_SMALL = motif("""
    .ooo.
    oWwwo
    oWqwo
    owDwo
    .ooo.
""")
SEED = motif("""
    .ooo.
    oNnUo
    .ooo.
""")


def leaf(im, tile, x, y, flip=False, edge="O"):
    stamp(im, tile, x, y, flip, edge=edge)


def seed():
    result = canvas()
    stamp(result, SEED, 5, 28)
    return result


def shoot(kind):
    result = canvas()
    stem = "r" if kind == 2 else "g"
    twig(result, [(7, 29), (7, 26)], stem)
    colors = (("k", "j"), ("S", "s"), ("y", "a"), ("F", "f"))[kind]
    left = motif(f"""
        .oo.
        o{colors[0]}{colors[1]}o
        .o{colors[1]}o
        ..o.
    """)
    stamp(result, left, 3, 24)
    stamp(result, left, 8, 23, True)
    # Ground anchor is consistent with every later phase (vanilla bottom=30).
    result.putpixel((7, 30), INK)
    return result


def dewberry(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 25), (8, 23)], "g")
        leaf(im, TEAL_LOW, 2, 25)
        leaf(im, TEAL_LEAF, 7, 22)
        return im
    twig(im, [(7, 29), (6, 24), (8, 18)], "g")
    twig(im, [(7, 25), (4, 22)], "j")
    leaf(im, TEAL_LEAF, 5, 13)
    leaf(im, TEAL_LEAF, 1, 17, True)
    leaf(im, TEAL_LEAF, 8, 18)
    leaf(im, TEAL_LOW, 2, 25)
    leaf(im, TEAL_LOW, 7, 25, True)
    leaf(im, TEAL_LEAF, 4, 21)
    if stage == 3:
        stamp(im, BUD_BLUE, 9, 19, edge="z")
        stamp(im, BUD_BLUE, 3, 24, edge="z")
    elif stage == 4:
        stamp(im, BERRY, 8, 17, edge="z")
        stamp(im, BERRY, 1, 22, edge="z")
        stamp(im, BERRY_SMALL, 9, 25, edge="z")
    return im


def moonvelvet(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 25), (8, 23)], "s")
        leaf(im, SAGE_LOW, 2, 25)
        leaf(im, SAGE_LEAF, 7, 22)
        return im
    twig(im, [(7, 29), (7, 24), (6, 18), (8, 14), (10, 15)], "s")
    twig(im, [(7, 25), (3, 22)], "s")
    leaf(im, SAGE_LEAF, 5, 13)
    leaf(im, SAGE_LEAF, 1, 18, True)
    leaf(im, SAGE_LEAF, 7, 21)
    leaf(im, SAGE_LOW, 2, 25)
    leaf(im, SAGE_LOW, 7, 25, True)
    if stage == 3:
        stamp(im, BUD_PURPLE, 9, 17, edge="V")
        stamp(im, BUD_PURPLE, 2, 23, edge="V")
        stamp(im, BUD_PURPLE, 10, 25, edge="V")
    elif stage == 4:
        stamp(im, BELL, 7, 16, edge="V")
        stamp(im, BELL, 1, 22, edge="V")
        stamp(im, BELL_SMALL, 10, 24, edge="V")
    return im


def heartleaf(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 25)], "R")
        leaf(im, TEAL_LOW, 2, 25)
        stamp(im, HEART_SMALL, 8, 23, edge="A")
        return im
    twig(im, [(7, 29), (7, 23), (8, 18)], "R")
    twig(im, [(7, 25), (3, 22)], "R")
    leaf(im, TEAL_LEAF, 5, 13)
    leaf(im, TEAL_LEAF, 1, 20, True)
    leaf(im, TEAL_LEAF, 8, 20)
    leaf(im, TEAL_LOW, 2, 25)
    leaf(im, TEAL_LOW, 7, 25, True)
    if stage == 3:
        stamp(im, HEART_SMALL, 7, 18, edge="A")
        stamp(im, HEART_SMALL, 2, 23, edge="A")
    elif stage == 4:
        stamp(im, HEART, 4, 14, edge="A")
        stamp(im, HEART_MID, 1, 22, edge="A")
        stamp(im, HEART_MID, 8, 23, edge="A")
    else:
        stamp(im, HEART_SMALL, 8, 23, edge="A")
    return im


def seamleaf(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 26)], "e")
        leaf(im, SILVER_LOW, 2, 25, edge="e")
        leaf(im, SILVER_LEAF, 7, 23, edge="e")
        return im
    twig(im, [(7, 29), (7, 23), (9, 18)], "e")
    leaf(im, SAGE_LEAF, 5, 16)
    leaf(im, SILVER_LEAF, 1, 20, True, edge="e")
    leaf(im, SILVER_LEAF, 8, 20, edge="e")
    leaf(im, SILVER_LOW, 1, 25, edge="e")
    leaf(im, SILVER_LOW, 8, 25, True, edge="e")
    leaf(im, SILVER_LEAF, 4, 23, edge="e")
    if stage == 3:
        stamp(im, BUD_PEARL, 8, 18, edge="e")
    elif stage == 4:
        stamp(im, FLOWER, 6, 14, edge="e")
        stamp(im, FLOWER_SMALL, 2, 21, edge="e")
    return im


def crop_stages(kind):
    painter = (dewberry, moonvelvet, heartleaf, seamleaf)[kind]
    stages = [seed(), shoot(kind)] + [painter(stage) for stage in (2, 3, 4, 5)]
    for im in stages:
        # Stems finish at y29, with a dark base at y30. No art can leak into
        # adjacent crop cells, even while the game alternates source frames.
        for x in (6, 7, 8):
            if im.getpixel((x, 29))[3]:
                im.putpixel((x, 30), INK)
    return [complete_contour(im) for im in stages]


def herb(kind):
    """Independent native 16x16 harvest clusters, never miniature crop copies."""
    im = canvas((16, 16))
    twig(im, [(7, 13), (6, 9), (8, 5)], "g" if kind < 2 else "R" if kind == 2 else "e")
    if kind == 0:
        leaf(im, TEAL_LEAF, 5, 1)
        leaf(im, TEAL_LEAF, 1, 4, True)
        leaf(im, TEAL_LOW, 8, 9, True)
        stamp(im, BERRY, 8, 4, edge="z")
        stamp(im, BERRY, 1, 7, edge="z")
        stamp(im, BERRY_SMALL, 9, 10, edge="z")
    elif kind == 1:
        leaf(im, SAGE_LEAF, 5, 1)
        leaf(im, SAGE_LEAF, 1, 4, True)
        leaf(im, SAGE_LOW, 8, 9, True)
        stamp(im, BELL, 7, 3, edge="V")
        stamp(im, BELL, 1, 7, edge="V")
    elif kind == 2:
        leaf(im, TEAL_LOW, 2, 9)
        leaf(im, TEAL_LOW, 8, 9, True)
        stamp(im, HEART, 5, 1, edge="A")
        stamp(im, HEART_MID, 1, 7, edge="A")
        stamp(im, HEART_MID, 8, 9, edge="A")
    else:
        leaf(im, SILVER_LEAF, 1, 7, True, edge="e")
        leaf(im, SILVER_LEAF, 8, 7, edge="e")
        leaf(im, SILVER_LOW, 4, 9, edge="e")
        stamp(im, FLOWER, 6, 1, edge="e")
        stamp(im, FLOWER_SMALL, 1, 6, edge="e")
    return complete_contour(im)


def seed_packet(kind):
    im = motif("""
        ................
        ....oooooooo....
        ...oNNNNnnnUo...
        ...oEnnnnnnUo...
        ..oooooooooooo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNEEEEEENnUo..
        ..oNnnnnnnnUUo..
        ...oUUUUUUUuo...
        ....oooooooo....
        ................
    """)
    emblem = (
        motif(""".ooo. oCcbo ocbBo .ooo."""),
        motif("""..o.. .opVo .ovVo oPpVo .ooo."""),
        HEART_SMALL,
        motif("""...o. ..oWo .oFfo oFfeo .ooo."""),
    )[kind]
    stamp(im, emblem, 5, 6)
    draw = ImageDraw.Draw(im)
    dark, light = (("B", "c"), ("V", "p"), ("A", "y"), ("e", "F"))[kind]
    draw.line((4, 11, 10, 11), fill=PALETTE[dark])
    draw.line((4, 10, 5, 10), fill=PALETTE[light])
    return im


def build_items():
    sheet = canvas((128, 16))
    for i, im in enumerate([herb(k) for k in range(4)] + [seed_packet(k) for k in range(4)]):
        sheet.paste(im, (i * 16, 0))
    return sheet


def build_crops():
    field = canvas((256, 64))
    plants = [crop_stages(kind) for kind in range(4)]
    # Stardew Crop.getSourceRect: two crops per row. Both seed variants,
    # phase+1 offsets, hard-coded ripe/regrow slots remain in their old places.
    for kind, stages in enumerate(plants):
        for frame, stage in enumerate((0, 0, 1, 2, 3, 4, 4, 5)):
            field.paste(stages[stage], ((kind % 2) * 128 + frame * 16, (kind // 2) * 32))
    return field, plants


def validate_art(items, field):
    for sheet in (items, field):
        assert sheet.mode == "RGBA"
        assert set(sheet.getchannel("A").get_flattened_data()) == {0, 255}
        assert len({p[:3] for p in sheet.get_flattened_data() if p[3]}) <= 64
    for kind in range(4):
        for frame in range(8):
            x, y = (kind % 2)*128 + frame*16, (kind // 2)*32
            sprite = field.crop((x, y, x+16, y+32))
            box = sprite.getbbox()
            assert box and box[0] >= 1 and box[2] <= 15 and box[3] == 31, (kind, frame, box)
    for index in range(8):
        sprite = items.crop((index*16, 0, index*16+16, 16))
        box = sprite.getbbox()
        assert box and min(box[:2]) >= 1 and max(box[2:]) <= 15, (index, box)


def font(size):
    return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)


def paste_scaled(target, sprite, xy, scale):
    # Used exclusively by review images; exports never pass through this code.
    enlarged = sprite.resize((sprite.width * scale, sprite.height * scale), Image.Resampling.NEAREST)
    target.paste(enlarged, xy, enlarged)


def preview(items, plants):
    board = Image.new("RGB", (1160, 822), "#f2e5ca")
    d = ImageDraw.Draw(board)
    d.text((28, 20), "АПТЕКАРСКИЙ САД", font=font(29), fill="#403a39")
    d.text((28, 61), "Нативный пиксель-арт · урожай и семена 16×16 · растения 16×32 · тёмный контур", font=font(17), fill="#6d655c")
    for x, label in zip((346, 478, 610, 742, 874, 1006), ("Посев", "Росток", "Молодое", "Бутоны", "Зрелое", "После сбора")):
        d.text((x, 102), label, font=font(15), fill="#6d655c")
    for kind in range(4):
        y = 134 + kind * 164
        d.rounded_rectangle((18, y-5, 1140, y+150), radius=9, fill="#e4d5b5")
        d.text((32, y+6), LABELS[kind], font=font(18), fill="#403a39")
        for pos, index, caption in ((40, kind, "Урожай"), (144, kind+4, "Семена")):
            sprite = items.crop((index*16, 0, index*16+16, 16))
            paste_scaled(board, sprite, (pos, y+42), 4)
            d.text((pos, y+115), caption, font=font(14), fill="#6d655c")
            board.paste(sprite, (pos+72, y+90), sprite)
        for stage, sprite in enumerate(plants[kind]):
            x = 344 + stage * 132
            # Warm, grassy swatches make the dark silhouette readable.
            d.rectangle((x-8, y+32, x+77, y+137), fill="#8d9d69")
            d.rectangle((x-8, y+112, x+77, y+137), fill="#a47e55")
            paste_scaled(board, sprite, (x+2, y+4), 4)
    d.text((28, 800), "Показаны готовые игровые спрайты ×4. Маленькие иконки рядом — настоящие 16×16. Уменьшения исходников нет.", font=font(14), fill="#6d655c")
    board.save(REVIEW / "preview.png")
    board.save(ART / "preview.png")

    # A compact planted bed, with no visible planting grid: four pairs of mature
    # sprites at the game's normal 4x rendering scale, on light and dark grounds.
    garden = Image.new("RGB", (752, 358), "#eaddc2")
    gd = ImageDraw.Draw(garden)
    gd.text((24, 18), "ЗРЕЛЫЕ РАСТЕНИЯ · ИГРОВОЙ МАСШТАБ ×4", font=font(22), fill="#403a39")
    for row, soil in enumerate(("#99734f", "#5a463e")):
        yy = 76 + row * 136
        gd.rectangle((20, yy+30, 731, yy+120), fill=soil)
        for kind in range(4):
            for repeat in range(2):
                paste_scaled(garden, plants[kind][4], (36+kind*176+repeat*64, yy-10), 4)
    garden.save(REVIEW / "garden-preview.png")

    detail = Image.new("RGB", (848, 414), "#eee1c4")
    dd = ImageDraw.Draw(detail)
    dd.text((24, 18), "АПТЕКАРСКИЙ САД · ПЫШНЫЕ КУСТИКИ", font=font(26), fill="#403a39")
    dd.text((24, 56), "Растения вблизи ×8 · игровые кадры 16×32 · урожай 16×16", font=font(16), fill="#716658")
    for kind in range(4):
        x = 20 + kind * 207
        dd.rounded_rectangle((x, 91, x+186, 392), radius=8, fill="#d9ccad")
        first, second = LABELS[kind].split(" ", 1)
        dd.text((x+14, 102), first, font=font(18), fill="#403a39")
        dd.text((x+14, 125), second, font=font(18), fill="#403a39")
        dd.rectangle((x+12, 158, x+174, 345), fill="#8b9a73")
        dd.rectangle((x+12, 297, x+174, 345), fill="#99734f")
        paste_scaled(detail, plants[kind][4], (x+2, 90), 8)
        item = items.crop((kind*16, 0, kind*16+16, 16))
        paste_scaled(detail, item, (x+120, 274), 4)
        dd.text((x+15, 359), "16×32", font=font(14), fill="#716658")
        dd.text((x+112, 359), "16×16", font=font(14), fill="#716658")
    detail.save(REVIEW / "detail-preview.png")


def remember_before(target):
    if not target.is_file():
        return
    backup = REVIEW / "before" / target.relative_to(PACK)
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, backup)


def export(install=False):
    REVIEW.mkdir(parents=True, exist_ok=True)
    out = ART / "exports"
    out.mkdir(exist_ok=True)
    items = build_items()
    field, plants = build_crops()
    validate_art(items, field)
    for name, image in (("herbalItems.png", items), ("herbalCrops.png", field)):
        remember_before(out / name)
        image.save(out / name)
    for kind, name in enumerate(NAMES):
        for index in (kind, kind+4):
            path = out / (name + ("-seeds" if index >= 4 else "") + ".png")
            remember_before(path)
            items.crop((index*16, 0, index*16+16, 16)).save(path)
        for stage, sprite in enumerate(plants[kind]):
            path = out / f"{name}-stage-{stage}.png"
            remember_before(path)
            sprite.save(path)
    if install:
        for relative, image in (("assets/Items/herbalItems.png", items),
                                ("assets/Crops/herbalCrops.png", field),
                                ("art/native-16/exports/herbalItems.png", items)):
            target = PACK / relative
            remember_before(target)
            image.save(target)
        report_path = PACK / "art/native-16/report.json"
        if report_path.is_file():
            remember_before(report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["sheets"]["herbalItems.png"]["sha256"] = hashlib.sha256(items.tobytes()).hexdigest()
            report["herbalGarden"] = {"source": "../../scripts/native_herbal_garden.py",
                                     "method": "native pixel paintings; no resampling",
                                     "outline": "#263e31",
                                     "styleReference": "../herbal-garden/native-v4/style-reference.png"}
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    remember_before(ART / "preview.png")
    preview(items, plants)
    report = {"source": "../../../scripts/native_herbal_garden.py", "method": "native integer pixel painting; no input bitmaps or downscaling",
              "artDirection": "compact lush plants; rounded forms; warm upper-left glints; material-coloured internal contours; supplied Wildflour style reference",
              "outline": "#263e31", "cropCell": [16, 32], "itemCell": [16, 16],
              "frameMap": [0, 0, 1, 2, 3, 4, 4, 5], "installedInWorkspace": install,
              "sheets": {name: {"size": list(im.size), "colors": len({p for p in im.get_flattened_data() if p[3]}),
                                "sha256Pixels": hashlib.sha256(im.tobytes()).hexdigest()}
                         for name, im in (("herbalItems.png", items), ("herbalCrops.png", field))}}
    (REVIEW / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Native herbal garden: 8 icons 16x16, 24 growth paintings 16x32, 256x64 game atlas; no downscaling.")
    print("Workspace assets installed." if install else "Exports only; --install updates workspace assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    export(parser.parse_args().install)
