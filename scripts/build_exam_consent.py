"""Согласие в осмотрах: «стоп» → Харви останавливается → немного доверия (StressMeter).

1. Генерирует assets/Code/eventsExamConsent.json — ветки-форки, куда уходят осмотры, если фермерша сказала «стоп».
2. Один раз вставляет вопрос о согласии в рукописные осмотры (events.json, eventsCare.json) и действие
   ExamStopRespected в уже существующие ветки отказа (E2, E9). Повторный запуск ничего не дублирует.

Осмотры:
  eventHarveyCheckup              (eventsCare.json, Hospital, стадия 0 — «вы»)  → fork HarveyExam_CheckupStopped
  eventHarveyMedicalCheck         (events.json, Hospital, до отношений)          → fork HarveyExam_MedCheckStopped
  eventHarveyMedicalCheck_Dating  (events.json, Hospital, Dating)                → fork HarveyExam_MedCheckStoppedDating
  E2_InsistentExam «Покачать головой», E9_CameByHerself «Просто посидеть» / «Передумать» — только действие.

`question forkN` ставит флаг, если выбран ответ с индексом N (с нуля); `fork <ключ>` уходит в ветку по флагу.
Запуск:  python scripts/build_exam_consent.py
"""
import json
import os

from event_builder import H, msg, patch, sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, 'assets', 'Code')
OUT = os.path.join(CODE, 'eventsExamConsent.json')

STOP = 'action marilynsinister.HarveyStressMeter_ExamStopRespected'
# Forks inherit the seated/lying player pose from the examination.
# Release it under the fade, before control is returned to the player.
END_FADE = ['globalFade', 'viewport -1000 -1000', 'stopAnimation farmer']


def fork(cmds):
    for c in cmds:
        assert '/' not in c, c
    return '/'.join(cmds)


checkup_stopped = fork([
    sp(H, '*сразу опускает стетоскоп и кладёт его на стол* Хорошо. Остановился.$0#$b#Стетоскоп там, я здесь. Продолжим, только если вы сами захотите.$s'),
    STOP,
    'pause 600',
    sp(H, 'Тогда без приборов — просто пара вопросов. Вы регулярно едите? Спите хотя бы семь часов?$0'),
    msg('Стараюсь...'),
    sp(H, '*кивает* «Стараюсь» — уже хорошо. Пейте больше воды и не работайте до изнеможения.$l'),
    sp(H, 'И спасибо, что сказали «стоп». Мне проще помогать, когда я знаю, где ваша граница.$h#$b#Приходите через месяц. Или раньше — не обязательно на осмотр.$l'),
    'addConversationTopic topicAfterCheckup 5',
    'action RemoveConversationTopic topicAgreedCheckup',
    *END_FADE, 'pause 500', 'end position 10 17',
])


def med_check_stopped(dating):
    closing = ('Ты становишься сильнее с каждым днём. Я рядом, если понадоблюсь.$l' if dating
               else 'Ты становишься сильнее с каждым днём. Если что-то беспокоит — приходи сразу. Я помогу.$0')
    return fork([
        'stopAnimation Harvey',
        sp(H, 'Стоп — значит стоп.$0#$b#*откладывает манжету* Видишь? Руки на виду.$s'),
        STOP,
        'pause 600',
        sp(H, 'Тогда без осмотра. Просто скажи: когда ты последний раз ела?$a'),
        msg('Ты пожимаешь плечами.'),
        sp(H, 'Так я и думал.$s#$b#Вот кофе — и обещание поесть до вечера. Обещание — тоже лечение, если его выполнять.$a'),
        'addItem 395 1',
        sp(H, ('Солнышко, ' if dating else '') + 'спасибо, что сказала прямо. Мне так спокойнее, чем гадать по лицу.$l'),
        'pause 600', *END_FADE,
        f'end dialogue Harvey "{closing}"',
    ])


data = {'Changes': [
    patch('Осмотры — ветки «стоп» (согласие в осмотрах, build_exam_consent.py)', 'Data/Events/Hospital', {
        'HarveyExam_CheckupStopped': checkup_stopped,
        'HarveyExam_MedCheckStopped': med_check_stopped(False),
        'HarveyExam_MedCheckStoppedDating': med_check_stopped(True),
    }),
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT)


# ---------------------------------------------------------------- вставки в рукописные события
# В файлах события — многострочные JSON-строки: кавычки внутри экранированы \", ветки quickQuestion разделены \\.
Q = '\\"'
BS2 = '\\\\'


def inject(fname, marker, anchor, insert, count=1):
    path = os.path.join(CODE, fname)
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if marker in text:
        print(f'{fname}: уже есть ({marker[:40]}…)')
        return
    n = text.count(anchor)
    assert n == count, (fname, anchor[:60], n)
    text = text.replace(anchor, insert(anchor))
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print(f'{fname}: вставлено {n}x')


# eventHarveyCheckup: вместо «Конечно...» — вопрос с вариантом «стоп».
checkup_anchor = (
    f'speak Harvey {Q}*кивает* Хорошо. Тем не менее, давайте проверим основные показатели.$h#$b#*достает стетоскоп* Можно послушать сердце?$s{Q}/\n'
    f'                    emote farmer 32/\n'
    f'                    message {Q}Конечно...{Q}/\n')
inject('eventsCare.json', 'HarveyExam_CheckupStopped', checkup_anchor, lambda a: (
    f'speak Harvey {Q}*кивает* Хорошо. Тем не менее, давайте проверим основные показатели.$h#$b#*достает стетоскоп* Можно послушать сердце? Скажите «стоп» — и я остановлюсь.$s{Q}/\n'
    f'                    emote farmer 32/\n'
    f'                    question fork2 {Q}#Конечно...#Только побыстрее, пожалуйста#Стоп. Не сейчас{Q}/\n'
    f'                    fork HarveyExam_CheckupStopped/\n'))

# Медосмотр по письму: перед тем как Харви начинает слушать — вопрос (оба варианта события).
medcheck_anchor = (
    '        animate Harvey false true 1000 22 20 21 20/\n'
    '        pause 500/\n'
    f'        speak Harvey {Q}Сначала просто подыши... вот так.$u{Q}/\n')


def medcheck_insert(dating):
    key = 'HarveyExam_MedCheckStoppedDating' if dating else 'HarveyExam_MedCheckStopped'
    return (
        f'        speak Harvey {Q}Послушаю дыхание и проверю давление. Можно? Скажешь «стоп» — остановлюсь.$0{Q}/\n'
        f'        question fork2 {Q}#Кивнуть#Сначала скажи, что будешь делать#Стоп. Не сегодня{Q}/\n'
        f'        fork {key}/\n'
        + medcheck_anchor)


def inject_medcheck():
    path = os.path.join(CODE, 'events.json')
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if 'HarveyExam_MedCheckStopped' in text:
        print('events.json: медосмотр уже с вопросом')
        return
    for event, dating in (('"eventHarveyMedicalCheck/', False), ('"eventHarveyMedicalCheck_Dating/', True)):
        start = text.index(event)
        end = text.index('",\n', start)
        body = text[start:end]
        assert body.count(medcheck_anchor) == 1, event
        text = text[:start] + body.replace(medcheck_anchor, medcheck_insert(dating)) + text[end:]
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print('events.json: медосмотр — вопрос вставлен в 2 события')


inject_medcheck()

# E2: «Покачать головой» — Харви сокращает осмотр. E9: «Просто посидеть» / «Передумать».
inject('events.json', 'ExamStopRespected\\\\speak Harvey \\"Понял. Не удерживаю.',
       f'emote farmer 40{BS2}speak Harvey {Q}Понял. Не удерживаю.$0{Q}',
       lambda a: f'emote farmer 40{BS2}{STOP}{BS2}speak Harvey {Q}Понял. Не удерживаю.$0{Q}')

# E9 «Просто посидеть»: он сел без стетоскопа — это тоже уважение к «стоп».
inject('events.json', 'ExamStopRespected' + BS2 + f'speak Harvey {Q}Хорошо. Я посижу здесь.',
       f'(break)speak Harvey {Q}Хорошо. Я посижу здесь. Без стетоскопа.$0{Q}',
       lambda a: f'(break){STOP}{BS2}speak Harvey {Q}Хорошо. Я посижу здесь. Без стетоскопа.$0{Q}')

# E9 «Передумать»: раньше AddMail стоял без action — это не команда события, письмо не ставилось.
inject('events.json', 'action AddMail Current HarveyOverhaul_E9_ClinicOpen',
       f'{BS2}AddMail Current HarveyOverhaul_E9_ClinicOpen tomorrow{BS2}',
       lambda a: f'{BS2}action AddMail Current HarveyOverhaul_E9_ClinicOpen tomorrow{BS2}{STOP}{BS2}')
