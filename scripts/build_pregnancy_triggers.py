"""Генерирует assets/Code/triggersPregnancy.json — темы Харви во время беременности фермерши.

Файл подключается из content.json только при Married + Pregnant, поэтому условия брака здесь не повторяются.
Все триггеры — MarkActionApplied: false: без этого Data/TriggerActions срабатывает один раз за сохранение,
и «ежедневные» темы звучали бы только в первый день первой беременности.
Повтор реплик обеспечивает RepeatableTopicResetter (Core) — для topic*-ключей.

Группа = несколько вариантов одной темы с общим кулдауном: первый прошедший RANDOM ставит кулдаун,
остальные в этот же момент уже не проходят. ID с суффиксом _v2 — старые ID в сохранениях помечены
как применённые и не мешают.
Запуск:  python scripts/build_pregnancy_triggers.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'triggersPregnancy.json')
P = 'topicHarvey_Pregnancy'


def no_topic(t):
    return f'!PLAYER_HAS_CONVERSATION_TOPIC Current {t}'


def group(name, trigger, cond, variants, chance, cooldown_days, topic_days=2, log=''):
    """variants — суффиксы тем (Check_01 …). Каждый вариант пробует RANDOM chance, пока не стоит кулдаун."""
    cd = f'{P}{name}CD'
    out = {}
    for v in variants:
        tid = f'{{{{ModId}}}}_preg_{v}_v2'
        parts = [*cond, f'RANDOM {chance}', no_topic(cd), no_topic(P + v)]
        out[tid] = {
            'Id': tid,
            'Trigger': trigger,
            'Condition': ', '.join(parts),
            'Actions': [f'AddConversationTopic {cd} {cooldown_days}', f'AddConversationTopic {P}{v} {topic_days}'],
            'MarkActionApplied': False,
            'LogName': f'Pregnancy — {log} ({v})',
        }
    return out


entries = {}
# Начало беременности: одна тема на 30 дней (беременность в игре — 14 дней, следующая — не раньше).
entries['{{ModId}}_preg_Start_v2'] = {
    'Id': '{{ModId}}_preg_Start_v2',
    'Trigger': 'DayStarted',
    'Condition': no_topic('topicHarvey_PregnancyCareStarted'),
    'Actions': ['AddConversationTopic topicHarvey_PregnancyCareStarted 30',
                'AddConversationTopic topicHarveyGentleCare 7'],
    'MarkActionApplied': False,
    'LogName': 'Pregnancy — начало: мягкая забота',
}
entries.update(group('Check', 'DayStarted', [no_topic('topicHarveyGentleCare')],
                     ['Check_01', 'Check_02', 'Check_03', 'Check_04', 'Check_05'], 0.25, 2, log='утренняя проверка'))
entries.update(group('Tender', 'DayStarted', [], ['Tender_01', 'Tender_02', 'Tender_03'], 0.15, 3, 3, log='нежность'))
entries.update(group('Food', 'DayStarted', [], ['Food_01', 'Food_02', 'Food_03'], 0.15, 3, log='еда'))
entries.update(group('Exhausted', 'DayStarted', ['PLAYER_HAS_CONVERSATION_TOPIC Current timeReaction_VeryLate'],
                     ['Exhausted_01', 'Exhausted_02', 'Exhausted_03'], 0.5, 2, 3, log='после очень позднего отбоя'))
entries.update(group('Storm', 'DayStarted', ['WEATHER Here Storm'], ['Storm_01', 'Storm_02'], 0.5, 1, log='гроза'))
entries.update(group('Heat', 'DayStarted', ['SEASON Summer', 'WEATHER Here Sun Wind'], ['Heat_01', 'Heat_02'], 0.25, 3,
                     log='летняя жара'))
entries.update(group('NightOwl', 'DayStarted', [], ['Night_02'], 0.1, 4, log='беспокойная ночь'))
entries.update(group('Mine', 'LocationChanged', ['ANY "PLAYER_LOCATION_NAME Current Mine" "PLAYER_LOCATION_NAME Current SkullCave"'],
                     ['MineWarning_01', 'MineWarning_02', 'MineWarning_03'], 0.5, 2, 3, log='шахта'))
entries.update(group('Rain', 'LocationChanged', ['WEATHER Here Rain Storm', 'LOCATION_IS_OUTDOORS Here'],
                     ['RainWarning_01', 'RainWarning_02'], 0.4, 2, log='дождь на улице'))
entries.update(group('Night', 'LocationChanged', ['TIME 2200 2600'], ['Night_01'], 0.4, 2, log='поздно на ногах'))
entries.update(group('FarmHeavy', 'LocationChanged', ['PLAYER_LOCATION_NAME Current Farm', 'TIME 0900 1800'],
                     ['FarmHeavy_01', 'FarmHeavy_02'], 0.15, 3, log='тяжёлая работа на ферме'))

data = {'Changes': [{
    'LogName': 'Pregnancy — темы Харви (повторяемые)',
    'Action': 'EditData',
    'Target': 'Data/TriggerActions',
    'Entries': entries,
}]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, len(entries), 'triggers')
