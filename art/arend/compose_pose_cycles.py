"""Native layered pose cycles and intermediate phases for frames 0–87.

pose_bases.png is the reviewed pre-edit native sheet region 28–55. A single
head, body and foot placement is used for each cycle. Only the named layers
change; furniture and the rest of the silhouette are never rescaled.
"""
from pathlib import Path

from PIL import Image, ImageDraw
from native_body import standing, walk
from pose_layers import (reader_pose, breathing, gesture_phases, glasses_phases,
                         chin_phases, profile_phases, warming_pose, arm)

ART = Path(__file__).resolve().parent
OUTLINE = (18, 8, 3, 255)
JACKET = (73, 47, 27, 255)
SKIN = (234, 157, 103, 255)
HIGHLIGHT = (248, 185, 128, 255)


def source(index):
    with Image.open(ART / 'pose_bases.png') as sheet:
        x, y = index % 4 * 16, (index // 4 - 7) * 32
        pose = sheet.convert('RGBA').crop((x, y, x + 16, y + 32))
        return pose if index == 40 else standing(pose, back=index in range(36, 40))


def page_pose(phase):
    return reader_pose(phase)


def reader():
    return [page_pose(p) for p in (0, 3, 5, 0)]


def breath_pose(base, level):
    return breathing(base, level)


def breathe(base):
    return [breath_pose(base, n) for n in (0, 1, 2, 1)]


def clear_hands(base, box):
    result = base.copy()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = base.getpixel((x, y))
            if a and r > 110 and r > g * 1.15 and g > 50:
                result.putpixel((x, y), JACKET)
    return result


def hand(draw, x, y):
    draw.rectangle((x, y, x + 1, y + 1), fill=SKIN)
    draw.point((x, y), fill=HIGHLIGHT)


def armchair():
    base = clear_hands(source(40), (4, 18, 12, 24))
    # The two central shoes are mirrored; chair legs remain on the source pixels.
    feet = standing(source(44)).crop((2, 28, 13, 32))
    base.paste(feet, (2, 28))
    result = []
    for y in (21, 20, 20, 21):
        pose = base.copy()
        draw = ImageDraw.Draw(pose)
        hand(draw, 5, y)
        hand(draw, 9, y)
        result.append(pose)
    return result


def chair_transition():
    base = clear_hands(armchair()[0], (4, 18, 12, 24))
    result = []
    for rise, left_x, right_x in ((2, 3, 11), (1, 3, 11), (0, 4, 10), (1, 3, 11)):
        pose = base.copy()
        # Only the actor rises. Furniture starts at y=14, outside the torso mask.
        actor = Image.new('RGBA', (16, 32))
        actor.paste(base.crop((0, 0, 16, 14)), (0, 0))
        actor.paste(base.crop((2, 14, 13, 24)), (2, 14))
        pose.paste((0, 0, 0, 0), (0, 0, 16, 14))
        pose.paste((0, 0, 0, 0), (2, 14, 13, 24))
        pose.alpha_composite(actor, (0, -rise))
        # Keep the pelvis joined to the stationary thighs while the torso rises.
        if rise:
            pose.paste(base.crop((2, 24 - rise, 13, 24)), (2, 24 - rise))
        draw = ImageDraw.Draw(pose)
        # Hands push against the armrests; shoulders/coat rise as one actor.
        for path in (((4, 16 - rise), (3, 19 - rise // 2), (left_x, 21)),
                     ((10, 16 - rise), (11, 19 - rise // 2), (right_x, 21))):
            draw.line(path, fill=OUTLINE, width=4, joint='curve')
            draw.line(path, fill=JACKET, width=2, joint='curve')
        hand(draw, left_x, 21)
        hand(draw, right_x, 21)
        # Lower furniture/feet are a static layer behind the actor.
        pose.paste(base.crop((0, 24, 16, 32)), (0, 24))
        result.append(pose)
    return result


def cup_pose(y, grip=False):
    # Use one standing front base for the whole tea cycle. Original loose
    # hands become coat shading before the new forearms are drawn.
    base = source(44)
    for box in ((0, 18, 4, 25), (12, 18, 16, 25)):
        base = clear_hands(base, box)
    draw = ImageDraw.Draw(base)
    left = [(2, 17), (3, y + 2), (4, y + 2)]
    right = [(12, 17), (12, y + 2), (11, y + 2)]
    for points in (left, right):
        draw.line(points, fill=OUTLINE, width=3)
        draw.line(points, fill=JACKET, width=1)
    hand(draw, 3 if not grip else 4, y + 1)
    hand(draw, 11, y + 1)
    with Image.open(ART / 'cup.png') as cup:
        base.alpha_composite(cup.convert('RGBA'), (4, y))
    # Drawing the arms must not alter any trouser or shoe pixels.
    base.paste(source(44).crop((0, 24, 16, 32)), (0, 24))
    return base


def conversation():
    phases = profile_phases(source(54))
    return [phases[i] for i in (0, 2, 4, 6)]


def birds():
    rest = arm(source(54), 'right', (10, 22), profile=True)
    return [breathing(rest, stage) for stage in (0, 1, 2, 1)]


def build_cycles():
    result = reader()
    chin = chin_phases(source(32))
    result += [chin[i] for i in (0, 3, 6, 7)]
    result += breathe(source(36))
    result += armchair()
    result += [cup_pose(y) for y in (18, 15, 12, 15)]
    result += [warming_pose(source(44), y) for y in (18, 17, 16, 17)]
    result += conversation()
    result += [page_pose(p) for p in (1, 2, 4, 6)]  # 56–59
    result += [cup_pose(y) for y in (17, 16, 14, 13)]  # 60–63
    result += chair_transition()  # 64–67
    result += birds()  # 68–71
    result += [chin[i] for i in (1, 2, 4, 5)]  # 72–75
    result += [gesture_phases()[i] for i in (1, 3, 5, 7)]  # 76–79
    result += [glasses_phases()[i] for i in (1, 4, 5, 6)]  # 80–83
    result += [profile_phases(source(54))[i] for i in (1, 3, 5, 7)]  # 84–87
    assert len(result) == 60
    return result


def main():
    # The first five override rows map to runtime rows 0, 2, 4, 5, 6.
    with Image.open(ART / 'sprite_fixes.png') as fixed:
        prefix = fixed.convert('RGBA').crop((0, 0, 64, 160))
    sheet = Image.new('RGBA', (64, 640))
    for row in range(5):
        cells = [prefix.crop((c * 16, row * 32, c * 16 + 16, row * 32 + 32)) for c in range(4)]
        if row < 2:
            # Immutable snapshot makes authoring idempotent even after body bob.
            with Image.open(ART / 'walk_bases.png') as bases:
                cells = walk(bases.convert('RGBA').crop((0, row * 32, 16, row * 32 + 32)), back=row == 1)
        elif row == 4:
            cells = reader()
        elif row == 2:
            cells = [gesture_phases()[i] for i in (0, 2, 4, 6)]
        elif row == 3:
            cells = [glasses_phases()[i] for i in (0, 3, 7, 2)]
        else:
            cells = [standing(pose) for pose in cells]
        for c, pose in enumerate(cells):
            sheet.paste(pose, (c * 16, row * 32))
    for i, pose in enumerate(build_cycles()):
        sheet.paste(pose, (i % 4 * 16, 160 + i // 4 * 32))
    sheet.save(ART / 'sprite_fixes.png')
    print('Composed layered book, shoulder breathing and articulated limbs; 88 runtime cells.')


if __name__ == '__main__':
    main()
