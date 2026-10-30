"""Build game-sized 16x16 inventory and effect sheets.

python scripts/draw_native_icons.py --install
Medical/effect icons are authored at 16 pixels. Garden icons are reductions
of the large paintings in art/herbal-garden/painted-v6/sources.
Effect paintings and material ramps live in dimensional_effect_icons.py.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image, ImageDraw, ImageFont
from injury_debuff_icons import preview as injury_debuff_preview
from painted_herbal_garden import herb, seed_packet
from dimensional_effect_icons import build as dimensional_effects

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


def pack(icons, columns, rows=None):
    sheet = Image.new("RGBA", (columns*16, (rows or ((len(icons)+columns-1)//columns))*16))
    for index, icon in enumerate(icons):
        assert icon.size == (16, 16)
        sheet.paste(icon, (index % columns*16, index // columns*16))
    return sheet


def build_sheets():
    index = json.loads((PACK / "assets/Tilesheets/harveyBuffIcons.json").read_text(encoding="utf-8-sig"))
    images, handbook, injury_legacy, mishap_images = dimensional_effects(index)
    atlas = pack([images[key] for key in sorted(index, key=index.get)], 16)
    sheets = {
        "medicalItems.png": pack(MEDICAL, 9), "arendItems.png": pack(AREND, 3),
        "herbalItems.png": pack([herb(i) for i in range(4)] + [seed_packet(i) for i in range(4)], 8),
        "injury-book.png": book(), "stress-handbook.png": book(True),
        "harveyBuffIcons.png": atlas, "mishapBuffIcons.png": pack(mishap_images, 6),
        "stressIcons.png": pack(handbook, 7), "injuryIcon.png": pack(injury_legacy, 4),
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
    # Publish the preview atomically so a viewer reading its old contents
    # cannot interrupt generation of the runtime PNGs and review artifacts.
    pending = ART / 'preview-effects.pending.png'
    all_icons.crop((0, 0, 1120, y)).save(pending)
    pending.replace(ART / 'preview-effects.png')
    index = json.loads((PACK / 'assets/Tilesheets/harveyBuffIcons.json').read_text(encoding='utf-8-sig'))
    injury_debuff_preview(PACK / 'art/injury-debuffs-v4', sheets['harveyBuffIcons.png'], index)


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
    from render_dimensional_effects import render as render_effects
    render_effects(sheets, index)
    report = {"cellSize": [16, 16], "method": "native integer pixel drawing; garden paintings reduced separately",
              "outline": "#301e25, opaque 1px", "buffCount": len(index),
              "currentEffects": {"source": "../../scripts/dimensional_effect_icons.py",
                                 "preview": "../effects-dimensional-16/preview.png",
                                 "gallery": "../effects-dimensional-16/all-effects.png",
                                 "method": "hand-painted pixel clusters; jewel colors; explicit light/shadow planes"},
              "anatomy": {"source": "../../scripts/native_anatomy.py",
                          "concept": "anatomy-v3/concept.png",
                          "prompt": "anatomy-v3/concept-prompt.txt",
                          "conceptMethod": "built-in image_gen, art direction only",
                          "runtimeMethod": "integer pixel sources on 16x16 canvas; no bitmap sampling"},
              "injuryDebuffs": {"source": "../../scripts/injury_debuff_icons.py",
                                "concept": "../injury-debuffs-v4/concept.png",
                                "preview": "../injury-debuffs-v4/preview.png",
                                "method": "one dominant symbol per injury, native 16x16"},
              "herbalGarden": {"source": "../../scripts/painted_herbal_garden.py",
                                "method": "v6 paintings; 3x intermediate color sampling with nearest decimation; unchanged alpha; saturated pixel bands",
                                "outline": "material colors; no expansion or edge whitening",
                                "colorSource": "../../scripts/refine_herbal_pixels.py",
                                "sources": "../herbal-garden/painted-v6/sources"},
              "sheets": {name: {"size": list(sheet.size), "sha256": hashlib.sha256(sheet.tobytes()).hexdigest(),
                                 "targets": TARGETS[name]} for name, sheet in sheets.items()}}
    (ART / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Native 16x16: 20 inventory, 2 books, 166 buffs, 21 stress, 12 injury, 6 mishap cells.")
    print("Installed into workspace." if install else "Exports only; use --install for workspace assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    main(parser.parse_args().install)
