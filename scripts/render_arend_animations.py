"""Export every Arend frame group and schedule animation for visual review."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT.parent / 'output/ArendSprites-2026-10-27'
GROUPS = (
    ('walk_down', 'Ходьба вниз'), ('walk_right', 'Ходьба вправо'),
    ('walk_up', 'Ходьба вверх'), ('walk_left', 'Ходьба влево'),
    ('hand_gesture', 'Жест рукой'), ('adjust_glasses', 'Поправляет очки'),
    ('reading', 'Чтение спереди'), ('book_and_gestures', 'Перелистывает страницу'),
    ('standing_poses', 'Задумался: рука к подбородку'), ('rear_idle', 'Дыхание спиной'),
    ('armchair_poses', 'Неподвижное кресло'), ('standing_and_tea', 'Подносит чашку ко рту'),
    ('cup_and_hands', 'Держит чашку двумя руками'), ('side_conversation', 'Поправляет лацкан в профиль'),
    ('birds_breathing', 'Птицы: спокойное дыхание'),
)
BEHAVIORS = {
    'arend_read': 'Чтение', 'arend_armchair': 'Отдых в кресле',
    'arend_tea': 'Чаепитие', 'arend_birds': 'Наблюдение за птицами',
    'arend_think': 'Размышления',
}
BG, INK, FLOOR = '#e7dcc0', '#342a22', '#a58264'
COMPACT_W, COMPACT_H = 280, 300
FONT_PATH = 'C:/Windows/Fonts/arial.ttf'
FONT = ImageFont.truetype(FONT_PATH, 17)
SMALL = ImageFont.truetype(FONT_PATH, 14)


def cell(sheet, index):
    x, y = index % 4 * 16, index // 4 * 32
    return sheet.crop((x, y, x + 16, y + 32))


def centered(draw, box, y, text, font=FONT):
    x0, x1 = box
    width = draw.textbbox((0, 0), text, font=font)[2]
    draw.text(((x0 + x1 - width) // 2, y), text, font=font, fill=INK)


def panel(old, new, spec, tick, compact=False):
    width, height, scale = (COMPACT_W, COMPACT_H, 6) if compact else (384, 364, 8)
    page = Image.new('RGB', (width, height), BG)
    draw = ImageDraw.Draw(page)
    font = SMALL if compact else FONT
    centered(draw, (0, width), 5, spec['title'], font)
    centered(draw, (0, width // 2), 29, 'До', font)
    centered(draw, (width // 2, width), 29, 'После', font)
    index, phase = spec['timeline'][min(tick, len(spec['timeline']) - 1)]
    before_tick = tick * spec['frame_ms'] // spec.get('before_frame_ms', spec['frame_ms'])
    if spec.get('before_repeat'):
        before_tick %= len(spec['before_timeline'])
    before_index, _ = spec['before_timeline'][min(before_tick, len(spec['before_timeline']) - 1)]
    y = 52
    for column, (sheet, frame_index) in enumerate(((old, before_index), (new, index))):
        sprite = cell(sheet, frame_index).resize((16 * scale, 32 * scale), Image.Resampling.NEAREST)
        x = (width // 2 - sprite.width) // 2 + column * (width // 2)
        page.paste(sprite, (x, y), sprite)
        draw.line((x - 4, y + sprite.height, x + sprite.width + 4, y + sprite.height), fill=FLOOR)
        centered(draw, (column * width // 2, (column + 1) * width // 2), y + 32 * scale + 5, f'Кадр {frame_index}', SMALL)
    centered(draw, (0, width), height - 21, phase, SMALL)
    return page


def save_gif(path, images, frame_ms):
    images[0].save(path, save_all=True, append_images=images[1:],
                   duration=frame_ms, loop=0, disposal=2, optimize=False)
    with Image.open(path) as gif:
        duration = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            duration += gif.info['duration']
        assert duration == frame_ms * len(images), (path, duration)
        assert gif.size == images[0].size
        assert gif.info.get('loop') == 0
        return {'encoded_frames': gif.n_frames, 'duration_ms': duration,
                'size': list(gif.size), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def overview(path, old, new, specs, columns, frame_ms):
    count = max((duration(spec) + frame_ms - 1) // frame_ms for spec in specs)
    rows = (len(specs) + columns - 1) // columns
    images = []
    for tick in range(count):
        page = Image.new('RGB', (COMPACT_W * columns, COMPACT_H * rows), '#cdbf9f')
        for i, spec in enumerate(specs):
            local_tick = tick * frame_ms // spec['frame_ms']
            page.paste(panel(old, new, spec, local_tick, compact=True), (i % columns * COMPACT_W, i // columns * COMPACT_H))
        images.append(page)
    return save_gif(path, images, frame_ms)


def catalog(output, groups, behaviors):
    cards = []
    for heading, specs in (('Анимации расписания', behaviors), ('Все группы кадров', groups)):
        cards.append(f'<h2>{heading}</h2><section>')
        for spec in specs:
            name, title = html.escape(spec['filename']), html.escape(spec['title'])
            note = spec.get('note', 'Вход → два цикла → выход. Реальные кадры расписания, по 100 мс.')
            revision = hashlib.sha256((output / spec['filename']).read_bytes()).hexdigest()[:12]
            cards.append(f'<article><h3>{title}</h3><p>{note}</p><a href="{name}" target="_blank">'
                         f'<img src="{name}?v={revision}" alt="{title}"></a></article>')
        cards.append('</section>')
    document = '''<!doctype html><html lang="ru"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Аренд — версия 6, 88 кадров</title><style>
body{margin:24px;background:#f5f0e5;color:#342a22;font:16px Arial,sans-serif}
h1{font-size:26px}h2{margin-top:32px}h3{font-size:17px;margin:0 0 8px}
section{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}
article{padding:14px;border:1px solid #b7a889;border-radius:8px;background:#fffaf0}
article p{font-size:14px;min-height:32px}img{width:100%;max-width:384px;height:auto;image-rendering:pixelated}
a{color:#75482a}.note{max-width:1000px;line-height:1.5}</style><body>
<h1>Аренд — версия 6 · 88 кадров</h1>
<p class="note">Слева предыдущая сборка (v5), справа новая (v6). У каждой стороны свой номер кадра.
Сначала показаны пять анимаций, действительно используемых расписанием; затем все
15 действий с полными переходами. Дополнительные кадры показаны внутри движений,
а не как отдельные обрывочные циклы. Все 88 ячеек включены в GIF.
Возвращена большая красная книга из v4: меняется только лист над ней.
Утолщены рукава и соединены локти. При дыхании голова и шея неподвижны.
В кресле приподнимается, опираясь на подлокотники; в профиль поправляет лацкан.
Ноги стоят на одной линии пола.
Зимний лист совпадает с обычным.</p>
<p><a href="all-frame-groups.gif">Общий обзор всех движений</a> ·
<a href="all-schedule-animations.gif">Общий обзор расписания</a></p>'''
    (output / 'index.html').write_text(document + '\n'.join(cards) + '</body></html>', encoding='utf-8')
    lines = ['# GIF всех анимаций Аренда', '',
             'Версия 6: 20 отдельных GIF (15 действий и 5 анимаций расписания). Откройте `index.html`.', '',
             'В анимациях расписания показаны вход, два повтора основного цикла и выход (100 мс на кадр).',
             'Слева версия 5, справа версия 6. Все 88 кадров показаны в полных движениях, включая дополнительные фазы жестов 76–87.', '',
             '| GIF | Кадры |', '|---|---|']
    for spec in behaviors + groups:
        frames = ', '.join(str(n) for n in sorted({n for n, phase in spec['timeline']}))
        lines.append(f'| [{spec["title"]}]({spec["filename"]}) | {frames} |')
    (output / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def duration(spec):
    return max(len(spec['timeline']) * spec['frame_ms'],
               len(spec['before_timeline']) * spec.get('before_frame_ms', spec['frame_ms']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--before', type=Path, default=REVIEW / 'v6-before/Sprite.png')
    parser.add_argument('--before-manifest', type=Path, default=REVIEW / 'animations-v5-5728cd514b17/manifest.json')
    args = parser.parse_args()
    sprite_path = ROOT / 'assets/Character/Arend/Sprite.png'
    data_path = ROOT / 'assets/Code/arend.json'
    revision = hashlib.sha256(sprite_path.read_bytes() + data_path.read_bytes()).hexdigest()[:12]
    output = (args.output or REVIEW / f'animations-v6-{revision}').resolve()
    output.mkdir(parents=True, exist_ok=True)
    old = Image.open(args.before).convert('RGBA')
    new = Image.open(sprite_path).convert('RGBA')
    assert old.size == new.size == (64, 704)
    data = json.loads(data_path.read_text(encoding='utf-8-sig'))
    entries = next(c['Entries'] for c in data['Changes'] if c.get('Target') == 'Data/animationDescriptions')
    before_data = json.loads(args.before.with_name('arend.json').read_text(encoding='utf-8-sig'))
    before_entries = next(c['Entries'] for c in before_data['Changes'] if c.get('Target') == 'Data/animationDescriptions')
    before_specs = {s['filename']: s for s in json.loads(args.before_manifest.read_text(encoding='utf-8'))['gifs']}
    def timeline(description):
        intro, loop, outro = [[int(n) for n in part.split()] for part in description.split('/')]
        return ([(n, 'Вход') for n in intro] + [(n, f'Цикл {repeat}') for repeat in (1, 2) for n in loop]
                + [(n, 'Выход') for n in outro])
    manual = {
        4: [16] * 8 + [76, 17, 77] + [18] * 5 + [78, 19, 79] + [16] * 8,
        5: [20] * 10 + [80, 23, 21, 81, 82, 83] + [22] * 6 + [83, 82, 81, 21, 23, 80] + [20] * 8,
        6: [24] * 8 + [25] * 6 + [26] * 6 + [27] * 8 + [24] * 8,
        9: [36] * 8 + [37] * 6 + [38] * 8 + [39] * 6 + [36] * 8,
        12: [48] * 8 + [49] * 4 + [50] * 8 + [51] * 4 + [48] * 8,
        13: [52] * 8 + [84, 53, 85] + [54] * 5 + [86, 55, 87] + [52] * 8,
    }
    groups, behaviors = [], []
    for row, (slug, title) in enumerate(GROUPS):
        start = row * 4 if row < 14 else 68
        groups.append({'kind': 'frame_group', 'title': f'{start}–{start + 3} · {title}',
                       'filename': f'frames_{start:02d}-{start + 3:02d}_{slug}.gif',
                       'frame_ms': 180 if row < 4 else 350,
                       'note': 'Четыре игровые фазы ходьбы.' if row < 4 else 'Полное движение с паузами и промежуточными положениями.',
                       'timeline': [(i, 'Обзор группы кадров') for i in range(start, start + 4)]})
        full = {7: 'arend_read', 8: 'arend_think', 10: 'arend_armchair', 11: 'arend_tea', 14: 'arend_birds'}.get(row)
        if full:
            groups[-1].update(timeline=timeline(entries[full]), before_timeline=timeline(before_entries[full]),
                              frame_ms=100, note='Полный цикл с промежуточными фазами; 100 мс на кадр.')
        elif row in manual:
            previous = before_specs[groups[-1]['filename']]
            groups[-1].update(timeline=[(i, 'Движение') for i in manual[row]], frame_ms=100,
                              before_timeline=previous['timeline'],
                              before_frame_ms=previous['frame_ms'])
        else:
            groups[-1]['before_timeline'] = list(groups[-1]['timeline'])
    assert set(entries) == set(BEHAVIORS), 'Export every schedule animation'
    for key, description in entries.items():
        behaviors.append({'kind': 'schedule', 'key': key, 'title': BEHAVIORS[key],
                          'filename': f'schedule_{key}.gif', 'frame_ms': 100,
                          'description': description, 'timeline': timeline(description),
                          'before_timeline': timeline(before_entries[key])})
    assert {n for spec in groups for n, phase in spec['timeline']} == set(range(88))
    manifest = {'before': str(args.before.resolve()), 'current': str(ROOT / 'assets/Character/Arend/Sprite.png'),
                'version': 6, 'revision': revision, 'frame_count': 88,
                'sprite_sha256': hashlib.sha256(sprite_path.read_bytes()).hexdigest(),
                'animation_data_sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
                'empty_cells': [i for i in range(88) if cell(new, i).getbbox() is None],
                'before_empty_cells': [i for i in range(88) if cell(old, i).getbbox() is None], 'gifs': []}
    for spec in groups + behaviors:
        count = (duration(spec) + spec['frame_ms'] - 1) // spec['frame_ms']
        images = [panel(old, new, spec, i) for i in range(count)]
        result = save_gif(output / spec['filename'], images, spec['frame_ms'])
        manifest['gifs'].append({**spec, **result})
    manifest['overviews'] = {
        'all-frame-groups.gif': overview(output / 'all-frame-groups.gif', old, new, groups, 4, 100),
        'all-schedule-animations.gif': overview(output / 'all-schedule-animations.gif', old, new, behaviors, 3, 100),
    }
    catalog(output, groups, behaviors)
    index = output / 'index.html'
    index.write_text(index.read_text(encoding='utf-8').replace('<h1>', f'<p>Сборка v6-{revision}</p><h1>', 1), encoding='utf-8')
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive = output.parent / f'Arend-AllAnimations-v6-{revision}.zip'
    names = [spec['filename'] for spec in groups + behaviors]
    names += ['all-frame-groups.gif', 'all-schedule-animations.gif', 'index.html', 'README.md', 'manifest.json']
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as package:
        for name in names:
            package.write(output / name, name)
    # Existing browser links now lead to the hash-specific current build.
    legacy = REVIEW / 'animations/index.html'
    if legacy.is_file() and output != legacy.parent:
        saved = legacy.with_name('index-v3.html')
        if not saved.exists():
            saved.write_bytes(legacy.read_bytes())
        import os
        target = Path(os.path.relpath(output / 'index.html', legacy.parent)).as_posix()
        legacy.write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}">'
                          f'<title>Аренд v6</title><a href="{target}">Открыть новую галерею Аренда v6</a>', encoding='utf-8')
    (REVIEW / 'current-gallery.txt').write_text(str(output / 'index.html') + '\n', encoding='utf-8')
    print(f'Exported {len(groups)} frame groups + {len(behaviors)} schedule animations + 2 overviews.')
    print(f'All 88 cells covered; GIF frame timings and dimensions verified. Gallery: {output / "index.html"}')
    print(f'Archive: {archive}')


if __name__ == '__main__':
    main()
