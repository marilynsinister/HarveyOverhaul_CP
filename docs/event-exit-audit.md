# Аудит выхода из событий и пропуска сцен

Сгенерировано `scripts/audit_event_exits.py` 2026-10-27. Событий: 266 (все файлы, подключённые в content.json).

HIGH: 0, MEDIUM: 0, INFO: 6.

- **HIGH** — в `setSkipActions` команды события вместо trigger actions: при пропуске не выполняются.
- **MEDIUM** — пропуск сцены теряет тему, письмо, дружбу или предмет.
- **INFO** — сцена уходит в другую локацию и кончается простым `end`: фермер вернётся на старт.

| Risk | Файл | Событие | Локация | Что | Как исправить |
|------|------|---------|---------|-----|---------------|
| INFO | `courtshipLine.json` | `HarveyOverhaulCourtship.I2_Kidnap` | Hospital | сцена уходит в Town, конец `end` — фермер вернётся в Hospital | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
| INFO | `courtshipLine.json` | `HarveyOverhaulCourtship.I2_Kidnap` | Hospital | сцена уходит в Town, конец `end` — фермер вернётся в Hospital | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
| INFO | `events.json` | `528013` | Town | сцена уходит в Custom_GrampletonFields_Small, конец `end` — фермер вернётся в Town | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
| INFO | `events.json` | `eventHarveyLateNightCollapse` | Town | сцена уходит в Hospital, конец `end dialogue Harvey "Спокойной ночи... х` — фермер вернётся в Town | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
| INFO | `events.json` | `eventHarveyStormComfortMine` | Mine | сцена уходит в Town, конец `end` — фермер вернётся в Mine | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
| INFO | `events.json` | `eventHarveyStormComfortMountain` | Custom_AdventurerSummit | сцена уходит в Mountain, конец `end` — фермер вернётся в Custom_AdventurerSummit | `end position X Y` задаёт точку на исходной карте; для выхода в другую локацию нужен отдельный переход после события |
