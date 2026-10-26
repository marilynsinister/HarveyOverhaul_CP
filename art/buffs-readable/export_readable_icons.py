"""Pack image_gen artwork into existing 16px cells; never change HUD layout or indices."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ART = Path(__file__).resolve().parent
CP = ART.parents[1]
ROOT = CP.parent
EXPORTS = CP / 'art/buffs-stardew/exports'
MAPPING = json.loads((CP / 'assets/Tilesheets/harveyBuffIcons.json').read_text(encoding='utf-8'))
IDS = [
    'HarveyMod_WetBandage', 'HarveyMod_InfectedWound_Treatment',
    'buffStressNoSleep', 'buffStressThunder', 'buffDarknessOvercome',
    'buffStressSocial', 'buffRestingAtHome', 'buffStressClearMind',
    'buffStressTired', 'buffStressLonely', 'buffStressHunger', 'buffStressOverwork',
    'buffStressTooCold', 'buffStressDarkness', 'buffStressLoadTier', 'buffStressFireMemory',
]
LABELS = [
    'Мокрая повязка', 'Лечение раны', 'Недосып', 'Пугающая гроза',
    'Преодоление', 'Социальная тревожность', 'Отдых дома', 'Ясная голова',
    'Усталость', 'Одиночество', 'Голод', 'Переутомление',
    'Переохлаждение', 'Боязнь темноты', 'Напряжение', 'Запах дыма',
]


def tile(atlas, index):
    columns = atlas.width // 16
    x, y = index % columns * 16, index // columns * 16
    return atlas.crop((x, y, x + 16, y + 16))


def paste(atlas, index, icon):
    columns = atlas.width // 16
    atlas.paste(icon, (index % columns * 16, index // columns * 16))


def extract(source, index):
    x0, y0 = index % 4 * source.width // 4, index // 4 * source.height // 4
    x1, y1 = (index % 4 + 1) * source.width // 4, (index // 4 + 1) * source.height // 4
    icon = source.crop((x0, y0, x1, y1))
    alpha = icon.getchannel('A').point(lambda value: 255 if value >= 192 else 0)
    bounds = alpha.getbbox()
    assert bounds, f'Empty generated cell {index}'
    icon = icon.crop(bounds)
    scale = min(14 / icon.width, 14 / icon.height)
    size = (max(1, round(icon.width * scale)), max(1, round(icon.height * scale)))
    icon = icon.resize(size, Image.Resampling.NEAREST)
    # Pure mechanical export: nearest sampling, binary transparency, no redrawing.
    icon.putalpha(icon.getchannel('A').point(lambda value: 255 if value >= 128 else 0))
    result = Image.new('RGBA', (16, 16))
    result.paste(icon, ((16 - size[0]) // 2, (16 - size[1]) // 2))
    return result


def main():
    native_builder = CP / 'scripts/draw_native_icons.py'
    if native_builder.is_file():
        import subprocess
        import sys
        subprocess.run([sys.executable, str(native_builder), '--install'], check=True)
        return
    source = Image.open(ART / 'generated/common-statuses.png').convert('RGBA')
    assert source.width == source.height, 'Expected a regular four by four generated sheet'
    atlas = Image.open(EXPORTS / 'harveyBuffIcons.png').convert('RGBA')
    before = atlas.copy()
    icons = [extract(source, i) for i in range(len(IDS))]
    assert len({icon.tobytes() for icon in icons}) == len(icons), 'Duplicate replacements'
    for buff_id, icon in zip(IDS, icons):
        paste(atlas, MAPPING[buff_id], icon)
    changed = {MAPPING[buff_id] for buff_id in IDS}
    for i in range(176):
        icon = tile(atlas, i)
        alpha = icon.getchannel('A')
        assert set(alpha.tobytes()) <= {0, 255}, f'Partial alpha in cell {i}'
        if i < 166:
            assert alpha.getbbox(), f'Empty active cell {i}'
            assert not alpha.crop((0, 0, 16, 1)).getbbox()
            assert not alpha.crop((0, 15, 16, 16)).getbbox()
            assert not alpha.crop((0, 0, 1, 16)).getbbox()
            assert not alpha.crop((15, 0, 16, 16)).getbbox()
        else:
            assert not alpha.getbbox(), f'Reserved cell {i} must remain empty'
        if i not in changed:
            assert icon.tobytes() == tile(before, i).tobytes(), f'Unexpected change in cell {i}'
    for path in (EXPORTS / 'harveyBuffIcons.png', CP / 'assets/Tilesheets/harveyBuffIcons.png'):
        atlas.save(path)

    # Matching handbook entries consume the same 16px motifs, with unchanged cell coordinates.
    stress_path = EXPORTS / 'stressIcons.png'
    stress = Image.open(stress_path).convert('RGBA')
    for handbook_cell, replacement in {0: 11, 2: 3, 5: 9, 11: 12, 12: 2, 20: 13}.items():
        paste(stress, handbook_cell, icons[replacement])
    for path in (stress_path, CP / 'assets/Tilesheets/stressIcon.png',
                 ROOT / 'HarveyStressMeter/assets/sprites/stressIcons.png'):
        stress.save(path)

    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
    preview = Image.new('RGB', (800, 530), '#20202a')
    draw = ImageDraw.Draw(preview)
    draw.text((18, 12), '16×16 — новые силуэты в ванильном размере', font=font, fill='#ffe0a3')
    for i, (label, icon) in enumerate(zip(LABELS, icons)):
        x, y = 18 + (i % 4) * 198, 48 + (i // 4) * 120
        # Actual native sprite, then exactly the same sprite at the game's usual 4x scale.
        preview.paste(icon, (x, y + 25), icon)
        large = icon.resize((64, 64), Image.Resampling.NEAREST)
        preview.paste(large, (x + 40, y), large)
        draw.text((x, y + 72), label, font=font, fill='#ffe0a3')
        draw.text((x, y + 94), '16 px                  64 px (×4)', font=small, fill='#c9c2b4')
    preview.save(ART / 'preview.png')
    report = {'source': 'generated/common-statuses.png', 'cellSize': [16, 16],
              'hudLayout': 'vanilla, no Harmony patch',
              'replacements': [{'id': key, 'index': MAPPING[key], 'label': label}
                               for key, label in zip(IDS, LABELS)],
              'validated': ['binary alpha', 'transparent cell borders', 'indices unchanged',
                            'other 150 icons unchanged', '10 reserved cells empty', '16 unique replacements']}
    (ART / 'export-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Packed and verified 16 HUD replacements and 6 matching handbook icons. Original indices and cell sizes preserved.')


if __name__ == '__main__':
    main()
