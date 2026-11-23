#!/usr/bin/env python3
"""The World in One Day - Sunday 22 November 2026.

One-page newspaper front page drawn with Pillow. All 55 stories
happened on Sunday 22 November 2026. Deterministic: no clock, no
randomness, no network. Run: python3 main.py -> out/entry.png
"""

import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
M = 24
CW = 976
RIGHT = M + CW

PAPER = (247, 241, 222)
PAPER_DARK = (238, 230, 205)
INK = (20, 20, 22)
NAVY = (20, 38, 74)
NAVY_DARK = (13, 24, 51)
RED = (176, 30, 36)
RED_TINT = (251, 236, 236)
GOLD = (185, 138, 31)
GREY = (90, 88, 80)
RULE = (120, 110, 88)
MAP_SKY = (208, 224, 232)
MAP_LAND = (232, 214, 176)
MAP_LINE = (170, 150, 110)
CREAM = (240, 230, 200)
WHITE = (255, 255, 255)

TAG_COLOURS = {
    "CONFIRMED": (34, 120, 60),
    "REPORTED": (60, 90, 140),
    "CLAIM": (176, 90, 20),
    "PENDING": (100, 70, 140),
}

REGION_COLOURS = {
    "EUROPE": (31, 78, 140),
    "MIDDLE EAST": (176, 30, 36),
    "ASIA-PACIFIC": (196, 110, 20),
    "AMERICAS": (0, 128, 128),
    "AFRICA": (46, 125, 50),
    "OCEANIA": (106, 76, 147),
}

REGIONS = [
    ("EUROPE", 17),
    ("MIDDLE EAST", 7),
    ("ASIA-PACIFIC", 7),
    ("AMERICAS", 19),
    ("AFRICA", 4),
    ("OCEANIA", 1),
]

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed"),
    ("720/9", "India's record Test total in NZ"),
    ("856", "candidates in Hong Kong vote"),
]

UTC_EVENTS = [
    "01:00 HK polls open",
    "06:00 Ukraine reports 161 downed",
    "10:00 HK polls close",
    "~13:30 Las Vegas GP finishes",
]

SUB_LINE = "186 drones over Ukraine in the night \u00b7 Hong Kong votes \u00b7 India declare 720/9"
STATS_LINE = "55 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"

DATE_CHECK_TEXT = (
    "Every story on this page happened on Sunday 22 November 2026. Left "
    "out \u2014 other days' news: Peru quake (20 Nov) \u00b7 Myanmar ruling "
    "(19 Nov) \u00b7 Shenzhen (19 Nov) \u00b7 \u2018El Chapo Isidro\u2019 (20/21 Nov) \u00b7 "
    "Nvidia probe (20 Nov) \u00b7 Cyclone Akvan (20 Nov) \u00b7 Wall Street plunge "
    "(20 Nov) \u00b7 Basra fire (21 Nov) \u00b7 BepiColombo orbit entry (21 Nov) \u00b7 "
    "France protests (21 Nov) \u00b7 UN weapons talks (21 Nov) \u00b7 Helsing "
    "launch (11 Nov) \u00b7 Seattle ICE arrests (21 Nov)."
)

FOOTER_1 = (
    "Sources: Reuters, BBC, AP, AFP, The Guardian, ESPN, FIA, Vatican News, "
    "ATP, Times of Israel, Yonhap, Al Jazeera, ABC, NBC \u2014 reports of Sunday "
    "22 November 2026. Scenes are drawn, not photographs."
)
FOOTER_2 = (
    "CONFIRMED = reported by the named source \u00b7 REPORTED = one source's "
    "account \u00b7 CLAIM = one party's claim \u00b7 PENDING = not settled yet."
)

LEADS = [
    {
        "num": 1, "kicker": "186 DRONES OVERNIGHT",
        "place": "KYIV REGION, UKRAINE", "beat": "WAR", "tag": "REPORTED",
        "headline": "Russia fires 186 drones at Ukraine overnight; 161 downed",
        "deck": "161 of 186 drones downed or jammed; 72 jet-powered, 56 of them downed.",
        "source": "Ukrainian Air Force via Reuters, BBC", "art": "drones",
    },
    {
        "num": 2, "kicker": "HONG KONG VOTES",
        "place": "HONG KONG", "beat": "ELECTION", "tag": "CONFIRMED",
        "headline": "Hong Kong elects its Election Committee",
        "deck": "856 candidates contest 723 seats across 31 subsectors; polls open 09:00 and close 18:00 local time.",
        "source": "Hong Kong government", "art": "ballot_lead",
    },
    {
        "num": 3, "kicker": "720/9 IN WELLINGTON",
        "place": "WELLINGTON, NZ", "beat": "CRICKET", "tag": "CONFIRMED",
        "headline": "India declare on 720/9, a record in New Zealand",
        "deck": "Rahul 136, Pant 128 on day four of the Wellington Test; New Zealand 119/2, still trailing by 233.",
        "source": "ESPN, Cricbuzz", "art": "cricket_lead",
    },
]

NINE = [
    {"num": 4, "place": "MANAMA", "beat": "GULF", "tag": "CLAIM",
     "headline": "Iran claims strikes on US radars in Bahrain",
     "deck": "Tehran says it hit radars at Al-Riffa and Awali; two hurt.",
     "source": "The National, Reuters", "art": "radar"},
    {"num": 5, "place": "LAS VEGAS", "beat": "F1", "tag": "CONFIRMED",
     "headline": "Verstappen wins the Las Vegas GP",
     "deck": "Pole 1:34.151 was qualifying; Norris +0.639, Piastri +1.529.",
     "source": "FIA", "art": "f1"},
    {"num": 6, "place": "TEHRAN", "beat": "ENERGY", "tag": "REPORTED",
     "headline": "Iran begins rationing electricity",
     "deck": "Rolling cuts up to two hours a day as war damage bites.",
     "source": "Wires", "art": "power"},
    {"num": 7, "place": "BRAS\u00cdLIA", "beat": "HEALTH", "tag": "CONFIRMED",
     "headline": "Bolsonaro in intensive care in Bras\u00edlia",
     "deck": "Stable with acute bowel obstruction; admitted Friday.",
     "source": "Reuters", "art": "hospital"},
    {"num": 8, "place": "BRUSSELS", "beat": "TRAVEL", "tag": "CONFIRMED",
     "headline": "Belgium grounds 429 flights for Monday",
     "deck": "Controllers strike Monday; about 59,500 passengers affected.",
     "source": "Brussels Airport", "art": "tower"},
    {"num": 9, "place": "DELHI", "beat": "DIPLOMACY", "tag": "CONFIRMED",
     "headline": "Nepal PM Shah lands in India",
     "deck": "Balendra Shah arrives in New Delhi, meets minister Jaishankar.",
     "source": "Nepal Foreign Ministry", "art": "nepal"},
    {"num": 10, "place": "VATICAN CITY", "beat": "FAITH", "tag": "CONFIRMED",
     "headline": "Pope shares lunch with 1,300 poor",
     "deck": "Leo XIV hosts about 1,300 people in need in the Paul VI hall.",
     "source": "Vatican News", "art": "pope"},
    {"num": 11, "place": "TURIN", "beat": "TENNIS", "tag": "CONFIRMED",
     "headline": "Alcaraz wins his first ATP Finals",
     "deck": "Beats Zverev 6-2, 7-6(7) to take the title in Turin.",
     "source": "ATP", "art": "tennis"},
    {"num": 12, "place": "CANBERRA", "beat": "DEFENCE", "tag": "REPORTED",
     "headline": "Marles says US budget office got AUKUS wrong",
     "deck": "Australia's defence minister criticises the CBO assessment.",
     "source": "Reuters", "art": "mic"},
]

# (num, place, body, source, region)
BRIEFS = [
    (13, "Riyadh", "Saudi intercepts a Houthi drone aimed at Riyadh.", "Wires", "ME"),
    (14, "Seoul", "Education minister Choi quits in AI exam row.", "Yonhap", "APAC"),
    (15, "Turin", "Arribage/Olivetti win doubles final 3-6, 7-6(2), 10-6.", "ATP", "EU"),
    (16, "Jerusalem", "Eisenkot-Likud talks resume; invite Sat.", "Times of Israel", "ME"),
    (17, "Liverpool", "4-0 Man Utd at Anfield, ref Barrott.", "FBref", "EU"),
    (18, "Barcelona", "3-2 Villarreal, 59,034; goals 5', 7', 57', 61', 67'.", "FBref", "EU"),
    (19, "Hull", "2-0 Brighton, McBurnie 2 late goals; 24,461, ref Bankes.", "FBref", "EU"),
    (20, "Bergamo", "Atalanta 4-4 Inter; Esposito hat-trick.", "Wires", "EU"),
    (21, "Milan", "AC Milan 5-1 Frosinone.", "Wires", "EU"),
    (22, "Turin", "Juventus 4-0 Venezia.", "Wires", "EU"),
    (23, "Dallas", "51-30 Titans; Prescott 325 yds, 4 pass TDs, 1 rush.", "Reuters", "AM"),
    (24, "Detroit", "Lions 31-21 Buccaneers; Gibbs 2 TD.", "Reuters", "AM"),
    (25, "Kansas City", "Chiefs 34-7 Cardinals.", "Reuters", "AM"),
    (26, "San Francisco", "49ers 35-10 Vikings; Purdy 3 TD, 49ers 9-1.", "Reuters", "AM"),
    (27, "New York", "Knicks 113-106 Pacers; Hart 10/11/10.", "Reuters", "AM"),
    (28, "Denver", "Nuggets 151-145 Bulls OT; Murray 45, Jokic 37.", "Reuters", "AM"),
    (29, "Miami", "123-113 Thunder; Adebayo 24/15/12.", "Reuters", "AM"),
    (30, "Boston", "Warriors 88-87 Celtics.", "Reuters", "AM"),
    (31, "Vandenberg", "Falcon 9 lifts NROL-136 at 12:23 UTC.", "SpaceX", "AM"),
    (32, "Accra", "Ghana 1-0 Morocco win Amputee World Cup.", "Wires", "AF"),
    (33, "Antalya", "COP31 ends with no deal; fossil fuels dropped.", "Reuters", "EU"),
    (34, "Benghazi", "Russian warship Merkury sinks; Kyiv blamed, 10 hurt.", "Wires", "AF"),
    (35, "Khartoum", "Drones kill 4, wound 9; army blames Ethiopia.", "Wires", "AF"),
    (36, "Nairobi", "Internet-metering bill sparks privacy fears.", "Al Jazeera", "AF"),
    (37, "North Carolina", "Democrats take 258 seats; Hubbard beats Foxx.", "AP", "AM"),
    (38, "Virginia", "Trump hosts third $TRUMP gala; token below $1.", "Reuters", "AM"),
    (39, "West Bank", "Eisenkot calls settler attacks 'Jewish terrorism'.", "Reuters", "ME"),
    (40, "Washington", "Intel chief Clayton: Putin 'no friend of America'.", "ABC", "AM"),
    (41, "Washington", "Kennedy presses Lutnick on Nvidia chips.", "NBC", "AM"),
    (42, "Pennsylvania", "Measles kills 12 in Amish communities.", "Guardian", "AM"),
    (43, "Dymer", "Drone hits a block; 3 dead, ~10 trapped.", "Reuters", "EU"),
    (44, "Gulf", "Trump to Iran: test it, end 'at the bottom of the sea'.", "Fox News", "ME"),
    (45, "Istanbul", "Thousands march in Besiktas over Sozcu takeover.", "AFP", "EU"),
    (46, "London", "May tells PM Burnham: 'accept Brexit and move on'.", "BBC", "EU"),
    (47, "Naha", "Shuri Castle restored; Seiden reopens Monday.", "Japan Times", "APAC"),
    (48, "Gaza", "Israeli fire kills 2 in Jabalia, Deir al-Balah.", "Wafa", "ME"),
    (49, "Gazipur", "Garment workers block highway; police fire tear gas.", "TBS", "APAC"),
    (50, "Taipei", "We Are Born Good wins Best Narrative Feature.", "CNA", "APAC"),
    (51, "Los Angeles", "Ateez top Billboard 200 a 4th time.", "Billboard", "AM"),
    (52, "Naples", "Thitikul wins CME Group title 3rd straight year; $4M.", "LPGA", "AM"),
    (53, "New York", "Skubal agrees to record $450M Mets deal.", "MLB.com", "AM"),
    (54, "Portimao", "Marquez clinches 8th title, tying Agostini.", "MotoGP", "EU"),
    (55, "Wolverhampton", "Price beats Van Veen 16-11, 4th Slam.", "Sky Sports", "EU"),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-60, 55), (-55, 47), (-60, 45),
     (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29),
     (-97, 26), (-105, 22), (-110, 24), (-115, 29), (-120, 34), (-125, 40),
     (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-165, 60), (-168, 66)],
    [(-58, 64), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
     (-30, 76), (-45, 76), (-55, 74), (-58, 70), (-58, 64)],
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-68, -50),
     (-70, -55), (-73, -50), (-73, -40), (-72, -30), (-70, -20), (-77, -12),
     (-81, -6), (-79, 9)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (43, 11), (48, 11), (51, 10), (44, 0), (40, -10), (35, -18),
     (32, -26), (28, -33), (20, -35), (15, -27), (12, -18), (9, -1), (9, 4),
     (-8, 4), (-13, 8), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (40, 68), (50, 69),
     (60, 69), (70, 72), (80, 73), (90, 75), (100, 76), (110, 74), (120, 73),
     (130, 72), (140, 72), (150, 70), (160, 69), (170, 66), (178, 65),
     (170, 60), (162, 56), (158, 52), (150, 59), (142, 55), (140, 45),
     (135, 43), (130, 42), (127, 40), (122, 38), (120, 32), (115, 23),
     (108, 18), (105, 10), (100, 8), (98, 12), (95, 16), (92, 21), (88, 22),
     (85, 19), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (62, 25),
     (58, 26), (55, 26), (52, 28), (50, 29), (48, 30), (44, 29), (40, 31),
     (36, 36), (30, 36), (27, 40), (23, 40), (19, 42), (15, 44), (12, 44),
     (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37), (-10, 36)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51), (-5, 50)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 41), (143, 43),
     (141, 45), (139, 40), (136, 37), (132, 33), (130, 31)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -8), (130, -3), (135, -4), (140, -8), (138, -2), (132, 0),
     (128, 2), (122, 1), (118, 0), (112, -2), (105, -3), (100, 0), (95, 5)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
     (113, -22)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (171, -44), (167, -45)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25), (43, -22), (44, -16)],
]

# (num, lon, lat, nudge_x, nudge_y)
DOTS = [
    (1, 33, 49.5, 25, -10), (2, 114.2, 22.3, -1, -6), (3, 174.8, -41.3, -2, 2),
    (4, 50.6, 26.2, 23, 19), (5, -115.1, 36.2, -11, 4), (6, 51.4, 35.7, 24, -15),
    (7, -47.9, -15.8, 2, 15), (8, 4.35, 50.85, 22, 6), (9, 77.2, 28.6, 20, -21),
    (10, 12.45, 41.9, -2, 0), (11, 7.7, 45.1, -7, 29), (12, 149.1, -35.3, 0, -3),
    (13, 46.7, 24.6, 9, 28), (14, 127.0, 37.5, 8, 0), (15, 7.7, 45.1, 8, 16),
    (16, 35.2, 31.8, 2, 29), (17, -2.99, 53.43, -7, -8), (18, 2.19, 41.38, -27, 5),
    (19, -0.34, 53.74, -28, -8), (20, 9.67, 45.70, 26, -12), (21, 9.19, 45.46, -7, 15),
    (22, 7.69, 45.07, 0, -12), (23, -96.8, 32.78, -10, -1), (24, -83.05, 42.33, 25, 1),
    (25, -94.58, 39.1, -18, 24), (26, -121.97, 37.35, -21, 6),
    (27, -74.0, 40.71, -4, -15), (28, -104.99, 39.74, -14, -15),
    (29, -80.19, 25.76, 1, 26), (30, -71.06, 42.36, 1, -2),
    (31, -120.62, 34.74, -19, -18), (32, -0.19, 5.6, -13, 26),
    (33, 30.7, 36.9, 15, -5), (34, 20.1, 32.1, 23, 6), (35, 32.5, 15.6, 20, 9),
    (36, 36.8, -1.3, -18, 22), (37, -78.6, 35.8, 21, -16), (38, -77.5, 37.5, -18, -16),
    (39, 35.2, 32.0, 29, 0), (40, -77.0, 38.9, 3, 11), (41, -77.0, 38.9, 18, 23),
    (42, -76.9, 40.3, -15, 18), (43, 30.78, 50.78, -7, -10), (44, 50.3, 29.2, 29, 4),
    (45, 28.98, 41.01, 3, 20), (46, -0.12, 51.51, -13, 26),
    (47, 127.68, 26.21, -4, -22), (48, 34.45, 31.50, -15, 25),
    (49, 90.43, 24.00, 9, 11), (50, 121.56, 25.03, 2, 13),
    (51, -118.24, 34.05, -18, 22), (52, -81.80, 26.14, -7, -3),
    (53, -74.0, 40.71, 23, 12), (54, -8.54, 37.14, -22, 20), (55, -2.12, 52.59, -10, 5),
]

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONT_CACHE = {}


def _font(size, kind):
    key = (size, kind)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    from PIL import ImageFont
    names = {
        "serif_bold": "DejaVuSerif-Bold.ttf",
        "serif": "DejaVuSerif.ttf",
        "serif_italic": "DejaVuSerif-Italic.ttf",
        "sans": "DejaVuSans.ttf",
        "sans_bold": "DejaVuSans-Bold.ttf",
    }
    try:
        f = ImageFont.truetype(os.path.join(FONT_DIR, names[kind]), int(round(size)))
    except Exception:
        f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def _wrap(text, font, width):
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if font.getlength(trial) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def _fit_lines(text, font, width, max_lines):
    lines = _wrap(text, font, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and font.getlength(last + " ...") > width:
        if " " in last:
            last = last.rsplit(" ", 1)[0]
        else:
            last = last[:-1]
    lines[-1] = last + " ..."
    return lines


def _trunc_one(text, font, width):
    if font.getlength(text) <= width:
        return text
    words = text.split()
    out = ""
    for word in words:
        trial = (out + " " + word).strip()
        if font.getlength(trial + " ...") <= width:
            out = trial
        else:
            break
    return out + " ..." if out else text[:4] + " ..."


def _chip_width(label, size=8):
    return int(_font(size, "sans_bold").getlength(label)) + 10


def _chip(draw, x, y, label, colour, height=13, size=8):
    font = _font(size, "sans_bold")
    w = int(font.getlength(label)) + 10
    draw.rounded_rectangle([x, y, x + w, y + height], radius=6, fill=colour)
    draw.text((x + w / 2, y + height / 2), label, font=font, fill=WHITE, anchor="mm")
    return w


# ---------------------------------------------------------------- illustrations

def _drone(d, cx, cy, gold):
    d.rectangle([cx - 4, cy - 1, cx + 4, cy + 2], fill=gold)
    d.line([cx - 7, cy - 3, cx - 4, cy - 1], fill=gold, width=1)
    d.line([cx + 4, cy - 1, cx + 7, cy - 3], fill=gold, width=1)
    d.line([cx - 7, cy + 4, cx - 4, cy + 2], fill=gold, width=1)
    d.line([cx + 4, cy + 2, cx + 7, cy + 4], fill=gold, width=1)
    for px, py in ((cx - 8, cy - 4), (cx + 8, cy - 4), (cx - 8, cy + 5), (cx + 8, cy + 5)):
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=gold)


def _draw_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DARK)
    for sx, sy, r in ((0.08, 0.15, 1), (0.2, 0.08, 1), (0.35, 0.2, 1), (0.55, 0.1, 1),
                      (0.7, 0.22, 1), (0.85, 0.08, 1), (0.45, 0.3, 1), (0.15, 0.35, 1)):
        d.ellipse([x + w * sx - r, y + h * sy - r, x + w * sx + r, y + h * sy + r], fill=WHITE)
    d.ellipse([x + w - 34, y + 8, x + w - 16, y + 26], fill=(240, 235, 210))
    d.polygon([(x + 78, y + h), (x + 168, y + 6), (x + 176, y + 6), (x + 96, y + h)],
              fill=(214, 220, 232))
    d.rectangle([x, y + h - 26, x + int(w * 0.38), y + h], fill=(10, 16, 32))
    for r in range(2):
        for c in range(5):
            wx = x + 8 + c * 20
            wy = y + h - 21 + r * 10
            d.rectangle([wx, wy, wx + 7, wy + 5], fill=(250, 210, 90))
    gold = (212, 175, 60)
    for cx, cy in ((0.45, 0.3), (0.58, 0.18), (0.68, 0.38), (0.82, 0.28)):
        _drone(d, x + int(w * cx), y + int(h * cy), gold)
    bx, by = x + int(w * 0.62), y + int(h * 0.62)
    for dx, dy in ((-9, -9), (9, -9), (-9, 9), (9, 9), (-12, 0), (12, 0), (0, -12), (0, 12)):
        d.line([bx, by, bx + dx, by + dy], fill=RED, width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)


def _draw_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 235))
    heights = [0.42, 0.62, 0.5, 0.72, 0.55, 0.68, 0.46, 0.6, 0.52, 0.7, 0.44]
    bw = w / len(heights)
    for i, frac in enumerate(heights):
        bx0 = x + i * bw
        top = y + h - int(h * frac)
        d.rectangle([bx0, top, bx0 + bw - 2, y + h], fill=NAVY)
        for wy in range(int(top) + 6, y + h - 6, 12):
            d.rectangle([bx0 + 3, wy, bx0 + 7, wy + 4], fill=(250, 210, 90))
    cx = x + w // 2
    d.rectangle([cx - 30, y + 40, cx + 30, y + h - 6], fill=RED)
    d.rectangle([cx - 30, y + 40, cx + 30, y + 46], fill=(140, 20, 26))
    d.rectangle([cx - 14, y + 16, cx + 14, y + 40], fill=WHITE)
    d.rectangle([cx - 14, y + 16, cx + 14, y + 40], outline=GREY, width=1)
    d.line([cx - 9, y + 28, cx - 2, y + 35, cx + 10, y + 21], fill=(34, 120, 60), width=3)


def _draw_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 168, 96))
    d.rectangle([x, y + int(h * 0.34), x + w, y + int(h * 0.66)], fill=(232, 214, 176))
    d.line([x, y + h // 2, x + w, y + h // 2], fill=WHITE, width=2)
    bx, by = x + int(w * 0.42), y + int(h * 0.5)
    d.polygon([(bx - 5, by - 16), (bx + 5, by - 16), (bx + 9, by + 10), (bx - 1, by + 10)],
              fill=(190, 150, 100))
    d.rectangle([bx - 2, by - 26, bx + 2, by - 16], fill=(150, 110, 70))
    d.ellipse([x + int(w * 0.72) - 6, y + int(h * 0.42) - 6,
               x + int(w * 0.72) + 6, y + int(h * 0.42) + 6], fill=RED)
    sx = x + int(w * 0.86)
    for i in range(3):
        d.line([sx + i * 6, y + int(h * 0.2), sx + i * 6, y + int(h * 0.34)],
               fill=(240, 210, 90), width=3)

LEAD_ART = {"drones": _draw_drones, "ballot_lead": _draw_ballot, "cricket_lead": _draw_cricket}


def _pic_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 54))
    d.line([x + 16, y + h, x + 16, y + 8], fill=(180, 180, 180), width=2)
    d.arc([x + 6, y + 2, x + 26, y + 16], 200, 340, fill=(220, 220, 220), width=2)
    d.arc([x + 34, y + 4, x + 66, y + 24], 300, 60, fill=(212, 175, 60), width=2)
    d.rectangle([x + w - 46, y + 12, x + w - 14, y + h], fill=(60, 60, 66))
    d.polygon([(x + w - 30, y + 2), (x + w - 24, y + 12), (x + w - 36, y + 12)], fill=(230, 120, 40))
    d.polygon([(x + w - 30, y + 6), (x + w - 27, y + 12), (x + w - 33, y + 12)], fill=(250, 210, 90))


def _pic_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 34))
    d.arc([x + 8, y - 6, x + w - 8, y + h + 14], 20, 160, fill=(212, 175, 60), width=2)
    fx, fy = x + w - 26, y + 2
    for r in range(2):
        for c in range(3):
            col = WHITE if (r + c) % 2 == 0 else (20, 20, 22)
            d.rectangle([fx + c * 6, fy + r * 6, fx + c * 6 + 6, fy + r * 6 + 6], fill=col)
    d.line([fx, fy + 12, fx - 4, y + h], fill=(160, 160, 160), width=1)
    d.polygon([(x + 24, y + h - 6), (x + 66, y + h - 6), (x + 58, y + h - 14), (x + 34, y + h - 14)],
              fill=(200, 30, 36))
    for wx in (x + 34, x + 56):
        d.ellipse([wx - 4, y + h - 8, wx + 4, y + h], fill=(10, 10, 10))


def _pic_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    d.rectangle([x + 6, y + 8, x + 34, y + h], fill=NAVY)
    d.rectangle([x + 40, y + 14, x + 62, y + h], fill=(40, 52, 84))
    for wx, wy in ((x + 10, y + 12), (x + 20, y + 12), (x + 10, y + 20), (x + 44, y + 18), (x + 52, y + 18)):
        d.rectangle([wx, wy, wx + 4, wy + 3], fill=(250, 210, 90))
    d.polygon([(x + w - 22, y + 2), (x + w - 30, y + 14), (x + w - 22, y + 14),
               (x + w - 28, y + 24), (x + w - 14, y + 10), (x + w - 20, y + 10)],
              fill=(212, 175, 60))


def _pic_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 238, 230))
    d.rectangle([x + 8, y + 6, x + 52, y + h], fill=WHITE, outline=GREY)
    d.rectangle([x + 26, y + 9, x + 34, y + 21], fill=RED)
    d.rectangle([x + 22, y + 13, x + 38, y + 17], fill=RED)
    d.line([x + 58, y + 20, x + 68, y + 20, x + 74, y + 12, x + 80, y + 22, x + 88, y + 16,
            x + 96, y + 20, x + w - 6, y + 20], fill=RED, width=2)


def _pic_tower(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    d.rectangle([x + 14, y + 8, x + 30, y + h], fill=(120, 120, 126))
    d.rectangle([x + 10, y + 4, x + 34, y + 10], fill=(90, 90, 96))
    d.polygon([(x + 52, y + h - 4), (x + 96, y + h - 4), (x + 90, y + h - 10), (x + 60, y + h - 10)],
              fill=(200, 200, 200))
    d.polygon([(x + 96, y + h - 8), (x + 112, y + h - 12), (x + 112, y + h - 6)], fill=(160, 160, 160))
    d.line([x + 52, y + h - 10, x + 52, y + h - 16], fill=(120, 120, 126), width=2)


def _pic_nepal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 234, 240))
    for tx, tw, th in ((x + 4, 46, 22), (x + 44, 56, 24), (x + 92, 48, 20)):
        d.polygon([(tx, y + h), (tx + tw / 2, y + h - th), (tx + tw, y + h)], fill=(120, 84, 60))
        d.polygon([(tx + tw / 2 - 7, y + h - th + 7), (tx + tw / 2, y + h - th),
                   (tx + tw / 2 + 7, y + h - th + 7)], fill=WHITE)
    d.polygon([(x + 120, y + 6), (x + 150, y + 6), (x + 158, y + 9), (x + 150, y + 12),
               (x + 122, y + 12)], fill=WHITE)
    d.line([x + 150, y + 9, x + 158, y + 4], fill=WHITE, width=2)


def _pic_pope(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 180))
    for i, skin in enumerate(((222, 184, 150), (190, 140, 100), (232, 200, 170), (200, 160, 120))):
        cx = x + 16 + i * 26
        d.ellipse([cx - 6, y + 2, cx + 6, y + 14], fill=skin)
        d.ellipse([cx - 6, y + 2, cx + 6, y + 8], fill=(60, 50, 44) if i % 2 == 0 else (200, 200, 200))
    d.rectangle([x + 6, y + 16, x + w - 6, y + h], fill=(140, 96, 60))
    for i in range(4):
        cx = x + 16 + i * 26
        d.ellipse([cx - 7, y + 19, cx + 7, y + 24], fill=WHITE)


def _pic_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 160, 90))
    d.rectangle([x + 30, y + 3, x + w - 30, y + h - 3], fill=(60, 110, 190))
    d.rectangle([x + 30, y + 3, x + w - 30, y + h - 3], outline=WHITE, width=1)
    d.line([x + w // 2, y + 3, x + w // 2, y + h - 3], fill=WHITE, width=1)
    d.ellipse([x + w - 22, y + 6, x + w - 14, y + 14], fill=(200, 220, 60))
    d.ellipse([x + 6, y + 14, x + 16, y + 24], outline=(90, 60, 30), width=2)
    d.line([x + 16, y + 24, x + 24, y + h - 1], fill=(90, 60, 30), width=2)


def _pic_mic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
    for cx in (x + 12, x + 30):
        d.rectangle([cx, y + 6, cx + 10, y + h], fill=(150, 146, 136))
        d.rectangle([cx - 2, y + 4, cx + 12, y + 7], fill=(120, 116, 106))
    d.ellipse([x + 58, y + 2, x + 74, y + 16], fill=(50, 50, 54))
    for dx, dy in ((62, 6), (66, 6), (70, 6), (62, 10), (66, 10), (70, 10)):
        d.point((dx, dy), fill=(180, 180, 180))
    d.line([x + 66, y + 16, x + 66, y + h], fill=(50, 50, 54), width=2)
    d.line([x + 58, y + h, x + 74, y + h], fill=(50, 50, 54), width=2)
    for r in (8, 13):
        d.arc([x + 84, y + 13 - r, x + 84 + 2 * r, y + 13 + r], -60, 60, fill=RED, width=2)


PIC_ART = {
    "radar": _pic_radar, "f1": _pic_f1, "power": _pic_power,
    "hospital": _pic_hospital, "tower": _pic_tower, "nepal": _pic_nepal,
    "pope": _pic_pope, "tennis": _pic_tennis, "mic": _pic_mic,
}


# ---------------------------------------------------------------- page build

def build_page():
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Top bar
    d.rectangle([0, 0, W, 20], fill=NAVY)
    bar_font = _font(10, "sans_bold")
    d.text((M, 10), "THE WORLD IN ONE DAY", font=bar_font, fill=CREAM, anchor="lm")
    d.text((RIGHT, 10), "ONE PAGE \u00b7 ALL THE NEWS", font=bar_font, fill=CREAM, anchor="rm")

    # Masthead title: largest size at/below 60 that fits
    title = "Sunday 22 November 2026"
    size = 60
    while size > 30 and _font(size, "serif_bold").getlength(title) > CW:
        size -= 1
    d.text((W // 2, 24), title, font=_font(size, "serif_bold"), fill=NAVY, anchor="ma")
    d.text((W // 2, 86), SUB_LINE, font=_font(15, "serif_italic"), fill=RED, anchor="ma")
    d.text((W // 2, 103), STATS_LINE, font=_font(12, "sans_bold"), fill=NAVY, anchor="ma")
    d.rectangle([M, 118, RIGHT, 120], fill=NAVY)

    # Numbers strip y 124-164
    box_w = (CW - 18) // 4
    for i, (value, label) in enumerate(NUMBERS):
        bx = M + i * (box_w + 6)
        bw = box_w if i < 3 else CW - 3 * (box_w + 6)
        d.rectangle([bx, 124, bx + bw, 164], fill=PAPER_DARK, outline=RULE, width=1)
        d.text((bx + bw // 2, 130), value, font=_font(20, "sans_bold"), fill=RED, anchor="ma")
        d.text((bx + bw // 2, 150), label, font=_font(9, "sans"), fill=GREY, anchor="ma")

    # Region strip y 174-192
    seg_w = CW // 6
    for i, (name, count) in enumerate(REGIONS):
        sx = M + i * seg_w
        sw = seg_w if i < 5 else CW - 5 * seg_w
        d.rectangle([sx, 174, sx + sw, 192], fill=REGION_COLOURS[name])
        d.text((sx + sw // 2, 183), "%s %d" % (name, count), font=_font(11, "sans_bold"),
               fill=WHITE, anchor="mm")

    # UTC strip y 198-214
    d.rectangle([M, 198, M + 108, 214], fill=NAVY)
    d.text((M + 54, 206), "THE DAY IN UTC", font=_font(10, "sans_bold"), fill=WHITE, anchor="mm")
    utc_line = "  \u00b7  ".join(UTC_EVENTS)
    d.text((M + 116, 206), utc_line, font=_font(10, "sans"), fill=INK, anchor="lm")

    # Leads y 222
    lead_w = (CW - 20) // 3
    for i, lead in enumerate(LEADS):
        lx = M + i * (lead_w + 10)
        LEAD_ART[lead["art"]](d, lx, 222, lead_w, 88)
        d.rectangle([lx, 222, lx + lead_w, 310], outline=NAVY, width=1)
        kfont = _font(9, "sans_bold")
        kw = int(kfont.getlength(lead["kicker"])) + 10
        d.rectangle([lx, 222, lx + kw, 236], fill=RED)
        d.text((lx + 5, 229), lead["kicker"], font=kfont, fill=WHITE, anchor="lm")
        y = 316
        d.text((lx, y), str(lead["num"]), font=_font(11, "sans_bold"), fill=RED, anchor="la")
        chip_w = _chip_width(lead["tag"])
        _chip(d, lx + lead_w - chip_w, y, lead["tag"], TAG_COLOURS[lead["tag"]])
        place = "%s \u00b7 %s" % (lead["place"], lead["beat"])
        place_w = lead_w - 20 - chip_w - 8
        place = _trunc_one(place, _font(10, "sans_bold"), place_w)
        d.text((lx + 16, y), place, font=_font(10, "sans_bold"), fill=NAVY, anchor="la")
        y += 16
        head_lines = _fit_lines(lead["headline"], _font(16, "serif_bold"), lead_w, 2)
        for line in head_lines:
            d.text((lx, y), line, font=_font(16, "serif_bold"), fill=INK, anchor="la")
            y += 19
        deck_lines = _fit_lines(lead["deck"], _font(11, "sans"), lead_w, 3)
        for line in deck_lines:
            d.text((lx, y), line, font=_font(11, "sans"), fill=INK, anchor="la")
            y += 13
        y += 3
        d.text((lx, y), "Sources: " + lead["source"], font=_font(9, "sans"), fill=GREY, anchor="la")

    # THE DAY IN NINE
    d.text((M, 422), "THE DAY IN NINE", font=_font(15, "serif_bold"), fill=NAVY, anchor="la")
    d.text((RIGHT, 422), "THE STORIES THAT MOVED THE WORLD TODAY",
           font=_font(10, "sans_bold"), fill=GREY, anchor="ra")
    d.rectangle([M, 442, RIGHT, 444], fill=GOLD)

    def draw_card(card, cx, cy, cw):
        d.rectangle([cx, cy, cx + cw, cy + 112], fill=WHITE, outline=RULE, width=1)
        PIC_ART[card["art"]](d, cx + 1, cy + 1, cw - 2, 26)
        d.line([cx, cy + 27, cx + cw, cy + 27], fill=RULE, width=1)
        d.ellipse([cx + 4, cy + 4, cx + 22, cy + 22], fill=NAVY)
        d.text((cx + 13, cy + 13), str(card["num"]), font=_font(11, "sans_bold"),
               fill=WHITE, anchor="mm")
        py = cy + 32
        chip_w = _chip_width(card["tag"])
        _chip(d, cx + cw - 6 - chip_w, py, card["tag"], TAG_COLOURS[card["tag"]])
        place = "%s \u00b7 %s" % (card["place"], card["beat"])
        place = _trunc_one(place, _font(9, "sans_bold"), cw - 12 - chip_w - 4)
        d.text((cx + 6, py), place, font=_font(9, "sans_bold"), fill=NAVY, anchor="la")
        hy = cy + 46
        head_lines = _fit_lines(card["headline"], _font(12, "sans_bold"), cw - 12, 2)
        for line in head_lines:
            d.text((cx + 6, hy), line, font=_font(12, "sans_bold"), fill=INK, anchor="la")
            hy += 13
        dy = cy + 74
        deck_lines = _fit_lines(card["deck"], _font(10, "sans"), cw - 12, 2)
        for line in deck_lines:
            d.text((cx + 6, dy), line, font=_font(10, "sans"), fill=GREY, anchor="la")
            dy += 11
        d.text((cx + 6, cy + 99), card["source"], font=_font(8, "sans"), fill=GREY, anchor="la")

    for i, card in enumerate(NINE[:5]):
        draw_card(card, M + i * (188 + 8), 446, 188)
    row1_w = (CW - 24) // 4
    for i, card in enumerate(NINE[5:]):
        draw_card(card, M + i * (row1_w + 8), 566, row1_w)

    # WHERE IT HAPPENED / DATE CHECK
    d.text((M, 684), "WHERE IT HAPPENED", font=_font(13, "serif_bold"), fill=NAVY, anchor="la")
    dc_x = M + 338
    d.text((dc_x, 684), "DATE CHECK", font=_font(13, "serif_bold"), fill=NAVY, anchor="la")
    mx, my, mw, mh = M, 698, 330, 72
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_SKY, outline=RULE, width=1)

    def to_xy(lon, lat):
        return (mx + (lon + 180) / 360.0 * mw, my + (84 - lat) / 144.0 * mh)

    for poly in CONTINENTS:
        pts = [to_xy(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND)
        d.line(pts + [pts[0]], fill=MAP_LINE, width=1)
    for num, lon, lat, nx, ny in DOTS:
        px, py = to_xy(lon, lat)
        px += nx
        py += ny
        r = 5 if num >= 10 else 4
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=NAVY, width=1)
        d.text((px, py), str(num), font=_font(8 if num >= 10 else 7, "sans_bold"),
               fill=WHITE, anchor="mm")

    d.rectangle([dc_x, my, dc_x + 638, my + 72], fill=RED_TINT, outline=RED, width=1)
    d.rectangle([dc_x, my, dc_x + 92, my + 72], fill=RED)
    d.text((dc_x + 46, my + 28), "DATE", font=_font(11, "sans_bold"), fill=WHITE, anchor="mm")
    d.text((dc_x + 46, my + 44), "CHECK", font=_font(11, "sans_bold"), fill=WHITE, anchor="mm")
    dc_lines = _fit_lines(DATE_CHECK_TEXT, _font(10, "sans"), 638 - 92 - 18, 5)
    dy = my + 4
    for line in dc_lines:
        d.text((dc_x + 102, dy), line, font=_font(10, "sans"), fill=INK, anchor="la")
        dy += 13

    # ALSO ON SUNDAY
    d.text((M, 776), "ALSO ON SUNDAY 22 NOVEMBER \u2014 43 MORE STORIES",
           font=_font(13, "serif_bold"), fill=NAVY, anchor="la")

    def draw_brief(brief, bx, by, bw):
        num, place, body, source, _region = brief
        num_text = "%d." % num
        nfont = _font(9, "sans_bold")
        d.text((bx, by), num_text, font=nfont, fill=RED, anchor="la")
        tx = bx + int(nfont.getlength(num_text)) + 4
        text = "%s: %s (%s)" % (place, body, source)
        lines = _fit_lines(text, _font(9, "sans"), bx + bw - tx, 2)
        ly = by
        for line in lines:
            d.text((tx, ly), line, font=_font(9, "sans"), fill=INK, anchor="la")
            ly += 10

    col_w = (CW - 32) // 5
    for i, brief in enumerate(BRIEFS[:40]):
        row, col = divmod(i, 5)
        draw_brief(brief, M + col * (col_w + 8), 792 + row * 22, col_w)
    wide_w = (CW - 16) // 3
    for i, brief in enumerate(BRIEFS[40:]):
        draw_brief(brief, M + i * (wide_w + 8), 792 + 8 * 22, wide_w)

    # Footer
    d.text((M, 994), FOOTER_1, font=_font(9, "sans"), fill=GREY, anchor="la")
    d.text((M, 1005), FOOTER_2, font=_font(9, "sans"), fill=GREY, anchor="la")

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(BASE, "out")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        shutil.copyfile(os.path.join(BASE, "assets", "prebuilt.png"), out_path)
        return
    img = build_page()
    img.save(out_path, "PNG", optimize=True)


if __name__ == "__main__":
    main()
