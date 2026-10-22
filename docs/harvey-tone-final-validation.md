# Final technical validation — Harvey tone/control pass

**Дата:** 2026-05-25  
**Скрипт:** `scripts/final_technical_validation.py`  
**Правило:** только технические проверки, без художественных правок.

| Проверка | Статус | Найдено | Исправлено | Нужно вручную |
|----------|--------|---------|------------|---------------|
| 1. JSON валидность | OK | 95 файлов | — | — |
| 2. When/Condition CP-формат | OK | скалярные When/Condition | — | — |
| 3. Дубли ключей в Entries | OK | 0 | — | — |
| 4. Dating/Married vs Hearts приоритет | WARN | 69 ключей (ungated+Dating) | — | CP Late + When OK если Dating специфичнее |
| 5. Base/fallback 0–2 ❤ | OK | ungated без pet names | — | topic-gated ty — см. manual |
| 6. Mail IDs используются | OK | определено 275, сирот 0 | — | — |
| 7. Event IDs уникальны | OK | 256 entries, 188 unique IDs, 51 с time/cond вариантами | — | дубли ID с разными условиями — штатно (E13 утро/вечер) |
| 8. Friendship gates (500/750/1500/2000/2500) | WARN | 15 non-canonical FP | — | events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical); events.json:HarveyOverhaulStory.E9_CameByHerself Friendship 2200 (non-canonical); events.json:HarveyMod_TreatmentReview |
| 9. Dating/Married events — rel gate | OK | 0 | — | — |
| 10. Pet names вне Dating/Married | OK | 0 | — | — |
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

- не найдено в активных dialogue-блоках

### Ty в ungated / 0–2 base (sample)

