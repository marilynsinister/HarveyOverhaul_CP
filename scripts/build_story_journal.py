"""Генерирует assets/Code/storyJournal.json — данные вкладки «История» (HarveyOverhaulCore: HarveyStoryJournal).

Пустой ассет Mods/marilynsinister.HarveyOverhaul/StoryJournal создаёт Core, здесь — EditData с записями.
Арки, которые зависят от настроек, подключаются через When (TraumaBackstory, AdultEvents).

Поля записи: Arc, ArcOrder, Order, EventIds (варианты через пробел), Title, Summary (после просмотра),
Hint (мягкая подсказка — где и когда, без сюжета), Requires (ID через пробел, все должны быть просмотрены),
Condition (GameStateQuery, для «любой из вариантов» и статуса отношений), Repeatable.
Новую сцену — добавить строку сюда и перезапустить скрипт.
Запуск:  python scripts/build_story_journal.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'storyJournal.json')

S = 'HarveyOverhaulStory.'
A3 = 'HarveyOverhaulArc3.'
SC = 'HarveyOverhaulScars.'
LF = 'HarveyOverhaulLife.'
M = 'HarveyOverhaulMarriage.'
F = 'HarveyOverhaulFestival.'
R = 'HarveyOverhaulRotation.'
AD = 'HarveyOverhaulAdult.'

DATING = 'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married'
MARRIED = 'PLAYER_NPC_RELATIONSHIP Current Harvey Married'
YEAR2 = 'YEAR 2'


def any_seen(*ids):
    return 'ANY ' + ' '.join(f'"PLAYER_HAS_SEEN_EVENT Current {i}"' for i in ids)


def hearts(text):
    """«(4♥)» → «(4 сердца)»: в шрифте игры нет символа сердца."""
    def word(n):
        return 'сердце' if n == 1 else 'сердца' if 2 <= n <= 4 else 'сердец'
    return re.sub(r'(\d+)♥', lambda m: f'{m.group(1)} {word(int(m.group(1)))}', text)


def e(ids, title, summary, hint, requires='', condition='', repeatable=False):
    hint = hearts(hint)
    return {'EventIds': ids, 'Title': title, 'Summary': summary, 'Hint': hint,
            'Requires': requires, 'Condition': condition, 'Repeatable': repeatable}


ARCS = [
    ('Знакомство', 'base', [
        e('eventHarveyFirstMeeting', 'Первая встреча', 'Харви встретил тебя на остановке и накормил бутербродами.',
          'В первые дни в долине — у автобусной остановки.'),
        e('eventHarveyCheckup', 'Первый осмотр', 'Храбрость — продолжать, несмотря на страх. Так сказал Харви.',
          'Если пообещаешь Харви осмотр — загляни в клинику после обеда.', 'eventHarveyFirstMeeting'),
        e('eventHarveyFirstVisit', 'Визит на ферму', 'Харви пришёл проверить, как ты устроилась.',
          'Утром на ферме, в первую неделю.', 'eventHarveyFirstMeeting'),
        e('eventHarveySecondVisit', 'Второй визит', 'Харви снова пришёл утром — уже почти как сосед.',
          'Утром на ферме, через неделю после первого визита.', 'eventHarveyFirstVisit'),
        e('eventHarveyFirstWalk', 'Первая прогулка', 'Солнечное утро и первая прогулка вместе.',
          'Солнечным утром на ферме, ближе к середине первого сезона.', 'eventHarveySecondVisit'),
    ]),
    ('Арка 1. Принять помощь', 'base', [
        e(S + 'E1_SlipperyPath', 'Скользкая тропа', 'Ветреное утро, ты поскользнулась — Харви оказался рядом.',
          'Ветреным утром у автобусной остановки (2♥).'),
        e(S + 'E2_InsistentExam', 'Настойчивый осмотр', 'Харви настоял на осмотре — и сократил его по твоему знаку.',
          'Днём в клинике (3♥).', S + 'E1_SlipperyPath'),
        e(S + 'E2B_QuietAgreement', 'Тихий договор', 'Договорились без слов.', 'Днём в городе.', S + 'E2_InsistentExam'),
        e(S + 'E3_ForestApothecary', 'Лесная аптека', 'Ты показала Харви травы, которых нет в его справочниках.',
          'Днём в лесу, с четверга по субботу (4♥).', S + 'E2B_QuietAgreement'),
        e(S + 'E3B_WingPatient', 'Пациент с крылом', 'Раненая птица и двое лекарей.', 'Снова днём в лесу.',
          S + 'E3_ForestApothecary'),
        e(S + 'E4_PierBreath', 'Дыхание на пирсе', 'Вечер на пирсе: Харви учил дышать медленно.',
          'Вечером на пляже (5♥).', S + 'E3B_WingPatient'),
        e(S + 'E4B_TooQuiet', 'Слишком тихо', 'Харви заметил, что ты замолчала.', 'Вечером в горах (6♥).',
          S + 'E4_PierBreath'),
        e(S + 'E5_StormBeside', 'Гроза рядом', 'В грозу он просто был рядом.', 'В грозу, днём в клинике.',
          S + 'E4B_TooQuiet'),
        e(S + 'E6_SayItOutLoud', 'Сказать вслух', 'Ты впервые сказала словами, что тебе плохо.',
          'В клинике после обеда (7♥).', S + 'E5_StormBeside'),
        e(S + 'E7_DoorSignal', 'Знак на двери', 'Ваш тихий знак: если плохо — сигнал на двери.',
          'Вечером у фермы (8♥).', S + 'E6_SayItOutLoud'),
        e(S + 'E7_TownSip_Sunny', 'Глоток на площади', 'Солнечный день и вода на площади.',
          'В ясный полдень в городе.', S + 'E7_DoorSignal'),
        e(S + 'E8_QuietShelf', 'Тихая полка', 'Субботний музей и тишина на двоих.', 'В субботу в музее.',
          S + 'E7_TownSip_Sunny'),
        e(S + 'E8_BadDayNoReason', 'Плохой день без причины', 'Харви не спрашивал «почему». Просто был рядом.',
          'Днём в лесу.', S + 'E7_DoorSignal'),
        e(S + 'E9_LightInWindow', 'Свет в окне', 'Он оставил свет в окне клиники — для тебя.',
          'Поздним вечером в городе.', S + 'E8_QuietShelf'),
        e(S + 'E9_CameByHerself', 'Пришла сама', 'Ты сама пришла в клинику — и сама выбрала, какой будет осмотр.',
          'Днём в клинике (9♥).', S + 'E8_BadDayNoReason'),
    ]),
    ('Арка 2. Ошибки и договоры', 'base', [
        e(f'{S}E10_HarveyWasWrong {S}E10_HarveyWasWrong_Dating', 'Харви ошибся', 'Харви сорвался на тон — и извинился.',
          'Вечером в городе.', S + 'E9_CameByHerself'),
        e(S + 'E11_HomeSafetyProtocol', 'Протокол безопасности', 'Правила для дома — с твоими поправками.',
          'Днём дома или в клинике.', condition=any_seen(S + 'E10_HarveyWasWrong', S + 'E10_HarveyWasWrong_Dating')),
        e(f'{S}E12_HarveyIsTired {S}E12_HarveyIsTired_Dating', 'Харви устал', 'Теперь уставшим был он — и ты заметила.',
          'В клинике после обеда.', S + 'E11_HomeSafetyProtocol'),
        e(S + 'E13_MinesAgreement', 'Договор о шахтах', 'Правила о шахтах — для обоих.',
          'Утром у остановки или вечером в лесу.',
          condition=any_seen(S + 'E12_HarveyIsTired', S + 'E12_HarveyIsTired_Dating')),
        e('HarveyOverhaulRomance.E1_NotAnExamDate', 'Не осмотр, а свидание', 'Первое свидание, которое не было осмотром.',
          'Вечером на пляже, когда вы встречаетесь.', condition=DATING),
        e(S + 'E14_NotOnlyPatient', 'Не только пациентка', 'Ты для него — не только пациентка.', 'Вечером в лесу.',
          f'HarveyOverhaulRomance.E1_NotAnExamDate {S}E13_MinesAgreement'),
        e(f'{S}E15_FuturePlan {S}E15_FuturePlan_Married', 'План жизни', 'Харви показал план на будущее — общий.',
          'Вечером дома.', S + 'E14_NotOnlyPatient'),
    ]),
    ('Арка 3. Право на заботу', 'base', [
        e(A3 + 'N1_NightShift', 'Ночная смена', 'Ты узнала, откуда в нём эта гиперопека.',
          'Вечером у клиники (8♥).', S + 'E6_SayItOutLoud'),
        e(A3 + 'N2_Spring', 'Источник', 'Её мир, где он не главный.', 'Ясным днём у Источника фей.', A3 + 'N1_NightShift'),
        e(A3 + 'N3_ContactCard', 'Графа «близкие»', 'Его анкета — и в графе «близкие» твоё имя.',
          'В клинике, после букета.', condition=DATING),
        e(A3 + 'N4_BlueMoon', 'Голубая луна', 'Признание на винограднике.',
          'Ясным вечером на винограднике «Голубая луна».', A3 + 'N3_ContactCard'),
        e(f'{A3}N5_ReversedKit {A3}N5_ReversedKit_Confess', 'Перевёрнутая аптечка', 'Ты перевязала его — роли поменялись.',
          'Днём на Плато искателей приключений — после того, как побываешь в Хайлендс.', A3 + 'N4_BlueMoon'),
        e(A3 + 'N6_StormCall', 'Гроза и вызов', 'Ты отпустила его на вызов в грозу.', 'В грозу, в клинике (брак).',
          condition=any_seen(A3 + 'N5_ReversedKit', A3 + 'N5_ReversedKit_Confess')),
        e(A3 + 'N7_Key', 'Ключ', 'Запасной ключ от клиники: ты — его экстренный контакт.',
          'После обеда в клинике (брак).', A3 + 'N6_StormCall'),
    ]),
    ('Своя жизнь Харви', 'base', [
        e(LF + 'H1_Offer', 'Письмо на столе', 'Харви позвали возглавить травмоцентр в Зузу.',
          'Днём в клинике — после того, как заметишь его усталость (8♥).',
          condition=any_seen(S + 'E12_HarveyIsTired', S + 'E12_HarveyIsTired_Dating')),
        e(LF + 'H2_Doubts', 'Сомнения', 'Закат на пляже и честный вопрос.', 'Ясным вечером на пляже.', LF + 'H1_Offer'),
        e(f'{LF}H3_Answer {LF}H3_Answer_Go', 'Ответ', 'Харви остался — на своих условиях. У Мару теперь есть наставник.',
          'Ясным утром у клиники.', LF + 'H2_Doubts'),
        e(LF + 'K1_TwoWars', 'Двое с войной', 'Кент и Харви на лавке, шахматы без фигур.',
          'Ясным вечером у дома Кента — когда Кент вернётся в долину (6♥).', condition=YEAR2),
        e(LF + 'L1_LinusTea', 'Чай у Линуса', 'Линус учит доктора отдыхать.', 'Ясным вечером у палатки Линуса (4♥).'),
        e('HarveyOverhaulClinic.V1_VaccineDay', 'День прививок', 'Винсент, наклейки-звёздочки и одно храброе плечо.',
          'Весной, после письма из клиники (3♥).', repeatable=True),
        e('HarveyOverhaulClinic.HS1_Heatstroke', 'Тепловой удар', 'Наутро после луау Пэм оказалась в клинике — и ты помогла.',
          'Через день-два после луау, утром в клинике (3♥).', repeatable=True),
    ]),
    ('Свидания и брак', 'base', [
        e('eventHarveyFirstDate', 'Первое свидание', 'Вечер в лесу — уже не врач и пациентка.',
          'Ясным вечером в лесу, после букета.', condition=DATING),
        e('eventHarveyMountainDate', 'Свидание в горах', 'Утро в горах вдвоём.', 'Ясным утром в горах.', condition=DATING),
        e('HarveyOverhaulDate.D1_Fountain', 'Свидание у фонтана', 'Три пункта плана — и шарф в два оборота.',
          'В воскресенье у фонтана, после записки от Харви.', condition=DATING),
        e('eventHarveyPropose', 'Предложение', 'Вечер на пляже и самый важный вопрос.', 'Ясным вечером на пляже (10♥).',
          condition=DATING),
        e(M + 'M1_FirstShift', 'Первая смена', 'Первое утро после свадьбы: Харви не может уйти на работу.',
          'Утром на ферме после свадьбы.', condition=MARRIED),
        e(M + 'M2_SickDay', 'Больничный', 'Харви заболел — и ты не пустила его на смену.', 'Зимним утром на ферме.',
          M + 'M1_FirstShift'),
        e(M + 'M3_Anniversary', 'Годовщина', 'Отчёт о годовщине: «Состояние: любима».',
          'В годовщину свадьбы, вечером на пляже.', condition=MARRIED, repeatable=True),
        e(M + 'M4_HarveyBirthday', 'День рождения Харви', 'Торт со свечой-стетоскопом.', '14 зимы, в клинике.',
          condition=DATING),
        e(M + 'M5_Overworked', 'Перетрудилась', 'Он вымыл тебе руки и сам полил дальнее поле.',
          'Летним или осенним вечером на ферме.', M + 'M1_FirstShift'),
        e(M + 'M6_HerCold', 'Твоя простуда', 'Теперь болела ты — и он остался дома.', 'Осенним или зимним утром.',
          M + 'M2_SickDay'),
        e(M + 'M7_LateReturn', 'Ждал ночью', 'Фонарь на крыльце и плед на ступенях.', 'Если вернёшься домой очень поздно.',
          condition=MARRIED),
        e(M + 'M8_SleeplessNight', 'Бессонная ночь', 'Ему приснился Зузу. Ты уложила его спать.', 'На рассвете у дома.',
          M + 'M1_FirstShift'),
        e(M + 'M9_ForestPharmacy', 'Лесная аптека', 'Ты — эксперт, он — стажёр.', 'Ясным весенним днём в лесу.',
          condition=MARRIED),
        e(M + 'M10_FountainDance', 'Танец у фонтана', 'Обещанный танец вместо пропущенного.',
          'Ясным субботним вечером у фонтана.', condition=MARRIED),
        e(M + 'M11_BadDay', 'Тяжёлый день', 'Он потерял пациента. Ты пришла.', 'После обеда в клинике.',
          M + 'M8_SleeplessNight'),
        e(M + 'M12_SundayPancakes', 'Блинчики', 'Воскресный закон: никакой фермы до завтрака.', 'Воскресным утром.',
          M + 'M1_FirstShift'),
    ]),
    ('Праздники', 'base', [
        e(F + 'F1_AfterFlowerDance', 'После Танца цветов', 'Второй танец — без музыки, со сверчками.',
          'Вечером после Танца цветов, на ферме (встречаетесь или в браке).', condition=DATING),
        e(F + 'F2_AfterLuau', 'После луау', 'Алоэ, плечи и звёзды.', 'Вечером после луау, на ферме.', condition=DATING),
        e(F + 'F3_AfterSpiritsEve', 'После Ночи духов', 'Фонарь, который горел до утра.',
          'Ночью после Ночи духов, на ферме.', condition=DATING),
        e(F + 'F4_WinterStarNight', 'Под Зимней звездой', 'Шарф с кривыми петлями — на двоих.',
          'Вечером после Праздника Зимней звезды, на ферме.', condition=DATING),
    ]),
    ('Будни брака', 'base', [
        e(R + 'R1_Umbrella', 'Зонт', 'Клетчатый зонт и мокрое плечо.', 'Весенним дождливым утром на ферме.',
          condition=MARRIED, repeatable=True),
        e(R + 'R2_Stars', 'Звёзды с крыльца', 'Созвездие «Перелом лучевой кости».', 'Ясной летней ночью на крыльце.',
          condition=MARRIED, repeatable=True),
        e(R + 'R3_FallLeaves', 'Листопад', 'Гербарий для клиники и атака листьями.', 'Ясным осенним днём в лесу.',
          condition=MARRIED, repeatable=True),
        e(R + 'R4_Snowballs', 'Снежки', 'Снежная битва — и сразу проверка рук.', 'Зимним днём на ферме.',
          condition=MARRIED, repeatable=True),
        e(R + 'R5_ClinicLunch', 'Обед в клинике', 'Ты принесла ему обед посреди рабочего дня.',
          'В среду в обед, в клинике.', condition=MARRIED, repeatable=True),
        e(R + 'R6_ReadingAloud', 'Чтение вслух', 'Медицинский журнал вслух — и сказка про лиса-лекаря.',
          'Воскресным вечером на крыльце.', condition=MARRIED, repeatable=True),
        e(R + 'R7_Heartbeat', 'Ритм', 'Диагноз: счастливый.', 'Поздним вечером на крыльце.',
          condition=MARRIED, repeatable=True),
        e(R + 'R8_FountainWalk', 'Вечер у фонтана', 'Одна монетка каждую пятницу.', 'Ясным пятничным вечером у фонтана.',
          condition=MARRIED, repeatable=True),
    ]),
    ('Вечера у Харви', 'base', [
        e('{{ModId}}_eventHarveyEveningRadio', 'Радио', 'Вечер у Харви и старое радио.',
          'Вечером в комнате Харви над клиникой (4♥).'),
        e('{{ModId}}_eventHarveyEveningPlanes', 'Модели самолётов', 'Харви показал свои модели.',
          'Вечером в комнате Харви (6♥).'),
        e('{{ModId}}_eventHarveyEveningJournal', 'Дневник', 'Он прочитал тебе страницу из дневника.',
          'Вечером в комнате Харви, когда вы встречаетесь.', condition=DATING),
    ]),
    ('Прошлое', 'trauma', [
        e('eventRescueOperation', 'Гроза в кустах', 'Харви нашёл тебя в грозу и понял: для тебя это не гром.',
          'В грозу — если Харви позовут на помощь.'),
        e(LF + 'LW1_LewisSorry', 'Прости старого дурака', 'Льюис извинился за ту ночь на дороге.',
          'Через пару дней после грозы — утром у клиники.', 'eventRescueOperation'),
        e('eventHarveyTraumaExam', 'Осмотр спины', 'Харви увидел ожоги и не стал расспрашивать.',
          'Днём в клинике (8♥).'),
        e(S + 'T1_WhatIRemember', 'Что я помню', 'Ты рассказала столько, сколько захотела.', 'В клинике после обеда (8♥).',
          condition=any_seen('eventHarveyTraumaExam', 'eventRescueOperation')),
        e(S + 'T2_LastOne', 'Последняя', '«Ты не последняя. Ты — выжившая».', 'Днём на лесной тропе.',
          S + 'T1_WhatIRemember'),
    ]),
    ('Шрамы', 'trauma', [
        e(SC + 'C1_LongSleeves', 'Длинные рукава', 'Жара, площадь и компресс — ни слова о рукавах.',
          'Жарким летним полднем у фонтана (4♥).',
          condition=any_seen('eventHarveyTraumaExam', 'eventRescueOperation')),
        e(SC + 'C2_Pop', 'Хлопок', 'Хлопок пробки — и Кент, который считал вслух.',
          'Ясным вечером у салуна — когда в долине будет Кент (5♥).', SC + 'C1_LongSleeves'),
        e(SC + 'C3_ScarSalve', 'Мазь для рубцов', 'Харви сделал мазь и спросил: «Сама — или мне можно?»',
          'Осенью или зимой в клинике — когда Харви начнёт доверять тому, как ты соблюдаешь лечение (вкладка «Доверие»).',
          SC + 'C1_LongSleeves'),
        e(SC + 'C4_ZuzuLetter', 'Письмо из Зузу', 'Письмо министерства — и решение было твоим.',
          'Когда придёт письмо из Зузу, отнеси его в клинику (7♥).', SC + 'C3_ScarSalve'),
        e(SC + 'C6_Stranger', 'Чужой в Долине', 'Харви понял: защищать не значит воевать.',
          'Ясным днём на автобусной остановке (8♥).', SC + 'C4_ZuzuLetter'),
        e(SC + 'C7_SleevesUp', 'Рукава закатаны', 'Ты закатала рукава при всех. Он — тоже.',
          'Летним днём на пляже, когда вы будете вместе.', SC + 'C6_Stranger'),
        e(SC + 'C8_Map', 'Карта, которую не пишут', 'Он не лечил — запоминал.', 'Вечером на крыльце, в браке.',
          SC + 'C7_SleevesUp'),
    ]),
    ('Только вдвоём (18+)', 'adult', [
        e(AD + 'A1_LunchBreak', 'Обеденный перерыв', 'Записка в среду — и четверг только для вас.',
          'В четверг днём в комнате Харви, после его записки.', condition=MARRIED),
        e(AD + 'A2_NightSwim', 'Ночное купание', 'Летняя ночь у моря.', 'Ясной летней ночью на пляже.', condition=MARRIED),
        e(AD + 'A3_Downpour', 'Ливень', 'Дождь, который никто не заметил.', 'Дождливым вечером на ферме.', condition=MARRIED),
        e(AD + 'A4_WhiteCoat', 'Белый халат', 'Его халат тебе велик.', 'Во вторник днём в комнате Харви.',
          AD + 'A1_LunchBreak'),
        e(AD + 'A5_ReverseExam', 'Наоборот', 'Стетоскоп у тебя, пациент — он.', 'В пятницу днём в клинике.',
          AD + 'A1_LunchBreak'),
        e(AD + 'A6_Vineyard', 'Виноградник', 'Вино, «одобренное кардиологией».', 'Ясным вечером на винограднике.',
          condition=MARRIED),
        e(AD + 'A7_NightSpring', 'Ночной источник', 'Светящаяся вода и никаких минут.', 'Ночью у Источника фей.',
          A3 + 'N2_Spring'),
        e(AD + 'A8_Frozen', 'Мороз', 'Ты согревала его после метели.', 'Зимним вечером на ферме.', condition=MARRIED),
    ]),
]

GROUPS = {'base': {}, 'trauma': {}, 'adult': {}}
for arc_order, (arc, group, entries) in enumerate(ARCS, start=1):
    for order, entry in enumerate(entries, start=1):
        first_id = entry['EventIds'].split()[0].replace('{{ModId}}_', '')
        GROUPS[group][f'{{{{ModId}}}}_{first_id}'] = {'Arc': arc, 'ArcOrder': arc_order, 'Order': order, **entry}

TARGET = 'Mods/marilynsinister.HarveyOverhaul/StoryJournal'
data = {'Changes': [
    {'LogName': 'Story journal — сцены (вкладка «История» в окне Харви)', 'Action': 'EditData', 'Target': TARGET,
     'Entries': GROUPS['base']},
    {'LogName': 'Story journal — прошлое и «Шрамы» (TraumaBackstory)', 'Action': 'EditData', 'Target': TARGET,
     'Entries': GROUPS['trauma'], 'When': {'TraumaBackstory': 'true'}},
    {'LogName': 'Story journal — 18+ (AdultEvents)', 'Action': 'EditData', 'Target': TARGET,
     'Entries': GROUPS['adult'], 'When': {'AdultEvents': 'true'}},
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, sum(len(g) for g in GROUPS.values()), 'entries')
