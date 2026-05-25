# Changelog: P0 tone fixes (dialoguesHarvey*.json)

**Дата:** 2026-05-25  
**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md), [harvey-tone-fix-plan.md](./harvey-tone-fix-plan.md)  
**Область:** только P0 — ранние стадии (0–2 ❤ / до Dating) не должны видеть romance-маркеры и «ты».

---

## Изменённые файлы

| Файл | Статус P0 |
|------|-----------|
| `assets/Code/dialoguesHarvey.json` | ✅ P0 + **gift reactions split** (50 ключей × 5 стадий) |
| `assets/Code/dialoguesHarveyCure.json` | ✅ P0/P1 — лестница тона cure (0–2 / 3–5 / 6–10) |
| `assets/Code/dialoguesHarveyCureStress.json` | ✅ gate + смягчение |
| `assets/Code/dialoguesHarveyInjury.json` | ✅ P0/P1 — лестница тона injury topics |
| `assets/Code/dialoguesHarveyCare.json` | ✅ без изменений (base «Вы», 3–5 в отдельном блоке) |
| `assets/Code/mail.json`, `mailInjury.json`, `mailCare.json`, `mailCure.json`, `mailStress.json` | ✅ P0/P1 — tone + gates (см. секцию mail) |
| `assets/Code/triggersInjuryMail.json`, `triggersCare.json` | ✅ gate sleep control, FP-пороги |
| `assets/Code/events.json`, `eventsCare.json`, `eventsMineRescue.json` | ✅ P0/P1 — tone + gates (см. секцию events) |
| `assets/Code/dialoguesHarveyStress.json` | — не в `content.json`, не трогали |
| `assets/Code/dialoguesHarveyPregnant.json` | — Married-implicit, P0 не требовал правок |

---

## Перенесённые блоки / ключи

### `dialoguesHarvey.json`

| Что | Откуда | Куда |
|-----|--------|------|
| `dating_Harvey`, `married_Harvey`, `dating_Harvey_memory_*` | ungated base | **удалены из base** — дубли есть в блоках `Relationship: Dating` / `Married` |
| `FlowerDance_Accept_Spouse` | ungated base | **удалён** — только marriage-слой |
| `marriageJob.000`, `marriage_Mon.000`, `marriage_Mon.001` | ungated `strings/schedules/Harvey` | **блок `Relationship: Married`** |
| Расписание `Fri.000`, `Fri.001`, `Sat.000`, `winter_15.000` | ungated (был «ты») | **остались в ungated**, переписаны на «Вы» |
| Блок «4–7 сердец» (реакции, локации, праздники) | ungated | **`When: Hearts 3,4,5,6,7`** — «ты» допустим для стадии 1+ |

### `dialoguesHarveyCure.json`

| Что | Откуда | Куда |
|-----|--------|------|
| ~321 ключ (`topic*`, `Recovery_*`, `Treat_*`, `Proximity_*`, …) | ungated base (git HEAD) | **слой F:** `Hearts 0,1,2` — «Вы», медпротокол |
| те же ключи | base «ты» | **слой E:** `Hearts 3,4,5` — личная забота без romance |
| те же ключи + overrides | base «ты» | **слой D:** `Hearts 6,7,8,9,10` — усиленная тревога, без pet names |
| Блоки `Relationship: Married`, `Relationship: Dating` | git HEAD | без изменений gate / тона |

**P0/P1 — исправлено (2026-05-25):**

- **Архитектура:** ungated base заменён на три hearts-блока; Married/Dating сохранены отдельно.
- **0–2 ❤:** `Treat_*_Before` → «Сейчас осмотрю и обработаю…»; `Treat_*_After` → «После перевязки избегайте нагрузки…»; `topicHarvey_NightRound` — протокол; `topic*Cured` — клинический «Вы» без «хрупкая» / «не позволю».
- **3–5 ❤:** overrides для `topic*Cured`, `Treat_Hurt_*`, `Proximity_*`, `Treatment_Phase_Warning`; «ты», без pet names.
- **6–10 ❤ pre-Dating:** overrides с тревожным тоном («Ты снова решила справиться одна?», «Я рядом — просто дай проверить»); strip forbidden из base.
- **Проверено grep:** `хрупкая`, `солнышко`, `не позволю`, `не могу позволить` — только в Married (стр. ~1200+) и Dating (~1300+).

**Сохранено:** медицинская конкретика по травмам (Recovery_Complete_*, фазовые topic*, injury-specific Treat_*).

**P1 — остаточное (не блокер):** в слое 0–2 часть `Recovery_Complete_*` после auto-«Вы» может содержать единичные ty-императивы («Береги», «слушай») — при smoke-test прочитать вслух 5–10 строк.

**Скрипт пересборки:** `scripts/cure_tone_final.py` (читает base из `git HEAD`, не из уже пересобранного файла). **Не использовать** `scripts/cure_tone_layers.py` — ломает JSON.

### `dialoguesHarveyCure.json` — прежняя запись (gate split)

### `dialoguesHarveyCureStress.json`

| Что | Откуда | Куда |
|-----|--------|------|
| `topicStressTreatment*` started/cured | ungated | **`When: Hearts 0,1,2`** + перепись на «Вы» |
| дублирующий блок started/cured | `Hearts 7,8,9,10` | **`When: Hearts 3,4,5,6,7,8,9,10`** (закрыт gap 3–6 ❤) |

---

## Смягчённые тексты (base / 0–2)

### `dialoguesHarvey.json` — ungated base (Вы, без romance)

- **Vanilla / entry:** `Introduction`, `Hospital_Entry`, `Farm_Entry`, `breakUp`, `DumpsterDiveComment`, `HitBySlingshot`
- **Подарки / отказы:** `AcceptBirthdayGift_*`, `AcceptBouquet`, `RejectBouquet_*`, `RejectMermaidPendant_*`, `RejectMovieTicket_*`, `RejectRoommateProposal_*`, `MovieInvitation`, `FlowerDance_Decline`
- **События / memories:** `eventSeen_*`, `event_heart*`, `event_grave*`, `eventSeen_eventHarveyFirstMeeting_*` (`fourweeks`: «люблю» → «доверие»)
- **Trust / visit topics:** `topicHarveyDeclineFirstWalk` … `topicHarveyFirstVisit*`, `topicHarvey_*` (wet bandage, pain flare, door signal, bad day)
- **Реакции (base):** `timeReaction_*`, `locationReaction_*`, `emotionalReaction_*`, `situationReaction_*` — «Вы», без «не позволю» / «под моей защитой»
- **Погода / курорт / алкоголь:** `GreenRain*`, `AcceptGift_(O)432/348`, `Resort_*`, `RejectItem_category_alcohol`

### `dialoguesHarvey.json` — блок 6+ ❤

- `Hospital2`: убрано «под моей защитой» → «безопасное место для пациентов»
- `topicHarvey_ForcedHospitalization`: убрано «не отпущу»

### `dialoguesHarveyCure.json` — слой 0–2 (устарело — см. секцию P0/P1 выше)

- Gate + overrides через `cure_tone_final.py`; см. актуальную архитектуру в секции cure P0/P1.

### `dialoguesHarveyCureStress.json`

- Блок 0–2: полный протокол на «Вы»
- Блок 3–10: `topicStressTreatmentTooColdStarted` — «не позволю» → «простуда недопустима»
- Блок 7–10: `topicStressTreatmentCriticismCured` — убрано «моя особенная девочка»

### `dialoguesHarveyInjury.json` — P0/P1 (лестница тона)

**Архитектура слоёв (проверено / дополнено):**

| Слой | When | Обращение |
|------|------|-----------|
| F | `Hearts 0,1,2` | «Вы», клинический протокол |
| E | `Hearts 3,4,5` | «ты», мягкая забота без romance |
| D | `Hearts 6–10` pre-Dating | «ты», тёплая тревога, без pet names |
| B | `Relationship: Dating` | солнышко, моя девочка + escape hatch |
| A | `Relationship: Married` | котёнок, девочка моя + opt-out в ключевых строках |

**P0 — исправлено:**
- Base-блок получил явный gate `Hearts 0,1,2` (все `topic*` травм на «Вы»).
- Блок `topicBadlyHurt` Hospital: **split** — 0–2 «Вы» / 3–5 «ты» (раньше «ты» на 0–2 ❤).
- Блок 3–5: **добавлены все** injury topics (раньше только ~8 ключей → остальные падали на «Вы» при 3–5 ❤).
- Блок 6–10: **полный набор** topics; убраны «не отпущу», «хрупкая» о личности, «не оставлю одну» из pre-Dating.

**P1 — смягчено:**
- `topicOverprotectiveMode` (6–10): протокол + «скажи стоп».
- `topicConcussion` (6–10): «спорить будем после осмотра», без pet names.
- `topicFarmerExhausted` Hospital (6–10): убрана угроза шприцом.
- Dating/Married `topicOverprotectiveMode`: escape hatch («стоп», «граница»).
- Married `topicPassedOutInTown`, `FarmHouse_Sat` (topicBadlyHurt), `Hospital2` (exhausted): opt-out вместо жёсткого «не выходишь одна» / «не отпущу».

**Добавлено:**
- `topicFarmerExhausted` Hospital-блок для `Hearts 3,4,5`.
- `topicPostOperativeCare` Hospital-блок для `Hearts 3,4,5`.

**Не трогали:** `PhaseTransition_*` (клинически нейтральны; ty-версии только в блоке 3–5 для Concussion).

**Не найдено в моде:** `topicSpeakToHarvey` (ключ отсутствует). Маппинг: `topicFarmerExhausted` = exhausted, `topicBurnWounds` = burn, `topicFracturedBone` = fracture.

---

## Что требует ручной проверки (smoke-test)

1. **Новая игра, 0–2 ❤:** разговор с Харви — только «Вы»; нет pet names, «люблю» (romance), «не отпущу», «под моей защитой».
2. **Лечение травмы на 0–2 ❤:** `Treat_*` / `topic*Cured` / `topicHarvey_NightRound` — протокол «Вы»; сравнить с 3–5 и 6–10 (должны отличаться по тону).
3. **3–5 ❤:** «ты» в cure-блоке 3–5; `topicHurtCured` — «Давай проверим повязку…»; без pet names.
4. **6–8 ❤ до букета:** `topicHurtCured` — «Ты снова решила справиться одна?»; `Treat_Hurt_Before1` — «Ты опять терпела…»; pet names только с Dating.
5. **Dating / Married:** pet names и супружеский тон на месте (`marriage_Mon.*` только при `Relationship: Married`).
6. **`dialoguesHarveyCure.json` слой 0–2:** auto-rewrite мог оставить редкие смешения «Вы» + старый imperative — прочитать 5–10 `Recovery_Complete_*` / `Treat_*` вслух.
7. **Trust-arc:** `topicHarveyTrust_*`, `HarveyOverhaulStory.E*`, письма — не трогали; убедиться, что event chain не сломан.
8. **Блок 3–7 vs 6+:** часть ключей (`situationReaction_*`, `FlowerDance_Accept`) в 3–7 всё ещё содержит «не позволю» / «под моей защитой» — **намеренно для 3+**, но при тесте на 3–5 ❤ проверить, не слишком ли жёстко для стадии 1 (P1-кандидат).
9. **Topic-gated блоки** (`topicFirstMeeting`, `topicHarveyWalkGood`, `topicHarveyTraumaReveal`): остаются на «ты» — OK, если topic активен только после события; проверить, не всплывают ли на 0 ❤ без topic.
10. **`dialoguesHarveyInjury.json`:** на 3–5 ❤ проверить `topicBruisedRibs`, `topicBurnWounds`, `topicCold` — должны быть «ты» без pet names; на 6–10 — тёплая тревога без «солнышко»; Dating/Married — pet names + opt-out в overprotective/exhausted.

## Вспомогательные скрипты (не часть мода)

- `scripts/cure_tone_final.py` — rebuild cure.json (0–2 / 3–5 / 6–10 + Married/Dating)
- `scripts/p0_tone_fix.py` — batch для main + cureStress
- `scripts/p0_cure_gate.py` — split cure.json (legacy)
- `scripts/fix_cure_imperatives.py` — доработка imperative в слое 0–2 (legacy)

*Скрипты можно удалить после ревью; в `content.json` не подключены.*

---

## P0/P1 — mail*.json (2026-05-25)

**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Цель:** письма не звучат как парень/муж на 0 ❤; C#-fallback — клинический «Вы».

### Изменённые файлы

| Файл | Gate | Текст |
|------|------|-------|
| `assets/Code/triggersInjuryMail.json` | **да** — sleep control split | — |
| `assets/Code/triggersCare.json` | **да** — FP-пороги, EmergencySupervision, note4 → Married | — |
| `assets/Code/mailInjury.json` | — | **да** — sleep split + C# injury/cure fallback |
| `assets/Code/mailCure.json` | — | **да** — процесс лечения, фазы, wet/alcohol |
| `assets/Code/mailCare.json` | — | **да** — recovery/post-trauma/cave/mine/step |
| `assets/Code/mailStress.json` | — | **да** — все treatment-start (C# без gate) |
| `assets/Code/mail.json` | — | **да** — time/mine/supervision; moderate/intensive care |
| `assets/Code/eventsMineRescue.json` | — | **да** — `mailHarveyAfterMineRescue` |
| `content.json` | **да** — Include `triggersInjuryMail.json` | — |

### Gate (CP-триггеры)

| Триггер | Было | Стало |
|---------|------|-------|
| `triggerSleepControl_*` (Injury mod) | один `mailHarveySleepControl` без ❤/Dating | **4 триггера:** Neutral 0–3 / Friend 4–10 / Dating / Married; Injury-триггер **null** |
| `triggerTimeReactionLate` | FP 500 | **750** (~3 ❤) |
| `triggerTimeReactionVeryLate` | FP 1000 | **1500** (~6 ❤) |
| `triggerTimeReactionEarly` | FP 300 | **750** |
| `triggerEmergencySupervision` | FP 2000 | **+ Dating/Married** |
| `triggerHarveyNote4` | Dating Married | **Married only** |
| Notes 1–3, cave/mine, moderate care | уже Dating/Married | без изменений |

**C# gate изменить нельзя** (нет исходников `HarveyOverhaulInjury.dll`). Для всех ID, которые шлёт DLL/triggers Injury-мода без проверки отношений — **neutral fallback в CP** (перекрывает Data/Mail).

### mailHarveySleepControl — split

| ID | When (CP) | Тон |
|----|-----------|-----|
| `mailHarveySleepControl_Neutral` | 0–3 ❤, !Dating !Married | «Вы», рекомендации сна, клиника; **без** curfew-приказа, «худая/бледная», успокоительного |
| `mailHarveySleepControl_Friend` | 4–10 ❤ pre-Dating | «ты», мягкая забота |
| `mailHarveySleepControl_Dating` | Dating | теплее + item 773, без давления |
| `mailHarveySleepControl_Married` | Married | домашняя нежность + opt-out «скажи, если хочешь побыть одна» |
| `mailHarveySleepControl` (legacy) | fallback = Neutral | для совместимости |

### C#-отправители → neutral текст (только CP override)

**HarveyOverhaulInjury.dll** (без relationship gate):  
`mailHarveyMineForbidden`, `HarveyMod_Neglect`, `HarveyMod_NeglectWarning`, `HarveyMod_DirtyWoundInfection`, `HarveyMod_WetBandageInfection`, `HarveyMod_TreatmentUrgentReminder`, `HarveyMod_TreatmentFinalWarning`, `HarveyMod_PainFlare`, `HarveyMod_WetBandage`, `HarveyMod_WetStitches`, `HarveyMod_AllergicRash`, injury alerts (`RibInjuryAlert` … `InfectionAlert`), `HarveyMod_HurtCare`, `CriticalCareNotice`, `PostSurgeryInstructions`, `OverprotectiveNotice`, `HospitalAdmission/Discharge`, `TooColdCare`, `HungerAdvice`, `mailHarveyOverprotectiveNotice`.

**triggersCure.json (Injury mod):**  
`HarveyMod_TreatmentProgress`, `RecoveryUpdate`, `MorningCheckup`, `NutritionPlan`, `RecoveryMilestone`, `TreatmentComplete`, `FullRecovery`, `PreventiveCare`, `SafetyGuidelines`, phase mails, `WetCare`, `WetStitchesCare`, `AlcoholWarning` → **mailCure.json**.

**Stress treatment mails** (`mailHarveyStressTreatment*`, `HarveyStress_Letter*_Start`) — вероятно C#/Stress-мод без gate → **все на «Вы»**, без «не позволю».

### Только текст (gate уже был)

- `mailHarveyNote1–3`, `NoteGirlfriend`, `NoteWife`, `ModerateCare`, `IntensiveCare` — триггеры Dating/Married; тексты оставлены romantic где уместно.
- `mailHarveyCaveWarning`, `mailHarveyMineWarning` — Dating/Married gate; смягчены (рекомендация, не «приказ»).
- `HarveyMod_LateNightWarning`, `EmergencyNightWarning`, `EarlyMorningCare`, `MineWarning`, `EmergencySupervision` — gate FP/Dating; тексты смягчены; удалены дубликаты harsh-ключей в `mail.json`.
- Story mails (`mailHarveyHomeSafetyProtocol`, `MinesAgreement`, `FuturePlanNote`, `HarveyOverhaul_E*`) — event-gated; не трогали.

### Smoke-test (mail)

1. **0–2 ❤, обморок от недосыпа:** `mailHarveySleepControl_Neutral` — «Вы», без curfew/успокоительного.
2. **6 ❤ pre-Dating, тот же триггер:** `_Friend`.
3. **Dating/Married:** соответствующий вариант + item только Dating/Married.
4. **0 ❤ + травма (Injury C#):** neglect/wet bandage/pain flare — клинический «Вы».
5. **0 ❤ + stress treatment start:** `mailHarveyStressTreatment*` — «Вы», без контроля.
6. **Dating, cave/mine с buff:** мягкое предупреждение, не угроза вытащить силой.
7. **Mine rescue event:** `mailHarveyAfterMineRescue` — без «приду сам».

### Не входило / P1-остаток

- Legacy romance/control mails в `mail.json` (`LoveConfession`, `FuturePlans`, `WinterHealthTips`, `ComfortLetter`, …) — **нет активных триггеров**, но ключи остаются в Data/Mail; при появлении триггеров — split по Dating/Married или удаление.
- `mailHarveyRecoveryFinal*` — Dating-gated в events; тексты romantic OK.
- Синхронизация `HarveyOverhaulInjury/assets/data/*.json` с CP — не делали (CP Late override).

---

## P0/P1 — events*.json (2026-05-25)

**Цель:** события развивают отношения постепенно; gate + тон + escape hatch + короткая POV фермерши.

### Изменённые файлы

| Файл | Gate | Текст / структура |
|------|------|-------------------|
| `assets/Code/eventsCare.json` | — | **да** — ранние визиты, exhaustion, mine intercept |
| `assets/Code/eventsMineRescue.json` | — | **да** — ungated rescue → «Вы»; Dating rescue смягчён |
| `assets/Code/events.json` | **да** — `eventHarveyFirstWalk` +750 FP | **да** — приоритетные сцены ниже |

`events_for_mode_new_formatted.json` — **не подключён** в `content.json`; не трогали.

### Gate (условия триггеров)

| Событие | Было | Стало |
|---------|------|-------|
| `eventHarveyFirstWalk` | только `DAYS_PLAYED 11` | **+ `Friendship Harvey 750`** (3+ ❤, «ты» OK) |
| `eventHarveyMedicalCheck` / `_Dating` | уже split pre-Dating / Dating | без изменений gate |
| `HarveyMod_NightCrisis_*` | уже split PreDating / Dating | без изменений gate |
| `HarveyOverhaulRomance.E1` | Dating only | без изменений |
| `HarveyOverhaulStory.E10+` | pre-Dating / Dating split где нужно | без изменений gate |
| `eventHarveyMineRescue` | ungated fallback | gate не меняли — **только текст «Вы»** |

### Только текст (gate уже был)

| Событие | FP / Relationship | Правки |
|---------|-------------------|--------|
| `eventHarveyFirstVisit`, `eventHarveySecondVisit` | 0–2 ❤ (days 3/7) | «Вы», короткие `message`, без личной привязанности |
| `eventHarveyFirstMeeting` (BusStop) | 0–2 ❤ | «хрупкой» → «бледной» |
| `eventHarveyEmergencyCare`, `eventHarveyExhaustion` | fork/C# | клинический тон, «Вы» где уместно |
| `eventHarveyMineInterception` | Dating Married (trigger) | opt-out `quickQuestion`, без «слово закон» |
| `eventHarveyFirstWalk` | 3+ ❤ (после gate) | убрано «люблю лес» у POV; смягчены ветки walk |
| `eventHarveyTraumaExam` | 2000 FP pre-Dating | «стоп», без «приказ»; ty |
| `HarveyMod_TreatmentPlanMeeting` | 750 FP | «решение за тобой» вместо «никаких поблажек» |
| `HarveyMod_NightCrisis_PreDating` | 1500 FP | `quickQuestion` остаться/осмотр/домой; без «бледная» |
| `HarveyMod_NightCrisis_Dating` | Dating | `quickQuestion` + opt-out |
| `eventHarveyCheckFarmerOutsideAfter22` | Dating | убрано «привяжу к кровати» |
| `528013` balloon (vanilla 10❤) | 2500 FP | убрано «хрупкая девушка» |
| `eventHarveyMineRescue` | ungated | клинический «Вы» |
| `eventHarveyMineRescueDating` | Dating Married | «не отпущу» → opt-out; палата — обсудить план |
| `eventHarveyMinorMineRescue` | Dating Married | смягчён императив |
| `HarveyOverhaulStory.E1` … `E15`, `Romance.E1` | по FP в ключах | **уже** с «Вы»/opt-out в E1–E9; E10+ split — без правок gate |
| `eventRescueOperation` | topicRescueOperation | trauma-сцена уже с opt-out («стоп», «подожду») — без правок |

### HarveyOverhaulStory.E* / Romance.E* (статус)

- **E1–E9:** «Вы» на ранних FP (500–2500), `quickQuestion`, короткие `message` — соответствует гайду.
- **E10_HarveyWasWrong** / `_Dating`: split pre-Dating / Dating — OK.
- **E11–E15, E13 MinesAgreement:** Dating/Married или post-rescue — OK.
- **Romance.E1_NotAnExamDate:** Dating, kiss с `quickQuestion` — OK.

### Smoke-test (events)

1. **День 3–7, 0–2 ❤:** FirstMeeting / FirstVisit / SecondVisit — только «Вы».
2. **11+ день, <750 FP:** FirstWalk **не** должен триггериться.
3. **750+ FP, pre-Dating:** FirstWalk, TreatmentPlanMeeting, NightCrisis_PreDating — ty + выбор.
4. **2000 FP, pre-Dating:** TraumaExam — «стоп», без romance.
5. **Dating:** NightCrisis_Dating, MedicalCheck_Dating, Romance.E1 — warmth + opt-out.
6. **Mine rescue без Dating:** «Вы» в шахте и клинике.
7. **Mine rescue Dating:** без «не отпущу»; можно отказаться от жёсткой палаты (текст).

### P1-остаток (events)

- `eventHarveyCheckHealthFarmer` (Dating): «никуда не денешься» — нужен `quickQuestion` при следующем проходе.
- `eventHarveySkullCavePrevention` (Dating gate): «без меня» — смягчить до договора.
- `eventHarveyTreatmentCollapse`, `eventStayInHospital` — fork без relationship gate; смягчить при появлении триггеров.
- Vanilla balloon: часть реплик всё ещё hyper-care 10❤ — OK для 2b, но без «хрупкая».

---

## P0/P1 — gift reactions (dialoguesHarvey.json) (2026-05-25)

**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Цель:** одна и та же реакция на подарок звучит по-разному на 0–2 / 3–5 / 6–10 pre-Dating / Dating / Married.

### Изменённые файлы

| Файл | Gate | Текст |
|------|------|-------|
| `assets/Code/dialoguesHarvey.json` | **да** — 4 новых CP-блока + Dating override | **да** — 50 ключей × 5 стадий |

### Архитектура слоёв (AcceptGift / AcceptBirthdayGift)

| Слой | When | Обращение | Pet names |
|------|------|-----------|-----------|
| F | `Hearts 0,1,2` | «Вы» | ❌ |
| E | `Hearts 3,4,5` | «ты», тепло | ❌ |
| D | `Hearts 6,7,8,9,10` | «ты», смущение | ❌ |
| C | `Relationship: Dating` | «ты», romance | солнышко, моя девочка (не котёнок/малышка; не «дорогая») |
| B | `Relationship: Married` | «ты», домашняя нежность | котёнок, девочка моя, солнышко |

**Приоритет CP:** Dating/Married перекрывают hearts-блоки при совпадении `Relationship`.

### Что убрано / исправлено

- **Ungated base:** все `AcceptGift_*` / `AcceptBirthdayGift_*` вынесены из блока без `When` (раньше «Вы» на всех ❤).
- **Блоки `Hearts 3–7` и `8–10`:** удалены старые overrides `AcceptGift_(O)432/348` («хрупкая», контроль, «девочка моя» на 8–10).
- **Dating-блок:** заменены 2 ключа на полный набор 50 ключей; убраны «малышка», «люблю бодрствовать ради тебя» в кофе.
- **Добавлен `AcceptGift_(O)395` (кофе)** во все стадии — раньше был только в Dating с romance-маркерами.

### Ключи (50)

`AcceptBirthdayGift_*` (6), `AcceptGift_(O)StardropTea`, `395`, `432`, `348`, `342`, `237`, `196`, `200`, `201`, `610`, `618`, `651`, `614`, `24`, `192`, `18`, `22`, `20`, `78`, `404`, `281`, `257`, `422`, `436`, `438`, `442`, `444`, `349`, `773`, `80`, `72`, `74`, `279`, `373`, `446`, `797`, `346`, `303`, `296`, `396`, `88`, `90`, `2`, `30`.

**Vanilla fallback:** предметы вне списка по-прежнему используют базовые `AcceptGift_Loved/Liked/…` из игры (не в mod CP).

### Smoke-test (gifts)

1. **0–2 ❤:** любой ключ из списка — только «Вы»; нет pet names / «ты».
2. **4 ❤:** «ты», без «солнышко»; кофе — «очень кстати», не romance.
3. **8 ❤ pre-Dating:** теплее («ты всё-таки заметила»), без pet names; вино — без «хрупкая».
4. **Dating:** кофе/энергетик — «солнышко», объятие; без «котёнок»/«малышка» (по гайду Dating).
5. **Married:** «котёнок», «девочка моя», «рядом с кофейником».
6. **Сравнение:** один и тот же `432` на 0 / 4 / 8 / Dating / Married — тексты **разные**.

### Скрипт пересборки

- `scripts/gift_tone_layers.py` — тексты 50×5 (ручные, не auto-replace)
- `scripts/apply_gift_tone_layers.py` — патч JSON с сохранением `//` комментариев

---

## Не входило в P0 (следующие итерации)

- Split блока `Hearts 8,9,10` → 2b без pet names vs Dating (P0-2 в plan) — **gift reactions закрыты**; осталось в **обычных диалогах** romance-блока 8–10 без `When: Dating`
- Разделение 3–5 vs 6–7 внутри блока `Hearts 3,4,5,6,7` (main dialogue)
- Полная ручная вычитка `Recovery_Complete_*` в cure F-слое (единичные ty-остатки)
- `dialoguesHarveyStress.json` при подключении в mod pack

---

## P0/P1 — control / opt-out audit (2026-05-25)

**Основа:** [audit-harvey-control-optout.md](./audit-harvey-control-optout.md)

### Аудит (первый проход)

- Инвентаризация сцен контроля: шахты, сон/curfew, госпитализация, overprotective, darkness therapy, quest starts, dialogue 6–10 ❤
- Для каждой записи: медпротокол vs гиперопека, gate, opt-out, quickQuestion, приоритет P0/P1/OK

### P0 — исправлено

| Файл | Что |
|------|-----|
| `quest_dialogues.json` | Breakdown/Collapse/Despair/Fatigue/Sleep — протокол вместо «живёшь у меня», «без обсуждений», «контролирую», «никаких компромиссов» |
| `dialoguesHarveyStress.json` | base `topicStressDarknessLevel3`, `topicDarknessTherapyStart`, `topicDarknessStep1Complete` — убраны «приказ», «нет выбора», mix «Вы»+«ты» |
| `dialoguesHarveyStress.json` | Hearts 7–10 darkness L3 — «не приму отказа» → согласие пациента + «стоп» |
| `dialoguesHarveyStress.json` | Dating darkness L3 — escape hatch «стоп» / «пространство» |
| `dialoguesHarveyInjury.json` | Hearts 3–5 `topicOverprotectiveMode` — «скажи стоп» |
| `dialoguesHarvey.json` | `Fall_20` (6–10) — рекомендация стационара вместо угрозы госпитализации |
| `eventsCare.json` | `eventHarveySkullCavePrevention` — смягчён финал + QQ «Мне нужно пространство» |
| `eventsCare.json` | `eventHarveyMineInterception` — fix «Вы»/«ты» + QQ «Харви, остановись» |
| `events.json` | `eventHarveyCheckFarmerOutsideAfter22` — QQ «Мне нужно пространство», без topic при отступлении |
| `events.json` | `eventHarveyCheckHealthFarmer` — QQ клиника/пространство/дом; смягчена госпитализация + «стоп» |

### P1 — отложено

- Hospital_Mon–Sun (3–7 weekly): частично смягчены в художественной полировке; остаток season_* weeklies — при следующем проходе
- `timeReaction_VeryLate` Married: явный opt-out в тексте
- `eventHarveyTreatmentCollapse`: QQ «согласна на наблюдение» / «справлюсь дома»

### Smoke-test (control)

1. Quest Despair start на 0–2 ❤ — «наблюдение по протоколу», не «живёшь у меня»
2. Darkness L3 base — только «Вы», есть «стоп»
3. Dating + injury → Mine: нет «Вы думаешь», работает «Харви, остановись»
4. Dating curfew 22:00 — «пространство» завершает event без mandatory topic
5. Dating PlayerKilled — «пространство» / «дома» не ведут в hospital bed scene

---

## Художественная полировка (2026-05-25)

**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Цель:** естественнее речь, меньше шаблонов и театральной драмы в обычных topics; сохранить gates, IDs, event structure, медицинскую точность и тревогу в severe/rescue.

**Не меняли:** `When`, event IDs, `quickQuestion`-структуру, mail IDs, условия триггеров.

### Принципы правки

| Принцип | Было | Стало |
|---------|------|-------|
| Повторы | «не спорь», «прослежу», «не дам тебе», «медицинский факт», «По протоколу» | Короткие императивы с заботой; «скажи, если давлю» / «это забота, не приказ» |
| Драма | Театральные stage directions, «сказочная атмосфера», «смертельно опасно» в бытовых сценах | Конкретика симптомов и действий врача |
| Romance до Dating | «защищу от всех бурь», «эмоционально рядом», «особенная», «всю жизнь» | Профессиональная забота без романтических обещаний |
| Severe / rescue | — | Тревога и срочность **сохранены** (collapse, despair, panic start, `topicHealthDamageSevere`) |
| Обращение | Mix «Вы»/«ты» в ungated quest lines | Ungated quest → «Вы»; hearts 3–7 → «ты» |

### Изменённые файлы

| Файл | Объём |
|------|-------|
| `assets/Code/quest_dialogues.json` | Все `HarveyMod_*` start/progress/complete; weeklies Stress/Fatigue/Breakdown |
| `assets/Code/dialoguesHarvey.json` | Блок 6–10 ❤ (Hospital_Mon–Sun, сезонные, локации); блок 3–7 ❤ (time/location/emotional/situation reactions; Resort/Saloon/Beach/Desert/Hospital weeklies) |
| `assets/Code/dialoguesHarveyInjury.json` | `topicOverprotectiveMode` (0–2 / 3–5 / 6–10) — естественнее, без «протокол» |
| `assets/Code/events.json` | Только текст: curfew — убрано «По протоколу» |

**Не трогали:** `dialoguesHarveyStress.json` (не в pack), Dating/Married pet names, C# injury severe topics с «не спорь» (клиническая срочность), `eventsCare.json` / `eventsMineRescue.json` (уже проходили control/opt-out).

### Примеры (до → после)

- **Hospital_Mon (6–10):** «уверенно проверяет… не спорь… прослежу за каждым шагом» → «*проверяет капельницу* Температура 36.8 — хорошо… Остальное на мне»
- **situationReaction_Exhausted (3–7):** «Не спорь… не дам довести до истощения» → «Это забота, не приказ. Скажи, если нужно пространство»
- **StormProtectionStart:** «защищу от всех бурь / эмоционально рядом» → «при громе — в клинику или позвоните; на связи»
- **DespairInterventionComplete:** «моя любовь / навсегда» → «буду опорой, пока не поверите в себя»

### Smoke-test (полировка)

1. **6–10 ❤, Hospital_*:** забота + медпоказатели, без «не спорь» в каждой реплике
2. **3–7 ❤, locationReaction_Mine:** осмотр без повторяющегося «бледная уставшая девушка»
3. **Quest Fatigue/Sleep на 0–2 ❤:** только «Вы» в complete/weeklies
4. **Dating/Married:** pet names на месте; Resort_Chair Married («девочка моя») не затронут
5. **Severe injury topic (6–10):** `topicHealthDamageSevere` — «не спорь» остаётся (срочность)

### P1-остаток (полировка)

- `spring_*` / `summer_*` / `fall_*` weeklies в блоке 3–7 — частично ещё содержат «прослежу» / «уставшая девушка»
- Seasonal duplicates в блоках 6–10 vs 3–7 (Hospital_Mon побеждает блок 3–7 при Late) — тексты различаются намеренно
- `dialoguesHarveyInjury.json` pre-Dating Hospital/FarmHouse — «прослежу» в post-op сценах (уместно)
- `dialoguesHarveyStress.json` — полировка при подключении в `content.json`

