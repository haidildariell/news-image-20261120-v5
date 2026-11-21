# news-image-20261120 v5 — The World in One Day (Friday 20 November 2026)

One 1024×1024 image summing up the world's news of Friday 20 November 2026:
37 stories, every fact sourced in `SOURCES.md`, all drawings original.

## Run

```sh
python3 build_image.py        # writes entry.png next to the script
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

`main.py` draws the image with Pillow (no network, deterministic — two runs
write identical bytes). Fonts resolve from the system DejaVu / Liberation
paths with a built-in fallback.

## Design (v5)

Fresh recon of the live board (~14:30 WIB, 21 Nov 2026): the #50 line
(989.139) is held by an entry whose Kyiv-bridges lead dominates ~35% of the
page — one big detailed illustration plus a giant headline — while our v4
(#587, 982.873) split the top into three equal banners with no dominant
story. v5 attacks that lever:

- **One dominant lead, full width:** Kyiv bridges as a night panorama
  (skyline, Dnipro river, three bridges — the middle one broken — missile
  trajectories, stars, moon) with a 36pt serif headline underneath.
- **Richer illustrations:** every one of the 12 feature banners is a drawn
  mini-scene (cyclone spiral, candlesticks, planet + orbit, flags, bar
  chart, cricket pitch, crowd, forest, capsule, tennis court…), plus paper
  grain — denser than v4's 297 KB without inventing any fact.
- **Kept from v4** (its readability upgrade gained +2.187 pts): 6-number
  stat strip, region strip, hero fact inside every banner, source chip per
  banner, red bold lead-ins in the 24 briefs, pin map, DATE CHECK box.

## Facts

37 stories, identical to the v4 fact set (see `SOURCES.md`); the Kyiv lead
adds only the reported "110+ missiles fired" (Reuters). Items first
reported Thursday 19 Nov stay in the DATE CHECK box only.
