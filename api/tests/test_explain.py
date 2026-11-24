from app.explain import explain, format_range, join_words, match_label, slot_ranges


def breakdown(**overrides):
    base = {
        "a_teaches": ["Limits", "Derivatives"],
        "b_teaches": ["Integrals"],
        "shared_slots": [(1, 16), (1, 17), (3, 17)],
        "shared_noise": "quiet",
        "shared_time": "afternoon",
    }
    base.update(overrides)
    return base


def test_full_explanation_matches_plan_example():
    text = explain(breakdown(), "Sam")
    assert text == (
        "You're strong in Limits and Derivatives, and Sam is strong in Integrals. "
        "You're both free Tue 4–6pm and Thu 5–6pm. "
        "You both prefer quiet study in the afternoon."
    )


def test_viewer_b_sees_the_swap_flipped():
    text = explain(breakdown(), "Alex", viewer="b")
    assert text.startswith("You're strong in Integrals, and Alex is strong in Limits and Derivatives.")


def test_one_way_wording():
    assert "where Sam wants help" in explain(breakdown(b_teaches=[]), "Sam")
    assert "Sam is strong in Integrals, where you want help" in explain(breakdown(a_teaches=[]), "Sam")


def test_style_sentence_variants():
    assert explain(breakdown(shared_time=None), "Sam").endswith("You both like quiet study.")
    assert explain(breakdown(shared_noise=None), "Sam").endswith("You both like studying in the afternoon.")
    assert explain(breakdown(shared_noise=None, shared_time=None), "Sam").endswith("Thu 5–6pm.")


def test_time_ranges():
    assert format_range(16, 18) == "4–6pm"
    assert format_range(11, 13) == "11am–1pm"
    assert format_range(9, 11) == "9–11am"
    # Slots from JSON arrive as lists, not tuples.
    assert slot_ranges([[0, 15], [0, 16], [0, 18]]) == ["Mon 3–5pm", "Mon 6–7pm"]


def test_join_words():
    assert join_words(["A"]) == "A"
    assert join_words(["A", "B", "C"]) == "A, B, and C"


def test_match_label():
    assert match_label(0.8) == "Great match"
    assert match_label(0.55) == "Good match"
    assert match_label(0.3) == "Possible match"
