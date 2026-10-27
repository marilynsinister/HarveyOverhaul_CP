"""Генерирует assets/Code/herbalWorkshop.json — «мастерская трав», продолжение аптекарского сада (этап 4 roadmap).

Открывается после финала цепочки сада (флаг {{ModId}}_HerbalGardenFinished), по письму в день:
  1. сушилка: 5 любых трав сада → 2 «Сушёные травы» (правило для ванильной Dehydrator) + рецепт «Чайный запас»
     (травы + мёд → 3 обычных травяных сбора);
  2. «Согревающий чай» (травы + имбирь) — новый напиток: +1 защита, +1 скорость на 8 часов;
  3. «Травяной бальзам» (травы + масло + 2 сока) — подарок, который любят Эвелин и Джордж;
  4. «Антисептик на травах» (травы + 2 волокна → 2 обычных антисептика).

Сезонные заготовки для клиники — раз в год, письмо 3–9 числа сезона, адресаты разные:
  весна — Харви, 3 сушёных травы (саше от пыльцы); лето — Пэм, 2 аптекарских сбора (после жары);
  осень — Эвелин, 3 согревающих чая (старикам к холодам); зима — Джордж, 2 бальзама (руки трескаются).
Ничего из этого не продаётся в клинике.

Иконки — scripts/generate_workshop_sprites.py → assets/Items/workshopItems.png.
Запуск:  python scripts/build_herbal_workshop.py
"""
import json
import os

from event_builder import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Code', 'herbalWorkshop.json')
M = '{{ModId}}'
FINISHED = f'PLAYER_HAS_MAIL Current {M}_HerbalGardenFinished Received'

OBJECTS = {
    f'{M}_DriedHerbs': {
        'Name': f'{M}_DriedHerbs', 'DisplayName': 'Сушёные травы',
        'Description': 'Пучок трав из аптекарского сада, высушенный до хруста. Пахнет летом даже зимой. Основа для чаёв и бальзамов.',
        'Type': 'Basic', 'Category': -26, 'Price': 95, 'Texture': f'Mods/{M}/WorkshopItems', 'SpriteIndex': 0,
        'Edibility': -300, 'ExcludeFromShippingCollection': True, 'ExcludeFromRandomSale': True,
        'ContextTags': [f'{M}_dried_herbs', f'{M}_workshop_item'],
    },
    f'{M}_WarmingTea': {
        'Name': f'{M}_WarmingTea', 'DisplayName': 'Согревающий чай',
        'Description': 'Сушёные травы и имбирь. Харви наливает такой всем, кто пришёл в клинику с мороза. Согревает изнутри.',
        'Type': 'Cooking', 'Category': -7, 'Price': 160, 'Texture': f'Mods/{M}/WorkshopItems', 'SpriteIndex': 1,
        'Edibility': 30, 'IsDrink': True, 'ExcludeFromShippingCollection': True,
        'Buffs': [{'Id': f'{M}_WarmingTea', 'Duration': 480, 'CustomAttributes': {'Defense': 1, 'Speed': 1}}],
        'ContextTags': ['hot_drink_item', 'drink_item', f'{M}_workshop_item'],
    },
    f'{M}_HerbBalm': {
        'Name': f'{M}_HerbBalm', 'DisplayName': 'Травяной бальзам',
        'Description': 'Мягкий бальзам на масле и смоле с сушёными травами. Для обветренных рук и тех, кто много работает на холоде.',
        'Type': 'Basic', 'Category': 0, 'Price': 150, 'Texture': f'Mods/{M}/WorkshopItems', 'SpriteIndex': 2,
        'Edibility': -300, 'ExcludeFromShippingCollection': True, 'ExcludeFromRandomSale': True,
        'ContextTags': [f'{M}_workshop_item'],
    },
}

DEHYDRATOR = {
    f'{M}_DriedHerbs': {
        'Id': f'{M}_DriedHerbs',
        'Triggers': [{'Id': 'ItemPlacedInMachine', 'Trigger': 'ItemPlacedInMachine',
                      'RequiredTags': [f'{M}_medicinal_herb'], 'RequiredCount': 5}],
        'OutputItem': [{'Id': f'(O){M}_DriedHerbs', 'ItemId': f'(O){M}_DriedHerbs', 'MinStack': 2, 'MaxStack': 2}],
        'DaysUntilReady': 1,
        'InvalidCountMessage': '[LocalizedText Strings\\Objects:Machine_NeedsInputCount 5]',
    },
}

COOKING = {
    f'{M}_TeaStockRecipe': f'{M}_DriedHerbs 1 340 1/1 10/{M}_HerbalTea 3/none/Чайный запас',
    f'{M}_WarmingTeaRecipe': f'{M}_DriedHerbs 1 829 1/1 10/{M}_WarmingTea 1/none/Согревающий чай',
}
CRAFTING = {
    f'{M}_HerbBalmRecipe': f'{M}_DriedHerbs 1 247 1 92 2/Home/{M}_HerbBalm 1/false/none/Травяной бальзам',
    f'{M}_HerbAntisepticRecipe': f'{M}_DriedHerbs 1 771 2/Home/{M}_Antiseptic 2/false/none/Антисептик на травах',
}

# Письма-рецепты: по одному в день, в этом порядке.
RECIPE_MAIL = [
    ('Dryer', 'cookingRecipe', f'{M}_TeaStockRecipe', 'Сушилка',
     '@,^^Сад работает лучше, чем я надеялся: у меня на подоконнике уже не помещаются пучки.^^Если у тебя есть сушилка '
     '(её продаёт Пьер), положи в неё пять любых трав из нашего сада — к утру будет два пучка сушёных. Они хранятся '
     'всю зиму.^^А из пучка и ложки мёда получается целый чайный запас: три обычных травяных сбора. Рецепт прилагаю.^^— Харви'),
    ('Warming', 'cookingRecipe', f'{M}_WarmingTeaRecipe', 'Согревающий чай',
     '@,^^Второй рецепт — мой любимый. Сушёные травы и имбирь. Я наливаю такой всем, кто приходит в клинику с мороза, '
     'и половина сразу перестаёт спорить.^^Пей перед шахтой зимой. Это не назначение. Почти.^^— Харви'),
    ('Balm', 'craftingRecipe', f'{M}_HerbBalmRecipe', 'Бальзам для рук',
     '@,^^Эвелин научила меня бальзаму, которым мазала руки Джорджу после столярки: травы, капля масла и немного смолы.^^'
     'Я записал состав точнее, чем она диктовала. Она сказала, что я «зануда в халате». Это правда.^^— Харви'),
    ('Antiseptic', 'craftingRecipe', f'{M}_HerbAntisepticRecipe', 'Антисептик на травах',
     '@,^^Последняя страница тетради — практическая. Из пучка сушёных трав и волокна выходит антисептик не хуже '
     'того, что на моей полке. Две порции.^^Теперь у тебя дома почти вся клиника. Пожалуйста, пусть она пригождается '
     'как можно реже.^^— Харви'),
]


def recipe_mail():
    mail, triggers = {}, {}
    previous = None
    for name, kind, recipe, title, text in RECIPE_MAIL:
        mail_id = f'{M}_mailWorkshop{name}'
        mail[mail_id] = f'{text}%item {kind} {recipe} %%[#]{title}'
        cond = f'{FINISHED}, !PLAYER_HAS_MAIL Current {mail_id} Any'
        if previous:
            cond = f'PLAYER_HAS_MAIL Current {previous} Received, ' + cond
        tid = f'{M}_triggerWorkshop{name}'
        triggers[tid] = {'Id': tid, 'Trigger': 'DayStarted', 'Condition': cond, 'Actions': [f'AddMail Current {mail_id} now']}
        previous = mail_id
    return mail, triggers


SEASONAL = [
    ('spring', 'Pollen', 'Харви', 'Harvey', f'(O){M}_DriedHerbs', 3, 'Саше от пыльцы',
     '@,^^Весной в клинику приходят с красными глазами и чиханием на всю приёмную. Шейн уверяет, что это не аллергия, '
     'а «весна в целом».^^Я шью маленькие саше из сушёных трав — их кладут под подушку. Нужно три пучка. '
     'Если в сушилке найдутся, занеси, пожалуйста.^^— Харви',
     'Саше от пыльцы/Весной в клинике чихают все. Харви шьёт для пациентов маленькие саше из сушёных трав./Принеси Харви 3 пучка сушёных трав.',
     'Пахнет так, что даже Шейн перестал спорить.$h#$b#Сошью сегодня вечером. Первое — тебе, под подушку. Не отказывайся, это профилактика.$l'),
    ('summer', 'Heat', 'Пэм', 'Pam', f'(O){M}_GardenBlend', 2, 'После жары',
     '@,^^Пэм после теплового удара пьёт только холодное пиво и уверяет, что это «восстановление водного баланса».^^'
     'Я бы предложил ей наш аптекарский сбор — остуженный, с лимоном. От меня она не возьмёт. От тебя — возьмёт.^^'
     'Два сбора, если не трудно.^^— Харви',
     'После жары/Пэм никак не восстановится после летней жары, а лекарства из клиники пить отказывается./Отнеси Пэм 2 аптекарских сбора Харви.',
     'Это от дока? Ну… раз ты принесла — выпью. Холодный? С лимоном? Хм.$s#$b#…Слушай, а неплохо. Только ему не говори, что мне понравилось.$h'),
    ('fall', 'Cold', 'Эвелин', 'Evelyn', f'(O){M}_WarmingTea', 3, 'Старикам к холодам',
     '@,^^Эвелин собирает корзинки для тех, кто живёт один, — к первым холодам. Попросила у меня «что-нибудь тёплое, '
     'но не горькое».^^Согревающий чай подойдёт лучше всего. Три чашки — и она обещала отнести их сама.^^— Харви',
     'Старикам к холодам/Эвелин собирает корзинки для одиноких соседей и просит что-нибудь тёплое, но не горькое./Отнеси Эвелин 3 согревающих чая.',
     'Ох, имбирь! Как раз то, что нужно. Линусу — первую, он опять ночует у костра.$h#$b#Спасибо, дорогая. Доктор говорил, что ты сама их готовишь. Он очень тобой гордится — правда, только мне об этом и говорит.$l'),
    ('winter', 'Hands', 'Джордж', 'George', f'(O){M}_HerbBalm', 2, 'Руки трескаются',
     '@,^^Джордж зимой не носит перчатки из принципа, а потом прячет руки в карманы, чтобы я не видел трещины.^^'
     'Бальзам Эвелин по нашему рецепту — то, что нужно. Две баночки. Отнеси, пожалуйста, сама: мне он скажет, что всё в порядке.^^— Харви',
     'Руки трескаются/Джордж зимой не носит перчатки, а трещины на руках прячет от доктора./Отнеси Джорджу 2 травяных бальзама.',
     'Бальзам? Я не просил.$a#$b#…Ладно. Эвелин всё равно заставит. Пахнет, как её старый, только лучше.$s#$b#Передай доктору, что у меня всё в порядке. И спасибо. Это тоже передай.$h'),
]


def seasonal():
    quests, mail, triggers = {}, {}, {}
    for season, name, _who_ru, npc, item, count, title, letter, quest_text, reaction in SEASONAL:
        qid = f'{M}_Prep{name}'
        quests[qid] = (f'ItemDelivery/{quest_text}/{npc} {item} {count}/-1/{300 + 100 * count}/-1/true/'
                       f'{reaction}#$action AddFriendshipPoints Harvey 40')
        mail_id = f'{M}_mailPrep{name}{{{{Year}}}}'
        mail[mail_id] = f'{letter}%item quest {qid} true %%[#]{title}'
        tid = f'{M}_triggerPrep{name}'
        triggers[tid] = {'Id': tid, 'Trigger': 'DayStarted',
                         'Condition': f'{FINISHED}, SEASON {season}, DAY_OF_MONTH 3 4 5 6 7 8 9, RANDOM 0.4, '
                                      f'!PLAYER_HAS_MAIL Current {mail_id} Any',
                         'Actions': [f'AddMail Current {mail_id} now'], 'MarkActionApplied': False}
    return quests, mail, triggers


def build():
    recipe_letters, recipe_triggers = recipe_mail()
    quests, season_mail, season_triggers = seasonal()
    return {'Changes': [
        {'Action': 'Load', 'Target': f'Mods/{M}/WorkshopItems', 'FromFile': 'assets/Items/workshopItems.png'},
        patch('Мастерская трав — предметы', 'Data/Objects', OBJECTS),
        {**patch('Мастерская трав — сушилка: 5 трав сада → 2 пучка', 'Data/Machines', DEHYDRATOR),
         'TargetField': ['(BC)Dehydrator', 'OutputRules']},
        patch('Мастерская трав — кухня', 'Data/CookingRecipes', COOKING),
        patch('Мастерская трав — изготовление', 'Data/CraftingRecipes', CRAFTING),
        {'Action': 'EditData', 'Target': 'Data/NPCGiftTastes', 'LogName': 'Мастерская трав — бальзам любят Эвелин и Джордж, чай нравится Харви',
         'TextOperations': [
             {'Operation': 'Append', 'Target': ['Fields', 'Evelyn', '1'], 'Value': f'{M}_HerbBalm', 'Delimiter': ' '},
             {'Operation': 'Append', 'Target': ['Fields', 'George', '1'], 'Value': f'{M}_HerbBalm', 'Delimiter': ' '},
             {'Operation': 'Append', 'Target': ['Fields', 'Harvey', '3'], 'Value': f'{M}_WarmingTea', 'Delimiter': ' '},
         ]},
        patch('Мастерская трав — сезонные заготовки для клиники', 'Data/Quests', quests),
        patch('Мастерская трав — письма', 'Data/Mail', {**recipe_letters, **season_mail}),
        patch('Мастерская трав — письма-рецепты и заготовки раз в год', 'Data/TriggerActions',
              {**recipe_triggers, **season_triggers}),
    ]}


if __name__ == '__main__':
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
    print('written', OUT)
