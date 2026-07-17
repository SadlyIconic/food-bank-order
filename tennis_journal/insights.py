"""Rule-based analysis of journal notes for recurring themes."""

from __future__ import annotations

THEMES: list[dict] = [
    {
        "id": "second_serve",
        "label": "Second serve under pressure",
        "kind": "issue",
        "keywords": [
            "second serve",
            "double fault",
            " df",
            "dfs",
            "kick serve",
            "second-serve",
        ],
        "tip": "Prioritize spin and placement over pace; drill kick wide to the ad court.",
    },
    {
        "id": "return_position",
        "label": "Passive return position",
        "kind": "issue",
        "keywords": [
            "return position",
            "behind baseline",
            "behind the baseline",
            "camping deep",
            "stood deep",
            "standing deep",
            "passive return",
            "too far back",
            "retreating",
            "retreat",
        ],
        "tip": "Stand inside the baseline on second serves; take the ball early.",
    },
    {
        "id": "forehand",
        "label": "Forehand breakdown",
        "kind": "issue",
        "keywords": [
            "forehand",
            "overhit",
            "over-hit",
            "rushed",
            "sailing",
            "contact point",
            "netting",
            "pushed",
        ],
        "tip": "Stay on the front foot; crosscourt until you get a short ball.",
    },
    {
        "id": "topspin",
        "label": "Struggle vs heavy topspin",
        "kind": "issue",
        "keywords": [
            "topspin",
            "heavy spin",
            "on the rise",
            "back foot",
            "jumped above",
        ],
        "tip": "Practice taking the ball on the rise; aim deep middle, not lines.",
    },
    {
        "id": "third_set",
        "label": "Third-set fade",
        "kind": "issue",
        "keywords": [
            "third set",
            "third-set",
            "decider",
            "legs were gone",
            "fitness",
            "when tired",
            "collapse",
            "fade",
        ],
        "tip": "Plan third-set energy (fuel at changeovers); stick to patterns when fatigued.",
    },
    {
        "id": "over_aggression",
        "label": "Over-aggression when ahead",
        "kind": "issue",
        "keywords": [
            "when ahead",
            "over-aggression",
            "hero",
            "going for winners",
            "winners instead",
            "momentum",
            "low-percentage",
            "swing harder",
            "blew it",
        ],
        "tip": "When up, play margin — crosscourt and wait; don't hunt winners.",
    },
    {
        "id": "net_approach",
        "label": "Poor approach / net timing",
        "kind": "issue",
        "keywords": [
            "approach",
            "came in",
            "volley",
            "at net",
            "poach",
            "lob",
        ],
        "tip": "Only approach on balls landing inside the service line when balanced.",
    },
    {
        "id": "big_points",
        "label": "Big-point decision making",
        "kind": "issue",
        "keywords": [
            "break point",
            "30-30",
            "deuce",
            "tiebreak",
            "scoreboard pressure",
            "big point",
            "clutch",
        ],
        "tip": "Default to high-percentage patterns on break points; grind crosscourt.",
    },
    {
        "id": "crosscourt_patterns",
        "label": "Patient crosscourt patterns",
        "kind": "strength",
        "keywords": [
            "crosscourt",
            "patience",
            "patterns",
            "blueprint",
            "waited for short",
            "rebuilding points",
        ],
        "tip": "Keep using this as your default game plan when the score gets tight.",
    },
    {
        "id": "serve_weapon",
        "label": "Serve working well",
        "kind": "strength",
        "keywords": [
            "kick",
            "slice serve",
            "placement",
            "serve clicked",
            "serving well",
            "body serve",
            "only 1 df",
            "only one double fault",
        ],
        "tip": "When the serve is clicking, build the rest of the game around it.",
    },
    {
        "id": "aggressive_return",
        "label": "Aggressive returns",
        "kind": "strength",
        "keywords": [
            "return position",
            "inside baseline",
            "returns were",
            "broke twice",
            "first-strike",
        ],
        "tip": "Make the inside-baseline return position your default.",
    },
]


def _entry_text(entry: dict) -> str:
    parts = [
        entry.get("notes", ""),
        entry.get("score", ""),
        entry.get("result", ""),
    ]
    return " ".join(parts).lower()


def _matches_theme(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def analyze(entries: list[dict]) -> dict:
    with_notes = [e for e in entries if e.get("notes", "").strip()]
    wins = sum(1 for e in entries if e.get("result") == "win")
    losses = sum(1 for e in entries if e.get("result") == "loss")

    theme_results: list[dict] = []
    for theme in THEMES:
        matched: list[dict] = []
        for entry in with_notes:
            if _matches_theme(_entry_text(entry), theme["keywords"]):
                matched.append(entry)

        if not matched:
            continue

        win_count = sum(1 for e in matched if e.get("result") == "win")
        loss_count = sum(1 for e in matched if e.get("result") == "loss")

        theme_results.append(
            {
                "id": theme["id"],
                "label": theme["label"],
                "kind": theme["kind"],
                "tip": theme.get("tip", ""),
                "count": len(matched),
                "wins": win_count,
                "losses": loss_count,
                "matches": [
                    {
                        "id": e["id"],
                        "opponent": e["opponent"],
                        "date": e["date"],
                        "result": e.get("result", ""),
                    }
                    for e in sorted(matched, key=lambda x: x.get("date", ""), reverse=True)
                ],
            }
        )

    issues = sorted(
        [t for t in theme_results if t["kind"] == "issue"],
        key=lambda t: (t["losses"], t["count"]),
        reverse=True,
    )
    strengths = sorted(
        [t for t in theme_results if t["kind"] == "strength"],
        key=lambda t: t["count"],
        reverse=True,
    )

    min_entries = 3
    has_enough = len(with_notes) >= min_entries

    return {
        "total_entries": len(entries),
        "entries_with_notes": len(with_notes),
        "min_entries": min_entries,
        "has_enough": has_enough,
        "record": {"wins": wins, "losses": losses},
        "issues": issues,
        "strengths": strengths,
        "focus_areas": issues[:3] if has_enough else [],
    }
