"""Deterministic Quiet Rewrite paraphrases. Training targets are NOT verbatim originals.

Exact match 0 is by design: Creative Guessing, not an Exact Copy.
This is a rule-based paraphraser so dataset synthesis does not need a live Smart Robot
and never sees player Memories.
"""

from __future__ import annotations

import hashlib
import re

SYNONYMS: dict[str, list[str]] = {
    "first": ["earliest", "opening"],
    "time": ["moment", "hour"],
    "rode": ["took", "caught"],
    "night": ["evening", "late"],
    "bus": ["coach", "omnibus"],
    "home": ["back", "houseward"],
    "city": ["town", "downtown"],
    "windows": ["panes", "glass"],
    "fogged": ["misted", "clouded"],
    "small": ["tiny", "modest"],
    "heart": ["shape", "curve"],
    "corner": ["edge", "margin"],
    "streetlights": ["lamps", "lanterns"],
    "smear": ["blur", "streak"],
    "driver": ["operator", "driver"],
    "hummed": ["murmured", "sang"],
    "notes": ["tones", "bars"],
    "hour": ["while", "stretch"],
    "rain": ["shower", "weather"],
    "ended": ["stopped", "passed"],
    "pavement": ["sidewalk", "stones"],
    "smelled": ["scented", "smelt"],
    "dust": ["earth", "dry air"],
    "sunday": ["weekend", "sabbath"],
    "mornings": ["dawns", "early hours"],
    "kitchen": ["cookspace", "kitchen"],
    "radio": ["wireless", "set"],
    "windowsill": ["ledge", "sill"],
    "sink": ["basin", "sink"],
    "played": ["carried", "filled"],
    "station": ["channel", "broadcast"],
    "mother": ["mom", "ma"],
    "trusted": ["loved", "kept"],
    "fried": ["cooked", "sizzled"],
    "eggs": ["breakfast", "eggs"],
    "butter": ["fat", "ghee"],
    "slept": ["rested", "dozed"],
    "kettle": ["pot", "boiler"],
    "clicked": ["snapped", "ticked"],
    "room": ["kitchen", "space"],
    "filled": ["rose", "gathered"],
    "steam": ["mist", "vapor"],
    "hear": ["catch", "notice"],
    "click": ["snap", "tick"],
    "quiet": ["still", "hushed"],
    "hide": ["sit", "linger"],
    "back": ["far", "rear"],
    "aisle": ["row", "stack"],
    "public": ["town", "city"],
    "library": ["reading room", "stacks"],
    "street": ["road", "lane"],
    "turned": ["went", "shifted"],
    "silver": ["pale", "bright"],
    "carpet": ["floor", "rug"],
    "paper": ["pages", "books"],
    "wet": ["damp", "soaked"],
    "coats": ["jackets", "wool"],
    "read": ["opened", "followed"],
    "adventure": ["quest", "journey"],
    "novel": ["story", "book"],
    "closing": ["last", "evening"],
    "bell": ["chime", "ring"],
    "rang": ["sounded", "called"],
    "librarian": ["clerk", "keeper"],
    "rushed": ["hurried", "pushed"],
    "lights": ["lamps", "bulbs"],
    "began": ["started", "started"],
    "dim": ["low", "soft"],
    "sat": ["stayed", "waited"],
    "porch": ["stoop", "veranda"],
    "counted": ["tracked", "marked"],
    "seconds": ["beats", "pauses"],
    "lightning": ["flash", "bolt"],
    "thunder": ["rumble", "crash"],
    "storm": ["front", "weather"],
    "hill": ["ridge", "rise"],
    "dog": ["hound", "pup"],
    "pressed": ["leaned", "rested"],
    "knee": ["leg", "side"],
    "look": ["stare", "glance"],
    "sky": ["clouds", "dark"],
    "afterward": ["later", "then"],
    "yard": ["lawn", "grass"],
    "steamed": ["smoked", "breathed"],
    "single": ["lone", "one"],
    "chair": ["seat", "stool"],
    "blown": ["carried", "tossed"],
    "garden": ["beds", "plot"],
    "nobody": ["no one", "none"],
    "fetch": ["bring", "get"],
    "morning": ["dawn", "daylight"],
    "old": ["ancient", "aged"],
    "oak": ["oak", "oak"],
    "tree": ["tree", "tree"],
    "river": ["stream", "water"],
    "stood": ["lasted", "remained"],
    "centuries": ["ages", "years"],
    "roots": ["rootwork", "hold"],
    "drank": ["drew", "pulled"],
    "slow": ["lazy", "quiet"],
    "stream": ["brook", "current"],
    "wound": ["curved", "bent"],
    "valley": ["hollow", "glen"],
    "thread": ["line", "ribbon"],
    "birds": ["wrens", "finches"],
    "nested": ["rested", "settled"],
    "high": ["upper", "tall"],
    "branches": ["limbs", "boughs"],
    "children": ["kids", "young ones"],
    "shade": ["shadow", "cool"],
    "summer": ["july", "heat"],
    "autumn": ["fall", "harvest"],
    "leaves": ["foliage", "canopy"],
    "color": ["hue", "tint"],
    "fire": ["ember", "flame"],
    "fell": ["dropped", "drifted down"],
    "walked": ["strolled", "went"],
    "beach": ["shore", "strand"],
    "waves": ["surf", "breakers"],
    "cold": ["chill", "cool"],
    "hands": ["fingers", "palms"],
    "pocket": ["coat", "jacket"],
    "letter": ["note", "page"],
    "wrote": ["penned", "set down"],
    "remember": ["recall", "keep"],
    "train": ["rail", "carriage"],
    "station": ["platform", "depot"],
    "coffee": ["tea", "mug"],
    "warm": ["hot", "mild"],
    "snow": ["flakes", "white"],
    "window": ["pane", "glass"],
    "blue": ["pale", "clear"],
    "green": ["leafy", "deep"],
    "red": ["bright", "warm"],
}


def _token_key(word: str) -> str:
    return re.sub(r"[^a-z']", "", word.lower())


def _rng_pick(seed_s: str, choices: list[str]) -> str:
    digest = hashlib.sha256(seed_s.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "big") % len(choices)
    return choices[idx]


def quiet_rewrite(original: str, salt: str = "") -> str:
    """Return a paraphrase that shares meaning but is not an Exact Copy."""
    words = re.split(r"(\s+)", original)
    out: list[str] = []
    changed = 0
    i = 0
    for part in words:
        if not part.strip() or not re.search(r"[A-Za-z]", part):
            out.append(part)
            continue
        key = _token_key(part)
        options = SYNONYMS.get(key)
        take = False
        if options:
            take = _rng_pick(f"{salt}:{i}:{key}:take", ["0", "1", "1", "1"]) != "0"
        if options and take:
            repl = _rng_pick(f"{salt}:{i}:{key}:repl", options)
            if part[0].isupper():
                repl = repl[:1].upper() + repl[1:]
            if part.endswith((".", ",", ";", ":")):
                punct = part[-1]
                core = part[:-1]
                if core and core[0].isupper():
                    repl = repl[:1].upper() + repl[1:]
                out.append(repl + punct)
            else:
                out.append(repl)
            if repl.lower() != key:
                changed += 1
        else:
            out.append(part)
        i += 1
    text = "".join(out).strip()
    if text == original.strip() or changed == 0:
        # Guarantee a visible Quiet Rewrite: swap a closing cadence.
        if text.endswith("."):
            text = text[:-1] + ", and I still think of it."
        else:
            text = text + " I still think of it."
    return text
