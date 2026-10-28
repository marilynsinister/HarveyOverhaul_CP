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
REVIEW = ART / "native-v3"
NAMES = ("glass-dewberry", "moonvelvet", "amber-heartleaf", "silver-seamleaf")
LABELS = ("Стеклянная росница", "Лунная бархатница", "Янтарный сердцелист", "Серебряный шовник")
INK = (48, 30, 37, 255)
PALETTE = {
    ".": (0, 0, 0, 0), "o": INK,
    # Foliage: forest, teal, sage; glass: blue with a small opaque reflection.
    "d": "2c4949", "g": "537d5c", "m": "8cab6b", "h": "c8dc98",
    "t": "28576c", "j": "397f7c", "k": "73b7a0", "l": "b4dfb7", "H": "e4f2c5",
    "z": "28395e", "B": "395a90", "b": "428dbf", "c": "68c8e1", "C": "b9edf0", "W": "fff8e2",
    "i": "638cca",
    # Velvet flowers and the soft sage undersides of leaves.
    "V": "584471", "v": "9776ba", "p": "c7a1e3", "P": "efd5ee", "K": "fff0ec",
    "s": "6d968d", "S": "abc9af", "L": "e0e9cb",
    # Warm heart-shaped leaves, red stems and pearl-white seamleaf flowers.
    "r": "78404c", "R": "ad624b", "A": "a9563e", "a": "db903e",
    "y": "f6bf64", "Y": "ffe49b", "Q": "fff4cb", "e": "487276", "f": "83afa3",
    "F": "b8d9bc", "x": "93b6c7", "w": "e1dbd5", "D": "aa9eb8", "q": "deb264",
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


def stamp(image, tile, x, y, flip=False):
    if flip:
        tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    assert 0 <= x and x + tile.width <= image.width
    assert 0 <= y and y + tile.height <= image.height
    image.alpha_composite(tile, (x, y))


def twig(image, points, color="g"):
    draw = ImageDraw.Draw(image)
    # Outline and the single-pixel stem are drawn at their final coordinates.
    draw.line(points, fill=INK, width=3)
    draw.line(points, fill=PALETTE[color], width=1)


def complete_contour(image):
    """Close exposed stem ends with ink without thickening painted outlines."""
    source = image.copy()
    for y in range(image.height):
        for x in range(image.width):
            pixel = source.getpixel((x, y))
            if not pixel[3] or pixel == INK:
                continue
            for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                assert 0 <= xx < image.width and 0 <= yy < image.height
                if not source.getpixel((xx, yy))[3]:
                    image.putpixel((xx, yy), INK)
    return image


# Small leaf paintings. The dark internal edge separates overlapping leaves;
# light runs along the upper left, with a short, deliberate vein in each leaf.
TEAL_LEAF = motif("""
    ....oo.
    ..ooHko
    .oHlkko
    oHlkjto
    .ojjto.
    ..ooo..
""")
TEAL_LOW = motif("""
    .ooo...
    oHlloo.
    olkkjto
    .ojjto.
    ..ooo..
""")
SAGE_LEAF = motif("""
    ....oo.
    ..ooLSo
    .oLSSso
    oLSssdo
    .ossdo.
    ..ooo..
""")
SAGE_LOW = motif("""
    .ooo...
    oLLSoo.
    oLSssdo
    .ossdo.
    ..ooo..
""")
HEART = motif("""
    ..oo.oo..
    .oQyoYao.
    oQYyyyAAo
    oYyyyAaAo
    .oyyaAAo.
    ..oyAAo..
    ...oAo...
    ....o....
""")
HEART_MID = motif("""
    .oo.oo.
    oQYoYao
    oYyyaAo
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
    .....o.
    ....oWo
    ...oLWo
    ..oWLfo
    .oWLxfo
    oWLFefo
    oFxfeo.
    .oeeo..
    ..oo...
""")
SILVER_LOW = motif("""
    .o.....
    oWFo...
    oWLFfo.
    .oFFefo
    ..oexo.
    ...ooo.
""")
BERRY = motif("""
    ..ooo..
    .oCCco.
    oCWcbBo
    oCcbBzo
    ocbbBbo
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
    ...oo...
    ..oPpo..
    .oKPvVo.
    .oPpvVo.
    .opvvVVo
    oPppvvVo
    oKPvVvPo
    .oPoqoo.
    ..o.oo..
""")
BELL_SMALL = motif("""
    ..ooo..
    .oKPVo.
    .opvVo.
    .opvvVo
    oPpvvVo
    oooVooo
    ..oPo..
""")
BUD_PURPLE = motif("""
    .oo.
    oPvo
    ovVo
    .oo.
""")
FLOWER = motif("""
    ...oo....
    ..oWWo...
    .ooWwooo.
    oWWwqwWwo
    oWwwqqwDo
    .ooWwDoo.
    ..oWWo...
    ...oo....
""")
SEED = motif("""
    .ooo.
    oNnUo
    .ooo.
""")


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
        twig(im, [(7, 29), (7, 23), (8, 20)], "j")
        stamp(im, TEAL_LOW, 2, 25)
        stamp(im, TEAL_LEAF, 7, 21)
        stamp(im, TEAL_LEAF, 2, 18, True)
    else:
        twig(im, [(7, 29), (7, 21), (8, 15), (7, 10)], "j")
        twig(im, [(7, 23), (3, 19), (4, 15)], "j")
        twig(im, [(8, 19), (11, 16), (11, 13)], "j")
        stamp(im, TEAL_LEAF, 6, 8)
        stamp(im, TEAL_LOW, 1, 15)
        stamp(im, TEAL_LEAF, 7, 17)
        stamp(im, TEAL_LOW, 1, 25)
        stamp(im, TEAL_LEAF, 7, 24)
        stamp(im, TEAL_LOW, 2, 21)
        stamp(im, TEAL_LEAF, 2, 11, True)
        if stage == 3:
            stamp(im, BUD_BLUE, 3, 17)
            stamp(im, BUD_BLUE, 9, 14)
            stamp(im, BUD_BLUE, 7, 23)
        elif stage == 4:
            # Large glass fruit, lit from the same corner; foliage stays visible.
            stamp(im, BERRY, 7, 11)
            stamp(im, BERRY, 1, 17)
            stamp(im, BERRY, 8, 22)
    return im


def moonvelvet(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 23), (6, 20)], "s")
        stamp(im, SAGE_LOW, 2, 25)
        stamp(im, SAGE_LEAF, 7, 22)
        stamp(im, SAGE_LEAF, 1, 19, True)
    else:
        # Two arching stems give the hanging bells space and a clear silhouette.
        twig(im, [(7, 29), (7, 21), (6, 16), (7, 10), (9, 8), (11, 9)], "s")
        twig(im, [(7, 23), (4, 19), (4, 13), (3, 12)], "s")
        twig(im, [(7, 24), (10, 19), (11, 18)], "s")
        stamp(im, SAGE_LEAF, 1, 20, True)
        stamp(im, SAGE_LOW, 2, 26)
        stamp(im, SAGE_LEAF, 7, 24)
        stamp(im, SAGE_LEAF, 4, 14)
        if stage == 3:
            stamp(im, BUD_PURPLE, 9, 9)
            stamp(im, BUD_PURPLE, 2, 13)
            stamp(im, BUD_PURPLE, 10, 19)
        elif stage == 4:
            stamp(im, BELL, 7, 8)
            stamp(im, BELL, 1, 15)
            stamp(im, BELL_SMALL, 7, 22)
    return im


def heartleaf(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 23), (8, 21)], "R")
        stamp(im, HEART_SMALL, 3, 23)
        stamp(im, HEART_SMALL, 8, 20)
    else:
        twig(im, [(7, 29), (6, 23), (7, 17), (8, 12)], "R")
        twig(im, [(7, 23), (3, 19), (3, 16)], "R")
        twig(im, [(8, 22), (11, 20), (11, 17)], "R")
        if stage == 3:
            stamp(im, HEART_SMALL, 5, 12)
            stamp(im, HEART_SMALL, 1, 18)
            stamp(im, HEART_SMALL, 9, 19)
            stamp(im, HEART_SMALL, 4, 25)
        elif stage == 4:
            stamp(im, HEART, 4, 8)
            stamp(im, HEART, 1, 16)
            stamp(im, HEART, 6, 22)
            stamp(im, HEART_SMALL, 9, 17)
        else:
            # The harvested leaves disappear; a few small hearts keep the
            # regrowing plant alive and identifiable, rather than looking dead.
            stamp(im, HEART_SMALL, 5, 13)
            stamp(im, HEART_SMALL, 1, 21)
            stamp(im, HEART_SMALL, 8, 24)
    return im


def seamleaf(stage):
    im = canvas()
    if stage == 2:
        twig(im, [(7, 29), (7, 24)], "e")
        stamp(im, SILVER_LOW, 2, 24)
        stamp(im, SILVER_LEAF, 7, 20)
    else:
        twig(im, [(7, 29), (7, 20), (8, 14), (8, 10)], "e")
        stamp(im, SILVER_LEAF, 2, 17, True)
        stamp(im, SILVER_LEAF, 6, 16)
        stamp(im, SILVER_LOW, 1, 23)
        stamp(im, SILVER_LOW, 8, 24, True)
        stamp(im, SILVER_LEAF, 4, 22)
        if stage == 3:
            stamp(im, motif("""
                .oo.
                owFo
                ofeo
                .oo.
            """), 6, 11)
        elif stage == 4:
            stamp(im, FLOWER, 4, 9)
            # A second pearl bud, kept smaller than the single open flower.
            stamp(im, motif("""
                .o.
                oWo
                .o.
            """), 3, 18)
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
    """Harvest paintings authored separately in 16x16, never resized crops."""
    im = canvas((16, 16))
    if kind == 0:
        twig(im, [(7, 13), (7, 8), (9, 4)], "j")
        stamp(im, TEAL_LOW, 1, 8)
        stamp(im, TEAL_LEAF, 8, 9)
        stamp(im, BERRY, 7, 2)
        stamp(im, BERRY, 2, 6)
        stamp(im, BERRY_SMALL, 9, 9)
    elif kind == 1:
        twig(im, [(7, 13), (7, 8), (8, 4), (10, 3)], "s")
        stamp(im, SAGE_LOW, 1, 9)
        stamp(im, SAGE_LEAF, 8, 9)
        stamp(im, BELL, 6, 1)
        stamp(im, BELL_SMALL, 1, 6)
    elif kind == 2:
        twig(im, [(7, 13), (7, 7), (9, 4)], "R")
        stamp(im, HEART, 5, 1)
        stamp(im, HEART_MID, 1, 7)
        stamp(im, HEART_SMALL, 9, 10)
    else:
        twig(im, [(7, 13), (7, 8), (8, 5)], "e")
        stamp(im, SILVER_LEAF, 1, 5, True)
        stamp(im, SILVER_LEAF, 8, 6)
        stamp(im, FLOWER, 4, 1)
    # All existing inventory validators require a complete ink perimeter. The
    # tiles already carry it; thin isolated stems get the same 1px ink here.
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
    dd.text((24, 18), "АПТЕКАРСКИЙ САД · СВЕТ И ЦВЕТ", font=font(26), fill="#403a39")
    dd.text((24, 56), "Пиксели вблизи ×6 · игровые растения 16×32 · урожай 16×16", font=font(16), fill="#716658")
    for kind in range(4):
        x = 20 + kind * 207
        dd.rounded_rectangle((x, 91, x+186, 392), radius=8, fill="#d9ccad")
        first, second = LABELS[kind].split(" ", 1)
        dd.text((x+14, 102), first, font=font(18), fill="#403a39")
        dd.text((x+14, 125), second, font=font(18), fill="#403a39")
        dd.rectangle((x+12, 158, x+174, 345), fill="#8b9a73")
        dd.rectangle((x+12, 297, x+174, 345), fill="#99734f")
        paste_scaled(detail, plants[kind][4], (x+16, 154), 6)
        item = items.crop((kind*16, 0, kind*16+16, 16))
        paste_scaled(detail, item, (x+111, 274), 4)
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
            report["herbalGarden"] = {"source": "../../scripts/native_herbal_garden.py", "method": "native pixel paintings; no resampling"}
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    remember_before(ART / "preview.png")
    preview(items, plants)
    report = {"source": "../../../scripts/native_herbal_garden.py", "method": "native integer pixel painting; no input bitmaps or downscaling",
              "artDirection": "upper-left specular highlights; cool reflected light in glass; pearl flower folds; gold and silver leaf glints",
              "outline": "#301e25", "cropCell": [16, 32], "itemCell": [16, 16],
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
