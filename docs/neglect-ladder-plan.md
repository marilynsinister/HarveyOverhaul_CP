# Лестница последствий: ступени 4–5 и «Харви приходит сам» — план

Статус: план, код не начат (2026-10-27).

## Что уже есть (ступени 1–3)

| | Травмы (Injury) | Стресс (Stress, `StressNeglectService`) |
|---|---|---|
| 1 | Порог 1–3 дня → HUD + письмо | 2 дня → HUD «загляни к Харви» |
| 2 | Грязная рана → инфекция (открытые раны) | 4 дня → вес причины +10, каждое утро −15% энергии |
| 3 | «Небрежность»: −1 доверие, +1 день лечения каждые 3 дня (до +3) | 6 дней → доверие −3 |

Дальше ничего не происходит: штраф висит бесконечно. Ступени 4–5 закрывают этот потолок.

## Принципы

- Харви заботится, а не наказывает. «Не сейчас» уважается, а обморок — это предел тела, а не кара. В больнице он встревожен, но не упрекает.
- Всё видно заранее. Накануне ступени 4 приходит письмо «загляну утром». План Харви показывает, что будет дальше.
- Скрытые травмы (Харви не знает о них) лестница не трогает, как и сейчас.
- Не больше одного визита Харви в день на оба мода. Если ждут оба, травма идёт первой.
- Ступень 5 случается не больше одного раза на случай. На «Уютно» её нет.

## Ступень 4 — «Харви приходит сам»

### Когда

- **Травма**, Харви о ней знает:
  - «Небрежность» держится 3 дня;
  - или инфекция не лечена 2 дня.
- **Стресс**: дебафф без лечения 8 дней. Это `NeglectStage` 4 после текущей ступени 3 на 6-й день.

### Как

1. Вечером накануне приходит письмо от Харви. Тон зависит от отношений: «Завтра утром загляну до приёма».
2. Утром, когда игрок выходит на ферму (6:00–11:00, не фестиваль), C# запускает событие. В браке событие идёт в FarmHouse: Харви не ушёл на работу.
3. Развилка `quickQuestion`:
   - **«Хорошо, осмотри»** → действие `HouseCallAccept`. Выполняется то же, что сделал бы осмотр в клинике:
     - лечение не начато → начать лечение;
     - фаза ждёт осмотра → перевести на следующую фазу;
     - есть осложнение → вылечить его.

     Затем снимается «Небрежность» и возвращается 1 день удлинения: это бонус за то, что игрок дал помочь. Доверие +1. Для стресса начинается назначение по этому дебаффу.
   - **«Не сейчас, правда некогда»** → действие `HouseCallDefer`. Харви оставляет предметы: для травмы «Чистый бинт» и «Обезболивающее», для стресса «Травяной сбор». На 2 дня эскалация замирает: нет новых осложнений, нет +дней лечения, нет −15% энергии от плохого сна. Через 2 дня Харви приходит повторно, в короткой сцене, и снова даёт выбор.

### Сложность

- **Строго**: ступень 4 наступает на день раньше. При инфекции нет варианта «не сейчас».
- **Уютно**: отсрочка длится 3 дня.

## Ступень 5 — обморок / срыв

### Когда

- Игрок отказался при повторном визите и прошёл ещё день.
- Для стресса нужна ещё нагрузка не ниже High: если стресс спал сам, лестница замирает.

### Где и как

- Срабатывает в безопасной локации: не шахта, не вулкан, не Пещера Черепа, не событие, не фестиваль, не мини-игра.
- Нужно одно из двух:
  - недавняя тяжёлая работа (`IsDoingHeavyWorkRecently`);
  - энергия меньше 25% после 12:00.
- В опасной локации ждём выхода.

### Что происходит

- **Травма**: C# затемняет экран («в глазах темнеет…»), игрок попадает в клинику и проходит `StartForcedHospitalizationWithExplanation(injury, harvey, "neglect_collapse")` с дневным пребыванием. Осмотр гарантирован: это уже делает `EnsureTreatmentBeforeForcedHospitalization`. Деньги не теряются, запрета на шахты нет. После выписки и Dating+ срабатывает существующее событие `AfterHospitalDischargeHome`.
- **Стресс**: затемнение, потом событие:
  - Dating+ → FarmHouse: Харви сидит рядом, как в `MorningAfterExhaustion`;
  - остальные → Hospital: Харви на приёме.

  После события нагрузка −20 («выплакалась»), принудительно начинается эпизод Burnout или PhysicalExhaustion, энергия на остаток дня — 50%.

## События (CP)

Новый файл: `assets/Code/eventsHouseCall.json`, подключается в `content.json`.

| ID | Локация | Варианты тона |
|---|---|---|
| `eventHarveyHouseCallInjury` | Farm | Нейтральный (<6♥) / Близкий (6+♥) / Dating-Engaged |
| `eventHarveyHouseCallInjuryMarried` | FarmHouse | Married |
| `eventHarveyHouseCallInjuryRevisit` | Farm / FarmHouse | короткая сцена, тон через `When` |
| `eventHarveyHouseCallStress` | Farm | те же 3 тона, Харви с термосом |
| `eventHarveyHouseCallStressMarried` | FarmHouse | Married |
| `eventHarveyHouseCallStressRevisit` | Farm / FarmHouse | короткая |
| `eventHarveyStressCollapseHome` | FarmHouse | Dating / Engaged / Married |
| `eventHarveyStressCollapseClinic` | Hospital | остальные |

Для обморока от травмы отдельного события нет. Его делают C#-затемнение и новая реплика при поступлении в `HospitalizationManager` (`GetNeglectCollapseExplanation`).

Предусловие каждого события — тема, которую ставит C# (`topicHarvey_HouseCall*Pending`). Запуск идёт через `LocationEventLauncher.TryStartEventByPrefix`, поэтому событие не всплывёт само.

Правила текста:
- Dating ≠ живём вместе: «пришёл до приёма», а не «проснулся рядом».
- Реплики — полные мысли.

## Письма и темы

- Письма «Загляну утром» в 4 тонах: для травмы в `mailInjury.json`, для стресса в `mailStress.json`.
- Темы после визита или отказа — для реплик Харви в клинике в ближайшие 2 дня: `dialoguesHarveyCare.json`.
- Тема после срыва — для разговора на следующий день.

## Файлы C#

### Core (`HarveyOverhaulCore`)

- `Services/HarveyHouseCallCoordinator.cs` — **новый**. Даёт один слот визита в день и хранит, кто его занял; приоритет у Injury.
- `Api/IHarveyCoreApi.cs`, `Api/HarveyCoreApi.cs`: `TryClaimHouseCall(providerId)`, `IsHouseCallClaimedToday()`, флаги лестницы.
- `Core/ModConfig.cs`, `Core/GenericModConfigMenuIntegration.cs`: `EnableHouseCalls` (вкл) и `EnableNeglectCollapse` (вкл, на «Уютно» всегда выкл).

### Injury (`HarveyOverhaulInjury`)

- `Managers/NeglectLadderManager.cs` — **новый**. Отвечает за:
  - утреннюю оценку ступени после `CheckTreatmentCompletion`;
  - письмо накануне;
  - запуск визита при входе на Farm;
  - отслеживание отсрочки;
  - проверку обморока на `TimeChanged`.
- `Core/Models/InjuryState.cs`: `NeglectLadderState` — CaseInjuryId, Stage, HouseCallDay, DeferredUntilDay, Revisited, CollapseDone.
- `Managers/ComplicationManager.cs`: пока действует отсрочка, пропускать броски инфекции и `CheckNeglectEscalation`.
- `Managers/TreatmentStartHandler.cs`: действия `HouseCallAccept` и `HouseCallDefer`, выбор нужного осмотра.
- `Managers/HospitalizationManager.cs`: причина `neglect_collapse` — объяснение и дневной срок.
- `Core/Constants.cs`: ID событий, тем, писем, действий.
- `ModEntry.cs`, `EventHandlers/GameEventHandler.cs`, `EventHandlers/PlayerEventHandler.cs`: подключение (DayStarted, Warped, TimeChanged).
- `ModEntry.Commands.cs`: `harvey_ladder <stage|reset>` для QA.

### Stress (`HarveyStressMeter`)

- `Services/StressNeglectService.cs`: `NeglectStage` 4 и 5, учёт отсрочки.
- `Services/StressHouseCallService.cs` — **новый**. Запуск визита, действия accept/defer, срыв.
- `Models/TreatmentState.cs`: `HouseCallDeferredUntil`, `HouseCallRevisited`, `CollapseDone`.
- `Constants/HarveyStressActions.cs`, `Constants/MailIds.cs`, `Constants/TopicIds.cs`: новые ID.
- `ModEntry.cs`: регистрация.
- `Handlers/StressDebugCommandHandler.cs`: команда QA.
- `Api/StressPanelForecast.cs`: строка «Харви зайдёт завтра утром» или «Если тянуть — может кончиться обмороком».

### Тесты

- `HarveyStressMeter/docs/mcp-test-plans/neglect_ladder.json`: прогон ступеней 4 → defer → revisit → 5 для травмы и для стресса.

## Порядок работы

1. Core: координатор, API и настройки.
2. Injury: состояние, менеджер, действия, госпитализация, команды.
3. Stress: ступени 4–5 и сервис визита.
4. CP: события, письма, темы. Проверить скриптами `validate_event_coords.py` и `verify_priority1_tone.py`.
5. Прогнать тест-план в игре.
