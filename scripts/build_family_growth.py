"""Генерирует assets/Code/familyGrowth.json — «дети растут» (этап 4 roadmap).

Спрайт ребёнка в игре дальше стадии «ходит» не растёт, поэтому растёт история: Core ставит флаги
HarveyFamily_ChildYear1…3 по числу полных игровых лет с рождения (HarveyFamilyLifeService.ChildYears).
Ребёнок в сценах — временный актёр со спрайтом настоящего (как G1–G3, build_family_life.py).

  K1 «Первое слово»     FarmHouse, 17–21, ребёнок уже ходит — первое слово «стоп».
  K2 «Коленка»          Farm, крыльцо, ясно, 10–16, год — первая ссадина; Харви учится не спешить.
  K3 «Первый год»       FarmHouse, 18–22, год, после K1 — свеча и торт. С Арендом / без.
  K4 «Сказка на ночь»   FarmHouse, 19–22, два года — с Арендом про птиц / Харви читает анатомию «для самых маленьких».
  K5 «Кружок у фонтана» Town, ясно, вт/чт 10–14, три года — Пенни читает детям; Харви учится отпускать.

Запуск:  python scripts/build_family_growth.py
"""
import json
import os

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp
from build_family_life import MARRIED, READY, child, flag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'familyGrowth.json')
NS = 'HarveyOverhaulFamily'
A = 'Arend'
FX, FY0, FY1, FY3, FY5 = '{{HO_FarmX}}', '{{HO_FarmY0}}', '{{HO_FarmY1}}', '{{HO_FarmY3}}', '{{HO_FarmY5}}'
ARRIVAL = 'HarveyOverhaulArend.A1_Arrival'
WITH_AREND = {'ArendEnabled': 'true', f'HasSeenEvent |contains={ARRIVAL}': 'true'}
NO_AREND = [{'ArendEnabled': 'false'}, {'ArendEnabled': 'true', f'HasSeenEvent |contains={ARRIVAL}': 'false'}]


def year(n):
    return f'GameStateQuery PLAYER_HAS_MAIL Current HarveyFamily_ChildYear{n} Received'


def seen(eid):
    return f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}'


# ================================================================ K1 «Первое слово»
k1_key = key(NS, 'K1_FirstWord', 'Time 1700 2100', MARRIED, READY)
k1 = script('continue', '12 7', 'farmer 11 7 1 Harvey 13 6 2',
    skip_cd('AddConversationTopic HarveyFamily_FirstWord 7'), [
        child(12, 7, 1), 'pause 500',
        msg('Вечер. Малыш сидит на полу среди кубиков. Харви подходит с градусником — «только проверить, лоб тёплый».'),
        sp(H, 'Секунду. Одну секундочку. Под мышку, и всё…$0'),
        msg('Малыш отодвигается, поднимает ладошку — точь-в-точь как ты — и очень отчётливо говорит:'),
        msg('«Стоп!»'),
        'pause 600', 'emote Harvey 16',
        sp(H, '…Это было слово? Это было слово. Первое слово.$u'),
        sp(H, 'И это «стоп».$s#$b#…Ну конечно. Он слышал его от тебя — каждый раз, когда я перегибал.$h'),
        qq(['Рассмеяться', 'Сказать, что это хорошее первое слово', 'Убрать градусник вместе с ним'], [
            ['emote farmer 28', sp(H, 'Смейся. Я запишу в карту: «Первое слово — ограничитель. Пациент уважает границы с рождения».$h'),
             flag('FirstWord_Laugh')],
            [sp(H, 'Хорошее. Правда. Значит, наш ребёнок знает, что его «нет» слышат.$l#$b#Это лучше, чем «папа». Ладно, почти.$h'),
             flag('FirstWord_Good')],
            [msg('Ты кладёшь градусник в футляр. Харви, помедлив, защёлкивает крышку сам.'),
             sp(H, 'Убрал. Лоб я потрогаю губами, как все нормальные родители. Это ведь тоже считается.$l'), flag('FirstWord_Thermometer')],
        ]),
        'friendship Harvey 40', 'addConversationTopic HarveyFamily_FirstWord 7',
    ])

# ================================================================ K2 «Коленка»
k2_key = key(NS, 'K2_Knee', 'Weather sunny', 'Time 1000 1600', MARRIED, READY, year(1))
k2 = script('continue', f'{FX} {FY0}', f'farmer {FX} {FY1} 2 Harvey {FX} {FY5} 0',
    skip_cd('AddConversationTopic HarveyFamily_Knee 7'), [
        child('{{HO_FarmX}}', '{{HO_FarmY3}}', 2), 'pause 500',
        msg('Малыш бежит к курятнику, спотыкается о порог — и садится прямо на дорожку. Тишина. Потом — громкий рёв.'),
        'emote Harvey 16',
        msg('Харви уже бежит: сумка через плечо, бинт, антисептик, фонарик — хотя на дворе полдень.'),
        'move Harvey 0 -1 0',
        sp(H, 'Так. Спокойно. Я спокоен. Колено, ссадина, кровь… две капли. Две капли крови.$u'),
        qq(['Положить ладонь ему на плечо', 'Спросить малыша, где болит', 'Подуть на коленку'], [
            [msg('Ты кладёшь руку ему на плечо. Он выдыхает — впервые с того момента, как услышал рёв.'),
             sp(H, 'Да. Ты права. Сначала — я. Испуганный врач лечит хуже.$s'),
             msg('Он промывает ссадину неторопливо, приговаривая что-то смешное. Рёв стихает.'), flag('Knee_Calm')],
            [msg('Малыш перестаёт плакать от удивления, что его спросили, и показывает пальцем: «Тут».'),
             sp(H, 'Вот. Пациент локализует боль сам. Анамнез собран. Учусь у тебя, как с ним говорить.$h'), flag('Knee_Asked')],
            [msg('Ты дуешь на коленку. Малыш смеётся сквозь слёзы. Харви смотрит на вас с раскрытым бинтом.'),
             sp(H, 'Этого метода нет ни в одном учебнике. И он работает лучше половины учебников.$l'), flag('Knee_Blow')],
        ]),
        msg('Пластырь со звёздочкой. Малыш тут же убегает обратно к курятнику.'),
        sp(H, 'Он упадёт ещё сто раз. Я знаю. Царапина — это тоже детство.$s#$b#…Но сумку я всё-таки повешу у двери.$h'),
        'friendship Harvey 35', 'addConversationTopic HarveyFamily_Knee 7',
    ])


# ================================================================ K3 «Первый год» (с Арендом / без)
def k3(arend):
    actors = 'farmer 11 7 1 Harvey 13 6 2' + (f' {A} 14 7 3' if arend else '')
    extra = ([sp(A, 'Год. Я принёс книгу про птиц. Читать ещё рано, но смотреть картинки — самое время.$h'),
              sp(H, 'Пап, там четыреста страниц.$a'), sp(A, 'Значит, хватит до школы.$h')] if arend else
             [sp(H, 'Папа звонил утром. Сказал передать: «Год — это много. Каждый следующий будет ещё больше».$l')])
    return script('harveys_theme_jazz', '12 7', actors, skip_cd('AddConversationTopic HarveyFamily_FirstYear 7'), [
        child(12, 7, 1), 'pause 500',
        msg('На столе — маленький торт с одной свечой. Харви трижды переставил его, чтобы малыш не дотянулся до пламени.'),
        sp(H, 'Год. Целый год. Я помню, как считал вдохи у колыбели в первую ночь.$s'),
        *extra,
        qq(['Задуть свечу вместе с малышом', 'Сфотографировать их двоих', 'Обнять Харви'], [
            [msg('Вы дуете вместе. Свеча гаснет с третьей попытки, малыш хлопает в ладоши.'),
             sp(H, 'Загадали? Я — да. То же, что и в прошлом году. Сбывается.$l'), flag('FirstYear_Candle')],
            [msg('Харви держит малыша на коленях и смотрит не в объектив, а на него.'),
             sp(H, 'Получилось? Я, наверное, опять смотрел не туда.$h'), flag('FirstYear_Photo')],
            [msg('Ты обнимаешь его со спины. Он накрывает твои руки своими.'),
             sp(H, 'Спасибо за этот год. За все наши годы. Но за этот — особенно.$l'), flag('FirstYear_Hug')],
        ]),
        'friendship Harvey 40', *(['friendship Arend 30'] if arend else []),
        'addConversationTopic HarveyFamily_FirstYear 7',
    ])


k3_key = key(NS, 'K3_FirstYear', 'Time 1800 2200', MARRIED, READY, year(1), seen('K1_FirstWord'))


# ================================================================ K4 «Сказка на ночь» (с Арендом / без)
def k4(arend):
    if arend:
        actors = 'farmer 11 7 1 Harvey 13 6 2 Arend 14 7 3'
        body = [
            msg('Аренд сидит на краю кровати с книгой про птиц. Малыш уже не слушает — он показывает картинки сам.'),
            sp(A, 'Это сорока. А это… да, ты прав, тоже «пи». Все птицы — «пи». Научная классификация меняется.$h'),
            sp(H, 'Пап, ему пора спать. Это уже пятая птица.$0'),
            sp(A, 'Шестая. Ты в его возрасте выпросил одиннадцать.$h'),
            qq(['Попросить ещё одну птицу', 'Тихо выключить лампу', 'Сесть рядом и слушать'], [
                [sp(A, 'Последняя. Цапля. Она стоит на одной ноге, пока все спят. Вот и ты спи, а цапля постоит.$l'), flag('Story_Heron')],
                [msg('Ты гасишь свет. Аренд дочитывает по памяти — тихо, почти шёпотом.'), flag('Story_Lamp')],
                [msg('Вы втроём сидите у кровати, пока дыхание малыша не становится ровным. Харви по привычке считает вдохи — и не мешает.'),
                 flag('Story_Together')],
            ]),
            sp(A, 'Он запомнит не птиц. Он запомнит, что рядом сидели. Ты тоже запомнил, сын.$l'),
            'friendship Arend 30',
        ]
    else:
        actors = 'farmer 11 7 1 Harvey 13 6 2'
        body = [
            msg('Харви читает малышу на ночь. Книга подозрительно похожа на анатомический атлас — с картинками.'),
            sp(H, '«Сердце — это мышца, которая работает всю жизнь и никогда не берёт выходной». …Хм. Как некоторые врачи.$h'),
            qq(['Предложить сказку про самолёт', 'Читать дальше вместе с ним', 'Забрать атлас и рассказать свою'], [
                [sp(H, 'Про самолёт… который однажды упал в озеро и был самым счастливым самолётом на свете. Хорошо. Эту я знаю наизусть.$l'), flag('Story_Plane')],
                [msg('Вы читаете по очереди. На главе про лёгкие малыш засыпает, держа палец на картинке.'),
                 sp(H, 'Будущий коллега. Или просто устал. Скорее второе.$h'), flag('Story_Atlas')],
                [msg('Ты рассказываешь, как пришла в долину и встретила доктора с бутербродами у остановки.'),
                 sp(H, 'Это лучшая сказка. И она правда случилась.$l'), flag('Story_Ours')],
            ]),
        ]
    return script('none', '12 7', actors, skip_cd('AddConversationTopic HarveyFamily_Story 7'), [
        child(12, 7, 0), 'pause 500', *body,
        'friendship Harvey 35', 'addConversationTopic HarveyFamily_Story 7',
    ])


k4_key = key(NS, 'K4_Story', 'Time 1900 2200', MARRIED, READY, year(2))

# ================================================================ K5 «Кружок у фонтана»
k5_key = key(NS, 'K5_StoryCircle', 'DayOfWeek Tue Thu', 'Weather sunny', 'Time 1000 1400', MARRIED, READY, year(3),
             seen('K1_FirstWord'))
k5 = script('continue', '27 29', 'farmer 29 31 3 Harvey 30 31 3 Penny 26 29 2 Jas 25 31 0 Vincent 27 31 0',
    skip_cd('AddConversationTopic HarveyFamily_StoryCircle 7'), [
        child(26, 31, 0), 'viewport 27 29 true', 'pause 500',
        msg('У фонтана — кружок Пенни. Джас и Винсент уже сидят на подушках. Твой малыш — впервые среди них.'),
        sp('Penny', 'Сегодня читаем про ёжика, который боялся темноты. Родители могут посидеть рядом — или погулять. Мы справимся.$h'),
        msg('Харви не двигается с места. Он стоит в трёх шагах и считает, сколько метров до фонтана.'),
        sp(H, 'Три метра. Бортик гладкий. Вода по колено взрослому… Пенни, вы знаете, где у вас аптечка?$u'),
        sp('Penny', 'Знаю, доктор. Вы сами её подписывали в прошлом году.$h'),
        qq(['Взять его под руку и увести на скамейку', 'Сказать, что малыш справится', 'Остаться, но на расстоянии'], [
            ['move farmer -1 0 3', msg('Ты берёшь его под руку. Он идёт, но оглядывается каждые два шага.'),
             sp(H, 'Скамейка. Хорошо. Отсюда видно. Видно же?$s#$b#…Видно. Он смеётся. Он не на меня смотрит — и смеётся.$l'),
             flag('Circle_Bench')],
            [sp(H, 'Справится. Он сказал «стоп» раньше, чем «папа». Он умеет за себя постоять.$s#$b#А я — нет. Учусь.$h'),
             flag('Circle_Trust')],
            [msg('Вы остаётесь в стороне. Через десять минут малыш оборачивается, машет вам — и снова поворачивается к Пенни.'),
             sp(H, 'Он помахал. Это значит «я в порядке». Мы его этому не учили. Сам.$l'), flag('Circle_Wave')],
        ]),
        sp('Penny', 'Приходите в четверг. Ёжик ещё не дочитан, а ваш — уже наш постоянный слушатель.$h'),
        'friendship Harvey 40', 'friendship Penny 30', 'addConversationTopic HarveyFamily_StoryCircle 7',
    ])


def build():
    changes = [
        patch('Family K1 — «Первое слово» (FarmHouse)', 'Data/Events/FarmHouse', {k1_key: k1}),
        patch('Family K2 — «Коленка» (Farm)', 'Data/Events/Farm', {k2_key: k2}),
        patch('Family K5 — «Кружок у фонтана» (Town)', 'Data/Events/Town', {k5_key: k5}),
        {**patch('Family K3 — «Первый год», с Арендом', 'Data/Events/FarmHouse', {k3_key: k3(True)}), 'When': WITH_AREND},
        {**patch('Family K4 — «Сказка на ночь», с Арендом', 'Data/Events/FarmHouse', {k4_key: k4(True)}), 'When': WITH_AREND},
    ]
    for i, when in enumerate(NO_AREND, start=1):
        changes.append({**patch(f'Family K3 — «Первый год», без Аренда ({i})', 'Data/Events/FarmHouse', {k3_key: k3(False)}), 'When': when})
        changes.append({**patch(f'Family K4 — «Сказка на ночь», без Аренда ({i})', 'Data/Events/FarmHouse', {k4_key: k4(False)}), 'When': when})
    harvey = {
        'HarveyFamily_FirstWord': '$query PLAYER_HAS_MAIL Current HarveyMemory_FirstWord_Thermometer Received#Градусник лежит в футляре третий день. Я держусь. Лоб проверяю губами, как договорились.$h|Сегодня малыш сказал «стоп» коту. Кот послушался. Я горжусь обоими.$h',
        'HarveyFamily_Knee': 'Пластыри со звёздочками кончились. Я заказал коробку. Нет, две. Это не паника, это снабжение.$h',
        'HarveyFamily_FirstYear': 'Год назад я считал вдохи у колыбели. Сегодня меня за палец ведут смотреть кур. Время — странная штука.$l',
        'HarveyFamily_Story': '$query PLAYER_HAS_MAIL Current HarveyMemory_Story_Plane Received#Малыш просит сказку про самолёт в озере каждый вечер. Я рассказываю. Каждый раз чуть смешнее.$h|Вчера он показал пальцем на мою грудь и сказал «серце». Почти правильно. Почти коллега.$h',
        'HarveyFamily_StoryCircle': 'Ёжика дочитали. Малыш теперь рассказывает его мне — со своими поправками. Ёжик у него больше не боится темноты: у него есть фонарь.$l',
    }
    arend = {
        'HarveyFamily_FirstYear': 'Год. Я подарил книгу про птиц, а малыш съел угол обложки. Хорошая рецензия.$h',
        'HarveyFamily_Story': 'Внук назвал цаплю «пи». Я не стал спорить. В его возрасте это и есть орнитология.$h',
        'HarveyFamily_StoryCircle': 'Сын рассказал про кружок у фонтана. Сказал: «Я стоял на скамейке, пап». Понимаешь? На скамейке. Не рядом.$l',
    }
    penny = {'HarveyFamily_StoryCircle': 'Ваш малыш сегодня первым поднял руку. Спросил, есть ли у ёжика доктор. Угадайте, в кого.$h'}
    changes += [
        {**patch('Family K — Харви о взрослеющем малыше', 'Characters/Dialogue/Harvey', harvey),
         'Priority': 'Late + 1', 'When': {'Relationship:Harvey': 'Married'}},
        {**patch('Family K — Аренд о внуке', 'Characters/Dialogue/Arend', arend), 'Priority': 'Late + 1', 'When': {'ArendEnabled': 'true'}},
        {**patch('Family K5 — Пенни о кружке', 'Characters/Dialogue/Penny', penny), 'Priority': 'Late + 1'},
    ]
    return {'Changes': changes}


if __name__ == '__main__':
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
    print('written', OUT, 'events: K1–K5')
