# Финальный аудит диалогов Харви

**Дата:** 2026-06-04  
**Область:** split-файлы `assets/Code/dialogues/harvey_*.json`, порядок загрузки — `assets/Code/dialoguesHarvey.json` (manifest, `Priority: Late` в `content.json`).  
**Вне scope:** `dialoguesHarveyInjury.json`, `dialoguesHarveyCure*.json`, `dialoguesHarveyMedicalCare.json` и др. (отдельные медицинские ветки).  
**Режим:** только отчёт; правки в JSON **не вносились**.

Автоматика: `scripts/final_audit_dialogues_harvey.py` + ручная выборочная проверка.

---

## Итог по критериям

| # | Критерий | Вердикт | Комментарий |
|---|----------|---------|-------------|
| 1 | Dating/Married без «Вы/Вас/…» | **PASS** | 0 вхождений в патчах `Relationship:Harvey = Dating` или `Married` и в `MarriageDialogueHarvey` |
| 2 | 0–2 ❤ без ты/ласковых | **PASS** | `harvey_hearts_0_2.json` — только «Вы»; ласковых нет |
| 3–4 | Дубли ключей / порядок When | **WARN** | 232 ключа в 2+ патчах; topics грузятся **раньше** hospital/dating — см. §3 |
| 5 | Topics не ломают dating/married | **PASS** | Нет «Вы» в topic-патчах при Dating/Married; topic+0–2 без «ты» |
| 6 | Лестница реакций | **PASS*** | Победитель по load order корректен для типичных стадий; см. §6 и оговорку про gifts |
| 7 | Гиперопека мягче | **PARTIAL** | Соотношение мягких/жёстких маркеров ~19:1; остатки жёсткого тона + дубль storm §7 |

---

## 1. «Вы» в Dating и Married

**Результат: PASS.**

Поиск `\b(Вы|Вас|Вам|Ваш|Ваше|Ваши)\b` по `harvey_dating.json`, `harvey_married.json`, `harvey_gifts.json` (блоки Dating/Married), `MarriageDialogueHarvey` — **0 совпадений**.

Формальное обращение сохранено там, где задумано:

- `harvey_base.json`, `harvey_locations.json` (базовый слой без `When` или 4–7 ❤),
- `harvey_hearts_0_2.json` / `harvey_hearts_3_5.json` (подарки и отказы),
- topic-патчи на 0–2 ❤ и нейтральные медицинские topics (`harvey_topics_medical.json`).

Смешения «Вы» + «ты» в **одной** строке: **0**.

---

## 2. Неформальное обращение в 0–2 ❤

**Результат: PASS** для патчей `Hearts:Harvey = 0,1,2`.

| Файл | Проверка |
|------|----------|
| `harvey_hearts_0_2.json` | 69 ключей (gifts + reject/flower dance) — только «Вы», без ты/солнышко/малышка/котёнок |
| Topic-overlay `Hearts=0,1,2` | `Hospital_*`, `Beach`, exhaustion, firstMeeting — формальный тон («Вы», «запишитесь») |

**Замечание (не FAIL по формулировке запроса):** базовый слой `harvey_locations.json` без `When` (`Mon`–`Sun`, `timeReaction_*`) использует «Вы» и действует на все стадии, пока не перебит более поздним патчем. На 0–2 ❤ игрок видит формальный тон — это ожидаемо.

---

## 3–4. Дубли ключей и порядок `When`

### Масштаб

| Метрика | Значение |
|---------|----------|
| Патчей EditData (3 target) | 41 |
| Слотов Entries (с дублями между патчами) | 1231 |
| Уникальных ключей | 513 |
| Ключей в 2+ патчах | 232 |

### Порядок manifest (кто побеждает при совпадении `When`)

1. schedule → base → hearts_0_2 → hearts_3_5 → hearts_6_7 → **topics_medical** → locations → hospital → gifts → **dating** → **married**

При `Priority: Late` побеждает **последний** подходящий патч.

### Намеренные пересечения (OK)

| Группа | Файлы-участники | Ожидание |
|--------|-----------------|----------|
| `AcceptGift_*` / `AcceptBirthdayGift_*` | hearts_0_2 → 3_5 → gifts (6–10, Married, **Dating последний**) | При свиданиях побеждает dating-блок в `harvey_gifts.json` (#37) |
| `timeReaction_*`, `locationReaction_*`, … | locations (база, 4–7, 8–10) → **dating** | В романе — `harvey_dating.json` |
| `Resort_*` (Dialogue/Harvey) | locations → dating; **MarriageDialogueHarvey** — отдельный target | Домашний курорт ≠ разговор с NPC на курорте |
| `Hospital_*` | topics (по topic+стадия) → hospital (4–7, 8–10, dating) → married (только при Married) | См. §3.1 |

### 3.1 Архитектурный WARN: topics **до** hospital/locations

В split manifest `harvey_topics_medical.json` идёт **раньше** `harvey_hospital.json` и `harvey_locations.json`.

**Следствие:** при одновременно активном topic и подходящих сердцах/локации **перебивает** topic-реплику более поздний «клинический» или «сердечный» патч, а не наоборот (в старом монолите topic-блоки шли позже heart-блоков — см. `dialogues_harvey_split_notes.md`).

Пример: `Hospital_Mon` при `topicHarveyExhaustion` + Dating — в игре может сыграть `harvey_hospital.json` (dating, «Солнышко, ты бледная…»), а не exhaustion-topic из `harvey_topics_medical.json`.

**Рекомендация на будущий PR (не делалось):** перенести `harvey_topics_medical.json` после `harvey_hospital.json` **или** поднять `Priority` у topic-патчей.

### 3.2 Дубли `When` в одном JSON-объекте

В split-файлах **не обнаружено** второго `"When"` в одном патче (баг монолита #5 исправлен при разбиении).

---

## 5. Topic-блоки vs dating/married

**Результат: PASS.**

- Topic-патчи с `Relationship:Harvey = Dating` / `Married` — на «ты», без «Вы».
- Topic + `Hearts=0,1,2` — формальный тон, без «ты»/ласковых (кроме ключей, где ласковое не используется).
- Dating-only topics (`topicHarveyDate_*`, `topicHarveyMines_CallMe` с «солнышко») — только в dating-блоках topics; к 0–2 ❤ не применяются.

---

## 6. Лестница отношений (реакции / больница / подарки / курорт)

Ожидаемая градация: **base (Вы)** → **0–2 / 3–5 gifts** → **4–7 / 8–10 locations** → **dating (ты, мягкая опека)** → **married (ты, домашняя близость)**.

### Фактический победитель (последний патч в manifest) по сценариям

| Ключ | Target | Сценарий | Побеждает |
|------|--------|----------|-----------|
| `timeReaction_Late` | Dialogue/Harvey | Dating | `harvey_dating.json` |
| `timeReaction_Late` | Dialogue/Harvey | 8–10 ❤, не в романе | `harvey_locations.json` (8–10) |
| `locationReaction_SkullCave` | Dialogue/Harvey | Dating | `harvey_dating.json` («Солнышко», «не отступлю» — опека) |
| `Hospital_Mon` | Dialogue/Harvey | Dating | `harvey_hospital.json` (dating-блок) |
| `Hospital_Mon` | Dialogue/Harvey | Married | `harvey_married.json` (Dialogue/Harvey, married) |
| `Resort_Shore` | Dialogue/Harvey | Dating | `harvey_dating.json` |
| `Resort_Shore` | MarriageDialogueHarvey | Married, дом | `harvey_married.json` (MarriageDialogue) |
| `AcceptGift_(O)StardropTea` | Dialogue/Harvey | Dating | `harvey_gifts.json` (Dating) |
| `AcceptGift_(O)StardropTea` | Dialogue/Harvey | 0–2 ❤ | `harvey_hearts_0_2.json` |

**Оговорка по подаркам:** в `harvey_gifts.json` порядок патчей: Married (#36) → Dating (#37). При одновременном применении обоих `When` (невозможно в ванильной игре) победил бы Dating — для игры неактуально.

**Оговорка по `Hospital_*`:** в `harvey_hospital.json` остаётся блок strict 6–10 с «Вы» (`Hospital_Sun`: «Вы не одна») — срабатывает только при 6–10 ❤ без более специфичного dating/married/topic-победителя.

---

## 7. Гиперопека: жёсткие vs мягкие формулировки

Эвристика по всем split-файлам (не полный семантический разбор).

### Счётчики

| Жёсткий маркер | Вхождений | Где |
|----------------|-----------|-----|
| «не спорь» / «не спорим» | 1 | `harvey_gifts.json` — `RejectRoommateProposal_SmallHouse` (Married): «не спорим» |
| «не отпущу» | 1 | `harvey_dating.json` — `Beach10` |
| «я всё решу» | 0 | — |
| «я не дам» | 4 | schedule `marriage_Mon.000`; `Wed4` (4–7 ❤); `Fri6`; storm `Rainy_Day_3` (Dialogue/Harvey) |
| «без возражений» | 0 | — |
| «под моим контролем» | 1 | `harvey_married.json` — `Rainy_Day_2` (**Dialogue/Harvey**, Storm) |
| «не пугайтесь» | 0 | — |

| Мягкий маркер | Вхождений |
|---------------|-----------|
| «давай договоримся» | 19 |
| «я напомню» | 7 |
| «мне спокойнее» | 24 |
| «если захочешь» / «если попросишь» | 62 |
| «без давления» / «без ложки» / «без нотаций» | 21 |

**Итого:** ~7 жёстких vs ~133 мягких вхождений → сдвиг к договорённости и согласию **подтверждён** относительно `dialogues_harvey_audit.md`.

### 7.1 WARN: два слоя storm-диалога (married)

В `harvey_married.json` coexist:

| Target | `When` | Тон `Rainy_Day_*` |
|--------|--------|-------------------|
| `MarriageDialogueHarvey` | Married | **Смягчённый** (2026): «давай договоримся», «помолчим», «я никуда не ухожу, пока не скажешь» |
| `Characters/Dialogue/Harvey` | Married + `Weather: Storm` | **Старый жёсткий** слой: «полностью в безопасности», «под моим контролем», «я прослежу», «котёнок» |

Игрок получает разный тон в зависимости от контекста (домашняя реплика супруга vs разговор с NPC в грозу). Для критерия 7 это **главный остаточный долг**.

### 7.2 Прочие наблюдения

- **Dating** в целом переписан мягко (`давай договоримся`, `мне спокойнее`, `без ложки в рот` в Saloon10); исключение — `Beach10` («не отпущу далеко»).
- **Marriage schedule** (`marriage_Mon.000`): «я не дам тебе голодать, девочка моя» — ласковая гиперопека, не формальное «Вы»; по тону ближе к старому marriage, не к новому MarriageDialogue.
- **6–7 ❤** (`Wed4`, `Fri6`): «я не дам тебе заболеть/игнорировать» — умеренно настойчиво, но без «не спорь».

---

## Дополнительно

### Сверка объёма после split

`scripts/count_dialogue_entries.py` на текущем manifest: manifest больше не содержит inline `EditData` (только `Include`) — учёт ведётся по сумме split-файлов (**1114** уникальных слотов в прошлой заметке; сейчас 1231 слот с учётом дублирующих патчей между файлами).

### Файлы и ключи

| Файл | Патчей | Ключей (в патчах) |
|------|--------|-------------------|
| `harvey_schedule_strings.json` | 2 | 7 |
| `harvey_base.json` | 2 | 61 |
| `harvey_hearts_0_2.json` | 1 | 69 |
| `harvey_hearts_3_5.json` | 2 | 81 |
| `harvey_hearts_6_7.json` | 1 | 12 |
| `harvey_topics_medical.json` | 18 | 193 |
| `harvey_locations.json` | 3 | 219 |
| `harvey_hospital.json` | 5 | 52 |
| `harvey_gifts.json` | 3 | 207 |
| `harvey_dating.json` | 1 | 95 |
| `harvey_married.json` | 3 | 235 |

---

## Рекомендации (только для следующего PR, без правок сейчас)

1. **Порядок topics:** переместить `harvey_topics_medical.json` после hospital **или** `Late + 1` для topic-патчей — чтобы exhaustion/trauma не терялись за `Hospital_*`.
2. **Storm Dialogue/Harvey:** переписать блок `Rainy_Day_*` / `Rainy_Night_*` (Married + Storm) в тоне `MarriageDialogueHarvey` или удалить дубль.
3. **Точечно смягчить:** `Beach10` (dating), `marriage_Mon.000` (schedule), при желании — `Wed4`/`Fri6`.
4. **Проверка в игре:** MCP/ручной клик — `Hospital_Mon` при active topic + dating; подарок при Dating после dedupe gifts.

---

*Сгенерировано: `scripts/final_audit_dialogues_harvey.py` + ручная верификация 2026-06-04.*
