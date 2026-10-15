"""Генерирует assets/Code/clinicSeasonal.json — сезонные мелочи клиники (дополняют clinicErrands.json).

  V1 «День прививок»      весна: письмо (6–12 весны, 3♥+) → сцена в клинике с Джоди и Винсентом.
                          Можно подставить плечо, держать Винсента за руку или отказаться — Харви не заставляет.
                          Прививка — бафф «Прививка» (+1 защита до конца дня).
  Луау: тент первой помощи лето: письмо (5–9 лета) с поручением принести виноград для холодного морса.
  HS1 «Тепловой удар»     12–14 лета, клиника: Пэм упала на луау от жары, фермерша помогает охладить её,
                          потом Харви проверяет саму фермершу.
Сцены возвращаются каждый год: 1-го числа сезона триггер снимает их из просмотренных (как в ротации брака).
Реплики Харви — для 3♥+ (на «ты», без ласковых имён), поэтому подходят для любой стадии отношений.
Запуск:  python scripts/build_clinic_seasonal.py
"""
import json
import os

from event_builder import H, key, msg, patch, qq, script, skip_cd, sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'clinicSeasonal.json')

NS = 'HarveyOverhaulClinic'
M = '{{ModId}}'
VACCINE = f'{M}_Vaccinated'


def mail_got(mail_id):
    return f'GameStateQuery PLAYER_HAS_MAIL Current {mail_id} Received'


# ---------------------------------------------------------------- V1
V1_MAIL = f'{M}_mailVaccineDay{{{{Year}}}}'
v1_key = key(NS, 'V1_VaccineDay', 'Season Spring', 'Time 0900 1500', 'Friendship Harvey 750', mail_got(V1_MAIL))
SHOT = 'playSound shwip'
v1 = script(
    'Hospital_Ambient', '10 16', 'Harvey 9 16 1 Jodi 13 16 3 Vincent 14 16 3 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyClinic_VaccineDay 5'),
    [
        'viewport 10 16 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -2 0', 'pause 300',
        msg('В клинике непривычно шумно. На стойке — коробка с наклейками-звёздочками. У кушетки Джоди и Винсент: он держится за мамину юбку обеими руками.'),
        sp('Jodi', 'О, @! Ты тоже на прививку? Скажи ему, что это не больно. Мне он не верит.$h'),
        sp('Vincent', 'Это больно! Сэм сказал — как пчела!$s'),
        sp(H, 'Сэм сказал неправду. Пчела жалит дольше.$h'),
        'emote Vincent 28', 'faceDirection Harvey 2',
        sp(H, 'А, @. Ты вовремя. Весенняя прививка от гриппа — я записал тебя ещё в понедельник.$h'),
        sp(H, 'Займёт минуту. Если сегодня не хочешь — скажи. Уговаривать буду, заставлять — нет.$0'),
        qq(['Подставить плечо первой', 'Взять Винсента за руку', '«Не сегодня»'], [
            [msg('Ты садишься на кушетку и закатываешь рукав.'),
             sp(H, 'Смотри, Винсент. Взрослый пример. Раз…$0'), SHOT,
             sp(H, '…и всё. Ватку прижми. Вот так.$h'),
             sp('Vincent', 'И всё?! Она даже не заплакала!$h'),
             sp(H, 'Говорил же. Твоя очередь, герой.$h'), SHOT,
             f'action AddBuff {VACCINE}', 'friendship Harvey 30', 'friendship Vincent 30', 'friendship Jodi 20'],
            [msg('Ты садишься рядом с Винсентом и протягиваешь ему ладонь. Он вцепляется в неё изо всех сил.'),
             sp(H, 'Отлично. Сожми крепко-крепко — @ выдержит, она фермер.$h'), SHOT,
             sp('Vincent', '…Ой. И всё?$s'),
             sp(H, 'И всё. Наклейку выбирай сам.$h#$b#А теперь ты, @. Без руки Винсента — но я в тебя верю.$h'), SHOT,
             f'action AddBuff {VACCINE}', 'friendship Harvey 25', 'friendship Vincent 40', 'friendship Jodi 30'],
            [sp(H, 'Хорошо. Не сегодня.$0'),
             sp(H, 'Поставлю тебя на четверг — и в четверг спрошу ещё раз. Это не давление, это расписание.$h'),
             sp('Jodi', 'Видишь, Винсент? Доктор никого не заставляет.$0'),
             sp('Vincent', '…Тогда я первый! Чтобы @ видела, как надо!$h'), SHOT,
             'friendship Harvey 20', 'friendship Vincent 30', 'friendship Jodi 20'],
        ]),
        msg('Винсент гордо клеит звёздочку на лоб. Джоди уводит его, и в клинике становится тихо.'),
        'warp Jodi -1000 -1000', 'warp Vincent -1000 -1000', 'pause 400',
        sp(H, 'Каждую весну одно и то же. Половина долины прячется от меня за деревьями.$h#$b#Спасибо, что пришла. С тобой сегодня было проще.$0'),
        'addConversationTopic HarveyClinic_VaccineDay 5',
    ])

# ---------------------------------------------------------------- HS1
hs1_key = key(NS, 'HS1_Heatstroke', 'Season Summer', 'Time 0900 1400', 'Friendship Harvey 750',
              'GameStateQuery DAY_OF_MONTH 12 13 14')
hs1 = script(
    'Hospital_Ambient', '11 16', 'Harvey 13 16 1 Pam 14 16 3 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic HarveyClinic_Heatstroke 5'),
    [
        'viewport 11 16 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -2 1', 'pause 300',
        msg('Утро после луау. На кушетке — Пэм с мокрым полотенцем на шее. Харви держит её запястье и смотрит на часы.'),
        sp('Pam', 'Док, хватит щупать. Я в порядке. Просто солнце в макушку било.$s'),
        sp(H, 'Ты упала у котла с супом, Пэм. Пульс сто двадцать, кожа горячая и сухая. Это тепловой удар.$a'),
        'faceDirection Harvey 3',
        sp(H, '@, хорошо, что зашла. Нужны руки. Возьми что-нибудь одно — остальное сделаю я.$u'),
        qq(['Сменить полотенце на холодное', 'Принести воды', 'Распахнуть окна'], [
            [msg('Ты отжимаешь полотенце в холодной воде и кладёшь его Пэм на шею.'),
             sp('Pam', 'Ох… вот это хорошо. Спасибо, детка.$h'),
             sp(H, 'Шея, подмышки, запястья — там сосуды близко к коже. Ты всё делаешь правильно.$0'),
             'friendship Pam 30', 'friendship Harvey 25'],
            [msg('Ты приносишь кувшин и наливаешь Пэм стакан.'),
             sp(H, 'Маленькими глотками. Пэм, это вода. Не пиво. Знаю, непривычно.$h'),
             sp('Pam', 'Очень смешно, док.$s#$b#…Спасибо, детка.$h'),
             'friendship Pam 30', 'friendship Harvey 25'],
            [msg('Ты распахиваешь окна. По клинике проходит прохладный ветер с реки.'),
             sp(H, 'Отлично. Прохладная комната — тоже лечение.$0'),
             sp('Pam', 'Хоть кто-то тут думает о моём комфорте.$h'),
             'friendship Pam 25', 'friendship Harvey 25'],
        ]),
        'faceDirection Harvey 1', 'pause 600',
        sp(H, 'Пульс сто. Уже лучше. Лежишь до обеда, Пэм, потом Пенни заберёт тебя домой — я ей позвоню.$0'),
        sp('Pam', 'До обеда?! Док…$a'),
        sp(H, 'До обеда. Ворчать можно, вставать — нет.$h'),
        'faceDirection Harvey 3', 'pause 400',
        sp(H, 'А теперь ты. Вчера ты была на солнце дольше, чем я бы одобрил. Голова не болит? Воду пила?$u'),
        qq(['«Пила, честно»', '«…Кажется, немного болит»'], [
            [sp(H, 'Верю. Но язык всё равно покажи.$h'),
             msg('Ты показываешь язык. Харви серьёзно кивает.'),
             sp(H, 'Влажный. Принято. Сегодня — шляпа и вода каждый час. Иначе начну приходить на ферму с термометром.$h'),
             'friendship Harvey 15'],
            [sp(H, 'Спасибо, что сказала сразу. Это очень важно.$s'),
             'addItem 254 1',
             sp(H, 'Садись вот сюда, в тень от окна. Дыня — наполовину вода, съешь при мне.$u#$b#И до вечера никакой работы на солнце. Я загляну проверить — не обижайся, это не недоверие.$a'),
             'friendship Harvey 25'],
        ]),
        'addConversationTopic HarveyClinic_Heatstroke 5',
    ])

# ---------------------------------------------------------------- данные
QUESTS = {
    f'{M}_ErrandLuauTent': ('ItemDelivery/Тент первой помощи/На луау Харви ставит тент с водой и холодным морсом — '
                           'каждый год кому-нибудь становится плохо от жары./Принеси Харви 3 винограда./'
                           'Harvey (O)398 3/-1/400/-1/true/Отлично — на морс хватит. Холодный, кислый, без сахара: '
                           'от жары лучше не придумаешь.$h#$b#Если на луау увидишь, что кто-то краснеет и перестаёт '
                           'потеть, — тащи ко мне в тент. Даже если это будет Пьер в костюме.$0'),
}
MAIL = {
    V1_MAIL: ('@,^^Всю эту весну в клинике — прививки от гриппа. Заходи в часы приёма, в любой день.^'
              'Ничего страшного: одно плечо, одна минута, одна наклейка-звёздочка (да, взрослым тоже).^^'
              'Я записал тебя. Если не хочешь — просто скажи при встрече. Но я очень надеюсь, что придёшь.^^'
              '— Харви[#]День прививок'),
    f'{M}_mailLuauTent{{{{Year}}}}': ('@,^^На луау обещают жару. Каждый год кто-нибудь падает у котла с супом — '
                                      'в прошлый раз это был мэр.^^Я поставлю тент первой помощи с водой и холодным морсом. '
                                      'Не хватает винограда — если попадётся в горах, принеси, пожалуйста.^^'
                                      'И сама приходи в шляпе. Я проверю.^^— Харви%item quest '
                                      f'{M}_ErrandLuauTent true %%[#]Тент первой помощи'),
}


def yearly_mail(tid, season, days, mail_id, chance):
    return {'Id': tid, 'Trigger': 'DayStarted',
            'Condition': f'SEASON {season}, DAY_OF_MONTH {days}, PLAYER_HEARTS Current Harvey 3, RANDOM {chance}, '
                         f'!PLAYER_HAS_MAIL Current {mail_id} Any',
            'Actions': [f'AddMail Current {mail_id} now'], 'MarkActionApplied': False}


def yearly_reset(tid, season, eid):
    return {'Id': tid, 'Trigger': 'DayStarted',
            'Condition': f'SEASON {season}, DAY_OF_MONTH 1, PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}',
            'Actions': [f'MarkEventSeen Current {NS}.{eid} false'], 'MarkActionApplied': False}


TRIGGERS = {
    f'{M}_triggerVaccineMail': yearly_mail(f'{M}_triggerVaccineMail', 'spring', '6 7 8 9 10 11 12', V1_MAIL, 0.35),
    f'{M}_triggerLuauTentMail': yearly_mail(f'{M}_triggerLuauTentMail', 'summer', '5 6 7 8 9', f'{M}_mailLuauTent{{{{Year}}}}', 0.4),
    f'{M}_resetVaccineDay': yearly_reset(f'{M}_resetVaccineDay', 'spring', 'V1_VaccineDay'),
    f'{M}_resetHeatstroke': yearly_reset(f'{M}_resetHeatstroke', 'summer', 'HS1_Heatstroke'),
}

BUFFS = {
    VACCINE: {
        'Id': VACCINE,
        'DisplayName': 'Прививка',
        'Description': 'Плечо немного ноет, зато простуда\nобойдёт стороной. +1 к защите.',
        'IsDebuff': False,
        'Duration': -2,
        'IconTexture': 'TileSheets\\BuffsIcons',
        'IconSpriteIndex': 10,
        'Effects': {'Defense': 1},
    },
}

TOPICS = {
    'HarveyClinic_VaccineDay': 'Винсент пришёл вчера показать звёздочку. Она до сих пор у него на лбу.$h#$b#Плечо не болит? Если немного ноет — это нормально. Если сильно — сразу ко мне.$u',
    'HarveyClinic_Heatstroke': 'Пэм уже ругается, что Пенни не пускает её на солнце. Значит, выздоравливает.$h#$b#А ты сегодня в шляпе? Хорошо. Я заметил.$h',
}

data = {'Changes': [
    patch('Clinic seasonal — V1 «День прививок», HS1 «Тепловой удар» (Hospital)', 'Data/Events/Hospital',
          {v1_key: v1, hs1_key: hs1}),
    patch('Clinic seasonal — квест «Тент первой помощи»', 'Data/Quests', QUESTS),
    patch('Clinic seasonal — письма', 'Data/Mail', MAIL),
    patch('Clinic seasonal — письма раз в год и возврат сцен', 'Data/TriggerActions', TRIGGERS),
    patch('Clinic seasonal — бафф «Прививка»', 'Data/Buffs', BUFFS),
    {**patch('Clinic seasonal — реплики Харви на темы', 'Characters/Dialogue/Harvey', TOPICS), 'Priority': 'Late'},
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT)
