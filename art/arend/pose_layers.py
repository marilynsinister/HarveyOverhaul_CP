"""Native pixel layers: limbs with a fixed shoulder, opaque book covers, breath.

All coordinates are on the 16x32 game grid. Motion is drawn in the actor's
layers; no frame is rescaled and no breathing phase erodes a sleeve contour.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from native_body import standing

ART = Path(__file__).resolve().parent
O = (18, 8, 3, 255)
J = (73, 47, 27, 255)
J_LIGHT = (92, 61, 38, 255)
J_DARK = (38, 26, 17, 255)
SKIN = (234, 157, 103, 255)
LIGHT = (248, 185, 128, 255)
PAGE_LIGHT = (248, 224, 182, 255)
PAGE_SHADE = (159, 133, 99, 255)


def front_base(glasses=False):
    with Image.open(ART / 'gesture_bases.png') as sheet:
        y = 32 if glasses else 0
        return standing(sheet.convert('RGBA').crop((0, y, 16, y + 32)))


def palm(draw, x, y):
    draw.rectangle((x, y, x + 1, y + 1), fill=SKIN)
    draw.point((x, y), fill=LIGHT)


def remove_arm(base, side):
    pose = base.copy()
    box = (0, 16, 4, 24) if side == 'left' else (11, 16, 16, 24)
    pose.paste((0, 0, 0, 0), box)
    # Exposed side of the torso stays solid behind the moving forearm.
    d = ImageDraw.Draw(pose)
    x = 3 if side == 'left' else 11
    d.line((x, 17, x, 23), fill=J_DARK)
    return pose


def arm(base, side, wrist, profile=False):
    if not profile and wrist == ((1, 22) if side == 'left' else (13, 22)):
        return base.copy()
    pose = remove_arm(base, side)
    x, y = wrist
    shoulder = (2, 16) if side == 'left' else (10 if profile else 11, 16)
    elbow_y = round(20 - max(0, 20 - y) * 0.6)
    elbow = (2 if side == 'left' else 11 if profile else 13, elbow_y)
    d = ImageDraw.Draw(pose)
    path = (shoulder, elbow, (x, y + 1))
    # A continuous four-pixel sleeve, with a two-pixel cloth interior.
    # Fill the elbow joint explicitly so diagonals cannot leave a broken hinge.
    d.line(path, fill=O, width=4, joint='curve')
    d.ellipse((elbow[0] - 1, elbow[1] - 1, elbow[0] + 2, elbow[1] + 2), fill=O)
    d.line(path, fill=J, width=2, joint='curve')
    d.rectangle((elbow[0], elbow[1], elbow[0] + 1, elbow[1] + 1), fill=J)
    d.point((elbow[0], elbow[1]), fill=J_LIGHT)
    palm(d, x, y)
    pose.paste(base.crop((0, 24, 16, 32)), (0, 24))
    return pose


def gesture_phases():
    base = front_base()
    return [arm(base, 'left', p) for p in
            ((1, 22), (2, 21), (3, 20), (4, 19), (5, 18), (5, 19), (4, 20), (3, 21))]


def glasses_phases():
    base = front_base(glasses=True)
    return [arm(base, 'right', p) for p in
            ((13, 22), (13, 20), (13, 18), (12, 16), (12, 14), (11, 12), (11, 10), (11, 9))]


def chin_phases(base):
    return [arm(base, 'right', p) for p in
            ((13, 22), (12, 21), (11, 20), (11, 19), (10, 17), (9, 15), (9, 13), (10, 18))]


def profile_phases(base):
    # Adjust the lapel at chest height; the wrist never gestures at the waist.
    return [arm(base, 'right', p, profile=True) for p in
            ((11, 18), (11, 17), (11, 16), (10, 15), (10, 14), (11, 15), (11, 16), (11, 17))]


def breathing(base, stage):
    """Subtle cloth movement over the ribcage; head, neck and outline stay fixed."""
    pose = base.copy()
    if stage == 0:
        return pose
    top = 19 if stage == 1 else 17
    for y in range(top, 22):
        for x in range(3, 12):
            current = base.getpixel((x, y))
            shifted = base.getpixel((x, y + 1))
            interior = all(base.getpixel(p)[3] for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            if interior and current[3] and shifted[3] and max(current[:3]) <= 130 and max(shifted[:3]) <= 130:
                pose.putpixel((x, y), shifted)
    return pose


def reader_pose(phase=0):
    # Preserve the preferred v4 reader pixel for pixel, including its large book.
    with Image.open(ART / 'reading_base.png') as image:
        base = image.convert('RGBA')
    pose = base.copy()
    d = ImageDraw.Draw(pose)
    shapes = (
        ((10, 17), (10, 16), (8, 18)),
        ((9, 17), (9, 15), (7, 18)),
        ((8, 17), (7, 15), (7, 18)),
        ((7, 18), (6, 15), (6, 17)),
        ((7, 18), (5, 16), (4, 17)),
        ((7, 18), (4, 17), (5, 18)),
    )
    if phase:
        d.polygon(shapes[phase - 1], fill=PAGE_LIGHT)
        d.line(shapes[phase - 1][:2], fill=PAGE_SHADE)
    # The original front cover, hands and body occlude every lower page pixel.
    pose.paste(base.crop((0, 18, 16, 32)), (0, 18))
    return pose


def warming_pose(base, y):
    base = remove_arm(remove_arm(base, 'left'), 'right')
    d = ImageDraw.Draw(base)
    for path in (((2, 16), (2, y + 2), (4, y + 3)),
                 ((12, 16), (12, y + 2), (10, y + 3))):
        d.line(path, fill=O, width=3)
        d.line(path, fill=J, width=1)
    palm(d, 3, y + 2)
    palm(d, 11, y + 2)
    with Image.open(ART / 'cup.png') as cup:
        base.alpha_composite(cup.convert('RGBA'), (4, y))
    return base
