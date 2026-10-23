# Проверка постановки событий — 23 октября 2026

Проверены **204 записей** (184 уникальных ID, включая 8 продолжений `fork`), **27 локаций**, все ветки `quickQuestion` и подключённые условия/варианты. Изменено **92 записей в 18 файлах**. В счётчик входят условные варианты одной сцены и спасения, подключённые одновременно к Forest и Woods.

## Что исправлено

- Медицинские осмотры: убраны длинные проходы через кабинет, перенос в палату происходит под затемнением; посадка на стул использует финальный тайл (5,4), остановку анимации и направление 2 перед кадром 107. Мару объявлена и расставлена в двух сценах, где она отвечает врачу.
- У клиники: E9_LightInWindow перенесено с лесистого юга Town (35,88) к действительной двери клиники (36,56); исправлены ответвления E6 и маршрут к лавкам в E7_TownSip.
- Пляж: предложение проходит на песке (37,24)/(38,24), без маршрута через воду и остановки `advancedMove` посреди пути. Реплики согласованы с прогулкой вдоль берега.
- Комната Харви: движения от двери выполняются последовательно. Второй осмотр получил короткое отступление в свободной части комнаты, выбор между проверкой пульса и чаем, без прохода к стене/окну. Проверены SVE и три SVE-варианта Off The Clock.
- Ферма: абсолютные токены Farm больше не складываются с автоматическим сдвигом событий. В садовой сцене Харви появляется отдельно от Аренда.
- Домашние визиты: исправлены заголовки восьми сцен. C# собирает корректный заголовок, сохраняет фактическое положение игрока, выбирает свободный тайл для Харви и направляет камеру на игрока. Учтены объекты, мебель, NPC и непроходимые terrain features; проходимые ковры и трава не блокируют визит.
- Спасения в лесу: Харви создаётся на карте рядом с игроком независимо от своего расписания; убрано смещение на 64 px, которое могло сдвинуть его в препятствие. Исправлен тот же резервный C#-сценарий.
- Удалены команды вида `--animate` и `stopIgnoringCollisions`, исправлен порядок аргументов `showFrame` и вопрос перед `fork`. Ожидания движения и остановки поз добавляет общий `event_staging.py`; генераторы используют его при повторной сборке событий.
- У домашних сцен пропуск теперь сохраняет предусмотренные темы, письма, предметы и дружбу.

## Проверки

- `scripts/check_all.py`: все 12 групп прошли.
- `scripts/test_event_staging.py`: 14 регрессионных тестов, включая ответвления, унаследованную расстановку fork, промежуточные тайлы advancedMove, кадры, позы и повторный запуск нормализатора.
- `scripts/validate_event_staging.py`: 204 записей, 27 локаций, **0 замечаний**.
- Кадры Харви проверены по обычному, зимнему спрайту и белому халату; анимационные кадры не выходят за границы и не пусты.
- Core и модули Injury/Stress собраны без ошибок и предупреждений. Консольные проверки Core: **823 проверки**, включая заголовок, динамическую камеру, направление Харви и сохранение `/` в реплике.
- Все шесть собственных TMX-карт загружены установленным `TMXTile.dll`: 15 действий, 4 проходимых двери.

Проверка основана на установленных SVE/Alchemistry, стандартной и Frontier Farm, домах уровней 0–2 и супружеских вариантах. Статическая проверка использует геометрию слоёв карт; C# выбирает место домашнего/лесного визита по загруженной карте и обстановке. Проигрывание сцен в конкретном игровом сохранении не выполнялось.

## Прогон в игре

После установки архива и перезапуска SMAPI проверить осмотры в Hospital и обе ветки остановки осмотра; E7_TownSip и E9_LightInWindow; оба домашних осмотра; предложение на пляже; домашний визит в улучшенном доме с мебелью; спасение в Forest и Woods, когда Харви находится в другой локации. Для каждой группы проверить обычное завершение и пропуск. Отдельно посмотреть положение спрайта на стуле и на кровати, появление Мару, камеру и возврат управления.

## Полный охват

| Файл | ID | Карта | Результат |
|---|---|---|---|
| goodWeek.json | `HarveyOverhaulGoodWeek.GW1_Picnic` | Farm | Исправлено |
| clinicSeasonal.json | `HarveyOverhaulClinic.V1_VaccineDay` | Hospital | Проверено |
| clinicSeasonal.json | `HarveyOverhaulClinic.HS1_Heatstroke` | Hospital | Проверено |
| clinicSeasonal.json | `HarveyOverhaulClinic.MS1_Mushrooms` | Hospital | Проверено |
| clinicSeasonal.json | `HarveyOverhaulClinic.IC1_IceFall` | Hospital | Проверено |
| fatherhood.json | `HarveyOverhaulFather.P1_FirstNight` | FarmHouse | Проверено |
| fatherhood.json | `HarveyOverhaulFather.P2_BabyMonitor` | Hospital | Проверено |
| familyLife.json | `HarveyOverhaulFamily.G1_Birds` | Forest | Проверено |
| familyLife.json | `HarveyOverhaulFamily.G2_Toy` | FarmHouse | Проверено |
| familyLife.json | `HarveyOverhaulFamily.G3_Drawing` | FarmHouse | Проверено |
| familyLife.json | `HarveyOverhaulClinic.FA1_FirstAid` | Hospital | Проверено |
| familyLife.json | `HarveyOverhaulAnniversary.A2_Kitchen` | FarmHouse | Проверено |
| familyLife.json | `HarveyOverhaulAnniversary.A3_Together` | FarmHouse | Проверено |
| familyLife.json | `HarveyOverhaulAnniversary.A3_Together` | FarmHouse | Проверено |
| outings.json | `HarveyOverhaulBirthday.B1_Celebration` | HarveyCelebrationRoom | Проверено |
| outings.json | `HarveyOverhaulBirthday.B1_Celebration` | HarveyCelebrationRoom | Проверено |
| outings.json | `HarveyOverhaulBirthday.B1_Celebration` | HarveyCelebrationRoom | Проверено |
| outings.json | `HarveyOverhaulBirthday.B1_Celebration` | HarveyCelebrationRoom | Проверено |
| outings.json | `HarveyOverhaulBirthday.B1_Celebration` | HarveyCelebrationRoom | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z1_Arrival` | HarveyZuzuSquare | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z2_Coffee` | HarveyZuzuCafe | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z3_Bookshop` | HarveyZuzuBooks | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z5_HotelEvening` | HarveyZuzuInn | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z6_SundayMorning` | HarveyZuzuInn | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z7_EveningSquare` | HarveyZuzuSquare | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z4_University` | HarveyZuzuCampus | Проверено |
| outings.json | `HarveyOverhaulZuzu.Z4_University` | HarveyZuzuCampus | Проверено |
| arend.json | `HarveyOverhaulArend.H6_Lecture` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.P1_TwoStethoscopes` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.A0_Letter` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.S2_StormPlan` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.A0_Letter` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.S2_StormPlan` | Hospital | Проверено |
| arend.json | `HarveyOverhaulArend.A1_Arrival` | BusStop | Проверено |
| arend.json | `HarveyOverhaulArend.F1_Suitcase` | BusStop | Проверено |
| arend.json | `HarveyOverhaulArend.A2_RoomWithoutWalls` | Forest | Проверено |
| arend.json | `HarveyOverhaulArend.P2_Window` | Forest | Проверено |
| arend.json | `HarveyOverhaulArend.A2_RoomWithoutWalls` | Forest | Проверено |
| arend.json | `HarveyOverhaulArend.P2_Window` | Forest | Проверено |
| arend.json | `HarveyOverhaulArend.H2_Chess` | Town | Проверено |
| arend.json | `HarveyOverhaulArend.H8_ImFine` | Town | Проверено |
| arend.json | `HarveyOverhaulArend.S1_Box` | Town | Проверено |
| arend.json | `HarveyOverhaulArend.S1_Box` | Town | Проверено |
| arend.json | `HarveyOverhaulArend.H4_Album` | HarveyRoom | Проверено |
| arend.json | `HarveyOverhaulArend.S3_PaperBoats` | Beach | Проверено |
| arend.json | `HarveyOverhaulArend.S3_PaperBoats` | Beach | Проверено |
| arend.json | `HarveyOverhaulArend.W1_ElinsCup` | Farm | Исправлено |
| arend.json | `HarveyOverhaulArend.P3_ElinsGarden` | Farm | Исправлено |
| eventsHarveyEvenings.json | `{{ModId}}_eventHarveyEveningRadio` | HarveyRoom | Исправлено |
| eventsHarveyEvenings.json | `{{ModId}}_eventHarveyEveningPlanes` | HarveyRoom | Исправлено |
| eventsHarveyEvenings.json | `{{ModId}}_eventHarveyEveningJournal` | HarveyRoom | Исправлено |
| events.json | `eventHarveyFirstWalk` | Farm | Исправлено |
| events.json | `acceptWalk` | Farm | Исправлено |
| events.json | `eventHarveyCheckHealthFarmer` | Farm | Исправлено |
| events.json | `eventHarveyCheckFarmerOutsideAfter22` | Farm | Исправлено |
| events.json | `eventHarveyMorningCheckup` | Farm | Исправлено |
| events.json | `eventHarveyStormComfortFarm` | Farm | Исправлено |
| events.json | `HarveyOverhaulStory.E7_DoorSignal` | Farm | Исправлено |
| events.json | `HarveyOverhaulStory.E5_StormBeside` | Hospital | Проверено |
| events.json | `HarveyOverhaulStory.E6_SayItOutLoud` | Hospital | Исправлено |
| events.json | `HarveyOverhaulStory.E9_CameByHerself` | Hospital | Исправлено |
| events.json | `eventHarveyMedicalCheck_Dating` | Hospital | Исправлено |
| events.json | `eventHarveyMedicalCheck` | Hospital | Исправлено |
| events.json | `eventHarveyTreatmentCollapse` | Hospital | Исправлено |
| events.json | `eventStayInHospital` | Hospital | Проверено |
| events.json | `HarveyMod_TreatmentPlanMeeting` | Hospital | Исправлено |
| events.json | `HarveyOverhaulStory.E2_InsistentExam` | Hospital | Исправлено |
| events.json | `HarveyMod_FirstTreatment` | Hospital | Исправлено |
| events.json | `HarveyMod_BirthdayHospital_Dating` | Hospital | Исправлено |
| events.json | `HarveyMod_BirthdayHospital_Friend` | Hospital | Исправлено |
| events.json | `58` | SeedShop | Исправлено |
| events.json | `eventRescueOperation` | Woods | Исправлено |
| events.json | `HarveyOverhaulStory.E4B_TooQuiet` | Mountain | Проверено |
| events.json | `eventHarveyMountainDate` | Mountain | Проверено |
| events.json | `eventHarveyStormComfortMountain` | Custom_AdventurerSummit | Проверено |
| events.json | `HarveyMod_NightCrisis_Dating` | Town | Проверено |
| events.json | `HarveyMod_NightCrisis_PreDating` | Town | Проверено |
| events.json | `HarveyOverhaulStory.E2B_QuietAgreement` | Town | Исправлено |
| events.json | `HarveyOverhaulStory.E7_TownSip_Sunny` | Town | Исправлено |
| events.json | `eventHarveyLateNightCollapse` | Town | Исправлено |
| events.json | `528013` | Town | Исправлено |
| events.json | `eventHarveyStormComfortTown` | Town | Исправлено |
| events.json | `HarveyOverhaulStory.E1_SlipperyPath` | BusStop | Исправлено |
| events.json | `eventHarveyRoomCheckup` | HarveyRoom | Исправлено |
| events.json | `eventHarveyRoomCheckup2` | HarveyRoom | Исправлено |
| events.json | `HarveyOverhaulStory.E3_ForestApothecary` | Forest | Проверено |
| events.json | `HarveyOverhaulStory.E3B_WingPatient` | Forest | Проверено |
| events.json | `HarveyOverhaulStory.E8_BadDayNoReason` | Forest | Исправлено |
| events.json | `eventHarveyFirstDate` | Forest | Проверено |
| events.json | `eventHarveyStormComfortForest` | Forest | Исправлено |
| events.json | `HarveyOverhaulStory.E4_PierBreath` | Beach | Проверено |
| events.json | `eventHarveyPropose` | Beach | Исправлено |
| events.json | `HarveyOverhaulStory.E8_QuietShelf` | ArchaeologyHouse | Проверено |
| events.json | `HarveyOverhaulStory.E9_LightInWindow` | Town | Исправлено |
| events.json | `HarveyOverhaulStory.E10_HarveyWasWrong` | Town | Проверено |
| events.json | `HarveyOverhaulStory.E10_HarveyWasWrong_Dating` | Town | Проверено |
| events.json | `HarveyOverhaulStory.E11_HomeSafetyProtocol` | FarmHouse | Проверено |
| events.json | `HarveyOverhaulStory.E12_HarveyIsTired` | Hospital | Исправлено |
| events.json | `HarveyOverhaulStory.E12_HarveyIsTired_Dating` | Hospital | Исправлено |
| events.json | `HarveyOverhaulRomance.E1_NotAnExamDate` | Beach | Исправлено |
| events.json | `HarveyOverhaulStory.E13_MinesAgreement` | BusStop | Проверено |
| events.json | `HarveyOverhaulStory.E13_MinesAgreement` | BusStop | Проверено |
| events.json | `HarveyOverhaulStory.E14_NotOnlyPatient` | Forest | Исправлено |
| events.json | `HarveyOverhaulStory.E15_FuturePlan` | FarmHouse | Проверено |
| events.json | `HarveyOverhaulStory.E15_FuturePlan_Married` | FarmHouse | Проверено |
| events.json | `eventHarveyStormComfortDesert` | Desert | Исправлено |
| events.json | `eventHarveyStormComfortMine` | Mine | Проверено |
| eventsCare.json | `eventHarveyFirstVisit` | Farm | Исправлено |
| eventsCare.json | `eventHarveySecondVisit` | Farm | Исправлено |
| eventsCare.json | `eventHarveyEmergencyCare` | Hospital | Исправлено |
| eventsCare.json | `eventHarveyExhaustion` | Hospital | Исправлено |
| eventsCare.json | `eventHarveyCheckup` | Hospital | Исправлено |
| eventsCare.json | `irregularEating` | Hospital | Исправлено |
| eventsCare.json | `eventHarveyFirstMeeting` | BusStop | Исправлено |
| eventsCare.json | `declineFood` | BusStop | Проверено |
| eventsCare.json | `refuseCheckup` | BusStop | Проверено |
| eventsCare.json | `eventHarveySkullCavePrevention` | SkullCave | Исправлено |
| eventsCare.json | `HarveySkullPromise` | SkullCave | Исправлено |
| eventsCare.json | `eventHarveyMineInterception` | Mine | Проверено |
| introRecovery.json | `eventHarveyCheckupInvitation` | Hospital | Проверено |
| eventsMineRescue.json | `eventHarveyMineRescue` | Mine | Исправлено |
| eventsMineRescue.json | `eventHarveyMinorMineRescue` | Mine | Исправлено |
| eventsMineRescue.json | `eventHarveyMineRescueDating` | Mine | Исправлено |
| eventsMineRescue.json | `eventHarveyMineRescueMorning` | FarmHouse | Исправлено |
| eventsMineRescue.json | `eventHarveyMineRescueMorningDating` | FarmHouse | Исправлено |
| eventsExternalRescue.json | `eventHarveyAfterExternalRescueHome` | FarmHouse | Исправлено |
| eventsExternalRescue.json | `eventHarveyAfterExternalRescueHomeEngaged` | FarmHouse | Исправлено |
| eventsExternalRescue.json | `eventHarveyAfterExternalRescueHomeMarried` | FarmHouse | Исправлено |
| collapse.json | `PlayerKilled` | Hospital | Исправлено |
| collapse.json | `PlayerKilled` | Hospital | Исправлено |
| eventsAfterHospitalDischarge.json | `eventHarveyAfterHospitalDischargeHome` | FarmHouse | Исправлено |
| eventsNightRoundSevere.json | `eventHarveyNightRoundSevereFirst` | FarmHouse | Исправлено |
| eventsMorningAfterExhaustion.json | `eventHarveyMorningAfterExhaustion` | FarmHouse | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_MidTrust` | Forest | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_HighTrust` | Forest | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_Dating` | Forest | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_Married` | Forest | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_MidTrust` | Woods | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_HighTrust` | Woods | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_Dating` | Woods | Исправлено |
| eventsGotoroForestRescue.json | `HarveyStress_GotoroForestRescue_Married` | Woods | Исправлено |
| eventsTraumaBackstory.json | `eventHarveyTraumaExam` | Hospital | Проверено |
| eventsTraumaBackstory.json | `eventHarveyTraumaExam` | Hospital | Проверено |
| eventsTraumaBackstory.json | `HarveyOverhaulStory.T1_WhatIRemember` | Hospital | Проверено |
| eventsTraumaBackstory.json | `HarveyOverhaulStory.T2_LastOne` | Forest | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N1_NightShift` | Town | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N2_Spring` | Custom_SpriteSpring2 | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N3_ContactCard` | Hospital | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N4_BlueMoon` | Custom_BlueMoonVineyard | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N5_ReversedKit` | Custom_AdventurerSummit | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N5_ReversedKit_Confess` | Custom_AdventurerSummit | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N6_StormCall` | Hospital | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N6_StormCall` | Hospital | Проверено |
| eventsArc3.json | `HarveyOverhaulArc3.N7_Key` | Hospital | Проверено |
| eventsMarriage.json | `HarveyOverhaulDate.D1_Fountain` | Town | Проверено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M1_FirstShift` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M2_SickDay` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M5_Overworked` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M6_HerCold` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M7_LateReturn` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M8_SleeplessNight` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M12_SundayPancakes` | Farm | Исправлено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M9_ForestPharmacy` | Forest | Проверено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M10_FountainDance` | Town | Проверено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M11_BadDay` | Hospital | Проверено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M3_Anniversary` | Beach | Проверено |
| eventsMarriage.json | `HarveyOverhaulMarriage.M4_HarveyBirthday` | Hospital | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A1_LunchBreak` | HarveyRoom | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A4_WhiteCoat` | HarveyRoom | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A2_NightSwim` | Beach | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A3_Downpour` | Farm | Исправлено |
| eventsAdult.json | `HarveyOverhaulAdult.A8_Frozen` | Farm | Исправлено |
| eventsAdult.json | `HarveyOverhaulAdult.A5_ReverseExam` | Hospital | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A6_Vineyard` | Custom_BlueMoonVineyard | Проверено |
| eventsAdult.json | `HarveyOverhaulAdult.A7_NightSpring` | Custom_SpriteSpring2 | Проверено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R1_Umbrella` | Farm | Исправлено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R2_Stars` | Farm | Исправлено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R4_Snowballs` | Farm | Исправлено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R6_ReadingAloud` | Farm | Исправлено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R7_Heartbeat` | Farm | Исправлено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R3_FallLeaves` | Forest | Проверено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R5_ClinicLunch` | Hospital | Проверено |
| eventsMarriageRotation.json | `HarveyOverhaulRotation.R8_FountainWalk` | Town | Проверено |
| festivalsHarvey.json | `HarveyOverhaulFestival.F1_AfterFlowerDance` | Farm | Исправлено |
| festivalsHarvey.json | `HarveyOverhaulFestival.F2_AfterLuau` | Farm | Исправлено |
| festivalsHarvey.json | `HarveyOverhaulFestival.F3_AfterSpiritsEve` | Farm | Исправлено |
| festivalsHarvey.json | `HarveyOverhaulFestival.F4_WinterStarNight` | Farm | Исправлено |
| eventsHarveyLife.json | `HarveyOverhaulLife.H1_Offer` | Hospital | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.H2_Doubts` | Beach | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.H3_Answer` | Town | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.H3_Answer_Go` | Town | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.K1_TwoWars` | Town | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.LW1_LewisSorry` | Town | Проверено |
| eventsHarveyLife.json | `HarveyOverhaulLife.L1_LinusTea` | Mountain | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C1_LongSleeves` | Town | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C2_Pop` | Town | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C3_ScarSalve` | Hospital | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C4_ZuzuLetter` | Hospital | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C6_Stranger` | BusStop | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C7_SleevesUp` | Beach | Проверено |
| eventsScars.json | `HarveyOverhaulScars.C8_Map` | Farm | Исправлено |
| eventsExamConsent.json | `HarveyExam_CheckupStopped` | Hospital | Исправлено |
| eventsExamConsent.json | `HarveyExam_MedCheckStopped` | Hospital | Проверено |
| eventsExamConsent.json | `HarveyExam_MedCheckStoppedDating` | Hospital | Проверено |
