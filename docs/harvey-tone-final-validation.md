# Final technical validation — Harvey tone/control pass

**Дата:** 2026-05-25  
**Скрипт:** `scripts/final_technical_validation.py`  
**Правило:** только технические проверки, без художественных правок.

| Проверка | Статус | Найдено | Исправлено | Нужно вручную |
|----------|--------|---------|------------|---------------|
| 1. JSON валидность | FAIL | buffsInjury.json:30:42 Expecting property name enclosed in double quotes; dialoguesHarveyCure.json:1117:22 Expecting ',' delimiter | content.json trailing comma; buffsCure.json trailing comma | dialoguesHarveyCure.json — inline // в Entries (CP OK) |
| 2. When/Condition CP-формат | OK | скалярные When/Condition | — | — |
| 3. Дубли ключей в Entries | FAIL | events.json:/GameStateQuery !PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulStory.E13_MinesAgreement/GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current HarveyMod_CD_Global/GameStateQuery !PLAYER_HAS_C | — | разделить блоки |
| 4. Dating/Married vs Hearts приоритет | WARN | 107 ключей (ungated+Dating) | — | CP Late + When OK если Dating специфичнее |
| 5. Base/fallback 0–2 ❤ | OK | ungated без pet names | — | topic-gated ty — см. manual |
| 6. Mail IDs используются | OK | определено 159, сирот 0 | — | — |
| 7. Event IDs уникальны | OK | 58 entries, 56 unique IDs, 1 с time/cond вариантами | — | дубли ID с разными условиями — штатно (E13 утро/вечер) |
| 8. Friendship gates (500/750/1500/2000/2500) | WARN | 15 non-canonical FP | — | events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical); events.json:HarveyMod_TreatmentReview Friendship 1000 (non-canonical); events.json:eventHarveyMountainDate Friendship 2 |
| 9. Dating/Married events — rel gate | OK | 0 | — | — |
| 10. Pet names вне Dating/Married | OK | 0 | — | — |
| Include: quest_dialogues.json | WARN | не в content.json | — | подключить или игнорировать |
| Include: dialoguesHarveyStress.json | WARN | закомментирован | — | правки darkness не в игре |
| Include: events_for_mode_new_formatted.json | OK | не подключён (SKIP) | — | — |
| C# mail/event refs | OK | C# не найден в мод-паке | — | только CP/triggers |

## Детали

### Non-canonical Friendship points в events

- events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical)
- events.json:HarveyMod_TreatmentReview Friendship 1000 (non-canonical)
- events.json:eventHarveyMountainDate Friendship 2250 (non-canonical)
- events.json:HarveyOverhaulStory.E3_ForestApothecary Friendship 1000 (non-canonical)
- events.json:HarveyOverhaulStory.E3B_WingPatient Friendship 1000 (non-canonical)
- events.json:HarveyOverhaulStory.E8_BadDayNoReason Friendship 2250 (non-canonical)
- events.json:HarveyOverhaulStory.E4_PierBreath Friendship 1250 (non-canonical)
- events.json:HarveyOverhaulStory.E9_LightInWindow Friendship 2250 (non-canonical)
- events.json:HarveyOverhaulStory.E10_HarveyWasWrong Friendship 2750 (non-canonical)
- events.json:HarveyOverhaulStory.E10_HarveyWasWrong_Dating Friendship 2750 (non-canonical)
- events.json:HarveyOverhaulStory.E12_HarveyIsTired Friendship 3250 (non-canonical)
- events.json:HarveyOverhaulStory.E12_HarveyIsTired_Dating Friendship 3250 (non-canonical)
- events.json:HarveyOverhaulStory.E14_NotOnlyPatient Friendship 4000 (non-canonical)
- events.json:HarveyOverhaulStory.E15_FuturePlan Friendship 4500 (non-canonical)
- events.json:HarveyOverhaulStory.E15_FuturePlan_Married Friendship 4500 (non-canonical)

### Pet names вне Dating/Married (dialogue)

- не найдено в активных dialogue-блоках

### Ty в ungated / 0–2 base (sample)

