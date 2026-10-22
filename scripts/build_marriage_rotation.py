"""Генерирует assets/Code/eventsMarriageRotation.json — повторяющиеся мини-сцены брака.

Сюжетные сцены брака (M1–M12) одноразовые, ко второму году брак затихал. Здесь — короткие бытовые
сцены, которые возвращаются:
  * у каждой свой кулдаун HarveyRot_<id>_CD (28 дней), между любыми двумя — HarveyRotation_CD (6 дней);
  * после кулдауна триггер DayStarted снимает сцену из просмотренных (MarkEventSeen … false);
  * сезонные сцены (весенний дождь, листопад, снег) повторяются раз в год сами собой.

  R1 «Зонт»              Farm, весна, дождь, утро       он провожает её до сарая под зонтом
  R2 «Звёзды с крыльца»  Farm, лето, ясно, ночь         считают звёзды — он называет созвездия по-врачебному
  R3 «Листопад»          Forest SVE (48–49,14), осень    прогулка, он собирает «гербарий для клиники»
  R4 «Снежки»            Farm, зима, день               снежная битва — и сразу проверка, не замёрзли ли руки
  R5 «Обед в клинике»    Hospital, палата A, среда      она приносит ему обед
  R6 «Чтение вслух»      Farm, воскресенье, вечер       медицинский журнал вслух — она засыпает
  R7 «Ритм»              Farm, ночь                     слушает её сердце: «ритм — счастливый»
  R8 «Вечер у фонтана»   Town SVE (25–26,30), пятница   прогулка, кормят уток… то есть фонтан
Запуск:  python scripts/build_marriage_rotation.py
"""
import json
import os

from event_builder import CD, H, msg, patch, qq, sp
from skip_actions import complete_skip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'eventsMarriageRotation.json')

NS = 'HarveyOverhaulRotation'
MARRIED = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married'
ROT_CD = 'HarveyRotation_CD'
REPEAT_DAYS = 28
BETWEEN_DAYS = 6
FX, FY0, FY1, FY3 = '{{HO_FarmX}}', '{{HO_FarmY0}}', '{{HO_FarmY1}}', '{{HO_FarmY3}}'
PORCH = f'farmer {FX} {FY1} 2 Harvey {FX} {FY3} 0'


def own_cd(eid):
    return f'HarveyRot_{eid}_CD'


def rkey(eid, *conds):
    return '/'.join([f'{NS}.{eid}', *conds, 'Friendship Harvey 2750', MARRIED, '!FestivalDay',
                     f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}',
                     f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {ROT_CD}',
                     f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {CD}'])


def rscript(eid, music, view, actors, body, extra=()):
    cds = [f'{own_cd(eid)} {REPEAT_DAYS}', f'{ROT_CD} {BETWEEN_DAYS}', f'{CD} 2']
    skip = [f'AddConversationTopic {c}' for c in cds]
    tail = [*[f'addConversationTopic {c}' for c in cds], 'globalFade', 'viewport -1000 -1000', 'end']
    cmds = [music, view, actors, 'skippable', 'setSkipActions ' + '#'.join(complete_skip(skip, [*extra, *body, *tail])),
            *extra, *body, *tail]
    for c in cmds:
        assert '/' not in c, c
    return '/'.join(cmds)


SCENES = {}

SCENES['R1_Umbrella'] = (rkey('R1_Umbrella', 'Season Spring', 'Weather Rain', 'Time 0600 1000'), rscript(
    'R1_Umbrella', 'continue', f'{FX} {FY0}', PORCH, [
        'pause 500',
        msg('Весенний дождь барабанит по крыльцу. Харви стоит у ступенек с раскрытым зонтом — огромным, клетчатым.'),
        sp(H, 'Провожу до сарая. Не потому что ты сахарная. Потому что у меня есть зонт и повод.$h'),
        qq(['Взять его под руку', '«Я и так промокну у грядок»', 'Выйти под дождь без зонта'], [
            [msg('Под зонтом тесно. Его плечо мокнет — он держит зонт над тобой.'),
             sp(H, 'Моё плечо высохнет. Твоё — моя забота.$l'), 'friendship Harvey 20'],
            [sp(H, 'Промокнешь. Но позже. Каждая сухая минута — маленькая победа медицины.$h'), 'friendship Harvey 15'],
            [msg('Ты выходишь под дождь и запрокидываешь голову. Он вздыхает — и складывает зонт.'),
             sp(H, 'Ладно. Промокнем вместе. Потом — чай. Это условие.$l'), 'friendship Harvey 25'],
        ]),
    ]))

SCENES['R2_Stars'] = (rkey('R2_Stars', 'Season Summer', 'Weather sunny', 'Time 2100 2500'), rscript(
    'R2_Stars', 'none', f'{FX} {FY0}', PORCH, [
        'pause 600',
        msg('Тёплая ночь. Вы сидите на ступеньках, голова к голове, и смотрите вверх.'),
        sp(H, 'Вон то созвездие я называю «Перелом лучевой кости». Видишь излом?$h'),
        qq(['«А это — „Пациент, который не пьёт воду“»', 'Положить голову ему на плечо', 'Найти самую яркую'], [
            [sp(H, 'Похоже. Очень похоже. Особенно вон та звезда, которая никого не слушает.$h#$b#…Это ты, если что.$l'), 'friendship Harvey 20'],
            [msg('Он замолкает на полуслове и укрывает тебя краем пледа.'),
             sp(H, 'Астрономия подождёт.$l'), 'friendship Harvey 20'],
            [sp(H, 'Самая яркая? Это планета, котёнок. Но я не буду спорить. Пусть будет звездой — твоей.$l'), 'friendship Harvey 20'],
        ]),
    ], extra=['ambientLight 120 120 60']))

SCENES['R3_FallLeaves'] = (rkey('R3_FallLeaves', 'Season Fall', 'Weather sunny', 'Time 1000 1600'), rscript(
    'R3_FallLeaves', 'continue', '49 14', 'farmer 48 14 1 Harvey 49 14 3', [
        'viewport 49 14 true', 'pause 500',
        msg('Осенний лес шуршит под ногами. Харви собирает листья — каждый внимательно, как образец для анализа.'),
        sp(H, 'Гербарий для клиники. Пациентам нравится смотреть на что-то, кроме моего лица.$h'),
        qq(['Принести ему самый красный лист', 'Засыпать его листьями', 'Найти гриб и показать'], [
            [sp(H, 'Клён. Идеальный. Подпишу: «Найден женой. Лучший экземпляр сезона».$l'), 'friendship Harvey 20'],
            [msg('Охапка листьев летит ему на голову. Он стоит неподвижно — весь в золоте.'),
             sp(H, 'Это… была атака. Я требую реванша. И тёплого какао.$h'), 'friendship Harvey 25'],
            [sp(H, 'Лисичка. Съедобная. Видишь, ты разбираешься в лесе лучше, чем я в людях.$h'), 'friendship Harvey 20'],
        ]),
    ]))

SCENES['R4_Snowballs'] = (rkey('R4_Snowballs', 'Season Winter', 'Time 1000 1500'), rscript(
    'R4_Snowballs', 'continue', f'{FX} {FY0}', PORCH, [
        'pause 500',
        msg('Свежий снег. Ты лепишь снежок — и Харви это видит.'),
        sp(H, 'Нет. Нет-нет. Я врач. Врачей не обстреливают — это конвенция.$u'),
        qq(['Бросить снежок', 'Сделать вид, что передумала', 'Отдать снежок ему'], [
            [msg('Снежок попадает ему в плечо. Через секунду в тебя летит ответный — аккуратный, медленный, почти вежливый.'),
             sp(H, 'Вот. Мы квиты. А теперь — руки. Покажи. Холодные. Конечно. Ко мне в карманы.$l'), 'friendship Harvey 25'],
            [sp(H, 'Передумала? Подозрительно.$a'),
             msg('Пока он подозревает, снежок прилетает ему в спину.'),
             sp(H, 'Коварство! Медицина такого не прощает. Только жена.$h'), 'friendship Harvey 20'],
            [msg('Он вертит снежок в руках и бросает в сугроб — далеко-далеко.'),
             sp(H, 'Вот. Безопасно. А теперь варежки — твои мокрые. Мои сухие. Меняемся.$l'), 'friendship Harvey 20'],
        ]),
    ]))

SCENES['R5_ClinicLunch'] = (rkey('R5_ClinicLunch', 'DayOfWeek Wed', 'Time 1200 1400'), rscript(
    'R5_ClinicLunch', 'Hospital_Ambient', '14 6', 'farmer 14 6 1 Harvey 15 6 3', [
        'viewport 14 6 true', 'pause 500',
        msg('Ты приносишь в клинику обед. Харви смотрит на контейнер так, будто ему вручили медаль.'),
        sp(H, 'Ты принесла мне обед. Посреди рабочего дня. Мару, ты это видишь?$h'),
        qq(['«Ешь, пока горячее»', '«Сначала вымой руки, доктор»', 'Сесть рядом и есть вместе'], [
            [sp(H, 'Есть, пока горячее. Это мой совет. Мне его вернули.$h'), 'friendship Harvey 20'],
            [sp(H, '…Справедливо. Ушёл мыть. Двадцать секунд, с мылом.$u'), 'friendship Harvey 20'],
            [msg('Вы едите на краю пустой койки. Он рассказывает про Джорджа и его спину, ты — про курицу, которая снесла двойное яйцо.'),
             sp(H, 'Самый лучший обеденный перерыв за неделю. Единственный, но лучший.$l'), 'friendship Harvey 25'],
        ]),
    ]))

SCENES['R6_ReadingAloud'] = (rkey('R6_ReadingAloud', 'DayOfWeek Sun', 'Time 1700 2000'), rscript(
    'R6_ReadingAloud', 'none', f'{FX} {FY0}', PORCH, [
        'pause 500',
        msg('Воскресный вечер. Харви читает вслух медицинский журнал. Ты слушаешь — или делаешь вид.'),
        sp(H, '«…Таким образом, регулярный отдых снижает риск сердечно-сосудистых…» Ты слушаешь?$a'),
        qq(['«Конечно»', 'Притвориться спящей', 'Попросить почитать что-нибудь другое'], [
            [sp(H, 'Тогда перескажи последнее предложение.$a'), msg('Ты пересказываешь. Почти правильно.'),
             sp(H, 'Почти правильно — это уже лучше, чем большинство моих коллег.$h'), 'friendship Harvey 15'],
            [msg('Ты закрываешь глаза. Он замолкает, укрывает тебя пледом — и продолжает читать, но уже шёпотом.'),
             sp(H, '«…регулярный отдых…» Вот. Молодец. Ты выполняешь рекомендации журнала.$l'), 'friendship Harvey 25'],
            [sp(H, 'Другое? У меня есть «Справочник по ядовитым грибам долины». Захватывающее чтение.$h#$b#…Ладно. Сказки. Я помню одну. Про лиса-лекаря.$l'), 'friendship Harvey 20'],
        ]),
    ]))

SCENES['R7_Heartbeat'] = (rkey('R7_Heartbeat', 'Time 2100 2400'), rscript(
    'R7_Heartbeat', 'none', f'{FX} {FY0}', PORCH, [
        'pause 600',
        msg('Ночь. Харви прикладывает ухо к твоей груди — без стетоскопа, просто так.'),
        sp(H, 'Тш-ш. Слушаю.$s'),
        'pause 1000',
        sp(H, 'Ритм ровный. Немного частый. Диагноз: счастливый.$l'),
        qq(['«Это из-за тебя»', 'Послушать его сердце в ответ', '«Ты же говорил, это не диагноз»'], [
            [sp(H, 'Значит, я — побочный эффект. Самый приятный в моей практике.$l'), 'friendship Harvey 20'],
            [msg('Ты прижимаешься ухом к его груди. Сердце стучит гулко и быстро.'),
             sp(H, '…Ну что, доктор? Не говори. Я знаю. Тоже счастливый.$l'), 'friendship Harvey 25'],
            [sp(H, 'Не диагноз. Но в карту я это запишу. Мелким почерком, на полях.$h'), 'friendship Harvey 20'],
        ]),
    ], extra=['ambientLight 120 120 60']))

SCENES['R8_FountainWalk'] = (rkey('R8_FountainWalk', 'DayOfWeek Fri', 'Weather sunny', 'Time 1800 2100'), rscript(
    'R8_FountainWalk', 'none', '26 28', 'farmer 25 30 1 Harvey 26 30 3', [
        'viewport 26 28 true', 'pause 500',
        msg('Пятничный вечер у фонтана. Харви достаёт из кармана монетку.'),
        sp(H, 'Каждую пятницу — одна монетка. Это не суеверие. Это… статистика желаний.$h'),
        qq(['Бросить монетку вместе', '«И что ты загадываешь?»', 'Взять его за руку и просто стоять'], [
            [msg('Две монетки булькают одновременно.'), sp(H, 'Одно желание на двоих. Так эффективнее.$l'), 'friendship Harvey 20'],
            [sp(H, 'Одно и то же. Каждую пятницу. Чтобы ты была здорова. И чтобы я перестал это загадывать — потому что сбылось.$l'), 'friendship Harvey 25'],
            [msg('Вы стоите у воды, пока не зажигаются фонари.'), sp(H, 'Монетка может подождать. Этот вечер — нет.$l'), 'friendship Harvey 20'],
        ]),
    ]))

TARGETS = {
    'R1_Umbrella': 'Farm', 'R2_Stars': 'Farm', 'R3_FallLeaves': 'Forest', 'R4_Snowballs': 'Farm',
    'R5_ClinicLunch': 'Hospital', 'R6_ReadingAloud': 'Farm', 'R7_Heartbeat': 'Farm', 'R8_FountainWalk': 'Town',
}

by_target = {}
for eid, (k, s) in SCENES.items():
    by_target.setdefault(TARGETS[eid], {})[k] = s

triggers = {}
for eid in SCENES:
    tid = f'{{{{ModId}}}}_Rotation_{eid}'
    triggers[tid] = {
        'Id': tid,
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}, !PLAYER_HAS_CONVERSATION_TOPIC Current {own_cd(eid)}',
        'Actions': [f'MarkEventSeen Current {NS}.{eid} false'],
        'MarkActionApplied': False,
    }

data = {'Changes': [
    *[patch(f'Rotation — повторяющиеся сцены брака ({t})', f'Data/Events/{t}', entries) for t, entries in by_target.items()],
    patch('Rotation — вернуть сцену в ротацию после кулдауна', 'Data/TriggerActions', triggers),
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, len(SCENES), 'scenes')
