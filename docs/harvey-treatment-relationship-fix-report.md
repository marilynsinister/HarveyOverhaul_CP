# Отчёт: выбор реплик лечения по стадии отношений

**Дата:** 2026-06-03

## C# (HarveyOverhaulInjury)

| Файл | Изменения |
|------|-----------|
| `Managers/DialogueManager.cs` | `HarveyRelationshipStage`, `GetHarveyRelationshipStage()`, выбор по `Prefix_{Stage}_`, fallback Dating/Married с фильтром формальных маркеров; `TryPickHarveyDialogueByPrefix` использует ту же логику |

### Логика fallback

- **Dating:** Dating → Close → Friend → общий ключ (без «Вы/приходите/…»)
- **Married:** Married → Dating → Close → Friend → общий ключ (с тем же фильтром)
- **Close / Friend / Acquaintance / Stranger:** цепочка стадий → общий ключ

## CP (HarveyOverhaul [CP])

| Файл | Изменения |
|------|-----------|
| `assets/Code/dialoguesHarveyCure.json` | 195 ключей `Treat_*_{Stranger}_*` в блоке 0–2 ❤; `Treat_*_{Dating|Married}_1` в блоках Relationship; `Recovery_Complete_*_Stranger` для формальных recovery; `Support_Cold_Dating` / `Support_Cold_Married` |
| `assets/Code/dialoguesHarveyInjury.json` | `PhaseTransition_*_Stranger` + `_Dating` + `_Married` для формальных phase-реплик (5 ключей) |
| `scripts/relationship_treatment_dialogue_keys.py` | Скрипт пересборки (повторный запуск идемпотентен для Treat inject) |

## Префиксы со стадийными вариантами

| Префикс | Stranger | Dating | Married |
|---------|----------|--------|---------|
| `Treat_{Injury}_Before_` | ✓ (0–2 ❤, 195 ключей) | ✓ `_Dating_1` | ✓ `_Married_1` |
| `Treat_{Injury}_After_` | ✓ | ✓ | ✓ |
| `Recovery_Complete_*` | ✓ `_Stranger` (19) | — (fallback tu 6–10 / фильтр C#) | — |
| `PhaseTransition_*` | ✓ `_Stranger` | ✓ `_Dating` | ✓ `_Married` |
| `Support_Cold` | — (в 0–2 нет) | ✓ `_Dating` | ✓ `_Married` |
| `topic*` (cured / treatment) | ✓ 0–2 «Вы» | ✓ блоки Relationship (уже были) | ✓ |

## Исправленные формальные dating/married реплики

| Ключ / область | Было | Стало |
|----------------|------|-------|
| `Treat_*_After*` (все травмы, dating) | «избегайте… приходите в клинику» (из merged 0–2) | `Treat_*_After_Dating_1` на «ты» |
| `Treat_*_Before*` (dating) | «Покажите…» | `Treat_*_Before_Dating_1` |
| `Support_Cold` (dating block) | только informal в конце файла | `Support_Cold_Dating` без «Вы» |
| `PhaseTransition_BruisedRibs_2_Dating/Married` | «почувствуете» | «почувствуешь» |
| C# fallback | случайный formal из unstaged | фильтр + staged keys |

## Проверка в игре

1. Сейв **Dating/Married** с Харви → клик лечение / смена фазы / recovery.
2. В логе SMAPI: `[Treat]` / `Диалоги лечения` с `stage=Dating` или `Married`, без warn о fallback.
3. Нет «Вы», «приходите», «Покажите» в репликах при романтике.
