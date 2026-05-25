# Аудит: контроль Харви и opt-out

**Дата:** 2026-05-25  
**Основа:** [harvey-relationship-tone-guide.md](./harvey-relationship-tone-guide.md)  
**Статус:** первый проход (инвентаризация + P0/P1-правки)

---

## Краткое резюме

| Категория | Всего сцен/ключей | OK | P1 | P0 |
|-----------|-------------------|----|----|-----|
| Шахты / Skull Cave | 6 | 2 | 2 | 2 |
| Сон / curfew / ночь | 9 | 3 | 4 | 2 |
| Госпитализация / collapse | 8 | 1 | 3 | 4 |
| Overprotective / supervision | 5 | 3 | 1 | 1 |
| Стресс / darkness therapy | 12 | 2 | 4 | 6 |
| Quest start (ungated) | 5 | 0 | 1 | 4 |
| Dialogue 6–10 ❤ (контроль) | ~25 | ~8 | ~15 | 2 |
| Dating/Married (escape hatch) | ~20 | ~12 | ~6 | 2 |

**Главные риски P0:** ungated quest-старты с «живёшь у меня» / «без обсуждений»; darkness arc base-слой с «нет выбора»; смешение «Вы»+«ты» в mine interception; skull cave «Домой. Сейчас же!» без ветки границы.

**Эталоны opt-out (не трогать):** Storm comfort (`events.json`), Door signal E7, E13 Mines Agreement, First visit forks, Safety kit «Не хочу аптечку», overprotective Dating/Married с «стоп».

---

## Критерии оценки

Для каждой записи:

1. **Медпротокол vs гиперопека** — клиническая необходимость или личная власть?
2. **Стадия** — hearts / Friendship / Relationship gate
3. **Opt-out** — есть ли выбор, «стоп», мягкий выход?
4. **quickQuestion** — нужен ли интерактивный выбор?
5. **Смягчение** — нужно ли переписать base-текст или перенести жёсткость в Dating/severe gate?

---

## 1. Шахты и опасные локации

| ID | Файл | Gate | Цитата (суть) | Протокол / гиперопека | Opt-out | QQ | Приоритет |
|----|------|------|---------------|----------------------|---------|-----|-----------|
| `eventHarveySkullCavePrevention` | `eventsCare.json` | Dating/Married + injury buff / SkullCave exit | «Домой. Сейчас же!» | Гиперопека (личная тревога «без меня») | Частично: обещание / ресурсы | fork2, нет «пространства» | **P0** |
| `eventHarveyMineInterception` | `eventsCare.json` | Dating/Married + injury buff | «никаких шахт во время лечения» | Протокол восстановления + личная тревога | Да: согласие / время / альтернатива | Да | **P0** (ty mix) |
| `HarveyOverhaulStory.E13_MinesAgreement` | `events.json` | FP 3000, Dating/Married/rescue | «хочу сказать: запрещаю» → договор | Протокол (осознанный reframing) | Да: 4 пункта договора | Да | OK |
| `triggerHarveySkullCaveWarning` | `triggersCare.json` | Dating/Married + buff | триггер события | Gate OK | через event | — | OK |
| `triggerHarveyMineWarning` | `triggersCare.json` | Dating/Married + buff | триггер события | Gate OK | через event | — | OK |
| `locationReaction_Mine/SkullCave` | `dialoguesHarvey.json` | 3–5 ❤ / 6–10 ❤ / Dating | «не дам рисковать» | Настойчивая забота | Нет QQ; просьба пообещать | Нет | P1 |
| `eventHarveyMineRescue*` | `eventsMineRescue.json` | post-rescue | эвакуация | Медпротокол экстренный | ограничен | частично | OK (severe) |

---

## 2. Сон, curfew, ночные патрули

| ID | Файл | Gate | Цитата | Протокол / гиперопека | Opt-out | QQ | Приоритет |
|----|------|------|--------|----------------------|---------|-----|-----------|
| `eventHarveyCheckFarmerOutsideAfter22` | `events.json` | Dating/Married + passed out topic | «марш в дом!» | Гиперопека (личный curfew) | Слабый: животные / сон | 2 ветки, нет границы | **P0** |
| `eventHarveyMorningCheckup` | `events.json` | Dating + mandatory checkup | щадящий режим | Протокол + партнёрская забота | «ты слишком волнуешься» | Да | OK |
| `triggerTimeReactionLate/VeryLate` | `triggersCare.json` | FP 750 / 1500 | mail + topic | Реакция, не блокировка | через dialogue | — | P1 |
| `timeReaction_Late/VeryLate` | `dialoguesHarvey.json` | Married (762+) | «не оставлю одной» | Гиперопека | Нет «стоп» в тексте | Нет | P1 (Married OK, нужен hatch) |
| `topicHarvey_NightRound` | `dialoguesHarveyCure.json` | 0–2 / 3–5 / 6–10 / Dating / Married | ночной обход | Протокол → гиперопека по слоям | Dating/Married: «стоп» | — | OK (см. cure log) |
| `HarveyMod_SleepTherapyStart` | `quest_dialogues.json` | ungated quest | «Никаких компромиссов» | Протокол, но императив | Нет | Нет | **P0** |
| `HarveyMod_LateNightWarning` (mail) | `mail.json` | FP gate | предупреждение | Протокол | — | — | OK |

---

## 3. Госпитализация и принудительное лечение

| ID | Файл | Gate | Цитата | Протокол / гиперопека | Opt-out | QQ | Приоритет |
|----|------|------|--------|----------------------|---------|-----|-----------|
| `eventHarveyCheckHealthFarmer` (хвост) | `events.json` | Dating + PlayerKilled | «никуда не денешься», привязка к койке | Гиперопека (шутка + угроза санитаров) | Нет | Нет | **P0** |
| `eventHarveyTreatmentCollapse` | `events.json` | collapse trigger | «на лечении под присмотром» | Медпротокол | farmer pushback, нет QQ | Нет | P1 |
| `eventStayInHospital` | `events.json` | hospital | «не говорил что можете вставать» | Протокол | farmer: «мне нужно домой» | Нет | OK |
| `eventHarveyLateNightCollapse` | `events.json` | Time 24–26 | «везу в клинику» | Экстренный протокол | нет | нет | OK (severe) |
| `topicHarvey_ForcedHospitalization` | `dialoguesHarvey.json` | 0–2 «Вы» / 6+ «ты» | «дыши, я рядом» | Протокол (смягчено ранее) | — | — | OK |
| `HarveyMod_BreakdownRecoveryStart` | `quest_dialogues.json` | ungated | «госпитализация, не отхожу» | Протокол + личная привязка | Нет | Нет | **P0** |
| `HarveyMod_CollapseRehabilitationStart` | `quest_dialogues.json` | ungated | «Без обсуждений» | Протокол, но властный тон | Нет | Нет | **P0** |
| `HarveyMod_DespairInterventionStart` | `quest_dialogues.json` | ungated | «живёшь у меня» | **Гиперопека** на base | Нет | Нет | **P0** |

---

## 4. Overprotective mode / emergency supervision

| ID | Файл | Gate | Цитата | Протокол / гиперопека | Opt-out | QQ | Приоритет |
|----|------|------|--------|----------------------|---------|-----|-----------|
| `triggerEmergencySupervision` | `triggersCare.json` | FP 2000, Dating/Married + topics | buff + topic | Протокол наблюдения | mail: «скорректируем» | — | OK |
| `topicOverprotectiveMode` | `dialoguesHarveyInjury.json` | 0–2 / 3–5 / 6–10 / Dating / Married | «шахты под запретом» | 0–2 протокол; 6+ «стоп» | 6+/D/M: «стоп» | — | P1 (3–5 без hatch) |
| `mailHarveyOverprotectiveNotice` | `mailInjury.json` | injury mail | протокол наблюдения | Протокол | «обсудим план» | — | OK |
| `HarveyMod_EmergencySupervision` | `mail.json` | supervision mail | режим наблюдения | Протокол | «скажите, скорректируем» | — | OK |
| `HarveyMod_FatigueTreatmentStart` | `quest_dialogues.json` | ungated | «буду контролировать соблюдение» | Протокол, императив | Нет | Нет | **P0** |

---

## 5. Стресс / darkness therapy arc

| ID | Файл | Gate | Цитата | Протокол / гиперопека | Opt-out | QQ | Приоритет |
|----|------|------|--------|----------------------|---------|-----|-----------|
| `topicStressDarknessLevel3` | `dialoguesHarveyStress.json` | base (0–2?) | «Без отговорок», mix «твою» | Протокол, но властно | Нет | Нет | **P0** |
| `topicStressDarknessLevel3` | same | Hearts 7–10 | «не приму отказа» | Граница протокол/гиперопека | Нет | Нет | **P0** |
| `topicStressDarknessLevel3` | same | Dating | «не позволит страху» | Гиперопека допустима | Нет «стоп» | Нет | P1 |
| `topicDarknessTherapyStart` | same | base | «приказ врача» | Протокол | Нет | Нет | **P0** |
| `topicDarknessStep1Complete` | same | base | «нет выбора — не дам сдаться» | **Гиперопека** | Нет | Нет | **P0** |
| `topicStressCritical` | same | base / 7–10 / Dating | «никаких отговорок» | Протокол экстренный | Нет | Нет | P1 |
| `eventHarveyStormComfortFarm` | `events.json` | FP 750, storm | «не могу позволить рисковать» (ветка 2) | Забота | «справлюсь дома» / escort | Да | OK |

---

## 6. Dialogue 6–10 ❤ — контроль без severe gate

| ID | Gate | Суть | Протокол / гиперопека | Opt-out | Приоритет |
|----|------|------|----------------------|---------|-----------|
| `Fall_20` | Hearts 6–10 | «госпитализирую, не шучу» | Императив | Нет | **P0** |
| `Hospital_Mon–Sun` (6–10 block) | 6–10 | «никаких возражений», «не спорь» | Настойчивая гиперопека | Нет | P1 |
| `Winter_3`, `Summer_12`, `Saloon2` | 6–10 | «не снимай», «не спорь» | Контроль режима | Нет | P1 |
| `situationReaction_Exhausted` | 6–10 | «не спорь — не просьба» | Забота + императив | Нет | P1 |
| `summer_Thu` (Married) | Married | «никуда не денешься от заботы» | Гиперопека | Нет явного hatch | P1 |

---

## 7. События с quickQuestion (эталоны)

| Event | Gate | Почему OK |
|-------|------|-----------|
| `eventHarveyStormComfortFarm` | pre-Dating storm | 3 ветки: клиника / дом / escort на ферме |
| `HarveyOverhaulStory.E7_DoorSignal` | FP 2000 | граница: близко / стул / дверь / спрятать записку |
| `HarveyOverhaulStory.E13_MinesAgreement` | Dating+ | договор вместо запрета |
| `eventHarveyFirstWalk` acceptWalk | post second visit | «Вы слишком настойчив» → −20 FP, topic |
| `HarveyMod_TreatmentPlanMeeting` | FP 750 | согласие / сократить / отказ |
| `eventHarveyMineInterception` | Dating + injury | 3 ветки (после правки ty + 4-я «остановись») |

---

## P0 — исправления (этот проход)

| # | Файл | Изменение |
|---|------|-----------|
| 1 | `quest_dialogues.json` | Despair/Breakdown/Collapse/Fatigue/Sleep — протокол вместо «живёшь у меня» / «без обсуждений» / «контролирую» |
| 2 | `dialoguesHarveyStress.json` | base darkness L3, therapy start, step1 — убрать «нет выбора», fix «Вы»+«ты» |
| 3 | `dialoguesHarveyStress.json` | 7–10 darkness L3 — «не приму отказа» → согласие пациента |
| 4 | `dialoguesHarveyInjury.json` | 3–5 `topicOverprotectiveMode` — escape hatch |
| 5 | `dialoguesHarvey.json` | `Fall_20` — рекомендация стационара вместо угрозы |
| 6 | `eventsCare.json` | skull cave: смягчить финал + QQ «Мне нужно пространство» |
| 7 | `eventsCare.json` | mine interception: fix «Вы»/«ты», + «Харви, остановись» |
| 8 | `events.json` | outside after 22: + «Мне нужно пространство» |
| 9 | `events.json` | check health farmer: QQ перед госпитализацией + смягчить end dialogue |

---

## P1 — следующая итерация

- Split Hospital_* 6–10: «не спорь» → «скажи, если давлю»
- `timeReaction_VeryLate` Married: явный «скажи стоп»
- `locationReaction_SkullCave` 3–5: просьба вместо «не дам»
- Darkness Dating block: «скажи стоп» в L3
- `eventHarveyTreatmentCollapse`: QQ «Я справлюсь дома» / «Согласна на наблюдение»
- Полный grep `events_for_mode_new_formatted.json` при подключении в pack

---

## Smoke-test после правок

1. **0–2 ❤, collapse quest:** quest start звучит как протокол («наблюдение», «стационар по показаниям»), не «живёшь у меня».
2. **Darkness L3 base:** только «Вы»; нет «нет выбора» / «приказ».
3. **Dating + injury buff → Mine:** interception без «Вы думаешь»; 4-я ветка QQ работает.
4. **Dating + SkullCave exit:** третья ветка «пространство» не ломает event chain.
5. **Dating, passed out, 22:00 farm:** третья ветка curfew — мягкий ответ Харви.
6. **Dating, PlayerKilled check:** QQ перед warp Hospital; можно «Я справлюсь» с мягким escort.

---

*Связанный журнал правок: [harvey-tone-fix-log.md](./harvey-tone-fix-log.md)*
