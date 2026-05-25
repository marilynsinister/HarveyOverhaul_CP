# План выравнивания тона Харви

**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Источник проблем:** [audit-harvey-tone-current.md](./audit-harvey-tone-current.md)  
**Статус:** планирование — **код не менять** до утверждения плана.

---

## Принципы работы

1. **Не использовать скрипты автозамены** («Вы»→«ты», массовая замена «люблю»/«моя»). Каждый ключ править вручную с учётом gate.
2. **Сначала gates, потом тексты** — если текст верный, но виден не той стадии, достаточно gate; если gate верный, но лексика не та — править текст.
3. **Предпочтительная архитектура слоёв** (сверху вниз по `Priority: Late`):

   | Слой | When | Стадия |
   |------|------|--------|
   | A | `Relationship: Married` | 4 |
   | B | `Relationship: Dating` | 3 |
   | C | `Hearts: 9,10` + `!Relationship: Dating` | 2b |
   | D | `Hearts: 6,7,8` | 2 |
   | E | `Hearts: 3,4,5` | 1 |
   | F | `Hearts: 0,1,2` или FP < 750 | 0 |

4. **Trust-arc не ломать:** `topicHarveyTrust_*`, `HarveyOverhaulStory.E*`, письма `HarveyOverhaul_E*` — «Вы» на ранних этапах оставить; не включать в массовый split без проверки event chain.
5. **Medical severe-gate:** шахта, критическое лечение, госпитализация могут быть жёстче обычного тона, но на стадии 0 — только **«Вы»** и протокол, без romance-маркеров.

---

## Карта стадий → CP-условия

| Стадия | Hearts (ориентир) | Friendship | Обращение | Romance-маркеры |
|--------|-------------------|------------|-----------|-----------------|
| 0 | 0–2 | < 750 | Вы | запрещены |
| 1 | 3–5 | 750–1249 | ты | запрещены |
| 2 | 6–8 | 1500–1999 | ты | запрещены |
| 2b | 9–10 до букета | 2000+ | ты | запрещены |
| 3 | Dating | — | ты | солнышко, моя девочка |
| 4 | Married | — | ты | котёнок, девочка моя, моя |

---

# P0 — ломает immersion / нарушает канон на ранних стадиях

Критерий: игрок на **0–2 ❤ (FP < 750)** или **до Dating** видит то, что по канону недопустимо.

---

## P0-1. Ungated блок `dialoguesHarvey.json` (без `When`)

**Файл:** `assets/Code/dialoguesHarvey.json` (~строки 18–275)  
**Проблема:** десятки vanilla-ключей активны **всегда** — «ты», «хрупкая», romance, spouse-тон с 0 ❤.

| Подпроблема | Ключи (примеры) | Рекомендация |
|-------------|-----------------|--------------|
| «ты» с 0 ❤ | `Farm_Entry`, `Hospital_Entry`, `GreenRain*`, `AcceptBirthdayGift_*`, многие `AcceptGift_*` | **Split** на слои F (0–2) + E (3–5) + … |
| Romance без Dating | `AcceptGift_(O)395` («солнышко», «люблю») | **Gate:** перенести в слой B (`Relationship: Dating`); в ungated/F — нейтральный AcceptGift |
| Spouse без Marriage | `FlowerDance_Accept_Spouse` | **Gate:** удалить из ungated; оставить только в `MarriageDialogueHarvey` / слой A |
| Ранние memories | `eventSeen_eventHarveyFirstMeeting_*`, `eventSeen_528013_*` | **Split:** версия F (Вы, протокол) + версии E+ по hearts; romance-фразы — только B+ |
| «Любовь» до Dating | `eventSeen_eventHarveyFirstMeeting_fourweeks` | **Текст:** «доверие» / «забота», не «любовь»; или **gate** hearts 9–10 + event |

**Предлагаемый порядок правки:**
1. **Gate:** разбить ungated `Entries` на 6 слоёв (таблица выше); ungated оставить только truly-neutral (`Introduction`, `DumpsterDiveComment`, часть gift с «Вы»).
2. **Текст:** для слоя F переписать «ты»→«Вы», убрать pet names и «хрупкая» о личности.
3. **Split:** дублировать ключи `AcceptGift_*`, `GreenRain*`, `eventSeen_*` по слоям — не один `$c` на весь файл.

**Эталон для слоя F:** `Introduction`, `topicHarvey_ForcedHospitalization` (ungated), база `dialoguesHarveyInjury.json`.

---

## P0-2. Блок `Hearts: 8,9,10` без `!Dating` (ложная «романтика»)

**Файл:** `assets/Code/dialoguesHarvey.json` (~556–716)  
**Gate сейчас:** `"Hearts:Harvey": "8,9,10"`  
**Проблема:** комментарий «РОМАНТИКА», но срабатывает **до букета** — pet names, «люблю», «ты только моя», date-tone.

| Подпроблема | Ключи (группа) | Рекомендация |
|-------------|----------------|--------------|
| Pet names до Dating | `Mon8`…`Sun10`, `spring_*`, `Hospital_*`, `timeReaction_*`, `locationReaction_*` | **Split:** текущий блок → слой **C (2b)** без pet names; новый слой **B (Dating)** — romance-лексика |
| «люблю» | `Fri8` | **Текст** в 2b: «Мне нравится проводить с тобой время»; «люблю» — только B |
| «ты только моя» | `summer_10` | **Текст** в 2b: «Ты важна»; «моя» — только A |
| Date-tone | `FlowerDance_Accept` («Потанцуем, малышка?») | **Gate + текст:** 2b — нейтральное приглашение; Dating — тёплое |

**Предлагаемый порядок:**
1. **Gate:** переименовать блок в «2b»; добавить `"Relationship:Harvey": "Dating, Married"` **не** — использовать `!Dating` для слоя C:
   ```json
   "When": {
     "Hearts:Harvey": "8,9,10",
     "Relationship:Harvey": "Unmet"
   }
   ```
   (или эквивалент CP: hearts 8–10 без Dating/Married — проверить синтаксис CP 2.7).
2. **Текст:** пройти все ключи слоя C — убрать запрещённые маркеры по [общему запрету до Dating](./harvey-relationship-tone-guide.md#общий-запрет-до-dating).
3. **Split:** скопировать romance-версии ключей в существующий блок `Relationship: Dating` (слой B).

---

## P0-3. «ты» до Friendship 750 (не только dialoguesHarvey)

**Проблема:** «ты» на стадии 0 в каналах вне trust-arc.

| # | Файл | Место | Рекомендация |
|---|------|-------|--------------|
| 1 | `dialoguesHarvey.json` | `strings/schedules/Harvey` → `Fri.000`, `Fri.001`, `Sat.000`, `winter_15.000` | **Split:** schedule-ключи для 0–2 с «Вы»; «ты» с слоя E |
| 2 | `dialoguesHarveyCure.json` | базовый блок + `Treat_*` | **Split:** слой F («Вы») + слой E+ («ты»); severe допустим, обращение — нет |
| 3 | `dialoguesHarveyInjury.json` | `PhaseTransition_*` в базовом блоке | **Split:** PhaseTransition F с «Вы»; E+ с «ты» |
| 4 | `eventsMineRescue.json` | `eventHarveyMineRescue` | **Текст** (triage): «Вы» / «@»; «ты» — с FP ≥ 750 или отдельная ветка event |
| 5 | `eventsMineRescue.json` | follow-up mail в том же файле | **Split** mail-текста по FP или hearts |
| 6 | `mailCure.json` | `HarveyMod_WetCare`, `AlcoholWarning` | **Split:** «Вы» если FP < 750 |
| 7 | `triggersCare.json` | `triggerTimeReactionLate` (FP ≥ 500) | **Gate:** см. P0-5 |

**Не трогать без причины:** trust-topics с «Вы» (`topicHarveyTrust_*`) — event-gated arc.

---

## P0-4. Pet names и Married-лексика в блоке `Relationship: Dating`

**Файлы:** `dialoguesHarveyCure.json`, `dialoguesHarveyInjury.json`, частично `dialoguesHarveyCureStress.json`  
**Gate:** `Relationship: Harvey` = Dating — **верный**  
**Проблема:** текст уровня **стадии 4** (котёнок, малышка, девочка моя, «люблю тебя», «моя девочка»).

| Группа ключей | ~кол-во | Рекомендация |
|---------------|---------|--------------|
| `topic*Cured`, `topic*Phase*` | 12+ × N фаз | **Текст** в Dating-блоке: «солнышко» / «моя девочка»; «котёнок»/«девочка моя» перенести в Married-блок |
| `Treatment_Phase_*` | 5+ | **Split:** Dating — без поцелуев в лоб; Married — полная версия |
| `topicHurt`, `topicConcussion`, … (injury Dating) | 20+ | **Текст:** шаблон Dating (солнышко/моя девочка); Married — котёнок/малышка |
| `dialoguesHarveyCureStress.json` | `topicStressTreatment*Cured` | **Текст:** Dating — убрать «люблю» и «моя»; оставить в Married-слое |

**Предлагаемый порядок:**
1. **Текст:** составить **шаблон фразы Dating** для cure/injury (1 эталон на «завершение лечения», 1 на «фаза»).
2. **Split:** Married-блок уже есть — убедиться, что «тяжёлые» pet names **только** там; Dating-блок упростить.
3. **Gate:** не менять (Dating gate корректен).

---

## P0-5. Почта и триггеры без relationship gate (жёсткий / интимный тон слишком рано)

**Файл:** `assets/Code/triggersCare.json` + `assets/Code/mail.json`

| Триггер | Условие сейчас | Письмо | Рекомендация |
|---------|----------------|--------|--------------|
| `triggerTimeReactionLate` | FP ≥ 500, нет Dating | `HarveyMod_LateNightWarning` | **Gate:** FP ≥ 750 **или** `Hearts: 3,4,5`+; альтернатива — два письма (F: «Вы», протокол / E+: «ты») |
| `triggerTimeReactionVeryLate` | FP ≥ 1000 | `HarveyMod_EmergencyNightWarning` | **Gate:** FP ≥ 1500 (6+ ❤) или Dating; иначе мягче |
| `triggerTimeReactionEarly` | FP ≥ 300 | `HarveyMod_EarlyMorningCare` | **Gate:** FP ≥ 750 |
| `triggerEmergencySupervision` | FP ≥ 2000 + topics | `HarveyMod_EmergencySupervision` | **Gate:** добавить `HasConversationTopic` severe **и** (Dating **или** post-injury topic); иначе P1 |

| Письмо (текст в mail.json) | Проблема | Рекомендация |
|----------------------------|----------|--------------|
| `HarveyMod_LoveConfession` | «влюблён» в Data/Mail; trigger не найден | **Gate:** если когда-либо отправится — только `Dating`+; иначе **удалить/архивировать** текст |
| `HarveyMod_FuturePlans` | кольцо, «под моим наблюдением» | **Gate:** только story event / FP 3500+ Dating |

**Предлагаемый порядок:**
1. **Gate** в `triggersCare.json` — минимальный FP 750 для «личных» писем.
2. **Split** писем: `HarveyMod_LateNightWarning_Professional` (F) vs `_Personal` (E+) — если нужен контроль на ранней игре в medical framing.
3. **Текст:** убрать «отправлю в клинику на наблюдение» как наказание на 2 ❤ — заменить на «рекомендую осмотр».

---

## P0-6. Quest completion без relationship gate

**Файл:** `assets/Code/questsCure.json`

| Квест | Текст completion | Рекомендация |
|-------|------------------|--------------|
| `HarveyMod_HarveyTreatment` | «солнышко», «под моей защитой» | **Текст:** нейтральный medical («Рад, что ты пришла»); romance — **gate** Dating в отдельном completion (если CP поддерживает) или единый нейтральный |
| `HarveyMod_CriticalInjuryTreatment` | «малышка», «дорога мне» | **Текст:** severe medical, без pet names |
| `HarveyMod_RibsTreatment`, `AnkleTreatment`, … | «малышка», «котёнок» | **Текст:** «@», протокол; шаблон на все completion strings |

**Примечание:** квесты часто не имеют per-stage completion в vanilla — **предпочтительно нейтральный текст** для всех стадий до Dating, без split, если нет технической возможности gate.

---

## P0-7. `FlowerDance_Accept_Spouse` и spouse-ключи вне marriage

**Файл:** `dialoguesHarvey.json`  
**Проблема:** spouse-реплики в ungated или hearts-блоках.

| Рекомендация |
|--------------|
| **Gate:** все `*_Spouse` ключи — только слой A (`MarriageDialogueHarvey` или `Relationship: Married`) |
| **Текст:** не дублировать в hearts 8–10 |

---

## P0 — сводный чеклист готовности

- [ ] Ungated `dialoguesHarvey.json` разбит; с 0 ❤ только «Вы» и протокол
- [ ] Блок 8–10 ❤ не содержит pet names / «люблю» до Dating
- [ ] Dating-блоки cure/injury без «котёнок»/«девочка моя»
- [ ] Триггеры почты FP ≥ 750 для личного тона
- [ ] Mine rescue triage на «Вы»
- [ ] Quest completions без pet names
- [ ] `dialoguesHarveyStress.json` **не** подключать в `content.json` до правки

---

# P1 — заметно, но не всегда ломает раннюю игру

---

## P1-1. Контроль без opt-out (escape hatch)

**Стадии:** 2, 2b, частично 3–4  
**Файлы:** `dialoguesHarvey.json` (6–10 ❤), `dialoguesHarveyCure.json` (6–10), `dialoguesHarveyInjury.json` (6–10), `events.json`, `mail.json`

| Паттерн | Примеры | Рекомендация |
|---------|---------|--------------|
| «запрещаю», «никаких возражений» | `Hospital_Wed` (6+), cure `topicSprainedAnkleCured` | **Текст:** «настаиваю» + «можешь сказать стоп»; в events — `quickQuestion` |
| «не отпущу», «одна никуда» | `emotionalReaction_Scared`, injury 6–10 | **Текст:** «я рядом»; **events:** ветка «мне нужно пространство» |
| «госпитализирую» без выбора | `Hospital_Fri` (6+ блок) | **Текст:** «предлагаю остаться на наблюдении» + отказ |
| Locked hospitalization topics | `topicHarvey_ForcedHospitalization` (6+ vs ungated) | **Split:** severe — протокол; 6–8 ❤ — мягче + opt-out где не life-threatening |

**Подход:** для каждой жёсткой реплики — **один** из трёх:
1. **Gate** — только severe (buff/topic critical).
2. **Текст** — смягчить глагол.
3. **Split** — добавить `$q` / `quickQuestion` в **events**; в dialogue — фраза «скажи, если не согласна».

---

## P1-2. «Хрупкая» и телесные оценки слишком рано

**Канон:** до 6+ ❤ избегать «хрупкая» о **личности**; допустимо «организм», «состояние» в medical context.

| Файл | Где | Рекомендация |
|------|-----|--------------|
| `dialoguesHarvey.json` | ungated, 4–7, 8–10 | **Текст:** «хрупкая» → «организм требует внимания» / «@, ты устала» на 1–2; личностное «хрупкая девушка» — с 6+ или убрать |
| `dialoguesHarveyCure.json` | `Treat_*`, 6–10 cured | **Текст:** «хрупкая девушка» → «@» + medical; оставить «организм хрупкий» где уместно |
| `dialoguesHarveyInjury.json` | 6–10 | **Текст:** снизить частоту «бледная и хрупкая» в каждой реплике |
| `mail.json` | `HarveyMod_WinterHealthTips`, recovery letters | **Gate:** post-injury topic; **текст:** «ослабленный иммунитет», не «хрупкая» |

---

## P1-3. Почта интимного / собственнического тона без relationship gate

| Письмо | Проблема | Рекомендация |
|--------|----------|--------------|
| `HarveyMod_DangerWarning` | «КАТЕГОРИЧЕСКИ ЗАПРЕЩАЮ» | **Gate:** post-severe-injury topic + min hearts 6; **текст:** протокол, не «муж» |
| `HarveyMod_DoctorWorries` | «твоя безопасность — мой приоритет» | **Gate:** hearts 6+ или Dating |
| `HarveyMod_ComfortLetter`, `ProtectionOffer` | опека + «личный контроль» | **Gate:** Dating **или** hearts 8+; **текст:** до Dating — «как врач» |
| `HarveyMod_RecoveryReliefLetter` | «ужин + обязательный осмотр» | **Текст:** смягчить; **gate:** post-treatment topic OK |

---

## P1-4. События с быстрой эмоциональной эскалацией

| Event | Gate | Проблема | Рекомендация |
|-------|------|----------|--------------|
| `HarveyMod_NightCrisis_PreDating` | FP 1500, !Dating | проверить pet names / romance | **Текст:** аудит реплик → 2b; без «люблю» |
| `eventSeen_*` memories | ungated / weak gate | эскалация за 4 недели | **Split:** см. P0-1; **текст:** `fourweeks` без «любовь» |
| Storm / medical events в `events.json` | mixed | отдельные `$l` без Dating | **Gate** или **текст:** point audit per event ID |
| `eventsMineRescue` | no hearts | «не отпущу» | **Текст:** P0-3; собственность → «я рядом» |

**Trust-arc (E1–E12):** не замедлять без дизайн-решения — только точечно убрать romance-маркеры до Dating в ветках `!Dating`.

---

## P1-5. Блок `Hearts: 4,5,6,7` — смешение стадий 1 и 2

**Файл:** `dialoguesHarvey.json`  
**Gate:** одним блоком 4–7 ❤  
**Проблема:** на 4 ❤ (750 FP, стадия 1) тон как на 6–7 (стадия 2): «под защитой», длинные опекающие монологи.

| Рекомендация |
|--------------|
| **Split:** `Hearts: 3,4,5` (слой E) и `Hearts: 6,7` (слой D); 8 — в слое 2 |
| **Текст:** слой E — короче, без «запрещаю»; слой D — настойчивее + opt-out (P1-1) |

---

## P1-6. «Ты у меня» / собственническое «моя» до Dating

**Файлы:** `dialoguesHarveyCure.json` (6–10), `dialoguesHarvey.json` (6–10, 8–10)

| Рекомендация |
|--------------|
| **Текст:** «ты у меня такая» → «@, ты» / «твой организм»; «у меня» только Married |
| **Gate:** не требуется, если текст исправлен |

---

## P1 — сводный чеклист

- [ ] Жёсткий контроль только с severe-gate или opt-out
- [ ] «Хрупкая» о личности реже / позже
- [ ] Recovery-mail привязана к topics + min hearts
- [ ] Блок 4–7 ❤ разделён на 1 и 2
- [ ] PreDating events проверены на romance-маркеры

---

# P2 — полировка и качество, не блокер канона

---

## P2-1. Стилистическая полировка

| Область | Проблема | Рекомендация |
|---------|----------|--------------|
| Повторы «очень хрупкая, бледная, испуганный взгляд» | 6–10 ❤ dialogue | **Текст:** ротировать 3–4 описания; не в каждой реплике |
| Одинаковые cure `topic*Cured` | 12 травм | **Текст:** после P0/P1 — лёгкая вариативность opening line |
| HUD `buffsCure.json` Description | narrative от Харви | **Текст:** опционально; низкий приоритет |
| `dialoguesNpc.json` | не Харви | не в scope |

---

## P2-2. Однообразные реакции (location / time / emotional)

**Файл:** `dialoguesHarvey.json` слои D, C, B

| Рекомендация |
|--------------|
| **Текст:** `locationReaction_Mine`, `timeReaction_Late`, `emotionalReaction_Crying` — 2–3 варианта `$c` **вручную** (не скриптом) per stage |
| **Split:** не обязательно; достаточно `$c 0.5` с двумя заранее написанными фразами одной стадии |

---

## P2-3. Речь фермерши

**Аудит:** `speak farmer` не найден; `message` в events — короткие.

| Область | Рекомендация |
|---------|--------------|
| `quickQuestion` options | **Текст:** проверить длинные варианты (>6 слов) в `events.json` — укоротить (P2) |
| Будущий контент | не добавлять `speak farmer` >1 предложения |

---

## P2-4. Неидеальные, но допустимые формулировки

| Формулировка | Контекст | Рекомендация |
|--------------|----------|--------------|
| «моя работа» | 0–2b | **Оставить** — не romance |
| «под моим наблюдением» | medical | **Оставить** на 0+ в severe |
| «организм хрупкий» | cure base | **Оставить** или P2 → «организм ослаблен» |
| Trust-topics «Вы» при 3–5 ❤ | после trust arc | **Оставить** — exception по гайду |
| `marriage_*` schedule | engine-gated | **Оставить** |
| Married поцелуи / «котёнок» | слой A | **Оставить**; P1 opt-out где жёстко |

---

## P2-5. `dialoguesHarveyStress.json` (мёртвый код)

| Рекомендация |
|--------------|
| **Gate:** не включать в `content.json` |
| **Текст:** при будущем включении — полный rewrite по стадиям (сейчас «люблю», pet names на 7–10 ❤) |
| Приоритет ниже P0, но блокировать включение до rewrite |

---

## P2-6. `dialoguesHarveyPregnant.json`, `dialoguesHarveyCare.json`

| Файл | Рекомендация |
|------|--------------|
| `dialoguesHarveyPregnant.json` | Married-implicit — **P2:** проверить escape hatch на «не отпущу» |
| `dialoguesHarveyCare.json` | Dating-блок — **P2:** сверить с каноном после P0 Dating cure |

---

# Порядок внедрения (рекомендуемый)

```
Фаза 1 (P0, gates)     → dialoguesHarvey ungated split + Hearts 8–10 !Dating
Фаза 2 (P0, text)      → Dating cure/injury lexicon + quests + mine rescue
Фаза 3 (P0, triggers)  → triggersCare.json FP thresholds
Фаза 4 (P1)            → opt-out, хрупкая, split 4–7 hearts, mail gates
Фаза 5 (P2)            → polish, $c variants, quickQuestion trim
```

**После каждой фазы:** in-game smoke test на стадиях 0, 1, 2, 2b, 3, 4 (см. ниже).

---

# Матрица решений: gate vs текст vs split

| Ситуация | Gate | Текст | Split |
|----------|------|-------|-------|
| Romance виден на 0 ❤ | ✅ primary | ✅ | ✅ если один ключ на все стадии |
| Pet name в Dating-блоке | — | ✅ | Married уже есть — перенести фразу |
| «ты» на 0 ❤ | ✅ hearts/FP | ✅ «Вы» | ✅ preferred |
| Жёсткий контроль на 6 ❤ | ⚠️ severe only | ✅ смягчить | ✅ event $q |
| Один AcceptGift для всех | — | ❌ insufficient | ✅ по слоям |
| Quest completion | ⚠️ если возможно | ✅ neutral | редко |
| Trust arc «Вы» | ❌ не менять | ⚠️ точечно | ❌ |
| 8–10 ❤ romance до букета | ✅ !Dating | ✅ 2b tone | ✅ Dating layer |

---

# Smoke-test после правок

| # | Стадия | FP / hearts | Relationship | Что проверить |
|---|--------|-------------|--------------|---------------|
| 1 | 0 | 0–250 / 0–1 ❤ | — | Introduction, injury topic, gift, schedule — только **«Вы»**, нет pet names |
| 2 | 0 | после mine rescue | — | Event + mail — **«Вы»** |
| 3 | 1 | 750–1249 / 3–5 ❤ | — | «ты», нет «люблю»/pet names |
| 4 | 2 | 1500–1999 / 6–8 ❤ | — | настойчивость + возможность отказа в events |
| 5 | 2b | 2000+ / 9–10 ❤ | не Dating | нет pet names, нет «люблю» |
| 6 | 3 | любые | Dating | «солнышко»/«моя девочка» OK; не «дорогая»; нет «котёнок» |
| 7 | 4 | — | Married | полный канон; opt-out на жёстком контроле |
| 8 | Regression | trust arc | — | E1 письма с «Вы»; topics trust не сломаны |

---

# Что не входить в первую волну правок

- Полный rewrite всех `events.json` (только point fixes из P0/P1).
- Автогенерация вариантов dialogue.
- Изменение vanilla Harvey вне mod keys.
- Подключение `dialoguesHarveyStress.json` без rewrite.
- Слияние слоёв Married и Dating «для краткости».

---

# Связанные документы

- [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md) — канон
- [audit-harvey-tone-current.md](./audit-harvey-tone-current.md) — текущие нарушения

---

*План подготовлен для ручной реализации. Следующий шаг после утверждения: Фаза 1 (P0 gates) в `dialoguesHarvey.json`.*
