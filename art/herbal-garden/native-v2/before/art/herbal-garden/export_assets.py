"""Mechanical export of image_gen art: crop, nearest sampling, palette, packing.

No replacement artwork is drawn here. Run with --install to copy runtime PNGs.
Stardew 1.6 packs TWO crops per 256px row; growth frames are offset by one.
"""
from pathlib import Path
import argparse
import shutil
from collections import deque
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PACK = HERE.parent.parent
NAMES = ["glass-dewberry", "moonvelvet", "amber-heartleaf", "silver-seamleaf"]
LABELS = ["Стеклянная росница", "Лунная бархатница", "Янтарный сердцелист", "Серебряный шовник"]


def cell(source, col, row, cols, rows):
    return source.crop((col * source.width // cols, row * source.height // rows,
                        (col + 1) * source.width // cols, (row + 1) * source.height // rows))


def regions(source, cols, rows):
    # Image generation uses a loose grid. Find the separate silhouettes before
    # packing the strict game grid, so a neighboring leaf cannot leak into a cell.
    width, height = source.size
    mask = bytearray(source.getchannel("A").point(lambda v: 255 if v >= 192 else 0).tobytes())
    found = []
    for start in range(len(mask)):
        if not mask[start]:
            continue
        mask[start] = 0
        queue = deque([start])
        x0 = x1 = start % width
        y0 = y1 = start // width
        count = 0
        while queue:
            index = queue.popleft()
            x, y = index % width, index // width
            x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
            count += 1
            for dy in (-1, 0, 1):
                yy = y + dy
                if not 0 <= yy < height:
                    continue
                for dx in (-1, 0, 1):
                    xx = x + dx
                    if 0 <= xx < width:
                        neighbor = yy * width + xx
                        if mask[neighbor]:
                            mask[neighbor] = 0
                            queue.append(neighbor)
        if count >= 64:
            found.append((count, (x0, y0, x1 + 1, y1 + 1)))
    found = sorted(found, reverse=True)[:cols * rows]
    if len(found) != cols * rows:
        raise ValueError(f"Expected {cols * rows} source silhouettes, got {len(found)}")
    result = []
    for row in range(rows):
        boxes = [box for _, box in found if int(((box[1] + box[3]) / 2) * rows / height) == row]
        if len(boxes) != cols:
            raise ValueError(f"Expected {cols} source sprites in row {row}, got {len(boxes)}")
        result.append([source.crop(box) for box in sorted(boxes)])
    return result


def bounds(source):
    # Ignore only the near-transparent generated edge fringe.
    alpha = source.getchannel("A").point(lambda v: 255 if v >= 192 else 0)
    box = alpha.getbbox()
    if box is None:
        raise ValueError("Empty generated cell")
    return box


def sampled(source, box, width, height, palette):
    result = source.crop(box).resize((width, height), Image.Resampling.NEAREST)
    alpha = result.getchannel("A").point(lambda v: 255 if v >= 160 else 0)
    result = result.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
    result.putalpha(alpha)
    return result


def export(install=False):
    out = HERE / "exports"
    out.mkdir(exist_ok=True)
    inventory = Image.open(HERE / "generated/herbal-inventory.png").convert("RGBA")
    crops = Image.open(HERE / "generated/herbal-crops.png").convert("RGBA")
    # Shared palette sampled from opaque source art; transparent pixels excluded.
    pixels = [p[:3] for source in (inventory, crops)
              for p in source.resize((512, 256), Image.Resampling.NEAREST).get_flattened_data() if p[3] >= 192]
    swatch = Image.new("RGB", (len(pixels), 1))
    swatch.putdata(pixels)
    palette = swatch.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    inventory_regions = regions(inventory, 4, 2)
    crop_regions = regions(crops, 8, 4)
    native_path = PACK / 'art/native-16/exports/herbalItems.png'
    native_inventory = Image.open(native_path).convert('RGBA') if native_path.is_file() else None
    sheet = Image.new("RGBA", (128, 16))
    for i in range(8):
        if native_inventory is not None:
            sprite = native_inventory.crop((i * 16, 0, i * 16 + 16, 16))
        else:
            source = inventory_regions[i // 4][i % 4]
            box = bounds(source)
            scale = min(14 / (box[2] - box[0]), 14 / (box[3] - box[1]))
            width = max(1, round((box[2] - box[0]) * scale))
            height = max(1, round((box[3] - box[1]) * scale))
            sprite = Image.new("RGBA", (16, 16))
            sprite.paste(sampled(source, box, width, height, palette), ((16 - width) // 2, (16 - height) // 2))
        sheet.paste(sprite, (i * 16, 0))
        suffix = "-seeds" if i >= 4 else ""
        sprite.save(out / f"{NAMES[i % 4]}{suffix}.png")
    sheet.save(out / "herbalItems.png")

    # getSourceRect: x = (phase+1)*16 + (cropIndex%2)*128.
    # Seed alternates 0/1. After a regrowing harvest the engine uses 6 (ripe)
    # or 7 (regrowing), regardless of the number of growing phases.
    frame_map = [0, 0, 1, 2, 3, 4, 4, 5]
    field = Image.new("RGBA", (256, 64))
    stages = []
    for plant in range(4):
        plant_cells = crop_regions[plant]
        # One scale per plant keeps seedlings visibly smaller than mature plants.
        mature_box = bounds(plant_cells[4])
        scale = min(14 / (mature_box[2] - mature_box[0]), 23 / (mature_box[3] - mature_box[1]))
        row = []
        for stage, source in enumerate(plant_cells):
            box = bounds(source)
            width = min(14, max(2, round((box[2] - box[0]) * scale)))
            height = min(23, max(2, round((box[3] - box[1]) * scale)))
            sprite = Image.new("RGBA", (16, 32))
            # Bottom is pixel 30, matching the vanilla crop's ground line.
            sprite.paste(sampled(source, box, width, height, palette), ((16 - width) // 2, 31 - height))
            row.append(sprite)
            sprite.save(out / f"{NAMES[plant]}-stage-{stage}.png")
        for frame, stage in enumerate(frame_map):
            field.paste(row[stage], ((plant % 2) * 128 + frame * 16, (plant // 2) * 32))
        stages.append(row)
    field.save(out / "herbalCrops.png")

    preview = Image.new("RGB", (1110, 730), "#25232e")
    draw = ImageDraw.Draw(preview)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 18)
    small = ImageFont.truetype(str(font_path), 14)
    title = ImageFont.truetype(str(font_path), 24)
    draw.text((24, 18), "АПТЕКАРСКИЙ САД ХАРВИ", fill="#fff0cd", font=title)
    draw.text((24, 54), "Игровые PNG • иконки 16×16 • растения 16×32 • увеличение без сглаживания", fill="#c0b9bd", font=small)
    for plant in range(4):
        y = 94 + plant * 150
        draw.text((24, y), LABELS[plant], fill="#f6d290", font=font)
        for offset, index in ((24, plant), (134, plant + 4)):
            icon = sheet.crop((index * 16, 0, index * 16 + 16, 16)).resize((80, 80), Image.Resampling.NEAREST)
            preview.paste(icon, (offset, y + 38), icon)
        for stage in range(6):
            sprite = stages[plant][stage].resize((64, 128), Image.Resampling.NEAREST)
            x = 340 + stage * 110
            preview.paste(sprite, (x, y - 7), sprite)
    draw.text((24, 702), "Урожай    Семена                         Посев → рост → зрелость → после сбора", fill="#c0b9bd", font=small)
    preview.save(HERE / "preview.png")
    if install:
        for name, folder in (("herbalItems.png", "Items"), ("herbalCrops.png", "Crops")):
            target = PACK / "assets" / folder / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(out / name, target)
    print("Exported 8 inventory icons, 32 source stages, 256x64 runtime crop atlas and preview.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    export(parser.parse_args().install)
