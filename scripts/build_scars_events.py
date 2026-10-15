"""Генерирует assets/Code/eventsScars.json — арка «Шрамы» (прошлое фермерши, TraumaBackstory).

Идея арки: фермерша не обязана рассказывать, а Харви не обязан спасать. Он учится не лечить её прошлое,
а быть рядом, пока она сама решает, что с ним делать. План — docs/story-captivity-arc-proposal.md §4.2.

  C1 «Длинные рукава»        Town SVE, фонтан, лето, полдень       4♥, после TraumaExam или RescueOperation
  C2 «Хлопок»                Town SVE, крыльцо салуна, вечер       5♥, 2-й год (Кент), после C1
  C3 «Мазь для рубцов»       Hospital, палата A, осень/зима        доверие ≥ TrustedDoctor (флаг StressMeter), после C1
  C4 «Письмо из Зузу»        Hospital, после письма министерства   7♥, после C3 → выбор: отправить / сжечь / оставить
  C6 «Чужой в Долине»        BusStop SVE                           8♥, 2-й год, после C4
  C7 «Рукава закатаны»       Beach SVE, лето                       Dating, после C6
  C8 «Карта, которую не пишут» Farm, крыльцо, вечер                Married, после C7; ответ на письмо — по выбору в C4
  (C5 «Что я помню» сделана раньше как T1/T2 — eventsTraumaBackstory.json.)

Механика (C#): рубцы на холоде + мазь — HarveyOverhaulInjury/Managers/ScarCareManager.cs;
огонь как триггер — HarveyStressMeter/Services/FireMemoryService.cs (флаг HarveyBackstory_FireKnown ставит T1).
Весь файл подключается только при TraumaBackstory = true (кроме снятия флага HarveyScars_Enabled).

Тайлы (scripts/validate_event_coords.py): Town — фонтан 24–28 × 25–28, площадь 21–31 × 29–35;
крыльцо салуна 41–48 × 72–75 (дверь 45,70); BusStop 16–28 × 22–25; Beach 38–46 × 17–24;
Hospital — палата A 14,6 / 15,6 и стол 10,14 (вход 10,19). Farm — токены HO_FarmX/Y.
Запуск:  python scripts/build_scars_events.py
"""
import json
import os

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'eventsScars.json')

NS = 'HarveyOverhaulScars'
SALVE = '(O)marilynsinister.HarveyOverhaul_ScarSalve'
STOP = 'action marilynsinister.HarveyStressMeter_ExamStopRespected'
YEAR2 = 'GameStateQuery YEAR 2'
TRAUMA_SEEN = ('GameStateQuery ANY "PLAYER_HAS_SEEN_EVENT Current eventHarveyTraumaExam" '
               '"PLAYER_HAS_SEEN_EVENT Current eventRescueOperation"')
FX, FY0, FY1, FY2 = '{{HO_FarmX}}', '{{HO_FarmY0}}', '{{HO_FarmY1}}', '{{HO_FarmY2}}'


def seen(eid):
    return f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}'


# ---------------------------------------------------------------- C1
c1_key = key(NS, 'C1_LongSleeves', 'Season Summer', 'Weather Sunny', 'Time 1200 1600',
             'Friendship Harvey 1000', TRAUMA_SEEN)
c1 = script(
    'continue', '26 29', 'farmer 25 29 2 Harvey 26 34 0 Gus 29 30 3',
    skip_cd('AddConversationTopic HarveyScars_Sleeves 3'),
    [
        'viewport 26 29 true', 'pause 500',
        msg('Полдень. Над площадью дрожит воздух, и даже фонтан не спасает. Ты сидишь на бортике — в рубашке с длинными рукавами.'),
        sp('Gus', 'Ну и пекло. Даже лимонад, кажется, закипает.$h'),
        msg('Через площадь идёт Харви с деревянным ящиком. Звенят бутылки.'),
        'move Harvey 0 -5 0',
        sp(H, 'Гас, это для всех. Холодная вода. Мару говорит, у нас сегодня рекорд по солнечным ударам.$0'),
        sp('Gus', 'Доктор, вы святой. Беру две.$h'),
        'faceDirection Harvey 3', 'faceDirection farmer 1',
        msg('Харви ставит рядом с тобой бутылку. Потом достаёт из сумки свёрнутое полотенце — мокрое, холодное.'),
        sp(H, 'Компресс. На шею, не на лицо — так быстрее остывает кровь. Я раздаю их всем, так что не спорь.$0'),
        msg('Он не смотрит на твои рукава. Ни разу.'),
        qq(['Взять компресс', '«Всем — правда?»', 'Потянуть манжету ниже'], [
            [msg('Холод ложится на шею, и дышать становится легче.'),
             sp(H, 'Вот. Через пять минут почувствуешь разницу. А ещё через пять — тень под липой.$h'),
             'friendship Harvey 25'],
            [sp(H, 'Всем. У меня ещё четыре полотенца и Пэм, которая будет спорить.$h'),
             sp(H, '…Ладно, тебе первой. Ты сидела ближе всех к солнцу.$0'),
             'friendship Harvey 25'],
            [msg('Ты тянешь рукав ниже, хотя ниже уже некуда.'), 'pause 600',
             sp(H, 'Тень вон там, под липой. И оттуда никто не смотрит. Даже я. Особенно я.$s'),
             'friendship Harvey 30'],
        ]),
        sp(H, 'Пей маленькими глотками. Закружится голова — клиника открыта, дверь не тяжёлая.$0'),
        'move Harvey 0 3 2',
        msg('Он уходит раздавать воду дальше. О рукавах — ни слова.'),
        'addConversationTopic HarveyScars_Sleeves 3',
    ])

# ---------------------------------------------------------------- C2
c2_key = key(NS, 'C2_Pop', 'Weather Sunny', 'Time 1900 2300', 'Friendship Harvey 1250', YEAR2, seen('C1_LongSleeves'))
c2 = script(
    'none', '44 73', 'farmer 44 74 0 Gus 45 72 2 Kent 47 74 3 Harvey 41 74 1',
    skip_cd('AddConversationTopic HarveyScars_Pop 3'),
    [
        'viewport 44 73 true', 'pause 500',
        msg('Вечер у салуна. Гас выкатил на крыльцо бочонок нового сидра и ящик бутылок — праздник урожая в миниатюре.'),
        sp('Gus', 'Первая бутылка — за счёт заведения! Осторожно, он игристый!$h'),
        'pause 600', 'playSound Cowboy_gunshot', 'jump farmer 6', 'faceDirection farmer 2',
        msg('Хлопок. Ты не успеваешь подумать — ты уже у ступенек, на корточках, руки над головой.'),
        'pause 600', 'emote Harvey 16',
        msg('Харви делает шаг — но Кент оказывается рядом раньше.'),
        'move Kent -2 0 3',
        sp('Kent', 'Эй. Я здесь. Не трогаю.$s'),
        sp('Kent', 'Считаем вместе. Раз — это пробка. Два — это Гас со своим сидром. Три — под ногами доски, а не… не то. Четыре.$s'),
        msg('Он сидит рядом на корточках и считает. Ровно, спокойно — так, будто делал это сотню раз.'),
        'pause 800',
        msg('Харви стоит в двух шагах. Кулаки сжаты. Он не подходит.'),
        sp('Kent', 'Пять. Видишь фонари? Назови три.$0'),
        qq(['Назвать фонари', 'Найти глазами Харви', 'Молча кивнуть'], [
            [msg('Голос дрожит, но ты называешь: над дверью, у бочонка, у моста.'),
             sp('Kent', 'Вот. Ты здесь. Это Пеликан-таун, а не там.$h'),
             'friendship Kent 30'],
            [msg('Ты ищешь Харви. Он ловит твой взгляд — и просто кивает: я тут.'),
             'friendship Harvey 30'],
            ['emote farmer 40',
             sp('Kent', 'Кивок засчитан. Говорить не обязательно.$0'),
             'friendship Kent 20'],
        ]),
        'pause 500', 'move Harvey 2 0 1',
        sp(H, 'Спасибо, Кент.$s'),
        sp('Kent', 'Я два года нырял под стол, док. После войны любой хлопок был выстрелом.$0#$b#Счёт помогает. И чтобы кто-то сидел рядом и ничего не чинил.$s'),
        sp(H, 'Меня учили, что помочь — значит сделать. Наложить, зашить, назначить.$s'),
        sp('Kent', 'А иногда помочь — это сесть на пол. Я не врач. Я просто помню.$0'),
        sp(H, '…Я тоже запомню.$0'),
        msg('Гас тихо уносит сидр внутрь. Никто ничего не говорит.'),
        'faceDirection Harvey 1',
        sp(H, 'Пойдём, провожу. Молча, если хочешь. Я неплохо умею молчать, когда стараюсь.$s'),
        'addConversationTopic HarveyScars_Pop 3',
    ])

# ---------------------------------------------------------------- C3
c3_key = key(NS, 'C3_ScarSalve', 'Season Fall Winter', 'Time 0900 1500', 'Friendship Harvey 1000',
             'GameStateQuery PLAYER_HAS_MAIL Current HarveyCareTrust_L2 Received', seen('C1_LongSleeves'))
c3 = script(
    'Hospital_Ambient', '14 6', 'farmer 14 6 1 Harvey 15 6 3',
    skip_cd('AddConversationTopic HarveyScars_Salve 3', f'AddItem {SALVE} 3'),
    [
        'viewport 14 6 true', 'pause 500',
        msg('Палата пустая. На тумбочке — маленькая жестяная банка, подписанная его ужасным почерком.'),
        sp(H, 'Холода начинаются. Я заметил, как ты держишь руки у кружки. Не греешь — растягиваешь пальцы.$s'),
        sp(H, 'Старые ожоги на морозе стягивает. Кожа на рубцах не тянется, как раньше.$0#$b#Это не слабость. Это кожа помнит огонь.$s'),
        sp(H, 'Я сделал мазь. Календула, воск, немного масла. Никакого запаха дыма — проверил трижды.$0'),
        'pause 400',
        sp(H, 'Один вопрос. Сама — или мне можно? Любой ответ правильный.$s'),
        qq(['«Я сама»', '«Можно. Только говори, что делаешь»', '«Не сегодня»'], [
            [msg('Он отдаёт тебе банку и отходит на шаг, чтобы не стоять над душой.'),
             sp(H, 'Тонким слоем, от запястья к локтю. Утром, перед тем как выйти на холод.$0'),
             sp(H, 'Если защиплет — значит, кожа трескалась. Тогда приходи, посмотрим вместе.$s'),
             'friendship Harvey 30'],
            [sp(H, 'Хорошо. Беру твою левую руку. Только запястье.$0'),
             msg('Его пальцы тёплые и очень медленные. Он проговаривает каждое движение, будто читает инструкцию самому себе.'),
             sp(H, 'Запястье. Теперь чуть выше. Здесь рубец плотнее — я не давлю. Скажи «стоп» в любой момент.$s'),
             msg('Ты не говоришь «стоп».'),
             sp(H, '…Спасибо, что доверила.$s'),
             'friendship Harvey 45'],
            [STOP,
             sp(H, 'Не сегодня — значит не сегодня.$0'),
             msg('Он ставит банку на край тумбочки, ближе к тебе, и убирает руки за спину.'),
             sp(H, 'Она твоя. Когда захочешь — сама или со мной. Второй раз спрашивать не буду, пока не спросишь ты.$s'),
             'friendship Harvey 35'],
        ]),
        sp(H, 'Вот ещё две, в запас. Зимой рубцы будут напоминать о себе. Мазь — на весь день. Закончится — у меня на полке есть ещё.$0'),
        f'addItem {SALVE} 3',
        'addConversationTopic HarveyScars_Salve 3',
    ])

# ---------------------------------------------------------------- C4
c4_key = key(NS, 'C4_ZuzuLetter', 'Time 0900 1500', 'Friendship Harvey 1750',
             'GameStateQuery PLAYER_HAS_MAIL Current HarveyScars_VeteransLetter Received', seen('C3_ScarSalve'))
c4 = script(
    'Hospital_Ambient', '10 15', 'Harvey 10 14 2 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyScars_Letter 3', 'AddMail Current HarveyScars_LetterKept Received'),
    [
        'viewport 10 15 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -3 0', 'pause 300',
        msg('Ты кладёшь на стол конверт с печатью Республики Ферн. Харви узнаёт её сразу.'),
        sp(H, 'Министерство по делам ветеранов. В Зузу такие приносили в ординаторскую пачками.$s'),
        sp(H, 'Можно прочитать? Только если хочешь.$0'),
        'pause 800',
        msg('Он читает долго. Потом аккуратно складывает письмо по старым сгибам.'),
        sp(H, 'Им нужно медицинское заключение. Ожоги, давность, характер повреждений. Я могу его написать.$0#$b#Могу — но не обязан. И ты не обязана его отправлять.$s'),
        sp(H, 'Это не экзамен и не долг. Компенсация — да. Но это ещё и бумага, где чужие люди прочитают про твои руки.$s'),
        qq(['«Напиши. Я отправлю»', '«Сожги его»', '«Положу в ящик. Потом решу»'], [
            [sp(H, 'Хорошо. Напишу сегодня. Сухо, по-врачебному — ни одного лишнего слова о тебе.$0'),
             sp(H, 'И покажу тебе перед тем, как запечатать. Каждую строчку.$s'),
             'action AddMail Current HarveyScars_LetterSent Received',
             'friendship Harvey 30'],
            [sp(H, 'Сожгу. Сам, вечером, во дворе — без тебя. Тебе не нужно на это смотреть.$s'),
             msg('Он убирает конверт во внутренний карман — подальше от твоих глаз.'),
             sp(H, 'Не все долги надо платить бумагой. Этот — точно нет.$0'),
             'action AddMail Current HarveyScars_LetterBurned Received',
             'friendship Harvey 30'],
            [msg('Ты убираешь конверт обратно в сумку.'),
             sp(H, 'Правильно. У решений нет срока годности. Надумаешь — заключение будет готово за вечер.$0'),
             'action AddMail Current HarveyScars_LetterKept Received',
             'friendship Harvey 25'],
        ]),
        sp(H, 'Спасибо, что принесла это мне. Ты ведь могла никому не показывать.$s'),
        'addConversationTopic HarveyScars_Letter 3',
    ])

# ---------------------------------------------------------------- C6
c6_key = key(NS, 'C6_Stranger', 'Weather Sunny', 'Time 1000 1600', 'Friendship Harvey 2000', YEAR2,
             seen('C4_ZuzuLetter'))
c6 = script(
    'continue', '22 22', 'farmer 20 23 1 Harvey 21 22 2 Kent 26 23 3',
    skip_cd('AddConversationTopic HarveyScars_Stranger 3'),
    [
        'viewport 22 22 true', 'pause 500',
        msg('Остановка. Ты ждёшь посылку из города, Харви — коробку лекарств. Чуть поодаль переминается Кент.'),
        sp(H, 'Если Пэм опять опоздает, начну выписывать ей рецепты на пунктуальность.$h'),
        'playSound doorClose',
        msg('Двери автобуса открываются. Выходит мужчина в выцветшей полевой форме. Нашивки Республики, тяжёлые ботинки.'),
        'pause 600', 'emote Harvey 16', 'move Harvey 0 1 1',
        sp(H, 'Стой за мной.$a'),
        msg('Он говорит это тихо и очень твёрдо. Плечи напряжены — как перед дракой, в которой он ни разу в жизни не был.'),
        'pause 800',
        sp('Kent', 'Рик! Чёрт возьми, всё-таки доехал!$h'),
        msg('Кент обнимает незнакомца так, что скрипят ремни рюкзака. Они смеются и хлопают друг друга по спине.'),
        sp('Kent', 'Док, знакомься: Рик. Сидели в одной траншее. Приехал на выходные — Джоди обещала пирог с ревенем.$h'),
        'pause 600', 'faceDirection Harvey 3',
        msg('Харви медленно разжимает кулаки. Уши у него красные.'),
        sp(H, '…Я встал между тобой и форменной курткой. Как будто куртка может кого-то обидеть.$s'),
        sp(H, 'Я обещал себе, что они сюда не дотянутся. Те, из твоего прошлого.$s#$b#А в итоге чуть не воевал с другом Кента. Я воевал не с тем.$s'),
        qq(['«Ты меня защищал»', 'Тронуть его за локоть', 'Рассмеяться — от облегчения'], [
            [sp(H, 'Защищал. От пирога с ревенем и ветерана с открыткой.$u'),
             sp(H, '…Но да. Будь это кто-то другой — я стоял бы так же.$s'),
             'friendship Harvey 30'],
            [msg('Ты касаешься его локтя. Он выдыхает — будто держал воздух с самого утра.'),
             sp(H, 'Спасибо. Сейчас ты успокаиваешь меня. Мы поменялись местами.$s'),
             'friendship Harvey 35'],
            [msg('Ты смеёшься — нервно, громко, до слёз. Через секунду не выдерживает и Харви.'),
             sp(H, 'Хорош защитник. Чуть не устроил дуэль на автобусной остановке.$h'),
             'friendship Harvey 30'],
        ]),
        sp(H, 'Защищать — не значит воевать. Пора бы мне это выучить. Защищать — это быть рядом, когда страшно, а не искать, с кем драться.$0'),
        sp('Kent', 'Док! Иди сюда, Рик спрашивает, нет ли у тебя чего-нибудь для колена.$h'),
        sp(H, '…Видишь? Даже те, кого я принял за врагов, приходят ко мне с коленями.$h'),
        'addConversationTopic HarveyScars_Stranger 3',
    ])

# ---------------------------------------------------------------- C7
c7_key = key(NS, 'C7_SleevesUp', 'Season Summer', 'Weather Sunny', 'Time 1100 1700', 'Friendship Harvey 2500',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating Married', seen('C6_Stranger'))
c7 = script(
    'continue', '40 20', 'farmer 40 21 2 Harvey 41 21 2 Sam 44 19 2 Haley 37 20 1',
    skip_cd('AddConversationTopic HarveyScars_SleevesUp 3'),
    [
        'viewport 40 20 true', 'pause 500',
        msg('Жаркий день на пляже. Полгорода у воды. Ты сидишь на песке — рукава, как всегда, до запястий.'),
        sp(H, 'Тридцать один в тени. Я не скажу ничего медицинского. Просто констатирую.$h'),
        'pause 800',
        msg('Ты смотришь на море. Потом на свои манжеты. И медленно расстёгиваешь пуговицу.'),
        msg('Один рукав. Второй. Розовато-белые рубцы на солнце — до самого локтя.'),
        'pause 1000', 'faceDirection Harvey 3',
        msg('Харви ничего не говорит. Он просто закатывает свои рукава — аккуратно, до локтя, как перед операцией.'),
        'faceDirection Harvey 2',
        sp('Sam', 'Эй, док! Вы что, загорать собрались? Это вообще законно?$h'),
        sp(H, 'Врачам тоже иногда положено солнце, Сэм. Изредка. По рецепту.$h'),
        sp('Haley', '…У тебя красивые руки, @. Правда. Сильные.$0'),
        qq(['Положить руку рядом с его рукой', 'Улыбнуться Хейли', 'Просто подставить руки солнцу'], [
            [msg('Ты кладёшь руку на песок рядом с его. На его запястье — маленький старый ожог от автоклава.'),
             sp(H, 'Видишь? У меня тоже есть. Глупый, рабочий. У всех что-то есть, солнышко.$l'),
             'friendship Harvey 35'],
            [sp('Haley', 'И крем от солнца на рубцы — обязательно. Это тебе как эксперт по загару говорю.$h'),
             sp(H, '…Хейли права. Медицински права. Запиши, это редкость.$h'),
             'friendship Haley 30', 'friendship Harvey 30'],
            [msg('Солнце тёплое. Никто не отворачивается. Никто не смотрит слишком долго.'),
             sp(H, 'Вот так. Просто лето, просто руки.$l'),
             'friendship Harvey 30'],
        ]),
        sp(H, 'Я горжусь тобой. Не потому что так надо. Потому что ты сама так решила.$l'),
        'addConversationTopic HarveyScars_SleevesUp 3',
    ])

# ---------------------------------------------------------------- C8
c8_key = key(NS, 'C8_Map', 'Time 2000 2400', 'Friendship Harvey 3000',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married', seen('C7_SleevesUp'))
c8 = script(
    'none', f'{FX} {FY0}', f'farmer {FX} {FY1} 2 Harvey {FX} {FY2} 0',
    skip_cd('AddConversationTopic HarveyScars_Map 3'),
    [
        'ambientLight 120 120 60', 'pause 600',
        msg('Поздний вечер. Крыльцо, плед, две кружки. Харви держит тебя за руку — уже по привычке.'),
        sp(H, 'Котёнок. Можно попросить?$s'),
        sp(H, 'Я никогда не касался рубцов просто так. Только как врач: мазь, осмотр, «скажи стоп».$s#$b#Можно… просто посмотреть? Не лечить. Запомнить.$s'),
        qq(['«Можно»', '«Только ладони»', '«Нет. Не сегодня»'], [
            [msg('Ты закатываешь рукав. Он берёт твою руку так, будто она стеклянная, и ведёт пальцем вдоль каждого рубца, не нажимая.'),
             sp(H, 'Этот — самый длинный. Этот похож на реку на карте Мару. А этот совсем маленький — я бы его не заметил, если бы не искал.$l'),
             sp(H, 'Я не лечу. Я запоминаю. Чтобы знать тебя всю — а не только то, что на виду.$l'),
             'friendship Harvey 40'],
            [msg('Ты протягиваешь ладони. Он берёт их в свои — и всё. Просто держит.'),
             sp(H, 'Ладони — это тоже много. Ими ты держишь ферму. И меня.$l'),
             'friendship Harvey 35'],
            [STOP,
             sp(H, 'Хорошо.$0'),
             msg('Он не убирает руку — только перестаёт спрашивать. Пальцы остаются лежать рядом, тёплые.'),
             sp(H, 'Я подожду. Хоть годы. Мне некуда торопиться — я уже дома.$l'),
             'friendship Harvey 30'],
        ]),
        sp(H, 'Когда я впервые увидел рубцы, я думал как врач: ожог второй степени, давность, прогноз.$s'),
        sp(H, 'А сейчас думаю: это карта того, как ты выжила. И пришла ко мне.$l#$b#Такую карту не пишут. Её просто носят.$l'),
        'addConversationTopic HarveyScars_Map 3',
    ])

# ---------------------------------------------------------------- данные
MAIL = {
    'HarveyScars_VeteransLetter': (
        'Уважаемая @,^^Министерство по делам ветеранов Республики Ферн разыскивает гражданских лиц, '
        'переживших лагеря империи Готоро.^Если вы одна из них, вы вправе получить статус пострадавшей и компенсацию.'
        '^^Для этого нужно свидетельство в свободной форме и медицинское заключение о характере повреждений.'
        '^Срок подачи не ограничен. Решение о подаче остаётся за вами.'
        '^^   — Отдел по делам гражданских пострадавших, Зузу[#]Письмо из Зузу'),
    'HarveyScars_ReplyRecognized': (
        'Уважаемая @,^^по вашему обращению и приложенному заключению доктора Харви вы признаны '
        'пострадавшей гражданской в войне с империей Готоро.^Компенсация приложена к письму.'
        '^^Министерство приносит извинения за то, что Республика не смогла защитить ваш город.'
        '^^   — Отдел по делам гражданских пострадавших, Зузу%item money 5000 %%[#]Ответ из министерства'),
}

TOPICS_ANY = {
    'HarveyScars_Sleeves': 'Полотенца разошлись за час. Пэм забрала два.$h#$b#Одно я оставил в холодильнике клиники. На случай, если кому-то снова будет жарко.$0',
    'HarveyScars_Pop': 'Я спросил Кента, как он научился считать.$s#$b#Он сказал: «Кто-то считал для меня». Теперь и я умею. Раз — это просто звук.$0',
    'HarveyScars_Salve': 'Мазь — утром, до холода. Я не проверяю.$h#$b#…Почти не проверяю.$h',
    'HarveyScars_TightToday': 'Руки тянет? Я вижу, как ты сжимаешь и разжимаешь пальцы.$s#$b#Мазь, тёплая вода, перчатки. И пожалуйста — не геройствуй с ведром на морозе.$a',
    'HarveyScars_SalveUsed': 'Пахнет календулой — ты не забыла про мазь.$h#$b#Врачу приятно, когда назначения выполняют без напоминаний. Редкое удовольствие.$h',
    'HarveyScars_FireReaction': 'Ты сегодня стояла у огня, да? У тебя такой взгляд… я видел его в Зузу, после пожаров.$s#$b#Дыши. Дым — это память тела, не сегодняшний день.$0#$b#Хочешь, переставим печку подальше от двери? Я помогу.$s',
    'HarveyScars_Letter': 'Я думаю о письме. Не о бумаге — о тебе. Как ты?$s',
    'HarveyScars_Stranger': 'Рик заходил с коленом. Хороший человек. Я извинился — он так и не понял за что.$u#$b#Ничего. Я понял.$0',
    'HarveyScars_NoPaperNeeded': 'Я сжёг письмо в тот же вечер. Во дворе, как обещал.$0#$b#Тебе не нужна их бумага, чтобы это было правдой. Я знаю. Ты знаешь. Этого хватит.$s',
    'HarveyScars_DrawerLetter': 'Письмо всё ещё в ящике? Пусть лежит. У решений нет срока годности.$0#$b#Заключение я всё-таки написал — на всякий случай. Оно в столе. Просто чтобы ты знала.$s',
}
TOPICS_ROMANCE = {
    'HarveyScars_TightToday': 'Солнышко, руки тянет? Я вижу, как ты сжимаешь и разжимаешь пальцы.$s#$b#Мазь, тёплая вода, перчатки. Ведро на морозе понесу я — возражения после чая.$a',
    'HarveyScars_FireReaction': 'Ты сегодня стояла у огня. Я вижу по плечам.$s#$b#Иди сюда. Дым — это память тела, а не сегодняшний день. Сегодня — я и чай.$l',
    'HarveyScars_SleevesUp': 'У меня до сих пор загар до локтя. Мару говорит, я похож на фермера.$h#$b#Это комплимент, солнышко? Я решил, что да.$l',
    'HarveyScars_Map': 'Самый маленький рубец — у основания большого пальца. Я помню.$l#$b#Не бойся, лечить его не буду. Только иногда целовать.$l',
    'HarveyScars_Recognized': 'Пришёл ответ из министерства? «Признана пострадавшей гражданской…»$s#$b#Знаешь, что важнее их бумаги? Что ты сама решила её отправить.$l',
}

TRIGGERS = {
    # Флаг для C# (ScarCareManager): механика рубцов включается вместе с TraumaBackstory.
    '{{ModId}}_ScarsEnabled': {
        'Trigger': 'DayStarted', 'Condition': '!PLAYER_HAS_MAIL Current HarveyScars_Enabled Received',
        'Actions': ['AddMail Current HarveyScars_Enabled Received'], 'MarkActionApplied': False},
    # Старые сохранения: T1 пройдена до появления флага, но тема ещё активна.
    '{{ModId}}_FireKnownMigrate': {
        'Trigger': 'DayStarted',
        'Condition': 'ANY "PLAYER_HAS_CONVERSATION_TOPIC Current topicHarveyBackstoryFire" '
                     '"PLAYER_HAS_CONVERSATION_TOPIC Current topicHarveyBackstoryFull"',
        'Actions': ['AddMail Current HarveyBackstory_FireKnown Received']},
    '{{ModId}}_ScarsVeteransLetter': {
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.C3_ScarSalve, PLAYER_FRIENDSHIP_POINTS Current Harvey 1750, '
                     '!PLAYER_HAS_MAIL Current HarveyScars_VeteransLetter Any',
        'Actions': ['AddMail Current HarveyScars_VeteransLetter']},
    # Развилка C4 → после C8: ответ министерства / разговор о сожжённом / о письме в ящике.
    '{{ModId}}_ScarsReplySent': {
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.C8_Map, PLAYER_HAS_MAIL Current HarveyScars_LetterSent Received',
        'Actions': ['AddMail Current HarveyScars_ReplyRecognized', 'AddConversationTopic HarveyScars_Recognized 4']},
    '{{ModId}}_ScarsReplyBurned': {
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.C8_Map, PLAYER_HAS_MAIL Current HarveyScars_LetterBurned Received',
        'Actions': ['AddConversationTopic HarveyScars_NoPaperNeeded 3']},
    '{{ModId}}_ScarsReplyKept': {
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.C8_Map, PLAYER_HAS_MAIL Current HarveyScars_LetterKept Received',
        'Actions': ['AddConversationTopic HarveyScars_DrawerLetter 3']},
}
for tid, t in TRIGGERS.items():
    t['Id'] = tid

BUFFS = {
    'HarveyScars_Tightness': {
        'DisplayName': 'Рубцы стягивает',
        'Description': 'Холод стягивает старые ожоги на руках. Пальцы слушаются хуже. Мазь Харви поможет.',
        'IsDebuff': True, 'Duration': -2,
        'IconTexture': 'Mods/{{ModId}}/MishapBuffIcons', 'IconSpriteIndex': 5,
        'Effects': {'FarmingLevel': -1, 'FishingLevel': -1}},
    'HarveyScars_Salved': {
        'DisplayName': 'Мазь для рубцов',
        'Description': 'Кожа мягкая и тёплая. Сегодня холод рубцы не стянет.',
        'Duration': -2,
        'IconTexture': 'Mods/{{ModId}}/MedicalItems', 'IconSpriteIndex': 5,
        'Effects': {}},
    'buffStressFireMemory': {
        'DisplayName': 'Запах дыма',
        'Description': 'Память тела. Отойди от огня и подыши.',
        'IsDebuff': True, 'Duration': 168000,
        'IconTexture': 'Mods/{{ModId}}/HarveyBuffIcons', 'IconSpriteIndex': 121,
        'Effects': {'Defense': -1}},
}

SALVE_ITEM = {
    '{{ModId}}_ScarSalve': {
        'Name': '{{ModId}}_ScarSalve',
        'DisplayName': 'Мазь для рубцов',
        'Description': 'Календула, воск и масло — по рецепту Харви. Зимой снимает стянутость старых рубцов на весь день. Используй, держа в руках.',
        'Type': 'Basic', 'Category': 0, 'Price': 120,
        'Texture': 'Mods/{{ModId}}/MedicalItems', 'SpriteIndex': 5,
        'Edibility': -300, 'ExcludeFromShippingCollection': True,
        'ContextTags': ['medicine_item', '{{ModId}}_medical_item'],
    },
}
SALVE_SHOP = {
    '{{ModId}}_ScarSalve': {
        'Id': '{{ModId}}_ScarSalve', 'ItemId': '(O){{ModId}}_ScarSalve', 'Price': 240,
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {NS}.C3_ScarSalve'},
}

TRAUMA_ON = {'TraumaBackstory': 'true'}


def when(p, cond):
    p['When'] = cond
    return p


data = {'Changes': [
    when(patch('Scars — арка «Шрамы»: события в городе (C1, C2)', 'Data/Events/Town', {c1_key: c1, c2_key: c2}), TRAUMA_ON),
    when(patch('Scars — C3 мазь, C4 письмо из Зузу (Hospital)', 'Data/Events/Hospital', {c3_key: c3, c4_key: c4}), TRAUMA_ON),
    when(patch('Scars — C6 «Чужой в Долине» (BusStop)', 'Data/Events/BusStop', {c6_key: c6}), TRAUMA_ON),
    when(patch('Scars — C7 «Рукава закатаны» (Beach)', 'Data/Events/Beach', {c7_key: c7}), TRAUMA_ON),
    when(patch('Scars — C8 «Карта, которую не пишут» (Farm)', 'Data/Events/Farm', {c8_key: c8}), TRAUMA_ON),
    when(patch('Scars — письма министерства', 'Data/Mail', MAIL), TRAUMA_ON),
    when(patch('Scars — триггеры (флаг механики, письмо, развилка C4)', 'Data/TriggerActions', TRIGGERS), TRAUMA_ON),
    when({**patch('Scars — реплики Харви на темы', 'Characters/Dialogue/Harvey', TOPICS_ANY), 'Priority': 'Late'}, TRAUMA_ON),
    when({**patch('Scars — реплики Харви на темы (Dating / Married)', 'Characters/Dialogue/Harvey', TOPICS_ROMANCE),
          'Priority': 'Late'}, {**TRAUMA_ON, 'Relationship:Harvey': 'Dating, Married'}),
    when(patch('Scars — баффы: рубцы, мазь, запах дыма', 'Data/Buffs', BUFFS), TRAUMA_ON),
    when(patch('Scars — мазь для рубцов', 'Data/Objects', SALVE_ITEM), TRAUMA_ON),
    when({**patch('Scars — мазь в магазине клиники', 'Data/Shops', SALVE_SHOP), 'TargetField': ['Hospital', 'Items']}, TRAUMA_ON),
    # TraumaBackstory выключили — снимаем флаг, механика рубцов и огня замолкает.
    when(patch('Scars — снять флаг при выключенном TraumaBackstory', 'Data/TriggerActions', {
        '{{ModId}}_ScarsDisabled': {
            'Id': '{{ModId}}_ScarsDisabled', 'Trigger': 'DayStarted',
            'Actions': ['RemoveMail Current HarveyScars_Enabled', 'RemoveMail Current HarveyBackstory_FireKnown'],
            'MarkActionApplied': False}}), {'TraumaBackstory': 'false'}),
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, sum(1 for c in data['Changes'] if c['Target'].startswith('Data/Events')), 'event patches')

# ---------------------------------------------------------------- T1: запомнить, что она рассказала про огонь
# Тема topicHarveyBackstoryFire/Full живёт 14 дней, а FireMemoryService нужен постоянный флаг.
BS2 = chr(92) * 2
T1_PATH = os.path.join(ROOT, 'assets', 'Code', 'eventsTraumaBackstory.json')
with open(T1_PATH, encoding='utf-8') as f:
    t1 = f.read()
if 'HarveyBackstory_FireKnown' not in t1:
    for topic in ('topicHarveyBackstoryFull 14', 'topicHarveyBackstoryFire 14'):
        anchor = f'addConversationTopic {topic}(break)'
        assert t1.count(anchor) == 1, anchor
        t1 = t1.replace(anchor, f'addConversationTopic {topic}{BS2}action AddMail Current HarveyBackstory_FireKnown Received(break)')
    with open(T1_PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(t1)
    print('T1: флаг HarveyBackstory_FireKnown добавлен в ветки «всё» и «про огонь»')
