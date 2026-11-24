from app.matching import match
from app.seed_data import COURSES, make_seed, students_for_course


def test_seed_is_reproducible():
    assert make_seed(7) == make_seed(7)


def test_seed_shape_and_privacy():
    data = make_seed()
    assert len(data["students"]) == 40
    assert len(COURSES["AP Calculus AB"]) == 8
    allowed = {"id", "first_name", "pref_noise", "pref_time", "pref_camera_on", "slots", "courses", "ratings"}
    for s in data["students"]:
        assert set(s) == allowed  # no extra personal fields sneak in
        assert s["pref_camera_on"] is False
        assert all(8 <= hour <= 21 for _, hour in s["slots"])


def test_every_course_produces_matches():
    data = make_seed()
    for course in COURSES:
        students = students_for_course(data, course)
        assert len(students) >= 4
        assert len(match(students)) >= len(students) // 3
