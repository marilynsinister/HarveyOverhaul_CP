"""Check runtime PNG contracts: native size, outlines, alpha, indices and copies."""
from pathlib import Path
import json

from PIL import Image
from draw_native_icons import TARGETS, INK
from validate_event_coords import strip_jsonc

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK.parent
ART = PACK / 'art/native-16'
LAYOUTS = {
    'medicalItems.png': (9, 1, 9), 'arendItems.png': (3, 1, 3),
    'herbalItems.png': (8, 1, 8), 'injury-book.png': (1, 1, 1),
    'stress-handbook.png': (1, 1, 1), 'harveyBuffIcons.png': (16, 11, 166),
    'stressIcons.png': (7, 3, 21), 'injuryIcon.png': (4, 3, 12),
    'mishapBuffIcons.png': (6, 1, 6),
}


def read(path):
    return json.loads(strip_jsonc(path.read_text(encoding='utf-8-sig')), strict=False)


def tile(sheet, index):
    x, y = index % (sheet.width//16)*16, index // (sheet.width//16)*16
    return sheet.crop((x, y, x+16, y+16))


def main():
    count = 0
    for name, (columns, rows, used) in LAYOUTS.items():
        source = ART / 'exports' / name
        with Image.open(source) as image:
            assert image.mode == 'RGBA', name
            assert image.size == (columns*16, rows*16), (name, image.size)
            assert set(image.getchannel('A').get_flattened_data()) == {0, 255}, name
            assert len(set(image.get_flattened_data())) <= 65, name
            seen = set()
            for index in range(columns*rows):
                icon = tile(image, index)
                if index >= used:
                    assert icon.getbbox() is None, (name, 'reserved cell', index)
                    continue
                assert icon.getbbox(), (name, 'empty cell', index)
                if name == 'harveyBuffIcons.png':
                    assert icon.tobytes() not in seen, (name, 'duplicate', index)
                    seen.add(icon.tobytes())
                if rows == 1 and name != 'mishapBuffIcons.png':
                    x0, y0, x1, y1 = icon.getbbox()
                    assert x0 >= 1 and y0 >= 1 and x1 <= 15 and y1 <= 15, (name, index, icon.getbbox())
                for y in range(16):
                    for x in range(16):
                        pixel = icon.getpixel((x, y))
                        if pixel[3] and any(
                            not (0 <= nx < 16 and 0 <= ny < 16) or not icon.getpixel((nx, ny))[3]
                            for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
                        ):
                            assert pixel == INK, (name, index, 'outline', x, y, pixel)
                count += 1
        for relative in TARGETS[name]:
            assert (ROOT / relative).read_bytes() == source.read_bytes(), relative

    mapping = read(PACK / 'assets/Tilesheets/harveyBuffIcons.json')
    assert len(mapping) == 166 and set(mapping.values()) == set(range(166))
    assert read(ART / 'exports/harveyBuffIcons.json') == mapping
    assert read(PACK / 'art/buffs-stardew/exports/harveyBuffIcons.json') == mapping
    original = read(PACK / 'art/buffs-stardew/originals/harveyBuffIcons.json')
    assert all(mapping[key] == index for key, index in original.items()), 'Original buff indices changed'
    found = set()
    for path in (PACK / 'assets/Code').glob('*.json'):
        for change in read(path).get('Changes', []):
            if change.get('Target') != 'Data/Buffs':
                continue
            for key, entry in change.get('Entries', {}).items():
                if isinstance(entry, dict) and entry.get('IconTexture') == 'Mods/{{ModId}}/HarveyBuffIcons':
                    assert mapping[key] == entry['IconSpriteIndex'], (path.name, key)
                    found.add(key)
    assert found == set(mapping), 'Runtime buff set differs from atlas map'

    for name in ('ui', 'handbook'):
        metadata = read(ROOT / f'HarveyStressMeter/assets/sprites/{name}.json')
        sprite = metadata['Sprites']['handbook']
        assert (sprite['X'], sprite['Y'], sprite['Width'], sprite['Height']) == (0, 0, 16, 16)
    core = (ROOT / 'HarveyOverhaulCore/UI/HarveyPanelIcons.cs').read_text(encoding='utf-8')
    assert 'new Sprite(book, new Rectangle(0, 0, 16, 16))' in core
    print(f'Native icons: {count} cells; 9 sheets; binary alpha; dark contours; runtime copies and 166 buff indices OK.')


if __name__ == '__main__':
    main()
