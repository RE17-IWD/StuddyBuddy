"""Greedy vs. maximum weight matching, for the Devpost writeup.

Usage (from the repo root):
    python scripts/compare_matching.py
    python scripts/compare_matching.py --trials 500

Part 1 runs both methods on the demo data (seed 2026).
Part 2 repeats it on many random fake classes, because on any single class
the two methods can tie, and judges will want to know how often max-weight wins.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.matching import greedy_match, match  # noqa: E402
from app.seed_data import COURSES, make_seed, students_for_course  # noqa: E402


def summarize(pairs: list[dict]) -> dict:
    n = len(pairs)
    return {
        "matched": 2 * n,
        "total": sum(p["score"] for p in pairs),
        "swap": sum(p["breakdown"]["swap"] for p in pairs) / n if n else 0.0,
    }


def compare(students: list[dict]) -> tuple[dict, dict]:
    return summarize(greedy_match(students)), summarize(match(students))


def print_demo_table() -> None:
    data = make_seed()
    header = f"{'Course':<16}{'Students':>9}  {'Matched (G / M)':>16}  {'Total score (G / M)':>20}  {'Avg swap (G / M)':>17}"
    print("Demo data (seed 2026). G = greedy, M = max-weight\n")
    print(header)
    print("-" * len(header))
    totals = {"n": 0, "g": 0, "m": 0}
    for course in COURSES:
        students = students_for_course(data, course)
        g, m = compare(students)
        totals["n"] += len(students)
        totals["g"] += g["matched"]
        totals["m"] += m["matched"]
        print(
            f"{course:<16}{len(students):>9}  "
            f"{g['matched']:>7} / {m['matched']:<6}  "
            f"{g['total']:>9.2f} / {m['total']:<8.2f}  "
            f"{g['swap']:>7.3f} / {m['swap']:<7.3f}"
        )
    print("-" * len(header))
    print(f"{'All courses':<16}{totals['n']:>9}  {totals['g']:>7} / {totals['m']:<6}\n")


def print_trials(trials: int) -> None:
    more_students = fewer_students = higher_score = 0
    extra_students = 0
    score_gain = 0.0
    classes = 0
    for seed in range(trials):
        data = make_seed(seed=seed, num_students=24)
        for course in COURSES:
            students = students_for_course(data, course)
            if len(students) < 4:
                continue
            g, m = compare(students)
            classes += 1
            if m["matched"] > g["matched"]:
                more_students += 1
                extra_students += m["matched"] - g["matched"]
            elif m["matched"] < g["matched"]:
                fewer_students += 1
            if m["total"] > g["total"] + 1e-9:
                higher_score += 1
                score_gain += (m["total"] - g["total"]) / g["total"] if g["total"] else 0

    print(f"Random fake classes: {classes} (from {trials} seeds)\n")
    print(f"  Max-weight matched MORE students in {more_students} classes "
          f"({100 * more_students / classes:.0f}%), {extra_students} extra students in total.")
    print(f"  Max-weight had a HIGHER total score in {higher_score} classes "
          f"({100 * higher_score / classes:.0f}%), "
          f"+{100 * score_gain / max(higher_score, 1):.1f}% on average when it did.")
    print(f"  Max-weight matched FEWER students in {fewer_students} classes.")
    print("  Max-weight never has a lower total score: it is the best possible total by definition.")


def main() -> None:
    trials = 200
    if "--trials" in sys.argv:
        trials = int(sys.argv[sys.argv.index("--trials") + 1])
    print_demo_table()
    print_trials(trials)


if __name__ == "__main__":
    main()
