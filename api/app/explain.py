"""Plain-language match explanations.

Built from the match `breakdown` with a fixed template, never an LLM,
so the text always matches the real numbers behind the score.
"""

from __future__ import annotations

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

TIME_PHRASES = {
    "morning": "in the morning",
    "afternoon": "in the afternoon",
    "evening": "in the evening",
}


def join_words(items: list[str]) -> str:
    """['a'] -> 'a', ['a','b'] -> 'a and b', ['a','b','c'] -> 'a, b, and c'."""
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _clock(hour: int) -> str:
    return f"{(hour + 11) % 12 + 1}{'am' if hour < 12 else 'pm'}"


def format_range(start: int, end: int) -> str:
    """Hours to text. 16, 18 -> '4–6pm'; 11, 13 -> '11am–1pm'."""
    same_half = (start < 12) == (end < 12)
    first = str((start + 11) % 12 + 1) if same_half else _clock(start)
    return f"{first}–{_clock(end)}"


def slot_ranges(slots) -> list[str]:
    """Group (day, hour) slots into readable blocks like 'Tue 4–6pm'.

    Each slot is a one-hour block starting at `hour`, so hours 16 and 17
    together mean 4pm to 6pm. Slots may be tuples or lists (from JSON).
    """
    by_day: dict[int, list[int]] = {}
    for day, hour in slots:
        by_day.setdefault(int(day), []).append(int(hour))

    blocks = []
    for day in sorted(by_day):
        hours = sorted(set(by_day[day]))
        start = prev = hours[0]
        for hour in hours[1:] + [None]:
            if hour is not None and hour == prev + 1:
                prev = hour
                continue
            blocks.append(f"{DAY_NAMES[day]} {format_range(start, prev + 1)}")
            if hour is not None:
                start = prev = hour
    return blocks


def explain(breakdown: dict, partner_name: str, viewer: str = "a") -> str:
    """Explain a match to one of its two students.

    `viewer` is "a" or "b": which side of the match is reading the card.
    """
    if viewer == "a":
        mine, theirs = breakdown["a_teaches"], breakdown["b_teaches"]
    else:
        mine, theirs = breakdown["b_teaches"], breakdown["a_teaches"]

    sentences = []
    if mine and theirs:
        sentences.append(f"You're strong in {join_words(mine)}, and {partner_name} is strong in {join_words(theirs)}.")
    elif mine:
        sentences.append(f"You're strong in {join_words(mine)}, where {partner_name} wants help.")
    elif theirs:
        sentences.append(f"{partner_name} is strong in {join_words(theirs)}, where you want help.")

    times = slot_ranges(breakdown["shared_slots"])
    if times:
        sentences.append(f"You're both free {join_words(times)}.")

    noise, time = breakdown.get("shared_noise"), breakdown.get("shared_time")
    noise_word = {"quiet": "quiet", "talk": "talkative"}.get(noise)
    if noise_word and time:
        sentences.append(f"You both prefer {noise_word} study {TIME_PHRASES[time]}.")
    elif noise_word:
        sentences.append(f"You both like {noise_word} study.")
    elif time:
        sentences.append(f"You both like studying {TIME_PHRASES[time]}.")

    return " ".join(sentences)


def match_label(score: float) -> str:
    """Simple label for the match card instead of a raw number."""
    if score >= 0.7:
        return "Great match"
    if score >= 0.5:
        return "Good match"
    return "Possible match"
