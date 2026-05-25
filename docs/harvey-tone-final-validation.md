# Final technical validation — Harvey tone/control pass

**Дата:** 2026-05-25  
**Скрипт:** `scripts/final_technical_validation.py`  
**Правило:** только технические проверки, без художественных правок.

| Проверка | Статус | Найдено | Исправлено | Нужно вручную |
|----------|--------|---------|------------|---------------|
| 1. JSON валидность | OK | 30 strict OK; 3 CP-multiline (events.json, eventsCare.json, eventsMineRescue.json) | buffsInjury.json:30 — inline `//` после значения перенесён на отдельную строку; content.json/buffsCure.json trailing comma (ранее) | dialoguesHarveyCure.json — inline `//` в Entries (CP OK, strict JSON не требуется) |
| 2. When/Condition CP-формат | OK | скалярные When/Condition | — | — |
| 3. Дубли ключей в Entries | OK | 0 (после правок) | events.json: E13 утро/вечер разделены на два `Changes`-блока; парсер `final_technical_validation.py` учитывает `\"` в ключах (ложный dup с `GameStateQuery ANY`) | — |
| 4. Dating/Married vs Hearts приоритет | WARN | 107 ключей (ungated+Dating) | — | CP Late + When OK если Dating специфичнее |
| 5. Base/fallback 0–2 ❤ | OK | ungated без pet names | — | topic-gated ty — см. manual |
| 6. Mail IDs используются | OK | определено 214, сирот 0 | — | — |
| 7. Event IDs уникальны | OK | 58 entries, 56 unique IDs, 1 с time/cond вариантами | E13: два CP-блока (0700–1200 / 1800–2200), один script на слот | дубли ID с разными условиями — штатно |
| 8. Friendship gates (500/750/1500/2000/2500) | WARN | 15 non-canonical FP | — | events.json:HarveyOverhaulStory.E6_SayItOutLoud Friendship 1750 (non-canonical); events.json:HarveyMod_TreatmentReview Friendship 1000 (non-canonical); events.json:eventHarveyMountainDate Friendship 2 |
| 9. Dating/Married events — rel gate | OK | 0 | — | — |
| 10. Pet names вне Dating/Married | OK | 0 | — | — |
| Include: quest_dialogues.json | WARN | не в content.json | — | подключить или игнорировать |
| Include: dialoguesHarveyStress.json | WARN | закомментирован | — | правки darkness не в игре |
| Include: events_for_mode_new_formatted.json | OK | не подключён (SKIP) | — | — |
| C# mail/event refs | OK | C# не найден в мод-паке | — | только CP/triggers |

## Исправления после 73c95c0 (2026-05-25)

### Сделано автоматически

1. **buffsInjury.json:30:42** — удалён inline-комментарий `// 1.5 дня` после числового значения `Duration` (невалидный strict JSON). Комментарий перенесён на отдельную строку над полем; multiline event strings не трогались.
2. **events.json — E13_MinesAgreement** — один `Changes`-блок с двумя Entries (утро + вечер) разделён на два блока: `E13 … (BusStop, утро)` и `E13 … (BusStop, вечер)`. Ключи по-прежнему различаются по `Time`, перетирания нет.
3. **scripts/final_technical_validation.py** — детектор дублей ключей в `Entries` теперь корректно парсит escaped quotes (`\"`) в длинных event keys (`GameStateQuery ANY "…"`). Ранее это давало ложный FAIL с ключом `/GameStateQuery !PLAYER_HAS_SEEN_EVENT …`.

### Остаётся вручную (WARN, не блокеры)

| Область | Что | Рекомендация |
|---------|-----|--------------|
| Friendship gates | 15 non-canonical FP (1000, 1250, 1750, …) | См. список ниже; менять только если нужна унификация с каноном 500/750/1500/2000/2500 |
| Dating vs Hearts | 107 ключей ungated+Dating | Проверить приоритет CP `When` / `Update: OnLocationChange` — OK если Dating-ветка специфичнее |
| quest_dialogues.json | не в content.json | Подключить или сознательно игнорировать |
| dialoguesHarveyStress.json | закомментирован | Правки stress/darkness не в активном паке |
| dialoguesHarveyCure.json | inline `//` в Entries | CP-compatible; strict JSON не применять |

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

