"""Все проверки Content Patcher-пака одной командой. Код выхода 1, если хоть одна не прошла.

  validate_story_events   — ссылки сюжета: события, темы, письма, GameStateQuery
  validate_event_coords   — координаты на реальных картах (SVE, Alchemistry, ферма, дом, музей)
  audit_event_exits       — setSkipActions и выход из сцен (HIGH и MEDIUM должны быть 0)
  final_technical_validation — JSON как в CP, дубли ключей, ласковые имена до отношений
  validate_herbal_garden — травы, рецепты, цепочка поручений и игровой атлас роста
  fix_skip_actions --dry  — в ручных событиях нечего чинить

Запуск:  python scripts/check_all.py      (deploy.sh вызывает его до сборки)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

CHECKS = [
    ("регрессии постановки", ["test_event_staging.py"], lambda out: out.strip().endswith('OK')),
    ("день рождения, Зузу и переходы между картами", ["validate_outings.py"], lambda out: "Outings: all checks passed." in out),
    ("спрайты и поведение Аренда", ["validate_arend_behaviour.py"], lambda out: "Arend behaviour: all checks passed." in out),
    ("погода и доступность первого осмотра", ["validate_intro_recovery.py"], lambda out: "Intro recovery: all checks passed." in out),
    ("семья, памятные вещи и годовщины", ["validate_family_life.py"], lambda out: "Family life: all static checks passed." in out),
    ("аптекарский сад", ["validate_herbal_garden.py"], lambda out: "Herbal garden: all static checks passed." in out),
    ("сюжет", ["validate_story_events.py"], lambda out: out.strip().splitlines()[-1:] == ["OK"]),
    ("координаты", ["-I", "validate_event_coords.py"], lambda out: re.search(r"замечаний: 0\b", out)),
    ("ветки, маршруты, анимации и варианты комнаты", ["validate_event_staging.py"], lambda out: "issues: 0" in out),
    ("пропуск и выход из сцен", ["-I", "audit_event_exits.py"], lambda out: re.search(r"HIGH 0, MEDIUM 0\b", out)),
    ("JSON и тон", ["final_technical_validation.py"],
     lambda out: re.search(r"JSON errors: 0, dup keys: 0, pet: 0\b", out)),
    ("setSkipActions в ручных файлах", ["-I", "fix_skip_actions.py", "--dry"], lambda out: not out.strip()),
]


def run(args):
    cmd = [sys.executable, *[os.path.join(HERE, a) if a.endswith(".py") else a for a in args]]
    proc = subprocess.run(cmd, cwd=os.path.dirname(HERE), env=ENV, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout + proc.stderr


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    failed = []
    for title, args, ok in CHECKS:
        code, out = run(args)
        passed = code == 0 and bool(ok(out))
        print(f"[{'OK' if passed else 'FAIL'}] {title}")
        if not passed:
            failed.append(title)
            for line in out.strip().splitlines()[-15:]:
                print(f"       {line}")
    if failed:
        print(f"\nНе прошло: {', '.join(failed)}")
        return 1
    print("\nВсе проверки пройдены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
