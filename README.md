# TungstenSkylark Themes

Official TungstenSkylark brand themes for Hermes surfaces (CLI, TUI, Desktop)
plus a portable token sheet other apps can consume directly.

Source of truth for colours: the brand `ts-brand.css` / TS-Themes.md framework
(nine themes × light/dark, five colour roles, ~10% amber discipline, Chakra
Petch + Space Mono). Reference-only; nothing in this repo writes into the
brand material.

## Skins

| Skin | Classification | Description |
|---|---|---|
| `tungsten-skylark` | dark | Skylark brand base — amber `#FFB24D` on tungsten `#232529`, text `#F5F2EC` |
| `tungsten-skylark-light` | light | Skylark brand base for bright terminals — cream `#F5F2EC`, amber text darkened to `#9A5300`/`#B26300` to hold WCAG AA |

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

- **`themes/tokens.json`** — machine-readable token set: nine themes × light/dark,
  six roles (bg, surface, text, accent, accent_soft, ink), typography stacks,
  8px spacing rhythm, and the brand's derived-colour recipes (text-soft,
  line, glow). Import into design tools, code generators, or native apps.
- **`exports/ts-tokens.css`** — drop-in CSS custom properties for web/Electron
  apps. Mirror of the brand mechanics: `data-theme` selects one of the nine
  themes, `data-appearance` (or the OS preference) flips light/dark. Includes
  `--ts-accent-text` — per-theme AA-safe accents for amber-as-text situations,
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

All 22 declared pairs pass; re-run `python3 tools/build.py` to re-verify.

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
- Light/dark classification: `tungsten-skylark` = dark, `tungsten-skylark-light`
  = light (also stated in each theme's `meta.json`).
- Fleet adoption: ColourPicker / Timer / MarkdownEditor should consume
  `exports/ts-tokens.css` (per the same sign-off; YadaWallet precedent).
