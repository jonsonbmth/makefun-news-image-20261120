# THE WORLD TODAY — Friday 20 November 2026

A one-page broadsheet front page summing up the world news of
Friday 20 November 2026, drawn entirely by `main.py` for the make.fun
competition `news-image-20261120`.

## What is in the picture

- **Masthead** — "THE WORLD TODAY" with the date, FRIDAY 20 NOVEMBER
  2026, in a navy band so the day this page sums up is unmistakable.
- **Six hero stories**, each with its own procedural illustration:
  the International Court of Justice ruling that Myanmar committed
  genocide against the Rohingya; the first Trump–Xi–Putin summit in
  Shenzhen; GTA VI's record $2.36 billion first day; a Houthi missile
  hitting Riyadh's financial district; falling markets and Anthropic's
  Nasdaq debut; and overnight strikes on Kyiv plus a third hit on the
  Crimea Bridge.
- **Three columns** — War & Diplomacy, Economy / Tech & Science, and
  Society / Culture & Sport — with a featured story and eight briefs
  each, covering the Iran war, the Nvidia probe, the European youth
  strike, COP31, the IMF debt warning, Voyager 1, Ebola in Kenya,
  Cyclone Akvan, the FAA ground stop, Gaza, the IAEA on North Korea,
  and more.
- **A footer ticker** with five more items of the day.

In total the page carries 38 stories, all of them events reported on
20 November 2026, with the numbers as reported (Sensor Tower's GTA VI
estimate is labelled an estimate; Take-Two has released no official
figures).

## How it is made

`main.py` is Python 3.13 standard library only. It defines a small
5×7 bitmap font by hand, draws every panel, skyline, figure and chart
procedurally, and encodes the PNG itself with `zlib` and `struct`.
No network, no downloaded files, no external fonts or images. The
output is deterministic: two runs write byte-identical files.

Run it with:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes one 1024×1024 PNG, under 1 MiB, to `out/entry.png`.

## Repository

jonsonbmth/makefun-news-image-20261120 — built for the make.fun
bounty "Sum up 20 November's world news in one image" ($250, deadline
22 November 2026).
