# Аудит тона Харви (текущее состояние)

**Дата:** 2026-05-25  
**Эталон:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Область:** `HarveyOverhaul [CP]` — JSON-тексты, триггеры, квесты. C# в репозитории CP **не найден** (логика почты/событий — через `triggersCare.json`, BETAS/SpaceCore).

---

## Краткие выводы

| Категория | Оценка |
|-----------|--------|
| Trust-arc (E1–E12, topicHarveyTrust_*, письма с «Вы») | В целом **соответствует** стадии 0 / trust-gated |
| `dialoguesHarveyInjury.json` (база + 0–1 ❤) | **Соответствует** стадии 0 («Вы») |
| Безусловный блок `dialoguesHarvey.json` (без `When`) | **Критичные расхождения** — «ты» и romance-маркеры с 0 ❤ |
| Блок `Hearts: 8,9,10` без `!Dating` | **Критично** — помечен как «романтика», но срабатывает **до букета** |
| `Relationship: Dating` в cure/injury/quests | **Системно** — pet names уровня Married (`котёнок`, `девочка моя`, `малышка`) |
| Письма `HarveyMod_*` + триггеры времени/ночи | **Расхождение gate и тона** — жёсткий контроль при Friendship 500+ без Dating |
| `speak farmer` | **Не найдено** — речь фермерши в норме |
| Gift reactions (отдельного файла нет) | В `dialoguesHarvey.json`, см. таблицу |

**Главная архитектурная проблема:** несколько слоёв с одинаковыми ключами перекрывают друг друга по `Priority: Late`, но **стадия в тексте не совпадает с `When`** (особенно 8–10 ❤ и Dating).

---

## Сводка по типам нарушений

| Тип | ~кол-во затronутых ключей/групп | Самый частый gate |
|-----|----------------------------------|-------------------|
| «ты» при стадии 0 (< 750 FP) | 40+ | без `When`, schedules, injury phase (ungated), mail triggers FP≥500 |
| Pet names до Dating | 80+ | `Hearts 8–10`, `Dating`, quests, cure/injury Dating |
| «люблю» / «влюблён» до Dating | 8+ | ungated, `Hearts 8–10`, `HarveyMod_LoveConfession` (если отправится) |
| «моя/ты у меня» собственнически | 50+ | `Hearts 6–10`, cure 6–10, Dating |
| «хрупкая» (личностно / интимно) | 60+ | все стадии; на 0–2 особенно |
| Контроль без escape hatch | 30+ | `Hearts 6–10`, events, mail |
| Married-тон не в Married-блоке | 70+ | `Hearts 8–10`, `Dating` |
| «Вы» после перехода на «ты» | 15+ | trust-topics в ungated (частично **корректно** для arc 0) |
| Длинные `speak farmer` | 0 | — |

---

## Таблица находок

| Файл | Ключ / Event ID | Текущий gate | Фактический тон | Проблема | Нужная стадия | Как исправить |
|------|------------------|--------------|-----------------|----------|---------------|---------------|
| `dialoguesHarvey.json` | *(блок Entries без When)* | **Нет** — всегда | «ты», хрупкая, контроль | Стадия 0: запрещён «ты» и личная опека | **0 — «Вы»** | Вынести в `Hearts 0,1,2` + «Вы» или разделить gift/event keys по стадиям |
| `dialoguesHarvey.json` | `Introduction` | Нет | «Вы», клиника | ✅ Соответствует | 0 | Эталон для стадии 0 |
| `dialoguesHarvey.json` | `Farm_Entry`, `Hospital_Entry` | Нет | «ты», осмотр, «хрупкая» | «ты» и личная опека с 0 ❤ | 0 → **Вы**; 1+ → «ты» | Дублировать ключ по `Hearts` / `Friendship` |
| `dialoguesHarvey.json` | `AcceptBirthdayGift_Positive/Negative` | Нет | «ты», «хрупкая», «не позволю» | Стадия 0 | 0 | «Вы» + протокол; «хрупкая» → «организм» / убрать |
| `dialoguesHarvey.json` | `GreenRain`, `GreenRain_2` | Нет | «ты», «не позволю заболеть» | Стадия 0 | 0–1 | Разнести по hearts; на 0 — «Вы» |
| `dialoguesHarvey.json` | `AcceptGift_(O)432`, `(O)348` | Нет | «ты», «хрупкая» | Gift reaction без gate | 0 / 1+ | Отдельные версии или `$c` по hearts (вручную) |
| `dialoguesHarvey.json` | `AcceptGift_(O)395` | Нет | **«солнышко»**, **«люблю»**, «хрупкое» сердце | Romance + pet name без Dating | 3 (Dating) | Перенести в `Relationship: Dating`; до этого — нейтральный AcceptGift |
| `dialoguesHarvey.json` | `FlowerDance_Accept_Spouse` | **Нет** (ungated) | «солнышко», «не отпущу руку» | Spouse-реплика доступна не только супругам | 4 — Married | Удалить из ungated; оставить только в `MarriageDialogueHarvey` / spouse When |
| `dialoguesHarvey.json` | `eventSeen_eventHarveyFirstMeeting_oneday` | Нет | «ты», «хрупкая», «не позволю исчезнуть» | Раннее событие, тон 6+ ❤ | 1 | Смягчить; «Вы» если FP < 750 |
| `dialoguesHarvey.json` | `eventSeen_eventHarveyFirstMeeting_fourweeks` | Нет | **«Любовь — часть исцеления»** | «люблю»/love до Dating | 2b max без romance-слов | Убрать «любовь»; заменить на «доверие» / «забота» |
| `dialoguesHarvey.json` | `eventSeen_528013_fourweeks` | Нет | «не отпущу», романтика воздушного шара | Romance без Dating gate | 3+ | Привязать к `eventSeen` + `Dating` или смягчить до 2b |
| `dialoguesHarvey.json` | `topicHarvey_ForcedHospitalization` (ungated) | Нет | «Дышите… **Вы** под наблюдением» | ✅ Медицинский «Вы» | 0 (severe) | OK; не смешивать с married-версией в 6+ блоке |
| `dialoguesHarvey.json` | `topicHarveyTrust_*`, `topicHarveyStorm_*` | Нет (trust arc) | «Вы» / смешанно | **Специально event-gated trust-arc** — в целом OK | 0–1 | Сохранить; не автозаменой «Вы»→«ты» |
| `dialoguesHarvey.json` | `strings/schedules/Harvey` → `Fri.000`, `Fri.001`, `Sat.000`, `winter_15.000` | Нет | «ты» | Schedule без hearts | 0 | «Вы» или `marriage_*` только для супругов |
| `dialoguesHarvey.json` | `strings/schedules/Harvey` → `marriageJob.000`, `marriage_Mon.*` | Vanilla marriage schedule | «котёнок», «малышка», «солнышко» | ✅ Если ключ только у женатых | 4 | OK при условии engine gate |
| `dialoguesHarvey.json` | **Блок** `Hearts: 6,7,8,9,10` | 6+ ❤ | «запрещаю», «под моим контролем», «не отпущу» | Контроль без escape hatch на 6–8 ❤ | 2 (6–8) | Добавить `$q`/отказ; смягчить собственность |
| `dialoguesHarvey.json` | **Блок** `Hearts: 4,5,6,7` | 4–7 ❤ | «ты», «хрупкая», «под защитой» | На 4 ❤ (750 FP) ещё ранняя стадия 1 | 1 | Отделить 4–5 от 6–7; убрать romance-оттенок на 4–5 |
| `dialoguesHarvey.json` | **Блок** `Hearts: 8,9,10` *(коммент: «РОМАНТИКА»)* | 8–10 ❤, **без `!Dating`** | **«малышка»**, **«котёнок»**, **«девочка моя»**, **«люблю»**, «только моя» | **Married/Dating-тон до букета** | 2b (9–10 ❤, не Dating) | Убрать pet names и «люблю»; добавить `!Relationship Dating` для romance-слоя **или** переименовать блок в 2b |
| `dialoguesHarvey.json` | `Fri8`, `Mon8`…`Sun10` (внутри 8–10 блока) | 8–10 ❤ | «солнышко», «котёнок», «люблю проводить время» | Pre-dating romance | 2b | Переписать под 2b; romance → Dating-блок |
| `dialoguesHarvey.json` | `summer_10` (8–10 блок) | 8–10 ❤ | «**ты только моя**, девочка моя» | «моя» + pet name | 2b | «Ты важна» без «моя»; pet names → Married |
| `dialoguesHarvey.json` | `emotionalReaction_Scared` (8–10) | 8–10 ❤ | «не отпущу тебя одну» | Собственность без выбора | 2 | «Я рядом» + ветка дистанции |
| `dialoguesHarvey.json` | **Блок** `Relationship: Dating` | Dating | «солнышко» в topics, смешанный тон | Частично OK | 3 | OK для «солнышко»; проверить «котёнок» в topics — см. cure |
| `dialoguesHarvey.json` | `MarriageDialogueHarvey` | Married | «котёнок», «девочка моя», контроль | ✅ Married-тон | 4 | Добавить escape hatch где жёсткий контроль |
| `dialoguesHarveyCure.json` | *(базовый блок без When)* | **Нет** | «ты», лечение | Лечение доступно с ранней игры | 0–1 на triage | База: «Вы» для FP<750; «ты» с 750+ |
| `dialoguesHarveyCure.json` | `topicBadlyHurtCured` (base) | Нет | «организм очень **хрупкий**» | Допустимо мед.; borderline | 1+ | OK если «организм»; не «ты хрупкая» |
| `dialoguesHarveyCure.json` | `Treat_*_Before*` (base) | Нет | «ты», «хрупкая девушка», «под наблюдением» | Severe medical — частично OK; «ты» на 0 ❤ | 0 / 1+ | Split по FP; «Вы» на 0 |
| `dialoguesHarveyCure.json` | **Блок** `Hearts: 6,7,8,9,10` | 6+ ❤ | «**ты у меня**», «запрещаю», «не отпущу» | Собственность + контроль | 2 | «@» вместо «у меня»; escape hatch |
| `dialoguesHarveyCure.json` | `topicSprainedAnkleCured` (6–10) | 6+ ❤ | «**запрещаю** бегать» | Жёсткий запрет | 2 | «настаиваю» + выбор |
| `dialoguesHarveyCure.json` | **Блок** `Relationship: Married` | Married | pet names, «люблю мужа», поцелуи | ✅ Married | 4 | OK; проверить «не давая возразить» → soft stop |
| `dialoguesHarveyCure.json` | **Блок** `Relationship: Dating` | Dating | **«котёнок»**, **«девочка моя»**, **«малышка»** во всех `topic*Cured`, `topic*Phase*` | Pet names уровня **Married** в Dating | 3 | Dating: только «солнышко»/«моя девочка»; «котёнок»/«девочка моя» → Married-блок |
| `dialoguesHarveyCure.json` | `Treatment_Phase_Encouragement` (Dating) | Dating | «не отпущу», «моя девочка» | Married-лексика | 3 / 4 | Перенести фразы в Married; Dating — мягче |
| `dialoguesHarveyInjury.json` | *(базовый блок)* | **Нет** | «Вы» в topics; **«ты»** в `PhaseTransition_*` | Phase transitions без gate | 0 | PhaseTransition: «Вы» до 750 FP |
| `dialoguesHarveyInjury.json` | `topicHurt` … `topicFracturedBone` (base) | Нет | «Вы», протокол | ✅ Стадия 0 | 0 | Эталон |
| `dialoguesHarveyInjury.json` | **Блок** `Hearts: 3,4,5` | 3–5 ❤ | «ты» | ✅ Стадия 1 | 1 | OK |
| `dialoguesHarveyInjury.json` | **Блок** `Hearts: 6,7,8,9,10` | 6+ ❤ | «хрупкая», «не могу отпустить», «одна никуда» | Контроль без выхода | 2 | Добавить отказ; убрать «не отпустить одну» |
| `dialoguesHarveyInjury.json` | **Блок** `Relationship: Dating` | Dating | **«котёнок»**, **«девочка моя»**, **«малышка»**, «под моей защитой» | Married-лексика в Dating | 3 | Сократить до Dating-канона; pet names → Married |
| `dialoguesHarveyInjury.json` | `topicPassedOutInTown` (Dating) | Dating | «**девочка моя**», «не выходишь одна» | Контроль + pet name | 3 | «солнышко»/«моя девочка» + «останешься под наблюдением» с выбором |
| `dialoguesHarveyCare.json` | `topicHarveyGentleCare` (base) | Нет | «Вы», клиника | ✅ Стадия 0 | 0 | OK |
| `dialoguesHarveyCare.json` | Dating-блок | Dating | проверить при правках | — | 3 | Сверить с каноном при выравнивании |
| `dialoguesHarveyCureStress.json` | `topicStressTreatment*Cured` (Dating/Married gates) | Dating / Married | **«люблю тебя»**, «моя девочка» | «люблю» на Dating — спорно; «моя» — Married | 3 / 4 | Dating: без «люблю»/«моя»; Married: OK |
| `dialoguesHarveyStress.json` | `topicDarknessFullyCured` и др. | `Hearts 7–10` / Married | **«люблю тебя»**, pet names | **Файл подключён?** `content.json` — **закомментирован** | 2b / 4 | При включении — исправить; сейчас мёртвый код |
| `dialoguesHarveyPregnant.json` | spouse overrides | Married (implicit) | «не отпущу», хрупкая | Married — OK | 4 | Проверить escape hatch |
| `mail.json` | `HarveyOverhaul_E1`–`E4`, `E9`, trust mails | Event/story-gated | «Вы» | ✅ Trust arc | 0 | OK |
| `mail.json` | `HarveyMod_LoveConfession` | **Текст в Data/Mail**; триггер отправки **не найден** в CP | **«влюблён»**, «хрупкая» | Romance в базе mail | 3+ (если используется) | Gate `Dating`+ или удалить; не слать до букета |
| `mail.json` | `HarveyMod_FuturePlans` | Текст без явного trigger в CP | «под моим наблюдением», кольцо | Pre-marriage proposal tone | 3 / event | Только после Dating + event |
| `mail.json` | `HarveyMod_DangerWarning`, `MineWarning`, `EmergencySupervision` | Триггеры частично без Dating | «КАТЕГОРИЧЕСКИ ЗАПРЕЩАЮ», «ты» | Жёсткий контроль | 2+ severe / Dating | Severe-gate OK; иначе смягчить + relationship When |
| `mail.json` | `HarveyMod_WinterHealthTips` и др. recovery | Зависит от buff/topic | «хрупких», «ты» | Может прийти рано | 1+ / severe | Привязать к post-injury + min hearts |
| `mailCure.json` | `HarveyMod_WetCare`, `AlcoholWarning` | Buff/treatment | «ты», протокол | Medical — mostly OK | 1+ | «Вы» если FP < 750 |
| `triggersCare.json` | `triggerTimeReactionLate` | **FP ≥ 500**, **нет Dating** | → `HarveyMod_LateNightWarning` | Письмо с контролем на ~2 ❤ | 0–1 | Поднять порог до 750+ или добавить `Dating Married` / hearts |
| `triggersCare.json` | `triggerTimeReactionVeryLate` | **FP ≥ 1000**, нет Dating | → `HarveyMod_EmergencyNightWarning` | Жёсткий тон на ~4 ❤ | 1–2 | FP ≥ 1500 или hearts 6+ |
| `triggersCare.json` | `triggerEmergencySupervision` | FP ≥ 2000, topics | → `HarveyMod_EmergencySupervision` | Протокол «круглосуточно» | 2b / severe | OK если severe; иначе Dating |
| `triggersCare.json` | `triggerLocationReactionMine` | Dating/Engaged/Married | `HarveyMod_MineWarning` | ✅ Gate OK | 3+ | Текст письма — severe, OK |
| `eventsMineRescue.json` | `eventHarveyMineRescue` | **Нет hearts** (раннее падение) | «**ты**», «Что **ты** здесь делаешь» | «ты» на стадии 0 | 0 | «Вы» / безличное «пациент» в triage |
| `eventsMineRescue.json` | `eventHarveyMineRescue` | Нет | «**Я не отпущу**» (стр. ~154) | Собственность в rescue | 0 severe | «Я рядом» / «Держитесь» |
| `eventsMineRescue.json` | follow-up mail in file | Post-rescue | «ты», контроль | Mixed | 1+ | «Вы» если FP < 750 |
| `events.json` | `HarveyOverhaulStory.E1`–`E12` (большинство) | Friendship + event chain | «Вы»→«ты» по прогрессу | **В целом выстроенный trust-arc** | 0→2b | Сохранить логику; точечно сверить E10+ |
| `events.json` | `HarveyOverhaulRomance.E1_NotAnExamDate` | **Dating**, FP 3500 | romance | ✅ Dating-only | 3 | OK |
| `events.json` | `eventHarveyMountainDate` | **Dating**, FP 2250 | date scene | ✅ | 3 | OK |
| `events.json` | `eventHarveyFirstDate`, `eventHarveyPropose` | Dating | romance | ✅ | 3 | OK |
| `events.json` | `HarveyMod_NightCrisis_PreDating` | FP 1500, **!Dating** | кризис, забота | Pre-romance event | 2b | Проверить реплики на pet names |
| `events.json` | storm/medical events (mixed) | Various | часть с `$l` romance | Сверить по event ID при правках | 2–3 | Аудит по одному событию при правке |
| `events.json` | farmer `message` (trust arc) | Event-gated | ≤1 предложение, emote | ✅ Речь фермерши | — | Эталон |
| `eventsCare.json` | care events | Mixed | medical | Сверить при правках | 0–2 | Точечный проход |
| `questsCure.json` | `HarveyMod_HarveyTreatment` completion | Quest (лечение) | **«солнышко»**, «под моей защитой» | Quest text без relationship gate | 1+ / severe | Neutral completion до Dating |
| `questsCure.json` | `HarveyMod_CriticalInjuryTreatment` | Quest | **«малышка»**, «дорога **мне**» | Pet name + romance | 1+ | Medical tone; без pet names |
| `questsCure.json` | `HarveyMod_RibsTreatment`, `AnkleTreatment`, … | Quest | «**малышка**», «**котёнок**» | Pet names в наградах квеста | 1–2 | Переписать на «@» / «пациент» |
| `questsStress.json` | completion strings | Quest | «ты», забота | Mostly OK | 1+ | Без «люблю» |
| `buffsCure.json` | `Description` (buff HUD) | Buff | «Харви…» narrative | HUD — не dialogue; низкий приоритет | — | Опционально выровнять |
| `content.json` | includes | — | `dialoguesHarveyStress.json` **commented out** | Мёртвый toxic-контент | — | Не включать без правки |
| *(C#)* | — | — | — | **Не найдено** в `HarveyOverhaul [CP]` | — | Триггеры — JSON (`triggersCare.json`) |

---

## Критические кластеры (подробнее)

### 1. Ungated блок `dialoguesHarvey.json` (строки ~18–275)

Перекрывает **vanilla keys** для всех игроков независимо от hearts:

- Gift reactions: смесь **«Вы»** ( `(O)201`, `(O)610` ) и **«ты»** ( `(O)432`, `(O)348`, `(O)395` ) в одном слое.
- **`AcceptGift_(O)395`** — единственный явный romance-gift в ungated: «солнышко», «люблю бодрствовать ради тебя».
- **`FlowerDance_Accept_Spouse`** в ungated — дублирует spouse-контент вне marriage gate.
- **`eventSeen_*`** memories — эмоциональная эскалация без проверки Dating (особенно `fourweeks` + «любовь»).

**Нужная стадия:** split на `Hearts 0,1,2` / `3,4,5` / … или `Friendship` tokens.

### 2. Блок `Hearts: 8,9,10` без `!Dating` (строки ~556–716)

Комментарий в JSON: «УРОВЕНЬ 8-10 СЕРДЕЦ (РОМАНТИКА)», но `When` только:

```json
"Hearts:Harvey": "8,9,10"
```

Игрок с **8–10 ❤ до букета** получает:

- `Mon8`…`Sun10`, `spring_*`, `Hospital_*` с **«солнышко»**, **«котёнок»**, **«девочка моя»**;
- **`Fri8`**: «**Я люблю** проводить с тobой время»;
- **`summer_10`**: «Сегодня **ты только моя**, девочка моя»;
- `FlowerDance_Accept`: «**Потанцуем, малышка?**» — date-tone до Dating.

**Нужная стадия:** **2b** (без romance-маркеров) **или** добавить второй слой `Relationship: Dating` / `Married` для romance-версий.

### 3. Dating-блоки cure/injury с Married-лексикой

При `Relationship: Dating` Content Patcher подставляет тексты с:

- `котёнок`, `малышка`, `девочка моя` — по канону **только Married (4)**.
- Dating (3) допускает **«солнышко»**, **«моя девочка»**, не «котёнок» и не «дорогая».

Затронуты десятки ключей: `topic*Cured`, `topic*Phase*`, `Treatment_Phase_*`, `topicHurt`, … в `dialoguesHarveyCure.json` и `dialoguesHarveyInjury.json`.

### 4. Триггеры почты без relationship gate

| Триггер | Условие | Письмо | Проблема |
|---------|---------|--------|----------|
| `triggerTimeReactionLate` | TIME 22–02, **FP ≥ 500** | `HarveyMod_LateNightWarning` | ~2 ❤, стадия 0 — «ты», «отправлю в клинику» |
| `triggerTimeReactionVeryLate` | TIME 24–02, **FP ≥ 1000** | `HarveyMod_EmergencyNightWarning` | ~4 ❤ — тон супруга/опекуна |
| `triggerTimeReactionEarly` | FP ≥ 300 | `HarveyMod_EarlyMorningCare` | Очень ранний FP |

**Как исправить:** добавить `PLAYER_NPC_RELATIONSHIP Current Harvey Dating Married` **или** `PLAYER_FRIENDSHIP_POINTS Current Harvey 1500` (3+ ❤) в зависимости от задумки; тексты писем — отдельно по стадиям.

### 5. `dialoguesHarveyInjury.json` — PhaseTransition без gate

В базовом блоке (~40–59) фразы `PhaseTransition_Concussion_2` и др. используют **«ты»**, «**Можешь** потихоньку…», «**ты** честно соблюдала» — могут показываться при **«Вы»**-topics на 0 ❤.

---

## Что уже хорошо

- **`dialoguesHarveyInjury.json`**: базовые injury-topics и блок `Hearts: 0,1` — последовательное **«Вы»**.
- **Trust / story arc**: письма `HarveyOverhaul_E*`, topics `topicHarveyTrust_*`, `topicHarveyStorm_*`, события `HarveyOverhaulStory.E*` — выстроенная лестница 0 → 2b с «Вы» на ранних этапах.
- **`events.json`**: romance-сцены (`eventHarveyFirstDate`, `HarveyOverhaulRomance.E1`, `eventHarveyMountainDate`) gated **`Relationship: Dating`**.
- **Речь фермерши**: `speak farmer` **не используется**; в events — `message` ≤1 предложения, `quickQuestion`, `emote farmer` — **соответствует** гайду.
- **Married-блоки** (`MarriageDialogueHarvey`, cure/injury Married): тон целевой; правки — только escape hatch.

---

## Рекомендуемый порядок выравнивания (без автозамен)

1. **Ungated `dialoguesHarvey.json`** — split по hearts / relationship (максимальный игровой эффект).
2. **Блок `Hearts 8–10`** — переименовать в 2b или добавить `!Dating`; убрать pet names и «люблю».
3. **Dating-блоки** cure/injury — понизить лексику до Dating-канона; Married-версии оставить в Married-блоке.
4. **`triggersCare.json`** — FP-пороги + relationship для `HarveyMod_*Warning` писем.
5. **`questsCure.json`** — нейтральные completion texts до Dating.
6. **`eventsMineRescue.json`** — «Вы» на triage для FP < 750.
7. **`dialoguesHarveyStress.json`** — не включать в `content.json` до правки.

---

## Примечания по методологии

- Аудит выполнен **вручную** (grep + чтение gate-блоков), **без Python-скриптов** и без массовой автозамены.
- Один JSON-ключ может иметь **несколько** CP-патчей; фактический текст = победитель по `Priority` + `When`. Перед правкой проверять in-game / SMAPI log.
- Повторяющиеся строки в Dating/Married cure (`topic*Cured` ×12 травм) — **одна и та же проблема**, исправлять шаблоном вручную по каждому ключу.

---

*Следующий шаг (по запросу): точечный audit одного файла с полным списком ключей Dating-блока cure/injury или in-game checklist по стадиям.*
