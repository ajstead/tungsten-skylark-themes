#!/usr/bin/env python3
"""Build skins for the TungstenSkylark theme pack.

Reads each theme under themes/<slug>/ :
  - colors.toml          palette source (required unless skin.yaml exists)
  - skin.yaml            hand-made skin — wins over generated output
  - meta.json            {"skin": "<name>", "label": "...", "classification": "light|dark"}
and writes the distributable skin to skins/<slug>.yaml.

Also runs a WCAG contrast audit on every palette pair declared in the
theme's colors.toml [contrast] section (fg/bg keys, kind=text|accent) and
fails the build if any text pair drops below 4.5:1 or accent pair below 3:1.

Usage: python3 tools/build.py [--audit-only] [slug ...]
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

assert yaml is not None, (
    "PyYAML required for generated skins: pip3 install pyyaml"
)

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "themes"
SKINS = ROOT / "skins"

# Reserved Desktop built-in skin names — a backend skin with such a name
# never paints in Desktop. Hard fail if a theme tries to use one.
RESERVED = {
    "default", "classic", "mono", "slate", "daylight", "warm-lightmode",
    "poseidon", "sisyphus", "ares",
}

TEXT_MIN = 4.5   # WCAG AA, normal text
ACCENT_MIN = 3.0  # labels / accents


def _rel_lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = _rel_lum(fg), _rel_lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def load_theme(slug: str) -> dict:
    tdir = THEMES / slug
    meta_path = tdir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    skin_name = meta.get("skin", f"tungsten-skylark-{slug}")

    handmade = tdir / "skin.yaml"
    if handmade.exists():
        return {
            "slug": slug,
            "skin_name": skin_name,
            "classification": meta.get("classification", "unknown"),
            "handmade": True,
            "skin": handmade.read_text(),
        }

    colors_path = tdir / "colors.toml"
    if not colors_path.exists():
        raise SystemExit(f"[{slug}] need either skin.yaml or colors.toml")

    data = tomllib.loads(colors_path.read_text())
    doc = {"name": skin_name}
    if meta.get("label"):
        doc["description"] = meta["label"]
    if "colors" in data:
        doc["colors"] = data["colors"]
    for section in ("spinner", "branding"):
        if section in data:
            doc[section] = data[section]
    for key in ("tool_prefix", "tool_emojis", "banner_logo", "banner_hero",
                "customCSS"):
        if key in data:
            doc[key] = data[key]

    light = data.get("light") or {}
    if isinstance(light, dict) and "colors" in light:
        # [light] table: full second palette + its own audit set.
        doc["light_colors"] = light["colors"]

    return {
        "slug": slug,
        "skin_name": skin_name,
        "classification": meta.get("classification", "unknown"),
        "handmade": False,
        "skin": doc,
        "contrast_pairs": data.get("contrast", {}),
        "bg": data.get("backgrounds", {}),
        "light_pairs": (light.get("contrast") or {}) if isinstance(light, dict) else {},
        "light_bg": (light.get("backgrounds") or {}) if isinstance(light, dict) else {},
    }


def audit(theme: dict) -> list[str]:
    """Return a list of human-readable contrast failures (empty = pass).

    Audits the base [contrast] pairs against [backgrounds], and — when the
    theme carries a [light] polarity — the [light.contrast] pairs against
    [light.backgrounds]. Both must clear AA before the build writes a skin.
    """
    failures = []
    sections = [("", theme.get("contrast_pairs", {}), theme.get("bg", {}))]
    if theme.get("light_pairs"):
        sections.append(("light ", theme["light_pairs"], theme["light_bg"]))
    for prefix, pairs, bgs in sections:
        for key, val in pairs.items():
            fg_key, bg_key, kind = val if isinstance(val, list) else (val[0], val[1], "text")
            palette = theme["skin"]["colors"] if isinstance(theme["skin"], dict) else None
            if palette is None:
                continue  # hand-made skin: audit lives in its own README
            if prefix and "light_colors" in theme["skin"]:
                palette = {**palette, **theme["skin"]["light_colors"]}
            fg, bg = palette.get(fg_key), bgs.get(bg_key) or palette.get(bg_key)
            if fg is None or bg is None:
                failures.append(f"  {prefix}{key}: missing {fg_key}/{bg_key}")
                continue
            ratio = contrast_ratio(fg, bg)
            threshold = ACCENT_MIN if kind == "accent" else TEXT_MIN
            mark = "PASS" if ratio >= threshold else "FAIL"
            print(f"  {mark}  {prefix}{key:<26} {fg} on {bg}  {ratio:.2f}:1 "
                  f"(need {threshold}:1)")
            if ratio < threshold:
                failures.append(f"  {prefix}{key}: {ratio:.2f}:1 < {threshold}:1")
    return failures


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    audit_only = "--audit-only" in sys.argv
    slugs = argv or sorted(
        d.name for d in THEMES.iterdir() if d.is_dir() and not d.name.endswith(".json")
    ) if THEMES.exists() else []

    if not slugs:
        print("no themes found under themes/")
        return 1

    all_failures, built = {}, []
    for slug in slugs:
        print(f"\n== {slug} ==")
        theme = load_theme(slug)
        if theme["skin_name"] in RESERVED:
            print(f"  ERROR: skin name '{theme['skin_name']}' is a reserved "
                  f"Desktop built-in; rename with a suffix.")
            all_failures[slug] = ["reserved name collision"]
            continue
        print(f"  classification: {theme['classification']}")
        if not theme["handmade"]:
            fails = audit(theme)
            if fails:
                all_failures[slug] = fails
                continue
        else:
            print("  hand-made skin.yaml — copied verbatim (audit manually)")
        if not audit_only:
            SKINS.mkdir(exist_ok=True)
            out = SKINS / f"{slug}.yaml"
            existing = out.read_text() if out.exists() else None
            content = theme["skin"] if theme["handmade"] else yaml.safe_dump(
                theme["skin"], sort_keys=False, allow_unicode=True,
                default_flow_style=False)
            if existing == content:
                print(f"  {out.name} unchanged")
            else:
                backup = out.with_suffix(".yaml.bak")
                if existing:
                    backup.write_text(existing)  # never clobber user edits
                out.write_text(content)
                print(f"  wrote {out.name}" + (" (backup .bak saved)" if existing else ""))
        built.append(slug)

    print(f"\nbuilt: {', '.join(built) if built else 'none'}")
    if all_failures:
        print("\nCONTRAST/NAME FAILURES:")
        for slug, fails in all_failures.items():
            print(f"[{slug}]")
            print("\n".join(fails))
        return 1
    print("all contrast checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
