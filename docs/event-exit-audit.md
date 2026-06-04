# Аудит выхода из Content Patcher-событий (HarveyOverhaul [CP])

Дата: 2026-06-04. Проверены все файлы с `Target: Data/Events/*`, подключённые в `content.json`:
`events.json`, `eventsCare.json`, `eventsMineRescue.json`, `eventsGotoroForestRescue.json`.

Файл `events_for_mode_new_formatted.json` **не включён** в `content.json` — отмечен отдельно в конце.

## Легенда

| Risk | Значение |
|------|----------|
| **HIGH** | Сюжетно игрок должен быть в другой локации, но событие заканчивается обычным `end` без фиксации позиции |
| **MEDIUM** | Есть `changeLocation`/`warp`, но финальная позиция неочевидна или skip может сломать результат |
| **LOW** | Обычная сцена без переноса, либо корректный `end position` / `end newDay` / `end dialogue` после warp |

## Сводная таблица

| EventId | File | Start location | Story result | Current ending | Skip-safe? | Risk | Recommended fix |
|---------|------|----------------|--------------|----------------|------------|------|-----------------|
| `eventHarveyMineInterception` | `eventsCare.json` | Mine @ 17,7 | перехват в шахте (раны); лечение/осмотр; гроза/укрытие → **Town @ 72,22** | `end position 72 22 (+ changeLocation Town)` | Частично | **HIGH** | После «выведу наверх» добавить `changeLocation Mine` warp у выхода или `end position` у лифта; setSkipActions с тем же warp |
| `acceptWalk` | `events.json` | Farm @ 51,13 | ветка/fork → **Forest @ 51,13** | `end position 51 13 (+ changeLocation Forest)` | Частично | **MEDIUM** | После Forest-сцены: `end position 51 13` или warp обратно на Farm при отказе skip |
| `eventHarveyStormComfortFarm` | `events.json` | Farm @ 64,16 | гроза/укрытие → **Farm (без смены локации)** | `end` | Частично | **MEDIUM** | Ветка «клиника» в quickQuestion делает changeLocation; финальный end на Farm — OK для других веток; для ветки клиники end сразу после warp (без возврата fade) |
| `eventHarveySkullCavePrevention` | `eventsCare.json` | SkullCave @ 5,5 | сцена дня → **SkullCave (без смены локации)** | `end` | Частично | **MEDIUM** | Сюжет «домой», но end в SkullCave; добавить warp/warpOut или changeLocation |
| `eventHarveyMineRescue` | `eventsMineRescue.json` | Mine @ 17,7 | спасение в шахте; обморок; лечение/осмотр → **Hospital @ 20,5** | `end position 20 5 dialogue Harvey \"Как боль? Нужно обезболивающее?$s\" (+ chang` | N/A | **MEDIUM** | Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки |
| `eventHarveyMineRescueDating` | `eventsMineRescue.json` | Mine @ 17,7 | спасение в шахте; обморок; лечение/осмотр → **Hospital @ 20,5** | `end position 20 5 dialogue Harvey \"Если боль усилится — скажи сразу. Я не далек` | N/A | **MEDIUM** | Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки |
| `eventHarveyMinorMineRescue` | `eventsMineRescue.json` | Mine @ 17,7 | спасение в шахте → **Hospital @ 14,6** | `end position 14 6 dialogue Harvey \"Отдыхай. Я загляну позже.$h\" (+ changeLocat` | N/A | **MEDIUM** | Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки |
| `528013` | `events.json` | Town @ 90,72 | ванilla balloon override → **Custom_GrampletonFields_Small @ 22,36** | `end position 16 42 (+ changeLocation Custom_GrampletonFields_Small)` | Да | **LOW** | — |
| `58` | `events.json` | SeedShop @ 14,12 | локальная сцена → **SeedShop (без смены локации)** | `end dialogue Harvey \"Заходи в любое время, если захочешь позаниматься. И... пож` | Да | **LOW** | — |
| `HarveyMod_BirthdayHospital_Dating` | `events.json` | Hospital @ 10,19 | ДР в клинике → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyMod_BirthdayHospital_Friend` | `events.json` | Hospital @ 10,19 | ДР в клинике → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyMod_FirstTreatment` | `events.json` | Hospital @ 4,6 | лечение/осмотр → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyMod_NightCrisis_Dating` | `events.json` | Town @ 37,56 | ночной кризис → клиника; лечение/осмотр → **Hospital @ 10,7** | `end newDay (+ changeLocation Hospital)` | Частично | **LOW** | end newDay после Hospital — штатно; setSkipActions: warp 10 7 + changeLocation Hospital |
| `HarveyMod_NightCrisis_PreDating` | `events.json` | Town @ 37,56 | ночной кризис → клиника; лечение/осмотр → **Hospital @ 10,7** | `end newDay (+ changeLocation Hospital)` | Частично | **LOW** | end newDay после Hospital — штатно; setSkipActions: warp 10 7 + changeLocation Hospital |
| `HarveyMod_TreatmentPlanMeeting` | `events.json` | Hospital @ 5,5 | лечение/осмотр → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulRomance.E1_NotAnExamDate` | `events.json` | Beach @ 26,18 | сюжетная арка доверия; романтическая арка → **Beach (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E10_HarveyWasWrong` | `events.json` | Town @ 26,22 | сюжетная арка доверия → **Town (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E10_HarveyWasWrong_Dating` | `events.json` | Town @ 26,22 | сюжетная арка доверия → **Town (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E11_HomeSafetyProtocol` | `events.json` | FarmHouse @ 11,6 | сюжетная арка доверия → **FarmHouse (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E12_HarveyIsTired` | `events.json` | Hospital @ -1000,-1000 | сюжетная арка доверия → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E12_HarveyIsTired_Dating` | `events.json` | Hospital @ -1000,-1000 | сюжетная арка доверия → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E13_MinesAgreement` | `events.json` | BusStop @ 22,23 | спасение в шахте; сюжетная арка доверия → **BusStop (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E13_MinesAgreement` | `events.json` | BusStop @ 22,23 | спасение в шахте; сюжетная арка доверия → **BusStop (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E14_NotOnlyPatient` | `events.json` | Forest @ 32,30 | сюжетная арка доверия; романтическая арка → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E15_FuturePlan` | `events.json` | FarmHouse @ 11,6 | обморок; лечение/осмотр; сюжетная арка доверия → **FarmHouse (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E15_FuturePlan_Married` | `events.json` | FarmHouse @ 11,6 | обморок; лечение/осмотр; сюжетная арка доверия → **FarmHouse (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E1_SlipperyPath` | `events.json` | BusStop @ 7,23 | сюжетная арка доверия → **BusStop (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E2B_QuietAgreement` | `events.json` | Town @ 37,58 | сюжетная арка доверия → **Town (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E2_InsistentExam` | `events.json` | Hospital @ 5,10 | сюжетная арка доверия → **Hospital (без смены локации)** | `end dialogue Harvey \"Завтра — пирс, после шести. Я буду ждать.$0\"` | Да | **LOW** | — |
| `HarveyOverhaulStory.E3B_WingPatient` | `events.json` | Forest @ 48,14 | сюжетная арка доверия → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E3_ForestApothecary` | `events.json` | Forest @ 50,13 | сюжетная арка доверия → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E4B_TooQuiet` | `events.json` | Mountain @ 42,21 | сюжетная арка доверия → **Mountain (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E4_PierBreath` | `events.json` | Beach @ 40,17 | сюжетная арка доверия → **Beach (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E5_StormBeside` | `events.json` | Hospital @ 10,19 | гроза/укрытие; сюжетная арка доверия → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E6_SayItOutLoud` | `events.json` | Hospital @ 10,19 | сюжетная арка доверия → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E7_DoorSignal` | `events.json` | Farm @ 64,16 | сюжетная арка доверия → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E7_TownSip_Sunny` | `events.json` | Town @ 26,22 | сюжетная арка доверия → **Town (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E8_BadDayNoReason` | `events.json` | Forest @ 48,14 | сюжетная арка доверия → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E8_QuietShelf` | `events.json` | ArchaeologyHouse @ 16,9 | сюжетная арка доверия → **ArchaeologyHouse (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E9_CameByHerself` | `events.json` | Hospital @ -1000,-1000 | обморок; лечение/осмотр; сюжетная арка доверия → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `HarveyOverhaulStory.E9_LightInWindow` | `events.json` | Town @ 35,88 | сюжетная арка доверия → **Town (без смены локации)** | `end` | Да | **LOW** | — |
| `declineFood` | `events.json` | BusStop (message \"Спасибо, но я справлюсь с) | ветка/fork → **BusStop (без смены локации)** | `end dialogue Harvey \"Берегите себя. Увидимся!$l\"` | N/A | **LOW** | — |
| `eventHarveyCareMovementAnimationTest` | `events.json` | Hospital @ 5,6 | обморок → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyCheckFarmerOutsideAfter22` | `events.json` | Farm @ 64,16 | обморок → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyCheckHealthFarmer` | `events.json` | Farm @ 64,16 | сцена дня → **Hospital @ 20,5** | `end position 20 5 dialogue Harvey \"Если увижу, что ты взяла кирку — вызову сани` | Да | **LOW** | — |
| `eventHarveyFirstDate` | `events.json` | Forest @ 65,38 | локальная сцена → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyFirstMeeting` | `events.json` | BusStop @ 20,23 | лечение/осмотр; знакомство → **BusStop (без смены локации)** | `end dialogue Harvey \"Рад был познакомиться. Отдыхайте хорошо.$l\"` | Да | **LOW** | — |
| `eventHarveyFirstWalk` | `events.json` | Farm @ 64,16 | сцена дня → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyLateNightCollapse` | `events.json` | Town @ 37,59 | ночной коллапс → капельница → **Hospital @ 20,5** | `end position 20 5 dialogue Harvey \"Спокойной ночи... хотя сейчас уже утро.$s\" ` | Да | **LOW** | — |
| `eventHarveyMedicalCheck` | `events.json` | Hospital @ 10,19 | медосмотр → **Hospital (без смены локации)** | `end dialogue Harvey \"Ты становишься сильнее с каждым днём... Пока постарайся не` | Да | **LOW** | — |
| `eventHarveyMedicalCheck_Dating` | `events.json` | Hospital @ 10,19 | медосмотр → **Hospital (без смены локации)** | `end dialogue Harvey \"Ты становишься сильнее с каждым днём... Я рядом, если пона` | Да | **LOW** | — |
| `eventHarveyMorningCheckup` | `events.json` | Farm @ 64,16 | медосмотр → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyMountainDate` | `events.json` | Mountain @ 41,19 | локальная сцена → **Mountain (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyPropose` | `events.json` | Beach @ 40,7 | локальная сцена → **Beach (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyRoomCheckup` | `events.json` | HarveyRoom @ 1000,1000 | медосмотр → **HarveyRoom (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyRoomCheckup2` | `events.json` | HarveyRoom @ 1000,1000 | медосмотр → **HarveyRoom (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyStormComfortDesert` | `events.json` | Desert @ 15,23 | гроза/укрытие → **Desert (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyStormComfortForest` | `events.json` | Forest @ 23,13 | гроза/укрытие → **Forest (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyStormComfortMine` | `events.json` | Mine @ 15,5 | гроза/укрытие → **Town @ 72,22** | `end position 72 22 (+ changeLocation Town)` | Да | **LOW** | — |
| `eventHarveyStormComfortMountain` | `events.json` | Custom_AdventurerSummit @ 41,28 | гроза/укрытие → **Mountain @ 79,1** | `end position 79 1 (+ changeLocation Mountain)` | Да | **LOW** | — |
| `eventHarveyStormComfortTown` | `events.json` | Town @ 39,73 | гроза/укрытие → **Saloon @ 14,23** | `end position 14 23 (+ changeLocation Saloon)` | Да | **LOW** | — |
| `eventHarveyTraumaExam` | `events.json` | Hospital @ 5,6 | локальная сцена → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveyTreatmentCollapse` | `events.json` | Hospital @ 1000,1000 | принудительная госпитализация; обморок; лечение/осмотр → **Hospital @ 14,6** | `end position 14 6 (+ changeLocation Hospital)` | Частично | **LOW** | — |
| `eventRescueOperation` | `events.json` | Woods @ 1000,1000 | спасение после ДТП/лес; гроза/укрытие → **Hospital @ 20,5** | `end position 20 5 (+ changeLocation Hospital)` | Да | **LOW** | — |
| `eventStayInHospital` | `events.json` | Hospital @ 9,16 | локальная сцена → **Hospital (без смены локации)** | `end` | Да | **LOW** | — |
| `refuseCheckup` | `events.json` | BusStop (speak Harvey \"*кивает с пониманием) | медосмотр → **BusStop (без смены локации)** | `end dialogue Harvey \"Берегите себя. Увидимся!$l\"` | N/A | **LOW** | — |
| `HarveySkullPromise` | `eventsCare.json` | SkullCave (speak Harvey \"Ресурсы?!$a#$b#Твоя ) | ветка/fork → **SkullCave (без смены локации)** | `end` | N/A | **LOW** | — |
| `declineFood` | `eventsCare.json` | BusStop (message \"Спасибо, но я справлюсь с) | ветка/fork → **BusStop (без смены локации)** | `end dialogue Harvey \"Берегите себя. Увидимся!$l\"` | N/A | **LOW** | — |
| `eventHarveyCheckup` | `eventsCare.json` | Hospital @ 4,6 | медосмотр; знакомство → **Hospital @ 10,17** | `end position 10 17` | Да | **LOW** | — |
| `eventHarveyEmergencyCare` | `eventsCare.json` | Hospital @ 1000,1000 | принудительная госпитализация → **Hospital @ 14,6** | `end (+ changeLocation Hospital)` | N/A | **LOW** | — |
| `eventHarveyExhaustion` | `eventsCare.json` | Hospital @ 1000,1000 | принудительная госпитализация → **Hospital @ 20,5** | `end (+ changeLocation Hospital)` | N/A | **LOW** | — |
| `eventHarveyFirstMeeting` | `eventsCare.json` | BusStop @ 20,23 | лечение/осмотр; знакомство → **BusStop (без смены локации)** | `end dialogue Harvey \"Рад был познакомиться. Отдыхайте хорошо.$l\"` | Да | **LOW** | — |
| `eventHarveyFirstVisit` | `eventsCare.json` | Farm @ 64,16 | знакомство → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `eventHarveySecondVisit` | `eventsCare.json` | Farm @ 64,16 | знакомство → **Farm (без смены локации)** | `end` | Да | **LOW** | — |
| `irregularEating` | `eventsCare.json` | Hospital (message \"Иногда забываю поесть... ) | ветка/fork → **Hospital @ 10,17** | `end position 10 17` | Да | **LOW** | — |
| `refuseCheckup` | `eventsCare.json` | BusStop (speak Harvey \"*кивает с пониманием) | медосмотр → **BusStop (без смены локации)** | `end dialogue Harvey \"Берегите себя. Увидимся!$l\"` | N/A | **LOW** | — |
| `HarveyStress_GotoroForestRescue_Dating` | `eventsGotoroForestRescue.json` | Forest @ -1,-1 | Gotoro flashback в лесу → **Forest (без смены локации)** | `end dialogue Harvey \"Я подожду столько, сколько нужно. Когда будешь готов$0^Ког` | Да | **LOW** | — |
| `HarveyStress_GotoroForestRescue_HighTrust` | `eventsGotoroForestRescue.json` | Forest @ -1,-1 | гроза/укрытие; Gotoro flashback в лесу → **Forest (без смены локации)** | `end dialogue Harvey \"Когда отпустит — зайди ко мне. Мы разберёмся без спешки.\"` | Да | **LOW** | — |
| `HarveyStress_GotoroForestRescue_Married` | `eventsGotoroForestRescue.json` | Forest @ -1,-1 | гроза/укрытие; Gotoro flashback в лесу → **Forest (без смены локации)** | `end dialogue Harvey \"Когда будешь готов$0^Когда будешь готова$1 — поговорим дом` | Да | **LOW** | — |
| `HarveyStress_GotoroForestRescue_MidTrust` | `eventsGotoroForestRescue.json` | Forest @ -1,-1 | Gotoro flashback в лесу → **Forest (без смены локации)** | `end dialogue Harvey \"Когда будете готовы — зайдите в клинику. Сейчас вам не нуж` | Да | **LOW** | — |
| `eventHarveyMineRescueMorning` | `eventsMineRescue.json` | FarmHouse (continue — текущая позиция) | спасение в шахте; лечение/осмотр → **FarmHouse (кровать)** | `end dialogue Harvey \"Как боль? Нужно обезболивающее?$s\"` | N/A | **LOW** | Сюжет: пробуждение дома (ветка если C# не сделал warp в шахте); согласовать текст с фактической локацией |
| `eventHarveyMineRescueMorningDating` | `eventsMineRescue.json` | FarmHouse (continue — текущая позиция) | спасение в шахте; обморок; лечение/осмотр → **FarmHouse (без смены локации)** | `end dialogue Harvey \"Если боль усилится — сразу позови. Я не далеко.$u\"` | N/A | **LOW** | Сюжет: пробуждение дома (ветка если C# не сделал warp в шахте); согласовать текст с фактической локацией |

**Всего событий:** 82 (HIGH: 1, MEDIUM: 6, LOW: 75)

## Приоритетные находки

### Спасение из шахты / госпитализация

- **`eventHarveyMineRescue`** (eventsMineRescue.json): MEDIUM — Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки
- **`eventHarveyMineRescueDating`** (eventsMineRescue.json): MEDIUM — Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки
- **`eventHarveyMinorMineRescue`** (eventsMineRescue.json): MEDIUM — Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки
- **`eventHarveyMineRescueMorning`** (eventsMineRescue.json): LOW — Сюжет: пробуждение дома (ветка если C# не сделал warp в шахте); согласовать текст с фактической локацией
- **`eventHarveyMineInterception`** (eventsCare.json): HIGH — После «выведу наверх» добавить `changeLocation Mine` warp у выхода или `end position` у лифта; setSkipActions с тем же warp
- **`eventHarveyMineRescueMorningDating`** (eventsMineRescue.json): LOW — Сюжет: пробуждение дома (ветка если C# не сделал warp в шахте); согласовать текст с фактической локацией

### Обморок / коллапс / принудительная клиника

- **`eventHarveyEmergencyCare`** (eventsCare.json): LOW — —
- **`eventHarveyExhaustion`** (eventsCare.json): LOW — —
- **`eventHarveyTreatmentCollapse`** (events.json): LOW — —
- **`eventHarveyLateNightCollapse`** (events.json): LOW — —
- **`eventHarveyCheckHealthFarmer`** (events.json): LOW — —
- **`eventHarveyTreatmentCollapse`** (events.json): LOW — —
- **`eventStayInHospital`** (events.json): LOW — —

### Спасение / перенос в клинику (сюжет)

- **`eventRescueOperation`** (events.json): LOW — —
- **`HarveyMod_NightCrisis_Dating`** (events.json): LOW — end newDay после Hospital — штатно; setSkipActions: warp 10 7 + changeLocation Hospital
- **`HarveyMod_NightCrisis_PreDating`** (events.json): LOW — end newDay после Hospital — штатно; setSkipActions: warp 10 7 + changeLocation Hospital

### Гроза / changeLocation

- **`eventHarveyStormComfortFarm`** (events.json): MEDIUM — Ветка «клиника» в quickQuestion делает changeLocation; финальный end на Farm — OK для других веток; для ветки клиники end сразу после warp (без возврата fade)
- **`eventHarveyStormComfortMine`** (events.json): LOW — —
- **`eventHarveyStormComfortDesert`** (events.json): LOW — —

## Примечания по механике SDV

1. Обычный `end` после `changeLocation` + `warp farmer` **обычно** оставляет игрока в новой локации, если warp успел выполниться.
2. При **skip** (`skippable` без `setSkipActions`) все команды после точки пропуска не выполняются → игрок остаётся в **стартовой** локации триггера.
3. `end dialogue` / `end position X Y` / `end newDay` явнее фиксируют финальное состояние.
4. События с ключом `continue/` используют текущую позицию игрока; риск ниже, если нет `changeLocation`.
5. `eventHarveyEmergencyCare` / `eventHarveyExhaustion` вызываются из C# (Injury) — триггерная локация может не совпадать с Data/Events/Hospital.
