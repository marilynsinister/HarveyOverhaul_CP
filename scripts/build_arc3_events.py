"""Генерирует assets/Code/eventsArc3.json — арка 3 «Право на заботу» (N1–N7).

Сцены пишутся списками команд, чтобы JSON-экранирование кавычек и обратных слэшей
делал json.dump, а не руками. Запуск:  python scripts/build_arc3_events.py
Проверенные тайлы (SVE / Alchemistry / Aimon) — docs/story-arc3-proposal.md.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'eventsArc3.json')

NS = 'HarveyOverhaulArc3'
CD = 'HarveyMod_CD_Global'


def sp(who, text):
    return f'speak {who} "{text}"'


def msg(text):
    return f'message "{text}"'


def qq(answers, branches, question=''):
    """quickQuestion: answers — список, branches — список списков команд."""
    assert len(answers) == len(branches)
    for t in answers:
        assert '#' not in t and '/' not in t
    head = f'quickQuestion {question}#' + '#'.join(answers)
    return head + ''.join('(break)' + '\\'.join(b) for b in branches)


def key(eid, *conds):
    parts = [f'{NS}.{eid}', *conds, '!FestivalDay',
             f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {NS}.{eid}',
             f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {CD}']
    return '/'.join(parts)


def script(music, view, actors, skip, body, ending='end'):
    cmds = [music, view, actors, 'skippable', 'setSkipActions ' + '#'.join(skip), *body,
            f'addConversationTopic {CD} 3', 'globalFade', 'viewport -1000 -1000', ending]
    for c in cmds:
        assert '/' not in c, c
    return '/'.join(cmds)


def skip_cd(*extra):
    return [f'AddConversationTopic Current {CD} 3', *extra]


H = 'Harvey'

# ---------------------------------------------------------------- N1
n1_key = key('N1_NightShift', 'Time 2000 2400', 'Friendship Harvey 2000',
             'GameStateQuery PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulStory.E6_SayItOutLoud',
             'GameStateQuery !PLAYER_NPC_RELATIONSHIP Current Harvey Dating Married')
n1 = script(
    'none', '36 57', 'farmer 36 58 0 Harvey -1000 -1000 2',
    skip_cd('AddConversationTopic Current HarveyArc3_KnowsWhy 7',
            'AddMail Current HarveyArc3_N1_Bandage tomorrow'),
    [
        'viewport 36 57 true', 'pause 600',
        msg('Поздно. В окне клиники ещё горит свет. Левая рука спрятана в рукав — порез от серпа ноет сильнее, чем хотелось бы.'),
        'move farmer 0 -1 0', 'pause 400', 'playSound doorOpen',
        'warp Harvey 36 56', 'faceDirection Harvey 2', 'pause 300', 'emote Harvey 16',
        sp(H, '@? Так поздно…$u#$b#Что-то случилось? Нет, не говори «ничего». Покажи руки.$a'),
        'emote farmer 28',
        sp(H, 'Левую. Ту, которую ты прячешь.$a'),
        qq(['Показать руку', 'Сказать, что всё нормально', 'Покачать головой: не сейчас'], [
            [msg('Ты медленно вытаскиваешь руку из рукава. Носовой платок вместо повязки уже промок.'),
             sp(H, 'Спасибо, что показала. Это самое важное, что ты сегодня сделала.$s'),
             'friendship Harvey 40'],
            [sp(H, '«Нормально» не пахнет кровью, @.$a'),
             sp(H, 'Внутрь. Сначала рука — разговоры потом.$a'),
             'friendship Harvey 25'],
            [sp(H, 'Хорошо. Тогда я ни о чём не спрашиваю.$0'),
             sp(H, 'Но перевяжу. Молча. Это уступка — большая, поверь.$a'),
             'friendship Harvey 30'],
        ]),
        'globalFade', 'changeLocation Hospital',
        'warp farmer 14 6', 'faceDirection farmer 1', 'warp Harvey 15 6', 'faceDirection Harvey 3',
        'ambientLight 75 70 60', 'viewport 14 6 true', 'pause 600',
        msg('Йод щиплет. Харви работает быстро и аккуратно — и ни разу не отводит взгляд от пореза.'),
        sp(H, 'Неглубоко. Но ещё день под платком — и разговор был бы совсем другим.$a'),
        'pause 400',
        sp(H, 'Знаешь, почему я так реагирую на «всё нормально»?$0'),
        'emote farmer 8',
        sp(H, 'Ординатура в Зузу. Ночная смена — как сейчас. Пришёл мужчина, порезался на стройке.$s#$b#Сказал: «Я в порядке, доктор, не тратьте время». Я поверил. Обработал и отпустил.$s'),
        'pause 600',
        sp(H, 'Через три дня его привезли обратно. Заражение. Я успел — еле-еле.$s#$b#А мог не успеть.$s'),
        'pause 500',
        sp(H, 'С тех пор я не верю этим словам. Ни от кого.$a#$b#А от тебя — особенно.$u'),
        qq(['Кивнуть', 'Коснуться его рукава', 'Спросить взглядом: он выжил?'], [
            ['emote farmer 40', sp(H, 'Вот. Теперь ты знаешь, почему я невыносим.$h')],
            [msg('Ты на секунду касаешься его рукава.'),
             sp(H, '…Спасибо. Обычно утешаю я.$s'), 'friendship Harvey 20'],
            [sp(H, 'Выжил. Прислал потом открытку — с ошибками и с котом.$h'),
             sp(H, 'Она до сих пор лежит у меня в столе.$0')],
        ]),
        'pause 400',
        sp(H, 'Поэтому договоримся. Я больше не спрашиваю «ты в порядке?».$a#$b#Я спрашиваю: «что болит?». А ты отвечаешь. Хоть жестом.$a'),
        sp(H, 'Повязку меняем завтра, до обеда. Я напомню, если забудешь. А ты забудешь.$h'),
        sp(H, 'И домой я тебя провожу. Не обсуждается.$a#$b#…Ладно, обсуждается. По дороге.$h'),
        'addConversationTopic HarveyArc3_KnowsWhy 7',
        'action AddMail Current HarveyArc3_N1_Bandage tomorrow',
    ],
    ending='end warpOut')

# ---------------------------------------------------------------- N2
n2_key = key('N2_Spring', 'Weather Sunny', 'Time 1000 1700', 'Friendship Harvey 2000',
             f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.N1_NightShift',
             'GameStateQuery !PLAYER_NPC_RELATIONSHIP Current Harvey Married')
n2 = script(
    'continue', '47 24', 'farmer 46 24 3 Harvey 48 24 3',
    skip_cd('AddConversationTopic Current HarveyArc3_Spring 7'),
    [
        'viewport 47 24 true', 'pause 600',
        msg('Ты привела Харви туда, куда не водишь никого: к источнику за западным лесом. Вода светится, будто помнит что-то своё.'),
        sp(H, 'Значит, это и есть знаменитый источник. Говорят, лечит.$0#$b#Как врач я обязан сказать: вода не лечит. Как человек — я уже закатал рукава.$h'),
        'emote farmer 32',
        qq(['Показать на воду', 'Сесть на камень у берега', 'Протянуть ему пустую склянку'], [
            ['move farmer -1 0 3',
             msg('Ты подходишь к самой кромке и показываешь: опусти руки.'),
             sp(H, 'Холодная. Очень.$u'),
             sp(H, 'Руки — минуту, не больше. Ноги — даже не думай. Я считаю, и не смотри на меня так.$a'),
             'friendship Harvey 30'],
            [msg('Ты садишься на тёплый камень. Через миг он садится рядом — на расстоянии вытянутой руки.'),
             sp(H, 'Тишина здесь другая. Не больничная.$s'),
             'friendship Harvey 30'],
            [msg('Ты протягиваешь склянку. Он смеётся — коротко, удивлённо.'),
             sp(H, 'Пробу для Мару? Ты меня слишком хорошо знаешь.$h'),
             sp(H, 'Если в ней найдётся что-то полезное, я первым извинюсь перед феями.$h'),
             'friendship Harvey 35'],
        ]),
        'pause 600',
        sp(H, 'Знаешь, что странно? Здесь я не знаю правил.$0#$b#Где можно ступать, что можно трогать, кто тут хозяин. В клинике держу я. А здесь…$s'),
        sp(H, '…здесь, кажется, держишь ты.$u'),
        'pause 500',
        sp(H, 'Непривычно. И почему-то легче.$s'),
        'pause 400',
        sp(H, 'Есть вещь, которую я однажды скажу. Не сегодня.$0#$b#Когда ты будешь готова её услышать. И когда я сам буду готов её сказать.$u'),
        'emote farmer 16',
        sp(H, 'Не пугайся, медицинских новостей нет.$h#$b#А теперь обратно. Тропа скользкая, первым иду я — это я решил, пока ты держала склянку.$a'),
        'addConversationTopic HarveyArc3_Spring 7',
    ])

# ---------------------------------------------------------------- N3
n3_key = key('N3_ContactCard', 'Time 0900 1500', 'Friendship Harvey 2000',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating')
n3 = script(
    'Hospital_Ambient', '10 15', 'Harvey 10 14 2 farmer -1000 -1000 0',
    skip_cd('AddConversationTopic Current HarveyArc3_Rules 7',
            'AddMail Current HarveyArc3_N3_Rules tomorrow'),
    [
        'viewport 10 15 true', 'pause 400', 'playSound doorOpen',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -3 0', 'pause 400',
        'emote Harvey 20',
        sp(H, 'Доброе утро, солнышко.$l#$b#…Я репетировал это слово полночи. Звучит?$h'),
        qq(['Кивнуть', 'Спрятать улыбку', 'Покраснеть и отвернуться'], [
            ['emote farmer 32', sp(H, 'Принято. Остаётся.$h')],
            [msg('Ты прикусываешь губу, чтобы не улыбнуться. Не получается.'), sp(H, 'Вижу. Засчитано.$l')],
            ['faceDirection farmer 3', sp(H, 'Значит, звучит. Отлично.$h'), 'faceDirection farmer 0'],
        ]),
        msg('Он достаёт из ящика твою медицинскую карту и открывает первую страницу.'),
        sp(H, 'Здесь написано: «Лечащий врач — Харви». Это остаётся.$0#$b#А вот графа «экстренный контакт» была пустой.$a'),
        msg('Он аккуратно вписывает своё имя. Почерк, как всегда, ужасный.'),
        sp(H, 'Теперь, если с тобой что-то случится, звонят мне. Не потому что я врач. Потому что я — твой.$l'),
        'pause 500',
        sp(H, 'И раз уж я теперь официально твой… три правила для моей девушки.$a#$b#Обсуждаются. Почти.$h'),
        sp(H, 'Первое: завтрак. Каждый день, хоть маленький.$a#$b#Второе: перед шахтой — записка. Куда, надолго ли, когда вернёшься.$a#$b#Третье: боль не терпят до утра. Болит — идёшь ко мне. В любое время.$a'),
        qq(['Завтрак', 'Записку перед шахтой', 'Боль до утра', 'Оставить все три'], [
            [sp(H, 'Завтрак? Серьёзно?$a'),
             sp(H, '…Хорошо, вычёркиваю. Но тогда по средам я приношу его сам. Это не правило — это доставка.$h'),
             'addConversationTopic HarveyArc3_RuleBreakfast 7', 'friendship Harvey 30'],
            [sp(H, 'Записку…$u'),
             sp(H, 'Ладно. Без записки. Но тогда ты возвращаешься до десяти вечера, а я жду у лифта. С бутербродом и очень выразительным лицом.$a'),
             'addConversationTopic HarveyArc3_RuleMines 7', 'friendship Harvey 30'],
            [sp(H, 'Нет. Вот это — нет.$a'), 'pause 400',
             sp(H, 'Прости. Спорить можно. Но это правило я буду защищать, как пациента на столе. Вычеркни другое — или оставь все.$s'),
             sp(H, '…Вижу по лицу — оставляем все. Спасибо, солнышко.$l'),
             'friendship Harvey 25'],
            ['emote Harvey 16', sp(H, 'Все три? Без торга?$u'),
             sp(H, 'Мне нужно присесть. Я морально готовился к войне.$h'),
             'friendship Harvey 45'],
        ], question='"Вычеркнуть одно правило?"'),
        sp(H, 'Карта лежит в верхнем ящике. Теперь на ней две подписи — твоя и моя.$0#$b#А сейчас иди. И позавтракай: я знаю, что ты не завтракала, моя девочка.$h'),
        'addConversationTopic HarveyArc3_Rules 7',
        'action AddMail Current HarveyArc3_N3_Rules tomorrow',
    ])

# ---------------------------------------------------------------- N4
n4_key = key('N4_BlueMoon', 'Weather Sunny', 'Season Spring Summer Fall', 'Time 1900 2300',
             'Friendship Harvey 2250',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating',
             f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.N3_ContactCard')
CONFESSED = 'action AddMail Current HarveyArc3_Confessed received'
n4 = script(
    'harveys_theme_jazz', '29 48', 'farmer 28 49 1 Harvey 30 49 3',
    skip_cd(),
    [
        'viewport 29 48 true', 'pause 600',
        msg('Вечером на винограднике «Голубая луна» почти никого. С моря над рядами лоз тянет холодом.'),
        sp(H, 'Я заказал ужин на двоих и забыл, что у воды здесь дует. Плохой врач.$s'),
        msg('Ты обхватываешь себя руками — пальцы уже ледяные.'),
        sp(H, 'Ты дрожишь.$a'),
        msg('Он уже снимает пальто.'),
        sp(H, 'Не спорь.$a#$b#…Ладно, спорь. Но в пальто.$h'),
        qq(['Позволить укутать себя', 'Возмутиться: «А ты?»', 'Отступить на шаг'], [
            [msg('Пальто тяжёлое и тёплое. Пахнет антисептиком и кофе.'),
             sp(H, 'Вот. Теперь и у меня нормальный пульс.$l'), 'friendship Harvey 30'],
            [sp(H, 'Я? У меня свитер, упрямство и профессиональный иммунитет.$h'),
             sp(H, 'А у тебя — пальто. Спор окончен: ты в нём уже.$a'), 'friendship Harvey 30'],
            [sp(H, 'Хорошо. Не подхожу.$0'),
             msg('Он кладёт пальто на скамью рядом с тобой и отходит на шаг.'),
             sp(H, 'Оно здесь. Остынет — заберу и буду ворчать. Выбор за тобой.$u'),
             msg('Через минуту ты всё-таки накидываешь его на плечи.'), 'friendship Harvey 30'],
        ]),
        'pause 600',
        sp(H, 'Помнишь источник? Я сказал, что однажды скажу тебе кое-что.$0'),
        sp(H, 'Кажется, я готов. Но слушать или нет — решаешь ты.$u'),
        qq(['Слушать', 'Взять его за руку', '«Я пока не готова это услышать»'], [
            [sp(H, 'Я люблю тебя.$l#$b#Не как пациентку, которую надо спасти. Как человека, без которого клиника — просто здание.$l'),
             sp(H, 'Вот. Сказал. Пульс сто двадцать, если тебе интересно.$h'),
             'addConversationTopic HarveyArc3_SaidIt 10', CONFESSED, 'friendship Harvey 60'],
            [msg('Ты берёшь его ладонь. Она тёплая, несмотря на ветер.'),
             sp(H, 'Тогда скажу прямо сюда.$l'),
             sp(H, 'Я люблю тебя, @. Давно. Наверное, с той мокрой дорожки. Просто не знал, как записать это в карту.$l'),
             'addConversationTopic HarveyArc3_SaidIt 10', CONFESSED, 'friendship Harvey 70'],
            [sp(H, 'Хорошо.$0'), 'pause 500',
             sp(H, 'Тогда я подожду. Но знай: оно уже есть. И никуда не денется.$l'),
             'action AddMail Current HarveyArc3_ConfessionPending received', 'friendship Harvey 40'],
        ]),
        sp(H, 'Ужин остывает. И пальто ты вернёшь мне только у двери фермы — я провожу.$h'),
    ])

# ---------------------------------------------------------------- N5 (+ вариант с отложенным признанием)
N5_COMMON = ['Weather Sunny Wind Snow', 'Time 1200 1800', 'Friendship Harvey 2500',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Dating Married',
             'GameStateQuery PLAYER_VISITED_LOCATION Current Custom_Highlands',
             f'GameStateQuery ANY "PLAYER_HAS_SEEN_EVENT Current {NS}.N4_BlueMoon" "PLAYER_NPC_RELATIONSHIP Current Harvey Married"']


def n5_body(confess):
    body = [
        'viewport 33 26 true', 'pause 500',
        msg('На плато у тропы к Хайлендсу кто-то сидит на камне, вытянув ногу. Белая рубашка. Знакомая сумка.'),
        'emote farmer 16', 'move farmer 4 0 1',
        sp(H, '…Ты не должна была меня здесь увидеть.$s'),
        sp(H, 'Я узнал, что ты ходишь в Хайлендс. Одна. Хотел дойти до развилки — просто посмотреть, насколько там опасно.$s#$b#Выяснил. Очень опасно. Особенно камни.$u'),
        msg('Лодыжка распухла. Он пытается встать — и бледнеет.'),
        sp(H, 'Так. Спокойно. Растяжение, без перелома, я почти уверен. Сначала надо…$a'),
        sp(H, 'Нет, подожди, бинт не так, начинай от пальцев… или…$a'),
        'pause 400',
        msg('Ты кладёшь ладонь ему на плечо. Он замолкает.'),
        qq(['Перевязать молча', 'Отдать ему бинт', 'Позвать Марлона'], [
            [msg('Ты достаёшь аптечку — ту самую, из «домашнего протокола». Восьмёркой, от пальцев к голени, не туго. Как он учил.'),
             sp(H, '…Правильно. Всё правильно.$s'),
             sp(H, 'Очень неприятно, когда о тебе заботятся. Как ты это выносила?$u'),
             'friendship Harvey 50'],
            [msg('Ты протягиваешь ему бинт. Он смотрит на него — и возвращает.'),
             sp(H, 'Нет. Перевяжи ты. Я хочу понять, каково это — довериться.$s'),
             msg('Ты бинтуешь. Он ни разу не поправляет.'),
             'friendship Harvey 45'],
            ['warp Marlon 30 26', 'move Marlon 3 0 1',
             sp('Marlon', 'Доктор? На моей тропе? Я много чего повидал, но такого — нет.$h'),
             sp(H, 'Марлон. В гильдии — ни слова.$a'),
             sp('Marlon', 'Ни слова. Разве что пару. Обопритесь на плечо, доктор, а фермерша подстрахует с другой стороны.$0'),
             msg('Вдвоём вы поднимаете его на ноги.'),
             'friendship Harvey 40'],
        ]),
        'pause 500',
        sp(H, 'Я злюсь. Не на тебя — на себя. Пошёл проверить, безопасно ли тебе, и сам стал тем, кого надо спасать.$s'),
        sp(H, 'Но раз уж я сижу здесь с ногой в бинте — давай договоримся.$a#$b#В Хайлендс ты одна не ходишь. Записка, время возвращения, и я жду на плато.$a'),
        sp(H, 'И я туда один не хожу. Никаких тайных проверок. Справедливо, как бы мне ни хотелось обратного.$h'),
        qq(['Кивнуть', 'Протянуть мизинец', 'Показать на его ногу: сначала это'], [
            ['emote farmer 32', sp(H, 'Договор. Двусторонний. Первый в моей практике.$h'), 'friendship Harvey 30'],
            [msg('Ты протягиваешь мизинец. Он смотрит на него очень серьёзно — и сцепляет со своим.'),
             sp(H, 'Клятва на мизинцах. Самая надёжная форма медицинского согласия.$h'), 'friendship Harvey 35'],
            [sp(H, 'Да. Ты права, солнышко. Сначала нога, потом договоры.$l'),
             sp(H, 'Видишь? Я учусь быть пациентом. Плохо, но учусь.$h'), 'friendship Harvey 35'],
        ]),
    ]
    if confess:
        body += [
            'pause 500',
            sp(H, 'И ещё. На винограднике я обещал подождать.$0#$b#Я ждал. А сидя здесь на камне, вдруг понял, что не хочу больше ждать подходящего момента.$u'),
            sp(H, 'Я люблю тебя. Можешь не отвечать. Мне достаточно, что ты здесь.$l'),
            CONFESSED, 'addConversationTopic HarveyArc3_SaidIt 10', 'friendship Harvey 40',
        ]
    body += [
        sp(H, 'А теперь домой. Ведёшь ты. Я хромаю и делаю вид, что это не унизительно.$h'),
        'addConversationTopic HarveyArc3_Limping 3',
        'addConversationTopic HarveyArc3_HighlandsPact 14',
        'action AddMail Current HarveyArc3_N5_Ankle tomorrow',
    ]
    return body


N5_SKIP = skip_cd('AddConversationTopic Current HarveyArc3_HighlandsPact 14',
                  'AddMail Current HarveyArc3_N5_Ankle tomorrow')
N5_ACTORS = 'farmer 30 26 1 Harvey 35 26 3 Marlon -1000 -1000 1'
n5a_key = key('N5_ReversedKit', *N5_COMMON,
              f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {NS}.N5_ReversedKit_Confess',
              'GameStateQuery !PLAYER_HAS_MAIL Current HarveyArc3_ConfessionPending Received')
n5b_key = key('N5_ReversedKit_Confess', *N5_COMMON,
              f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {NS}.N5_ReversedKit',
              'GameStateQuery PLAYER_HAS_MAIL Current HarveyArc3_ConfessionPending Received')
n5a = script('continue', '33 26', N5_ACTORS, N5_SKIP, n5_body(False))
n5b = script('continue', '33 26', N5_ACTORS, N5_SKIP + [CONFESSED.replace('action ', '')], n5_body(True))

# ---------------------------------------------------------------- N6
n6_key = key('N6_StormCall', 'Weather Storm', 'Time 0900 1500', 'Friendship Harvey 3000',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married',
             f'GameStateQuery ANY "PLAYER_HAS_SEEN_EVENT Current {NS}.N5_ReversedKit" "PLAYER_HAS_SEEN_EVENT Current {NS}.N5_ReversedKit_Confess"')
n6 = script(
    'rain', '10 15', 'Harvey 10 14 2 farmer -1000 -1000 0 Maru -1000 -1000 0',
    skip_cd('AddMail Current HarveyArc3_N6_Report tomorrow'),
    [
        'ambientLight 80 80 110', 'viewport 10 15 true', 'playSound thunder',
        'warp farmer 10 19', 'faceDirection farmer 0', 'move farmer 0 -3 0', 'emote farmer 28',
        sp(H, 'Пришла. По плану. Умница, котёнок.$l'),
        sp(H, 'А вот «мокрая насквозь» в план не входило. Сюда.$a'),
        msg('Через минуту у тебя в руках кружка, на плечах плед, а на столе лампа, которую он не выключит, пока не стихнет гром.'),
        sp(H, 'Сегодня главный здесь я. Возражения принимаются после чая.$a'),
        'playSound thunder', 'emote farmer 28',
        sp(H, 'Дыши со мной. Вдох на четыре, выдох на шесть. Я считаю.$0'),
        'pause 1000',
        msg('Гром уходит за холмы. Харви не выпускает твою ладонь.'),
        'pause 600', 'playSound doorOpen', 'warp Maru 10 19', 'move Maru 0 -1 0',
        sp('Maru', 'Доктор! Простите… Линус сорвался со склона у палатки. Рука, похоже, сломана, сам он не спустится.$s'),
        sp(H, '…$s'),
        msg('Он смотрит на тебя, на окно, на дверь. Видно, как тяжело ему выбирать.'),
        sp(H, 'Мару, возьми шину и… нет. Я не могу её оставить. Не в грозу.$a'),
        qq(['«Иди»', 'Попросить остаться', '«Иди — и возьми меня с собой»'], [
            [msg('Ты отпускаешь его руку и сама вкладываешь ему в ладонь ремень от сумки.'),
             sp(H, 'Ты уверена?$u'), 'emote farmer 40',
             sp(H, 'Хорошо. Хорошо.$s'),
             msg('Он быстро, не глядя, пишет на бланке рецептов: «Чай. Плед. Лампа не гаснет. Дверь не запирать».'),
             sp(H, 'Список на столе. Лампу не выключать. Я вернусь раньше, чем ты успеешь соскучиться, солнышко.$l'),
             sp(H, '…Почти раньше.$h'),
             'addConversationTopic HarveyArc3_LetHimGo 7', 'friendship Harvey 60'],
            [sp(H, 'Тогда остаюсь.$0'),
             sp(H, 'Мару, бери Себастьяна и носилки. Звони мне каждые десять минут — буду руководить по телефону.$a'),
             sp('Maru', 'Поняла, доктор!$h'),
             msg('Он остаётся. Но весь следующий час ходит от окна к телефону и обратно.'),
             sp(H, 'Не вини себя. Это мой выбор. Просто я — очень беспокойный выбор.$s'),
             'addConversationTopic HarveyArc3_HeStayed 7', 'friendship Harvey 40'],
            [sp(H, 'С собой? В грозу, на склон?$a'), 'pause 400',
             sp(H, 'Нет. Это единственное «нет» за сегодня, и оно твёрдое.$a#$b#Но ты можешь сделать другое: остаться здесь и встретить нас. Мне понадобятся тёплые руки и горячая вода. Ты — мой тыл.$l'),
             'addConversationTopic HarveyArc3_LetHimGo 7', 'friendship Harvey 50'],
        ]),
        'globalFade',
        msg('К вечеру гроза стихла. На столе осталась записка его ужасным почерком: «Все живы. Линус ворчит. Ты — главная героиня этого дня».'),
        'action AddMail Current HarveyArc3_N6_Report tomorrow',
    ])

# ---------------------------------------------------------------- N7
n7_key = key('N7_Key', 'Time 1300 1500', 'Friendship Harvey 3250',
             'GameStateQuery PLAYER_NPC_RELATIONSHIP Current Harvey Married',
             f'GameStateQuery PLAYER_HAS_SEEN_EVENT Current {NS}.N6_StormCall')
n7 = script(
    'Hospital_Ambient', '14 6', 'farmer 14 6 1 Harvey 15 6 3',
    skip_cd('AddConversationTopic Current HarveyArc3_KeyGiven 14',
            'AddMail Current HarveyArc3_Graduated received'),
    [
        'viewport 14 6 true', 'pause 500',
        sp(H, 'Приём окончен. Садись, котёнок. Сегодня ты не пациентка, а ученица.$h'),
        msg('Он выкладывает на кушетку бинты, шину, ножницы и маленький латунный ключ.'),
        sp(H, 'Это запасной ключ от клиники.$0#$b#После плато мы оба знаем: однажды на кушетке могу оказаться я. Или Мару. Или кто-то, кого ты найдёшь в лесу.$a'),
        sp(H, 'Так что сейчас будет урок. Строгий. Я буду придираться. Это любовь в медицинской форме.$a'),
        msg('Он протягивает тебе руку — свою. «Перевяжи запястье. Растяжение. Пациент капризный».'),
        qq(['Начать с фиксации у ладони', 'Затянуть покрепче — для надёжности', 'Сначала спросить взглядом, не больно ли'], [
            [sp(H, 'Правильно. Восьмёркой, через ладонь… да.$0'),
             sp(H, 'Узел кривой. Но держит. Поставил бы «отлично» и спрятал гордость за ворчанием.$h'),
             'friendship Harvey 40'],
            [sp(H, 'Ай. Слишком туго — через десять минут пальцы посинеют.$a'),
             sp(H, 'Ослабь. Вот так. Видишь? Ошибиться здесь не страшно. Страшно не проверить.$0'),
             'friendship Harvey 30'],
            [msg('Ты поднимаешь на него глаза, не начиная.'),
             sp(H, '…Ты спросила, больно ли мне. Раньше любых манипуляций.$s'),
             sp(H, 'Этому я научить не мог. Это у тебя своё.$l'),
             'friendship Harvey 50'],
        ]),
        sp(H, 'Официально: ты мой экстренный контакт. А я по-прежнему твой.$l'),
        sp(H, 'Это не обсуждается.$a#$b#…Хорошо, обсуждается. Но я выиграю.$h'),
        qq(['Завязать последний узел', 'Перевязать ему вторую руку — просто так', 'Положить ключ в карман и обнять'], [
            [msg('Ты затягиваешь узел — ровно, как он показывал.'),
             sp(H, 'Идеально. Ну, почти. Только не говори Мару, что я так сказал.$h')],
            [msg('Ты молча бинтуешь ему вторую руку. Совершенно здоровую.'),
             sp(H, 'Это… профилактика?$u'),
             sp(H, 'Принято. Теперь я самый перебинтованный врач в долине.$h')],
            [msg('Ключ холодный. Объятие — нет.'),
             sp(H, 'Вот так. Теперь у тебя ключ от клиники, а у меня — ты.$l')],
        ]),
        sp(H, 'И ещё. Я перестану звонить тебе каждый вечер, когда ты одна дома.$s#$b#Ты справляешься, я видел. Буду звонить через вечер. Это огромная уступка, цени.$h'),
        'addConversationTopic HarveyArc3_KeyGiven 14',
        'action AddMail Current HarveyArc3_Graduated received',
    ])


def patch(log, target, entries):
    return {'LogName': log, 'Action': 'EditData', 'Target': target, 'Entries': entries}


data = {'Changes': [
    patch('Arc3 N1 — «Ночная смена» (Town → Hospital, ночь, 8♥)', 'Data/Events/Town', {n1_key: n1}),
    patch('Arc3 N2 — «Источник» (SVE Sprite Spring, день, 8♥)', 'Data/Events/Custom_SpriteSpring2', {n2_key: n2}),
    patch('Arc3 N3 — «Графа „близкие“» (Hospital, Dating)', 'Data/Events/Hospital', {n3_key: n3}),
    patch('Arc3 N4 — «Голубая луна» (SVE Blue Moon Vineyard, Dating)', 'Data/Events/Custom_BlueMoonVineyard', {n4_key: n4}),
    patch('Arc3 N5 — «Перевёрнутая аптечка» (SVE Adventurer Summit, Dating/Married)',
          'Data/Events/Custom_AdventurerSummit', {n5a_key: n5a, n5b_key: n5b}),
    patch('Arc3 N6/N7 — «Гроза и вызов», «Ключ» (Hospital, Married)', 'Data/Events/Hospital', {n6_key: n6, n7_key: n7}),
]}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('written', OUT, sum(len(c['Entries']) for c in data['Changes']), 'events')
