"""Семья, урок первой помощи, памятная мебель и годовщины: пункты 5–8.

Координаты сверены validate_event_coords.py по установленным картам.
Награды приходят письмом на следующее утро; пропуск сцены не теряет предмет.
"""
import json
from pathlib import Path

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp

ROOT = Path(__file__).resolve().parents[1]
M = '{{ModId}}'
NS = 'HarveyOverhaulFamily'
AN = 'HarveyOverhaulAnniversary'
WORKSHOP = 'HarveyOverhaulClinic.FA1_FirstAid'
MARRIED = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married'
READY = 'GameStateQuery PLAYER_HAS_MAIL Current HarveyFamily_ToddlerReady Received'
AR = 'HarveyOverhaulArend.A1_Arrival'
FAMILY_WHEN = {'ArendEnabled': 'true', 'Relationship:Harvey': 'Married'}
CHILD = 'HarveyFamilyChild'
MEMORY = 'HarveyMemory_'
KEEPSAKE_IDS = ['FamilyDrawing', 'ModelPlane', 'PressedFlower', 'AnniversaryNote', 'FamilyPhoto', 'RingBox']
# Маленькие вещи 1x1 лежат в третьем ряду атласа (generate_keepsake_sprites.py).
SMALL_KEEPSAKES = {'RingBox': 20}


def flag(name):
    if name.startswith('Photo_'):
        # Повторные годовщины не переписывают историю уже подаренного первого снимка.
        return (f'action If !PLAYER_HAS_MAIL Current HarveyFamily_PhotoTaken Received '
                f'## AddMail Current {MEMORY}{name} Received')
    return f'action AddMail Current {MEMORY}{name} Received'


def child(x, y, direction=2):
    return f'addTemporaryActor {CHILD} 16 32 {x} {y} {direction} true Character FamilyChild'


def seen(eid):
    return f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {eid}'


def family_key(eid, *conditions):
    return key(NS, eid, MARRIED, READY, seen(AR), *conditions)


birds_key = family_key('G1_Birds', 'Weather sunny', 'Time 1000 1700', 'Friendship Arend 1000')
birds = script('continue', '49 14', 'farmer 48 15 1 Harvey 51 15 3 Arend 50 13 2',
    skip_cd('AddConversationTopic HarveyFamily_Birds 5'), [
        child(49, 14, 0), 'viewport 49 14 true', 'pause 500',
        msg('Аренд присел у тропы с раскрытым блокнотом. Малыш показывает пальцем на ветку, а Харви держит панамку наготове.'),
        sp('Arend', 'Сорок седьмой вид. Правда, наш наблюдатель называет его «пи».$h'),
        sp(H, 'Панамку я взял. Воду тоже. И запасную панамку.$0'),
        sp('Arend', 'Сын, для птицы панамка не нужна.$h'),
        qq(['Попросить Аренда показать птицу', 'Дать Харви блокнот, а самой взять панамку', 'Тихонько послушать'], [
            [sp('Arend', 'Вон, на нижней ветке. Не торопимся. Пусть смотрит столько, сколько хочется.$0'),
             flag('Birds_Look'), 'friendship Arend 30'],
            [msg('Харви берёт карандаш. На полях появляется маленькая птичка в огромной шляпе.'),
             sp(H, 'Это научная иллюстрация. Прошу не смеяться.$h'), flag('Birds_Hat'), 'friendship Harvey 30'],
            [msg('Некоторое время слышны только листья, птицы и очень серьёзное детское «пи».'),
             sp('Arend', 'Вот это я и хотел вам показать.$h'), flag('Birds_Quiet'), 'friendship Arend 30'],
        ]),
        msg('Аренд вписывает дату и рядом рисует три больших следа и один совсем маленький.'),
        sp(H, 'В следующий раз опять пойдём вместе. И да, панамки всё равно возьму.$l'),
        'addConversationTopic HarveyFamily_Birds 5',
    ])

toy_key = family_key('G2_Toy', 'Time 1700 2200', seen(NS + '.G1_Birds'))
toy = script('continue', '12 7', 'farmer 11 7 1 Harvey 13 6 2 Arend 14 7 3',
    skip_cd('AddConversationTopic HarveyFamily_Toy 5'), [
        child(12, 7, 0), 'pause 400',
        msg('На полу лежат деревянные крылья. Харви сверяется с чертежом, Аренд держит готовую игрушку — простой самолётик с толстыми колёсами.'),
        sp(H, 'У моего двенадцать подвижных частей. Возрастная маркировка, конечно, подходящая.$0'),
        sp('Arend', 'А у моего — колёса. Проверим, что выберет испытатель?$h'),
        qq(['Помочь Харви упростить конструкцию', 'Предложить устроить испытания', 'Сделать самолётик из бумаги'], [
            [msg('Ты убираешь лишние детали. Харви смотрит, как игрушка помещается в маленьких руках.'),
             sp(H, 'Да. Вот так лучше. Иногда крыло — просто крыло.$h'), flag('Toy_Simple')],
            [msg('Малыш с важным видом прокатывает самолёт Аренда через всю площадку, а затем выбирает пустую коробку.'),
             sp('Arend', 'Первое место у упаковки. Безоговорочно.$h'), flag('Toy_Box')],
            [msg('Бумажный самолётик пролетает совсем недалеко. Малыш хлопает в ладоши.'),
             sp(H, 'Ни винтика. А восторга больше, чем от всего моего чертежа.$h'), flag('Toy_Paper')],
        ]),
        sp('Arend', 'Ты в этом возрасте тоже выбирал коробки. Только подписывал их «скорая помощь».$h'),
        sp(H, 'Пап. Это была очень хорошая скорая.$h'),
        'friendship Harvey 30', 'friendship Arend 25', 'addConversationTopic HarveyFamily_Toy 5',
    ])

drawing_key = family_key('G3_Drawing', 'Time 1600 2200', seen(NS + '.G2_Toy'))
drawing = script('continue', '12 7', 'farmer 11 7 1 Harvey 13 6 2 Arend 14 7 3',
    skip_cd('AddConversationTopic HarveyFamily_Drawing 7'), [
        child(12, 7, 0), 'pause 400',
        msg('На большом листе — несколько цветных кружков и длинная зелёная линия. Аренд наклоняет голову, рассматривая рисунок.'),
        sp('Arend', 'Это мы. Сходство со мной особенно точное: очки крупнее головы.$h'),
        sp(H, 'А я с сумкой. Меня даже на семейном портрете отправляют на вызов.$h'),
        qq(['Предложить дорисовать птиц', 'Предложить дорисовать наш дом', 'Предложить дорисовать самолёт'], [
            [msg('Над цветными кружками появляются три кривоватые птички. Аренд подписывает каждую: «пи».'), flag('Drawing_Birds')],
            [msg('Ты показываешь на окно. На листе появляется дом с удивительно большой дверью — чтобы все поместились.'), flag('Drawing_Home')],
            [msg('Харви помогает провести линию крыла. Получается самолёт, который везёт всю семью сразу.'), flag('Drawing_Plane')],
        ]),
        sp(H, 'Я вставлю его в рамку. Да, даже этот зелёный хвост. Это, кажется, я.$l'),
        sp('Arend', 'С обратной стороны поставим дату. Остальное и так запомним.$0'),
        msg('На следующее утро Харви обещает прислать рисунок в рамке. Его можно будет повесить дома.'),
        'friendship Harvey 35', 'friendship Arend 30', 'addConversationTopic HarveyFamily_Drawing 7',
    ])

lesson_key = key('HarveyOverhaulClinic', 'FA1_FirstAid', 'DayOfWeek Sat', 'Time 1000 1500', 'Friendship Harvey 750')
lesson = script('Hospital_Ambient', '11 17',
    'farmer 10 18 0 Harvey 10 16 2 Maru 13 16 2 Sam 13 18 3 George 9 18 1',
    skip_cd('AddConversationTopic HarveyClinic_FirstAid 7'), [
        'viewport 11 17 true', 'pause 400',
        msg('В приёмной стоят коробка бинтов и учебный манекен. Сэм уже лежит на стуле с таким видом, будто умирает от скуки.'),
        sp(H, 'Сегодня короткое занятие по первой помощи. Всё отрабатываем на манекене. Сэм, тебя в программу не включали.$0'),
        sp('Sam', 'Я могу достоверно стонать!$h'),
        sp('George', 'Я пришёл посмотреть, сколько времени вы потратите на один бинт.$a'),
        sp('Maru', 'Таймер работает. И манекен тоже. Хотя доктор проверил его три раза.$h'),
        sp(H, '@, поможешь? Можно показать на манекене, прочитать условие задачи или следить за временем.$0'),
        qq(['Помочь с учебной повязкой', 'Прочитать задачу про вызов помощи', 'Взять таймер и остановить спектакль Сэма'], [
            [msg('Мару придерживает манекен, пока вы с Харви разбираете учебную повязку. Сэм предлагает нарисовать на ней молнию.'),
             sp(H, 'Молния не обязательна. Главное — аккуратно и по заданию.$h'), flag('Lesson_Bandage'), 'friendship Maru 25'],
            [msg('Ты читаешь карточку. Джордж первым замечает, что в учебном адресе забыли номер дома.'),
             sp('George', 'Как к вам приедут, если вы даже адрес сообщить не можете?$a'),
             sp(H, 'Справедливо. Это и был наш вопрос с подвохом. Теперь будет — благодаря вам.$h'),
             flag('Lesson_Address'), 'friendship George 25'],
            [msg('Ты запускаешь таймер. Сэм тут же садится ровно.'),
             sp('Sam', 'Когда время настоящее, умирать скучно.$h'),
             sp('Maru', 'Впишу это в отчёт о занятии.$h'), flag('Lesson_Timer'), 'friendship Sam 25'],
        ]),
        sp('George', 'Бинт ровный. Адрес полный. Можно расходиться.$0'),
        sp(H, 'Занятие окончено. И спасибо за помощь — одному мне пришлось бы лечить актёрскую карьеру Сэма.$h'),
        'friendship Harvey 35', 'addConversationTopic HarveyClinic_FirstAid 7',
    ])

second_key = key(AN, 'A2_Kitchen', 'Time 1800 2400', MARRIED,
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyMarriage_AnniversaryToday Received',
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyMarriage_AnniversarySecond Received', cooldown=False)
second = script('harveys_theme_jazz', '12 7', 'farmer 11 7 1 Harvey 13 7 3',
    skip_cd('AddConversationTopic HarveyMarriage_SecondAnniversary 3'), [
        'pause 500', msg('Харви встречает тебя с маленьким тортом. На фартуке мука, на щеке — тоже.'),
        sp(H, 'Два года. Я хотел приготовить ужин из трёх блюд.$l#$b#Одно получилось. Второе теперь сухарь. Третье я решил не называть.$h'),
        qq(['Попробовать торт', 'Стереть муку с его щеки', 'Предложить доесть вчерашний суп'], [
            [msg('Торт немного кривой и очень вкусный. Харви явно ждал оценки.'),
             sp(H, 'Правда? Тогда рецепт сохраняем. Температуру духовки — исправляем.$h'), flag('Anniversary_Cake')],
            [msg('Ты стираешь муку. Он на секунду закрывает глаза и улыбается.'),
             sp(H, 'Вот. Ради этого я готов ещё что-нибудь сжечь.$l'), flag('Anniversary_Flour')],
            [sp(H, 'Суп, торт и ты. Убедительная программа. Почему я составлял свою два вечера?$h'), flag('Anniversary_Soup')],
        ]),
        sp(H, 'В прошлом году я готовил речь. В этом хотел ужин. В следующем, пожалуй, просто заранее освобожу вечер.$l'),
        msg('Он ставит торт между вами и убирает часы в ящик. Сегодня можно никуда не торопиться.'),
        'addItem (O)221 1', 'friendship Harvey 40', 'addConversationTopic HarveyMarriage_SecondAnniversary 3',
    ])

later_key = key(AN, 'A3_Together', 'Time 1800 2400', MARRIED,
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyMarriage_AnniversaryToday Received',
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyMarriage_AnniversaryLater Received', cooldown=False)
later_couple = script('harveys_theme_jazz', '12 7', 'farmer 11 7 1 Harvey 13 7 3',
    skip_cd('AddConversationTopic HarveyMarriage_LaterAnniversary 3'), [
        'pause 500', msg('На столе две чашки. Харви освободил место рядом с собой и отложил книгу раскрытой вниз.'),
        sp(H, 'С годовщиной, солнышко. У меня готов ужин. Проверенный. Суп не подводит.$h'),
        qq(['Вспомнить первую годовщину', 'Спросить, что он читал', 'Предложить помечтать о следующем годе'], [
            [sp(H, 'Плед на пляже и моя ужасная речь? Я хранил её в кармане и боялся забыть каждое слово.$l'),
             msg('Ты напоминаешь ему одно из слов. Он смеётся: помнит все.'), flag('Later_Remember')],
            [sp(H, 'Каталог моделей. На странице девятнадцать есть самолёт, для которого у нас совершенно нет места.$h'),
             msg('Вы меряете ладонями пустую полку. Места, конечно, достаточно.'), flag('Later_Plane')],
            [sp(H, 'Хочу больше таких вечеров. И съездить с тобой к морю просто так, без сумки врача.$l'), flag('Later_Plans')],
        ]),
        sp(H, 'Раньше я репетировал, что скажу тебе вечером. Теперь слышу ключ в двери — и всё нужное само находится.$l'),
        'friendship Harvey 40', 'addConversationTopic HarveyMarriage_LaterAnniversary 3',
    ])
later_family = script('harveys_theme_jazz', '12 7', 'farmer 11 7 1 Harvey 13 6 2 Arend 14 7 3',
    skip_cd('AddConversationTopic HarveyMarriage_LaterAnniversary 3', 'AddMail Current HarveyFamily_PhotoTaken Received'), [
        child(12, 7, 0), 'pause 500',
        msg('На столе торт, под столом игрушка, в руках Аренда фотоаппарат. Харви безуспешно пытается добиться, чтобы все посмотрели в одну сторону.'),
        sp('Arend', 'За всю мою практику никто не сопротивлялся фотографии так убедительно.$h'),
        sp(H, 'Пап, можно без вспышки. И без двадцати попыток. У нас годовщина, а не обследование.$h'),
        qq(['Сфотографироваться всем вместе', 'Поставить в центр малыша', 'Предложить смешное фото без позирования'], [
            [msg('Аренд ставит таймер и едва успевает встать рядом. На снимке его очки снова на лбу.'), flag('Photo_Together')],
            [msg('Малыш держит игрушку перед объективом. У самолёта получилось особенно торжественное лицо.'), flag('Photo_Child')],
            [msg('Харви смеётся, Аренд машет рукой, а ты пытаешься поймать падающую игрушку. Щёлк!'), flag('Photo_Laugh')],
        ]),
        sp('Arend', 'Напечатаю и пришлю. Такие фотографии должны висеть там, где их видят каждый день.$0'),
        sp(H, 'С годовщиной, любимая. Посмотри, сколько нас теперь.$l'),
        'action AddMail Current HarveyFamily_PhotoTaken Received', 'friendship Harvey 40', 'friendship Arend 25',
        'addConversationTopic HarveyMarriage_LaterAnniversary 3',
    ])


def choice(name, description):
    return {'Flag': MEMORY + name, 'Description': description}


KEEPSAKES = {
    'FamilyDrawing': {
        'Description': 'Семейный рисунок в деревянной рамке. Несколько цветных кружков, очки Аренда и дата на обороте.',
        'HarveyLine': 'Вот этот зелёный — я. Утверждено автором. Спорить с художником я не собираюсь.',
        'ArendLine': 'Узнаю свои очки. В следующий раз попрошу нарисовать их на лбу — так будет ещё точнее.',
        'Choices': [
            choice('Drawing_Birds', 'Над всей семьёй летают три птицы. Под каждой Аренд подписал: «пи». На обороте — дата вашего вечера.'),
            choice('Drawing_Home', 'Вся семья стоит перед домом с огромной дверью. «Чтобы все поместились», — написал Харви на обороте.'),
            choice('Drawing_Plane', 'Самолёт везёт всю семью. Крыло нарисовано особенно аккуратно: его помогал выводить Харви.'),
        ],
    },
    'ModelPlane': {
        'Description': 'Небольшая модель самолёта. Одно крыло вы придерживали вместе, пока высыхал клей.',
        'HarveyLine': 'Это крыло до сих пор самое ровное. Вторая пара рук оказалась полезнее инструкции.',
    },
    'PressedFlower': {
        'Description': 'Засушенный цветок под стеклом. На бумажной полоске почерком Харви: «С нашей прогулки».',
        'HarveyLine': 'В тот вечер я три раза проверил корзину и всё равно забыл салфетки. А ты даже не заметила.',
    },
    'AnniversaryNote': {
        'Description': 'Записка с первой годовщины. «Состояние: любима. Рекомендации: продолжать». Внизу осталось место для ответа.',
        'HarveyLine': 'Почерк ужасный, согласен. Но это заключение я бы и сейчас подписал.',
        'Choices': [
            choice('FirstAnniversary_Wrote', 'Под запиской Харви твой ответ: «Лечащий врач тоже любим». Две подписи стоят совсем рядом.'),
            choice('FirstAnniversary_Shoulder', 'Записка с первой годовщины. На краешке осталась песчинка с пляжа, где вы сидели плечом к плечу.'),
            choice('FirstAnniversary_HisCard', 'Записка с первой годовщины. На обороте твоё имя — экстренный контакт. Теперь у врача тоже есть к кому обратиться.'),
        ],
    },
    'FamilyPhoto': {
        'Description': 'Фотография с семейной годовщины. Торт, игрушка и люди, которые едва поместились в кадр.',
        'HarveyLine': 'Я хотел, чтобы все посмотрели в камеру. Хорошо, что не получилось. Так гораздо больше похоже на нас.',
        'ArendLine': 'Хорошо, что я взял фотоаппарат. Словами этот вечер было бы труднее пересказать.',
        'Choices': [
            choice('Photo_Together', 'Аренд едва успел к таймеру. Очки на лбу, плечи рядом — вся семья наконец в одном кадре.'),
            choice('Photo_Child', 'В центре снимка малыш с игрушечным самолётом. Взрослые видны чуть меньше, зато никто не спорит с композицией.'),
            choice('Photo_Laugh', 'Харви смеётся, Аренд машет, игрушка падает. Самый нерезкий и самый любимый семейный снимок.'),
        ],
    },
    'RingBox': {
        'Description': 'Бархатная коробочка с потёртыми уголками. Харви носил в ней кольцо с весны — ждал правильного дня.',
        'HarveyLine': 'Она полгода жила у меня в кармане халата. Мару думала, там успокоительное. В каком-то смысле так и было.',
        'ArendLine': 'Он звонил мне из Зузу из ювелирного. Сорок минут выбирал между двумя одинаковыми кольцами.',
        'Choices': [
            choice('Ring_Yes', 'Бархатная коробочка от кольца. Внутри на крышке Харви вывел: «Да. Снова да». Твоими словами.'),
            choice('Ring_Stand', 'Бархатная коробочка от кольца. На подушечке — пылинка с мостовой у клиники, где он стоял на одном колене при всём городе.'),
            choice('Ring_HePutOn', 'Бархатная коробочка от кольца. Под подушечкой — бумажная мерка, снятая с твоей перчатки. Врачебная привычка.'),
        ],
    },
}
NAMES = ['Семейный рисунок', 'Наш самолёт', 'Цветок с прогулки', 'Записка с годовщины', 'Семейная фотография',
         'Коробочка от кольца']


def build():
    family_events = [
        {**patch('Family G1 — «Пи» (Forest, ребёнок уже ходит)', 'Data/Events/Forest', {birds_key: birds}), 'When': FAMILY_WHEN},
        {**patch('Family G2 — «Испытатель» (FarmHouse)', 'Data/Events/FarmHouse', {toy_key: toy}), 'When': FAMILY_WHEN},
        {**patch('Family G3 — «Все поместились» (FarmHouse)', 'Data/Events/FarmHouse', {drawing_key: drawing}), 'When': FAMILY_WHEN},
        patch('Clinic FA1 — занятие по первой помощи', 'Data/Events/Hospital', {lesson_key: lesson}),
        patch('Anniversary A2 — второй год, ужин на кухне', 'Data/Events/FarmHouse', {second_key: second}),
        {**patch('Anniversary A3 — третий и следующие годы, вдвоём', 'Data/Events/FarmHouse', {later_key: later_couple}),
         'When': {'HO_AnniversaryFamily': 'false'}},
        {**patch('Anniversary A3 — третий и следующие годы, семья', 'Data/Events/FarmHouse', {later_key: later_family}),
         'When': {'HO_AnniversaryFamily': 'true'}},
    ]
    topics = {
        'HarveyFamily_Birds': 'Папа завёл отдельную страницу для наших прогулок. В графе «наблюдатель» уже четыре имени.$h',
        'HarveyFamily_Toy': '$query PLAYER_HAS_MAIL Current HarveyMemory_Toy_Box Received#Коробку пока не выбрасывай. У неё первое место в испытаниях.$h|Самолётик пережил испытания. А я научился не усложнять игрушки. Почти.$h',
        'HarveyFamily_Drawing': 'Если на рисунке я зелёный, значит, буду зелёным. Место на стене уже присмотрел.$l',
        'HarveyMarriage_SecondAnniversary': '$query PLAYER_HAS_MAIL Current HarveyMemory_Anniversary_Soup Received#На следующую годовщину готовлю суп. Этот план ты уже одобрила.$h|Рецепт торта сохранил. Подгоревшую часть инструкции — исправил.$h',
        'HarveyMarriage_LaterAnniversary': 'Спасибо за вчерашний вечер. Сегодня я опять на смене, но домой уже хочется.$l',
    }
    lesson_topics = {
        'Harvey': '$query PLAYER_HAS_MAIL Current HarveyMemory_Lesson_Timer Received#Сэм предложил проводить занятия с секундомером. По-моему, он боится твоего взгляда больше, чем моего.$h|Спасибо за помощь на занятии. В следующий раз Сэму дадим роль здорового прохожего.$h',
        'Sam': '$query PLAYER_HAS_MAIL Current HarveyMemory_Lesson_Timer Received#Я теперь умею выздоравливать по таймеру. Мару говорит, это бесполезный навык.$h|Доктор запретил стонать без задания. Мой талант опять пропадает.$h',
        'Maru': '$query PLAYER_HAS_MAIL Current HarveyMemory_Lesson_Bandage Received#Та учебная повязка ещё держится. Я оставила её на манекене до следующего занятия.$h|Занятие удалось. Манекен цел, Сэм жив, доктор даже успел пообедать.$h',
        'George': '$query PLAYER_HAS_MAIL Current HarveyMemory_Lesson_Address Received#Адрес на карточке исправили. Хоть какая-то польза от моего визита.$h|В следующий раз пусть учат молодых не оставлять доски поперёк дорожек.$a',
    }
    followups = [patch('Family — реплики Харви после домашних сцен', 'Characters/Dialogue/Harvey', topics)]
    followups[0]['Priority'] = 'Late + 1'
    followups[0]['When'] = {'Relationship:Harvey': 'Married'}
    for npc, text in lesson_topics.items():
        followups.append({**patch(f'First aid — {npc} вспоминает занятие', f'Characters/Dialogue/{npc}',
                                 {'HarveyClinic_FirstAid': text}), 'Priority': 'Late + 1'})
    followups.append({**patch('Family — Аренд после прогулок и рисунка', 'Characters/Dialogue/Arend', {
        'HarveyFamily_Birds': 'Следующий вид ищем вместе. Блокнот у меня, панамки — у сына. Всё распределено.$h',
        'HarveyFamily_Toy': 'Сын всю ночь собирал игрушку. А малыш потом играл коробкой. Воспитание продолжается.$h',
        'HarveyFamily_Drawing': '$query PLAYER_HAS_MAIL Current HarveyMemory_Drawing_Birds Received#Три птицы на нашем портрете. Всех зовут «пи». Теперь не перепутаю.$h|На рисунке мы все поместились. Даже очки нарисованы. Хорошая семья.$h',
    }), 'When': FAMILY_WHEN, 'Priority': 'Late + 1'})
    furniture = {}
    for index, (suffix, name) in enumerate(zip(KEEPSAKE_IDS, NAMES)):
        kind, size = ('decor', '2 1') if suffix == 'ModelPlane' else ('painting', '2 2')
        sprite = index * 2
        if suffix in SMALL_KEEPSAKES:
            kind, size, sprite = 'decor', '1 1', SMALL_KEEPSAKES[suffix]
        furniture[f'{M}_Keepsake_{suffix}'] = (
            f'HarveyKeepsake_{suffix}/{kind}/{size}/{size}/1/0/0/{name}/{sprite}/Mods\\{M}\\KeepsakeSprites/true')
    sources = {
        'FamilyDrawing': (f'PLAYER_HAS_SEEN_EVENT Current {NS}.G3_Drawing', 'Рисунок в рамке',
                          'Рамка готова. Зелёного человека поправлять не стал — художник лучше знает.^^— Харви'),
        'ModelPlane': (f'PLAYER_HAS_SEEN_EVENT Current {M}_eventHarveyEveningPlanes', 'Ровное крыло',
                       'Нашёл место для новой модели, а эту хочу отдать тебе. Крыло, которое ты придерживала, до сих пор самое ровное.^^— Харви'),
        'PressedFlower': ('PLAYER_HAS_SEEN_EVENT Current eventHarveyFirstDate', 'С той прогулки',
                          'Этот цветок всё это время лежал в моём блокноте. Попросил Робин сделать маленькую рамку. Пусть будет у тебя.^^— Харви'),
        'AnniversaryNote': ('PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulMarriage.M3_Anniversary', 'Заключение в рамке',
                           'Переписал записку с нашей первой годовщины. Твой ответ тоже сохранил, если он был. На стене ей будет лучше, чем в кармане халата.^^— Харви'),
        'FamilyPhoto': ('PLAYER_HAS_MAIL Current HarveyFamily_PhotoTaken Received', 'Все в кадре',
                       'Снимок напечатал. Никто не смотрит туда, куда я просил, и это лучшая фотография в моей жизни.^^Обнимаю. Аренд'),
        'RingBox': ('PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulCourtship.P1_SecondAsk', 'Пустая коробочка',
                    'Кольцо теперь у тебя на пальце, а коробочка осталась у меня в кармане. Карман без неё непривычно лёгкий.^'
                    'Пусть стоит у тебя на полке. Полгода она ждала правильного дня — пусть теперь его помнит.^^— Твой Харви'),
    }
    mail, triggers = {}, {}
    for suffix, (condition, title, text) in sources.items():
        mail_id = f'{M}_mailKeepsake_{suffix}'
        mail[mail_id] = f'@,^^{text}%item id (F){M}_Keepsake_{suffix} 1%%[#]{title}'
        # Историю повторяемых годовщин Core хранит отдельно: награда доступна и после обновления старого сейва.
        if suffix == 'AnniversaryNote':
            condition = ('ANY "' + condition + '" "PLAYER_HAS_MAIL Current '
                         'HarveyJournal_Seen_HarveyOverhaulMarriage.M3_Anniversary Received"')
        tid = f'{M}_triggerKeepsake_{suffix}'
        triggers[tid] = {'Id': tid, 'Trigger': 'DayStarted',
                         'Condition': f'{condition}, !PLAYER_HAS_MAIL Current {mail_id} Any',
                         'Actions': [f'AddMail Current {mail_id} now']}
    keepsakes = {f'{M}_Keepsake_{suffix}': data for suffix, data in KEEPSAKES.items()}
    assets = [
        {'Action': 'Load', 'Target': f'Mods/{M}/KeepsakeSprites', 'FromFile': 'assets/Furniture/keepsakes.png'},
        patch('Keepsakes — памятная мебель', 'Data/Furniture', furniture),
        patch('Keepsakes — описания и память о выборе', f'Mods/{M}/Keepsakes', keepsakes),
        patch('Keepsakes — письма с предметами', 'Data/Mail', mail),
        patch('Keepsakes — награды за сцены, один раз на сохранение', 'Data/TriggerActions', triggers),
    ]
    return {'Changes': [*family_events, *followups, *assets]}


if __name__ == '__main__':
    path = ROOT / 'assets/Code/familyLife.json'
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('written', path)
