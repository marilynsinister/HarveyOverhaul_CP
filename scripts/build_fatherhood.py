"""Генерирует assets/Code/fatherhood.json — Харви-отец (брак, в доме есть ребёнок).

Всё подключается только при «Relationship:Harvey: Married» и непустом токене ChildNames.
Тексты не говорят, кто родил: у пары с Харви ребёнок может быть и усыновлённым.

  Список у колыбели   утро после появления ребёнка: записка Харви + тема HarveyFather_NewBaby (7 дней);
                      на эту тему поздравляют Эвелин, Джоди и Мару.
  P1 «Первая ночь»    FarmHouse, 22:00–2:00: Харви не спит у детской и считает вдохи.
                      Забрать у него часы / слушать вместе / дежурить по очереди.
  P2 «Радионяня»      Hospital, 9:00–15:00, после P1: радионяня на два километра и Мару, которая засекает время.
  Домашние реплики    HarveyMod_Spouse_*_Kids_* — Injury (DomesticSpouseCareManager) берёт их, когда в доме
                      есть ребёнок, примерно в трети случаев вместо обычного слоя.

Тон — docs/harvey-relationship-tone-guide.md: он тревожится, но не командует; она помогает ему выдохнуть.
Запуск:  python scripts/build_fatherhood.py
"""
import json
import os

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'fatherhood.json')

NS = 'HarveyOverhaulFather'
M = '{{ModId}}'
MARRIED = 'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married'
LIST_MAIL = f'{M}_mailFatherList'
WHEN = {'Relationship:Harvey': 'Married', 'HasValue:{{ChildNames}}': 'true'}

# ---------------------------------------------------------------- P1
p1_key = key(NS, 'P1_FirstNight', 'Time 2200 2600', MARRIED,
             f'GameStateQuery PLAYER_HAS_MAIL Current {LIST_MAIL} Received')
p1 = script(
    'none', '12 7', 'farmer 11 6 1 Harvey 13 6 3',
    skip_cd('AddConversationTopic HarveyFather_FirstNight 7'),
    [
        'ambientLight 60 60 90', 'viewport 12 7 true', 'pause 600',
        msg('Глубокая ночь. Из детской — тишина. Харви стоит у двери с часами в руке и не моргает.'),
        sp(H, 'Двадцать два вдоха в минуту. Норма.$0#$b#Я знаю, что норма. Я проверил двенадцать раз.$s'),
        sp(H, 'Котёнок, иди спать. Я посижу ещё немного. Только послушаю.$s'),
        qq(['Забрать у него часы', 'Сесть рядом и слушать вместе', '«Давай по очереди: два часа ты, два — я»'], [
            [msg('Ты осторожно вынимаешь часы из его пальцев. Он не сопротивляется.'),
             sp(H, '…Ты права. Если я не высплюсь, завтра перепутаю пластырь с рецептом.$h#$b#Пять минут. Потом ляжем.$0'),
             'friendship Harvey 30'],
            [msg('Вы садитесь на пол у детской. В темноте слышно, как малыш сопит.'),
             sp(H, 'Слышишь? Вдох, выдох. Самый лучший звук на свете.$l#$b#Я слышал тысячи сердец. Ни одно не было таким громким.$l'),
             'friendship Harvey 40'],
            [sp(H, 'По очереди. Как дежурства.$h#$b#Это очень разумно. Почему я сам не придумал?$h'),
             msg('Он пишет расписание на обороте рецептурного бланка — и засыпает, не дописав второй строчки.'),
             'friendship Harvey 35'],
        ]),
        sp(H, 'Спасибо, что ты со мной. Я так боюсь ошибиться — и так счастлив, что даже бояться приятно.$l'),
        'addConversationTopic HarveyFather_FirstNight 7',
    ])

# ---------------------------------------------------------------- P2
p2_key = key(NS, 'P2_BabyMonitor', 'Time 0900 1500', MARRIED,
             f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.P1_FirstNight')
p2 = script(
    'Hospital_Ambient', '11 16', 'Harvey 13 16 1 Maru 14 16 3 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyFather_Monitor 5'),
    [
        'viewport 11 16 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -2 1', 'pause 300',
        msg('В клинике непривычно тихо. Харви склонился над маленькой коробочкой с антенной. Мару закатывает глаза.'),
        sp('Maru', 'Доктор купил радионяню. Мощную. Она ловит даже палатку Линуса.$h'),
        sp(H, 'Она ловит наш дом. Радиус два километра — я рассчитал.$a'),
        sp('Maru', '@, он проверяет её каждые четыре минуты. Я засекала.$s'),
        'faceDirection Harvey 3',
        sp(H, '…Каждые пять.$s'),
        qq(['Взять радионяню себе на час', 'Послушать вместе', '«Малыш спит. А ты обедал?»'], [
            [msg('Ты кладёшь радионяню в карман.'),
             sp(H, 'Хорошо. Час. Если что-то услышишь — сразу ко мне.$u#$b#…Это было «хорошо» сквозь зубы. Но хорошо.$h'),
             sp('Maru', 'Спасибо! Наконец-то можно работать.$h'),
             'friendship Harvey 25', 'friendship Maru 30'],
            [msg('Вы слушаете вместе. Из коробочки доносится тихое сопение — и, кажется, чей-то храп.'),
             sp(H, 'Это… это не малыш.$a'),
             sp('Maru', 'Я же говорила! Это Линус.$h'),
             'friendship Harvey 30', 'friendship Maru 20'],
            [sp(H, 'Обед… А, обед. Был такой.$s'),
             msg('Ты ставишь перед ним контейнер с едой. Мару беззвучно аплодирует.'),
             sp(H, 'Справедливо. Отец, который падает в обморок от голода, — так себе отец.$h'),
             'friendship Harvey 35'],
        ]),
        'addConversationTopic HarveyFather_Monitor 5',
    ])

# ---------------------------------------------------------------- данные
MAIL = {
    LIST_MAIL: ('@,^^Пишу это ночью у колыбели. Список — на всякий случай:^^'
                '1. Спать, когда спит малыш. Это не совет, это рецепт.^'
                '2. Есть. Да, даже если некогда.^'
                '3. Звать меня. Даже по пустякам. Особенно по пустякам.^^'
                'И ещё: у тебя всё получается. Я смотрю на вас двоих — и не верю своему счастью.^^'
                '— Харви[#]Список у колыбели'),
}

TRIGGERS = {
    f'{M}_triggerFatherList': {
        'Id': f'{M}_triggerFatherList', 'Trigger': 'DayStarted',
        'Condition': f'PLAYER_NPC_RELATIONSHIP Current Harvey Married, !PLAYER_HAS_MAIL Current {LIST_MAIL} Any',
        'Actions': [f'AddMail Current {LIST_MAIL} now', 'AddConversationTopic HarveyFather_NewBaby 7'],
    },
}

TOPICS = {
    'HarveyFather_NewBaby': 'Я видел сотни новорождённых. А на нашего смотрю — и забываю всё, что знаю.$l#$b#Малыш здоров. Я проверил. Трижды. Ладно, пять раз.$h',
    'HarveyFather_FirstNight': 'Я спал. Четыре часа подряд. Это рекорд месяца.$h#$b#Спасибо за вчерашнее. Мне правда стало легче.$l',
    'HarveyFather_Monitor': 'Радионяня лежит на полке. Я смотрю на неё всего раз в десять минут. Прогресс?$h',
}

NPC_CONGRATS = {
    'Evelyn': 'Малыш! У тебя и у доктора!$h#$b#Я связала две шапочки: одну малышу, другую Харви. Он теперь тоже будет спать урывками.$h',
    'Jodi': 'Поздравляю!$h#$b#Если Харви начнёт мерить малышу температуру каждый час — зови меня. Я через это прошла с Сэмом.$h',
    'Maru': 'Поздравляю!$h#$b#Доктор сегодня три раза назвал меня «малыш». Он счастлив и совсем не спит.$h',
}

# Домашние реплики (Injury → DomesticSpouseCareManager, префикс HarveyMod_Spouse_<время>_Kids).
DOMESTIC = {
    'HarveyMod_Spouse_EarlyMorning_Kids_0': 'Тише… малыш только уснул. Я сварил кофе на двоих. Шёпотом.$l',
    'HarveyMod_Spouse_EarlyMorning_Kids_1': 'Я встал к малышу в пять. Ты спи ещё. Нет, серьёзно — это моя смена.$h',
    'HarveyMod_Spouse_Morning_Kids_0': 'Малыш поел, срыгнул и посмотрел на меня как на идиота. По-моему, мы подружились.$h',
    'HarveyMod_Spouse_Morning_Kids_1': 'Температура тридцать шесть и шесть. Да, я померил. Да, просто так. Да, я знаю.$h',
    'HarveyMod_Spouse_Morning_Kids_2': 'Не забудь поесть сама. Малыш накормлен — теперь очередь его родителей.$0',
    'HarveyMod_Spouse_Evening_Kids_0': 'Он схватил меня за палец. Крепко. Я врач, я знаю, что это рефлекс. Мне всё равно.$l',
    'HarveyMod_Spouse_Evening_Kids_1': 'Я прочитал малышу статью о кровообращении. Уснул на второй странице. Строгий критик растёт.$h',
    'HarveyMod_Spouse_Evening_Kids_2': 'Посиди с нами. Просто посиди. Я хочу запомнить этот вечер.$l',
    'HarveyMod_Spouse_LateNight_Kids_0': 'Если он проснётся — встану я. Ты сегодня работала весь день. Спи, котёнок.$l',
    'HarveyMod_Spouse_LateNight_Kids_1': 'Я не проверяю, дышит ли он. Я просто… стою у двери. Ладно, проверяю.$s',
    'HarveyMod_Spouse_Farm_Day_Kids_0': 'Малыш спит. Я принёс тебе воды.$h',
    'HarveyMod_Spouse_Farm_Day_Kids_1': 'Радионяня молчит. Значит, всё хорошо.$0',
    'HarveyMod_Spouse_Farm_Day_Kids_2': 'Шляпу! Не мне — тебе. Малышу я уже надел.$h',
    'HarveyMod_Spouse_Farm_Morning_Kids_0': 'Мы с малышом смотрим, как ты работаешь. Он одобряет.$h',
    'HarveyMod_Spouse_Farm_Evening_Kids_0': 'Пора домой. Нас там ждут.$l',
}
for k, v in DOMESTIC.items():
    assert '"' not in v and 'родил' not in v, k

data = {'Changes': [
    {**patch('Fatherhood — P1 «Первая ночь» (FarmHouse)', 'Data/Events/FarmHouse', {p1_key: p1}), 'When': WHEN},
    {**patch('Fatherhood — P2 «Радионяня» (Hospital)', 'Data/Events/Hospital', {p2_key: p2}), 'When': WHEN},
    {**patch('Fatherhood — записка «Список у колыбели»', 'Data/Mail', MAIL), 'When': WHEN},
    {**patch('Fatherhood — записка и тема после появления ребёнка', 'Data/TriggerActions', TRIGGERS), 'When': WHEN},
    {**patch('Fatherhood — реплики Харви на темы и дома', 'Characters/Dialogue/Harvey', {**TOPICS, **DOMESTIC}),
     'Priority': 'Late', 'When': WHEN},
    *[{**patch(f'Fatherhood — поздравление ({npc})', f'Characters/Dialogue/{npc}', {'HarveyFather_NewBaby': text}),
       'Priority': 'Late', 'When': WHEN} for npc, text in NPC_CONGRATS.items()],
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT)
