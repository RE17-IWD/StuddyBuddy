import networkx as nx

from app.matching import (
    _greedy_edges,
    match,
    pair_score,
    unmatched,
)

TUE_4PM = (1, 16)
TUE_5PM = (1, 17)


def student(id, ratings, slots=(TUE_4PM,), noise="quiet", time="afternoon", blocked=()):
    return {
        "id": id, "name": id, "ratings": ratings, "slots": set(slots),
        "noise": noise, "time": time, "blocked": set(blocked), "declined": set(),
    }


def test_no_edge_without_schedule_overlap():
    a = student("a", {"Limits": 3, "Integrals": 1}, slots=[TUE_4PM])
    b = student("b", {"Limits": 1, "Integrals": 3}, slots=[TUE_5PM])
    assert pair_score(a, b) is None


def test_blocked_pair_excluded_either_direction():
    a = student("a", {"Limits": 3, "Integrals": 1}, blocked=["b"])
    b = student("b", {"Limits": 1, "Integrals": 3})
    assert pair_score(a, b) is None
    assert pair_score(b, a) is None


def test_two_way_swap_beats_one_way():
    me = student("me", {"Limits": 3, "Integrals": 1})
    two_way = student("two", {"Limits": 1, "Integrals": 3})
    one_way = student("one", {"Limits": 1, "Integrals": 1})
    assert pair_score(me, two_way)[0] > pair_score(me, one_way)[0]


def test_breakdown_lists_who_teaches_what():
    a = student("a", {"Limits": 3, "Integrals": 1, "Series": 3})
    b = student("b", {"Limits": 1, "Integrals": 3, "Series": 2})
    _, bd = pair_score(a, b)
    assert bd["a_teaches"] == ["Limits", "Series"]  # Series is Strong vs OK
    assert bd["b_teaches"] == ["Integrals"]


def test_greedy_strands_students_but_max_weight_does_not():
    # The example from PLAN.md section 8.
    g = nx.Graph()
    g.add_edge("A", "B", weight=10)
    g.add_edge("A", "C", weight=9)
    g.add_edge("B", "D", weight=9)  # C-D: no edge

    greedy = _greedy_edges(g)
    best = nx.max_weight_matching(g, maxcardinality=False)

    def total(edges):
        return sum(g.edges[u, v]["weight"] for u, v in edges)

    assert total(greedy) == 10 and len(greedy) == 1  # C and D stranded
    assert total(best) == 18 and len(best) == 2      # everyone matched


def test_odd_count_leaves_exactly_one_unmatched():
    a = student("a", {"Limits": 3, "Integrals": 1})
    b = student("b", {"Limits": 1, "Integrals": 3})
    c = student("c", {"Limits": 1, "Integrals": 3})
    pairs = match([a, b, c])
    assert len(pairs) == 1
    assert len(unmatched([a, b, c], pairs)) == 1
