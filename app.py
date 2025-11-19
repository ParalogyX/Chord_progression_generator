#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
from generator_script import filter_progressions, AVAILABLE_MOODS

app = Flask(__name__)


@app.route("/")
def index():
    modes = ["Any", "Major", "Minor"]
    moods = sorted(AVAILABLE_MOODS)
    chord_counts = ["Any"] + [str(n) for n in range(3, 9)]
    sections = [
        "Riff",
        "Intro",
        "Verse",
        "Pre-chorus",
        "Chorus",
        "Bridge",
        "Breakdown",
        "Outro",
        "Custom..."
    ]
    return render_template(
        "index.html",
        modes=modes,
        moods=moods,
        chord_counts=chord_counts,
        sections=sections,
    )


def _parse_filters(data):
    # Mode
    mode_text = (data.get("mode") or "").lower()
    if mode_text == "any":
        mode_filter = "any"
    elif mode_text == "major":
        mode_filter = "major"
    elif mode_text == "minor":
        mode_filter = "minor"
    else:
        mode_filter = "any"

    # Mood
    mood_text = data.get("mood") or "Any"
    if mood_text == "Any":
        mood_filter = []
    else:
        mood_filter = [mood_text.lower()]

    # Chord count
    bars_text = data.get("bars") or "Any"
    if bars_text == "Any":
        bars = 0
    else:
        try:
            bars = int(bars_text)
        except ValueError:
            bars = 0

    return mode_filter, mood_filter, bars


@app.route("/available_count", methods=["POST"])
def available_count():
    data = request.get_json(force=True)
    mode_filter, mood_filter, bars = _parse_filters(data)

    res = filter_progressions(
        mode_filter=mode_filter,
        mood_filter=mood_filter,
        bars=bars,
        max_results=9999,
    )
    available = len(res)
    return jsonify({"available_count": available})


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    mode_filter, mood_filter, bars = _parse_filters(data)

    try:
        count = int(data.get("count", 0))
    except ValueError:
        count = 0

    section_label = (data.get("section_label") or "").strip()
    if not section_label:
        section_label = "riff"

    res = filter_progressions(
        mode_filter=mode_filter,
        mood_filter=mood_filter,
        bars=bars,
        max_results=count,
    )

    if not res:
        return jsonify({
            "text": "No progressions found with these filters.",
            "status": "No results. Try loosening the filters."
        })

    lines = []
    for pr in res:
        header = f"#{pr['id']} | {pr['roman']} | mode={pr['base_mode']} | moods={','.join(pr['moods'])}"
        lines.append(header)
        lines.append(f"  → suggested section: {section_label}")
        lines.append(f"  {pr['description']}")
        lines.append("")

    output = "\n".join(lines)
    status = f"Generated {len(res)} progression(s)."
    return jsonify({"text": output, "status": status})


if __name__ == "__main__":
    # For dev use only; behind a real server use WSGI instead
    app.run(debug=True)
