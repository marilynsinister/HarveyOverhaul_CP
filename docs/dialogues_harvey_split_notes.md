# Заметки по разбиению `dialoguesHarvey.json`

**Дата:** 2026-06-04  
**Исходник:** монолит `assets/Code/dialoguesHarvey.json` (теперь manifest с `Include`)  
**Скрипт:** `scripts/split_dialogues_harvey.py` (повторный запуск перезапишет файлы в `assets/Code/dialogues/`)

Проверка объёма: **1114** записей `Entries` в исходнике = **1114** в сумме по split-файлам (`scripts/count_dialogue_entries.py`).

---

## Порядок подключения (в manifest)

1. `harvey_schedule_strings.json`
2. `harvey_base.json`
3. `harvey_hearts_0_2.json`
4. `harvey_hearts_3_5.json`
5. `harvey_hearts_6_7.json`
6. `harvey_topics_medical.json`
7. `harvey_locations.json`
8. `harvey_hospital.json`
9. `harvey_gifts.json`
10. `harvey_dating.json`
11. `harvey_married.json`

`content.json` по-прежнему подключает `assets/Code/dialoguesHarvey.json` с `Priority: Late`.

---

## Файлы и группы ключей

| Файл | Патчей | Ключей (слотов) | Что внутри |
|------|--------|-----------------|------------|
| `harvey_schedule_strings.json` | 2 | 7 | `strings/schedules/Harvey`: `Fri.*`, `Sat.*`, `winter_15.000`, married `marriageJob.*`, `marriage_Mon.*` |
| `harvey_base.json` | 2 | 61 | Без `When`: intro, breakUp, reject bouquet/pendant/gift, event memories (не topic), `WipedMemory`, `MovieInvitation`, `FlowerDance_Decline`; блок #31: `topicHarveyFirstVisit*`, `topicHarveySecondVisit*` |
| `harvey_hearts_0_2.json` | 1 | 50 | `Hearts: 0,1,2` — все `AcceptGift_*` / `AcceptBirthdayGift_*` |
| `harvey_hearts_3_5.json` | 2 | 62 | `Hearts: 3,4,5` gifts + из блока 4–7: `Mon4`–`Sun4`, `Saloon4`, `Hospital4`, `Desert4`, … |
| `harvey_hearts_6_7.json` | 1 | 12 | Из блока 4–7 (`When: 4,5,6,7`): `Mon6`–`Sun6`, `*6` location lines |
| `harvey_topics_medical.json` | 18 | 193 | Все `topicHarvey*` / `Treat_Hurt_*` из базы + `HasConversationTopic`: trauma, firstMeeting, walkGood, exhaustion (по стадиям ❤/dating/married) + dating-only topics из блока Dating |
| `harvey_locations.json` | 3 | 199 | Без When / `4–7` / `8–10`: `timeReaction_*`, `locationReaction_*`, `emotionalReaction_*`, `situationReaction_*`, `GreenRain*`, `Resort_*`, `spring_*`/`summer_*`/…, `Mon`–`Sun`, `Mon2`, фестивальные даты, `Saloon*`/`Desert*`/`Beach*` (не hospital/gift) |
| `harvey_hospital.json` | 5 | 52 | Strict `6–10` clinic block + `Hospital_Mon`–`Sun` из 4–7, 8–10, Dating |
| `harvey_gifts.json` | 3 | 150 | Gifts `6–10`, `Married`, и gift-часть блока Dating (`When: Dating`) |
| `harvey_dating.json` | 1 | 95 | `Relationship: Dating` — реакции, resort, сезон (не gifts/topics/hospital) |
| `harvey_married.json` | 3 | 233 | `MarriageDialogueHarvey`, `Weather: Storm` rainy, `FarmHouse` `spring_1`–`winter_28` |

---

## Разделение бывших монолитных блоков

| Исходный блок | Куда ушёл |
|---------------|-----------|
| #3 база (180 keys) | Разбит по типу ключа: `base`, `topics_medical`, `locations`, `hospital` |
| #5 сердца 4–7 (99) | `locations` + `hearts_3_5` (*4) + `hearts_6_7` (*6) + `hospital` |
| #6 сердца 8–10 (87) | `locations` + `hospital` |
| #11 Dating (182) | `gifts` + `dating` + `hospital` + `topics_medical` |

Тексты **не менялись** — только перенос и дублирование отдельных `EditData`-патчей.

---

## Пересекающиеся условия (не исправлялись)

При `Priority: Late` для совпадающего ключа побеждает **последний** патч в порядке загрузки manifest.

### Дубли `Hospital_Mon` … `Hospital_Sun`

Один и тот же ключ в нескольких файлах / патчах, например:

- `harvey_hospital.json` — strict 6–10, 4–7, 8–10, Dating
- `harvey_topics_medical.json` — trauma, firstMeeting, exhaustion (+ базовые topic overrides)

**Риск:** при активном topic + 8 ❤ играет exhaustion/trauma **после** heart-hospital (если topic-блок ниже в общем порядке — сейчас topics **до** hospital в manifest → hospital перебивает topic на том же ключе).  
**Это изменение приоритета относительно старого монолита**, где topic-блоки шли **после** heart-блоков.

| Старый порядок (монолит) | Новый порядок (manifest) |
|--------------------------|---------------------------|
| … hearts → gifts → dating → married → **topics** → storm → farm | … **topics** → locations → hospital → gifts → dating → married |

**Действие на будущий PR:** либо перенести `harvey_topics_medical.json` **после** `harvey_hospital.json`, либо оставить как есть и принять, что clinic lines при topic сильнее topic-hospital (как сейчас после split).

### `timeReaction_*`, `GreenRain`, `Resort_*`

- Fallback в `harvey_locations.json` (база, без When)
- Переопределения: `4–7`, `8–10`, `dating`

### `AcceptGift_*`

- Патчи в `hearts_0_2`, `hearts_3_5`, `gifts` (6–10, married, dating)
- При dating + 8 ❤: dating gifts идут **после** 6–10 gifts → dating побеждает (как в монолите: dating block после gift 6–10)

### Базовый блок #3 vs специализированные

Ключи, оставшиеся только в `harvey_base.json`, не дублируются. Ключи, вынесенные в topics/locations/hospital, **удалены** из базового патча #3 (не копируются дважды в base).

### Блок #31 (visit topics, без When)

Перенесён в `harvey_base.json` последним патчем файла → перекрывает одноимённые ключи из разделённого патча #3 в том же файле (в монолите #31 был **после** всего — поведение сохранено относительно полного списка Changes).

### Дублирующий `When` в исходном блоке #5

В JSON по-прежнему два поля `"When"`; эффективно `Hearts: 4,5,6,7` (не `3`). Отражено в `harvey_hearts_3_5` / `harvey_hearts_6_7` — **условие не меняли**.

### `When` после `Entries`

В `harvey_dating.json` и `harvey_married.json` (MarriageDialogue) поле `When` остаётся **после** `Entries`, как в исходнике.

---

## Что править в следующих PR (текст / логика)

См. `docs/dialogues_harvey_audit.md` — тон по стадиям, PR-0 (JSON), PR-1+ (тексты).

Для split-логики отдельно:

1. Решить порядок **topics vs hospital** в manifest, если нужны topic-override'ы поверх clinic lines.
2. Объединить `hearts_6_7` с отдельным `When: 6,7` при исправлении блока #5.
3. Вынести `topicHarveySecondVisit*` из глобального base в staged topics.

---

## Вспомогательные артефакты

- `docs/_split_stats.json` — список ключей по файлу (генерируется скриптом, можно не коммитить).
