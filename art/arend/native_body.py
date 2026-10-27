"""Centred, mirrored native trousers/boots and one-pixel walking body bob."""
from PIL import Image

O = (18, 8, 3, 255)
P = (73, 47, 27, 255)
H = (76, 52, 32, 255)
D = (38, 26, 17, 255)
S = (4, 0, 0, 255)


def legs(back=False, raised=None):
    result = Image.new('RGBA', (16, 8))
    boot = (53, 28, 15, 255) if back else (71, 38, 20, 255)
    shine = (71, 38, 20, 255) if back else (105, 67, 41, 255)
    # The torso/head axis is x=7 in a 15-pixel silhouette, not x=7.5.
    # Build one leg and mirror it about precisely that axis.
    for y in range(8):
        result.putpixel((7, y), O)
    for x in range(3, 12):
        result.putpixel((x, 0), P if 3 < x < 11 else O)
    result.putpixel((7, 0), D)
    for y in range(1, 5):
        for x, color in ((3, O), (4, H), (5, P), (6, D)):
            result.putpixel((x, y), color)
            result.putpixel((14 - x, y), color)
    for y, colors in ((5, (O, boot, boot, boot, O)),
                      (6, (O, boot, shine, boot, O)),
                      (7, (S, S, S, S, S))):
        for x, color in zip(range(2, 7), colors):
            result.putpixel((x, y), color)
            result.putpixel((14 - x, y), color)
    if raised:
        x0, x1 = (2, 7) if raised == 'left' else (8, 13)
        patch = result.crop((x0, 2, x1, 8))
        result.paste((0, 0, 0, 0), (x0, 0, x1, 8))
        result.paste(patch, (x0, 0))
    return result


def standing(base, back=False):
    result = base.copy()
    result.paste(legs(back=back), (0, 24))
    return result


def upper_bob(base, amount=1):
    result = base.copy()
    # Duplicate a torso row at the join rather than opening a transparent gap.
    result.paste(base.crop((0, amount, 16, 20 + amount)), (0, 0))
    return result


def walk(base, back=False):
    neutral = standing(base, back=back)
    result = []
    for phase, lifted in enumerate((None, 'right', None, 'left')):
        pose = neutral.copy()
        if phase in (1, 3):
            for x0, x1, dy in ((0, 3, -1 if phase == 1 else 1),
                               (12, 15, 1 if phase == 1 else -1)):
                arm = neutral.crop((x0, 19, x1, 24))
                pose.paste((0, 0, 0, 0), (x0, 19, x1, 25))
                pose.paste(arm, (x0, 19 + dy))
                if dy > 0:
                    pose.paste(arm.crop((0, 0, arm.width, 1)), (x0, 19))
            pose = upper_bob(pose)
        pose.paste(legs(back=back, raised=lifted), (0, 24))
        result.append(pose)
    return result
