# Audit: обращение Вы/ты (after fix)

**Дата:** 2026-05-25  
**Скрипты:** `scripts/audit_vy_ty.py`, `scripts/fix_vy_mixed.py`  
**C# messages:** в репозитории `[CP]` не найдены (только Content Patcher JSON).

## Сводка

- **Документированных правок (основные блоки):** ~15 категорий / ~280+ ключей суммарно по проходам
- **Оставшихся нарушений после fix:** 0
- **Trust-arc exceptions (без правки):** 29

### Правила gate

| Условие | Обращение |
|---------|-----------|
| Ungated / 0–2 ❤ / FP < 750 | **Вы** |
| 3+ ❤ / FP ≥ 750 | **ты** |
| Dating / Married / Pregnant | **ты** (кроме намеренной формальности) |
| Trust-arc keys (см. ниже) | **Вы** или mixed — осознанно |

### Осознанные исключения (trust-arc, «Вы» сохранено)

| Паттерн ключей | Причина |
|----------------|---------|
| `topicHarveyTrust_*` | Event-gated trust arc — границы и согласие |
| `topicHarveyStorm_*`, `topicHarveyDoorSignal_*` | Storm/safety trust protocol |
| `topicHarveyBadDay_*`, `topicHarveyHelp_*`, `topicHarveyMines_*` | Post-event trust topics |
| `topicHarveyWalk*`, `topicHarveyApology*`, `topicHarveyNeedsSpace` | First walk / opt-out arc |
| `HarveyOverhaul_E*`, story events | Story mail/events ladder 0→2b |
| `mailHarveyStorm_*` | Storm trust mail |

## Таблица правок (основные)

| Файл | Ключ/Event | Gate | Было | Стало | Комментарий |
|------|------------|------|------|-------|-------------|
| assets/Code/dialoguesHarvey.json | spring_12 … winter_Sun (ungated) | ungated | ты | Вы | сезонные/дневные реплики 0–2 ❤ fallback |
| assets/Code/dialoguesHarvey.json | timeReaction_* / locationReaction_* / emotionalReaction_* | ungated | ты | Вы | реакции без heart-gate |
| assets/Code/dialoguesHarvey.json | AcceptGift_* / AcceptBirthdayGift_* | Hearts:Harvey=0,1,2 | ты | Вы | gift reactions 0–2 ❤ |
| assets/Code/dialoguesHarvey.json | Hospital2 | Hearts:Harvey=6,7,8,9,10 | Вы | ты | строгий блок 6+ ❤ |
| assets/Code/dialoguesHarvey.json | OneKid_0 / OneKid_3 / TwoKids_3 | Relationship:Harvey=Married | смешанное | ты | married — только «ты» |
| assets/Code/dialoguesHarvey.json | Hospital_* / Town / Saloon / Beach | HasConversationTopic=topicFirstMeeting | смешанное | Вы | trust-adjacent early arc — формальное «Вы» |
| assets/Code/dialoguesHarvey.json | Hospital_* / Saloon | HasConversationTopic=topicHarveyExhaustion | смешанное | Вы | post-exhaustion care — «Вы» до 3 ❤ |
| assets/Code/dialoguesHarvey.json | topicHarvey_ForcedHospitalization | ungated | Дыши (ty) | Дышите | ungated fallback |
| assets/Code/dialoguesHarveyStress.json | topicStress* (ungated block) | ungated | смешанное | Вы | stress intake 0–2 ❤ |
| assets/Code/dialoguesHarveyStress.json | topicStress* (Hearts 3+ block) | Hearts:Harvey=3+ | Вы | ты | stress care 3+ ❤ |
| assets/Code/dialoguesHarveyInjury.json | selected entries | Hearts gates | смешанное | по gate | injury layers 0–2 / 3+ |
| assets/Code/dialoguesHarveyPregnant.json | selected entries | Pregnant/Married | смешанное | ты | pregnant arc |
| assets/Code/mailInjury.json | HarveyMod_* | ungated | смешанное | Вы | injury mail early stage |
| assets/Code/quest_dialogues.json | quest lines | mixed gates | смешанное | по gate | quest Harvey lines |
| assets/Code/quest_dialogues.json | HarveyMod_CollapseRehabilitationStart | ungated | ТЫ/смешанное | Вы | collapse emergency — формальное «Вы» |

## Trust-arc (оставлено без правки)

| Файл | Ключ/Event | Gate | Обращение |
|------|------------|------|-----------|
| assets/Code/dialoguesHarvey.json | topicHarveyDeclineFirstWalk | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyWalkGood | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyWalkNeutral | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyWalkBad | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyAcceptFirstWalk | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_Breakfast | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_DoctorDecides | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_TouchOk | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_BreathHard | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyStorm_Note | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyStorm_Escort | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyDoorSignal_Close | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_FullExam | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyTrust_LeftClinic | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyApologyAccepted | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyQuietFiveMinutes | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyNeedsSpace | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveySafetyKit_Door | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveySafetyKit_Kitchen | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveySafetyKit_NoKit | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyMines_Note | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyHelp_Asks | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyHelp_Spotter | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyHelp_Independent | ungated | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyBadDay_Silent | Relationship:Harvey=Dating | ты |
| assets/Code/dialoguesHarvey.json | topicHarveyBadDay_Water | Relationship:Harvey=Dating | ты |
| assets/Code/dialoguesHarvey.json | topicHarveyBadDay_NoQuestions | Relationship:Harvey=Dating | ты |
| assets/Code/dialoguesHarvey.json | topicHarveyNotOnlyPatient | Relationship:Harvey=Dating | Вы |
| assets/Code/dialoguesHarvey.json | topicHarveyFuturePlan_CheckIn | Relationship:Harvey=Married | ты |
