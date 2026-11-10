#!/usr/bin/env python3
"""Export TungstenSkylark palettes as macOS Terminal.app .terminal profiles.

Reads themes/tokens.json (W3C DTCG) and writes one .terminal file per theme
per polarity into exports/terminal/: 20 files (10 themes x dark/light).
Maps brand roles (bg, surface, text, accent, accentSoft, ink + derived
ok/error/warn) onto the ANSI 16 + background/text/bold/selection/cursor
slots, applying the same AA-blend derivation rules as the skin and CSS
builders (ratified brand standard, Nov 2026).

Import on any Mac: double-click the .terminal file, or
Terminal > Settings > Profiles > gear menu > Import...
Then Profiles > select it > "Use as Default" to make it permanent.

Note: Terminal.app has no automatic light/dark palette swap; the -light
files import as their own separate profiles.
"""

import json
import os
import plistlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "exports", "terminal")

DISPLAY = {
    "skylark": "Tungsten Skylark", "ember": "Tungsten Ember",
    "dawn": "Skylark Dawn", "frost": "Skylark Frost",
    "harbour": "Tungsten Harbour", "meadow": "Skylark Meadow",
    "dusk": "Skylark Dusk", "rose": "Tungsten Rose",
    "ink": "Tungsten Ink", "phosphor": "Tungsten Phosphor",
    "brassworks": "Tungsten Brassworks",
}
# file-name slugs MUST carry the correct metal/bird prefix from the display
# name (site-verified): skylark-dawn.terminal, NOT tungsten-dawn.terminal.
SLUG = {tid: display.lower().replace(" ", "-") for tid, display in DISPLAY.items()}
# ratified semantic anchors: ok/error/warn <- meadow/rose/ember accents
ANCHORS = {"ok": ("meadow", "accent"), "error": ("rose", "accent"),
           "warn": ("ember", "accent")}


def _term_float(v: float) -> str:
    """Format like Terminal's own exports: 10 decimals, trailing zeros trimmed."""
    s = f"{v:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"


def ns_color(rgb_hex: str) -> bytes:
    """NSKeyedArchiver NSColor in Terminal's classic layout (matches the
    Dracula reference exactly): NSColorSpace=int 1, NSRGB=NUL-terminated
    bytes "r g b\\x00". The modern string layout makes Terminal reject the
    file as corrupt."""
    h = rgb_hex.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return plistlib.dumps({
        "$version": 100000,
        "$archiver": "NSKeyedArchiver",
        "$top": {"root": plistlib.UID(1)},
        "$objects": [
            "$null",
            {
                "NSColorSpace": 1,
                "NSRGB": f"{_term_float(r)} {_term_float(g)} {_term_float(b)}".encode() + b"\x00",
                "$class": plistlib.UID(2),
            },
            {"$classname": "NSColor", "$classes": ["NSColor", "NSObject"]},
        ],
    }, fmt=plistlib.FMT_BINARY, sort_keys=False)


def rel_lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(fg: str, bg: str) -> float:
    l1, l2 = rel_lum(fg), rel_lum(bg)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def mix(a_hex: str, b_hex: str, p: float) -> str:
    def parse(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    (r1, g1, b1), (r2, g2, b2) = parse(a_hex), parse(b_hex)
    return "#{:02X}{:02X}{:02X}".format(
        round(r1 + (r2 - r1) * p), round(g1 + (g2 - g1) * p), round(b1 + (b2 - b1) * p))


def aa_blend(color: str, bg: str, floor: float = 4.5) -> str:
    """Blend toward white/black until >=floor on bg (brand derivation method)."""
    if ratio(color, bg) >= floor:
        return color
    toward_white = rel_lum(bg) < 0.5
    cur = color
    for step in range(1, 41):
        cur = mix(color, "#FFFFFF" if toward_white else "#000000", step * 0.025)
        if ratio(cur, bg) >= floor:
            return cur
    return cur


def build_profile(pal: dict, name: str) -> dict:
    """pal: role->hex for one polarity; returns a Terminal profile dict."""
    bg, txt = pal["bg"], pal["text"]
    ac, acs, ink = pal["accent"], pal["accentSoft"], pal["ink"]
    dark = rel_lum(bg) < 0.5
    lift = "#FFFFFF" if dark else "#000000"

    # brand-derived ANSI mapping: semantics fill their colour families;
    # blue/magenta/cyan derived from ink/accent mixes so no hue is invented
    blue = aa_blend(mix(ink, ac, 0.5), bg)
    magenta = aa_blend(mix(ac, ink, 0.5), bg)
    cyan = aa_blend(acs, bg)
    dim = mix(bg, txt, 0.45)  # bright-black = the "dim grey" role

    ansi = {
        "Black": bg,          # slot 0 doubles as the backdrop hue
        "Red": pal["error"],
        "Green": pal["ok"],
        "Yellow": pal["warn"],
        "Blue": blue,
        "Magenta": magenta,
        "Cyan": cyan,
        "White": txt,
        "BrightBlack": dim,
        "BrightRed": mix(pal["error"], lift, 0.15),
        "BrightGreen": mix(pal["ok"], lift, 0.15),
        "BrightYellow": mix(pal["warn"], lift, 0.15),
        "BrightBlue": mix(blue, lift, 0.2),
        "BrightMagenta": mix(magenta, lift, 0.2),
        "BrightCyan": mix(cyan, lift, 0.2),
        "BrightWhite": mix(txt, lift, 0.3),
    }

    prof = {"type": "Window Settings", "name": name, "ProfileCurrentVersion": 2.05}
    for slot, hexv in ansi.items():
        prof[f"ANSI{slot}Color"] = ns_color(hexv)
    prof["BackgroundColor"] = ns_color(bg)
    prof["TextColor"] = ns_color(txt)
    prof["TextBoldColor"] = ns_color(pal.get("accentText", ac))
    prof["CursorColor"] = ns_color(ac)
    prof["CursorTextColor"] = ns_color(bg)
    prof["SelectionColor"] = ns_color(mix(bg, acs, 0.4))
    prof["TextSmokeColor"] = ns_color(bg)
    return prof


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    tokens = json.load(open(os.path.join(ROOT, "themes", "tokens.json")))
    themes = tokens["ts"]["color"]["theme"]

    written, fails, report = 0, [], []
    for tid, th in themes.items():
        for mode in ("light", "dark"):
            m = th[mode]
            pal = {r: m[r]["$value"] for r in
                   ("bg", "surface", "text", "accent", "accentSoft", "ink")}
            if "accentText" in m:
                pal["accentText"] = m["accentText"]["$value"]
            else:
                # same rule as build-tokens-css.py: unsanctioned accents are
                # AA-blended for text-bearing use
                pal["accentText"] = aa_blend(pal["accent"], pal["bg"])
            for role, (anchor_tid, slot) in ANCHORS.items():
                pal[role] = aa_blend(themes[anchor_tid][mode][slot]["$value"],
                                     pal["bg"])
            # AA audit: text, semantics, and all ANSI text-bearing slots
            checks = {"text": ratio(pal["text"], pal["bg"]),
                      "ok": ratio(pal["ok"], pal["bg"]),
                      "error": ratio(pal["error"], pal["bg"]),
                      "warn": ratio(pal["warn"], pal["bg"]),
                      "blue": ratio(aa_blend(mix(pal["ink"], pal["accent"], 0.5), pal["bg"]), pal["bg"]),
                      "magenta": ratio(aa_blend(mix(pal["accent"], pal["ink"], 0.5), pal["bg"]), pal["bg"]),
                      "cyan": ratio(aa_blend(pal["accentSoft"], pal["bg"]), pal["bg"]),
                      "bold/accentText": ratio(pal.get("accentText", pal["accent"]), pal["bg"])}
            bad = {k: v for k, v in checks.items() if v < 4.5}
            suffix = "" if mode == "dark" else "-light"
            name = f"{DISPLAY[tid]}{' (Light)' if mode == 'light' else ''}"
            fname = f"{SLUG[tid]}{suffix}.terminal"
            if bad:
                fails.append(f"{fname}: FAIL {bad}")
                continue
            with open(os.path.join(OUT, fname), "wb") as f:
                plistlib.dump(build_profile(pal, name), f)
            written += 1
            report.append(f"  {fname:<34} text/bg {checks['text']:.2f}:1  "
                          f"sem ok/error/warn {checks['ok']:.2f}/{checks['error']:.2f}/{checks['warn']:.2f}")

    print("\n".join(report))
    if fails:
        print("FAILED:\n" + "\n".join(fails))
        return 1
    print(f"wrote {written} .terminal profiles -> {os.path.relpath(OUT, ROOT)}/ "
          f"(all slots AA >= 4.5:1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
