# Decisions

Short log of important design choices and why. Newest at the bottom.

## Phase 0: Setup

- **One time zone per school.** Availability is stored as local day/hour. Every student at one school is assumed to share a time zone, which keeps the schedule overlap check simple.
- **Backend writes, students read.** Matches and sessions are written only by the FastAPI backend (service-role key). RLS lets a student read only the matches and sessions they are part of.
- **Reports are write-only for students.** A student can file a report but can't read any reports, including their own. Admins review them with the service role.

## Phase 1 head start: Matching

- **Pairs where nobody teaches anybody get no edge.** The plan only skipped pairs with no shared time or a block. Without this rule, two students with zero swap value but matching schedules would still score about 0.4 and could be paired. (`REQUIRE_TEACHING` in `matching.py`.)
- **Teaching is counted in points, not units.** Strong vs Weak = 1 point and Strong vs OK = 0.5 points. The swap formula `min(a, b) * 2 + max(a, b)` uses these points, which is how "half a point each way" fits the formula.
- **Max-weight matching, not greedy.** Greedy can strand people. Example: A–B = 10, A–C = 9, B–D = 9, and C–D has no shared time. Greedy takes A–B and leaves C and D unmatched (total 10). Max-weight takes A–C + B–D (total 18, everyone matched). This case is tested in `tests/test_matching.py`.
