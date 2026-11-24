"""Fake demo data: one school, three courses, about 40 students.

Pure functions, no database. `make_seed()` always returns the same data for
the same seed number, so the demo and the Devpost numbers are reproducible.
Writing this data into Supabase comes in Phase 3 (admin "Seed data" button).

Only fake first names. No emails, ages, last names, or anything personal.
"""

from __future__ import annotations

import random

SCHOOL = {"name": "Maple Ridge High (demo)", "email_domain": "demo.studyswap.xyz"}

# Official College Board unit names, in course order.
COURSES = {
    "AP Calculus AB": [
        "Limits and Continuity",
        "Differentiation: Definition and Fundamental Properties",
        "Differentiation: Composite, Implicit, and Inverse Functions",
        "Contextual Applications of Differentiation",
        "Analytical Applications of Differentiation",
        "Integration and Accumulation of Change",
        "Differential Equations",
        "Applications of Integration",
    ],
    "AP Chemistry": [
        "Atomic Structure and Properties",
        "Molecular and Ionic Compound Structure and Properties",
        "Intermolecular Forces and Properties",
        "Chemical Reactions",
        "Kinetics",
        "Thermodynamics",
        "Equilibrium",
        "Acids and Bases",
        "Applications of Thermodynamics",
    ],
    "AP Biology": [
        "Chemistry of Life",
        "Cell Structure and Function",
        "Cellular Energetics",
        "Cell Communication and Cell Cycle",
        "Heredity",
        "Gene Expression and Regulation",
        "Natural Selection",
        "Ecology",
    ],
}

FIRST_NAMES = [
    "Alex", "Sam", "Priya", "Jordan", "Mei", "Diego", "Ava", "Noah", "Zara", "Leo",
    "Hana", "Omar", "Ivy", "Theo", "Maya", "Kofi", "Lena", "Ravi", "Sofia", "Eli",
    "Nia", "Mateo", "Aisha", "Ben", "Chloe", "Dev", "Emma", "Finn", "Grace", "Hugo",
    "Isla", "Jin", "Kai", "Lucia", "Marcus", "Nora", "Oscar", "Rosa", "Tariq", "Yuki",
]


def _ratings(rng: random.Random, units: list[str]) -> dict[str, int]:
    """Ratings with a deliberate lean, so complementary pairs exist.

    Each student leans strong in either the early or the late units of the
    course (like real students who "got" the first half but not the second),
    with some randomness on top.
    """
    leans_early = rng.random() < 0.5
    half = len(units) // 2
    ratings = {}
    for i, unit in enumerate(units):
        in_strong_half = (i < half) == leans_early
        roll = rng.random()
        if in_strong_half:
            ratings[unit] = 3 if roll < 0.55 else 2 if roll < 0.9 else 1
        else:
            ratings[unit] = 1 if roll < 0.5 else 2 if roll < 0.85 else 3
    return ratings


def _availability(rng: random.Random, pref_time: str) -> list[tuple[int, int]]:
    """Mostly after-school blocks on weekdays, shaped by the time preference."""
    slots = set()
    weekdays = rng.sample(range(5), k=rng.randint(2, 4))
    for day in weekdays:
        if pref_time == "evening":
            start = rng.randint(17, 19)
        else:
            start = rng.randint(15, 17)
        for hour in range(start, min(start + rng.randint(1, 3), 22)):
            slots.add((day, hour))
    # Morning people and some others also study on weekend mornings.
    if pref_time == "morning" or rng.random() < 0.3:
        day = rng.choice([5, 6])
        start = rng.randint(9, 11)
        slots.update({(day, start), (day, start + 1)})
    return sorted(slots)


def make_seed(seed: int = 2026, num_students: int = 40) -> dict:
    rng = random.Random(seed)
    course_names = list(COURSES)
    students = []
    for i in range(num_students):
        pref_time = rng.choice(["afternoon", "afternoon", "evening", "morning"])
        # Everyone takes Calc so the main demo course is full; many take a second course.
        courses = ["AP Calculus AB"]
        if rng.random() < 0.7:
            courses.append(rng.choice(course_names[1:]))
        students.append({
            "id": f"demo-{i + 1:02d}",
            "first_name": FIRST_NAMES[i % len(FIRST_NAMES)],
            "pref_noise": "quiet" if rng.random() < 0.6 else "talk",
            "pref_time": pref_time,
            "pref_camera_on": False,
            "slots": _availability(rng, pref_time),
            "courses": courses,
            "ratings": {c: _ratings(rng, COURSES[c]) for c in courses},
        })
    return {"school": SCHOOL, "courses": COURSES, "students": students}


def students_for_course(data: dict, course: str) -> list[dict]:
    """Convert seed students into the dicts that matching.py expects."""
    return [
        {
            "id": s["id"],
            "name": s["first_name"],
            "ratings": s["ratings"][course],
            "slots": set(s["slots"]),
            "noise": s["pref_noise"],
            "time": s["pref_time"],
            "blocked": set(),
            "declined": set(),
        }
        for s in data["students"]
        if course in s["courses"]
    ]
