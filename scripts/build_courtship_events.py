"""Генерирует assets/Code/eventsCourtship.json — помолвка и свадьба (docs/romance-proposal.md, блок P).

  P1 «Ты опять меня опередила»  Town SVE у клиники, 9:00–15:00, Engaged — его предложение «второй раз».
  P2 «Анкета невесты»           Hospital, регистратура, 9:00–15:00, Engaged, после P1 — цветы, страх, желание.
  P3 «Мандраж»                  Farm, крыльцо, 22:00–2:00, канун свадьбы — речь у алтаря, сказанная ей одной.
  P3b «Благословение»           HarveyRoom, 12:00–15:00, канун свадьбы, только с Арендом (ArendEnabled).
  Ещё P1 даёт флаги HarveyMemory_Ring_* — по ним Core описывает сувенир «Коробочка от кольца» (build_family_life.py).
  P4 «Первое утро»              FarmHouse, 6:00–9:00, первое утро брака — цветы из анкеты P2. Мост к M1.

Флаги помолвки ставит HarveyOverhaulCore (Services/HarveyMarriageMilestones.cs) каждое утро:
  HarveyRomance_Engaged, HarveyRomance_WeddingEve, HarveyRomance_FirstMorning (и HarveyRomance_TwoYears для W4).
Помолвка в ванили длится 3 дня, поэтому сцены P без глобального кулдауна (cooldown=False).

Тайлы:
  Town SVE — у двери клиники 34–38,58 (36,57 и 37–41,58 проверены в romance-proposal.md §2).
  Hospital — регистратура 10,14 · 10,16 · вход 10,19, как N3 в build_arc3_events.py.
  Farm — токены HO_FarmX/HO_FarmY*, как в build_marriage_events.py.
  FarmHouse — координаты дома ур. 1 (как A2 в build_family_life.py); в браке дом не ниже ур. 1.
Запуск:  python scripts/build_courtship_events.py
"""
import json
import os

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'eventsCourtship.json')

NS = 'HarveyOverhaulCourtship'
ENGAGED = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Engaged'
MARRIED = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married'
FX, FY0, FY1, FY3 = '{{HO_FarmX}}', '{{HO_FarmY0}}', '{{HO_FarmY1}}', '{{HO_FarmY3}}'


def flag(name):
    return f'action AddMail Current {name} Received'


def has(name):
    return f'GameStateQuery PLAYER_HAS_MAIL Current {name} Received'


def seen(eid):
    return f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}'


# ---------------------------------------------------------------- P1
p1_key = key(NS, 'P1_SecondAsk', 'Time 0900 1500', ENGAGED, cooldown=False)
p1 = script(
    'harveys_theme_jazz', '37 57', 'farmer 34 58 1 Harvey 38 58 3',
    skip_cd('AddConversationTopic HarveyRomance_Proposal 3', 'AddMail Current HarveyRomance_Ring Received'),
    [
        'viewport 37 57 true', 'pause 500',
        msg('У двери клиники Харви ходит туда-сюда и то и дело хлопает себя по карману пальто.'),
        'move farmer 3 0 1', 'emote Harvey 16',
        sp(H, 'Ты. Уже. Здесь.$u#$b#Я хотел прийти к тебе на ферму. С речью. Речь, между прочим, была хорошая.$a'),
        msg('Он достаёт из кармана маленькую бархатную коробочку. Уголки у неё потёрты — её явно долго носили с собой.'),
        sp(H, 'Я купил его в Зузу, ещё весной. Ждал правильного дня. А потом ты пришла с кулоном — и опередила меня.$s'),
        sp(H, 'Опять. Ты опять меня опередила. Это становится системой.$h'),
        sp(H, 'Так что позволь хотя бы спросить красиво. Второй раз — для меня.$l'),
        msg('Харви опускается на одно колено прямо на мостовой. Из-за угла выглядывает Мару — и тут же прячется обратно.'),
        sp(H, 'Ты выйдешь за меня? Я буду невыносимым мужем. Буду проверять, завтракала ли ты, и греть тебе руки.$l#$b#Всю жизнь, если позволишь.$l'),
        qq(['Да. Снова да.', 'Встань, все смотрят!', 'Надень мне его сам'], [
            [msg('Он выдыхает так, будто всё это время задерживал дыхание.'),
             sp(H, 'Второе «да» звучит ещё лучше первого. Запомню оба.$l'),
             flag('HarveyMemory_Ring_Yes'), 'friendship Harvey 40'],
            ['emote farmer 28',
             sp(H, 'Пусть смотрят. Пусть весь Пеликан-Таун знает.$h#$b#…Но встать я, пожалуй, встану. Мостовая холодная.$h'),
             flag('HarveyMemory_Ring_Stand'), 'friendship Harvey 35'],
            [msg('Ты протягиваешь руку. Пальцы у него дрожат — у человека, который зашивает раны не моргнув.'),
             msg('Кольцо садится как влитое.'),
             sp(H, 'Размер я снял с твоей перчатки. Прости. Врачебная привычка — всё измерять.$l'),
             flag('HarveyMemory_Ring_HePutOn'), 'friendship Harvey 45'],
        ]),
        'pause 400',
        sp(H, 'Три дня до свадьбы. Я составил список дел. Пункт первый — ты высыпаешься. Пункт второй — тоже ты высыпаешься.$a#$b#Пункт третий я пока не придумал. Но придумаю.$h'),
        flag('HarveyRomance_Ring'),
        'addConversationTopic HarveyRomance_Proposal 3',
    ])

# ---------------------------------------------------------------- P2
FLOWERS = [('Tulip', 'Тюльпаны'), ('Sunflower', 'Подсолнухи'), ('SweetPea', 'Душистый горошек')]
FEARS = [('Height', 'Высоты'), ('Dark', 'Темноты'), ('Alone', 'Остаться одной')]
WISHES = [('Dance', 'Танцевать'), ('Stars', 'Смотреть на звёзды'), ('Quiet', 'Просто тишины')]

p2_key = key(NS, 'P2_BrideChart', 'Time 0900 1500', ENGAGED, seen('P1_SecondAsk'), cooldown=False)
p2 = script(
    'Hospital_Ambient', '10 15', 'Harvey 10 14 2 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyRomance_Questionnaire 3'),
    [
        'viewport 10 15 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -3 0', 'pause 400',
        'emote Harvey 32',
        sp(H, 'А, невеста. Садись. У меня к тебе официальное дело.$h'),
        msg('Он кладёт на стойку бланк. Сверху его почерком: «Медицинская карта невесты. Строго конфиденциально».'),
        sp(H, 'Я понял, что знаю твою группу крови, но не знаю, какие цветы ты любишь. Это врачебная ошибка. Исправляю.$a'),
        sp(H, 'Вопрос первый. Какие цветы ты хочешь видеть в доме?$0'),
        qq([name for _, name in FLOWERS], [
            [flag(f'HarveyRomance_Flower_{fid}'), sp(H, f'{name}. Записал. Подчеркнул дважды.$h')]
            for fid, name in FLOWERS
        ]),
        sp(H, 'Вопрос второй. Это серьёзно, не смейся. Чего ты боишься?$s'),
        qq([name for _, name in FEARS], [
            [flag('HarveyRomance_Fear_Height'),
             sp(H, 'Высоты. Значит, лестницы в сарае теперь мои. И крыша. И ветки яблони.$a#$b#Не спорь, это уже в карте.$h')],
            [flag('HarveyRomance_Fear_Dark'),
             sp(H, 'Темноты. Хорошо. В доме будет ночник. Не детский — просто тёплый.$l#$b#И я рядом, если он погаснет.$l')],
            [flag('HarveyRomance_Fear_Alone'),
             msg('Харви долго не пишет. Потом откладывает ручку.'),
             sp(H, 'Этот пункт я лечу просто. Я никуда не денусь.$l')],
        ]),
        sp(H, 'И последний. Тайное желание. Что-то, чего тебе хочется, но ты никогда не просишь.$l'),
        qq([name for _, name in WISHES], [
            [flag('HarveyRomance_Wish_Dance'),
             sp(H, 'Танцевать. Я танцую как заржавевший аппарат ИВЛ. Но я научусь.$h')],
            [flag('HarveyRomance_Wish_Stars'),
             sp(H, 'Звёзды. У меня есть старая карта неба, ещё со студенчества. Найду.$l')],
            [flag('HarveyRomance_Wish_Quiet'),
             sp(H, 'Тишины. Понимаю. Иногда лучшее лекарство — когда никто ничего не спрашивает.$l#$b#…Кроме меня. Я всё равно спрошу, завтракала ли ты.$h')],
        ]),
        msg('Он аккуратно складывает бланк вчетверо и убирает во внутренний карман, к сердцу.'),
        sp(H, 'Карта закрыта. Диагноз: невеста. Прогноз — отличный.$l'),
        'friendship Harvey 30',
        'addConversationTopic HarveyRomance_Questionnaire 3',
    ])

# ---------------------------------------------------------------- P3
p3_key = key(NS, 'P3_Jitters', 'Time 2200 2600', ENGAGED, has('HarveyRomance_WeddingEve'), cooldown=False)
p3 = script(
    'none', f'{FX} {FY0}', f'farmer {FX} {FY1} 2 Harvey {FX} {FY3} 0',
    skip_cd('AddConversationTopic HarveyRomance_Jitters 2'),
    [
        'pause 800',
        msg('Ночь перед свадьбой. У крыльца стоит Харви — без пальто, с растрёпанными волосами.'),
        sp(H, 'Я не передумал. Сразу говорю, чтобы ты не испугалась.$u'),
        sp(H, 'Просто не могу уснуть. Хотел проверить, что ты есть. Что всё это — правда.$s'),
        'emote farmer 8',
        sp(H, 'Смешно, да? В операционной у меня руки не дрожат. А от мысли о речи у алтаря — дрожат.$s'),
        sp(H, 'Я написал шесть вариантов. Все ужасные. В одном я случайно процитировал справочник по кардиологии.$h'),
        qq(['Попросить сказать речь сейчас', 'Отправить его спать', 'Сесть рядом на ступеньку молча'], [
            [sp(H, 'Сейчас? Тебе? …Ладно. Это даже легче.$u'),
             'pause 600',
             sp(H, 'Я долго думал, что моя работа — держать всех. Не отпускать. Следить, чтобы никто не упал.$s'),
             sp(H, 'А потом появилась ты. Ты падала, поднималась, приходила ко мне в пыли из шахт — и держала меня.$l'),
             sp(H, 'Я не обещаю, что перестану волноваться. Я обещаю волноваться рядом. Всю жизнь.$l'),
             msg('Он замолкает. Тишину нарушают только сверчки.'),
             sp(H, '…Это было седьмое. Кажется, его я и скажу.$l'),
             'friendship Harvey 40'],
            ['emote farmer 12',
             sp(H, 'Слушаюсь. Ты уже главная.$h'),
             msg('Он подчиняется подозрительно легко, но у калитки оборачивается.'),
             sp(H, 'До завтра. Высыпайся. Это пункт первый, помнишь?$l'),
             'friendship Harvey 30'],
            [msg('Ты садишься на ступеньку. Он — рядом. Плечо к плечу.'),
             msg('Вы долго смотрите на тёмное поле. Постепенно его дыхание становится ровным.'),
             sp(H, 'Вот. Пульс шестьдесят. Ты лучше любого успокоительного.$l'),
             'friendship Harvey 35'],
        ]),
        sp(H, 'Завтра я буду стоять у алтаря и ждать тебя. И, честно, я буду ждать столько, сколько нужно.$l'),
        'addConversationTopic HarveyRomance_Jitters 2',
    ])

# ---------------------------------------------------------------- P3b (только с Арендом)
A = 'Arend'
p3b_key = key(NS, 'P3b_Blessing', 'Time 1200 1500', ENGAGED, has('HarveyRomance_WeddingEve'),
              'GameStateQuery PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulArend.A1_Arrival', cooldown=False)
p3b = script(
    'none', '7 9', 'farmer 7 9 1 Arend 8 9 3 Harvey -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyRomance_Blessing 3', 'AddFriendshipPoints Arend 40'),
    [
        'viewport 7 9 true', 'pause 500',
        msg('Комната Харви наверху. Аренд позвал тебя «на два слова». Очки у него на лбу, в руках — листок, исписанный красным карандашом.'),
        sp(A, 'Дитя. Садись. Я… подготовился.$0'),
        sp(A, 'Сорок лет я говорю с людьми о самом трудном. А тут написал три страницы — и все про сердечно-сосудистую систему. Видимо, это у нас семейное.$h'),
        msg('Он складывает листок и убирает его в карман. Долго молчит.'),
        sp(A, 'Можно я спрошу, а не скажу? Так мне привычнее.$0'),
        sp(A, 'Тебе с ним спокойно?$0'),
        qq(['Да. Очень.', 'Иногда он слишком волнуется', 'Спокойнее, чем с кем-либо'], [
            [sp(A, 'Хорошо. Это главное. Остальному можно научиться.$l'), 'friendship Arend 30'],
            [sp(A, 'Знаю. Это он у меня взял — я тоже не спал, когда он был маленьким.$s'),
             sp(A, 'Но он научился спрашивать, а не только тревожиться. Я видел. Это ты его научила, дитя.$l'),
             'friendship Arend 40'],
            [msg('Аренд снимает очки и долго протирает их краем свитера.'),
             sp(A, 'Элин сказала бы про тебя то же самое. Она умела выбирать людей. Харви, видимо, тоже.$s'),
             'friendship Arend 40'],
        ]),
        sp(A, 'Тогда вот моё благословение. Короткое, потому что длинное я испортил.$0'),
        sp(A, 'Берегите друг друга. И разрешайте друг другу беречь себя. Второе труднее.$l'),
        'playSound doorClose', 'warp Harvey 6 12', 'move Harvey 0 -2 0', 'move Harvey 1 0 0',
        'faceDirection farmer 2', 'faceDirection Arend 3', 'emote Harvey 16',
        sp(H, 'Пап. Ты обещал не устраивать речей до завтра.$a'),
        sp(A, 'Я и не устроил, сын. Я задал один вопрос. Профессиональная деформация.$h'),
        msg('Харви смотрит на тебя, потом на отца. Уши у него краснеют.'),
        sp(H, '…Что она ответила?$s'),
        sp(A, 'Врачебная тайна.$h'),
        'friendship Arend 40',
        'addConversationTopic HarveyRomance_Blessing 3',
    ])

# ---------------------------------------------------------------- P4
P4_FLOWERS = {
    'Tulip': 'На подоконнике — тюльпаны. Целое ведро. Похоже, весь запас Пьера.',
    'Sunflower': 'На подоконнике — подсолнухи. Огромные, тяжёлые, повёрнутые к окну.',
    'SweetPea': 'На подоконнике — душистый горошек в банке из-под пикулей. В доме пахнет летом.',
}
P4_FALLBACK = 'На подоконнике — букет полевых цветов. Кажется, он собрал их сам на рассвете.'


def p4_body(flowers_line):
    return [
        'pause 600',
        msg('Первое утро. Харви проснулся раньше тебя и стоит у окна — в рубашке, босиком, будто не знает, куда себя деть.'),
        msg(flowers_line),
        sp(H, 'Доброе утро, жена.$l#$b#…Я тренировался это говорить. Звучит лучше, чем я думал.$h'),
        sp(H, 'Я привык просыпаться от будильника клиники. А тут — петух и ты.$h#$b#Второе мне нравится больше.$l'),
        sp(H, 'Я не знаю, где у тебя лежат ложки. Я не знаю, какая чашка твоя. Я впервые за много лет не знаю, что делать.$s'),
        qq(['Показать ему дом', 'Отдать ему свою чашку', 'Утянуть его обратно под одеяло'], [
            [msg('Ты водишь его по дому: вот ложки, вот чай, вот ящик, куда всё прячется.'),
             sp(H, 'Записываю. Ложки — второй ящик. Аптечку я, если позволишь, повешу сюда, на видное место.$a'),
             sp(H, 'Теперь это наш дом. Звучит как диагноз. Хороший.$l'),
             'friendship Harvey 30'],
            [msg('Ты молча протягиваешь ему свою кружку.'),
             sp(H, 'Твоя? …Значит, теперь она наша. Как и всё остальное.$l'),
             'friendship Harvey 30'],
            [msg('Ты берёшь его за руку и тянешь обратно.'),
             sp(H, 'Режим дня. Куры. Грядки…$u#$b#А, ладно. Первое утро бывает один раз.$l'),
             'friendship Harvey 35'],
        ]),
        sp(H, 'Завтра у меня первая смена после свадьбы. Сегодня — нет. Сегодня я просто твой.$l'),
        'addConversationTopic HarveyRomance_NewHome 3',
    ]


P4_COMMON = ('Time 0600 0900', MARRIED, has('HarveyRomance_FirstMorning'),
             'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulMarriage.M1_FirstShift')


def p4_event(eid, conds, flowers_line):
    k = key(NS, eid, *P4_COMMON, *conds, cooldown=False)
    v = script('harveys_theme_jazz', '12 7', 'farmer 11 7 1 Harvey 13 7 3',
               skip_cd('AddConversationTopic HarveyRomance_NewHome 3'), p4_body(flowers_line))
    return k, v


p4 = dict(p4_event(f'P4_FirstMarriedMorning_{fid}', [has(f'HarveyRomance_Flower_{fid}')], line)
          for fid, line in P4_FLOWERS.items())
p4.update([p4_event('P4_FirstMarriedMorning', [f'GameStateQuery !PLAYER_HAS_MAIL Current HarveyRomance_Flower_{fid} Received'
                                        for fid in P4_FLOWERS], P4_FALLBACK)])

# ---------------------------------------------------------------- реплики на темы
topics = {
    'HarveyRomance_Proposal': 'Рука всё ещё тянется к карману, где полгода лежала коробочка. Привычка.$h#$b#Потом вспоминаю, что ты сказала «да». Дважды.$l',
    'HarveyRomance_Questionnaire': 'Твоя анкета лежит у меня во внутреннем кармане.$l#$b#Мару спросила, что там. Я сказал: «Врачебная тайна».$h',
    'HarveyRomance_Jitters': 'Седьмой вариант речи я выучил наизусть. Остальные шесть сжёг в камине.$h#$b#Спасибо, что выслушала. Ты была моей первой и единственной репетицией.$l',
    'HarveyRomance_NewHome': 'Ложки — второй ящик. Чай — над плитой. Аптечка — у двери.$a#$b#Я изучаю наш дом, как новую больницу. Только здесь мне нравится каждый угол.$l',
}

data = {'Changes': [
    patch('Courtship P1 — «Ты опять меня опередила» (Town SVE, Engaged)', 'Data/Events/Town', {p1_key: p1}),
    patch('Courtship P2 — «Анкета невесты» (Hospital, Engaged)', 'Data/Events/Hospital', {p2_key: p2}),
    patch('Courtship P3 — «Мандраж» (Farm, канун свадьбы)', 'Data/Events/Farm', {p3_key: p3}),
    patch('Courtship P4 — «Первое утро» (FarmHouse, первое утро брака)', 'Data/Events/FarmHouse', p4),
    {**patch('Courtship — реплики Харви на темы помолвки', 'Characters/Dialogue/Harvey', topics),
     'Priority': 'Late', 'When': {'Relationship:Harvey': 'Engaged, Married'}},
    {**patch('Courtship P3b — благословение Аренда (HarveyRoom, канун свадьбы)', 'Data/Events/HarveyRoom',
             {p3b_key: p3b}), 'When': {'ArendEnabled': 'true'}},
    {**patch('Courtship P3b — Харви и Аренд после благословения', 'Characters/Dialogue/Harvey', {
        'HarveyRomance_Blessing': 'Папа так и не сказал, что ты ответила. Я спрашивал трижды.$a#$b#…Ладно. Судя по его лицу, что-то хорошее.$l',
    }), 'Priority': 'Late', 'When': {'ArendEnabled': 'true', 'Relationship:Harvey': 'Engaged, Married'}},
    {**patch('Courtship P3b — Аренд после благословения', 'Characters/Dialogue/Arend', {
        'HarveyRomance_Blessing': 'Три страницы про сердечно-сосудистую систему я сохранил. Прочту на вашей серебряной свадьбе.$h',
    }), 'Priority': 'Late', 'When': {'ArendEnabled': 'true'}},
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, sum(len(c['Entries']) for c in data['Changes'] if c['Target'].startswith('Data/Events/')), 'events')
