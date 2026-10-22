"""Первый осмотр: повторная запись и сохранение согласия без срока давности.

Старые сохранения без активного topicAgreedCheckup получают короткое предложение
в клинике. Отказ или пропуск откладывает предложение на неделю; согласие
сохраняется отдельным флагом, не затрагивая уже просмотренные сюжетные сцены.
"""
import json
from pathlib import Path

from event_builder import patch, qq, sp

ROOT = Path(__file__).resolve().parents[1]
AGREED = 'HarveyIntro_CheckupAgreed'
INVITE = 'eventHarveyCheckupInvitation'
CHECKUP = 'eventHarveyCheckup'
TOPIC = 'topicAgreedCheckup'
DEFER = 'topicRefusedCheckup'


def build():
    key = '/'.join([
        INVITE, 'Time 1400 1600',
        'GameStateQuery DAYS_PLAYED 2',
        'GameStateQuery PLAYER_HAS_SEEN_EVENT Current eventHarveyFirstMeeting',
        f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {CHECKUP}',
        f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {TOPIC}',
        f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {DEFER}',
        f'GameStateQuery !PLAYER_HAS_MAIL Current {AGREED} Received',
    ])
    body = '/'.join([
        'none', '4 6', 'farmer 4 6 1 Harvey 4 5 3', 'skippable',
        f'setSkipActions AddConversationTopic {DEFER} 7',
        sp('Harvey', 'Здравствуйте. Если захотите, можно записаться на обычный осмотр: давление, пульс, несколько вопросов.$0#$b#Я принимаю после обеда, с двух до четырёх. Записать вас?$h'),
        qq(['Записаться на осмотр', 'Пока не хочу'], [
            [f'action AddMail Current {AGREED} Received', f'addConversationTopic {TOPIC} 5',
             sp('Harvey', 'Хорошо, я подготовлю кабинет.$h#$b#Приходите с двух до четырёх, когда будет удобно. Запись не пропадёт, даже если не получится прийти сразу.$0')],
            [f'addConversationTopic {DEFER} 7',
             sp('Harvey', 'Конечно. Решение за вами.$0#$b#Если передумаете, можно будет записаться позже.$h')],
        ]),
        'globalFade', 'viewport -1000 -1000', 'end position 10 17',
    ])
    triggers = {}
    for suffix, condition, actions in [
        ('KeepCheckupConsent',
         f'PLAYER_HAS_CONVERSATION_TOPIC Current {TOPIC}, !PLAYER_HAS_SEEN_EVENT Current {CHECKUP}, !PLAYER_HAS_MAIL Current {AGREED} Received',
         [f'AddMail Current {AGREED} Received']),
        ('OfferCheckupAgain',
         f'PLAYER_HAS_SEEN_EVENT Current {INVITE}, !PLAYER_HAS_SEEN_EVENT Current {CHECKUP}, !PLAYER_HAS_MAIL Current {AGREED} Received, !PLAYER_HAS_CONVERSATION_TOPIC Current {TOPIC}, !PLAYER_HAS_CONVERSATION_TOPIC Current {DEFER}',
         [f'MarkEventSeen Current {INVITE} false']),
    ]:
        tid = '{{ModId}}_' + suffix
        triggers[tid] = {'Id': tid, 'Trigger': 'DayStarted', 'Condition': condition,
                         'Actions': actions, 'MarkActionApplied': False}
    return {'Changes': [
        patch('Первый осмотр — повторная запись в клинике', 'Data/Events/Hospital', {key: body}),
        patch('Первый осмотр — сохранить согласие и вернуть предложение после отказа', 'Data/TriggerActions', triggers),
    ]}


if __name__ == '__main__':
    out = ROOT / 'assets/Code/introRecovery.json'
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Written {out}')
