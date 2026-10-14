# Final technical validation — Harvey tone/control pass

**Дата:** 2026-05-25  
**Скрипт:** `scripts/final_technical_validation.py`  
**Правило:** только технические проверки, без художественных правок.

| Проверка | Статус | Найдено | Исправлено | Нужно вручную |
|----------|--------|---------|------------|---------------|
| 1. JSON валидность | FAIL | eventsAfterHospitalDischarge.json:8:256 Invalid control character at; eventsExternalRescue.json:8:326 Invalid control character at; eventsGotoroForestRescue.json:8:443 Invalid control character at; ev | content.json trailing comma; buffsCure.json trailing comma | dialoguesHarveyCure.json — inline // в Entries (CP OK) |
| 2. When/Condition CP-формат | OK | скалярные When/Condition | — | — |
| 3. Дубли ключей в Entries | OK | 0 | — | — |
| 4. Dating/Married vs Hearts приоритет | WARN | 65 ключей (ungated+Dating) | — | CP Late + When OK если Dating специфичнее |
| 5. Base/fallback 0–2 ❤ | OK | ungated без pet names | — | topic-gated ty — см. manual |
| 6. Mail IDs используются | OK | определено 229, сирот 0 | — | — |
| 7. Event IDs уникальны | OK | 89 entries, 87 unique IDs, 1 с time/cond вариантами | — | дубли ID с разными условиями — штатно (E13 утро/вечер) |
| 8. Friendship gates (500/750/1500/2000/2500) | WARN | 15 non-canonical FP | — | events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical); events.json:HarveyOverhaulStory.E9_CameByHerself Friendship 2200 (non-canonical); events.json:HarveyMod_TreatmentReview |
| 9. Dating/Married events — rel gate | OK | 0 | — | — |
| 10. Pet names вне Dating/Married | WARN | 31 в dialogue | — | dialoguesHarveyCareTrust.json:HarveyCareTrust_TreatmentStart_Low_Married_03 gate=ungated; dialoguesHarveyCareTrust.json:HarveyCareTrust_TreatmentStart_High_Married_02 gate=ungated; dialoguesHarveyCare |
| Include: quest_dialogues.json | WARN | не в content.json | — | подключить или игнорировать |
| Include: dialoguesHarveyStress.json | WARN | закомментирован | — | правки darkness не в игре |
| Include: events_for_mode_new_formatted.json | OK | не подключён (SKIP) | — | — |
| C# mail/event refs | OK | C# не найден в мод-паке | — | только CP/triggers |

## Детали

### Non-canonical Friendship points в events

- events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical)
- events.json:HarveyOverhaulStory.E9_CameByHerself Friendship 2200 (non-canonical)
- events.json:HarveyMod_TreatmentReview Friendship 1000 (non-canonical)
- events.json:eventHarveyMountainDate Friendship 2250 (non-canonical)
- events.json:HarveyOverhaulStory.E3_ForestApothecary Friendship 1000 (non-canonical)
- events.json:HarveyOverhaulStory.E3B_WingPatient Friendship 1000 (non-canonical)
- events.json:HarveyOverhaulStory.E8_BadDayNoReason Friendship 2100 (non-canonical)
- events.json:HarveyOverhaulStory.E4_PierBreath Friendship 1250 (non-canonical)
- events.json:HarveyOverhaulStory.E9_LightInWindow Friendship 2150 (non-canonical)
- events.json:HarveyOverhaulStory.E10_HarveyWasWrong Friendship 2200 (non-canonical)
- events.json:HarveyOverhaulStory.E10_HarveyWasWrong_Dating Friendship 2250 (non-canonical)
- events.json:HarveyOverhaulStory.E12_HarveyIsTired Friendship 2200 (non-canonical)
- events.json:HarveyOverhaulStory.E12_HarveyIsTired_Dating Friendship 2300 (non-canonical)
- events.json:HarveyOverhaulStory.E15_FuturePlan Friendship 2600 (non-canonical)
- events.json:HarveyOverhaulStory.E15_FuturePlan_Married Friendship 2600 (non-canonical)

### Pet names вне Dating/Married (dialogue)

- dialoguesHarveyCareTrust.json:HarveyCareTrust_TreatmentStart_Low_Married_03 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_TreatmentStart_High_Married_02 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_PhaseAdvance_Low_Married_01 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_PhaseAdvance_High_Married_02 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_Recovery_Low_Married_01 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_Recovery_High_Married_02 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_NightVisit_Low_Married_01 gate=ungated
- dialoguesHarveyCareTrust.json:HarveyCareTrust_NightVisit_High_Married_03 gate=ungated
- dialoguesHarveyHiddenInjury.json:HarveyMod_HiddenInjury_Suspected_Generic_Married_03 gate=ungated
- dialoguesHarveyHiddenInjury.json:HarveyMod_HiddenInjury_Suspected_Generic_Married_05 gate=ungated
- dialoguesHarveyHiddenInjury.json:HarveyMod_HiddenInjury_Suspected_Generic_Married_11 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Default_0 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Morning_Default_0 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Morning_Default_3 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Morning_Default_5 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Morning_Stress_4 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Morning_LowStamina_0 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Evening_AfterPerfectPlan_2 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Evening_AfterViolation_3 gate=ungated
- dialoguesHarveySpouseDomestic.json:HarveyMod_Spouse_Farm_Day_Default_1 gate=ungated

### Ty в ungated / 0–2 base (sample)

