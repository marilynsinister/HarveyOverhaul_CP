"""Sculpted effect sprites, painted on a native 16x16 pixel canvas.

The reference's jewel colors, selective highlights and dark lower planes are
expressed as explicit pixel clusters. No image sampling, scaling, antialiasing,
gradient filters or quantization are used to build runtime art.
"""
from PIL import Image

from native_anatomy import replacements as anatomy
from injury_debuff_icons import build as injuries


INK = (48, 30, 37, 255)
PALETTE = {
    '.': (0, 0, 0, 0), 'o': INK,
    'W': 'fff8e5', 'w': 'e4dcbe', 's': 'afa28e', 'S': '615870',
    'p': 'ffa99c', 'r': 'ef514f', 'R': 'af2749', 'd': '601e42',
    'l': 'c9f68b', 'g': '72c94d', 'G': '318a47', 'D': '22563f',
    'H': 'ffd594', 'h': 'e9a660', 'b': 'a5643e', 'B': '63383a',
    'y': 'fff1a1', 'a': 'ffc44f', 'A': 'cf7e30',
    'i': 'd7ffff', 'I': '7ee4ec', 'j': '368fce', 'J': '344584',
    'v': 'd9b4ff', 'V': '9d6bdb', 'n': '65449c', 'N': '353050',
    'c': 'ffe0b6', 'k': 'f6be8b', 'K': 'd68e69', 't': 'a95356',
    'F': 'f4ffff', 'f': 'c3dde3', 'e': '839eb5',
    'q': '49c6ac', 'Q': '267785',
}
PALETTE = {key: tuple(bytes.fromhex(value)) + (255,) if isinstance(value, str) else value
           for key, value in PALETTE.items()}


def seal(image):
    """Keep the existing engine's opaque, one-pixel silhouette contract."""
    source = image.copy()
    for y in range(16):
        for x in range(16):
            if source.getpixel((x, y))[3] and any(
                not (0 <= xx < 16 and 0 <= yy < 16) or not source.getpixel((xx, yy))[3]
                for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
            ):
                image.putpixel((x, y), INK)
    return image


def tile(source):
    """Every character is a native pixel; short grids are only padded."""
    rows = source.strip().split('/')
    width = max(map(len, rows))
    assert len(rows) <= 16 and width <= 16, (len(rows), width, rows)
    x0, y0 = (16-width)//2, (16-len(rows))//2
    image = Image.new('RGBA', (16, 16))
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            image.putpixel((x+x0, y+y0), PALETTE[key])
    return seal(image)


def recolor(image, mapping):
    table = {PALETTE[a]: PALETTE[b] for a, b in mapping.items()}
    result = image.copy()
    result.putdata([table.get(pixel, pixel) for pixel in image.get_flattened_data()])
    return result


def paint(image, marks):
    result = image.copy()
    for x, y, key in marks:
        if result.getpixel((x, y))[3] and result.getpixel((x, y)) != INK:
            result.putpixel((x, y), PALETTE[key])
    return result


BADGES = {
    'care': '..o../.ogo./ogWgo/.ogo./..o..',
    'pain': '..o../.oro./orpro/.oro./..o..',
    'gold': '..o../.oyo./oyayo/.oAo./..o..',
    'leaf': '..ooo/.olGo/olGGo/oGGo./.oo..',
    'drop': '..o../.oIo./oIiIo/oIjIo/.ooo.',
    'rest': 'ooooo/oiiio/ooioo/oiooo/oiiio',
    'heart': 'oo.oo/orpro/orRro/.oRo./..o..',
    'down': '.ooo./.oro./orrro/.oRo./..o..',
    'up': '..o../.ogo./ogWgo/.ogo./.ooo.',
    'ban': '.ooo./orRro/oRoRo/orRro/.ooo.',
    'clock': '.ooo./oWWwo/oWowo/owowo/.ooo.',
    'alert': '.ooo./.oyo./.oAo./.ooo./.oAo.',
}


def badge(base, kind):
    rows = BADGES[kind].split('/')
    # Choose the quiet corner; central material and silhouette take priority.
    candidates = [(10, 10), (10, 1), (1, 10), (1, 1)]
    x0, y0 = min(candidates, key=lambda pos: sum(
        (2 if base.getpixel((x+pos[0], y+pos[1])) != INK else 1)
        for y, row in enumerate(rows) for x, key in enumerate(row)
        if key != '.' and base.getpixel((x+pos[0], y+pos[1]))[3]))
    result = base.copy()
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            if key != '.':
                result.putpixel((x+x0, y+y0), PALETTE[key])
    return seal(result)


# Hand-authored light planes, curved specular clusters, reflected rim colors.
# A consistent top-left light is shared across glass, enamel, fabric and metal.
SOURCES = {
    'cross':
        '.....oooo...../....olllGo..../....olggGo..../....olggGo..../.oooolggGoooo./ollllggggggGGo/olggggggggGGDo/oggggggggGGDDo/.ooooGgGDoooo./....ogGGDo..../....ogGGDo..../....oGGDDo..../.....oooo.....',
    'heart':
        '..ooo...ooo.../.opppo.oprRo../opWWprorrrRRo./opWprrrrrrRRo./opprrrrrrrRRo./oprrrrrrrRRRo./.orrrrrrRRRo../..orrrrRRRo.../...orrRRRo..../....oRRo....../.....oo.......',
    'leaf':
        '.........oooo./.......oollGo./.....oolllgGo./....ollllgGGo./...ollllgGGDo./..ollllgGDo.../.ollllgGDo..../.olllgGDo...../olgllgGo....../olggGDo......./.oGGDo......../.oGDo........./..oo..........',
    'shield':
        '.oooooooooooo./oFiiiiiiiiIijo/oIjjjjjjjjjJo/oIjIIjjjjjJJo/oIjIIjjjjjJJo/oIjjjjjjjjJJo/.ojjjjjjjJJo../.ojjjjjjJJJo../..ojjjjJJJo.../...ojjJJJo..../....oJJJo...../.....oJo....../......o.......',
    'iv':
        '.....oooo...../....ofFFeo..../...ooFooeoo.../..oFiFFFFfeo../..oFIiiiIfeo../..oFIiIIjfeo../..oFIiiiIfeo../..oFIIIIjfeo../..ofjjjjjee o../...ooooooo..../......oeo...../......oeo...../......oeooo.../.......ooeeo../..........oo..',
    'clipboard':
        '.....oooo...../..oooFeeeooo../.oHHhoFFobhBo./.oHWWooooWbBo./.oHWWWWWWwbBo./.oHWjeeeWwbBo./.oHWWWWWWwbBo./.oHWjeeeWwbBo./.oHWWWWWWwbBo./.oHWjeeWWwbBo./.oHWWWWWWwbBo./.oHwwwwwwsbBo./.ohbbbbbbbBBo./..oooooooooo..',
    'capsule':
        '..........ooo./.........oWWwo/........oFWWwo/.......oFWWwso/......oFWWwso./.....oFWWwso../....opFFwso.../...opprooo..../..opprRo....../.opprRo......./opprRRo......./oprRRo......../.oRRo........./..oo..........',
    'dropper':
        '..........ooo./.........opRRo/........oprrRo/........orRRRo/.......ooRRRo./......oFIooo../.....oFIjo..../....oFIjo...../...oFIjo....../..oFIjo......./.oFIjo......../.oIjo........./..oo..o......./.....oIo....../.....oJo....../......o.......',
    'vial':
        '....oooooo..../...oFffffeo.../...oeeeeeeo.../....oFooFo..../...oFiiiiIo.../...oFIiIIjo.../...oFIIIIjo.../...oFIqQQjo.../...oFIqqQjo.../...oFIqqQjo.../...oFIqqQjo.../...ofIQQQjo.../....oJJJJo..../.....oooo.....',
    'tea':
        '....oo..oo..../...oFo.oFo..../....oo..oo..../............../..oooooooooo../.oWAAggGAAwwo./oFWWoooooWWwsoo/oFWWWWWWWwwsoWo/oFWWgWWWWwwso.o/oFWgGgWWWwwsoWo/.oWWgWWWWwsooo/..oWWWWWwso.../...oswwsso..../....ooooo.....',
    'eye':
        '.....oooo...../...ooFFFFoo.../..oFWWWWWWwo../.oFWWojJoWWwo./oFWWoIijoWWwso/oFWWoIoooWWwso/.owWoJjooWwso./..osWooowwso../...oossssoo.../.....oooo.....',
    'siren':
        '.o..........o./oyo..oooo..oyo/.o..opprRo..o./...opWWrrRo.../...opWrrrRo.../..opprrrrRRo../..oprrrrrRRo../..orrrrrRRRo../..orrrrRRRRo../.ooRRRRRRRRoo./oFfffeeeeeSSSo/oeeeeeeeeSSSSo/.oooooooooooo.',
    'syringe':
        '...........o../..........oFo./.........oFFo./........ooFo../.......oFIIoo./......oFIijo../.....oFIIjo.../....oFIijo..../...ooFIjo...../..oWWooo....../.oWWo........./..oWo........./...o..........',
    'glasses':
        '.ooooo..ooooo./oFiIjeooFiIjeo/oFIIJJo oFIIJJo/oIjjJJo oIjjJJo/.oJJJo..oJJJo./..ooo....ooo..',
    'rx':
        '.ooooooooooo../oFWWWWWWWwwso/oFWjWWWWWwwso/oFWjjWWWWwwso/oFWjWjWWWwwso/oFWjjWWWWwwso/oFWjWjWWWwwso/oFWWWWWWWwwso/oFWeeeeWWwwso/oFWWWWWWWwwso/oFWeeeeWWwwso/oFWWWWWWWwwso/owwwwwwwwwsso/.ooooooooooo..',
    'bed':
        '............../.oo.........../oHho........../oHhooo......../oHhoWWooooooo./oHhWWwIIIIijJo/oHhwwsIIIIjjJo/oHhhhhhhhhbbBo/oHbbbbbbbbBBBo/oHboooooooobBo/oBBo.......oBo/.oo.........o.',
    'umbrella':
        '......oo....../....ooIIoo..../...oFIIjjJo.../..oFIIjjJJJo../.oFIIjjJJJJJo/oFIjjjJJJJJJJo/ooojjoooJJJooo/...oo...ooo.../......obo...../......obo...../......obo...../....o.obBo..../....ohbBo...../.....ooo......',
    'feather':
        '..........ooo./.........oFWwo/........oFWwso/.......oFWWso./......oFWwso../.....oFWwso.../....oFWwso..../...oFWwso...../..oFWwso....../.oFWwso......./.owwso......../..oso........./..oo..........',
    'stethoscope':
        '..oo......oo../.oFeo....oFeo./.oQoo....ooQo./.oQo......oQo./.oQo......oQo./..oQo....oQo../...oQQooQQo.../....ooQQoo..../......oQo...../......oQo...../.....ooQoo..../....oFfQeeo.../....oFffSSo.../.....oSSSo..../......ooo.....',
    'house':
        '......oo....../.....oHho...../....oHHhbo..../...oHHhhbBo.../..oHHhhbbBBo../.oHHhhhbbBBBo/ooHHhhhbbBBBoo/.ooooHHoooooo./.oWWWwwwwsso../.oWjjWoBbsso../.oWIjWoBbsso../.oWWWWoBbsso../.owwwwoBBsso../..ooooooooo...',
    'clinic':
        '......oo....../.....oppo...../....opprRo..../...opprrRRo.../..opprrrRRRo../.opprrrrRRRRo/oorrrrrRRRRRoo/.ooooWWoooooo./.oWWWWrWWsso../.oWWWrrrWsso../.oWWWWrWWsso../.oWjWWoBBsso../.owIwwobBsso../..ooooooooo...',
    'pillow':
        '.oo........oo./oFWooooooooWwo/oFWWWWWWWWwwso/.oFWWWWWWwwso./.oFWWWWWWwwso./.oFWWWWWWwwso./oFWWWWWWWWwwso/oWwsssssssssso/.oo........oo.',
    'clock':
        '.....oooo...../...ooHyyAoo.../..oHyWWWwaAo../.oHyWWWWwwaAo./.oHWWhWWwwsAo/oHyWWhWWwwwAAo/oHyWWhbbwwwAAo/oAyWWWWbbwwAAo/oAyWWWWWWwwAAo/.oAyWWWWwwAAo./.oAAwwwwwAAAo./..oAAAAAA AAo../...ooAAAAoo.../.....oooo.....',
    'snow':
        '......oo....../...o.oIjo.o.../..oIooiJooIo../...oIIijIIo.../....oIiIjo..../.oo.oIiIjo.oo./oIIIIIFFIjjJJo/oIjIIIIIIjjJJo/.oo.oIiIjo.oo./....oIiIjo..../...oIIijIIo.../..oJooIJo oJo./...o.oJjo.o.../......oo......',
    'scarf':
        '.oooooooooooo./oWppppprrrrRRo/orrrrrrrrrRRRo/oWWWWwwwwwRRRo/.oooooorRoooo./.......orRRo../.......orRRo../.......orRRo../.......orRRo../.......oRRRo../.......oRRRo../.......orRRo../........ooo...',
    'thermometer':
        '.....oooo...../....oFWWwo..../....oFrrwo..../....oFrrwo..../....oFrrwo..../....oFrrwo..../....oFrrwo..../....oFrrwo..../...oWprrRwo.../..oWprrrRRwo../..opprrrRRRo../..orrrrRRRRo../...oRRRRRRo.../....oooooo....',
    'battery':
        '.ooooooooooo../oFffffeeeeSSo./oFoooNNNNNoSSoo/oFoNNNNNNNoSSSo/oForrNNNNNoSSSo/oForRNNNNNoSSSo/oFoNNNNNNNoSSSo/oFoooNNNNNoSSoo/oeeeeeeeeSSSo./.ooooooooooo..',
    'moon':
        '.....ooo....../...ooHyo....../..oHyyAo....../.oHyyAo......./.oHyao......../oHyaa o......./oHyaa o......./oHyaaAo......./oHyaAAAo....../.oyaaAAAoooo../.oaaAAAAAAAo../..oAAAAAAA o../...ooAAAAoo.../.....oooo.....',
    'cloud':
        '.....oooo...../....oFffeo..../...oFffffeo.../.oooFffffeooo./oFffffffeeeeeo/oFfffffeeeeeSo/oFffffeeeeeSSo/.oeeeeeeeeSSo./..oooooooooo..',
    'plate':
        '.o..........o./oFo.........oFo/oFo..oooo...oFo/oFo.oFWWwo..oFo/oFooFWWWwso.oFo/.ooFWWwwwwsooo./.oFWWwsswwwso../.oFWWwwwwwwso../..oFWWwwwwso.../...oossssoo..../.....oooo......',
    'hoe':
        '.........oooo./........oFfeo./.......oFfeeSo/.......oeeeSSo/........oSoBo./........oBbo../.......oHbo.../......oHbo..../.....oHbo...../....oHbo....../...oHbo......./..oHbo......../.oHbo........./..oo..........',
    'wave':
        '......oooo..../....ooFIIjo.../...oFIIjjJJo../..oFIIjooooo../..oFIjJo....../.oFIIjJo....../.oFIIjjJo...oo/oFIIjjjjJoooIo/oFIIjjjjjjIIJo/oFIjjjjjjjjJJo/oIjjjjjjjjJJJo/.oJJJJJJJJJJo./..oooooooooo..',
    'brain':
        '....ooo.ooo.../..oopppoVvno../.opWWppoVVvno./opWpppopVVVnno/opppopppoVnVno/opppoppopVnVno/opppooppoVnVno/opppppopoVnVno/.oppppopVVnno./..oRRRoVnno.../...oo..ooo....',
    'ghost':
        '.....oooo...../...oovvvVoo.../..ovWWvvVVno../..ovWvvvVVno../.ovvvoovooVno./.ovvvoovooVno./.ovvvvvvVVVno./.ovvvvooVVVno./.ovvvvooVVnno./.ovvvvvVVVnno./.ovvvvVVVnnno./.ovVooVnooVno./..oo..oo..oo..',
    'match':
        '..........oo../.........oNNo./........oNNNo./........oNno../.......oHoo.../......oHbo..../.....oHbo...../....oHbo....../...oHbo......./..oHbo......../.oHbo........./.oBBo........./..oo..........',
    'warning':
        '......oo....../.....opRo...../.....oprRo..../....oprrRo..../....opWWrRo.../...oprWWrRo.../...oprWWrrRo../..oprrWWrrRo../..oprrWWrrRRo./.oprrrrrrrRRo./.oprrrWWrrRRRo/oprrrrWWrrRRRo/orrrrrrrrrRRRo/.oooooooooooo.',
    'sparkle':
        '......oo....../......oyo...../.....oWyao..../.....oWyao..../....oWWyaa o../..ooWWWWyaAoo./ooWWWWWWyaaAAo/oyyyyyyyyAAAAo/.ooaaaaaAA oo./...oaaaAo...../....oyAo....../....oyAo....../.....oo.......',
    'candle':
        '......o......./.....oyo....../....oyyao...../....oyaAo...../.....oAo....../......o......./....oooooo..../...oFWWwwso.../...oFWwwsso.../...oFWwwsso.../...oFWwwsso.../...oFWwwsso.../..ooowwwssoo../.oHHhhhhbbBBo./..oooooooooo..',
    'lantern':
        '.....oooo...../....oHooBo..../....oHooBo..../.....oooo...../...ooHHhboo.../..oHHhhhhbBo../..oBFyyyyfBo../..oBFyWWyfBo../..oBFyWWafBo../..oBFyyAAfBo../..oBFaaAAfBo../..oBBbbbbBBo../...oBBBBBBo.../....oooooo....',
    'bulb':
        '.....oooo...../...ooHyyAoo.../..oHWyyyaaAo../..oHWyyyaaAo../.oHWyyyyyaaAo./.oHyyyyyyaaAo./..oyyyyyAAAo../..oayyyAAA o../...oAyAAA o.../....ofeeeo..../....ofeeeo..../.....oSSo...../......oo......',
    'bubbles':
        '..ooooooo...../.oFWWWWWwo..../oFWWWWWWwso.../oFWWWWWWwso.../.owWWWWWso..../..ooWooooooo../...oo.oFIijJo./.....oFIIijJJo/.....oFIIjjJJo/......ojjjJJo./.......ooJJo../.........oo...',
    'ice':
        '...oooooooo.../..oFiiiiiiIo../.oFIiiiiIIjJo/oFIIiiiiIIjJJo/oFIWiiiIIIjJJo/oFIWiiIIIIjJJo/oFIIIoIIIIjJJo/oFIIIoIIIIjJJo/oFIIoIoIIIjJJo/oFIIoIooIIjJJo/oFIIIIIIooJJJo/.oIjjjjjjJJo../..ooooooooo...',
    'sun':
        '......oo....../..oo..oyo.oo../..oyo.oo.oyo../...o.oooo.o.../...ooHyyAoo.../.ooHWyyyaaAoo./oyHWyyyyyaaAAo/.oHyyyyyyaaAo./..oyyyyyaAAo../...oAAAAAAo.../..o.oooooo.o../.oyo..oo..oyo./..oo..oyo..oo./......oo......',
    'gauge':
        '.....oooo...../...ooggAAoo.../..oglllAArRo../.oglooooArrRo./ogloWWWWoRRRRo/ogloWWWWWoRRRo/ogloWWWooWoRRo/ogloWWoNoWWRRo/.oGoWWNoWWWdo./..oGoWWWWWoo../...ooooooo....',
    'pause':
        '.....oooo...../...ooFFFFoo.../..oFWWWWWWwo../.oFWWWWWWWwso/oFWWogooGowwso/oFWWogooGowwso/oFWWogooGowwso/oFWWogooGowwso/.oWWogooGowso./..oWWWWwwsso../...oossssoo.../.....oooo.....',
    'dumbbell':
        '.ooo......ooo./oFfeo....oFfeo/oFfSoo..ooFfSo/oFfSSooooeFfSo/oFfSSffffeFfSo/oFfSSffffeFfSo/oFfSSooooeFfSo/oFfSoo..ooFfSo/oSSSo....oSSSo/.ooo......ooo.',
    'arrow':
        '......oo....../.....olGo...../....ollgGo..../...olllggGo.../..ollllggGGo../.olllllggGGGo./oooollgGGGoooo/....olgGDo..../....olgGDo..../....olgGDo..../....ogGGDo..../....ogGGDo..../.....oooo.....',
    'bee':
        '..ooo..ooo..../.oFIIooFIjo.../.oFIjJoIIjJo../..oIJJoIJJo.../...oooooooo.../..oHyoNoyaNNo./.oHyaoNoaaNNoo/.oyAAoNoAANNoJo/.oAAA oNAANNNoo/..oAAA oNNNo../...oooooooo...',
    'fish':
        '.......ooo..../.....ooIIJoo../.oo.oFIIjjJJo/oIjoFIIjjjJJJo/oIjoFIIojjJJJo/.oIIjIIIjjJJJo/oIjojjjjjJJJo/oJjoJJJJJJJo./.oo.ooooooo..',
    'cave':
        '......ooo...../.....oFeeo..../....oFfeSSo.../...oFfeeSSSo../..oFfeeSSSSSo./.oFfeeooSSSSSo/oFfeeooNoSSSSo/oFeeoNNNNoSSSo/ofeoNNNNNNoSSo/oeeoNNNNNNoSSo/ooooNNNNNNoooo',
    'bone':
        '..........oo../.........oWWo./.........oWWwo/........oWWwso/.......oWWwso./......oWWwso../.....oWWwso.../....oWWwso..../.oooWWwso...../oWWWWWso....../oWWWWso......./.oWWwso......./..owso......../...oo.........',
    'fracture':
        '..........oo../.........oWWo./.........oWWwo/........oWWwso/.......oWWwso./......oWWwso../......owwso.../.......oo...../.oooo........./oWWWWo......../oWWWWso......./.oWWwso......./..owso......../...oo.........',
    'ribs':
        '.....oooo...../....oFWWso..../..oo.oWso.oo../.oWWooWwooWWo./oFwwwWWwwwwWso/oWso.oWso.osso/oWso.oWso.osso/.oo..oWso..oo./.oWWooWwooWWo./oFwwwWWwwwwWso/oWso.oWso.osso/.oWsooWsoosso./..oswwWwwsso../...oooooooo...',
    'muscle':
        '..........ooo./.........oWWwo/........oWWwso/.......oWWwso./.....oopwsoo../....opprrRo.../...opWWrrRRo../..opWrorrRRo../..opprorRrRo../..oprorRorRo../...oRoRorRo.../...oWwRRRo..../..oWWwsoo...../..oWWso......./...oo.........',
    'knife':
        '...........oo./..........oFo./.........oFWo./........oFWso./.......oFWwso./......oFWwso../.....oFWwso.../....oFWwso..../....oFwso...../...ooooo....../..oHHBo...oo../.oHHBo...opRo/oHHBo....opRo/oBBo......oRo./.oo........o..',
    'microbe':
        '......oo....../..oo.olGo.oo../..oGoolGooGo../...olllllGo.../..olWWWllgGo../.olWlgGllggGo./olWllgGlllGGDo/ogllllllGlGGDo/.oglllllGlGDo./..ogggggGGDo../...oGGGGGDo.../..oGooGDooGo../..oo.oDDo.oo../......oo......',
    'shrapnel':
        '...oo.....ooo./..oFFo...oFfo./..oFfSo.oFFSo./...ofSo.oFSo../...oeo..oSo.../....o....o..../..o.....oo..../.oFSo..oFWo.../.oFFSo.oFWso../..ofSSo.oWso../...oSSo..oo.../....oo........',
    'plaster':
        '..........ooo./.........oHWWo/........oHWWso/.......oHWWso./......oHWWso../.....oHhsso.../....oHhWsso.../...oHhWsso..../..oHhWWso...../.oHWWwso....../oHWWwso......./oWWwso......../.owso........./..oo..........',
    'crutch':
        '..ooooooooo.../.oHHhhhhbbBo../..ooooooooo.../...oHo.oBo..../...oHo.oBo..../...oHo.oBo..../...oHHhbBo..../....oHhBo...../....oHhBo...../....oHhBo...../....oHhBo...../....oHhBo...../....oeeSo...../.....ooo......',
    'lungs':
        '.....oooo...../.....oWwo...../.....oWwo...../...oooWwooo.../..oppoWWorr o./.opWWoWWorrRo/opWWoWwoWorRRo/opWpoWo.oWrRRo/opppoWo.oWrRRo/oprroWo.oWRRRo/.oRRo...oRRRo./..oo.....ooo..',
    'pickaxe':
        '..oooo......../.oFfff o....../..oFfeeoo...../...ooeeSSoo.../.....oFeSSSo../.....oHbSSSo../....oHboSSo.../...oHbo.oo..../..oHbo......../.oHbo........./oHbo........../oBBo........../.oo...........',
    'insomnia':
        '...ooo......../..oHyo......../.oHyao......../oHyaa o......./oHyaaAo......./oHyaAAAo....../.oaaAAAooo..../..oAAAAAAoo.../...ooooooooo../.....oFWWWWwo./....oFWojJWWwo/...oFWoIooWWwso/....owWoJjWwso/.....oossssoo./.......oooo...',
    'crowd':
        '..ooo....ooo../.okcKo..okcKo./.okkKo..okkKo./..oKo....oKo../.oIjJo..oVnNo/oIIjJJoVVnNNNo/oIJoooooonNNNo/.o okccKKo oo./...okccKKo..../....oKKKo...../...oIIjJJo..../..oIIIjjJJo.../..oIIjjJJJo.../...ooooooo....',
}


def symbols():
    # Spaces in a few diagonal grids are transparent native pixels.
    return {name: tile(source.replace(' ', '.')) for name, source in SOURCES.items()}


def build(index):
    art = symbols()
    anatomical, _, body, _ = anatomy(PALETTE)
    art['microbe'] = paint(art['microbe'], [(6, 7, 'G'), (7, 7, 'D'), (6, 8, 'G'),
                                           (10, 9, 'D'), (10, 10, 'G')])
    symbol_overrides = {
        'whole_bone': art['bone'], 'fracture': art['fracture'],
        'ribs': paint(art['ribs'], [(11, 9, 'V'), (12, 9, 'n'), (11, 10, 'n')]),
        'muscle': art['muscle'],
        'muscle_healing': paint(art['muscle'], [(5, 8, 'W'), (6, 8, 'w'), (7, 9, 'W'), (8, 9, 'w')]),
        'weak_muscle': recolor(art['muscle'], {'p': 'v', 'r': 'V', 'R': 'n', 'W': 'f'}),
        'cut': art['knife'], 'infection': art['microbe'], 'shrapnel': art['shrapnel'],
        'plaster': art['plaster'], 'crutch': art['crutch'], 'lungs': art['lungs'],
        'dirty': paint(art['plaster'], [(10, 4, 'b'), (9, 5, 'B'), (6, 9, 'b'), (5, 10, 'B')]),
        'neglect': recolor(art['plaster'], {'W': 's', 'w': 'S', 'H': 'b', 'h': 'B'}),
    }
    injury, legacy, injury_art = injuries(PALETTE, badge, symbol_overrides)
    result = {key: image.copy() for key, image in anatomical.items()}
    result.update(injury)

    def use(key, subject, mark=None, colors=None):
        image = art[subject].copy()
        if colors:
            image = recolor(image, colors)
        result[key] = badge(image, mark) if mark else image

    # Primary medical treatment objects.
    direct = {
        'buffHarveyTreatment': ('cross', None),
        'buffHarveyIntensiveCare': ('iv', None),
        'HarveyMod_BadlyHurt_OutpatientCare': ('clipboard', 'heart'),
        'buffHarveyHealing': ('leaf', 'care'),
        'buffHarveyRecovery': ('heart', 'leaf'),
        'buffHarveyProtection': ('shield', 'care'),
        'buffAntibioticsTreatment': ('capsule', None),
        'buffHarveyDropper': ('dropper', None),
        'buffTeracitin': ('vial', None),
        'buffCalmTeaEffect': ('tea', 'leaf'),
        'buffStrictSupervision': ('eye', None),
        'buffEmergencySupervision': ('siren', None),
        'buffConstantSupervision': ('eye', 'clock'),
        'buffForcedSedation': ('syringe', 'rest'),
        'buffHarveyCare': ('glasses', 'heart'),
        'buffFarmerExhausted': ('battery', 'rest'),
        'buffSleepy': ('pillow', 'rest'),
        'buffTooCold': ('thermometer', None),
        'buffCold': ('scarf', None),
        'HarveyMod_Cold_Acute': ('thermometer', 'pain'),
        'HarveyMod_Cold_Recovery': ('scarf', 'leaf'),
        'HarveyMod_Prescription_Rest': ('rx', 'rest'),
        'HarveyMod_Prescription_NoMine': ('rx', 'ban'),
        'HarveyMod_Prescription_KeepDry': ('umbrella', None),
        'HarveyMod_Prescription_LightWork': ('feather', None),
        'HarveyMod_Prescription_Checkup': ('stethoscope', None),
        'HarveyMod_Hospitalized': ('bed', 'care'),
        'HarveyMod_DoctorVisitNeeded': ('clinic', 'alert'),
        'buffHarveyRehab': ('dumbbell', 'leaf'),
        'HarveyMod_SelfCare': ('house', 'heart'),
        'HarveyMod_WarmTea': ('tea', None),
        'buffStressImmunity': ('shield', 'gold'),
        'buffStressRecovery': ('arrow', None),
        'buffStressRecoveryAdvanced': ('arrow', 'gold'),
        'buffStressRecoveryGlow': ('sparkle', None),
        'buffRestingAtHome': ('house', 'rest'),
        'buffCalmingAtHospitalWithHarvey': ('clinic', 'heart'),
        'buffOverworkBreak': ('pause', None),
        'buffLightAndSafe': ('bulb', None),
        'buffDimLight': ('candle', None),
        'buffHarveyLantern': ('lantern', None),
        'buffDarknessOvercome': ('sun', 'leaf'),
        'buffStressLoadTier': ('gauge', None),
        'HarveyMod_MineForbidden': ('pickaxe', 'ban'),
        'HarveyMod_MineRestricted': ('pickaxe', 'alert'),
        'HarveyMod_Resilience': ('heart', 'gold'),
        'HarveyMod_BeeSting': ('bee', None),
        'HarveyMod_Sunstroke': ('sun', 'drop'),
        'HarveyMod_Frostbite': ('snow', 'pain'),
    }
    for key, (subject, mark) in direct.items():
        use(key, subject, mark)
    result['buffTooCold'] = recolor(result['buffTooCold'], {'p': 'i', 'r': 'I', 'R': 'j'})
    # The care/status versions keep the same symbol as the corresponding injury.
    result['HarveyMod_CleanBandage'] = injury_art['gauze'].copy()
    result['buffPostSurgicalCare'] = badge(injury_art['stitches'], 'heart')
    result['buffTraumaHealing'] = badge(art['heart'], 'care')
    result['HarveyMod_TornMuscles_Rehab'] = badge(art['dumbbell'], 'gold')
    result['HarveyMod_BadlyHurt_Acute'] = badge(art['heart'], 'pain')
    result['HarveyMod_BadlyHurt_Healing'] = badge(injury_art['stitches'], 'care')
    result['HarveyMod_BadlyHurt_Recovery'] = badge(art['heart'], 'up')

    # Stress icons use distinct object silhouettes, not a collection of faces.
    actors = people()
    stress = {
        'Tired': art['eye'], 'Lonely': actors['Lonely'],
        'Thunder': badge(art['cloud'], 'gold'), 'Hunger': art['plate'],
        'Overwork': badge(art['hoe'], 'drop'), 'NoSleep': art['insomnia'],
        'TooCold': art['snow'], 'Darkness': art['ghost'], 'Social': art['bubbles'],
        'BadDream': badge(art['moon'], 'pain'), 'AnxietyWave': art['wave'],
        'Breakdown': art['heart'], 'Collapse': actors['Collapse'], 'Despair': art['cloud'],
        'Panic': art['heart'], 'Critical': art['warning'], 'Exhaustion': art['battery'],
        'PhysicalDepletion': badge(recolor(art['battery'], {'r': 'a', 'R': 'A'}), 'down'),
        'NightTerror': art['ghost'],
        'Burnout': art['match'], 'MentalBreakdown': art['brain'],
        'PanicCollapse': badge(art['heart'], 'down'), 'DespairCollapse': badge(art['heart'], 'drop'),
        'PanicBreakdown': badge(art['warning'], 'pain'),
        'ParanoidCollapse': badge(art['ghost'], 'down'),
        'CriticalExhaustion': badge(recolor(art['battery'], {'r': 'N', 'R': 'N'}), 'alert'),
        'Numbness': recolor(injury_art['rash'], {'r': 'I', 'R': 'j', 'k': 'f', 'K': 'e', 'c': 'F'}),
        'ShadowParanoia': actors['ShadowParanoia'], 'FreezeResponse': art['ice'],
        'Isolation': actors['Isolation'], 'Criticism': actors['Criticism'],
        'MentalFatigue': recolor(art['brain'], {'p': 'v', 'r': 'V', 'R': 'n'}),
    }
    stress['Tired'] = paint(art['eye'], [(x, y, 'K') for y in range(5, 8) for x in range(2, 14)])
    stress['Breakdown'] = cracked(recolor(art['heart'], {'p': 'f', 'r': 'e', 'R': 'S'}))
    stress['Panic'] = lightning(art['heart'])
    stress['Despair'] = rainy(art['cloud'])
    stress['Thunder'] = lightning(art['cloud'])
    stress['MentalBreakdown'] = cracked(art['brain'])
    stress['DespairCollapse'] = badge(stress['Breakdown'], 'drop')
    stress['Darkness'] = recolor(art['ghost'], {'W': 'n', 'v': 'N', 'V': 'n', 'n': 'N'})
    # Small eyes remain readable in the dark silhouette.
    stress['Darkness'] = paint(stress['Darkness'], [(5, 6, 'y'), (6, 6, 'a'), (10, 6, 'y')])
    for suffix, image in stress.items():
        assert image is not None, suffix
        key = 'buffStress' + suffix
        if key in index:
            result[key] = image.copy()
        cure = 'buffHarveyTreatment' + suffix
        if cure in index:
            result[cure] = badge(image, 'care')
    result['buffSleepDeprivation'] = badge(stress['Tired'], 'clock')
    result['buffDarknessLevel1'] = badge(stress['Darkness'], 'alert')
    result['buffDarknessLevel2'] = badge(stress['Darkness'], 'pain')
    result['buffDarknessLevel3'] = badge(recolor(stress['Darkness'], {'N': 'd', 'n': 'R'}), 'ban')
    result['buffStressClearMind'] = badge(recolor(art['brain'], {'p': 'i', 'r': 'I', 'R': 'j', 'v': 'l', 'V': 'g', 'n': 'G'}), 'gold')
    result['buffStressFireMemory'] = tile('......o......./.....oro....../.....opRo...../....oparRo..../....opyarRo.../...opyyyaRo.../..opayyyyRRo../..opayyWWRRo../.opayyWWyaRRo./.opayyWWyaRRo./.orayyyyAA RRo/..oAAAAAA RRo./...oRRRRRRo.../....oooooo....'.replace(' ', '.'))
    missing = set(index) - set(result)
    assert not missing, sorted(missing)
    result = {key: result[key] for key in index}
    seen = {}
    for key, image in result.items():
        previous = seen.setdefault(image.tobytes(), key)
        assert previous == key, ('identical effect art', previous, key)
    handbook = [result['buffStressOverwork'], art['crowd'],
                result['buffStressThunder'], art['moon'], art['cave'], result['buffStressLonely'],
                art['rx'], art['vial'], cracked(art['ice']), badge(art['clipboard'], 'alert'),
                badge(art['rx'], 'gold'), result['buffStressTooCold'], result['buffStressNoSleep'],
                result['buffStressNumbness'], result['buffStressPanic'], result['buffHarveyCare'],
                art['tea'], art['fish'], art['candle'], badge(body['hand'], 'heart'),
                result['buffStressShadowParanoia']]
    mishaps = [result[key] for key in ('HarveyMod_Resilience', 'HarveyMod_Splinter',
               'HarveyMod_BeeSting', 'HarveyMod_Sunstroke', 'HarveyMod_Frostbite', 'HarveyMod_WetStitches')]
    return result, handbook, legacy, mishaps


def cracked(base):
    return paint(base, [(7, 3, 'o'), (7, 4, 'o'), (8, 5, 'o'), (8, 6, 'o'),
                        (7, 7, 'o'), (6, 8, 'o'), (7, 9, 'o'), (7, 10, 'o')])


def lightning(base):
    # The bolt is painted in full as a secondary object, in native pixels.
    result = base.copy()
    rows = ['...oo', '..oWo', '.oWyo', 'oWyoo', 'oWWo.', '.oWo.', '.oWo.', '.oo..']
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            if key != '.':
                result.putpixel((x+6, y+6), PALETTE[key])
    return seal(result)


def rainy(base):
    result = base.copy()
    for x in (3, 7, 11):
        for dx, dy, key in ((0, 0, 'o'), (0, 1, 'I'), (-1, 2, 'j'), (0, 2, 'o'), (-1, 3, 'o')):
            result.putpixel((x+dx, 11+dy), PALETTE[key])
    return seal(result)


def people():
    lonely = tile('.....oooo...../....obhhBo..../....okckKo..../....okkKKo..../.....oKK o..../....ooNooo..../...oVnNNNNo.../..oVVnNNNNNo../..oVVoNNNoNo../...oVooNoNo.../....oNoNNo..../...ooNNoNo..../..oSSSoSSSo.../...ooo.ooo....'.replace(' ', '.'))
    collapse = tile('..ooo........./.oIijo......../..oIjJo......./...oIjJoo...../..ooIjJJJo..../.oIjJoJJJoooo./..oJo.oJJokcKo/...o...ooWkkKo/.........oKKo./..........oo..')
    pointing = tile('...oooo......./..okccKo....../..okccKoooooo./.ookcckkcckkKo/okckccKKKKKKKo/okcckkKoooooo./.okcckkkKo..../.okckkkKKo..../..okkkKKKo..../...oKKKKKo..../....ooooo.....')
    shadow = tile('.....oooo...../....oVVnNo..../...oVvVnNNo.../..oVvNNNNNNo../..oVNyoNyNNo../..oVNNNNNNNo../...oVNNNNNo.../...ooNNNNoo.../..oVnNNNNNNo../.oVnNNNNNNNNo./.oVnNNNNNNNNo./.oVnNNNNNNNNo./..oooooooooo..')
    isolation = tile('.....oooo...../...ooffeeoo.../..oFFoNoSSSo../.oFFoNNNoSSSo./.oFoNNNNNoSSo/oFoNNokKoNoSSo/oFoNokcKKoNSSo/oFoNNokkNoNSSo/oFoNoVVNNoNSSo/.oFoVnNNNoSSo./.oFooVNNNoSSo./..oFoooooSSo../...ooffSSoo.../.....oooo.....')
    return {'Lonely': lonely, 'Collapse': collapse, 'Criticism': pointing,
            'ShadowParanoia': shadow, 'Isolation': isolation}
