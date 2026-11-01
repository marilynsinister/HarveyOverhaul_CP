"""Reduce garden colors, then add a dark one-pixel material-colored contour.

The reducer reserves a pixel around the body, so the ink fits the game cell.
"""
from colorsys import rgb_to_hls, hls_to_rgb, rgb_to_hsv
from PIL import Image


INKS = {
    'leaf': (23, 50, 39),
    'berry': (26, 37, 77),
    'bell': (61, 29, 64),
    'gold': (95, 47, 28),
    'ivory': (81, 51, 43),
    'stem': (70, 30, 29),
    'paper': (86, 48, 35),
}


def material_ink(rgb, kind, packet=False):
    if packet:
        return INKS['paper']
    h, s, value = rgb_to_hsv(*(c/255 for c in rgb))
    if 0.19 < h < 0.52 and s > 0.20:
        return INKS['leaf']
    if kind == 2 and (h > 0.94 or h < 0.055) and s > 0.35:
        return INKS['stem']
    return INKS[('berry', 'bell', 'gold', 'ivory')[kind]]


def edge_positions(image):
    a = image.getchannel('A')
    return {(x, y) for y in range(image.height) for x in range(image.width)
            if a.getpixel((x, y)) and any(
                not (0 <= xx < image.width and 0 <= yy < image.height)
                or not a.getpixel((xx, yy))
                for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)))}


def grade(rgb, kind):
    h, light, saturation = rgb_to_hls(*(c/255 for c in rgb))
    # Keep blue, purple and gold identities; prevent gray-olive foliage from
    # disappearing into the warm soil. Mint leaves retain their silver glints.
    foliage = 0.18 < h < 0.51
    if foliage:
        if kind in (0, 1) and h < 0.28:
            h = 0.31
        elif kind == 3:
            h = min(0.43, max(0.36, h))
    elif kind == 1 and h > 0.64:
        h = min(0.82, max(0.72, h))
    elif kind == 2 and h > 0.52:
        # A near-neutral dark source edge must not become a violet speck
        # after fine detail sampling and sharpening the reddish stem.
        h = 0.05
    elif kind == 3 and h > 0.58:
        h = 0.40
    light = light**(1.30 if kind == 3 and foliage else 1.20 if foliage else 1.16)
    saturation_cap = (0.86 if kind == 3 else 0.88) if foliage else 0.94
    saturation_factor = (1.58 if kind == 3 else 1.42) if foliage else 1.32
    saturation = min(saturation_cap, saturation*saturation_factor)
    # Discrete value bands replace the soft succession of painterly half-tones.
    light = round(light*18)/18
    return tuple(round(c*255) for c in hls_to_rgb(h, light, saturation))


def palette(colors, count):
    training = Image.new('RGB', (len(colors), 1))
    training.putdata(colors)
    p = training.quantize(colors=count, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    colors = [tuple(p.getpalette()[i:i+3]) for i in range(0, count*3, 3)]
    return colors


def nearest_material(rgb, colors):
    h, s, _ = rgb_to_hsv(*(c/255 for c in rgb))
    if s >= 0.25:
        related = []
        for color in colors:
            ch = rgb_to_hsv(*(c/255 for c in color))[0]
            if min(abs(h-ch), 1-abs(h-ch)) <= 0.12:
                related.append(color)
        colors = related or colors
    def distance(candidate):
        ch, cs, _ = rgb_to_hsv(*(c/255 for c in candidate))
        hue_distance = min(abs(h-ch), 1-abs(h-ch))
        return sum((a-b)**2 for a, b in zip(rgb, candidate)) + (hue_distance*255)**2*min(s, cs)*3
    return min(colors, key=distance)


def render(images):
    corrected = []
    for index, image in enumerate(images):
        kind = index//8
        alpha = image.getchannel('A')
        result = image.copy()
        for y in range(image.height):
            for x in range(image.width):
                rgba = image.getpixel((x, y))
                if not rgba[3]:
                    result.putpixel((x, y), (0, 0, 0, 0))
                    continue
                # Sharpen only against opaque neighbors: transparency cannot
                # introduce a light halo or a black fringe around a thin stem.
                neighbors = [image.getpixel((xx, yy))[:3]
                             for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
                             if 0 <= xx < image.width and 0 <= yy < image.height and alpha.getpixel((xx, yy))]
                rgb = rgba[:3]
                if len(neighbors) >= 2:
                    rgb = tuple(max(0, min(255, round(c+0.45*(c-sum(p[i] for p in neighbors)/len(neighbors)))))
                                for i, c in enumerate(rgb))
                rgb = grade(rgb, kind)
                result.putpixel((x, y), rgb+(255,))
        corrected.append(result)

    core_colors = [p[:3] for im in corrected for p in im.get_flattened_data() if p[3]]
    core = palette(core_colors, 48)
    core_lookup = {}
    result = []
    for index, im in enumerate(corrected):
        mapped = im.copy()
        for y in range(im.height):
            for x in range(im.width):
                q = im.getpixel((x, y))
                if not q[3]:
                    mapped.putpixel((x, y), (0, 0, 0, 0))
                    continue
                rgb = q[:3]
                if rgb not in core_lookup:
                    core_lookup[rgb] = nearest_material(rgb, core)
                mapped.putpixel((x, y), core_lookup[rgb]+(255,))
        # Eight-neighbor ink gives leaves, petals and berries a continuous
        # contour, including diagonal tips. Keep the bright body untouched.
        # Pick a material from nearby BODY pixels, never from already drawn ink.
        for y in range(im.height):
            for x in range(im.width):
                if im.getpixel((x, y))[3]:
                    continue
                neighbors = [im.getpixel((xx, yy))[:3]
                             for yy in range(max(0, y-1), min(im.height, y+2))
                             for xx in range(max(0, x-1), min(im.width, x+2))
                             if im.getpixel((xx, yy))[3]]
                if neighbors:
                    rgb = max(neighbors, key=lambda p: max(p)-min(p))
                    mapped.putpixel((x, y), material_ink(rgb, index//8, index%8 == 7)+(255,))
        result.append(mapped)
    return result
