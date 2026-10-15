"""Генерирует assets/Code/festivalsHarvey.json — Харви на праздниках.

1. Реплики на четырёх фестивалях по стадиям отношений (Data/Festivals/*):
   близкий друг (6♥+, без отношений) — ключ «Harvey»; Dating — «Harvey»; Married — «Harvey_spouse».
   Priority Late: перекрывает и ванильные строки, и строку SVE на Ночь духов (годы 3, 7, …).
     spring24 — Танец цветов, summer11 — Луау, fall27 — Ночь духов, winter25 — Праздник Зимней звезды.
2. Вечер после праздника (Farm, крыльцо, 22:00–2:00 — после фестиваля игра возвращает на ферму в 22:00),
   Dating или Married, по одному разу:
     F1 «После Танца цветов», F2 «После луау», F3 «После Ночи духов», F4 «Под Зимней звездой».
   Без общего кулдауна сюжета: праздник бывает раз в год.
3. Реплики накануне и на следующий день после всех 12 праздников 1.6 (ключи «<сезон>_<день>»,
   тексты — festival_around_data.py), по пяти стадиям. Priority Late + 10: перекрывают старые строки на эти дни
   из harvey_locations/dating/married. Беременность (dialoguesHarveyPregnant.json) — Late + 15, она главнее.
Запуск:  python scripts/build_festival_content.py
"""
import json
import os
import re

from event_builder import CD, H, msg, patch, qq, sp
from festival_around_data import AROUND, FESTIVAL_DAY_FRIEND

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'festivalsHarvey.json')

NS = 'HarveyOverhaulFestival'
ROMANCE = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married'
FX, FY0, FY1, FY3 = '{{HO_FarmX}}', '{{HO_FarmY0}}', '{{HO_FarmY1}}', '{{HO_FarmY3}}'

# ---------------------------------------------------------------- реплики на празднике
LINES = {
    'spring24': {
        'friend': 'Я не танцую. Я дежурю — на случай, если кто-то наступит кому-то на ногу.$h#$b#…Но цветы в этом году красивые. И ты, кажется, наконец выспалась — по лицу видно.$0',
        'dating': 'Солнышко, я тренировался. Три вечера подряд. На скелете из кабинета.$h#$b#Если наступлю тебе на ногу — бинт у меня с собой.$l',
        'married': 'Котёнок, в прошлом году я наступил тебе на ногу дважды. В этом у меня план: максимум один раз.$h#$b#И между танцами ты пьёшь воду. Возражения — после танца.$l',
    },
    'summer11': {
        'friend': 'Я принёс в суп морковь. Безопасно, полезно, скучно. Совсем как я.$h#$b#Если губернатору станет плохо от чьего-нибудь вклада — я рядом. Как всегда.$0',
        'dating': 'Солнышко, ты обгорела. Плечи. Не спорь, я вижу это отсюда.$a#$b#После луау — алоэ, и весь вечер ты под моим присмотром. В медицинском смысле. И не только.$l',
        'married': 'Я положил в суп имбирь — для иммунитета. Только не говори Гасу, он уверен, что это его секретный ингредиент.$h#$b#А тебе — шляпа, котёнок. Солнце в полдень — не шутки.$a',
    },
    'fall27': {
        'friend': 'Лабиринт? Нет, спасибо. Я и так каждый день блуждаю в чужих анамнезах.$h#$b#Если там станет не по себе — вернись. Я буду у входа. Возвращаться не стыдно.$0',
        'dating': 'Солнышко, если в лабиринте станет страшно — просто позови. Я приду быстрее любого скелета.$l#$b#…И нет, я не боюсь пауков. Я их уважаю. С безопасного расстояния.$h',
        'married': 'Котёнок, я в костюме. Да, это костюм врача. Нет, это не моя обычная одежда. Ну… почти.$h#$b#В лабиринте держись за мою руку. Не потому что страшно — потому что можно.$l',
    },
    'winter25': {
        'friend': 'Кто мой тайный друг? Не скажу. Врачебная тайна распространяется и на подарки.$h#$b#Пей горячее и не стой у двери — там сквозняк.$a',
        'dating': 'Солнышко, ты замёрзла — у тебя нос красный. Иди сюда, под мой шарф.$l#$b#Это медицинская процедура. Честно. Почти.$h',
        'married': 'Я каждый год волнуюсь, понравится ли тебе подарок, котёнок.$s#$b#Подсказка: он шерстяной, и в нём тебе будет тепло всю зиму. Я провалил сюрприз, да?$h',
    },
}


def festival_patches():
    patches = []
    for fest, lines in LINES.items():
        target = f'Data/Festivals/{fest}'
        patches.append({**patch(f'Festival {fest} — Харви, близкий друг (6♥+)', target, {'Harvey': lines['friend']}),
                        'Priority': 'Late',
                        'When': {'Relationship:Harvey': 'Friendly', 'Query: {{Hearts:Harvey}} >= 6': 'true'}})
        patches.append({**patch(f'Festival {fest} — Харви, Dating', target, {'Harvey': lines['dating']}),
                        'Priority': 'Late', 'When': {'Relationship:Harvey': 'Dating, Engaged'}})
        patches.append({**patch(f'Festival {fest} — Харви, Married', target, {'Harvey_spouse': lines['married']}),
                        'Priority': 'Late'})
    return patches


# ---------------------------------------------------------------- накануне и после праздника
STAGE_WHEN = {
    'doc': {'Relationship:Harvey': 'Unmet, Friendly', 'Hearts:Harvey': '0, 1, 2'},
    'friend': {'Relationship:Harvey': 'Friendly', 'Hearts:Harvey': '3, 4, 5, 6, 7'},
    'close': {'Relationship:Harvey': 'Friendly', 'Hearts:Harvey': '8, 9, 10'},
    'dating': {'Relationship:Harvey': 'Dating, Engaged'},
    'married': {'Relationship:Harvey': 'Married'},
}
TY = re.compile(r'(?<![а-яё])(ты|тебя|тебе|тобой|твой|твоя|твоё|твои|твою|твоих|сама)(?![а-яё])', re.I)
ROMANTIC = re.compile(r'солнышк|котён|любимая|люблю|дорогая|поцел', re.I)


def check_stage(stage, text):
    assert '"' not in text, text
    if stage == 'doc':
        assert not TY.search(text), ('doc: «ты»', text)
    if stage in ('doc', 'friend', 'close'):
        assert not ROMANTIC.search(text), (stage, 'романтика до отношений', text)


def around_patches():
    out = []
    for stage, when in STAGE_WHEN.items():
        entries = {}
        for day, lines in AROUND.items():
            check_stage(stage, lines[stage])
            entries[day] = lines[stage]
        out.append({**patch(f'Festival around — накануне и после праздников ({stage})', 'Characters/Dialogue/Harvey',
                            entries), 'Priority': 'Late + 10', 'When': when})
    for text in FESTIVAL_DAY_FRIEND.values():
        check_stage('friend', text)
    out.append({**patch('Festival around — утро праздника, 3–10 сердец без отношений', 'Characters/Dialogue/Harvey',
                        FESTIVAL_DAY_FRIEND), 'Priority': 'Late + 10',
                'When': {'Relationship:Harvey': 'Friendly', 'Hearts:Harvey': '3, 4, 5, 6, 7, 8, 9, 10'}})
    return out


# ---------------------------------------------------------------- вечер после праздника

def fkey(eid, season, day):
    """Как event_builder.key, но для праздничного дня: без !FestivalDay и без общего кулдауна."""
    return '/'.join([f'{NS}.{eid}', f'Season {season}', f'DayOfMonth {day}', 'Time 2200 2600', ROMANCE,
                     f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}'])


def fscript(actors, topic, body):
    cmds = ['none', f'{FX} {FY0}', actors, 'skippable',
            f'setSkipActions AddConversationTopic {topic} 2#AddConversationTopic {CD} 2',
            'ambientLight 120 120 60', 'pause 600', *body,
            f'addConversationTopic {topic} 2', f'addConversationTopic {CD} 2',
            'globalFade', 'viewport -1000 -1000', 'end']
    for c in cmds:
        assert '/' not in c, c
    return '/'.join(cmds)


PORCH = f'farmer {FX} {FY1} 2 Harvey {FX} {FY3} 0'

f1 = fscript(PORCH, 'HarveyFestival_FlowerDance', [
    msg('Поздний вечер после Танца цветов. Харви стоит у крыльца, всё ещё с цветком в петлице.'),
    sp(H, 'Я считал такты весь танец. Вслух. Кажется, Льюис слышал.$u'),
    sp(H, 'Можно… ещё раз? Здесь. Где никто не смотрит, как я сбиваюсь.$s'),
    qq(['Протянуть руку', '«Только если не будешь считать»', 'Надеть ему свой венок'], [
        [msg('Вы танцуете на траве у крыльца без музыки. Сверчки вместо скрипок.'),
         sp(H, 'Вот так лучше. Без зрителей я почти не наступаю.$l'), 'friendship Harvey 30'],
        [sp(H, 'Не буду. Обещаю. Раз… то есть ничего. Ничего не считаю.$h'),
         msg('Он сбивается сразу же — и смеётся. Ты тоже.'), 'friendship Harvey 30'],
        [msg('Ты снимаешь свой венок и надеваешь ему на голову. Он не снимает.'),
         sp(H, 'Теперь я весенний. Пациентам завтра не показывай.$h'), 'friendship Harvey 35'],
    ]),
    sp(H, 'Спасибо за танец. Оба. Второй — особенно.$l'),
])

f2 = fscript(PORCH, 'HarveyFestival_Luau', [
    msg('Тёплая ночь после луау. Пахнет морем и, почему-то, супом. Харви ждёт у крыльца с баночкой в руке.'),
    sp(H, 'Алоэ. Я же говорил — плечи.$a'),
    sp(H, 'Можно? Или сама?$s'),
    qq(['«Можно»', '«Сама. Но спасибо»', '«Сначала — твой нос. Он тоже красный»'], [
        [msg('Прохладный гель, осторожные пальцы. Он дует на кожу, как на ушиб у ребёнка.'),
         sp(H, 'Завтра не будет болеть. Послезавтра ты забудешь. А я — нет. Я всё помню.$l'), 'friendship Harvey 30'],
        [msg('Он отдаёт баночку и садится рядом на ступеньку.'),
         sp(H, 'Правильно. Ты сама знаешь, где болит. Я просто посижу.$0'), 'friendship Harvey 25'],
        [msg('Ты мажешь его нос — он даже не успевает возразить.'),
         sp(H, 'Это… справедливо. Врачи тоже обгорают. Особенно когда весь день смотрят не на солнце, а на кого-то другого.$l'),
         'friendship Harvey 35'],
    ]),
    sp(H, 'Посмотри наверх. Сколько звёзд. Хороший был день — один из тех, что хочется сохранить.$l'),
])

f3 = fscript(PORCH, 'HarveyFestival_SpiritsEve', [
    msg('Ночь духов позади. Харви проводил тебя до фермы с фонарём — и не спешит уходить.'),
    sp(H, 'Как тебе лабиринт? Только честно. Темнота, скелеты, крики… я весь вечер думал, не слишком ли это для тебя.$s'),
    qq(['«Было весело»', '«Было страшно. Но я дошла»', '«Я держалась за твою руку — этого хватило»'], [
        [sp(H, 'Весело. Хорошо. Тогда я зря перепроверил все выходы. Трижды.$h'), 'friendship Harvey 25'],
        [sp(H, 'Страшно — и дошла. Это и называется храбрость.$s#$b#Я горжусь. Нет, правда.$l'), 'friendship Harvey 35'],
        [sp(H, 'Хватило… Значит, рука работает лучше любого фонаря. Я запомню.$l'), 'friendship Harvey 35'],
    ]),
    sp(H, 'Мы оба храбрые, просто по-разному. Ты — в лабиринте. Я — когда отпускаю тебя туда.$s'),
    msg('Он вешает фонарь на крючок у двери. «Пусть горит до утра».'),
])

f4 = fscript(PORCH, 'HarveyFestival_WinterStar', [
    msg('Ночь Зимней звезды. Снег скрипит под ботинками. Харви достаёт из-за пазухи свёрток.'),
    sp(H, 'Официальный подарок был на празднике. А это — неофициальный.$s'),
    msg('Внутри — шарф ручной вязки. Петли неровные, один край длиннее другого.'),
    sp(H, 'Я учился у Эвелин. Шесть вечеров. Она сказала, у меня руки хирурга, а не вязальщицы.$u'),
    qq(['Надеть сразу', '«Ты связал это сам?..»', 'Обмотать шарфом вас обоих'], [
        [msg('Ты наматываешь шарф. Он колючий и очень тёплый.'),
         sp(H, 'Вот. Теперь я спокоен всю зиму.$l'), 'friendship Harvey 30'],
        [sp(H, 'Сам. Каждую кривую петлю. Если распустится — свяжу новый. Мне понравилось.$h'), 'friendship Harvey 30'],
        [msg('Шарф достаточно длинный для двоих — кажется, он так и задумывал.'),
         sp(H, 'Я… может быть, специально сделал его таким длинным.$l'), 'friendship Harvey 40'],
    ]),
    sp(H, 'С праздником Зимней звезды. Пусть следующий год будет таким же — только чуть меньше травм.$h'),
    'addItem (O)614 3',
])

EVENTS = {
    fkey('F1_AfterFlowerDance', 'Spring', 24): f1,
    fkey('F2_AfterLuau', 'Summer', 11): f2,
    fkey('F3_AfterSpiritsEve', 'Fall', 27): f3,
    fkey('F4_WinterStarNight', 'Winter', 25): f4,
}

TOPICS = {
    'HarveyFestival_FlowerDance': 'Я до сих пор слышу сверчков вместо скрипок. Лучший оркестр, что у меня был.$l',
    'HarveyFestival_Luau': 'Плечи не болят? Я проверю. Нет, не спрашиваю разрешения — уже спросил вчера, и оно, по-моему, действует.$h',
    'HarveyFestival_SpiritsEve': 'Фонарь горел до утра. Я проверял. В три часа. Случайно проснулся. Совершенно случайно.$u',
    'HarveyFestival_WinterStar': 'Ты носишь шарф. Кривые петли тебе идут.$l#$b#Эвелин хочет научить меня варежкам. Боюсь, это уже нейрохирургия.$h',
}

data = {'Changes': [
    *festival_patches(),
    *around_patches(),
    patch('Festival — вечер после праздника (Farm, Dating/Married)', 'Data/Events/Farm', EVENTS),
    {**patch('Festival — реплики Харви после праздника', 'Characters/Dialogue/Harvey', TOPICS), 'Priority': 'Late'},
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, len(EVENTS), 'evening events')
