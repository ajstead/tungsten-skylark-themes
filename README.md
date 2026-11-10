# TungstenSkylark Themes

Official TungstenSkylark brand themes for Hermes surfaces (CLI, TUI, Desktop)
plus a portable token sheet other apps can consume directly.

Source of truth for colours: the brand `ts-brand.css` / TS-Themes.md framework
(nine themes × light/dark, six colour roles, ~10% accent discipline, Chakra
Petch + Space Mono), expressed in the **W3C Design Tokens (DTCG) format**.
Reference-only; nothing in this repo writes into the brand material.

## Skins

| Skin | Classification | Description |
|---|---|---|
| `tungsten-skylark` | dual (dark+light) | Skylark brand base — amber `#FFB24D` on tungsten `#232529`, text `#F5F2EC`; ships a `light_colors` overlay (cream `#F5F2EC`, amber `#9A5300`) |
| `tungsten-skylark-light` | light | Standalone Skylark light palette — kept for back-compat; identical to the `tungsten-skylark` overlay |
| `tungsten-phosphor` | dual (dark+light) | Retro green-phosphor CRT: phosphor green `#00FF41` on near-black `#060D08`; light polarity is "paper printout": deep green `#0E6B2E` on paper `#F0F5EC` |
| `tungsten-brassworks` | dual (dark+light) | Steampunk eleventh theme: gaslight copper `#E08A3C` on oiled iron `#1A130D`; light polarity is "parchment & copper": oxidised copper `#A0521C` on aged parchment `#F0E7D0` |

Apply (repaints every surface within ~a second):

```bash
hermes config set display.skin tungsten-skylark        # or tungsten-skylark-light
```

## Install

```bash
hermes plugins install <gh-owner>/tungsten-skylark-themes
hermes plugins enable tungsten-skylark-themes
```

Local iteration: `hermes plugins install "file://$(pwd)" --no-deps`, or copy
`skins/*.yaml` to `$HERMES_HOME/skins/` for immediate `/skin <name>` preview.

## Build & verify

```bash
python3 tools/build.py              # colors.toml -> skins/*.yaml + WCAG audit
python3 tools/build-tokens-css.py   # tokens.json -> exports/ts-tokens.css
hermes plugins validate .
```

`tools/build.py` fails the build if any declared text/background pair drops
below 4.5:1 (WCAG AA) or accent pair below 3:1, and refuses reserved Desktop
skin names.

## Using the theme in OTHER apps

- **`themes/tokens.json`** — machine-readable token set in the **W3C Design
  Tokens Community Group (DTCG) format** (`$value`/`$type` groups): eleven themes
  (nine brand + Tungsten Phosphor + Tungsten Brassworks) × light/dark, six roles + derived
  `accentText`, typography stacks, 8px spacing rhythm, radius/content-max.
  Consumable by Style Dictionary, Tokens Studio and any DTCG-aware tooling.
- **`exports/ts-tokens.css`** — drop-in CSS custom properties for web/Electron
  apps. Mirror of the brand mechanics: `data-theme` selects a theme,
  `data-appearance` (or the OS preference) flips light/dark. Includes
  `--ts-accent-text` — per-theme AA-safe accents for accent-as-text situations,
  computed by `tools/build-tokens-css.py`.
- **Hermes skins** are themselves usable anywhere Hermes runs (CLI, TUI,
  Desktop, web dashboard) — the Desktop converts the palette automatically.

### Contrast (WCAG AA, computed by tools/build.py)

`tungsten-skylark` (dark, bg #232529):

| Pair | Ratio | Threshold |
|---|---|---|
| banner_text #F5F2EC | 13.74:1 | 4.5 |
| banner_title #FFB24D | 8.57:1 | 3.0 |
| banner_accent #FFC968 | 10.09:1 | 3.0 |
| banner_dim #A8A49C | 6.18:1 | 4.5 |
| ui_ok #76BE51 | 6.76:1 | 4.5 |
| ui_error #E86577 | 4.79:1 | 4.5 |
| ui_warn #FFA42B | 7.75:1 | 4.5 |
| prompt #F5F2EC | 13.74:1 | 4.5 |

`tungsten-skylark-light` (light, bg #F5F2EC):

| Pair | Ratio | Threshold |
|---|---|---|
| banner_text #3C3F44 | 9.46:1 | 4.5 |
| banner_title #9A5300 | 5.20:1 | 4.5 |
| banner_accent #B26300 | 4.02:1 | 3.0 (large/decorative only) |
| banner_dim #6B655B | 5.17:1 | 4.5 |
| ui_accent #9A5300 | 5.20:1 | 3.0 |
| ui_label #9A5300 | 5.20:1 | 4.5 |
| ui_ok #3F7226 | 5.15:1 | 4.5 |
| ui_error #B23244 | 5.48:1 | 4.5 |
| ui_warn #9A5300 | 5.20:1 | 4.5 |
| prompt #3C3F44 | 9.46:1 | 4.5 |

`tungsten-phosphor` (dark, bg #060D08):

| Pair | Ratio | Threshold |
|---|---|---|
| banner_text #CFF5D3 | 16.52:1 | 4.5 |
| banner_title #00FF41 | 14.39:1 | 4.5 |
| banner_accent #5CFF86 | 15.07:1 | 3.0 |
| banner_dim #6FA07A | 6.54:1 | 4.5 |
| ui_ok #3EE06C | 11.31:1 | 4.5 |
| ui_error #FF5C7A | 6.61:1 | 4.5 |
| ui_warn #E8C44A | 11.63:1 | 4.5 |
| prompt #CFF5D3 | 16.52:1 | 4.5 |

`tungsten-skylark` light overlay (bg #F5F2EC):

| Pair | Ratio | Threshold |
|---|---|---|
| banner_text #3C3F44 | 9.46:1 | 4.5 |
| banner_title #9A5300 | 5.20:1 | 4.5 |
| banner_accent #B26300 | 4.02:1 | 3.0 (large/decorative only) |
| banner_dim #6B655B | 5.17:1 | 4.5 |
| ui_ok #3F7226 | 5.15:1 | 4.5 |
| ui_error #B23244 | 5.48:1 | 4.5 |
| ui_warn #9A5300 | 5.20:1 | 4.5 |
| prompt #3C3F44 | 9.46:1 | 4.5 |

`tungsten-phosphor` light overlay — "paper printout" (bg #F0F5EC):

| Pair | Ratio | Threshold |
|---|---|---|
| banner_text #12351C | 12.23:1 | 4.5 |
| banner_title #0E6B2E | 6.00:1 | 4.5 |
| banner_accent #2E7D44 | 4.59:1 | 3.0 |
| banner_dim #4A6B54 | 5.39:1 | 4.5 |
| ui_ok #2E6B32 | 5.81:1 | 4.5 |
| ui_error #B23244 | 5.53:1 | 4.5 |
| ui_warn #7A6000 | 5.42:1 | 4.5 |
| prompt #12351C | 12.23:1 | 4.5 |

All 55 declared pairs pass; re-run `python3 tools/build.py` to re-verify.

## Repo layout

```
├── plugin.json          # Agent Plugins v1 manifest
├── skins/               # build output — committed, one skin per theme
├── themes/
│   ├── tokens.json      # portable brand tokens (all 9 brand themes)
│   ├── tungsten-skylark/        (dark)  colors.toml + meta.json
│   └── tungsten-skylark-light/ (light) colors.toml + meta.json
├── exports/ts-tokens.css  # generated CSS custom-property sheet
└── tools/               # build.py (skins+audit), build-tokens-css.py
```

## Brand notes

- Amber discipline: ~10% accent per screen; skins keep amber to titles,
  labels, borders and spinners.
- Terminal amber for light mode is darkened from brand `#FFA42B`/`#FFC968`
  to `#9A5300` — **sanctioned by brand sign-off 2026-11** as THE
  `--ts-accent-text` value; `#B26300` is large-text-only (4.02:1); brand
  ambers stay decorative. Dark mode keeps `#FFB24D` (8.57:1).
- Light/dark classification: `tungsten-skylark` and `tungsten-phosphor` are dual
  (dark base + `light_colors` overlay; each polarity audited to WCAG AA);
  `tungsten-skylark-light` = light (also stated in each theme's `meta.json`).
- Dual-mode behaviour: the CLI/TUI pick the overlay automatically on light
  terminals (Skin Engine `light_colors`/`dark_colors` support). The Desktop
  app's theme converter maps the light palette into its `colors` slot and the
  dark into `darkColors`, so the Appearance light/dark toggle transitions
  between the author's two palettes. Older Desktop builds pin one palette in
  both slots — update to a build with dual-mode converter support.
- Fleet adoption: ColourPicker / Timer / MarkdownEditor should consume
  `exports/ts-tokens.css` (per the same sign-off; YadaWallet precedent).
- Tungsten Phosphor is a retro-CRT permanent collection theme, dark-first (renamed from
  `tungsten-matrix` in v0.4.0 — breaking change). Its palette (phosphor green
  `#00FF41`, near-black `#060D08`) travels in tokens.json under its own `phosphor`
  theme id alongside the nine founding brand themes, and both its
  accents pass AA as text on their backgrounds.
