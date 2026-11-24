"""Print a summary of the fake demo data.

Usage (from the repo root):
    python scripts/seed.py            # summary
    python scripts/seed.py --json     # full data as JSON

Writing the data into Supabase comes in Phase 3 (admin "Seed data" button).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.seed_data import make_seed  # noqa: E402


def main() -> None:
    data = make_seed()
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
        return

    students = data["students"]
    print(f"School: {data['school']['name']}")
    print(f"Students: {len(students)} (fake first names only)\n")
    for course, units in data["courses"].items():
        enrolled = [s for s in students if course in s["courses"]]
        print(f"{course}: {len(units)} units, {len(enrolled)} students")
    avg_hours = sum(len(s["slots"]) for s in students) / len(students)
    print(f"\nAverage free hours per student: {avg_hours:.1f}")


if __name__ == "__main__":
    main()
