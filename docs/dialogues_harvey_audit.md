# Аудит `dialoguesHarvey.json`

**Дата:** 2026-06-04  
**Файл:** `assets/Code/dialoguesHarvey.json` (~1458 строк, подключён из `content.json`)  
**Цель:** подготовка к переработке диалогов Харви по уровням отношений — без хаотичных «Вы/ты», ранней романтики и гиперопеки.  
**Правки в JSON не вносились** (только этот отчёт).

---

## 1. Краткие выводы

| Проблема | Масштаб |
|----------|---------|
| Блоков `EditData` по целевым Target | **31** |
| Ключей, встречающихся в 2+ блоках | **210** |
| Перекрывающиеся диапазоны сердец | 4–7, 6–10, 8–10 + базовый слой без `When` |
| Базовый блок без `When` | **180** реплик (#3): дни недели, реакции, десятки `topicHarvey*`, фестивали |
| Смешение «Вы» + «ты» в одной строке (автопоиск) | **2** ключа (#31) |
| Доп. риски (ручная проверка) | `timeReaction_VeryLate` в #3: «Вы» → «ты» в одной реплике; Dating-topic с «Не пугайтесь» |
| Маркеры гиперопеки (триггер-лист §5) | сотни вхождений, пик — Marriage + FarmHouse + Dating |
| Технические баги JSON | Дублирующий `"When"` в блоке #5; `When` **после** `Entries` в #11–#12; финальный блок #31 **без** `When` |

**Оценка:** файл рабочий для Content Patcher, но архитектура отношений перегружена: один файл, `Priority: Late` везде, конкурирующие `When`, базовый слой перебивает стадийные оверрайды, а блок Dating (#11) дублирует 8–10 ❤ с marriage-тоном.

---

## 2. Блоки EditData по Target

Всего **31** блок `EditData` только для трёх Target ниже (других Target в файле нет).

### 2.1 `strings/schedules/Harvey`

| # | When | Entries | Группы ключей | Пересечения |
|---|------|---------|---------------|-------------|
| 1 | *(нет)* | 4 | `Fri.000`, `Fri.001`, `Sat.000`, `winter_15.000` | Нет |
| 2 | `Relationship:Harvey=Married` | 3 | `marriageJob.000`, `marriage_Mon.000`, `marriage_Mon.001` | Нет |

**Тон:** #1 — «Вы», нейтральная диетология ✓. #2 — «ты», «котёнок», «малышка», «я не дам» (контекст встречи на работе).

---

### 2.2 `Characters/Dialogue/Harvey`

| # | When | Entries | Назначение / группы ключей | Пересечения |
|---|------|---------|------------------------------|-------------|
| 3 | *(нет)* | **180** | См. §2.2.1 | Конфликтует почти со всеми heart/dating/married/topic-блоками |
| 4 | `Hearts:Harvey=6,7,8,9,10` | 24 | `Hospital_Mon`–`Sun`, локации `Saloon`/`Desert`/`Beach` + суффиксы 2, `topicHarvey_ForcedHospitalization` | `Hospital_*` с #3, #5, #6, #11, topics #13–28 |
| 5 | `Hearts:Harvey=4,5,6,7` * | 99 | `timeReaction_*`, `locationReaction_*`, `emotionalReaction_*`, `situationReaction_*`, `GreenRain*`, `Resort_*`, `Mon4`/`Mon6`, `spring_*`/`summer_*`/`fall_*`/`winter_*`, `Hospital_*`, фестивальные даты | Реакции и resort с #3, #6, #11; `Hospital_*` с topics |
| 6 | `Hearts:Harvey=8,9,10` | 87 | То же + `Mon8`/`Mon10`, `Saloon8`/`Saloon10`, … | С #5 на 8–10 ❤; `Mon8`/`Mon10` с #11 (Dating) |
| 7 | `Hearts:Harvey=0,1,2` | 50 | `AcceptBirthdayGift_*`, `AcceptGift_(O)*` | 50 ключей × #8–11 |
| 8 | `Hearts:Harvey=3,4,5` | 50 | Gifts | × #7–11 |
| 9 | `Hearts:Harvey=6,7,8,9,10` | 50 | Gifts (pre-dating) | × #7–11 |
| 10 | `Relationship:Harvey=Married` | 50 | Gifts married | × #7–11 |
| 11 | `Relationship:Harvey=Dating` | **182** | Gifts + все реакции/resort/сезон + `Mon8`/`Mon10` + dating-topics | Максимальное пересечение с #5, #6, #12, #30 |
| 13 | `topicHarveyTraumaReveal` + `Hearts=0,1,2` | 4 | `Hospital_Mon`, `Wed`, `Fri`, `Sun` | `Hospital_*` |
| 14 | `topicHarveyTraumaReveal` + `Hearts=3–10` | 4 | то же | то же |
| 15 | `topicHarveyTraumaReveal` + `Dating` | 4 | то же | то же |
| 16 | `topicHarveyTraumaReveal` + `Married` | 4 | то же | то же |
| 17 | `topicFirstMeeting` + `Hearts=0,1,2` | 8 | `Hospital_*` + `Town`, `Saloon`, `Beach`, `ArchaeologyHouse` | Location + hospital |
| 18 | `topicFirstMeeting` + `Hearts=3–10` | 8 | то же | то же |
| 19 | `topicFirstMeeting` + `Dating` | 8 | то же | то же |
| 20 | `topicFirstMeeting` + `Married` | 8 | то же | то же |
| 21 | `topicHarveyWalkGood` + `Hearts=0,1,2` | 4 | `eventSeen_eventHarveyFirstWalk_*` | — |
| 22 | `topicHarveyWalkGood` + `Hearts=3–10` | 4 | то же | — |
| 23 | `topicHarveyWalkGood` + `Dating` | 4 | то же | — |
| 24 | `topicHarveyWalkGood` + `Married` | 4 | то же | — |
| 25 | `topicHarveyExhaustion` + `Hearts=0,1,2` | 8 | `Hospital_*` + 4 location | Уже смягчённый тон (§5) |
| 26 | `topicHarveyExhaustion` + `Hearts=3–10` | 8 | «ты», без ultimatum | — |
| 27 | `topicHarveyExhaustion` + `Dating` | 8 | то же | — |
| 28 | `topicHarveyExhaustion` + `Married` | 8 | то же | — |
| 29 | `Relationship:Married` + `Weather=Storm` | 10 | `Rainy_Day_*`, `Rainy_Night_*` | — |
| 30 | `Relationship:Married` + `LocationName=FarmHouse` | **110** | `spring_1`–`winter_28` (каждый день сезона) | Фестивальные ключи с #3, #5, #11, #12 |
| 31 | *(нет)* | 6 | `topicHarveyFirstVisit*`, `topicHarveySecondVisit*` | Дубли #3 + **ломает** «Вы/ты» |

\* **Баг §2.3:** в объекте два поля `"When"` — см. ниже.

#### 2.2.1 Блок #3 (базовый слой) — группы ключей

| Группа | Примеры ключей | Замечание по тону |
|--------|----------------|-------------------|
| События / память | `eventHarveyMedicalCheck_*`, `eventSeen_58_*`, `event_heart*`, `event_grave*` | В основном «Вы» |
| Walk / visit (без стадии) | `topicHarveyWalk*`, `topicHarveyFirstVisit*`, `topicHarveySecondVisit*` (частично дубль #31) | Смешанная формальность |
| Медицинские topics (Injury) | `topicHarvey_WetBandage`, `Trust_*`, `Storm_*`, `Mines_*`, `ForcedHospitalization`, `Treat_Hurt_*`, … | **Без `When` по сердцам** — играют на всех стадиях |
| Отказы / подарки | `RejectBouquet_*`, `RejectMermaidPendant_*`, `RejectItem_*` | «Вы» ✓ |
| Дни недели | `Mon`–`Sun`, `Mon2` | `Mon`–`Sun`: строчное «вы/ваш» в части строк; `Mon2` только здесь |
| Сезонные дни | `spring_12`, `summer_10`, `winter_24`, … | Часть с ранней заботой («Вам», чай) |
| Сезон × день | `spring_Mon` … `winter_Sun` | Дубли с #5, #6, #11 |
| Реакции | `timeReaction_*`, `locationReaction_*`, `emotionalReaction_*`, `situationReaction_*` | Дубли; `timeReaction_VeryLate` — mix «Вы/ты» |
| Праздники в базе | `summer_9`, `winter_30` | Длинные монологи, шаблон «уставшая/испуганная» |

---

### 2.3 Технические проблемы JSON

**1. Дублирующий `"When"` в блоке #5** (комментарий «4–7 сердец», стр. ~251–362):

```json
"When": { "Hearts:Harvey": "3,4,5,6,7" },
"Entries": { ... },
"When": { "Hearts:Harvey": "4,5,6,7" }
```

Парсер оставляет **только** `4,5,6,7` → реплики **не применяются на 3 ❤**, хотя первый `When` и комментарий это предполагают.

**2. `When` после `Entries`** в блоках #11 (Dating) и #12 (`MarriageDialogueHarvey`). Для JSON это один объект — условие действует, но **легко ошибиться при правке** (кажется, что gifts без `When`).

**3. Блок #31 в конце файла** — без `When`, 6 ключей visit-topics. При `Priority: Late` перекрывает одноимённые ключи из #3 **для всех стадий**, включая 0–2 ❤ и married.

**4. Комментарий «8–10 романтика»** (стр. ~706) относится к объекту с `When: Dating` (#11) — комментарий **не соответствует** условию.

---

### 2.4 `Characters/Dialogue/MarriageDialogueHarvey`

| # | When | Entries | Группы ключей | Пересечения |
|---|------|---------|---------------|-------------|
| 12 | `Relationship:Harvey=Married` | **113** | `Mon`–`Wed`, `Sat`, `Resort_*`, `Rainy_*`, `Indoor_*`, `Outdoor_*`, `Mine_*`, `Forest_*`, `Beach_*`, `Town_*`, `Farm_*`, `Hospital_*`, kids, `Good_*`/`Bad_*`, `funLeave`/`jobLeave`, сезонные `spring_12`…`winter_24`, `spring_1`…`winter_28` | `Mon`/`Tue`/`Sat` с #3; фестивали и resort с #5, #11, #30 |

**Тон:** pet name почти в каждой строке; «я прослежу», «не спорь», «ты уставшая/бледная», location-barks как медконтроль.

---

## 3. Повторяющиеся ключи между условиями

При одинаковом `When` и `Priority: Late` побеждает **последний** блок в `Changes[]`.

### 3.1 По запрошенным шаблонам

| Шаблон | Ключей в 2+ блоках | Типичные блоки |
|--------|-------------------|----------------|
| `Hospital_Mon` … `Hospital_Sun` | 7 | #3?, #4, #5, #6, #11, #12, topics #13–20, exhaustion #25–28 |
| `Mon` … `Sun` (без суффикса) | 4 | #3, #12 (Marriage) |
| `Mon2` … `Sun2` | 0 дублей | только #3 |
| `Mon4` … `Sun4` | 0 дублей | #3 (формально) + #5 |
| `Mon6` … `Sun6` | 0 дублей | #3 + #5 |
| `Mon8` … `Sun8` | 7 | #6, #11 |
| `Mon10` … `Sun10` | 7 | #6, #11 |
| `GreenRain`, `GreenRain_2` | 2 | #3, #5, #6, #11 |
| `timeReaction_*` | 3 | #3, #5, #6, #11 |
| `locationReaction_*` | 2 | #3, #5, #6, #11 |
| `emotionalReaction_*` | 2 | #3, #5, #6, #11 |
| `situationReaction_*` | 3 | #3, #5, #6, #11 |
| `Resort_*` | 6 | #5, #6, #11, #12 |
| `AcceptGift_*` / birthday | 50 | #7, #8, #9, #10, #11 |
| Сезонные / фестивальные | много | `spring_12`: #3, #5, #11, #12, #30; `spring_14`: + #6; `winter_24`: #3, #5, #11, #12, #30 |

### 3.2 Критичные конфликты (примеры)

| Ключ | Конкурирующие When | Риск |
|------|-------------------|------|
| `Hospital_Mon` | strict #4 / friends #5 / 8–10 #6 / Dating #11 / trauma #13–16 / firstMeeting #17–20 / exhaustion #25–28 / Marriage location | На 8 ❤ + `topicHarveyExhaustion` побеждает **последний** подходящий блок (сейчас #28 — мягче, чем старый «без возражений») |
| `timeReaction_VeryLate` | #3 (mix), #5, #6, #11 (creepy + «котёнок») | На Dating — принуждение и pet names |
| `Mon` | #3 vs #12 | Разный Target, но игрок married слышит Marriage `Mon`, не базовый |
| `topicHarveySecondVisitAgree` | #3 и #31 | #31 без When → глобальный override с mix «Вы/ты» |
| `AcceptBirthdayGift_Positive` | #7–#11 | На Dating — «солнышко» в #11, не в отдельном 8–10 блоке |

---

## 4. Смешение «Вы» и «ты» в одной реплике

Автопоиск: **Вы/Вас/Вам/Ваш/Ваше/Ваши** + **ты/тебя/тебе/твой/…/доверяешь/помолчи/помни**.

| Блок | When | Ключ | Суть |
|------|------|------|------|
| 31 | *(нет)* | `topicHarveySecondVisitAgree` | «**Вы** согласилась… **Вам**…» → «просто **помолчи** рядом» |
| 31 | *(нет)* | `topicHarveySecondVisitRefused` | «**Вы** не готовы… **Вам**…» → «**помни**: если **Вам**…» |

**Дополнительно (не в автосчётчике, но критично):**

| Блок | Ключ | Проблема |
|------|------|----------|
| 3 | `timeReaction_VeryLate` | «**Вы**… отведу **Вас**» → «там **ты** сможешь» |
| 11 | `topicHarveyNotOnlyPatient` | `Relationship=Dating`, но «**Не пугайтесь**» (Вы) |
| 7 | `AcceptGift_(O)432` | «**Вы** всё-таки…» + «сама не **пропустишь**» (ты) — разные лица в одной реплике |
| 3 | `Mon`–`Sun` | строчное «вы/ваш» при общей линии 0–2 ❤ на «**Вы**» |

`topicHarveyWalkGood` (#21–24): стадии разделены ✓, смешения в `fourweeks` **нет** (в отличие от старых версий файла).

---

## 5. Проблемные фразы (триггер-лист)

Подсчёт вхождений по **всем 31 блокам** (скрипт `scripts/audit_dialogues_harvey.py`). Один ключ может дать несколько триггеров.

| Триггер | ~Вхождений | Где концентрировано |
|---------|------------|---------------------|
| малышка | 117 | #12 Marriage, #30 FarmHouse, #11 Dating, schedule #2 |
| солнышко | 86 | Marriage, FarmHouse, Dating gifts/reactions |
| я прослежу | 66 | #5, #6, #11, #12, #30, topics |
| девочка моя | 59 | Married gifts #10, Marriage #12 |
| котёнок | 47 | Married gifts, Marriage, schedule, Dating `timeReaction_VeryLate` |
| я не дам | 45 | Dating reactions, #5, #6, Marriage |
| ты рядом со мной | 8 | Dating, topics, `jobLeave` Marriage |
| не спорь | 8 | #5 `winter_Wed`, #11 Dating, #12 `Forest_8_18` |
| под моим контролем / всё под контролем | 8 | #6 `Beach10`, #11, Storm #29, FarmHouse |
| без возражений | 1 | #11 Dating `spring_14` |
| открой ротик | 1 | #11 Dating `spring_Tue` |
| кормит с ложки | 1 | #6 `Saloon10` (8–10 ❤) |
| только моя | 3 | #6 `spring_14`, #11 `summer_Sun`, #12 `winter_24` |
| я всегда рядом, даже ночью | 2 | #6 `Hospital10`, #30 `spring_28` |
| **это не обсуждается** | **0** | — |

### 5.1 Примеры наиболее проблемных реплик

**Dating #11, `timeReaction_VeryLate`:**  
«Глубокая ночь, **котёнок**… **Я не дам** тебе остаться одной… **не спорь**…»

**Dating #11, `timeReaction_Late`:**  
«…**не спорь со мной**… **не оставлю** одну… **Ты рядом со мной**.»

**Базовый #3, `timeReaction_VeryLate`:**  
формальное сопровождение в клинику + внутренняя смена на «ты».

**Marriage #12, `jobLeave`:**  
«твой личный номер спасения — это я… **Ты рядом со мной**, даже если меня нет рядом».

**FarmHouse #30, `spring_3` (типичный паттерн):**  
забор инструментов, сказка на ночь, тотальный контроль быта.

**topicHarveyExhaustion (#25–28):**  
уже переписан в сторону «если согласитесь / без отчёта» — **эталон** для остальных hospital-topics.

---

## 6. Логические несоответствия по стадиям

| Стадия | Ожидание | Факт в файле |
|--------|----------|--------------|
| 0–2 ❤ | «Вы», врач, без романтики | В основном ✓ (#3, #7); но базовые `spring_*`, visit #31, длинные `topicHarvey*` без стадии |
| 3–5 ❤ | «ты», без pet names | ✓ #8; блок #5 доступен с **4** ❤ с «не отпущу», «не спорь» |
| 6–7 ❤ | тепло, без infantilization | Пересекается с #4 strict hospital и #5 «4–7» |
| 8–10 до букета | близость, не marriage | #6 мягче Dating; отдельного «8–10 не dating» для реакций **нет** — только hearts |
| Dating | романтика без принуждения | ✗ блок #11 = 182 ключа, дублирует 8–10 с control + pet names |
| Married | умеренная близость | ✗ #12 + #30: surveillance, pet name в каждой строке |
| Medical topics | коротко, по стадии | Часть в #3 без `When`; trauma/firstMeeting ещё жёстче exhaustion |

---

## 7. Правила тона по уровням отношений (целевые)

### 0–2 сердца
- **«Вы»** последовательно (с заглавной).
- Роль: врач / главный медик, протокол, дистанция.
- **Запрещено:** pet names, «я прослежу», романтика, «ты рядом со мной», обещания «даже ночью».
- Длина: 1–3 предложения + одна рекомендация.

### 3–5 сердец
- **«ты»** после установления контакта (переход можно один раз обозначить в событии).
- Тон: мягкое доверие, **предложения**, не приказы.
- **Запрещено:** «малышка», «котёнок», «не спорь», контроль расписания игрока.
- Медицина: «если захочешь — зайди на осмотр».

### 6–7 сердец
- **«ты»**, теплее; допустимо «я волнуюсь».
- **Запрещено:** infantilization, «карантин», «я заберу инструменты».
- Допустимо: «я рядом, если попросишь»; чай **по приглашению**.

### Dating
- **«ты»**; **«солнышко»** — редко (1–2 на категорию, не в каждой строке).
- Романтика: да; **принуждение — нет** (убрать «не спорь», «не оставлю одной», «никаких возражений», «открой ротик»).
- Нет «Вы» в dating-репликах; нет дублирования всего 8–10 блока без отсечения по hearts.

### Married
- **«ты»**; «котёнок / девочка моя» — **точечно** (гроза, подарки, утешение), не в location-barks.
- Без surveillance: трекеры, «холодильник под замком», SPF каждые 40 минут в каждом `Outdoor_*`.
- FarmHouse seasonal: **короткая** забота, не 110 монологов.

### Медицинские topic-реплики
- Короткие: симптом → действие → optional follow-up.
- Не повторять «бледная, испуганная, уставшая» в каждом `Hospital_*`.
- **Обязательный `When`** по стадии (как #21–28 для walk/exhaustion).
- Один topic — одна эмоциональная нота, не 7× `Hospital_Mon`–`Sun` без нужды.

---

## 8. Предлагаемый порядок маленьких PR

Каждый PR: только `dialoguesHarvey.json` (или будущий split-файл), **без** автоформаттера, **без** массовой замены «Вы»→«ты», **без** C#.

| PR | Scope | ~Объём | Критерий готовности |
|----|--------|--------|---------------------|
| **PR-0** | Техника: убрать второй `When` в #5; перенести `When` **перед** `Entries` в #11–#12; **удалить или стадировать** блок #31 | 6–10 строк структуры | 3 ❤ снова получают блок #5; visit-topics не глобальны |
| **PR-1** | `topicHarveyTraumaReveal` (#13–16): убрать «ночью на связи», «под контролем», «не дам страхам»; выровнять «Вы/ты» | ~16 ключей | Как exhaustion: коротко, по стадии |
| **PR-2** | `topicFirstMeeting` (#17–20): убрать «не спорьте», «прослежу чтобы съели», шаблон «испуганная девушка» | ~32 ключа | 0–2 только «Вы», dating без «Вы» |
| **PR-3** | Базовый #3: `timeReaction_*` + `Mon`–`Sun` — вынести в heart-блоки или убрать дубли; исправить mix в `timeReaction_VeryLate` | ~10 ключей | Нет fallback-реакций на всех стадиях |
| **PR-4** | Gifts #7–10: убрать дубли из #11; dating gifts отдельно от «солнышко в каждой строке» | 50×4 | На 0–2 нет «пропустишь»; married pet names ≤30% реплик |
| **PR-5** | `Hearts=4,5,6,7` (#5): смягчить «не отпущу», «не спорь», GreenRain, resort | ~30 ключей | Предложения вместо запретов |
| **PR-6** | `Hearts=8,9,10` (#6): убрать «кормит с ложки», «только моя», «под контролем»; укоротить монологи | ~25 ключей | Близость без marriage-тона |
| **PR-7** | Strict hospital #4 (`6–10` clinic): клинический тон без «карантин для всех» | 24 ключа | Не конфликтует с exhaustion topic |
| **PR-8** | **Dating #11** (самый большой): реакции + сезон; убрать creepy; `topicHarveyNotOnlyPatient` → «ты» | ~80–100 ключей | Нет «не спорь», «котёнок» в night reactions |
| **PR-9** | `MarriageDialogueHarvey` #12: сократить pet names, location-barks, `Indoor_Night_*` | 113 ключей | ≤1 ласковое обращение на 3 реплики |
| **PR-10** | FarmHouse #30: сократить 110 → ~28 (1 на день сезона) или вынести в отдельный файл | 110 ключей | Нет «забронировал сауну»/датчиков в каждом дне |
| **PR-11** | Storm rainy #29 + schedule #1–2 | 17 ключей | Married schedule без «малышка» на работе |
| **PR-12** | Базовый #3: `topicHarvey*` Injury — стадии `_Stranger` / `_Friend` / `_Dating` / `_Married` (как в `dialoguesHarveyCure.json`) | ~60 ключей | Медицина короткая, без драмы каждый день |

**Порядок загрузки CP (целевой):** base (формальное) → hearts ↑ → gifts → hospital strict → topics (самый узкий `When` последним) → dating → married.

**После PR-0…PR-3** имеет смысл прогон в игре / Injury MCP по чеклисту `docs/testing/main-injury-testcases.md` (клик Харви при разных ❤ и topics).

---

## 9. Связанные файлы (вне scope)

Не аудировались; для единой системы отношений учитывать отдельно:

- `dialoguesHarveyCure.json`, `dialoguesHarveyInjury.json` — стадии Stranger/Dating/Married
- `dialoguesHarveyStress.json`, `buffsMedicalCare.json`
- C#: `HarveyRelationshipStage`, фильтр формальных маркеров — см. `docs/harvey-treatment-relationship-fix-report.md`

---

## Приложение: повторный аудит

Read-only скрипт (не меняет JSON):

```bash
python scripts/audit_dialogues_harvey.py
```

Создаёт вспомогательный `docs/_audit_dialogues_harvey_data.json` (можно не коммитить).

---

*Следующий шаг по запросу: **PR-0** (техника JSON + блок #31), затем **PR-1** / **PR-2** (topic-блоки).*
