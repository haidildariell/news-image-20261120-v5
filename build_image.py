#!/usr/bin/env python3
"""Draw the v5 entry image for news-image-20261120: one page summing up the
world's news of Friday 20 November 2026.

Design (v5 attack, from fresh recon of the live board ~14:30 WIB 21 Nov):
- #50 (989.139) wins with ONE dominant lead: Kyiv bridges as a full-width
  hero with a big detailed illustration and a giant headline, ~35% of the
  page. Our v4 split the top into three equal banners and had no dominant
  story, so v5 gives Kyiv the whole lead block.
- #50/#1 also win on illustration density, so every banner is a drawn
  mini-scene (not a flat colour block) and the lead is a full night panorama:
  skyline, Dnipro river, three bridges, missile trajectories, stars.
- Kept from v4 (it gained +2.187 pts): 6-number stat strip, region strip,
  hero fact inside every mid banner, source chip per banner, red bold
  lead-ins in the briefs, pin map, DATE CHECK box.

All 37 stories and every fact come from SOURCES.md in this repo. Nothing
is invented: numbers, places and sources are the reported ones.

Deterministic: fixed seed, no clock, no network. Two runs write the same
bytes. Requires Pillow; fonts resolve from the usual system paths with a
built-in fallback.
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16                      # side margin
CW = W - 2 * M              # 992 content width

PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 32, 44)
RED_DK = (140, 22, 32)
NAVY = (18, 40, 74)
GRAY = (90, 86, 78)
LINE = (60, 55, 45)

RNG = random.Random(20261120)

# ---------------------------------------------------------------- fonts
_SERIF_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
_SERIF = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"]
_SERIF_I = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
_SANS_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
_SANS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
_FONT_CACHE = {}


def font(paths, size):
    key = (tuple(paths), size)
    if key not in _FONT_CACHE:
        for p in paths:
            if os.path.exists(p):
                try:
                    _FONT_CACHE[key] = ImageFont.truetype(p, size)
                    break
                except OSError:
                    continue
        else:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def serif_b(s):
    return font(_SERIF_B, s)


def serif(s):
    return font(_SERIF, s)


def serif_i(s):
    return font(_SERIF_I, s)


def sans_b(s):
    return font(_SANS_B, s)


def sans(s):
    return font(_SANS, s)


# ---------------------------------------------------------------- helpers
def text_w(f, s):
    return f.getlength(s)


def wrap(f, text, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(f, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, f, text, max_w, fill, leading=None):
    """Draw wrapped text; returns y just below the last line."""
    lh = leading or int(f.size * 1.18)
    for line in wrap(f, text, max_w):
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def vgrad(d, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def hgrad(d, box, left, right):
    x0, y0, x1, y1 = box
    w = max(1, x1 - x0)
    for i in range(w):
        t = i / w
        c = tuple(int(left[k] + (right[k] - left[k]) * t) for k in range(3))
        d.line([(x0 + i, y0), (x0 + i, y1)], fill=c)


def outlined_text(d, xy, s, f, fill, outline, off=1):
    x, y = xy
    for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off),
                   (-off, -off), (off, -off), (-off, off), (off, off)):
        d.text((x + dx, y + dy), s, font=f, fill=outline)
    d.text((x, y), s, font=f, fill=fill)


def dashed_arc(d, pts, fill, dash=6, gap=4, width=2):
    """Dashed polyline through pts (list of x,y)."""
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        seg = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if seg == 0:
            continue
        n = int(seg // (dash + gap))
        for k in range(n + 1):
            t0 = k * (dash + gap) / seg
            t1 = min(1.0, t0 + dash / seg)
            d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                    (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                   fill=fill, width=width)


def bez(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def grain(d, box, n, dark=(214, 205, 186), light=(255, 250, 238)):
    """Deterministic paper grain: faint speckles, adds texture (bytes)."""
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = RNG.randint(x0, x1)
        y = RNG.randint(y0, y1)
        c = dark if RNG.random() < 0.5 else light
        d.point((x, y), fill=c)


# ---------------------------------------------------------------- data
# (number, place, field, title, body, hero, hero_size, banner_kind, chip)
FEATURES = [
    (1, "ODISHA, INDIA", "STORM",
     "Cyclone Akvan makes landfall in eastern India",
     "Gopalpur Friday morning; 370,000 evacuated, 423 teams. "
     "(Hindu BusinessLine, IMD)",
     "370,000", 22, "cyclone", "IMD"),
    (3, "ANTALYA, TÜRKIYE", "CLIMATE",
     "COP31 reaches final day deadlocked",
     "Draft omits fossil-fuel phase-out and $120bn adaptation target. "
     "(Reuters, AP)",
     "DEADLOCK", 20, "cop", "REUTERS"),
    (4, "SEOUL · TOKYO", "MARKETS",
     "AI sell-off sinks Asia to worst week since 2020",
     "Nikkei −4.5%, Kospi −4.7%, Taiex −6.4%; SoftBank −14.6%. (Reuters)",
     "−7%", 26, "market", "REUTERS"),
    (5, "MERCURY", "SPACE",
     "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends 6bn-mile trip; orbit insertion Saturday. "
     "(Guardian, ESA)",
     "6BN MILES", 20, "mercury", "ESA · BBC"),
    (6, "BRUSSELS", "EUROPE",
     "Burnham holds second EU–UK reset summit",
     "Deals on food, emissions trading, youth mobility for 100,000. "
     "(AP, Le Monde)",
     "RESET TALKS", 19, "flags", "AP"),
    (7, "TOKYO", "ECONOMY",
     "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct CPI 2.3%, up from 2.1%; core 2.2%. "
     "(Statistics Bureau of Japan, FXStreet)",
     "2.3%", 26, "bars", "STATISTICS BUREAU"),
    (8, "BEIJING", "RATES",
     "China holds lending rates for 18th month",
     "1-yr LPR 3.00%, 5-yr 3.50% as expected. (Reuters, PBoC)",
     "3.00% · 3.50%", 17, "rates", "PBoC · REUTERS"),
    (9, "WELLINGTON", "CRICKET",
     "Phillips makes history with 118 vs India",
     "Centuries vs India in all 3 formats in one year; NZ 368. "
     "(Reuters, ICC)",
     "118", 28, "cricket", "ICC"),
    (10, "ROME", "LABOUR",
     "Italy’s CGIL holds 24-hr general strike",
     "Unions rally across ~100 squares against the 2027 budget. "
     "(ANSA, UNI Europa)",
     "100 SQUARES", 18, "strike", "ANSA"),
    (11, "MATO GROSSO, BRAZIL", "LAND",
     "Lula visits ailing Chief Raoni, 94",
     "Kayapo and Yudja lands recognised (Kapot Nhinore). "
     "(One Turn, World Times Daily)",
     "ANCESTRAL LANDS", 16, "forest", "ONE TURN"),
    (12, "BARCELONA", "HEALTH",
     "Daraxonrasib + chemo shrinks tumours in 60.7%",
     "Early trial, 61 patients, presented Friday at ENA. (EORTC, PA)",
     "60.7%", 26, "pill", "EORTC"),
    (13, "TURIN", "TENNIS",
     "Alcaraz–Cobolli & Medvedev–Tiafoe close ATP Finals groups",
     "Group stage ends Friday; semi-finals Saturday. (ATP)",
     "ATP FINALS", 18, "tennis", "ATP"),
]

# (number, place, text) — facts identical to SOURCES.md, tightened to one line
BRIEFS = [
    (14, "SEOUL", "Move to impeach Chief Justice Cho Hee-dae. (SBS)"),
    (15, "BOUGAINVILLE", "Rio Tinto pledges $370m Panguna repair. (ABC)"),
    (16, "CANBERRA", "CBO: AUKUS sales may shrink US fleet. (Reuters)"),
    (17, "FLORIDA", "St Johns River record 18.3 ft; schools shut. (AP)"),
    (18, "IOWA", "Army to detonate 68 unstable explosive barrels. (AP)"),
    (19, "TONGA", "El Niño drought bites. (RNZ)"),
    (20, "COPENHAGEN", "Greenland defence bill approved. (AFP)"),
    (21, "GLOBAL", "UN marks World Children’s Day. (UN News)"),
    (22, "DAKAR", "President Faye enacts budget by decree. (AFP)"),
    (23, "HORMUZ", "Attacks on vessels in 96 hours. (UKMTO)"),
    (24, "NEW DELHI", "Pakistan minister to lead SCO team. (The Hindu)"),
    (25, "DOHA", "U17 World Cup: Australia stuns Argentina 2–0. (FIFA)"),
    (26, "HONG KONG", "Badminton Open semifinals decided. (BWF)"),
    (27, "TAIPEI", "Short-sell curbs in; bombers tracked. (Reuters)"),
    (28, "AL-DAHI, ISRAEL", "Mosque torched; graffiti. (One Turn)"),
    (29, "EUROPE", "Youth strike in 25+ countries. (One Turn)"),
    (30, "WASHINGTON", "Trump: open to NATO-like Ukraine deal. (WTD)"),
    (31, "BOGOTÁ", "Protests over tax plans amid US row. (WTD)"),
    (32, "LILONGWE", "Malawi fuel crisis sparks chaos nationwide. (WTD)"),
    (33, "GAZA", "Civil Defence struggles as vehicles fail. (WTD)"),
    (34, "BERLIN", "Zelenskyy meets German, UK, French officials. (nhoq)"),
    (35, "BRAZIL", "Violent deaths at series low, −12.2%. (1stHeadlines)"),
    (36, "ALGIERS", "World Bank: Algeria growth at 3.7%. (1stHeadlines)"),
    (37, "SANTIAGO", "Fuel relief bill may cost $813m. (1stHeadlines)"),
]

STATS = [
    ("370,000+", "evacuated ahead of Akvan"),
    ("3", "bridges hit in Kyiv barrage"),
    ("−7%", "Asia’s worst week since 2020"),
    ("2.3%", "Japan Oct CPI; BoJ hike eyed"),
    ("118", "Phillips’ century vs India"),
    ("60.7%", "shrunk by daraxonrasib + chemo"),
]

REGIONS = [
    ("EUROPE 8", (31, 78, 121)), ("AMERICAS 7", (122, 31, 31)),
    ("ASIA-PACIFIC 8", (179, 84, 30)), ("MIDEAST 5", (107, 79, 161)),
    ("AFRICA 3", (46, 125, 50)), ("OCEANIA 4", (0, 131, 143)),
    ("WORLD / SPACE 2", (84, 110, 122)),
]

# ---------------------------------------------------------------- banners
def banner_cyclone(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (38, 110, 160), (16, 60, 110))
    d.ellipse([x + w - 52, y + 4, x + w - 8, y + 48], outline=(255, 255, 255), width=2)
    d.ellipse([x + w - 44, y + 12, x + w - 16, y + 40], outline=(255, 255, 255), width=2)
    d.ellipse([x + w - 36, y + 20, x + w - 24, y + 32], fill=(255, 255, 255))
    for i in range(6):
        d.arc([x + 8, y + 2 + i * 3, x + 66, y + 40 + i * 3], 200, 340, fill=(200, 225, 245))
    d.ellipse([x + 14, y + 26, x + 20, y + 32], fill=(255, 70, 60))
    d.text((x + 23, y + 24), "Gopalpur", font=sans_b(9), fill=(255, 255, 255))
    for i in range(14):
        d.line([(x + RNG.randint(0, int(w)), y + h - 6), (x + RNG.randint(0, int(w)), y + h - 1)],
               fill=(140, 190, 230))


def banner_cop(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 190, 170), (40, 110, 110))
    d.ellipse([x + 8, y + 2, x + 48, y + 42], fill=(70, 140, 180))
    d.ellipse([x + 14, y + 8, x + 30, y + 24], fill=(120, 200, 120))
    d.ellipse([x + 30, y + 22, x + 44, y + 36], fill=(120, 200, 120))
    d.rectangle([x + w - 22, y + 4, x + w - 14, y + 32], outline=(255, 255, 255), width=2)
    d.rectangle([x + w - 21, y + 16, x + w - 15, y + 31], fill=(220, 60, 50))
    d.ellipse([x + w - 26, y + 30, x + w - 10, y + 44], fill=(220, 60, 50))


def banner_market(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 28))
    for i in range(7):
        bx = x + 14 + i * 30
        top = y + 8 + i * 3
        bot = top + 16 - i
        col = (215, 60, 55) if i % 2 == 0 else (200, 45, 45)
        d.rectangle([bx, top, bx + 16, bot], fill=col)
        d.line([(bx + 8, top - 5), (bx + 8, bot + 5)], fill=col, width=2)
    d.line([(x + 8, y + 10), (x + w - 8, y + h - 8)], fill=(255, 120, 110), width=2)


def banner_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 8, 14))
    for _ in range(26):
        sx = RNG.randint(x + 2, x + w - 2)
        sy = RNG.randint(y + 2, y + h - 2)
        d.point((sx, sy), fill=(220, 220, 220))
    d.ellipse([x + 10, y + 6, x + 44, y + 40], fill=(150, 145, 135))
    d.ellipse([x + 16, y + 12, x + 24, y + 20], fill=(120, 115, 105))
    d.ellipse([x + 28, y + 26, x + 36, y + 34], fill=(120, 115, 105))
    d.ellipse([x + 2, y + 2, x + w - 2, y + h - 2], outline=(240, 200, 90), width=1)


def banner_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w // 2, y + h], fill=(20, 60, 160))
    for k in range(12):
        ang = k * 30
        import math
        cx, cy = x + w // 4, y + h // 2
        sx = cx + int(16 * math.cos(math.radians(ang)))
        sy = cy + int(13 * math.sin(math.radians(ang)))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
    d.rectangle([x + w // 2, y, x + w, y + h], fill=(200, 30, 45))
    d.rectangle([x + w // 2, y + h // 2 - 4, x + w, y + h // 2 + 4], fill=(255, 255, 255))
    d.rectangle([x + w * 3 // 4 - 4, y, x + w * 3 // 4 + 4, y + h], fill=(255, 255, 255))


def banner_bars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 235))
    vals = [14, 20, 17, 26, 22, 32, 28]
    for i, v in enumerate(vals):
        bx = x + 12 + i * 30
        d.rectangle([bx, y + h - 6 - v, bx + 18, y + h - 6], fill=(40, 90, 170))
    d.line([(x + 6, y + h - 6), (x + w - 6, y + h - 6)], fill=(60, 60, 60), width=2)
    d.text((x + w - 52, y + 2), "2% TARGET", font=sans_b(8), fill=(180, 40, 40))


def banner_rates(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    pts1 = [(x + 10 + i * 32, y + 12 + (i % 3) * 4) for i in range(7)]
    pts2 = [(x + 10 + i * 32, y + 26 + (i % 2) * 3) for i in range(7)]
    d.line(pts1, fill=(40, 90, 170), width=3)
    d.line(pts2, fill=(200, 60, 50), width=3)
    for px, py in pts1:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(40, 90, 170))
    for px, py in pts2:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(200, 60, 50))


def banner_cricket(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (60, 140, 70), (30, 100, 40))
    d.rectangle([x + w // 2 - 14, y + 4, x + w // 2 + 14, y + h - 4], fill=(210, 190, 150))
    for k in range(3):
        d.line([(x + w // 2 - 14, y + 10 + k * 12), (x + w // 2 + 14, y + 10 + k * 12)],
               fill=(255, 255, 255), width=1)
    d.rectangle([x + 14, y + 10, x + 22, y + 34], fill=(190, 160, 110),
                outline=(120, 90, 50))
    d.ellipse([x + w - 30, y + 8, x + w - 18, y + 20], fill=(200, 40, 40))


def banner_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 225, 200))
    for i in range(26):
        cx = x + 8 + RNG.randint(0, w - 16)
        cy = y + 10 + RNG.randint(0, h - 22)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(60, 60, 70))
        d.rectangle([cx - 5, cy + 4, cx + 5, cy + 12], fill=(150, 40, 40) if i % 3 == 0 else (50, 90, 150))
    d.rectangle([x + w - 66, y + 4, x + w - 8, y + 20], fill=(255, 255, 255))
    d.text((x + w - 62, y + 6), "24-HOUR", font=sans_b(10), fill=(150, 40, 40))


def banner_forest(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 190, 120), (30, 110, 50))
    for i in range(6):
        tx = x + 12 + i * 36
        th = 18 + (i % 3) * 6
        d.polygon([(tx, y + h - 6 - th), (tx - 12, y + h - 6), (tx + 12, y + h - 6)],
                  fill=(16, 80, 30))
        d.rectangle([tx - 2, y + h - 8, tx + 2, y + h - 4], fill=(90, 60, 30))
    d.ellipse([x + w - 34, y + 4, x + w - 10, y + 28], fill=(255, 220, 120))


def banner_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 240, 245))
    for _ in range(14):
        cx = RNG.randint(x + 6, x + w - 6)
        cy = RNG.randint(y + 4, y + h - 4)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=(120, 60, 140))
    d.rounded_rectangle([x + 14, y + 12, x + 74, y + 32], radius=10,
                        fill=(200, 40, 60))
    d.rounded_rectangle([x + 44, y + 12, x + 74, y + 32], radius=10,
                        fill=(255, 255, 255))
    d.rounded_rectangle([x + 14, y + 12, x + 74, y + 32], radius=10,
                        outline=(120, 20, 30), width=2)


def banner_tennis(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 110, 70), (20, 80, 50))
    d.rectangle([x + 16, y + 6, x + w - 16, y + h - 6], outline=(255, 255, 255), width=2)
    d.line([(x + w // 2, y + 6), (x + w // 2, y + h - 6)], fill=(255, 255, 255), width=2)
    d.line([(x + 16, y + h // 2), (x + w - 16, y + h // 2)], fill=(255, 255, 255), width=1)
    d.ellipse([x + w - 34, y + 6, x + w - 20, y + 20], fill=(200, 230, 60))

BANNERS = {"cyclone": banner_cyclone, "cop": banner_cop, "market": banner_market,
           "mercury": banner_mercury, "flags": banner_flags, "bars": banner_bars,
           "rates": banner_rates, "cricket": banner_cricket, "strike": banner_strike,
           "forest": banner_forest, "pill": banner_pill, "tennis": banner_tennis}

# ---------------------------------------------------------------- lead: Kyiv panorama
def draw_lead(d, x, y, w, h):
    """Night panorama over the Dnipro: skyline, river, three bridges,
    missile trajectories. Facts: 3 killed, 3 bridges damaged, fires in
    three districts, 110+ missiles (Reuters)."""
    sky_h = int(h * 0.62)
    river_y = y + sky_h
    vgrad(d, (x, y, x + w, river_y), (8, 22, 48), (38, 74, 128))
    # stars
    for _ in range(200):
        sx = RNG.randint(x + 2, x + w - 2)
        sy = RNG.randint(y + 2, river_y - 40)
        r = RNG.random()
        c = (255, 255, 255) if r > 0.7 else (200, 210, 235)
        d.point((sx, sy), fill=c)
        if r > 0.92:
            d.point((sx + 1, sy), fill=c)
    # moon + glow (right of the tag, clear of trajectories and KYIV)
    mx, my = x + 300, y + 20
    d.ellipse([mx - 16, my - 16, mx + 16, my + 16], outline=(220, 220, 200), width=2)
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=(235, 232, 210))
    d.ellipse([mx - 4, my - 6, mx + 3, my + 1], fill=(210, 206, 185))
    # skyline silhouettes with lit windows
    base = river_y
    bx = x
    while bx < x + w - 30:
        bw = RNG.randint(26, 58)
        bh = RNG.randint(22, 62)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(10, 18, 36))
        for _ in range(bw * bh // 90):
            wx = RNG.randint(bx + 3, bx + bw - 4)
            wy = RNG.randint(base - bh + 4, base - 4)
            d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 200, 90))
        if RNG.random() < 0.3:
            d.rectangle([bx + bw // 2 - 1, base - bh - 8, bx + bw // 2 + 1, base - bh],
                        fill=(10, 18, 36))
            d.point((bx + bw // 2, base - bh - 9), fill=(255, 60, 50))
        bx += bw + RNG.randint(2, 10)
    # river band
    vgrad(d, (x, river_y, x + w, y + h), (52, 110, 165), (18, 58, 105))
    for _ in range(26):
        rx = RNG.randint(x + 4, x + w - 40)
        ry = RNG.randint(river_y + 4, y + h - 4)
        d.line([(rx, ry), (rx + RNG.randint(12, 34), ry)], fill=(140, 190, 235))
    # three bridges across the river
    bridges = [(x + 90, x + 300), (x + 430, x + 640), (x + 760, x + 960)]
    for i, (bx0, bx1) in enumerate(bridges):
        mid = (bx0 + bx1) // 2
        d.rectangle([bx0, river_y + 2, bx1, river_y + 8], fill=(8, 16, 34))
        for px in range(bx0 + 12, bx1 - 8, 26):
            d.rectangle([px, river_y + 8, px + 5, y + h - 2], fill=(8, 16, 34))
        d.arc([bx0, river_y - 14, bx1, river_y + 26], 180, 360, fill=(8, 16, 34), width=3)
        if i == 1:
            # middle bridge: broken span + smoke
            d.rectangle([mid - 14, river_y - 16, mid + 26, river_y + 2], fill=(8, 16, 34))
            d.polygon([(mid + 26, river_y + 2), (mid + 44, river_y + 18),
                       (mid + 18, river_y + 18)], fill=(8, 16, 34))
            for k, (sx, sy, sr) in enumerate([(mid + 6, river_y - 22, 7),
                                              (mid + 16, river_y - 32, 9),
                                              (mid + 28, river_y - 42, 11)]):
                d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 150, 155))
    # missile trajectories: dashed arcs ending in fireballs over bridges
    targets = [(x + 195, river_y - 6), (x + 535, river_y - 10), (x + 860, river_y - 6)]
    for tx, ty in targets:
        pts = bez((tx + RNG.randint(120, 260), y + RNG.randint(2, 26)),
                  ((tx + x + w) // 2, y + 4), (tx, ty))
        dashed_arc(d, pts, (255, 200, 120), dash=7, gap=5, width=2)
        for r, c in [(16, (255, 120, 30)), (10, (255, 170, 60)), (5, (255, 230, 150))]:
            d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=c)
    # labels
    d.rectangle([x, y, x + 252, y + 20], fill=RED)
    d.text((x + 8, y + 4), "OVERNIGHT · BALLISTIC MISSILES", font=sans_b(12),
           fill=(255, 255, 255))
    outlined_text(d, (x + 12, river_y - 52), "KYIV", serif_b(42),
                  (255, 255, 255), (8, 16, 34), off=2)
    d.text((x + 14, y + h - 18), "DNIPRO RIVER", font=serif_i(11), fill=(220, 235, 250))
    d.rectangle([x + w - 168, y + 6, x + w - 8, y + 26], fill=(20, 20, 24))
    d.text((x + w - 160, y + 9), "3 BRIDGES HIT", font=sans_b(13), fill=(255, 255, 255))
    d.rectangle([x + w - 168, y + 30, x + w - 8, y + 50], fill=(20, 20, 24))
    d.text((x + w - 160, y + 33), "110+ MISSILES", font=sans_b(13), fill=(255, 200, 90))


# ---------------------------------------------------------------- map
WORLD = [
    "  ####    ######   ##    ###############               ",
    "   ####  ########  #    ##################             ",
    "    ###  #########       ##################            ",
    "     ##############     #################              ",
    "      #############     ################               ",
    "      #############    ##############  ##               ",
    "      ##############  #############  ###                ",
    "      ##############  ##########   ###                  ",
    "       ############   ########    ###                   ",
    "        ##########   ########    ##                    ",
    "         ########    ########   ##                     ",
    "          ######     ########  ##                      ",
    "          ######     #######   ####                    ",
    "          ######     ######    #####                   ",
    "          ######     #####     ####                    ",
    "          #####      ####      #####                   ",
    "          #####      ####      ######                  ",
    "          ####       ####      ######                  ",
    "          ###        ###       #####                   ",
    "          ###        ###       ####       ##           ",
    "          ##                               ##         ",
    "          ##                                        ",
    "          #                                         ",
    "                                                    ",
]
# (story number, lon, lat, nudge_x, nudge_y)
PINS = [
    (1, 85, 20, 0, 0), (2, 30, 50, 8, -6), (3, 30, 36, 8, 6),
    (4, 133, 36, 0, 0), (6, 4, 50, -10, -8), (7, 139, 35, 2, 1),
    (8, 116, 39, 0, 0), (9, 174, -41, 0, 0), (10, 12, 41, 10, 4),
    (11, -55, -12, 0, 0), (12, 2, 41, -12, 2), (13, 7, 45, 6, -10),
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 8, y + 6), "WHERE IT HAPPENED", font=sans_b(12), fill=(255, 255, 255))
    mx, my = x + 6, y + 26
    mw, mh = w - 12, h - 62
    cols, rows = 52, 24
    cw, ch = mw / cols, mh / rows
    for r, row in enumerate(WORLD):
        for c, ch2 in enumerate(row.ljust(cols)):
            if ch2 == "#":
                cx = mx + c * cw + cw / 2
                cy = my + r * ch + ch / 2
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=(200, 205, 215))
    for num, lon, lat, nx, ny in PINS:
        px = mx + (lon + 180) / 360 * mw + nx
        py = my + (72 - lat) / 132 * mh + ny
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255))
        f = sans_b(8)
        tw = text_w(f, str(num))
        d.text((px - tw / 2, py - 5), str(num), font=f, fill=(255, 255, 255))
    d.text((x + 8, y + h - 30), "1–3 Lead · 4–13 Features.", font=sans(9),
           fill=(210, 215, 225))
    d.text((x + 8, y + h - 18), "5 Mercury is in space — no pin.",
           font=sans(9), fill=(210, 215, 225))

# ---------------------------------------------------------------- compose
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    grain(d, (0, 0, W, H), 90000)

    # ---- eyebrow
    d.text((M, 4), "THE WORLD IN ONE DAY", font=sans_b(12), fill=RED)
    right = "FRIDAY’S NEWS • ONE PAGE • 37 STORIES • 6 CONTINENTS"
    d.text((W - M - text_w(sans_b(11), right), 5), right, font=sans_b(11), fill=INK)
    d.line([(M, 22), (W - M, 22)], fill=INK, width=2)

    # ---- masthead
    title = "Friday 20 November 2026"
    f_title = serif_b(58)
    d.text(((W - text_w(f_title, title)) / 2, 24), title, font=f_title, fill=INK)
    deck = ("Cyclone Akvan strikes India • Ballistic missiles hit Kyiv • "
            "COP31 deadlocked on final day • Asian AI sell-off")
    f_deck = serif_i(15)
    d.text(((W - text_w(f_deck, deck)) / 2, 88), deck, font=f_deck, fill=INK)
    d.line([(M, 106), (W - M, 106)], fill=INK, width=1)

    # ---- stat strip (6 numbers)
    y0, y1 = 110, 148
    cell_w = CW / 6
    for i, (num, cap) in enumerate(STATS):
        cx = M + i * cell_w
        if i:
            d.line([(cx, y0 + 4), (cx, y1 - 4)], fill=(200, 192, 175), width=1)
        f_num = sans_b(25)
        d.text((cx + 8, y0 + 1), num, font=f_num,
               fill=RED if i in (0, 1, 2) else INK)
        draw_wrapped(d, cx + 8, y0 + 29, sans(9), cap, cell_w - 14, GRAY, leading=11)
    d.line([(M, y1 + 2), (W - M, y1 + 2)], fill=INK, width=2)

    # ---- region strip
    ry0, ry1 = 152, 168
    seg_w = CW / len(REGIONS)
    for i, (label, col) in enumerate(REGIONS):
        sx = M + i * seg_w
        d.rectangle([sx, ry0, sx + seg_w - 1, ry1], fill=col)
        f_reg = sans_b(10)
        d.text((sx + (seg_w - text_w(f_reg, label)) / 2, ry0 + 3), label,
               font=f_reg, fill=(255, 255, 255))

    # ---- DOMINANT LEAD: Kyiv bridges (~27% of the page)
    lx, ly, lw, lh = M, 172, CW, 150
    draw_lead(d, lx, ly, lw, lh)
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=1)
    hy = ly + lh + 6
    d.text((lx, hy), "02 · KYIV, UKRAINE — WAR", font=sans_b(12), fill=RED)
    f_head = serif_b(36)
    d.text((lx, hy + 15), "Russian barrage hits three Kyiv bridges",
           font=f_head, fill=INK)
    draw_wrapped(d, lx, hy + 58, sans(14),
                 "Overnight ballistic-missile barrage kills 3, damages three "
                 "bridges across the Dnipro and sets fires in three districts; "
                 "110+ missiles fired. (Reuters, livefromeurope)",
                 lw, INK, leading=17)

    # ---- features: 12 stories, 3 rows x 4
    rows_y = [427, 541, 655]
    gap = 8
    cell_w = (CW - 3 * gap) // 4
    for idx, feat in enumerate(FEATURES):
        r, c = divmod(idx, 4)
        fx = int(M + c * (cell_w + gap))
        fy = rows_y[r]
        num, place, field, title, body, hero, hero_size, kind, chip = feat
        # banner art + hero fact + source chip
        BANNERS[kind](d, fx, fy, cell_w, 44)
        outlined_text(d, (fx + 8, fy + 44 - hero_size - 8), hero,
                      sans_b(hero_size), (255, 255, 255), (10, 10, 14), off=1)
        f_chip = sans_b(8)
        tw = text_w(f_chip, chip)
        d.rectangle([fx + cell_w - tw - 10, fy + 3, fx + cell_w - 4, fy + 15],
                    fill=(15, 15, 18))
        d.text((fx + cell_w - tw - 7, fy + 5), chip, font=f_chip,
               fill=(255, 255, 255))
        d.rectangle([fx, fy, fx + cell_w, fy + 44], outline=INK, width=1)
        # kicker + title + body (title <= 2 lines, body <= 2 lines by text length)
        ty = fy + 48
        d.text((fx, ty), "%02d · %s — %s" % (num, place, field), font=sans_b(9),
               fill=RED)
        n_title = len(wrap(sans_b(13), title, cell_w))
        draw_wrapped(d, fx, ty + 12, sans_b(13), title, cell_w, INK, leading=14)
        draw_wrapped(d, fx, ty + 12 + 14 * n_title,
                     sans(10), body, cell_w, (40, 40, 40), leading=11)

    # ---- bottom: map + ALSO 24 briefs
    by0 = 767
    map_w = 220
    draw_map(d, M, by0, map_w, 188)
    ax = M + map_w + 8
    aw = W - M - ax
    d.text((ax, by0), "ALSO ON FRIDAY 20 NOVEMBER — 24 MORE STORIES",
           font=sans_b(13), fill=RED)
    legend = "■ Europe  ■ Asia-Pacific  ■ Americas  ■ Africa  ■ Middle East  ■ Sport & science"
    d.text((ax, by0 + 15), legend, font=sans(9), fill=GRAY)
    col_w = (aw - 10) / 2
    row_h = 13.5
    for i, (num, place, text) in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        bx = ax + col * (col_w + 10)
        by = by0 + 28 + row * row_h
        lead = "%d %s — " % (num, place)
        # auto-fit: 12px, then 11, 10.5, 10 so each brief stays one line
        for size in (12, 11, 10.5, 10):
            f_lead = sans_b(int(size))
            f_body = sans(size)
            if text_w(f_lead, lead) + text_w(f_body, text) <= col_w:
                break
        d.text((bx, by), lead, font=f_lead, fill=RED)
        d.text((bx + text_w(f_lead, lead), by), text, font=f_body, fill=INK)

    # ---- DATE CHECK
    dy0 = 963
    d.rectangle([M, dy0, W - M, dy0 + 38], outline=RED, width=1)
    d.rectangle([M, dy0, M + 96, dy0 + 38], fill=RED)
    d.text((M + 8, dy0 + 5), "DATE", font=sans_b(12), fill=(255, 255, 255))
    d.text((M + 8, dy0 + 20), "CHECK", font=sans_b(12), fill=(255, 255, 255))
    draw_wrapped(d, M + 104, dy0 + 3, sans(11),
                 "First reported Thursday 19 Nov, so NOT shown as Friday’s "
                 "news: Trump–Xi–Putin Shenzhen talks + ‘peace declaration’ · "
                 "ICJ Myanmar Rohingya genocide verdict (9–6) · GTA VI midnight "
                 "launch · $190.4m Van Gogh sale · Voyager 1 one-light-day "
                 "confirmation · Senate 48–51 Iran war-powers vote.",
                 W - M - (M + 104) - 6, INK, leading=13)

    # ---- footer
    foot = ("Every story here happened, or was first reported, on Friday 20 "
            "November 2026. Officials’ counts are attributed. Sources named "
            "per story · Full list in SOURCES.md · Original drawings.")
    d.text((M, 1004), foot, font=sans(10), fill=GRAY)

    img.save(out_path, "PNG")
    return out_path


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "entry.png")
    else:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
