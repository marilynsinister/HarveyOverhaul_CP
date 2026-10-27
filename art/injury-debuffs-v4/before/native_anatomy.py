"""Hand-pixelled anatomical illustrations, drawn directly on a 16x16 grid.

Organic silhouettes were hand-transcribed from the imagegen art-direction
concept in art/native-16/anatomy-v3. This module never loads or resizes it.
"""
from PIL import Image


def make_icons(palette):
    colors = {**palette, "c": (255, 218, 178, 255)}
    ink = colors['o']

    def tile(source):
        rows = [row.strip() for row in source.strip().splitlines()]
        assert len(rows) <= 16 and all(len(row) <= 16 for row in rows), rows
        rows = [row.ljust(16, '.') for row in rows]
        rows += ['.'*16]*(16-len(rows))
        image = Image.new('RGBA', (16, 16))
        image.putdata([colors[char] for row in rows for char in row])
        return seal(image)

    def seal(image):
        # Keep a complete single-pixel contour, including finger gaps and
        # the arch of the foot. No automatic recoloring of interior artwork.
        source = image.copy()
        for y in range(16):
            for x in range(16):
                if source.getpixel((x, y))[3] and any(
                    not (0 <= nx < 16 and 0 <= ny < 16) or not source.getpixel((nx, ny))[3]
                    for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
                ):
                    image.putpixel((x, y), ink)
        return image

    def draw_on(base, marks):
        image = base.copy()
        for x, y, color in marks:
            # Treatments stay inside the shape; a wrap must not erase the
            # silhouette that tells the player which part of the body it is.
            if image.getpixel((x, y))[3] and image.getpixel((x, y)) != ink:
                image.putpixel((x, y), colors[color])
        return image

    def badge(base, kind):
        patterns = {
            'pain': ['..o..', '.oro.', 'orpro', '.oro.', '..o..'],
            'care': ['..o..', '.ogo.', 'ogWgo', '.ogo.', '..o..'],
            'leaf': ['..ooo', '.olGo', 'olGGo', 'oGGo.', '.oo..'],
            'rest': ['ooooo', 'oiiio', 'ooioo', 'oiooo', 'oiiio'],
            'drop': ['..o..', '.oIo.', 'oIiIo', 'oIjIo', '.ooo.'],
            'gold': ['..o..', '.oyo.', 'oyayo', '.oyo.', '..o..'],
            'down': ['.ooo.', '.oro.', 'orrro', '.oro.', '..o..'],
            'heart': ['oo.oo', 'orpro', 'orpro', '.oro.', '..o..'],
        }
        rows = patterns[kind]
        image = base.copy()
        # Keep the illustration visible. The old fixed lower-right badge
        # covered the wrist, heel or lower ribs in several compositions.
        candidates = [(10, 10), (10, 1), (1, 1), (1, 10)]
        x0, y0 = min(candidates, key=lambda pos: sum(
            bool(base.getpixel((x+pos[0], y+pos[1]))[3])
            for y, row in enumerate(rows) for x, char in enumerate(row) if char != '.'))
        for y, row in enumerate(rows):
            assert len(row) == 5, (kind, row)
            for x, char in enumerate(row):
                if char != '.': image.putpixel((x+x0, y+y0), colors[char])
        return seal(image)

    head = tile('''
        ................
        ......oooo......
        ....oobhhboo....
        ...obhHhhbBBo...
        ..obHhhhhhBBBo..
        ..obhkkkkbBBBo..
        ..obkkcckkBBBo..
        ..okkccKkkbBBo..
        .okccooKkKkbBo..
        ..okcckKkoKBo...
        ...okkkKKKKBo...
        ....okKKKKoo....
        .....okKKko.....
        .....okKKo......
        ......ooo.......
        ................
    ''')
    head_hurt = draw_on(head, [(5, 5, 'p'), (6, 5, 'r'), (5, 6, 'p'), (6, 6, 'R')])
    head_wrap = draw_on(head, [(6, 4, 'W'), (7, 4, 'w'), (5, 5, 'W'), (6, 5, 'W'),
                               (7, 5, 'w'), (5, 6, 'w'), (6, 6, 's')])
    head_rest = tile('''
        ................
        ................
        ...oooooo.......
        ..obhHhbBo......
        .obhHhhbBBo.....
        .obkkckkBBBo....
        .okkcckkKkBo....
        .okccooKkkko....
        ..okkkkKtKKo....
        ...okKKKKoo.....
        ..oWWooooWWoo...
        .oWWWWWWWWWWwo..
        .oWWWWWWWWwwwso.
        ..owWWWWwwwsso..
        ...oooooooooo...
        ................
    ''')

    arm = tile('''
        ................
        .....ooo........
        ....okcco.......
        ...okcccko......
        ..okccKKkKo.....
        ..okckotKoo.....
        .okcckooo..ooo..
        .okccKo...okcKo.
        .okccKooooKccKo.
        .okcckkkkccckKo.
        .okckkkkccckKKo.
        ..okKkkcckkKKo..
        ...okKKKKKKKo...
        ....ooooooo.....
        ................
        ................
    ''')
    muscle = draw_on(arm, [(10, 8, 'p'), (11, 8, 'r'), (9, 9, 'r'), (10, 9, 'R'), (11, 9, 'p')])
    arm_wrap = draw_on(arm, [(10, 8, 'W'), (11, 8, 'W'), (12, 8, 'w'),
                             (9, 9, 'W'), (10, 9, 'w'), (11, 9, 's'),
                             (8, 10, 'W'), (9, 10, 'w'), (10, 10, 's')])
    thin_arm = tile('''
        ................
        .....ooo........
        ....okcko.......
        ...okccKko......
        ..okckKKKKo.....
        ..okckoKKoo.....
        .okckKooo.......
        .okckKo....ooo..
        .okckKoooooKKKo.
        ..okkKKKKkkcKKo.
        ..okkKKKkkkKKKo.
        ...oKKKKKKKKKo..
        ....oKKKKttto...
        .....ooooooo....
        ................
        ................
    ''')
    forearm = tile('''
        ................
        ..........oooo..
        .........okccKo.
        ........okccKKo.
        .......okccKKo..
        ......okccKKo...
        .....okccKKKo...
        ....okcckkKKo...
        ...okcckkKKo....
        ..okckkkKKKo....
        .okckKkkKkKo....
        .okckokkKkKo....
        .okco.okoKoo....
        ..oo..oo.oo.....
        ................
        ................
    ''')
    cut = draw_on(forearm, [(9, 4, 'p'), (8, 5, 'r'), (8, 6, 'R'), (7, 7, 'p')])
    stitched = draw_on(forearm, [(8, 4, 'S'), (10, 4, 'S'), (9, 4, 'R'), (7, 5, 'S'),
                                 (9, 5, 'S'), (8, 5, 'R'), (6, 6, 'S'), (8, 6, 'S'), (7, 6, 'R')])
    scar = draw_on(forearm, [(9, 4, 'K'), (8, 5, 'p'), (7, 6, 'K')])
    arm_bandage = draw_on(forearm, [(x, y, color)
        for y, start, row in ((4, 8, 'WWWWw'), (5, 7, 'wWWws'), (6, 6, 'WWWWws'), (7, 5, 'wwwwss'))
        for x, color in enumerate(row, start)])
    sling = tile('''
        ................
        ...........oo...
        ......oooooWwo..
        .....okccKoWwo..
        ....okccKoWWwo..
        ...okccKoWWWwo..
        ...okcKoWWWWwo..
        ....oKoWWWWWwo..
        ...oWWWWWWWWwo..
        ..okkkWWWwWWwo..
        .okccKWWWwWWwo..
        .okkkKWWWwwWwo..
        ..okKoWwwwwsso..
        ...ooowwwssso...
        ......oooooo....
        ................
    ''')
    foot = tile('''
        ................
        ........oooo....
        .......okccKo...
        .......okccKo...
        .......okckKo...
        .......okckKo...
        ......okkkKKo...
        .....okkkKKKoo..
        ....okcckkKKKko.
        ...okcckkKkkKKo.
        ..okcckkKkkKoo..
        .okcckkkKKoo....
        .okkKkKKoo......
        ..oooooo........
        ................
        ................
    ''')
    ankle = draw_on(foot, [(10, 6, 'v'), (9, 7, 'V'), (10, 7, 'n'), (11, 7, 'V'), (10, 8, 'v')])
    ankle_brace = draw_on(foot, [(x, y, color) for y, start, row in
        ((5, 8, 'Iij'), (6, 7, 'jiIj'), (7, 6, 'IijJI'), (8, 6, 'jjJ'))
        for x, color in enumerate(row, start)])
    leg_cast = foot.copy()
    cast_colors = {colors['c']: colors['W'], colors['k']: colors['W'], colors['K']: colors['w'], colors['t']: colors['s']}
    leg_cast.putdata([cast_colors.get(pixel, pixel) for pixel in foot.get_flattened_data()])
    leg_cast = draw_on(leg_cast, [(8, 4, 'w'), (9, 4, 's'), (10, 4, 's'), (11, 4, 's'),
        (7, 7, 'w'), (8, 7, 's'), (9, 7, 'w'), (10, 7, 's'), (11, 7, 's'),
        (5, 10, 'w'), (6, 10, 's'), (7, 10, 's'), (8, 10, 'w')])
    # The shoulder contour and tapered waist supply an immediately legible
    # human torso. Bone lines sit inside it instead of becoming a detached comb.
    torso = tile('''
        ................
        ......oooo......
        .....okccKo.....
        ...ookkcckKoo...
        ..okcckcckkkKo..
        .okccckcckkkKKo.
        .okccKkkKkkkkKo.
        .okkkKkkKkkkKKo.
        .oKkkKkkKkkKKo..
        ..oKkKkkKkkKo...
        ...oKkkkKKKo....
        ...okKkkKKKo....
        ..okkkkKKKKKo...
        ..oKKKKKKKKKo...
        ...ooooooooo....
        ................
    ''')
    back = draw_on(torso, [(7, y, 'K') for y in range(5, 12)] +
                           [(4, 5, 'K'), (5, 6, 't'), (6, 5, 'K'), (9, 5, 'K'), (10, 6, 't'),
                            (6, 9, 'k'), (8, 9, 'k')])
    back_pain = draw_on(back, [(6, 9, 'p'), (7, 9, 'r'), (8, 9, 'p'),
                              (6, 10, 'r'), (7, 10, 'R'), (8, 10, 'r')])
    back_wrap = draw_on(back, [(x, y, color) for y, row in [(9, 'WWWWWW'), (10, 'wWWwws'), (11, 'wwwwss')]
                              for x, color in enumerate(row, 4)])
    # Three airy, curved bone arches. Outline each native pixel stroke instead
    # of filling the gaps with a solid torso or dark oval behind the skeleton.
    ribcage = Image.new('RGBA', (16, 16))
    for y in range(2, 13):
        ribcage.putpixel((7, y), colors['W'])
        ribcage.putpixel((8, y), colors['w'])
    for x in range(6, 10):
        ribcage.putpixel((x, 2), colors['W' if x < 8 else 'w'])
    for cy, left in ((4, 2), (8, 2), (12, 3)):
        for x, y in ((left, cy-1), (left, cy), (left+1, cy+1),
                     (left+2, cy+1), (5, cy+1), (6, cy)):
            ribcage.putpixel((x, y), colors['W'])
            ribcage.putpixel((15-x, y), colors['w'])
    source = ribcage.copy()
    for y in range(16):
        for x in range(16):
            if not source.getpixel((x, y))[3] and any(
                0 <= nx < 16 and 0 <= ny < 16 and source.getpixel((nx, ny))[3]
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
            ):
                ribcage.putpixel((x, y), ink)
    ribs_bruise = draw_on(ribcage, [(12, 5, 'v'), (11, 5, 'V'), (10, 5, 'n')])
    ribs_wrap = draw_on(torso, [(x, y, color) for y, row in [(7, 'WWWWWWWW'), (8, 'wWWwwWWs'), (9, 'wwwsssss')]
                                for x, color in enumerate(row, 4)])
    lungs = tile('''
        ................
        .......oo.......
        ......oWwo......
        ......oWwo......
        ....oooWwooo....
        ...oppoWwoprRo..
        ..opcpWwWopprRo.
        ..opccWoWoprRRo.
        .opccWo.oWoprRo.
        .opccWo.oWorRRo.
        .oppcWo.oWorRRo.
        .oprrWo.oWorRRo.
        ..oRRo...orRRo..
        ...oo.....ooo...
        ................
        ................
    ''')
    palm = tile('''
        ................
        ........oo......
        .......okko.....
        ....oo.okcko....
        ...okkoKkcko.oo.
        ...okckoKkkookko
        ...okckoKkkokcko
        .oo.okkkkkkkkko.
        okkoKkkcckkKKKo.
        okckoKccckkkKKo.
        .okckkccckkKKKo.
        ..okkkcckkKKKo..
        ...okkkKKKKKo...
        ....okKKKKKo....
        .....okKKKo.....
        ......ooooo.....
    ''')
    numb_hand = palm.copy()
    skin_to_cool = {colors['c']: colors['F'], colors['k']: colors['f'], colors['K']: colors['e'], colors['t']: colors['S']}
    numb_hand.putdata([skin_to_cool.get(pixel, pixel) for pixel in palm.get_flattened_data()])
    rash = draw_on(forearm, [(10, 3, 'r'), (8, 5, 'r'), (7, 7, 'p'), (5, 9, 'r'), (6, 10, 'p')])
    burn = draw_on(forearm, [(9, 4, 'p'), (8, 5, 'r'), (9, 5, 'p'),
                            (7, 6, 'r'), (8, 6, 'R'), (6, 7, 'p'), (7, 7, 'r')])
    gel = draw_on(arm_bandage, [(8, 4, 'i'), (9, 4, 'I'), (7, 5, 'i'), (8, 5, 'I'),
                               (6, 6, 'i'), (7, 6, 'I'), (7, 7, 'j')])
    splinter = draw_on(palm, [(8, 9, 'b'), (7, 10, 'B'), (6, 11, 'p')])
    puncture = draw_on(forearm, [(9, 4, 'e'), (8, 5, 'r'), (9, 5, 'f'), (7, 6, 'p')])
    bone = tile('''
        ................
        .........oo.oo..
        ........oWwoWwo.
        ........oWWWWwo.
        .........oWWwo..
        ........oWWso...
        .......oWWso....
        ......oWWso.....
        .....oWWso......
        ....oWWso.......
        ..ooWWso........
        .oWWWWwo........
        .oWWwWWo........
        ..oo.oo.........
        ................
        ................
    ''')
    bone = draw_on(bone, [(10, 3, 'W'), (11, 4, 'w'), (8, 6, 'w'), (7, 7, 'w'),
                          (6, 8, 'w'), (5, 9, 'w'), (3, 11, 'W'), (5, 11, 's')])
    broken_bone = draw_on(bone, [(8, 5, 'R'), (7, 6, 'R'), (8, 6, 'r'), (7, 7, 'R')])
    healing_bone = draw_on(bone, [(7, 5, 'w'), (8, 5, 'W'), (6, 6, 's'), (7, 6, 'W'),
                                 (6, 7, 'w'), (7, 7, 'W')])

    icons = {
        'head': head, 'concussion': head_hurt, 'head_wrap': head_wrap, 'head_rest': head_rest,
        'arm': arm, 'muscle': muscle, 'arm_wrap': arm_wrap, 'thin_arm': thin_arm,
        'forearm': forearm, 'cut': cut, 'stitched': stitched, 'scar': scar,
        'arm_bandage': arm_bandage, 'sling': sling,
        'foot': foot, 'ankle': ankle, 'ankle_brace': ankle_brace, 'leg_cast': leg_cast,
        'back': back, 'back_pain': back_pain, 'back_wrap': back_wrap,
        'ribs': ribcage, 'ribs_bruise': ribs_bruise, 'ribs_wrap': ribs_wrap, 'lungs': lungs,
        'hand': palm, 'numb_hand': numb_hand, 'rash': rash, 'burn': burn, 'gel': gel,
        'splinter': splinter, 'puncture': puncture,
        'bone': bone, 'broken_bone': broken_bone, 'healing_bone': healing_bone,
    }
    return icons, badge


def replacements(palette):
    icons, badge = make_icons(palette)
    # Each phase is an illustration of the actual treatment, with one compact
    # additional cue. Detailed base artwork never goes through auto-shading.
    spec = {
        'buffPostSurgicalCare': ('stitched', 'care'),
        'HarveyMod_FracturedBone_Acute': ('broken_bone', 'pain'),
        'HarveyMod_FracturedBone_Cast': ('arm_bandage', 'gold'),
        'HarveyMod_FracturedBone_Recovery': ('healing_bone', 'leaf'),
        'HarveyMod_Concussion_Acute': ('concussion', 'pain'),
        'HarveyMod_Concussion_Rest': ('head_rest', None),
        'HarveyMod_Concussion_Limited': ('head_wrap', 'leaf'),
        'HarveyMod_Shrapnel_Surgery': ('puncture', 'pain'),
        'HarveyMod_Shrapnel_Healing': ('stitched', 'gold'),
        'HarveyMod_Shrapnel_Recovery': ('scar', 'leaf'),
        'HarveyMod_TornMuscles_Acute': ('muscle', 'pain'),
        'HarveyMod_TornMuscles_Healing': ('arm_wrap', 'gold'),
        'HarveyMod_SprainedAnkle_Acute': ('ankle', 'pain'),
        'HarveyMod_SprainedAnkle_Recovery': ('ankle_brace', 'leaf'),
        'HarveyMod_BruisedRibs_Acute': ('ribs_bruise', 'pain'),
        'HarveyMod_BruisedRibs_Healing': ('ribs_wrap', 'leaf'),
        'HarveyMod_DeepCuts_Acute': ('cut', 'pain'),
        'HarveyMod_DeepCuts_Healing': ('arm_bandage', 'care'),
        'HarveyMod_DeepCuts_Recovery': ('scar', 'care'),
        'HarveyMod_BurnWounds_Acute': ('burn', 'pain'),
        'HarveyMod_BurnWounds_Healing': ('gel', 'leaf'),
        'HarveyMod_BackStrain_Acute': ('back_pain', 'pain'),
        'HarveyMod_BackStrain_Recovery': ('back_wrap', 'leaf'),
        'buffHarveyTreatmentNumbness': ('numb_hand', 'care'),
        'buffBruisedRibs': ('ribs_bruise', None),
        'buffSprainedAnkle': ('ankle', None),
        'buffBackStrain': ('back_pain', None),
        'buffDeepCuts': ('cut', None),
        'buffBurnWounds': ('burn', None),
        'buffTornMuscles': ('muscle', None),
        'buffConcussion': ('concussion', None),
        'buffFracturedBone': ('broken_bone', None),
        'buffShrapnelWounds': ('puncture', None),
        'buffSurgicalWound': ('stitched', None),
        'HarveyMod_AllergicRash': ('rash', None),
        'HarveyMod_WetStitches': ('stitched', 'drop'),
        'HarveyMod_MuscleAtrophy': ('thin_arm', 'down'),
        'HarveyMod_BreathingDifficulty': ('lungs', None),
        'buffStressNumbness': ('numb_hand', None),
        'HarveyMod_Splinter': ('splinter', None),
        'buffStressClearMind': ('head', 'gold'),
    }
    drawings = {key: badge(icons[name], marker) if marker else icons[name].copy()
                for key, (name, marker) in spec.items()}
    legacy = [icons[name].copy() for name in (
        'muscle', 'arm_bandage', 'stitched', 'sling', 'cut', 'ribs_bruise',
        'ankle_brace', 'burn', 'rash', 'back_pain', 'ribs_wrap', 'leg_cast')]
    return drawings, legacy, icons, badge
