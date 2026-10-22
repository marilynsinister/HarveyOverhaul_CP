"""Генерирует assets/Code/triggersRepeatScenes.json — возвращает «повторяемые» сцены заботы в игру.

Игра не запускает событие, которое уже есть в просмотренных. Утешение в грозу, осмотр наверху, медосмотр
по письму, ночь на площади, «слишком поздно», завтрак в постель и утро после шахты задуманы повторяемыми
(у них свои условия и кулдауны), но без этого файла игрались один раз за сохранение.

Сами сцены не меняются. Два триггера DayStarted на сцену:
  1. сцена просмотрена и метки ещё нет → метка-письмо HarveyRepeat_<id> и тема-кулдаун HarveyRepeatCD_<id> на N дней;
  2. сцена просмотрена, метка есть, кулдауна уже нет → снять из просмотренных и убрать метку.
Так кулдаун отсчитывается от следующего утра после сцены, а сцену не нужно переписывать.

Запуск:  python scripts/build_repeat_scenes.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'triggersRepeatScenes.json')

# id сцены → дней до возвращения. Сцены, которые запускаются по теме от C# (обморок, проверка здоровья),
# сами по себе редкие; кулдаун только не даёт им идти два дня подряд.
SCENES = {
    # Утешение в грозу: у каждого места своя сцена, общий кулдаун HarveyMod_CD_StormComfort уже есть.
    'eventHarveyStormComfortFarm': 10,
    'eventHarveyStormComfortTown': 10,
    'eventHarveyStormComfortForest': 10,
    'eventHarveyStormComfortMountain': 10,
    'eventHarveyStormComfortDesert': 10,
    'eventHarveyStormComfortMine': 10,
    # Осмотр наверху — раз в сезон, медосмотр по письму — раз в два сезона.
    'eventHarveyRoomCheckup': 28,
    'eventHarveyRoomCheckup2': 28,
    'eventHarveyMedicalCheck': 56,
    'eventHarveyMedicalCheck_Dating': 56,
    # Ответ на её состояние: обморок, переутомление, ночь вне дома.
    'eventHarveyLateNightCollapse': 14,
    'eventHarveyCheckFarmerOutsideAfter22': 7,
    'eventHarveyMorningCheckup': 7,
    'eventHarveyCheckHealthFarmer': 7,
}


def mark(eid):
    return f'HarveyRepeat_{eid}'


def cooldown(eid):
    return f'HarveyRepeatCD_{eid}'


triggers = {}
for eid, days in SCENES.items():
    arm = f'{{{{ModId}}}}_Repeat_{eid}_Arm'
    rearm = f'{{{{ModId}}}}_Repeat_{eid}_Return'
    triggers[arm] = {
        'Id': arm,
        'Trigger': 'DayStarted',
        'Condition': f'PLAYER_HAS_SEEN_EVENT Current {eid}, !PLAYER_HAS_MAIL Current {mark(eid)} Received',
        'Actions': [f'AddMail Current {mark(eid)} Received', f'AddConversationTopic {cooldown(eid)} {days}'],
        'MarkActionApplied': False,
    }
    triggers[rearm] = {
        'Id': rearm,
        'Trigger': 'DayStarted',
        'Condition': (f'PLAYER_HAS_SEEN_EVENT Current {eid}, PLAYER_HAS_MAIL Current {mark(eid)} Received, '
                      f'!PLAYER_HAS_CONVERSATION_TOPIC Current {cooldown(eid)}'),
        'Actions': [f'MarkEventSeen Current {eid} false', f'RemoveMail Current {mark(eid)} Received'],
        'MarkActionApplied': False,
    }

data = {'Changes': [{
    'LogName': 'Повторяемые сцены заботы — вернуть после кулдауна',
    'Action': 'EditData',
    'Target': 'Data/TriggerActions',
    'Entries': triggers,
}]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, len(SCENES), 'scenes')
