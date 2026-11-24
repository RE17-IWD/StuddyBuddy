"""StudySwap matching engine.

Pure functions only: no database, no network. Every function takes plain
Python data and returns plain Python data, so it is easy to test and explain.

A student is a dict like:
    {
        "id": "u1",
        "name": "Alex",
        "ratings": {"Limits": 3, "Integrals": 1},   # 1 weak, 2 ok, 3 strong
        "slots": {(1, 16), (1, 17)},                # (day 0-6, hour 8-21)
        "noise": "quiet",                           # 'quiet' | 'talk'
        "time": "afternoon",                        # 'morning' | 'afternoon' | 'evening'
        "blocked": set(),                           # ids this student blocked
        "declined": set(),                          # ids this student declined before
    }
"""

from __future__ import annotations

import networkx as nx

WEAK, OK, STRONG = 1, 2, 3

W_SWAP, W_SCHEDULE, W_STYLE = 0.6, 0.25, 0.15

# Why: a pair where nobody can teach anybody defeats the purpose of the app,
# even if their schedules line up perfectly. The plan (section 8) did not say
# this explicitly; see DECISIONS.md.
REQUIRE_TEACHING = True


def teaching_points(teacher: dict, learner: dict) -> tuple[float, list[str], list[str]]:
    """How much `teacher` can teach `learner`.

    Strong vs Weak = 1 point (listed in `full`).
    Strong vs OK   = 0.5 points (listed in `half`).
    """
    full, half = [], []
    for unit, t_rating in teacher["ratings"].items():
        l_rating = learner["ratings"].get(unit)
        if t_rating != STRONG or l_rating is None:
            continue
        if l_rating == WEAK:
            full.append(unit)
        elif l_rating == OK:
            half.append(unit)
    return len(full) + 0.5 * len(half), full, half


def _blocked_or_declined(a: dict, b: dict) -> bool:
    return (
        b["id"] in a.get("blocked", set())
        or a["id"] in b.get("blocked", set())
        or b["id"] in a.get("declined", set())
        or a["id"] in b.get("declined", set())
    )


def pair_score(a: dict, b: dict) -> tuple[float, dict] | None:
    """Score one pair. Returns None when the pair must not be matched."""
    if _blocked_or_declined(a, b):
        return None

    shared = sorted(set(a["slots"]) & set(b["slots"]))
    if len(shared) < 1:
        return None

    a_pts, a_full, a_half = teaching_points(a, b)
    b_pts, b_full, b_half = teaching_points(b, a)
    if REQUIRE_TEACHING and a_pts == 0 and b_pts == 0:
        return None

    # Two-way swaps count double: each person both teaches and learns.
    swap_raw = min(a_pts, b_pts) * 2 + max(a_pts, b_pts)
    swap = min(swap_raw / 6, 1.0)

    schedule = min(len(shared), 6) / 6

    style = 0.0
    if a["noise"] == b["noise"]:
        style += 0.5
    if a["time"] == b["time"]:
        style += 0.5

    score = W_SWAP * swap + W_SCHEDULE * schedule + W_STYLE * style
    breakdown = {
        "swap": round(swap, 3),
        "schedule": round(schedule, 3),
        "style": style,
        "overlap_hours": len(shared),
        "a_teaches": a_full + a_half,
        "b_teaches": b_full + b_half,
        "shared_slots": shared,
        "same_noise": a["noise"] == b["noise"],
        "same_time": a["time"] == b["time"],
    }
    return round(score, 4), breakdown


def build_graph(students: list[dict]) -> nx.Graph:
    """One node per student, one weighted edge per allowed pair."""
    g = nx.Graph()
    for s in students:
        g.add_node(s["id"])
    for i, a in enumerate(students):
        for b in students[i + 1:]:
            result = pair_score(a, b)
            if result is not None:
                score, breakdown = result
                g.add_edge(a["id"], b["id"], weight=score, breakdown=breakdown)
    return g


def _pairs_from_graph(g: nx.Graph, chosen: set) -> list[dict]:
    pairs = []
    for u, v in chosen:
        data = g.edges[u, v]
        pairs.append({"a": u, "b": v, "score": data["weight"], "breakdown": data.get("breakdown")})
    return sorted(pairs, key=lambda p: -p["score"])


def match(students: list[dict]) -> list[dict]:
    """Best total pairing for the whole class (maximum weight matching)."""
    g = build_graph(students)
    chosen = nx.max_weight_matching(g, maxcardinality=False)
    return _pairs_from_graph(g, chosen)


def greedy_match(students: list[dict]) -> list[dict]:
    """Comparison only: repeatedly take the single best remaining pair."""
    g = build_graph(students)
    return _pairs_from_graph(g, _greedy_edges(g))


def _greedy_edges(g: nx.Graph) -> set:
    used, chosen = set(), set()
    for u, v, w in sorted(g.edges(data="weight"), key=lambda e: -e[2]):
        if u not in used and v not in used:
            chosen.add((u, v))
            used.update((u, v))
    return chosen


def unmatched(students: list[dict], pairs: list[dict]) -> list[str]:
    taken = {p["a"] for p in pairs} | {p["b"] for p in pairs}
    return [s["id"] for s in students if s["id"] not in taken]
