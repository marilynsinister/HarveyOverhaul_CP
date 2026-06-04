# Матрица покрытия диалогов Харви по уровням отношений

**Дата:** 2026-06-04  
**Источник:** split-файлы `assets/Code/dialogues/harvey_*.json` (manifest `dialoguesHarvey.json`)  
**Режим:** аудит покрытия; приоритет 1–2 дополнены в split-файлах (см. §9–10).

## Легенда

| Символ | Значение |
|--------|----------|
| ✓ | Есть хотя бы один патч `EditData` с этим ключом и условием стадии |
| — | Нет отдельного варианта для стадии |

**Стадии:** Base = блок без `When`; сердечные — по `Hearts:Harvey`; Dating/Married — по `Relationship:Harvey`. Topic-патчи с `HasConversationTopic` учитываются только в своих стадиях (не размазываются на Base).

**Охват:** 56 патчей, 506 уникальных ключей в `Characters/Dialogue/Harvey` + MarriageDialogue.

## Краткие выводы

| Метрика | Значение |
|---------|----------|
| Ключей: Base без Dating | 33 |
| Ключей: Base без Married | 56 |
| Ключей: 3–7 ❤ без 8–10 и Dating | 26 |
| topicHarvey* только в Base | 8 |
| Dating без Married | 32 |
| Married без Dating | 166 |
| Ключей с пересекающимися When | 281 |
| ⚠️ Специфичный патч раньше общего | 349 |

**Главный риск:** базовый слой (`harvey_base.json`) и блоки 4–7 ❤ без отдельных Dating/Married — при романе/браке игра часто возьмёт формальный «Вы» или нейтральный тон из Base.

**Лестница дней недели:** `Mon`–`Sun` / `*2` — только Base (+ частично Married для `Mon`/`Tue`/`Sat`); `*4`/`*6` — 3–7 ❤; `*8`/`*10` — 8–10 + Dating, без Married.

**Topic-травмы:** ~35 ключей `topicHarvey_*` в Base без разбивки по сердцам; исключения с Dating: `topicHarveyBadDay_*`, `topicHarveyMines_*`, часть `topicHarveyTrust_*`.

## 1. Повседневные (дни недели)

### Mon–Sun

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon` | ✓ | — | — | — | — | ✓ | ✓ |
| `Tue` | ✓ | — | — | — | — | ✓ | ✓ |
| `Wed` | ✓ | — | — | — | — | ✓ | ✓ |
| `Thu` | ✓ | — | — | — | — | ✓ | ✓ |
| `Fri` | ✓ | — | — | — | — | ✓ | ✓ |
| `Sat` | ✓ | — | — | — | — | ✓ | ✓ |
| `Sun` | ✓ | — | — | — | — | ✓ | ✓ |

### Mon2–Sun2

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Tue2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Wed2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Thu2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Fri2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Sat2` | ✓ | — | — | — | — | ✓ | ✓ |
| `Sun2` | ✓ | — | — | — | — | ✓ | ✓ |

### Mon4–Sun4

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon4` | — | — | ✓ | ✓ | — | — | — |
| `Tue4` | — | — | ✓ | ✓ | — | — | — |
| `Wed4` | — | — | ✓ | ✓ | — | — | — |
| `Thu4` | — | — | ✓ | ✓ | — | — | — |
| `Fri4` | — | — | ✓ | ✓ | — | — | — |
| `Sat4` | — | — | ✓ | ✓ | — | — | — |
| `Sun4` | — | — | ✓ | ✓ | — | — | — |

### Mon6–Sun6

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon6` | — | — | ✓ | ✓ | — | — | — |
| `Tue6` | — | — | ✓ | ✓ | — | — | — |
| `Wed6` | — | — | ✓ | ✓ | — | — | — |
| `Thu6` | — | — | ✓ | ✓ | — | — | — |
| `Fri6` | — | — | ✓ | ✓ | — | — | — |
| `Sat6` | — | — | ✓ | ✓ | — | — | — |
| `Sun6` | — | — | ✓ | ✓ | — | — | — |

### Mon8–Sun8

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Tue8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Wed8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Thu8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Fri8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Sat8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Sun8` | — | — | — | — | ✓ | ✓ | ✓ |

### Mon10–Sun10

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Mon10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Tue10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Wed10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Thu10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Fri10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Sat10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Sun10` | — | — | — | — | ✓ | ✓ | ✓ |

## 2. Госпиталь

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Hospital_Mon` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Tue` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Wed` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Thu` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Fri` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Sat` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital_Sun` | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Hospital` | — | — | — | ✓ | ✓ | — | — |
| `Hospital2` | — | — | — | ✓ | ✓ | — | — |
| `Hospital4` | — | — | ✓ | ✓ | — | — | — |
| `Hospital6` | — | — | ✓ | ✓ | — | — | — |
| `Hospital8` | — | — | — | — | ✓ | ✓ | — |
| `Hospital10` | — | — | — | — | ✓ | ✓ | — |
| `Hospital_Entry` | ✓ | — | — | — | — | — | — |

## 3. Время и состояние

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `timeReaction_Late` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `timeReaction_VeryLate` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `timeReaction_Early` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `situationReaction_Exhausted` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `situationReaction_Injured` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `situationReaction_Drunk` | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| `emotionalReaction_Crying` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `emotionalReaction_Scared` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 4. Локации

### `locationReaction_Mine*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `locationReaction_Mine` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### `locationReaction_SkullCave*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `locationReaction_SkullCave` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### `Desert*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Desert` | ✓ | — | — | ✓ | ✓ | ✓ | ✓ |
| `Desert10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Desert2` | ✓ | — | — | ✓ | ✓ | ✓ | ✓ |
| `Desert4` | — | — | ✓ | ✓ | — | — | — |
| `Desert6` | — | — | ✓ | ✓ | — | — | — |
| `Desert8` | — | — | — | — | ✓ | ✓ | ✓ |

### `Beach*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Beach` | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| `Beach10` | — | — | — | — | ✓ | ✓ | ✓ |
| `Beach2` | ✓ | — | — | ✓ | ✓ | ✓ | — |
| `Beach4` | — | — | ✓ | ✓ | — | — | — |
| `Beach6` | — | — | ✓ | ✓ | — | — | — |
| `Beach8` | — | — | — | — | ✓ | ✓ | ✓ |
| `Beach_10_15` | — | — | — | — | — | — | ✓ |
| `Beach_5_12` | — | — | — | — | — | — | ✓ |

### `Resort*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Resort` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Resort_Bar` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Resort_Chair` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Resort_Entering` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Resort_Leaving` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Resort_Shore` | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |

### `HarveyRoom*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `HarveyRoom` | — | — | — | ✓ | ✓ | ✓ | ✓ |
| `HarveyRoom10` | — | — | — | — | ✓ | ✓ | ✓ |
| `HarveyRoom2` | — | — | — | ✓ | ✓ | ✓ | ✓ |
| `HarveyRoom4` | — | — | ✓ | ✓ | — | — | — |
| `HarveyRoom6` | — | — | ✓ | ✓ | — | — | — |
| `HarveyRoom8` | — | — | — | — | ✓ | ✓ | ✓ |

### `ArchaeologyHouse*`

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `ArchaeologyHouse` | — | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| `ArchaeologyHouse10` | — | — | — | — | ✓ | ✓ | ✓ |
| `ArchaeologyHouse2` | — | — | — | ✓ | ✓ | — | — |
| `ArchaeologyHouse4` | — | — | ✓ | ✓ | — | — | — |
| `ArchaeologyHouse6` | — | — | ✓ | ✓ | — | — | — |
| `ArchaeologyHouse8` | — | — | — | — | ✓ | ✓ | ✓ |

## 5. Сезонные и фестивальные (`spring_*`, `summer_*`, `fall_*`, `winter_*`)

### spring_* (36 ключей)

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Spring_5` | — | — | — | ✓ | ✓ | — | — |
| `spring_1` | — | — | — | — | — | — | ✓ |
| `spring_10` | — | — | — | — | — | — | ✓ |
| `spring_11` | — | — | — | — | — | — | ✓ |
| `spring_12` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `spring_13` | ✓ | — | — | — | ✓ | ✓ | ✓ |
| `spring_14` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_15` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `spring_16` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `spring_17` | — | — | — | — | — | — | ✓ |
| `spring_18` | — | — | — | — | — | — | ✓ |
| `spring_19` | — | — | — | — | — | — | ✓ |
| `spring_2` | — | — | — | — | — | — | ✓ |
| `spring_20` | — | — | — | — | — | — | ✓ |
| `spring_21` | — | — | — | — | — | — | ✓ |
| `spring_22` | — | — | — | — | — | — | ✓ |
| `spring_23` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `spring_24` | — | — | — | — | — | — | ✓ |
| `spring_25` | — | — | — | — | — | — | ✓ |
| `spring_26` | — | — | — | — | — | — | ✓ |
| `spring_27` | — | — | — | — | — | — | ✓ |
| `spring_28` | — | — | — | — | — | — | ✓ |
| `spring_3` | — | — | — | — | — | — | ✓ |
| `spring_4` | — | — | — | — | — | — | ✓ |
| `spring_5` | — | — | — | — | — | — | ✓ |
| `spring_6` | — | — | — | — | — | — | ✓ |
| `spring_7` | — | — | — | — | — | — | ✓ |
| `spring_8` | — | — | — | — | — | — | ✓ |
| `spring_9` | — | — | — | — | — | — | ✓ |
| `spring_Fri` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Mon` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Sat` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Sun` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Thu` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Tue` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spring_Wed` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

### summer_* (36 ключей)

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Summer_12` | — | — | — | ✓ | ✓ | — | — |
| `summer_1` | — | — | — | — | — | — | ✓ |
| `summer_10` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `summer_11` | ✓ | — | — | — | ✓ | ✓ | ✓ |
| `summer_12` | — | — | — | — | — | — | ✓ |
| `summer_13` | — | — | — | — | — | — | ✓ |
| `summer_14` | — | — | — | — | — | — | ✓ |
| `summer_15` | — | — | — | — | — | — | ✓ |
| `summer_16` | — | — | — | — | — | — | ✓ |
| `summer_17` | — | — | — | — | — | — | ✓ |
| `summer_18` | — | — | — | — | — | — | ✓ |
| `summer_19` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `summer_2` | — | — | — | — | — | — | ✓ |
| `summer_20` | ✓ | — | — | — | — | ✓ | ✓ |
| `summer_21` | — | — | — | — | — | — | ✓ |
| `summer_22` | — | — | — | — | — | — | ✓ |
| `summer_23` | — | — | — | — | — | — | ✓ |
| `summer_24` | — | — | — | — | — | — | ✓ |
| `summer_25` | — | — | — | — | — | — | ✓ |
| `summer_26` | — | — | — | — | — | — | ✓ |
| `summer_27` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `summer_28` | — | — | — | — | — | — | ✓ |
| `summer_3` | — | — | — | — | — | — | ✓ |
| `summer_4` | — | — | — | — | — | — | ✓ |
| `summer_5` | — | — | — | — | — | — | ✓ |
| `summer_6` | — | — | — | — | — | — | ✓ |
| `summer_7` | — | — | — | — | — | — | ✓ |
| `summer_8` | — | — | — | — | — | — | ✓ |
| `summer_9` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Fri` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Mon` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Sat` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Sun` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Thu` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Tue` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `summer_Wed` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

### fall_* (36 ключей)

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Fall_20` | — | — | — | ✓ | ✓ | — | — |
| `fall_1` | — | — | — | — | — | — | ✓ |
| `fall_10` | — | — | — | — | — | — | ✓ |
| `fall_11` | — | — | — | — | — | — | ✓ |
| `fall_12` | — | — | — | — | — | — | ✓ |
| `fall_13` | — | — | — | — | — | — | ✓ |
| `fall_14` | — | — | — | — | — | — | ✓ |
| `fall_15` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `fall_16` | ✓ | — | — | — | ✓ | ✓ | ✓ |
| `fall_17` | — | — | — | — | — | — | ✓ |
| `fall_18` | — | — | — | — | — | — | ✓ |
| `fall_19` | — | — | — | — | — | — | ✓ |
| `fall_2` | — | — | — | — | — | — | ✓ |
| `fall_20` | — | — | — | — | — | — | ✓ |
| `fall_21` | — | — | — | — | — | — | ✓ |
| `fall_22` | — | — | — | — | — | — | ✓ |
| `fall_23` | — | — | — | — | — | — | ✓ |
| `fall_24` | — | — | — | — | — | — | ✓ |
| `fall_25` | — | — | — | — | — | — | ✓ |
| `fall_26` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `fall_27` | — | — | — | — | — | — | ✓ |
| `fall_28` | — | — | — | — | — | — | ✓ |
| `fall_3` | — | — | — | — | — | — | ✓ |
| `fall_4` | — | — | — | — | — | — | ✓ |
| `fall_5` | — | — | — | — | — | — | ✓ |
| `fall_6` | — | — | — | — | — | — | ✓ |
| `fall_7` | — | — | — | — | — | — | ✓ |
| `fall_8` | — | — | — | — | — | — | ✓ |
| `fall_9` | — | — | — | — | — | — | ✓ |
| `fall_Fri` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Mon` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Sat` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Sun` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Thu` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Tue` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fall_Wed` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

### winter_* (37 ключей)

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Winter_3` | — | — | — | ✓ | ✓ | — | — |
| `winter_1` | — | — | — | — | — | — | ✓ |
| `winter_10` | — | — | — | — | — | — | ✓ |
| `winter_11` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_12` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_13` | — | — | — | — | — | — | ✓ |
| `winter_14` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_15` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_16` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_17` | — | — | — | — | — | — | ✓ |
| `winter_18` | — | — | — | — | — | — | ✓ |
| `winter_19` | — | — | — | — | — | — | ✓ |
| `winter_2` | — | — | — | — | — | — | ✓ |
| `winter_20` | — | — | — | — | — | — | ✓ |
| `winter_21` | — | — | — | — | — | — | ✓ |
| `winter_22` | — | — | — | — | — | — | ✓ |
| `winter_23` | — | — | — | — | — | — | ✓ |
| `winter_24` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_25` | — | — | — | — | — | — | ✓ |
| `winter_26` | — | — | — | — | — | — | ✓ |
| `winter_27` | — | — | — | — | — | — | ✓ |
| `winter_28` | — | — | — | — | — | — | ✓ |
| `winter_3` | — | — | — | — | — | — | ✓ |
| `winter_30` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_4` | — | — | — | — | — | — | ✓ |
| `winter_5` | — | — | — | — | — | — | ✓ |
| `winter_6` | — | — | — | — | — | — | ✓ |
| `winter_7` | ✓ | — | ✓ | ✓ | — | ✓ | ✓ |
| `winter_8` | ✓ | — | — | — | ✓ | ✓ | ✓ |
| `winter_9` | — | — | — | — | — | — | ✓ |
| `winter_Fri` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Mon` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Sat` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Sun` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Thu` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Tue` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| `winter_Wed` | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

## 6. Медицинские topic и связанные ключи

Всего ключей в группе: **47**.

- Только Base (без стадий): **8**
- С 2+ стадиями: **39**

### Префиксы

- **topicHarvey_**: 23
- **topicHarveyTrust_**: 11
- **topicHarveyStorm_**: 4
- **topicHarveyBadDay_**: 3
- **прочие topicHarvey***: 22

<details><summary>Матрица topicHarvey_* (только Base)</summary>

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `Treat_Hurt_After` | ✓ | — | — | — | — | — | — |
| `Treat_Hurt_Before` | ✓ | — | — | — | — | — | — |
| `topicHarvey_EscalatedCare_memory_oneday` | ✓ | — | — | — | — | — | — |
| `topicHarvey_EscalatedCare_memory_oneweek` | ✓ | — | — | — | — | — | — |
| `topicHarvey_NightRound_memory_oneday` | ✓ | — | — | — | — | — | — |
| `topicHarvey_NightRound_memory_oneweek` | ✓ | — | — | — | — | — | — |
| `topicHarvey_WetStitches_memory_oneday` | ✓ | — | — | — | — | — | — |
| `topicHarvey_WetStitches_memory_oneweek` | ✓ | — | — | — | — | — | — |

</details>

<details><summary>Матрица topic с разделением по стадиям</summary>

| Ключ | Base | 0–2 ❤ | 3–5 ❤ | 6–7 ❤ | 8–10 ❤ | Dating | Married |
|------|---|---|---|---|---|---|---|
| `topicHarveyBadDay_NoQuestions` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyBadDay_Silent` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyBadDay_Water` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyMines_CallMe` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyMines_Note` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyMines_ReturnTime` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyMines_Supplies` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyStorm_Clinic` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyStorm_Escort` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyStorm_Home` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyStorm_Note` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_Breakfast` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_BreathHard` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_DoctorDecides` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_FullExam` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyTrust_JustSit` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyTrust_LeftClinic` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyTrust_NeedsSpace` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_Rest` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_SmallExam` | ✓ | — | — | — | — | ✓ | — |
| `topicHarveyTrust_TouchOk` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarveyTrust_Water` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_AllergicRash` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_AllergicRash_memory_oneday` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_AllergicRash_memory_oneweek` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_DirtyWound` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_DirtyWound_memory_oneday` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_DirtyWound_memory_oneweek` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_ForcedHospitalization` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `topicHarvey_ForcedHospitalization_memory_oneday` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_ForcedHospitalization_memory_oneweek` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_Neglect` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_Neglect_memory_oneday` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_Neglect_memory_oneweek` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_PainFlare` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_WetBandage` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_WetBandage_memory_oneday` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_WetBandage_memory_oneweek` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| `topicHarvey_WetStitches` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |

</details>

---

## 7. Пробелы и риски (сводные списки)

### 1. Есть Base, нет Dating

**Всего:** 33

- DumpsterDiveComment
- Farm_Entry
- HitBySlingshot
- Hospital_Entry
- Introduction
- Treat_Hurt_After
- Treat_Hurt_Before
- WipedMemory
- breakUp
- eventHarveyMedicalCheck_memory_oneday
- eventSeen_528013_fourweeks
- eventSeen_528013_oneweek
- eventSeen_528013_twoweek
- eventSeen_56
- eventSeen_56_memory_fourweeks
- eventSeen_56_memory_twoweeks
- eventSeen_58_memory_fourweeks
- eventSeen_58_memory_oneweek
- eventSeen_58_memory_twoweeks
- eventSeen_eventHarveyFirstMeeting_fourweeks
- eventSeen_eventHarveyFirstMeeting_oneday
- eventSeen_eventHarveyFirstMeeting_oneweek
- eventSeen_eventHarveyFirstMeeting_twoweek
- event_grave1
- event_grave2
- event_heart1
- event_heart2
- topicHarvey_EscalatedCare_memory_oneday
- topicHarvey_EscalatedCare_memory_oneweek
- topicHarvey_NightRound_memory_oneday
- topicHarvey_NightRound_memory_oneweek
- topicHarvey_WetStitches_memory_oneday
- topicHarvey_WetStitches_memory_oneweek

### 2. Есть Base, нет Married

**Всего:** 56

- Beach2
- DumpsterDiveComment
- Farm_Entry
- GreenRain
- GreenRain_2
- HitBySlingshot
- Hospital_Entry
- Introduction
- Treat_Hurt_After
- Treat_Hurt_Before
- WipedMemory
- breakUp
- eventHarveyMedicalCheck_memory_oneday
- eventSeen_528013_fourweeks
- eventSeen_528013_oneweek
- eventSeen_528013_twoweek
- eventSeen_56
- eventSeen_56_memory_fourweeks
- eventSeen_56_memory_twoweeks
- eventSeen_58_memory_fourweeks
- eventSeen_58_memory_oneweek
- eventSeen_58_memory_twoweeks
- eventSeen_eventHarveyFirstMeeting_fourweeks
- eventSeen_eventHarveyFirstMeeting_oneday
- eventSeen_eventHarveyFirstMeeting_oneweek
- eventSeen_eventHarveyFirstMeeting_twoweek
- event_grave1
- event_grave2
- event_heart1
- event_heart2
- situationReaction_Drunk
- topicHarveyApologyAccepted
- topicHarveyBadDay_NoQuestions
- topicHarveyBadDay_Silent
- topicHarveyBadDay_Water
- topicHarveyMines_CallMe
- topicHarveyMines_Note
- topicHarveyMines_ReturnTime
- topicHarveyMines_Supplies
- topicHarveyNeedsSpace
- topicHarveyQuietFiveMinutes
- topicHarveySafetyKit_Bed
- topicHarveySafetyKit_Door
- topicHarveySafetyKit_Kitchen
- topicHarveySafetyKit_NoKit
- topicHarveyTrust_FullExam
- topicHarveyTrust_JustSit
- topicHarveyTrust_LeftClinic
- topicHarveyTrust_SmallExam
- topicHarveyWasCaredFor
- topicHarvey_EscalatedCare_memory_oneday
- topicHarvey_EscalatedCare_memory_oneweek
- topicHarvey_NightRound_memory_oneday
- topicHarvey_NightRound_memory_oneweek
- topicHarvey_WetStitches_memory_oneday
- topicHarvey_WetStitches_memory_oneweek

### 3. Есть 3–7 ❤, нет 8–10 и Dating

**Всего:** 26

- ArchaeologyHouse4
- ArchaeologyHouse6
- Beach4
- Beach6
- Desert4
- Desert6
- Fri4
- Fri6
- HarveyRoom4
- HarveyRoom6
- Hospital4
- Hospital6
- Mon4
- Mon6
- Saloon4
- Saloon6
- Sat4
- Sat6
- Sun4
- Sun6
- Thu4
- Thu6
- Tue4
- Tue6
- Wed4
- Wed6

### 4. Topic-ключи только в Base (без стадий)

**Всего:** 6

- topicHarvey_EscalatedCare_memory_oneday
- topicHarvey_EscalatedCare_memory_oneweek
- topicHarvey_NightRound_memory_oneday
- topicHarvey_NightRound_memory_oneweek
- topicHarvey_WetStitches_memory_oneday
- topicHarvey_WetStitches_memory_oneweek

### 5. Есть Dating, нет Married

**Всего:** 32

- Beach2
- GreenRain
- GreenRain_2
- Hospital10
- Hospital8
- Saloon10
- Saloon8
- situationReaction_Drunk
- topicHarveyApologyAccepted
- topicHarveyBadDay_NoQuestions
- topicHarveyBadDay_Silent
- topicHarveyBadDay_Water
- topicHarveyDate_Hug
- topicHarveyDate_Kiss
- topicHarveyDate_NotYet
- topicHarveyDate_SitLonger
- topicHarveyMines_CallMe
- topicHarveyMines_Note
- topicHarveyMines_ReturnTime
- topicHarveyMines_Supplies
- topicHarveyNeedsSpace
- topicHarveyNotOnlyPatient
- topicHarveyQuietFiveMinutes
- topicHarveySafetyKit_Bed
- topicHarveySafetyKit_Door
- topicHarveySafetyKit_Kitchen
- topicHarveySafetyKit_NoKit
- topicHarveyTrust_FullExam
- topicHarveyTrust_JustSit
- topicHarveyTrust_LeftClinic
- topicHarveyTrust_SmallExam
- topicHarveyWasCaredFor

### 6. Есть Married, нет Dating

**Всего:** 166

- Bad_0
- Beach_10_15
- Beach_5_12
- Farm10
- Farm2
- Farm6
- Farm_25_38
- Farm_30_40
- Forest_12_22
- Forest_8_18
- Good_0
- Good_1
- Good_2
- Good_3
- Good_5
- Good_6
- Hospital_18_12
- Hospital_20_15
- Indoor_Day_0
- Indoor_Day_1
- Indoor_Day_2
- Indoor_Day_3
- Indoor_Day_4
- Indoor_Night_0
- Indoor_Night_1
- Indoor_Night_2
- Indoor_Night_3
- Indoor_Night_4
- Island_Resort
- Island_Resort_10_15
- Island_Resort_Fri
- Lake_10_25
- Lake_7_22
- Mine_10_10
- Mine_5_5
- Mountain_10_20
- Mountain_15_25
- Neutral_2
- OneKid_0
- OneKid_1
- OneKid_3
- Outdoor2
- Outdoor_0
- Outdoor_1
- Outdoor_2
- Outdoor_3
- Outdoor_4
- Rainy_Day_0
- Rainy_Day_1
- Rainy_Day_2
- Rainy_Day_3
- Rainy_Day_4
- Rainy_Night_0
- Rainy_Night_1
- Rainy_Night_2
- Rainy_Night_3
- Rainy_Night_4
- Saloon_Fri
- Store_12_8
- Store_15_10
- Town10
- Town4
- Town8
- Town_15_30
- Town_20_35
- TwoKids_0
- TwoKids_1
- TwoKids_2
- TwoKids_3
- fall_1
- fall_10
- fall_11
- fall_12
- fall_13
- fall_14
- fall_17
- fall_18
- fall_19
- fall_2
- fall_20
- fall_21
- fall_22
- fall_23
- fall_24
- fall_25
- fall_27
- fall_28
- fall_3
- fall_4
- fall_5
- fall_6
- fall_7
- fall_8
- fall_9
- funLeave
- funLeave_Harvey
- funReturn
- funReturn_Harvey
- jobLeave
- jobReturn
- patio_Harvey
- spouseRoom
- spring_1
- spring_10
- spring_11
- spring_17
- spring_18
- spring_19
- spring_2
- spring_20
- spring_21
- spring_22
- spring_24
- spring_25
- spring_26
- spring_27
- spring_28
- spring_3
- spring_4
- spring_5
- *… и ещё 46*

### 7. Пересекающиеся When (неясный победитель)

При `Priority: Late` побеждает **последний** патч в порядке manifest. Ниже — ключи с 2+ патчами и пересекающимися условиями; ⚠️ — более специфичный патч идёт **раньше** общего.

**Ключей с пересечением:** 281

- `AcceptBirthdayGift_Hated` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBirthdayGift_Liked` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBirthdayGift_Loved` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBirthdayGift_Negative` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBirthdayGift_Neutral` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBirthdayGift_Positive` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptBouquet` — 6 патчей, побеждает #44 harvey_gifts.json: #1 harvey_base.json ((нет When)); #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)18` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)192` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)196` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)2` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)20` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)200` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)201` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)22` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)237` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)24` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)257` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)279` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)281` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)296` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)30` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)303` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)342` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)346` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)348` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)349` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)373` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)395` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)396` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)404` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)422` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)432` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)436` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)438` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)442` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)444` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)446` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)610` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)614` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)618` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)651` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)72` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)74` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)773` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)78` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)797` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)80` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)88` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)90` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `AcceptGift_(O)StardropTea` — 5 патчей, побеждает #44 harvey_gifts.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating)
- `ArchaeologyHouse` — 5 патчей, побеждает #35 harvey_hospital.json: #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2); #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10); #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating); #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `ArchaeologyHouse10` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `ArchaeologyHouse8` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Beach` — 11 патчей, побеждает #35 harvey_hospital.json: #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2); #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10); #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating); #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married); #21 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=0,1,2); #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10); #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating); #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married); #28 harvey_locations.json ((нет When)); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach10` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Beach2` — 4 патчей, побеждает #51 harvey_priority2.json: #28 harvey_locations.json ((нет When)); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #51 harvey_priority2.json (Relationship:Harvey=Dating)
- `Beach4` — 2 патчей, побеждает #29 harvey_locations.json: #4 harvey_hearts_3_5.json (Hearts:Harvey=4,5,6,7); #29 harvey_locations.json (Hearts:Harvey=4,5,6,7)
- `Beach8` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Desert` — 5 патчей, побеждает #54 harvey_priority2.json: #28 harvey_locations.json ((нет When)); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #51 harvey_priority2.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Desert10` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Desert2` — 5 патчей, побеждает #54 harvey_priority2.json: #28 harvey_locations.json ((нет When)); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #51 harvey_priority2.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Desert4` — 2 патчей, побеждает #29 harvey_locations.json: #4 harvey_hearts_3_5.json (Hearts:Harvey=4,5,6,7); #29 harvey_locations.json (Hearts:Harvey=4,5,6,7)
- `Desert8` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `FlowerDance_Accept` — 8 патчей, побеждает #45 harvey_dating.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #29 harvey_locations.json (Hearts:Harvey=4,5,6,7); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating); #45 harvey_dating.json (Relationship:Harvey=Dating)
- `FlowerDance_Decline` — 7 патчей, побеждает #46 harvey_married.json: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2); #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5); #28 harvey_locations.json ((нет When)); #42 harvey_gifts.json (Hearts:Harvey=6,7,8,9,10); #43 harvey_gifts.json (Relationship:Harvey=Married); #44 harvey_gifts.json (Relationship:Harvey=Dating); #46 harvey_married.json (Relationship:Harvey=Married)
- `Fri` — 3 патчей, побеждает #52 harvey_priority2.json: #1 harvey_base.json ((нет When)); #50 harvey_priority2.json (Relationship:Harvey=Dating); #52 harvey_priority2.json (Relationship:Harvey=Married)
- `Fri10` — 3 патчей, побеждает #53 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #53 harvey_priority2.json (Relationship:Harvey=Married)
- `Fri2` — 3 патчей, побеждает #52 harvey_priority2.json: #1 harvey_base.json ((нет When)); #50 harvey_priority2.json (Relationship:Harvey=Dating); #52 harvey_priority2.json (Relationship:Harvey=Married)
- `Fri8` — 3 патчей, побеждает #53 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #53 harvey_priority2.json (Relationship:Harvey=Married)
- `GreenRain` — 4 патчей, побеждает #45 harvey_dating.json: #28 harvey_locations.json ((нет When)); #29 harvey_locations.json (Hearts:Harvey=4,5,6,7); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating)
- `GreenRain_2` — 4 патчей, побеждает #45 harvey_dating.json: #28 harvey_locations.json ((нет When)); #29 harvey_locations.json (Hearts:Harvey=4,5,6,7); #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating)
- `HarveyRoom` — 3 патчей, побеждает #54 harvey_priority2.json: #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #51 harvey_priority2.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `HarveyRoom10` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `HarveyRoom2` — 3 патчей, побеждает #54 harvey_priority2.json: #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #51 harvey_priority2.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `HarveyRoom8` — 3 патчей, побеждает #54 harvey_priority2.json: #30 harvey_locations.json (Hearts:Harvey=8,9,10); #45 harvey_dating.json (Relationship:Harvey=Dating); #54 harvey_priority2.json (Relationship:Harvey=Married)
- `Hospital10` — 2 патчей, побеждает #38 harvey_hospital.json: #37 harvey_hospital.json (Hearts:Harvey=8,9,10); #38 harvey_hospital.json (Relationship:Harvey=Dating)
- `Hospital8` — 2 патчей, побеждает #38 harvey_hospital.json: #37 harvey_hospital.json (Hearts:Harvey=8,9,10); #38 harvey_hospital.json (Relationship:Harvey=Dating)
- `Hospital_Fri` — 20 патчей, побеждает #48 harvey_married.json: #9 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=0,1,2); #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10); #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating); #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married); #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2); #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10); #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating); #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married); #21 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=0,1,2); #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10); #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating); #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #36 harvey_hospital.json (Hearts:Harvey=4,5,6,7); #37 harvey_hospital.json (Hearts:Harvey=8,9,10); #38 harvey_hospital.json (Relationship:Harvey=Dating); #39 harvey_hospital.json (Hearts:Harvey=0,1,2); #40 harvey_hospital.json (Hearts:Harvey=3,4,5); #41 harvey_hospital.json (Hearts:Harvey=6,7); #48 harvey_married.json (Relationship:Harvey=Married)
- `Hospital_Mon` — 21 патчей, побеждает #48 harvey_married.json: #9 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=0,1,2); #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10); #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating); #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married); #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2); #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10); #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating); #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married); #21 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=0,1,2); #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10); #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating); #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married); #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10); #36 harvey_hospital.json (Hearts:Harvey=4,5,6,7); #37 harvey_hospital.json (Hearts:Harvey=8,9,10); #38 harvey_hospital.json (Relationship:Harvey=Dating); #39 harvey_hospital.json (Hearts:Harvey=0,1,2); #40 harvey_hospital.json (Hearts:Harvey=3,4,5); #41 harvey_hospital.json (Hearts:Harvey=6,7); #46 harvey_married.json (Relationship:Harvey=Married); #48 harvey_married.json (Relationship:Harvey=Married)
- *… и ещё 201*

**⚠️ Риск порядка (специфичный раньше общего):**

- `ArchaeologyHouse`: #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `ArchaeologyHouse`: #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `ArchaeologyHouse`: #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #14 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #15 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Dating) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #16 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Relationship:Harvey=Married) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #21 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=0,1,2) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #22 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #23 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Dating) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Beach`: #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married) перебивается #28 harvey_locations.json ((нет When))
- `Beach`: #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married) перебивается #30 harvey_locations.json (Hearts:Harvey=8,9,10)
- `Beach`: #24 harvey_topics_medical.json (HasConversationTopic=topicHarveyExhaustion, Relationship:Harvey=Married) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `FlowerDance_Decline`: #3 harvey_hearts_0_2.json (Hearts:Harvey=0,1,2) перебивается #28 harvey_locations.json ((нет When))
- `FlowerDance_Decline`: #5 harvey_hearts_3_5.json (Hearts:Harvey=3,4,5) перебивается #28 harvey_locations.json ((нет When))
- `Hospital_Fri`: #9 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=0,1,2) перебивается #38 harvey_hospital.json (Relationship:Harvey=Dating)
- `Hospital_Fri`: #9 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=0,1,2) перебивается #39 harvey_hospital.json (Hearts:Harvey=0,1,2)
- `Hospital_Fri`: #9 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=0,1,2) перебивается #48 harvey_married.json (Relationship:Harvey=Married)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #36 harvey_hospital.json (Hearts:Harvey=4,5,6,7)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #37 harvey_hospital.json (Hearts:Harvey=8,9,10)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #38 harvey_hospital.json (Relationship:Harvey=Dating)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #40 harvey_hospital.json (Hearts:Harvey=3,4,5)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #41 harvey_hospital.json (Hearts:Harvey=6,7)
- `Hospital_Fri`: #10 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Hearts:Harvey=3,4,5,6,7,8,9,10) перебивается #48 harvey_married.json (Relationship:Harvey=Married)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #36 harvey_hospital.json (Hearts:Harvey=4,5,6,7)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #37 harvey_hospital.json (Hearts:Harvey=8,9,10)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #38 harvey_hospital.json (Relationship:Harvey=Dating)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #39 harvey_hospital.json (Hearts:Harvey=0,1,2)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #40 harvey_hospital.json (Hearts:Harvey=3,4,5)
- `Hospital_Fri`: #11 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Dating) перебивается #41 harvey_hospital.json (Hearts:Harvey=6,7)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #35 harvey_hospital.json (Hearts:Harvey=6,7,8,9,10)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #36 harvey_hospital.json (Hearts:Harvey=4,5,6,7)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #37 harvey_hospital.json (Hearts:Harvey=8,9,10)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #39 harvey_hospital.json (Hearts:Harvey=0,1,2)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #40 harvey_hospital.json (Hearts:Harvey=3,4,5)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #41 harvey_hospital.json (Hearts:Harvey=6,7)
- `Hospital_Fri`: #12 harvey_topics_medical.json (HasConversationTopic=topicHarveyTraumaReveal, Relationship:Harvey=Married) перебивается #48 harvey_married.json (Relationship:Harvey=Married)
- `Hospital_Fri`: #13 harvey_topics_medical.json (HasConversationTopic=topicFirstMeeting, Hearts:Harvey=0,1,2) перебивается #38 harvey_hospital.json (Relationship:Harvey=Dating)
- *… и ещё 299*

## 8. Приоритет дописывания (рекомендация)

Порядок — по влиянию на «не тот тон» при смене отношений:

1. **topicHarvey_EscalatedCare_memory_oneday** — topic только в Base — без стадий отношений
2. **topicHarvey_EscalatedCare_memory_oneweek** — topic только в Base — без стадий отношений
3. **topicHarvey_NightRound_memory_oneday** — topic только в Base — без стадий отношений
4. **topicHarvey_NightRound_memory_oneweek** — topic только в Base — без стадий отношений
5. **topicHarvey_WetStitches_memory_oneday** — topic только в Base — без стадий отношений
6. **topicHarvey_WetStitches_memory_oneweek** — topic только в Base — без стадий отношений
7. **Hospital_Entry** — есть Base, нет Dating — при романе уйдёт в базу
8. **situationReaction_Drunk** — есть Base, нет Married
9. **Fri4** — есть 3–7 ❤, нет 8–10 и Dating
10. **Fri6** — есть 3–7 ❤, нет 8–10 и Dating
11. **Hospital4** — есть 3–7 ❤, нет 8–10 и Dating
12. **Hospital6** — есть 3–7 ❤, нет 8–10 и Dating
13. **Mon4** — есть 3–7 ❤, нет 8–10 и Dating
14. **Mon6** — есть 3–7 ❤, нет 8–10 и Dating
15. **Sat4** — есть 3–7 ❤, нет 8–10 и Dating
16. **Sat6** — есть 3–7 ❤, нет 8–10 и Dating
17. **Sun4** — есть 3–7 ❤, нет 8–10 и Dating
18. **Sun6** — есть 3–7 ❤, нет 8–10 и Dating
19. **Thu4** — есть 3–7 ❤, нет 8–10 и Dating
20. **Thu6** — есть 3–7 ❤, нет 8–10 и Dating
21. **Tue4** — есть 3–7 ❤, нет 8–10 и Dating
22. **Tue6** — есть 3–7 ❤, нет 8–10 и Dating
23. **Wed4** — есть 3–7 ❤, нет 8–10 и Dating
24. **Wed6** — есть 3–7 ❤, нет 8–10 и Dating

### Групповые приоритеты

| Группа | Рекомендация |
|--------|----------------|
| Повседневные Mon–Sun10 | Для каждого суффикса закрыть Dating и Married, если сейчас только Base + heart-блоки |
| Hospital_* | `Hospital_Mon`–`Sun` и `Hospital8`/`10` — проверить Dating; married частично в `harvey_married` |
| time/situation/emotional | Все 8 ключей дублируются в base + hearts_4_7 + 8_10 + dating; убедиться, что married-варианты осмысленны |
| Локации Desert/Beach/Resort | Base перебивает topic-overlays при неверном порядке — дописать/переставить не нужно в этом шаге; дописать Married для Resort* |
| topicHarvey_* только Base | **8** ключей — главный долг: разнести по 0–2 / 3–10 / Dating / Married |
| Treat_* / Injury (в `dialoguesHarveyCure` / `Injury`) | Вне этого manifest; стадии Stranger/Dating/Married — отдельный проход |

---

## 9. Приоритет 2 — закрыто (2026-06-04)

Файл: `assets/Code/dialogues/harvey_priority2.json` (после `harvey_married` в manifest).

| Группа | Добавлено |
|--------|-----------|
| Повседневные `Mon`–`Sun`, `Mon2`–`Sun2` | Dating (14) — base с «Вы»; Married (14) — клиника/NPC |
| `Mon8`–`Sun8`, `Mon10`–`Sun10` | Married (14) |
| Локации | Dating: `Desert`, `Desert2`, `Beach2`, `HarveyRoom`, `HarveyRoom2`; Married: +8/10, Archaeology*, Resort |
| Сезонные `spring_Mon`…`winter_Sun` | Married (28) |
| Фестивали | Married: `summer_9`, `winter_30` (NPC) |

## 10. Приоритет 2 — намеренно НЕ закрыто

| Ключи / зона | Почему оставлено |
|--------------|------------------|
| `spring_1`…`spring_28` (кроме фестивальных дат) | Уже в `harvey_married` FarmHouse — отдельный контекст дома, дубли NPC не нужны |
| `Mon4`–`Sun6` без Dating/Married | При 4–7 ❤ блок с «ты» достаточен; при Dating игра берёт `Mon8`/`Mon10` |
| `Beach`, `ArchaeologyHouse` (базовые) | Topic-overlay + 6–10 ❤; отдельный Dating не нужен |
| `Resort_*` кроме `Resort` | Уже есть Dating/Married на под-ключах |
| `spring_12`, `summer_10`, … (фестивали) | Уже Dating + частично Married в FarmHouse; base формальный, но перекрывается |
| `spring_13` без 3–5 ❤ | Отдельная 8–10/Dating линия; 3–5 не срабатывает на этом ключе в игре |
| `0–2 ❤` для сезонных/локаций | Низкий hearts редко видит эти ключи; base «Вы» приемлем |
| `Saloon*`, `GreenRain`, фестивальные вторые дни | Dating уже в `harvey_dating`; Married — в FarmHouse или низкий приоритет тона |
| `Hospital8`/`10`, `situationReaction_Drunk` Married | Следующий проход (не P2) |
