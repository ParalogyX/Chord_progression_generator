#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import textwrap
import json

# ==========================
# LOAD PROGRESSION DATABASE
# ==========================

PROGRESSIONS = json.load(open("progressions_db.json"))


AVAILABLE_MOODS = sorted({
    m for pr in PROGRESSIONS for m in pr["moods"]
})

# ==========================
# FILTER UTILITIES
# ==========================

def filter_progressions(
    mode_filter="any",
    mood_filter=None,
    bars=0,
    max_results=10
):
    """
    Filter the progression database.

    mode_filter: 'major', 'minor', or 'any'
    mood_filter: None or list of mood strings from AVAILABLE_MOODS
    bars: 0 = ignore length; >0 = require that many chords in the progression
    max_results: maximum number of progressions to return
    """

    mode_filter = mode_filter.lower().strip()
    if mood_filter is None:
        mood_filter = []

    result = []
    for pr in PROGRESSIONS:
        # Mode filter
        if mode_filter == "major" and pr["base_mode"] != "major":
            continue
        if mode_filter == "minor" and pr["base_mode"] != "minor":
            continue

        # Mood filter (require at least one overlapping mood if specified)
        if mood_filter:
            if not any(m in pr["moods"] for m in mood_filter):
                continue

        # Bars (approximate: number of chords in the roman string)
        chords = [c for c in pr["roman"].replace("–", "-").split("-") if c.strip()]
        if bars > 0 and len(chords) != bars:
            continue

        pr_copy = pr.copy()
        pr_copy["chord_count"] = len(chords)
        result.append(pr_copy)

    random.shuffle(result)
    return result[:max_results]


# ==========================
# SIMPLE CLI
# ==========================

def ask_int(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    if not s:
        return default
    try:
        return int(s)
    except ValueError:
        print("Not a number, using default value.")
        return default

def ask_str(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return s if s else default

def main():
    print("=== Chord Progression Generator (Roman Numerals) ===")
    print()
    print("Available moods:")
    print(", ".join(AVAILABLE_MOODS))
    print()

    mode = ask_str("Mode (major / minor / any)", "any").lower()
    while mode not in ("major", "minor", "any"):
        print("Allowed values: major, minor, or any")
        mode = ask_str("Mode (major / minor / any)", "any").lower()

    mood_input = ask_str(
        "Mood(s) (comma-separated, e.g. aggressive,dark or empty for any)",
        ""
    )
    if mood_input:
        mood_filter = [m.strip() for m in mood_input.split(",") if m.strip()]
    else:
        mood_filter = []

    bars = ask_int("Desired number of chords (0 = any)", 0)
    count = ask_int("How many progressions to generate", 10)

    part = ask_str(
        "Song section label (intro/verse/chorus/bridge/riff, used only as a tag)",
        "riff"
    )

    print("\n=== Result ===\n")

    res = filter_progressions(
        mode_filter=mode,
        mood_filter=mood_filter,
        bars=bars,
        max_results=count
    )

    if not res:
        print("No progressions found with these filters. Try loosening the conditions.")
        return

    for pr in res:
        header = f"#{pr['id']} | {pr['roman']} | mode={pr['base_mode']} | moods={','.join(pr['moods'])}"
        print(header)
        print(f"  → suggested section: {part}")
        wrapped = textwrap.fill(pr["description"], width=80, subsequent_indent="    ")
        print("  " + wrapped)
        print()

if __name__ == "__main__":
    main()
