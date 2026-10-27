"""День рождения из Happy Birthday и выходные в Зузу. Все сцены на собственных картах."""
import json
from pathlib import Path

from event_builder import key, msg, patch, qq, script, skip_cd, sp

ROOT = Path(__file__).resolve().parents[1]
M = '{{ModId}}'
PARTY = 'HarveyCelebrationRoom'
NS = 'HarveyOverhaulZuzu'
REL = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married'
ACTIVE = 'GameStateQuery PLAYER_HAS_MAIL Current HarveyZuzu_Active Received'
AR_WHEN = {'HO_OutingArend': 'true'}
NO_AR_WHEN = {'HO_OutingArend': 'false'}


def memory(name):
    return f'action AddMail Current HarveyOutingMemory_{name} Received'


def seen(eid):
    return f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {eid}'


def birthday_key(style):
    return key('HarveyOverhaulBirthday', 'B1_Celebration', 'Time 1700 2500', REL,
               'GameStateQuery PLAYER_HAS_MAIL Current HarveyBirthday_Pending Received',
               f'GameStateQuery PLAYER_HAS_MAIL Current HarveyBirthday_{style} Received', cooldown=False)


def birthday_body(style, arend=False):
    guests = '' if style == 'Quiet' else ' Maru 8 10 1 Evelyn 16 10 3'
    if arend:
        guests += ' Arend 14 12 0'
    lines = ['viewport 12 10 true', 'pause 400']
    if style == 'Quiet':
        lines += [
            msg('В небольшой гостиной горит тёплый свет. Харви поставил на стол торт, две чашки и маленький свёрток.'),
            sp('Harvey', 'С днём рождения, солнышко.$l#$b#Я помню: сегодня ты хотела тихий вечер. Так и будет.$0'),
            sp('Harvey', 'Свечку купил одну. Не для подсчётов — для желания.$h'),
            qq(['Загадать желание', 'Попросить его загадать вместе', 'Сначала попробовать торт'], [
                [msg('Ты задуваешь свечу. Харви старается не спрашивать о желании — и видно, каких усилий ему это стоит.'),
                 sp('Harvey', 'Не рассказывай. Я подожду, пока сбудется.$l'), memory('Birthday_Wish')],
                [sp('Harvey', 'У меня уже есть. Но ещё одно можно.$l'),
                 msg('Он закрывает глаза рядом с тобой. Впервые за вечер не проверяет ничего вокруг.'), memory('Birthday_Together')],
                [sp('Harvey', 'Это разумный порядок. Желания лучше загадываются после ужина.$h'), memory('Birthday_Cake')],
            ]),
        ]
    elif style == 'Family':
        lines += [
            msg('У стола ждут несколько близких людей. Эвелин поправляет салфетки, Мару придерживает подарочный пакет.'),
            sp('Evelyn', 'С днём рождения, милая! Я принесла пирог. Доктор сказал, что торт уже есть, но это совершенно разные вещи.$h'),
            sp('Maru', 'Мы обещали маленький праздник. Честно. Просто у Эвелин очень вместительная корзина.$h'),
            sp('Harvey', 'Ты сегодня садишься первой. Остальное мы уже взяли на себя.$l'),
        ]
        if arend:
            lines += [sp('Arend', 'Я ничего не прятал. Совсем. Особенно вон за той книгой.$h'),
                      sp('Harvey', 'Пап, теперь уже можно не делать вид.$h')]
        lines += [qq(['Поблагодарить всех', 'Предложить рассказать смешную историю', 'Попросить первое слово у Харви'], [
            [sp('Evelyn', 'Хорошо, когда есть повод собраться именно ради тебя.$h'), memory('Birthday_Thanks')],
            [sp('Maru', 'Доктор трижды спросил, достаточно ли одной свечки. В последний раз я предложила провести консилиум.$h'),
             sp('Harvey', 'Я уточнял организационные детали.$h'), memory('Birthday_Story')],
            [sp('Harvey', 'Я много чего хотел сказать. Сейчас смотрю на тебя и помню только главное: как хорошо, что ты у нас есть.$l'),
             memory('Birthday_Words')],
        ])]
    else:
        lines += [
            msg('Харви открывает дверь и подозрительно долго объясняет, куда повесить пальто. За его спиной кто-то сдерживает смех.'),
            sp('Maru', 'С днём рождения! Мы больше не можем ждать — Эвелин уже дважды предложила всем поесть.$h'),
            sp('Evelyn', 'Праздник должен начинаться вовремя. Особенно если на нём есть пирог.$h'),
            sp('Harvey', 'Ты разрешила сюрприз. Я очень старался ничего не выдать.$h'),
        ]
        if arend:
            lines += [sp('Arend', 'Вчера сын оставил список гостей в подарочном пакете. Мы решили, что это приглашение.$h')]
        lines += [qq(['Признаться, что немного подозревала', 'Посмотреть, что в подарочном пакете', 'Обнять Харви'], [
            [sp('Harvey', 'Значит, не всё удалось скрыть. Надеюсь, торт ты всё-таки не заметила заранее.$h'), memory('Birthday_Guessed')],
            [msg('В пакете — открытки с короткими пожеланиями. У Харви исписаны обе стороны.'),
             sp('Maru', 'Мы ограничили его двумя страницами. Иначе праздничная речь заняла бы весь вечер.$h'), memory('Birthday_Cards')],
            [msg('Он обнимает тебя и наконец перестаёт следить, всё ли стоит на своих местах.'),
             sp('Harvey', 'С днём рождения, любимая. Теперь всё получилось.$l'), memory('Birthday_Hug')],
        ])]
    lines += [
        sp('Harvey', 'В этот день у меня всего одно пожелание: пусть у тебя будет больше того, что радует именно тебя.$l'),
        msg('Вечер продолжается за чаем. Харви заворачивает кусочек торта с собой.'),
        'addItem (O)221 1', 'friendship Harvey 40', 'addConversationTopic HarveyBirthday_Celebrated 7',
        'action marilynsinister.HarveyOverhaul.Core_BirthdayComplete',
    ]
    return script('harveys_theme_jazz', '12 10', 'farmer 11 10 1 Harvey 13 10 3' + guests,
                  skip_cd('AddConversationTopic HarveyBirthday_Celebrated 7'), lines)


def trip_key(eid, *conditions):
    return key(NS, eid, ACTIVE, REL, *conditions, cooldown=False)


arrival_key = trip_key('Z1_Arrival', 'Time 0800 2500')
arrival = script('continue', '18 14', 'farmer 17 14 1 Harvey 19 14 3',
    skip_cd('AddConversationTopic HarveyZuzu_Arrived 3'), [
        'viewport 18 14 true', 'pause 500',
        msg('Автобус высаживает вас у небольшой площади. Над крышами гудит город, в фонтане плещется вода.'),
        sp('Harvey', 'Добро пожаловать в Зузу. У меня есть маршрут.$h#$b#Кофейня, книжный и университет. Но его можно нарушать. Это я себе сейчас напоминаю.$0'),
        qq(['Начать с кофе', 'Посмотреть книжный', 'Сначала просто оглядеться'], [
            [sp('Harvey', 'Там меня знают с тех времён, когда я путал завтрак с четвёртой чашкой кофе.$h'), memory('Zuzu_FirstCoffee')],
            [sp('Harvey', 'Справедливое предложение. Если я зависну у полки с авиацией, можешь оставить закладку и идти дальше.$h'), memory('Zuzu_FirstBooks')],
            [sp('Harvey', 'Давай. Я всё время ходил здесь куда-то. А сейчас можно просто побыть.$l'), memory('Zuzu_FirstWalk')],
        ]),
        sp('Harvey', 'Номер уже забронирован. У гостиницы маленькая вывеска справа от площади. Если захочешь домой раньше — скажи.$0'),
        'addConversationTopic HarveyZuzu_Arrived 3',
    ])

cafe_key = trip_key('Z2_Coffee', 'Time 0800 2300', seen(NS+'.Z1_Arrival'))
cafe = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Coffee 5'), [
        'pause 400', msg('Харви останавливается у знакомого столика. На деревянной кромке сохранилась маленькая царапина.'),
        sp('Harvey', 'Я сидел здесь после экзаменов. Иногда заказывал один кофе и занимал стол на три часа.$h'),
        sp('Harvey', 'Здесь же однажды решил, что буду работать в маленьком городе. Хотел знать людей, которые приходят на приём.$0'),
        qq(['Спросить, скучает ли он по городу', 'Показать на царапину', 'Рассказать о своём первом дне в долине'], [
            [sp('Harvey', 'Иногда. По этому столику, библиотеке, запаху дождя у остановки.$0#$b#А потом приезжаю — и понимаю, что уже хочу показать всё тебе.$l'), memory('Zuzu_City')],
            [sp('Harvey', 'Это не я!$u#$b#…Может быть, я. Циркуль для схем был в сумке без колпачка.$h'), memory('Zuzu_Scratch')],
            [msg('Ты рассказываешь, как всё казалось незнакомым. Харви слушает, обхватив чашку ладонями.'),
             sp('Harvey', 'Я рад, что однажды наши дороги привели в одно место.$l'), memory('Zuzu_FirstDay')],
        ]),
        sp('Harvey', 'Посидим ещё? Сегодня никто не ждёт от меня заключения через десять минут.$l'),
        'friendship Harvey 25', 'addConversationTopic HarveyZuzu_Coffee 5',
    ])

books_key = trip_key('Z3_Bookshop', 'Time 0800 2300', seen(NS+'.Z1_Arrival'))
books = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Books 5'), [
        'pause 400', msg('Харви уверенно идёт к дальней полке, потом спохватывается и возвращается к тебе.'),
        sp('Harvey', 'Авиация там. Я только посмотрю. Это не обещание, это намерение.$h'),
        qq(['Выбрать книгу о полётах', 'Показать ему книгу о саде', 'Найти тонкий сборник рассказов'], [
            [msg('Ты снимаешь с полки книгу с потрёпанным самолётом на обложке. Внутри — схемы и карандашные пометки прежнего владельца.'),
             sp('Harvey', 'Вот эту я искал студентом. Она стоила как месяц моих обедов.$s#$b#Сегодня просто возьму. И обед тоже возьмём.$h'), memory('Zuzu_BookPlanes')],
            [sp('Harvey', 'Практическое руководство. Глава первая: не переливать папоротник.$h#$b#Учитывая мои прошлые результаты, очень своевременная книга.$h'), memory('Zuzu_BookGarden')],
            [sp('Harvey', 'Чтобы читать вслух? Хорошая мысль.$l#$b#И никаких медицинских терминов. Даже в предисловии.$h'), memory('Zuzu_BookStories')],
        ]),
        msg('Харви просит положить в пакет две закладки. Одна для тебя, вторая для него.'),
        'friendship Harvey 25', 'addConversationTopic HarveyZuzu_Books 5',
    ])

campus_key = trip_key('Z4_University', 'Time 0900 2000', seen(NS+'.Z1_Arrival'))


def campus_body(arend):
    actors = 'farmer 11 10 1 Harvey 13 10 3' + (' Arend 15 11 3' if arend else '')
    lines = ['pause 400', msg('В университетском читальном зале пахнет бумагой и старым деревом. Харви невольно выпрямляется у доски объявлений.')]
    if arend:
        lines += [sp('Arend', 'Сын. Ты приехал на выходные и всё равно нашёл читальный зал.$h'),
                  sp('Harvey', 'Я показываю город. Мы ненадолго.$0'),
                  sp('Arend', 'Так ты говорил и в семь лет, когда приходил ко мне после школы. Потом мы час искали твои варежки.$h'),
                  qq(['Попросить рассказать ещё', 'Предложить всем выпить чаю', 'Спросить, где Харви сидел после школы'], [
                      [sp('Arend', 'Однажды он принёс дипломную работу. Четыре страницы про то, как лечить игрушечного медведя.$h'), memory('Zuzu_CampusChildhood')],
                      [sp('Arend', 'Вот ради такого предложения я готов отложить красный карандаш.$h'), memory('Zuzu_CampusTea')],
                      [sp('Arend', 'У окна. Ноги не доставали до пола. А вопросы уже были длиннее моих ответов.$0'), memory('Zuzu_CampusWindow')],
                  ]), sp('Arend', 'Погуляйте за меня тоже. Мне ещё две работы читать. До встречи в долине.$0'), 'friendship Arend 25']
    else:
        lines += [sp('Harvey', 'В этом зале я готовился к экзаменам. Казалось, если прочитаю ещё одну главу, перестану волноваться.$0'),
                  qq(['Спросить, помогало ли', 'Найти место у окна', 'Попросить показать старый учебник'], [
                      [sp('Harvey', 'Ровно до следующей главы.$h#$b#Потом научился хотя бы выходить на обед. Не сразу.$0'), memory('Zuzu_CampusStudy')],
                      [msg('Вы на минуту садитесь у окна. Внизу спешат студенты с папками.'),
                       sp('Harvey', 'Я тогда всё откладывал жизнь на после экзаменов. Сейчас стараюсь так не делать.$l'), memory('Zuzu_CampusWindow')],
                      [sp('Harvey', 'Если найду издание с пятном от кофе, возможно, это мой экземпляр.$h'), memory('Zuzu_CampusBook')],
                  ])]
    lines += ['friendship Harvey 25', 'addConversationTopic HarveyZuzu_University 5']
    return script('continue', '12 10', actors, skip_cd('AddConversationTopic HarveyZuzu_University 5'), lines)

BIRTHDAY_TRIP = 'GameStateQuery PLAYER_HAS_MAIL Current HarveyZuzu_HisBirthday Received'
NOT_BIRTHDAY_TRIP = 'GameStateQuery !PLAYER_HAS_MAIL Current HarveyZuzu_HisBirthday Received'
VISITED = 'GameStateQuery PLAYER_HAS_MAIL Current HarveyZuzu_Visited Received'

# Вечер и утро в гостинице в поездку на день рождения Харви уступают место ZB1/ZB2.
night_key = trip_key('Z5_HotelEvening', 'Time 1900 2500', seen(NS+'.Z1_Arrival'), NOT_BIRTHDAY_TRIP)
night = script('harveys_theme_jazz', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Hotel 5'), [
        'pause 500', msg('За окном светятся чужие окна. Харви раскладывает покупки и никак не найдёт место для огромного бумажного пакета.'),
        sp('Harvey', 'Вещей стало больше. Свободного места меньше. Хороший день.$h'),
        sp('Harvey', '$query PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulFamily.G3_Drawing#Хочется потом показать малышу, где мы были. Можно принести открытку.$l|Я раньше думал, что поездка обязательно должна быть ради чего-то важного. Сейчас хорошо и просто так.$l'),
        qq(['Посмотреть в окно вместе', 'Разобрать покупки', 'Спросить, что ему больше понравилось'], [
            [msg('Вы стоите у окна и придумываете истории про освещённые окна напротив.'), memory('Zuzu_Window')],
            [sp('Harvey', '$query PLAYER_HAS_MAIL Current HarveyOutingMemory_Zuzu_BookPlanes Received#Книгу про самолёты кладу наверх. Иначе до утра буду искать её под пирожками.$h|Две закладки, кофе, пакет и почему-то три чека из одного магазина.$h'), memory('Zuzu_Shopping')],
            [sp('Harvey', 'Как ты выбирала, куда свернуть. Я столько лет ходил по одному маршруту, что перестал замечать соседние улицы.$l'), memory('Zuzu_Favourite')],
        ]),
        sp('Harvey', 'Завтра ещё целый день. А сейчас можно отдохнуть. Кровать тут убедительнее моего расписания.$h'),
        'addConversationTopic HarveyZuzu_Hotel 5',
    ])

morning_key = trip_key('Z6_SundayMorning', 'Time 0600 1200',
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyZuzu_Sunday Received', NOT_BIRTHDAY_TRIP)
morning = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Morning 3'), [
        'pause 400', msg('Харви принёс чай и завтрак. Снаружи уже шумят машины, но здесь утро начинается медленно.'),
        sp('Harvey', 'Доброе утро. До обратного автобуса у нас целый день.$l'),
        qq(['Вернуться в любимую кофейню', 'Погулять без маршрута', 'Признаться, что скучаешь по дому'], [
            [sp('Harvey', 'Любимую? Вчера она была моей, теперь нашей. Мне нравится эта поправка.$l'), memory('Zuzu_SundayCafe')],
            [sp('Harvey', 'Убираю карту. Но обратный билет оставлю. На всякий случай.$h'), memory('Zuzu_SundayWalk')],
            [sp('Harvey', 'Тогда можем вернуться раньше. Выходные от этого не станут хуже.$0#$b#А если захочешь ещё погулять — тоже успеем.$l'), memory('Zuzu_SundayHome')],
        ]), 'addConversationTopic HarveyZuzu_Morning 3',
    ])

evening_key = trip_key('Z7_EveningSquare', 'Time 1700 2100', seen(NS+'.Z2_Coffee'), seen(NS+'.Z3_Bookshop'))
evening = script('harveys_theme_jazz', '18 14', 'farmer 17 14 1 Harvey 19 14 3',
    skip_cd('AddConversationTopic HarveyZuzu_Evening 5'), [
        'viewport 18 14 true', 'pause 500', msg('Над площадью загораются огни. Вода в фонтане теперь кажется тёмной.'),
        sp('Harvey', 'Я рад, что приехал сюда с тобой. Теперь у города появились новые воспоминания.$l'),
        qq(['Выбрать место для следующей поездки', 'Предложить вернуться сюда ещё раз', 'Взять его за руку'], [
            [sp('Harvey', 'Выбирай. В этот раз очередь твоих любимых мест.$l'), memory('Zuzu_NextPlace')],
            [sp('Harvey', 'Да. И в следующий раз я сразу пойму, что одного пакета для книжного мало.$h'), memory('Zuzu_ReturnAgain')],
            [msg('Он переплетает пальцы с твоими и некоторое время молчит.'),
             sp('Harvey', 'Вот так и запомню.$l'), memory('Zuzu_Hand')],
        ]), 'friendship Harvey 30', 'addConversationTopic HarveyZuzu_Evening 5',
    ])


# ---------------------------------------------------------------- вторая поездка (флаг Core HarveyZuzu_Visited)
familiar_key = trip_key('Z8_Familiar', 'Time 0800 2500', VISITED, seen(NS+'.Z1_Arrival'))
familiar = script('continue', '18 14', 'farmer 17 14 1 Harvey 19 14 3',
    skip_cd('AddConversationTopic HarveyZuzu_Familiar 5'), [
        'viewport 18 14 true', 'pause 500',
        msg('Та же площадь, тот же фонтан. Только в этот раз Харви не достаёт карту.'),
        sp('Harvey', 'Смешно. В первый раз я вёл тебя по своему городу. А сейчас иду и думаю: вот здесь ты свернула не туда, и это было лучшее «не туда» в моей жизни.$h'),
        qq(['Повести его своим маршрутом', 'Спросить, что он хочет повторить', 'Предложить найти что-то новое'], [
            [sp('Harvey', 'Твоим? У тебя уже есть маршрут по моему городу? …Веди. Я даже не буду спрашивать, где обед.$h'), memory('Zuzu2_HerRoute')],
            [sp('Harvey', 'Столик в кофейне. И окно в гостинице. И ещё раз посмотреть, как ты смеёшься у полки с садоводством.$l'), memory('Zuzu2_Repeat')],
            [sp('Harvey', 'Новое… За все студенческие годы я так и не зашёл на крышу гостиницы. Говорят, оттуда видно весь город.$0'), memory('Zuzu2_New')],
        ]),
        'friendship Harvey 25', 'addConversationTopic HarveyZuzu_Familiar 5',
    ])

regulars_key = trip_key('Z9_Regulars', 'Time 0800 2300', VISITED, seen(NS+'.Z2_Coffee'))
regulars = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Regulars 5'), [
        'pause 400',
        msg('Бариста поднимает голову от кофемашины: «О, вы снова! Вам как в прошлый раз?» На вашем столике кто-то оставил табличку «занято».'),
        sp('Harvey', 'Она нас запомнила. Нас. Не меня — студента с четвёртой чашкой, а нас.$h'),
        sp('Harvey', 'Я годами был здесь «тот, что сидит три часа». А теперь мы «как в прошлый раз». Это лучше.$l'),
        qq(['Заказать как в прошлый раз', 'Попробовать что-то новое', 'Оставить на столике записку'], [
            [sp('Harvey', 'Традиция. У нас уже есть традиции в другом городе. Я врач, а не романтик, но это очень романтично.$h'), memory('Zuzu2_SameOrder')],
            [sp('Harvey', 'Новое? Тогда я тоже. Если не понравится — поменяемся чашками. Так честно.$h'), memory('Zuzu2_NewOrder')],
            [msg('Ты пишешь на салфетке пару слов и прячешь под сахарницу. Харви делает вид, что не подсматривает.'),
             sp('Harvey', 'Что ты написала? …Не говори. Найду в следующий раз. Если её не выбросят — значит, судьба.$l'), memory('Zuzu2_Note')],
        ]),
        'friendship Harvey 25', 'addConversationTopic HarveyZuzu_Regulars 5',
    ])

lecture_key = trip_key('Z10_Lecture', 'Time 0900 2000', VISITED, seen(NS+'.Z4_University'))
lecture = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Lecture 5'), [
        'pause 400',
        msg('На доске объявлений — листок: «Встреча выпускников. Пять минут о своей практике — для студентов первого курса. Записаться здесь».'),
        sp('Harvey', 'Пять минут. О маленькой клинике в долине. Для первокурсников. …Я? Нет. Я заикаюсь, когда говорю не про давление.$u'),
        qq(['Записать его самой', 'Предложить отрепетировать прямо здесь', 'Сказать, что не обязательно'], [
            [msg('Ты пишешь его имя. Харви бледнеет, потом краснеет, потом дописывает рядом: «и фермерша из долины — помощница».'),
             sp('Harvey', 'Раз уж ты меня записала — стой в первом ряду. Мне нужен хотя бы один пульс в зале, который я знаю.$h'), memory('Zuzu2_Signed')],
            [msg('Читальный зал пуст. Харви встаёт у доски и пять минут рассказывает тебе одной про клинику, где знаешь каждого пациента по имени.'),
             sp('Harvey', '…И там я понял, что лечить — это ещё и знать, кто ждёт человека дома. Конец.$s#$b#Как? Слишком сентиментально?$u'), memory('Zuzu2_Rehearsal')],
            [sp('Harvey', 'Не обязательно. Спасибо. Знаешь, мне впервые захотелось — именно потому, что не обязательно.$l'), memory('Zuzu2_NoPressure')],
        ]),
        'friendship Harvey 30', 'addConversationTopic HarveyZuzu_Lecture 5',
    ])

rooftop_key = trip_key('Z11_Rooftop', 'Time 1900 2500', VISITED, seen(NS+'.Z5_HotelEvening'), NOT_BIRTHDAY_TRIP)
rooftop = script('harveys_theme_jazz', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_Rooftop 5'), [
        'pause 500',
        msg('Харви выпросил у портье ключ от крыши. Наверху ветрено, внизу — весь город огнями.'),
        sp('Harvey', 'Вон университет. Вон кофейня — синяя крыша. А там, за горами, где темно, — долина. Наша.$l'),
        sp('Harvey', '$query PLAYER_HAS_MAIL Current HarveyRomance_Radio Received#Рация отсюда до долины не добьёт. Я проверил. Конечно, проверил.$h|Отсюда видно, сколько в мире огней. И только один из них мне нужен.$l'),
        qq(['Сказать, что здесь хорошо', 'Сказать, что хочется домой', 'Молча встать рядом'], [
            [sp('Harvey', 'Хорошо. Но я впервые в этом городе не хочу остаться. Хочу вернуться — с тобой.$l'), memory('Zuzu2_Rooftop_Good')],
            [sp('Harvey', 'Мне тоже. Странно, правда? Раньше дом был здесь. Теперь дом — это куда мы вернёмся завтра.$l'), memory('Zuzu2_Rooftop_Home')],
            [msg('Вы стоите рядом. Ветер треплет его шарф. Он не смотрит на город — смотрит на тебя.'), memory('Zuzu2_Rooftop_Quiet')],
        ]),
        'friendship Harvey 30', 'addConversationTopic HarveyZuzu_Rooftop 5',
    ])

# ---------------------------------------------------------------- поездка на день рождения Харви (выезд 13 зимы)
midnight_key = trip_key('ZB1_Midnight', 'Time 2300 2600', BIRTHDAY_TRIP)
midnight = script('harveys_theme_jazz', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_HisBirthday 7'), [
        'pause 500',
        msg('Без двух минут полночь. Харви думает, что ты уснула. Ты достаёшь из сумки кекс и одну свечку, которую везла через всю долину.'),
        'pause 600', msg('Полночь. Четырнадцатое зимы.'),
        sp('Harvey', '…Ты помнишь. Я думал, мы просто едем на выходные.$u'),
        sp('Harvey', 'Последние годы я встречал день рождения в клинике. Мару пекла кекс, я дежурил. Это было хорошо. Но это…$s'),
        qq(['Попросить загадать желание', 'Сказать, что поездка — и есть подарок', 'Спеть ему шёпотом'], [
            [msg('Он задувает свечу и долго держит глаза закрытыми.'),
             sp('Harvey', 'Я загадал. Не скажу. Но оно про то, чтобы через год было так же.$l'), memory('ZuzuB_Wish')],
            [sp('Harvey', 'Город, в котором я был один, — и ты в нём. Это лучший подарок. Других не нужно. …Но если есть, я не откажусь.$h'), memory('ZuzuB_Trip')],
            [msg('Ты поёшь шёпотом, чтобы не разбудить соседей. Харви смеётся, потом перестаёт смеяться и просто слушает.'),
             sp('Harvey', 'Никто мне не пел с тех пор, как мама… Спасибо. Правда.$s'), memory('ZuzuB_Song')],
        ]),
        'friendship Harvey 50', 'addConversationTopic HarveyZuzu_HisBirthday 7',
    ])

birthday_morning_key = trip_key('ZB2_BirthdayMorning', 'Time 0600 1200', BIRTHDAY_TRIP,
    'GameStateQuery PLAYER_HAS_MAIL Current HarveyZuzu_Sunday Received')
birthday_morning = script('continue', '12 10', 'farmer 11 10 1 Harvey 13 10 3',
    skip_cd('AddConversationTopic HarveyZuzu_HisBirthdayMorning 5'), [
        'pause 400',
        msg('Утро дня рождения. На подносе — завтрак из кофейни «Вторая чашка» и открытка с тремя подписями: Мару, Эвелин и Льюиса.'),
        sp('Harvey', 'Мару написала: «Клиника цела, пациенты живы, с днём рождения, не звоните». Это её любимый стиль.$h'),
        sp('Harvey', 'Можно я сегодня выберу маршрут? Один раз. В свой день рождения.$l'),
        qq(['Согласиться на любой маршрут', 'Предложить снова книжный', 'Предложить просто никуда не спешить'], [
            [sp('Harvey', 'Тогда — авиационный музей. Он маленький, в подвале, туда никто не ходит. Я тоже не ходил: не с кем было.$l'), memory('ZuzuB_Museum')],
            [sp('Harvey', 'Книжный. Ты меня знаешь. И не будешь торопить у полки с авиацией. Это лучший подарок для меня.$h'), memory('ZuzuB_Books')],
            [sp('Harvey', 'Никуда не спешить. В свой день рождения. Я… никогда так не делал. Давай попробуем.$l'), memory('ZuzuB_Slow')],
        ]),
        'friendship Harvey 30', 'addConversationTopic HarveyZuzu_HisBirthdayMorning 5',
    ])


def build():
    changes = []
    for style in ('Quiet', 'Family', 'Surprise'):
        for arend in ([False] if style == 'Quiet' else [False, True]):
            event = patch(f'Birthday — {style}, Arend={arend}', 'Data/Events/'+PARTY,
                          {birthday_key(style): birthday_body(style, arend)})
            if style != 'Quiet': event['When'] = AR_WHEN if arend else NO_AR_WHEN
            changes.append(event)
    for location, event_key, body in [
        ('HarveyZuzuSquare', arrival_key, arrival), ('HarveyZuzuCafe', cafe_key, cafe),
        ('HarveyZuzuBooks', books_key, books), ('HarveyZuzuInn', night_key, night),
        ('HarveyZuzuInn', morning_key, morning), ('HarveyZuzuSquare', evening_key, evening),
        ('HarveyZuzuSquare', familiar_key, familiar), ('HarveyZuzuCafe', regulars_key, regulars),
        ('HarveyZuzuCampus', lecture_key, lecture), ('HarveyZuzuInn', rooftop_key, rooftop),
        ('HarveyZuzuInn', midnight_key, midnight), ('HarveyZuzuInn', birthday_morning_key, birthday_morning),
    ]:
        changes.append(patch('Zuzu — '+event_key.split('/')[0], 'Data/Events/'+location, {event_key: body}))
    for arend in (False, True):
        changes.append({**patch('Zuzu — университет, Arend='+str(arend), 'Data/Events/HarveyZuzuCampus',
                               {campus_key: campus_body(arend)}), 'When': AR_WHEN if arend else NO_AR_WHEN})
    context = {
        'HappyBirthdayToday': 'false',
        'Talk_HarveyZuzuSquare': 'Площадь изменилась меньше, чем я ожидал.$0#$b#Но я впервые стою здесь с тобой. Это многое меняет.$l',
        'Talk_HarveyZuzuCafe': '$query PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulZuzu.Z2_Coffee#Наш столик пока свободен. Закажем ещё по чашке?$h|Пойдём к тому столику. Я хочу кое-что показать.$0',
        'Talk_HarveyZuzuBooks': '$query PLAYER_HAS_MAIL Current HarveyOutingMemory_Zuzu_BookPlanes Received#Они могли привезти продолжение той книги. Я только посмотрю.$h|Две закладки у меня уже есть. Теперь осталось выбрать, в какие книги их положить.$h',
        'Talk_HarveyZuzuCampus': 'У читального зала всё тот же запах бумаги. Сразу хочется говорить тише.$0',
        'Talk_HarveyZuzuInn': 'Кровать, горячая вода и завтра не надо на приём. Я начинаю понимать, зачем люди берут выходные.$h',
        'Place_CafeMenu': 'Кофейня «Вторая чашка». Свежий кофе, выпечка и тот самый столик у дальней стены. Заказать можно у стойки.',
        'Place_PilotBooks': 'Истории первых полётов, модели самолётов и справочники по навигации. Между томами лежит забытая закладка.',
        'Place_GardenBooks': 'Книги о садах и комнатных растениях. На обложке одной обещают помочь даже с самым упрямым папоротником.',
        'Place_UniversityBoard': 'Университет Зузу. Объявления о лекциях, встречах выпускников и студенческом книжном обмене.',
        'Place_UniversityLetter': 'Под стеклом — благодарственные письма преподавателям. У одного листа уголки заклеены уже дважды.',
        'Place_HotelWindow': 'С верхнего этажа видно крыши и огни площади. Субботний номер оплачен. Лечь спать можно у кровати.',
        'Place_CafeSign': 'Кофейня «Вторая чашка». Вход — под синей крышей.',
        'Place_BookSign': 'Книжный «Между строк». Книги и разговоры о книгах.',
        'Place_CampusSign': 'Университет Зузу. Читальный зал открыт для гостей.',
        'Place_InnSign': 'Гостиница «У площади». Ваш номер уже забронирован.',
        'Place_BirthdayCard': 'На открытке почерком Харви: «Сегодня — твой день. Я очень рад быть рядом».',
    }
    changes.append(patch('Outings — диалоги спутника и интерактивных мест', 'Mods/'+M+'/Outings', context))
    changes.append({**patch('Happy Birthday — официальный токен дня рождения', 'Mods/'+M+'/Outings',
                           {'HappyBirthdayToday': '{{Omegasis.HappyBirthday/IsPlayersBirthday}}'}),
                    'When': {'HasMod': 'Omegasis.HappyBirthday',
                             'HasValue:{{Omegasis.HappyBirthday/IsPlayersBirthday}}': 'true'}})
    changes.append(patch('Outings — письма', 'Data/Mail', {
        M+'_mailBirthdayInvitation': '@,^^С днём рождения! Сегодня я приготовил для тебя маленький праздник. '
            'Буду ждать после пяти вечера в гостиной у клиники.^^Если сегодня не получится, перенесём: '
            'приглашение действует ещё неделю.^^Открой меню встреч с Харви (по умолчанию J), '
            'чтобы выбрать формат и пойти на праздник.^^— Харви[#]Твой день',
        M+'_mailHarveyBirthdayHint{{Year}}': '@,^^Пишу тайком. Четырнадцатого зимы у доктора день рождения, и это воскресенье. '
            'Каждый год он дежурит и делает вид, что так и надо.^^Если в субботу, тринадцатого, увезти его в Зузу с утра — '
            'клинику я подменю. Он будет сопротивляться ровно три минуты.^^Только не говори, что это я придумала.^^— Мару[#]Тайный план',
        M+'_mailZuzuInvitation': '@,^^Хочу показать тебе Зузу: кофейню, книжный и университет. '
            'Можем выбрать свободные выходные и остаться на одну ночь.^^Выезд в субботу с 8 до 13 часов '
            'с автобусной остановки, если на выходных нет праздников. Меню встреч — по умолчанию J. '
            'Вернуться раньше всегда можно.^^— Харви[#]Выходные вдвоём',
    }))
    changes.append(patch('Outings — приглашение в Зузу', 'Data/TriggerActions', {
        M+'_triggerZuzuInvitation': {'Id': M+'_triggerZuzuInvitation', 'Trigger': 'DayStarted',
            'Condition': 'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married',
            'Actions': ['AddMail Current '+M+'_mailZuzuInvitation now']},
        # Подсказка Мару о поездке на день рождения Харви — раз в год, если вы уже знаете дорогу в Зузу.
        M+'_triggerHarveyBirthdayHint': {'Id': M+'_triggerHarveyBirthdayHint', 'Trigger': 'DayStarted',
            'Condition': 'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married, SEASON winter, DAY_OF_MONTH 6 7 8 9 10 11 12, '
                         'PLAYER_HAS_MAIL Current '+M+'_mailZuzuInvitation Received, '
                         '!PLAYER_HAS_MAIL Current '+M+'_mailHarveyBirthdayHint{{Year}} Any',
            'Actions': ['AddMail Current '+M+'_mailHarveyBirthdayHint{{Year}} now'], 'MarkActionApplied': False},
    }))
    topics = {
        'HarveyBirthday_Celebrated': 'Мне очень хотелось, чтобы этот вечер тебе понравился. Спасибо, что провела его со мной.$l',
        'HarveyZuzu_Arrived': 'Я принёс карту, а ты нашла дорогу без неё. Признаю: так было интереснее.$h',
        'HarveyZuzu_Coffee': 'Теперь у того столика есть ещё одна история. Наша.$l',
        'HarveyZuzu_Books': '$query PLAYER_HAS_MAIL Current HarveyOutingMemory_Zuzu_BookPlanes Received#Книгу про самолёты уже начал. На первой странице мне снова девятнадцать.$h|Закладку положил в новую книгу. Вторую оставил для тебя.$l',
        'HarveyZuzu_University': 'После университета я всё-таки перестал выпрямляться у каждой доски объявлений. Почти.$h',
        'HarveyZuzu_Hotel': 'Тот вечер у окна я буду помнить дольше всех чеков и билетов.$l',
        'HarveyZuzu_Morning': 'Мне понравилось никуда не торопиться утром. Кажется, стоит повторять это и дома.$l',
        'HarveyZuzu_Evening': 'Город тот же, а воспоминания теперь другие. Спасибо тебе.$l',
        'HarveyZuzu_Familiar': 'Во второй раз город уже не мой. Он наш. Я даже купил вторую карту — для тебя. Ты её, конечно, не откроешь.$h',
        'HarveyZuzu_Regulars': '$query PLAYER_HAS_MAIL Current HarveyOutingMemory_Zuzu2_Note Received#Я всё думаю, что ты написала на той салфетке. Не говори. Приедем — проверю.$h|«Как в прошлый раз». Я повторяю это про себя и улыбаюсь. Мару думает, у меня новый пациент.$h',
        'HarveyZuzu_Lecture': '$query PLAYER_HAS_MAIL Current HarveyOutingMemory_Zuzu2_Signed Received#Мне пришло письмо из университета: ждут на встрече выпускников. Я в ужасе. И немного горжусь.$h|Ты была лучшей аудиторией. Одна, в первом ряду, и ни разу не посмотрела на часы.$l',
        'HarveyZuzu_Rooftop': 'Ключ от крыши я вернул портье. Но вид оттуда оставил себе. И тебя на его фоне.$l',
        'HarveyZuzu_HisBirthday': 'Я никому не сказал, что ты увезла меня на день рождения. Хочу, чтобы это было только наше. Мару, правда, догадалась.$l',
        'HarveyZuzu_HisBirthdayMorning': 'Лучший день рождения. Я не дежурил, не проверял телефон и ни разу не спросил, ела ли ты. …Ладно, один раз спросил.$h',
        'HarveyZuzu_Returned': 'Покупки разобрал. Билеты оставил на память. Следующие выходные пока не планирую — но очень хочется.$h',
    }
    changes.append({**patch('Outings — Харви после праздника и поездки', 'Characters/Dialogue/Harvey', topics),
                    'Priority': 'Late + 2', 'When': {'Relationship:Harvey': 'Dating, Engaged, Married'}})
    changes.append({**patch('Outings — Аренд после университетской встречи', 'Characters/Dialogue/Arend', {
        'HarveyZuzu_University': 'Сын привёл тебя в читальный зал. Хорошо, что нашёл время и для прогулки.$h'}),
        'Priority': 'Late + 2', 'When': {'ArendEnabled': 'true'}})
    locations = {}
    names = {'HarveyCelebrationRoom': 'Праздничная гостиная', 'HarveyZuzuSquare': 'Зузу — университетская площадь',
             'HarveyZuzuCafe': 'Кофейня «Вторая чашка»', 'HarveyZuzuBooks': 'Книжный «Между строк»',
             'HarveyZuzuCampus': 'Университет Зузу', 'HarveyZuzuInn': 'Гостиница «У площади»'}
    for location, title in names.items():
        changes.append({'Action': 'Load', 'Target': 'Maps/'+location, 'FromFile': 'assets/Maps/'+location+'.tmx'})
        locations[location] = {'DisplayName': title, 'DefaultArrivalTile': {'X': 18 if location == 'HarveyZuzuSquare' else 12,
            'Y': 23 if location == 'HarveyZuzuSquare' else 15}, 'CreateOnLoad': {'MapPath': 'Maps/'+location},
            'CanPlantHere': False, 'CanHaveGreenRainSpawns': False, 'ExcludeFromNpcPathfinding': True,
            'MinDailyWeeds': 0, 'MaxDailyWeeds': 0}
    changes.append({'Action': 'Load', 'Target': 'Maps/outingSigns', 'FromFile': 'assets/Maps/outingSigns.png'})
    changes.append(patch('Outings — отдельные локации, сохраняются и при выключении поездок', 'Data/Locations', locations))
    changes.append(patch('Outings — магазин кофейни', 'Data/Shops', {
        M+'_ZuzuCafe': {'Items': [{'Id': 'Coffee', 'ItemId': '(O)395', 'Price': 300},
                               {'Id': 'Bread', 'ItemId': '(O)216', 'Price': 120},
                               {'Id': 'Cake', 'ItemId': '(O)220', 'Price': 500}]},
    }))
    return {'Changes': changes}


if __name__ == '__main__':
    path = ROOT / 'assets/Code/outings.json'
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('written', path)
