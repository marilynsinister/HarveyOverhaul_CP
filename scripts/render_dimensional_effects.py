"""Export exact runtime sprites and readable review galleries.

Scaling in this file is for previews only; exports remain unmodified 16x16.
"""
from pathlib import Path
import hashlib
import json
import textwrap

from PIL import Image, ImageDraw, ImageFont
from validate_event_coords import strip_jsonc

PACK = Path(__file__).resolve().parents[1]
ART = PACK / 'art/effects-dimensional-16'


def render(sheets, index):
    ART.mkdir(parents=True, exist_ok=True)
    exports = ART / 'icons'
    exports.mkdir(exist_ok=True)
    names = {}
    for path in (PACK / 'assets/Code').glob('*.json'):
        data = json.loads(strip_jsonc(path.read_text(encoding='utf-8-sig')), strict=False)
        for change in data.get('Changes', []):
            if change.get('Target') == 'Data/Buffs':
                for key, value in change.get('Entries', {}).items():
                    if key in index and isinstance(value, dict):
                        names[key] = value.get('DisplayName', key)
    atlas = sheets['harveyBuffIcons.png']
    icons = {}
    manifest = {}
    for key, i in index.items():
        icon = atlas.crop((i % 16*16, i//16*16, i % 16*16+16, i//16*16+16))
        icon.save(exports / (key + '.png'))
        icons[key] = icon
        manifest[key] = {'index': i, 'name': names.get(key, key),
                         'size': [16, 16], 'sha256': hashlib.sha256(icon.tobytes()).hexdigest()}
    (ART / 'icons.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 23)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)

    # Full gallery: exact runtime index/name, enlarged sprite, actual 1x sprite.
    columns, cw, ch = 8, 154, 140
    gallery = Image.new('RGB', (columns*cw+32, ((len(index)+columns-1)//columns)*ch+96), '#eee4cd')
    draw = ImageDraw.Draw(gallery)
    draw.text((20, 16), 'Баффы и эффекты · 166 иконок', font=title, fill='#301e25')
    draw.text((20, 49), 'Рисунки 16×16 · слева ×4, справа настоящий размер · свет сверху слева', font=font, fill='#655363')
    for key, i in index.items():
        x, y = 16+i % columns*cw, 84+i//columns*ch
        draw.rectangle((x, y, x+cw-8, y+ch-9), fill='#f6eddd')
        draw.rectangle((x+4, y+5, x+69, y+70), fill='#d1b58f')
        enlarged = icons[key].resize((64, 64), Image.Resampling.NEAREST)
        gallery.paste(enlarged, (x+5, y+6), enlarged)
        gallery.paste(icons[key], (x+87, y+12), icons[key])
        draw.rectangle((x+82, y+39, x+108, y+65), fill='#303546')
        gallery.paste(icons[key], (x+87, y+44), icons[key])
        text = f'{i:03d}  {names.get(key, key)}'
        for row, line in enumerate(textwrap.wrap(text, 20)[:3]):
            draw.text((x+5, y+78+row*15), line, font=small, fill='#433440')
    gallery.save(ART / 'all-effects.png')

    # Compact selection for viewing in chat.
    selection = [
        ('Лечение', 'buffHarveyTreatment'), ('Капельница', 'buffHarveyIntensiveCare'),
        ('Антибиотик', 'buffAntibioticsTreatment'), ('Травяной чай', 'buffCalmTeaEffect'),
        ('Защита', 'buffHarveyProtection'), ('Восстановление', 'buffHarveyRecovery'),
        ('Перелом', 'buffFracturedBone'), ('Ушиб рёбер', 'buffBruisedRibs'),
        ('Порез', 'buffDeepCuts'), ('Ожог', 'buffBurnWounds'),
        ('Инфекция', 'buffInfectedWound'), ('Повязка', 'HarveyMod_CleanBandage'),
        ('Усталость', 'buffStressTired'), ('Гроза', 'buffStressThunder'),
        ('Бессонница', 'buffStressNoSleep'), ('Паника', 'buffStressPanic'),
        ('Тревога', 'buffStressAnxietyWave'), ('Истощение', 'buffStressExhaustion'),
        ('Озноб', 'buffStressTooCold'), ('Ясный ум', 'buffStressClearMind'),
        ('Болезненная память', 'buffStressFireMemory'), ('Фонарь', 'buffHarveyLantern'),
        ('Укус пчелы', 'HarveyMod_BeeSting'), ('Реабилитация', 'buffHarveyRehab'),
    ]
    compact = Image.new('RGB', (1008, 665), '#eee4cd')
    draw = ImageDraw.Draw(compact)
    draw.text((22, 15), 'Баффы и эффекты · 16×16 пикселей', font=title, fill='#301e25')
    draw.text((22, 49), 'Нативные рисунки · объём, блики и глубокие цветные тени', font=font, fill='#655363')
    for i, (label, key) in enumerate(selection):
        x, y = 18+i % 6*164, 84+i//6*142
        draw.rectangle((x, y, x+151, y+130), fill='#f8efdf')
        draw.rectangle((x+12, y+7, x+109, y+104), fill='#c6a67f')
        enlarged = icons[key].resize((96, 96), Image.Resampling.NEAREST)
        compact.paste(enlarged, (x+13, y+8), enlarged)
        compact.paste(icons[key], (x+121, y+49), icons[key])
        draw.text((x+7, y+111), label, font=small, fill='#433440')
    compact.save(ART / 'preview.png')

    before_path = ART / 'before/harveyBuffIcons.png'
    if before_path.is_file():
        before = Image.open(before_path).convert('RGBA')
        comparison = Image.new('RGB', (1008, 760), '#eee4cd')
        draw = ImageDraw.Draw(comparison)
        draw.text((22, 15), 'Было / стало', font=title, fill='#301e25')
        for i, (label, key) in enumerate(selection):
            x, y = 16+i % 6*164, 65+i//6*170
            old_i = index[key]
            old = before.crop((old_i % 16*16, old_i//16*16, old_i % 16*16+16, old_i//16*16+16))
            for icon, xx, tag in ((old, x, 'Было'), (icons[key], x+80, 'Стало')):
                draw.rectangle((xx, y, xx+71, y+71), fill='#c6a67f')
                enlarged = icon.resize((64, 64), Image.Resampling.NEAREST)
                comparison.paste(enlarged, (xx+4, y+4), enlarged)
                draw.text((xx+5, y+76), tag, font=small, fill='#655363')
            for row, line in enumerate(textwrap.wrap(label, 23)):
                draw.text((x+5, y+102+row*15), line, font=small, fill='#433440')
        comparison.save(ART / 'comparison.png')
    report = {'cellSize': [16, 16], 'buffCount': len(index),
              'method': 'native pixel matrices; explicit material ramps; no resampling',
              'source': '../../scripts/dimensional_effect_icons.py',
              'previewScalingOnly': 'nearest neighbor', 'runtimeAtlas': [256, 176],
              'unchangedIndices': True, 'alpha': [0, 255],
              'paletteColors': len(set(atlas.get_flattened_data())),
              'gameSessionTested': False}
    (ART / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    from draw_native_icons import build_sheets
    render(*build_sheets())
