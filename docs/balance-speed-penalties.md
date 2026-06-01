# Balance: speed penalties (buffs)

Смягчены штрафы к скорости в Content Patcher (`HarveyOverhaul [CP]`). Проекты `HarveyOverhaulInjury` и `HarveyStressMeter` (C#) в рабочей копии не найдены — если там есть динамические модификаторы скорости, их нужно проверить отдельно в исходниках.

| Бафф | Было Speed | Стало Speed | Причина |
|---|---:|---:|---|
| `HarveyMod_Cold_Acute` | -2 | — | cold: no speed penalty |
| `HarveyMod_Cold_Recovery` | -1 | — | cold: no speed penalty |
| `HarveyMod_Concussion_Acute` | -2 | Speed -1 | critical care cap -1 |
| `HarveyMod_FracturedBone_Acute` | -2 | Speed -1 | critical care cap -1 |
| `HarveyMod_ImpairedMobility` | -3 | Speed -1 | leg/mobility injury max -1 |
| `HarveyMod_Prescription_Rest` | -0.5 | — | prescription rest: no fractional speed |
| `HarveyMod_Sepsis` | -4 | Speed -1 | heavy injury cap -1 |
| `HarveyMod_TornMuscles_Acute` | -2 | Speed -1 | critical care cap -1 |
| `buffAlcoholPoisoning` | -15 | Speed -1 | heavy injury cap -1 |
| `buffBackStrain` | -2 | — | light injury: no movement speed penalty |
| `buffBruisedRibs` | -2 | — | light injury: no movement speed penalty |
| `buffCold` | -2 | — | cold: no speed penalty |
| `buffConcussion` | -3 | MovementSpeed -1 | medium injury cap -1 |
| `buffConstantSupervision` | -3 | Speed -1 | critical care cap -1 |
| `buffDeepCuts` | -2 | MovementSpeed -1 | medium injury cap -1 |
| `buffEmergencySupervision` | -5 | Speed -1 | critical care cap -1 |
| `buffForcedSedation` | -10 | Speed -1 | critical care cap -1 |
| `buffFracturedBone` | -5 | MovementSpeed -1 | leg/mobility injury max -1 |
| `buffHarveyRehab` | -1 | — | rehab: stamina-only reminder |
| `buffPainFlare` | -3 | Speed -1 | heavy injury cap -1 |
| `buffPostSurgicalCare` | -5 | Speed -1 | critical care cap -1 |
| `buffShrapnelWounds` | -4 | MovementSpeed -1 | medium injury cap -1 |
| `buffSleepDeprivation` | -1 | — | stress: no speed penalty |
| `buffSprainedAnkle` | -3 | MovementSpeed -1 | leg/mobility injury max -1 |
| `buffStressBadDream` | -1 | — | stress: no speed penalty |
| `buffStressBreakdown` | -3 | — | stress: no speed penalty |
| `buffStressBurnout` | -2 | — | stress: no speed penalty |
| `buffStressCollapse` | -5 | — | stress: no speed penalty |
| `buffStressCritical` | -4 | — | stress: no speed penalty |
| `buffStressCriticalExhaustion` | -5 | — | stress: no speed penalty |
| `buffStressDespair` | -3 | — | stress: no speed penalty |
| `buffStressDespairCollapse` | -5 | — | stress: no speed penalty |
| `buffStressExhaustion` | -3 | — | stress: no speed penalty |
| `buffStressFreezeResponse` | -3 | — | stress: no speed penalty |
| `buffStressHunger` | -1 | — | stress: no speed penalty |
| `buffStressLonely` | -1 | — | stress: no speed penalty |
| `buffStressMentalBreakdown` | -3 | — | stress: no speed penalty |
| `buffStressMentalFatigue` | -2 | — | stress: no speed penalty |
| `buffStressNightTerror` | -1 | — | stress: no speed penalty |
| `buffStressNoSleep` | -2 | — | stress: no speed penalty |
| `buffStressNumbness` | -2 | — | stress: no speed penalty |
| `buffStressOverwork` | -2 | — | stress: no speed penalty |
| `buffStressPanic` | -3 | — | stress: no speed penalty |
| `buffStressPanicBreakdown` | -3 | — | stress: no speed penalty |
| `buffStressPanicCollapse` | -4 | — | stress: no speed penalty |
| `buffStressParanoidCollapse` | -4 | — | stress: no speed penalty |
| `buffStressPhysicalDepletion` | -2 | — | stress: no speed penalty |
| `buffStressShadowParanoia` | -3 | — | stress: no speed penalty |
| `buffStressTooCold` | -2 | — | stress: no speed penalty |
| `buffStrictSupervision` | -1 | — | supervision: mobility via stamina/health buff |
| `buffTornMuscles` | -4 | MovementSpeed -1 | medium injury cap -1 |

## Приоритетные баффы (проверка)

| Бафф | Штраф скорости после правки |
|---|---|
| `buffStressNoSleep` | нет |
| `buffStressHunger` | нет |
| `buffStressTooCold` | нет |
| `buffStressThunder` | **+1** (без изменений; паника/адреналин) |
| `buffStressDarkness` | нет (только Defense) |
| `buffStressOverwork` | нет |
| `buffStressTired` | нет |
| `buffStressLonely` | нет |
| `buffStressSocial` | нет (только Defense) |
| `buffHurt` / `buffBadlyHurt` | нет |
| `buffDeepCuts` / `buffBurnWounds` / `buffTornMuscles` | MovementSpeed **-1** |
| `buffSprainedAnkle` / `buffFracturedBone` | MovementSpeed **-1** |
| `buffConcussion` / `buffShrapnelWounds` | MovementSpeed **-1** |
| `buffHarveyIntensiveCare` | **+1** (лечебный бафф, не дебафф) |
| `HarveyMod_WetBandage` / `HarveyMod_DirtyWound` / `buffInfectedWound` | Speed **-1** (без изменений) |

## Файлы

- `assets/Code/buffsStress.json` — стресс: убраны все отрицательные Speed
- `assets/Code/buffsInjury.json` — травмы: cap MovementSpeed/Speed до **-1**
- `assets/Code/buffsCure.json` — фазы лечения и наблюдение: cap до **-1**
- `assets/Code/buffsMedicalCare.json` — рецепт отдыха: убран дробный Speed **-0.5**

Скрипт: `scripts/balance_speed_penalties.py` (повторный прогон не перезаписывает этот документ, если JSON уже исправлен).

## HarveyOverhaulInjury / HarveyStressMeter

Исходники C# в этой рабочей копии отсутствуют (установлены как DLL). Если в репозитории есть динамическое `player.Speed` / `BuffAttributes.Speed`, примените те же лимиты: стресс **0**, травмы **не ниже -1**.
