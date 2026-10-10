"""Генерирует assets/Code/triggersArc3Aftermath.json — темы «люблю» / «жду» после N4–N5.

Вариант реплики выбирается по дню месяца (6 вариантов «люблю», 2 — «жду»), шанс — RANDOM.
Игра показывает реплику темы один раз и запоминает это флагом «Harvey_<тема>» в mailReceived,
поэтому триггер сначала снимает этот флаг — иначе вариант больше не прозвучит.
MarkActionApplied=false — триггер срабатывает каждый подходящий день, а не один раз за игру.
Тексты — assets/Code/dialogues/harvey_arc3_aftermath.json.
Запуск:  python scripts/build_arc3_aftermath_triggers.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'triggersArc3Aftermath.json')

LOVE_VARIANTS = 6
LOVE_CHANCE = 0.35
WAIT_CHANCE = 0.3


def days_for(i, n):
    return ' '.join(str(d) for d in range(1, 29) if (d - 1) % n == i)


def trigger(tid, condition, topic):
    return {
        'Id': '{{ModId}}_' + tid,
        'Trigger': 'DayStarted',
        'Condition': condition,
        'Actions': [
            f'RemoveMail Current Harvey_{topic} Received',
            f'AddConversationTopic {topic} 1',
        ],
        'MarkActionApplied': False,
    }


entries = {}
for i in range(LOVE_VARIANTS):
    tid = f'Arc3Love_{i}'
    entries['{{ModId}}_' + tid] = trigger(
        tid,
        'PLAYER_HAS_MAIL Current HarveyArc3_Confessed Received, '
        'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Married, '
        f'DAY_OF_MONTH {days_for(i, LOVE_VARIANTS)}, RANDOM {LOVE_CHANCE}',
        f'HarveyArc3_Love_{i}')

for i in range(2):
    tid = f'Arc3Waiting_{i}'
    entries['{{ModId}}_' + tid] = trigger(
        tid,
        'PLAYER_HAS_MAIL Current HarveyArc3_ConfessionPending Received, '
        '!PLAYER_HAS_MAIL Current HarveyArc3_Confessed Received, '
        'PLAYER_NPC_RELATIONSHIP Current Harvey Dating, '
        f'DAY_OF_MONTH {days_for(i, 2)}, RANDOM {WAIT_CHANCE}',
        f'HarveyArc3_Waiting_{i}')

data = {'Changes': [{
    'LogName': 'Arc3 aftermath — темы «люблю» / «жду» (DayStarted)',
    'Action': 'EditData',
    'Target': 'Data/TriggerActions',
    'Entries': entries,
}]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, len(entries), 'triggers')
