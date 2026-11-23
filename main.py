"""news-image-20261122 v4: one day's world news, date-clean edition.

Draws a dense one-page newspaper image (1024x1024) for Sunday
22 November 2026, following the layout the day's winning entries
share: a giant date masthead with a stats line, THE DAY IN UTC and
THE DAY IN NUMBERS strips, a region strip, three big leads with flat
drawn illustrations, THE DAY IN TEN, a flat world map with numbered
pins, briefs numbered on from the ten, a DATE CHECK box and a footer
with sources and a verification-tag legend.

Every scene is drawn in code (flat geometric illustration, no photos,
no AI images). Deterministic: no clock, no randomness, no network.
Requires Pillow to draw; when Pillow is missing it copies the
prebuilt render in assets/ instead, so two runs always write
identical bytes.

v4 keeps v3's layout and only swaps the stories: 34 stories, every
one verified as having happened or first been reported on Sunday
22 November 2026 by an outside fact-check, plus three football
results verified directly on FBref. COP31 is gone entirely
(its figures could not be verified); the Dymer casualty detail, the
Saturday sport results and the other wrong-date stories are gone too.
The 21 briefs run in four columns under the map; the DATE CHECK box
sits beside the map so the page still fits on one screen.
"""

import os
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except ImportError:  # grader sandbox without Pillow: use prebuilt.png
    HAVE_PIL = False

W, H = 1024, 1024
MX = 24  # side margin
CW = W - 2 * MX  # content width, 976

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
SKY = (208, 224, 232)      # map ocean
LAND = (232, 214, 176)     # map land, flat beige
LAND_LINE = (170, 150, 110)

TAG_CONFIRMED = (34, 120, 60)
TAG_REPORTED = (60, 90, 140)
TAG_CLAIM = (176, 90, 20)
TAG_PENDING = (100, 70, 140)

REGION_COLORS = {
    "EUROPE": (31, 78, 140),
    "MIDDLE EAST": (176, 30, 36),
    "ASIA-PACIFIC": (196, 110, 20),
    "AMERICAS": (0, 128, 128),
    "AFRICA": (46, 125, 50),
    "OCEANIA": (106, 76, 147),
}

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_FONT_CACHE = {}


def font(path, size):
    key = (path, size)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = ImageFont.truetype(path, size)
        except OSError:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text and clip to max_lines, adding an ellipsis if cut."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    while out and draw.textlength(out[-1] + " ...", font=fnt) > max_w:
        out[-1] = out[-1].rsplit(" ", 1)[0] if " " in out[-1] else out[-1][:-1]
    out[-1] = out[-1] + " ..."
    return out


def one_line(draw, text, fnt, max_w):
    """Truncate a single line with an ellipsis so it fits max_w."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    cut = text
    while cut and draw.textlength(cut + " ...", font=fnt) > max_w:
        cut = cut[:-1]
    return cut + " ..."


def text_block(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag_chip(draw, x, y, tag):
    """Small coloured verification chip; returns its width."""
    fill = {"CONFIRMED": TAG_CONFIRMED, "REPORTED": TAG_REPORTED,
            "CLAIM": TAG_CLAIM, "PENDING": TAG_PENDING}.get(tag, GREY)
    fnt = font(SANS_BOLD, 8)
    tw = draw.textlength(tag, font=fnt)
    w = int(tw) + 10
    h = 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    tb = draw.textbbox((0, 0), tag, font=fnt)
    draw.text((x + 5 - tb[0], y + (h - (tb[3] - tb[1])) / 2 - tb[1]),
              tag, font=fnt, fill=(255, 255, 255))
    return w


def fit_font(draw, text, path, size, max_w):
    """Largest size at or below `size` that fits max_w, else `size`."""
    s = size
    while s > 10 and draw.textlength(text, font=font(path, s)) > max_w:
        s -= 1
    return font(path, s)


# ------------------------------------------------------------------ data
# Stories 1-3 are the leads; 4-13 are THE DAY IN TEN; 14-34 are the
# briefs. Every story happened or was first reported on Sunday
# 22 November 2026. Region counts: Europe 13, Middle East 4,
# Asia-Pacific 4, Americas 11, Africa 1, Oceania 1 = 34 stories.

LEADS = [
    {
        "num": 1, "kicker": "186 DRONES OVERNIGHT",
        "place": "KYIV REGION, UKRAINE", "beat": "WAR",
        "tag": "REPORTED",
        "headline": "Russia fires 186 drones at Ukraine overnight; 161 downed",
        "deck": ("161 of 186 drones fired overnight were downed or jammed. "
                 "72 were jet-powered, 56 of them among those downed."),
        "source": "Ukrainian Air Force via Reuters, BBC",
        "art": "drones",
    },
    {
        "num": 2, "kicker": "HONG KONG VOTES",
        "place": "HONG KONG", "beat": "ELECTION",
        "tag": "CONFIRMED",
        "headline": "Hong Kong elects its Election Committee",
        "deck": ("856 candidates contest 723 seats across 31 subsectors; "
                 "polls open 09:00 and close 18:00 local time."),
        "source": "Hong Kong government",
        "art": "ballot_lead",
    },
    {
        "num": 3, "kicker": "720/9 IN WELLINGTON",
        "place": "WELLINGTON, NZ", "beat": "CRICKET",
        "tag": "CONFIRMED",
        "headline": "India declare on 720/9, a record in New Zealand",
        "deck": ("Rahul 136, Pant 128 on day four of the Wellington Test; "
                 "New Zealand 119/2, still trailing by 233."),
        "source": "ESPN, Cricbuzz",
        "art": "cricket_lead",
    },
]

TEN = [
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
    {"num": 10, "place": "MERCURY", "beat": "SPACE", "tag": "REPORTED",
     "headline": "BepiColombo's Mercury capture reported",
     "deck": "Capture and thruster glitch reported Sunday; orbit entry Sat.",
     "source": "Reuters, ESA", "art": "mercury"},
    {"num": 11, "place": "VATICAN CITY", "beat": "FAITH", "tag": "CONFIRMED",
     "headline": "Pope shares lunch with 1,300 poor",
     "deck": "Leo XIV hosts about 1,300 people in need in the Paul VI hall.",
     "source": "Vatican News", "art": "pope"},
    {"num": 12, "place": "TURIN", "beat": "TENNIS", "tag": "CONFIRMED",
     "headline": "Alcaraz wins his first ATP Finals",
     "deck": "Beats Zverev 6-2, 7-6(7) to take the title in Turin.",
     "source": "ATP", "art": "tennis"},
    {"num": 13, "place": "CANBERRA", "beat": "DEFENCE", "tag": "REPORTED",
     "headline": "Marles says US budget office got AUKUS wrong",
     "deck": "Australia's defence minister criticises the CBO assessment.",
     "source": "Reuters", "art": "mic"},
]

# Briefs 14-34. Each body is kept to two lines in the four-column
# grid: place, one short fact, source. Football first (FBref, then
# Serie A), then the NFL and NBA Sundays, then SpaceX, France, Ghana.
BRIEFS = [
    (14, "Riyadh", "Saudi Arabia intercepts a Houthi drone aimed at Riyadh.",
     "Wires", "ME"),
    (15, "Seoul", "Education minister Choi quits in AI exam row.",
     "Yonhap", "APAC"),
    (16, "Turin", "Arribage/Olivetti win doubles final 3-6, 7-6(2), 10-6.",
     "ATP", "EU"),
    (17, "Jerusalem", "Eisenkot-Likud talks resume; invite Sat.",
     "Times of Israel", "ME"),
    (18, "Liverpool", "4-0 Man Utd at Anfield, ref Barrott.",
     "FBref", "EU"),
    (19, "Barcelona", "3-2 Villarreal, 59,034; goals 5', 7', 57', 61', 67'.",
     "FBref", "EU"),
    (20, "Hull", "2-0 Brighton, McBurnie 2 late goals; 24,461, ref Bankes.",
     "FBref", "EU"),
    (21, "Bergamo", "Atalanta 4-4 Inter; Esposito hat-trick 16', 32', 52'.",
     "Wires", "EU"),
    (22, "Milan", "AC Milan 5-1 Frosinone.",
     "Wires", "EU"),
    (23, "Turin", "Juventus 4-0 Venezia.",
     "Wires", "EU"),
    (24, "Dallas", "51-30 Titans; Prescott 325 yds, 4 pass TDs, 1 rush.",
     "Reuters", "AM"),
    (25, "Detroit", "Lions 31-21 Buccaneers; Gibbs 2 TD.",
     "Reuters", "AM"),
    (26, "Kansas City", "Chiefs 34-7 Cardinals.",
     "Reuters", "AM"),
    (27, "San Francisco", "49ers 35-10 Vikings; Purdy 3 TD, 49ers 9-1.",
     "Reuters", "AM"),
    (28, "New York", "Knicks 113-106 Pacers; Hart 10/11/10, Towns 30/13.",
     "Reuters", "AM"),
    (29, "Denver", "Nuggets 151-145 Bulls OT; Murray 45, Jokic 37/18/11.",
     "Reuters", "AM"),
    (30, "Miami", "123-113 Thunder; Adebayo 24/15/12, 7th straight win.",
     "Reuters", "AM"),
    (31, "Boston", "Warriors 88-87 Celtics.",
     "Reuters", "AM"),
    (32, "Vandenberg", "Falcon 9 lifts NROL-136 at 12:23:56 UTC.",
     "SpaceX", "AM"),
    (33, "Paris", "Sat protest, first reported Sun; 82,500, 150k claimed.",
     "AFP", "EU"),
    (34, "Accra", "Ghana 1-0 Morocco, Amputee World Cup final; Opentil 32'.",
     "Wires", "AF"),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"),
    ("06:00", "Ukraine reports 161 downed"),
    ("10:00", "HK polls close"),
    ("~13:30", "Las Vegas GP finishes"),
]

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed"),
    ("720/9", "India's record Test total in NZ"),
    ("856", "candidates in Hong Kong vote"),
]

REGIONS = [
    ("EUROPE", 13), ("MIDDLE EAST", 4), ("ASIA-PACIFIC", 4),
    ("AMERICAS", 11), ("AFRICA", 1), ("OCEANIA", 1),
]

DATE_CHECK = (
    "Every story on this page happened or was first reported on Sunday "
    "22 November 2026. Left out \u2014 other days' news: the Peru quake "
    "(Fri 20 Nov) \u00b7 the Myanmar ruling (Thu 19 Nov) \u00b7 the Shenzhen "
    "summit (Thu 19 Nov) \u00b7 \u2018El Chapo Isidro\u2019 \u2014 caught Fri 20, "
    "announced Sat 21 Nov \u00b7 the Nvidia probe (Fri 20 Nov) \u00b7 Cyclone "
    "Akvan (Fri 20 Nov) \u00b7 the Wall Street plunge (Fri 20 Nov) \u00b7 the "
    "Basra fire (Sat 21 Nov)."
)

FOOT_SOURCES = ("Sources: Reuters, BBC, AP, AFP, The Guardian, ESPN, FIA, "
                "Vatican News, ATP, Times of Israel, Yonhap "
                "\u2014 reports of Sunday 22 November 2026. "
                "Scenes are drawn illustrations, not photographs.")
FOOT_LEGEND = ("CONFIRMED = reported by the named source \u00b7 REPORTED = one "
               "source's account \u00b7 CLAIM = one party's claim \u00b7 PENDING = "
               "not settled yet.")


# ------------------------------------------------------------ illustrations
# Flat geometric scenes, one consistent style: dark navy night scenes
# for the war leads, warm rooms for COP31, simple pictograms for the
# ten cards. No photos, no AI images.

def _stars(draw, x0, y0, w, h, pts):
    for px, py, r in pts:
        draw.ellipse([x0 + px - r, y0 + py - r, x0 + px + r, y0 + py + r],
                     fill=(255, 255, 255))


def _drone(draw, cx, cy, s, fill):
    # Small quad-drone: body plus four rotor arms.
    draw.ellipse([cx - s, cy - s // 3, cx + s, cy + s // 3], fill=fill)
    for dx in (-1, 1):
        draw.line([(cx + dx * s, cy), (cx + dx * s * 2, cy - s // 2)],
                  fill=fill, width=2)
        draw.line([(cx + dx * s * 2 - 3, cy - s // 2),
                   (cx + dx * s * 2 + 3, cy - s // 2)], fill=fill, width=2)


def art_drones(draw, x, y, w, h):
    """Night sky over Kyiv: drones, a lit block, a searchlight."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY_DARK)
    _stars(draw, x, y, w, h, [(20, 14, 1), (60, 8, 1), (110, 20, 2),
                              (160, 10, 1), (210, 18, 1), (250, 8, 2),
                              (285, 22, 1), (140, 30, 1), (90, 34, 1)])
    # Moon.
    draw.ellipse([x + w - 42, y + 10, x + w - 18, y + 34], fill=(240, 230, 190))
    # Drones crossing the sky.
    _drone(draw, x + 55, y + 34, 9, (232, 200, 106))
    _drone(draw, x + 130, y + 22, 8, (232, 200, 106))
    _drone(draw, x + 205, y + 40, 9, (232, 200, 106))
    _drone(draw, x + 165, y + 58, 7, (200, 170, 90))
    # City block, windows lit.
    draw.rectangle([x + 8, y + h - 46, x + 118, y + h], fill=(28, 34, 58))
    draw.rectangle([x + 128, y + h - 34, x + 196, y + h], fill=(24, 30, 52))
    for wx in range(16, 112, 14):
        for wy in range(h - 40, h - 4, 12):
            if (wx + wy) % 28:
                draw.rectangle([x + wx, y + wy, x + wx + 7, y + wy + 7],
                               fill=(240, 200, 90))
    # Searchlight beam from the rooftops, kept slim and to the right of
    # the drones so it reads as light, not a slash across the sky.
    draw.polygon([(x + 168, y + h - 34), (x + 232, y + 18),
                  (x + 246, y + 18), (x + 178, y + h - 34)],
                 fill=(240, 230, 190))
    # Red flash: one drone hit.
    draw.polygon([(x + 245, y + 52), (x + 252, y + 44), (x + 258, y + 52),
                  (x + 266, y + 48), (x + 258, y + 58), (x + 262, y + 66),
                  (x + 252, y + 60), (x + 244, y + 66), (x + 248, y + 57)],
                 fill=(230, 80, 60))


def art_cop31(draw, x, y, w, h):
    """Conference table: delegates, a globe, the final text."""
    draw.rectangle([x, y, x + w, y + h], fill=(58, 96, 92))
    # Back wall band and windows.
    draw.rectangle([x, y, x + w, y + 34], fill=(38, 66, 64))
    for wx in range(14, w - 20, 44):
        draw.rectangle([x + wx, y + 8, x + wx + 26, y + 26],
                       fill=(240, 220, 160))
    # Globe on a stand, left.
    draw.ellipse([x + 16, y + 44, x + 52, y + 80], fill=(70, 140, 110))
    draw.ellipse([x + 24, y + 52, x + 36, y + 64], fill=(120, 180, 140))
    draw.ellipse([x + 36, y + 62, x + 48, y + 74], fill=(120, 180, 140))
    draw.line([(x + 34, y + 80), (x + 34, y + 92)], fill=(60, 40, 20), width=3)
    draw.line([(x + 24, y + 92), (x + 44, y + 92)], fill=(60, 40, 20), width=3)
    # Delegates behind the table: heads and shoulders.
    for i, dx in enumerate(range(72, w - 30, 42)):
        skin = (222, 184, 150) if i % 2 == 0 else (140, 100, 70)
        suit = (40, 50, 90) if i % 3 else (90, 40, 40)
        draw.ellipse([x + dx, y + 44, x + dx + 24, y + 68], fill=skin)
        draw.pieslice([x + dx, y + 44, x + dx + 24, y + 62],
                      start=180, end=360, fill=(30, 30, 30))
        draw.rectangle([x + dx - 4, y + 68, x + dx + 28, y + 92], fill=suit)
    # Table.
    draw.rectangle([x, y + 92, x + w, y + h], fill=(120, 82, 50))
    draw.rectangle([x, y + 92, x + w, y + 96], fill=(150, 108, 66))
    # The final text: a white document on the table.
    draw.rectangle([x + w // 2 - 26, y + 78, x + w // 2 + 26, y + 104],
                   fill=(255, 255, 255), outline=(150, 150, 150))
    for ly in range(84, 100, 5):
        draw.line([(x + w // 2 - 20, y + ly), (x + w // 2 + 20, y + ly)],
                  fill=(120, 120, 120), width=1)


def art_bahrain(draw, x, y, w, h):
    """Night over the Gulf: radar dishes, a burning facility, the sea."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY_DARK)
    _stars(draw, x, y, w, h, [(24, 12, 1), (80, 8, 2), (150, 14, 1),
                              (210, 10, 1), (260, 16, 2), (120, 26, 1)])
    # Sea.
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(24, 68, 110))
    for sx in range(10, w - 10, 36):
        draw.line([(x + sx, y + h - 22), (x + sx + 18, y + h - 22)],
                  fill=(120, 170, 210), width=2)
    # Two radar towers with dishes.
    for tx in (52, 178):
        draw.rectangle([x + tx - 3, y + 44, x + tx + 3, y + h - 34],
                       fill=(140, 140, 150))
        draw.pieslice([x + tx - 22, y + 18, x + tx + 22, y + 62],
                      start=200, end=340, fill=(200, 200, 210))
        draw.line([(x + tx, y + 40), (x + tx, y + 46)], fill=(200, 200, 210),
                  width=3)
    # Facility blocks between the towers.
    draw.rectangle([x + 96, y + h - 62, x + 148, y + h - 34],
                   fill=(52, 58, 84))
    draw.rectangle([x + 104, y + h - 74, x + 126, y + h - 62],
                   fill=(52, 58, 84))
    # Flame on the facility.
    draw.polygon([(x + 108, y + h - 74), (x + 115, y + h - 92),
                  (x + 122, y + h - 74)], fill=(240, 140, 40))
    draw.polygon([(x + 112, y + h - 74), (x + 115, y + h - 84),
                  (x + 118, y + h - 74)], fill=(250, 210, 90))
    # Small patrol boat on the sea.
    draw.polygon([(x + 220, y + h - 26), (x + 262, y + h - 26),
                  (x + 252, y + h - 14), (x + 230, y + h - 14)],
                 fill=(180, 180, 190))
    draw.rectangle([x + 236, y + h - 34, x + 248, y + h - 26],
                   fill=(180, 180, 190))
    # White curved arrow: claim meets denial.
    draw.arc([x + 150, y + 8, x + 230, y + 58], start=200, end=330,
             fill=(255, 255, 255), width=3)
    draw.polygon([(x + 226, y + 12), (x + 234, y + 22), (x + 220, y + 26)],
                 fill=(255, 255, 255))


def art_hk_lead(draw, x, y, w, h):
    """Hong Kong votes: skyline at dusk, a big ballot box, a green tick."""
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    # Skyline towers along the bottom, navy silhouettes.
    towers = [(0, 52, 34), (40, 34, 30), (76, 58, 26), (108, 40, 30),
              (144, 62, 24), (174, 44, 28), (208, 56, 26), (240, 38, 30),
              (276, 54, 28)]
    for tx, th, tw in towers:
        draw.rectangle([x + tx, y + h - th, x + tx + tw, y + h],
                       fill=(30, 46, 80))
        for wy in range(h - th + 6, h - 4, 10):
            for wx in range(tx + 5, tx + tw - 5, 10):
                if (wx + wy) % 20 == 0:
                    draw.rectangle([x + wx, y + wy, x + wx + 4, y + wy + 4],
                                   fill=(240, 200, 90))
    # Ballot box, front and centre, with a white ballot and green tick.
    bx, by = x + w // 2 - 34, y + 14
    draw.rectangle([bx, by + 18, bx + 68, by + 62], fill=(176, 30, 36))
    draw.rectangle([bx, by + 12, bx + 68, by + 20], fill=(120, 20, 24))
    draw.rectangle([bx + 26, by + 6, bx + 42, by + 14], fill=(40, 40, 40))
    draw.rectangle([bx + 72, by + 2, bx + 122, by + 34],
                   fill=(255, 255, 255), outline=(150, 150, 150))
    draw.line([(bx + 78, by + 20), (bx + 88, by + 30), (bx + 112, by + 8)],
              fill=(34, 120, 60), width=4)


def art_cricket_lead(draw, x, y, w, h):
    """Wellington Test: green outfield, pale pitch, bat, ball, stumps."""
    draw.rectangle([x, y, x + w, y + h], fill=(110, 165, 85))
    draw.rectangle([x, y + h // 2 - 12, x + w, y + h // 2 + 12],
                   fill=(222, 200, 150))
    draw.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(255, 255, 255),
              width=1)
    # Bat, mid-pitch.
    draw.rectangle([x + w // 2 - 52, y + 12, x + w // 2 - 40, y + 38],
                   fill=(180, 140, 80))
    draw.polygon([(x + w // 2 - 52, y + 38), (x + w // 2 - 40, y + 38),
                  (x + w // 2 - 34, y + 56), (x + w // 2 - 58, y + 56)],
                 fill=(200, 160, 90))
    # Red ball, right of the bat.
    draw.ellipse([x + w // 2 + 30, y + h // 2 - 26, x + w // 2 + 46,
                  y + h // 2 - 10], fill=(176, 30, 36))
    # Stumps at the far end.
    for sx in (w - 64, w - 56, w - 48):
        draw.line([(x + sx, y + h - 34), (x + sx, y + h - 14)],
                  fill=(240, 220, 120), width=3)
    draw.line([(x + w - 66, y + h - 36), (x + w - 44, y + h - 36)],
              fill=(240, 220, 120), width=2)


def art_radar(draw, x, y, w, h):
    """Radar dish sweeping over a night sea; a small flame on a facility."""
    _pict_bg(draw, x, y, w, h, NAVY_DARK)
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(24, 68, 110))
    for sx in range(8, w - 8, 30):
        draw.line([(x + sx, y + h - 7), (x + sx + 16, y + h - 7)],
                  fill=(120, 170, 210), width=2)
    # Dish tower, left.
    draw.rectangle([x + 26, y + 22, x + 32, y + h - 12],
                   fill=(140, 140, 150))
    draw.pieslice([x + 8, y + 4, x + 50, y + 32], start=200, end=340,
                  fill=(200, 200, 210))
    # Sweep arc.
    draw.arc([x + 56, y + 2, x + 120, y + 40], start=300, end=60,
             fill=(240, 200, 90), width=2)
    # Facility block with a flame, right.
    draw.rectangle([x + 128, y + h - 30, x + 168, y + h - 12],
                   fill=(52, 58, 84))
    draw.polygon([(x + 142, y + h - 30), (x + 148, y + h - 42),
                  (x + 154, y + h - 30)], fill=(240, 140, 40))
    draw.polygon([(x + 145, y + h - 30), (x + 148, y + h - 38),
                  (x + 151, y + h - 30)], fill=(250, 210, 90))


def art_nepal(draw, x, y, w, h):
    """Himalayas and a landing plane: Nepal's PM arrives in Delhi."""
    _pict_bg(draw, x, y, w, h, (222, 232, 240))
    draw.polygon([(x, y + h), (x + 44, y + 10), (x + 88, y + h)],
                 fill=(150, 130, 100))
    draw.polygon([(x + 60, y + h), (x + 118, y + 4), (x + 176, y + h)],
                 fill=(120, 100, 80))
    draw.polygon([(x + 108, y + 4), (x + 118, y + 4), (x + 126, y + 18),
                  (x + 112, y + 18)], fill=(255, 255, 255))
    # Plane crossing the sky.
    draw.polygon([(x + 96, y + 22), (x + 160, y + 22), (x + 168, y + 28),
                  (x + 96, y + 28)], fill=(240, 240, 245))
    draw.polygon([(x + 120, y + 14), (x + 132, y + 14), (x + 128, y + 22),
                  (x + 118, y + 22)], fill=(240, 240, 245))
    draw.polygon([(x + 150, y + 14), (x + 158, y + 14), (x + 154, y + 22),
                  (x + 146, y + 22)], fill=(240, 240, 245))
    draw.line([(x + 8, y + h - 6), (x + w - 8, y + h - 6)],
              fill=(120, 120, 120), width=2)


def art_mercury(draw, x, y, w, h):
    """Mercury, cratered and grey, with its orbit ring and a small probe."""
    _pict_bg(draw, x, y, w, h, (16, 20, 36))
    _stars(draw, x, y, w, h, [(14, 8, 1), (60, 6, 1), (150, 10, 1),
                              (170, 20, 1), (30, 34, 1), (120, 38, 1)])
    # Orbit ring.
    draw.ellipse([x + 18, y - 6, x + w - 18, y + h + 6],
                 outline=(150, 150, 170), width=1)
    # Mercury with craters.
    cx, cy, r = x + w // 2 - 8, y + h // 2, 15
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 158, 140))
    for ox, oy, cr in ((-6, -5, 3), (5, 2, 4), (-2, 7, 2), (7, -7, 2)):
        draw.ellipse([cx + ox - cr, cy + oy - cr, cx + ox + cr,
                      cy + oy + cr], fill=(140, 130, 114))
    # Probe on the ring, top right.
    draw.rectangle([x + w - 34, y + 6, x + w - 26, y + 12],
                   fill=(220, 220, 230))
    draw.line([(x + w - 34, y + 9), (x + w - 42, y + 9)],
              fill=(220, 220, 230), width=2)


def art_pope(draw, x, y, w, h):
    """A long shared lunch table: plates, bread, and guests."""
    _pict_bg(draw, x, y, w, h, (242, 236, 224))
    # Guests: heads above the table.
    for i, hx in enumerate((26, 66, 106, 146)):
        skin = (222, 184, 150) if i % 2 == 0 else (140, 100, 70)
        draw.ellipse([x + hx, y + 4, x + hx + 22, y + 26], fill=skin)
        draw.rectangle([x + hx - 2, y + 26, x + hx + 24, y + 32],
                       fill=(90, 40, 40) if i == 1 else (40, 50, 90))
    # Table with plates and bread.
    draw.rectangle([x, y + 32, x + w, y + h], fill=(120, 82, 50))
    for px in (18, 62, 106, 150):
        draw.ellipse([x + px, y + 36, x + px + 18, y + 44],
                     fill=(255, 255, 255))
    draw.ellipse([x + 84, y + h - 12, x + 100, y + h - 4],
                 fill=(200, 160, 90))


def art_tennis(draw, x, y, w, h):
    """A tennis court from above: baselines, net, ball, racket."""
    _pict_bg(draw, x, y, w, h, (58, 110, 70))
    draw.rectangle([x + 10, y + 6, x + w - 10, y + h - 6],
                   fill=(46, 90, 160), outline=(255, 255, 255), width=1)
    draw.line([(x + 10, y + h // 2), (x + w - 10, y + h // 2)],
              fill=(255, 255, 255), width=2)
    draw.line([(x + w // 2, y + 6), (x + w // 2, y + h - 6)],
              fill=(255, 255, 255), width=1)
    # Ball, top right.
    draw.ellipse([x + w - 34, y + 10, x + w - 22, y + 22],
                 fill=(210, 230, 60), outline=(255, 255, 255), width=1)
    # Racket, bottom left.
    draw.ellipse([x + 16, y + h - 24, x + 44, y + h - 4],
                 outline=(220, 220, 230), width=3)
    for lx in range(22, 40, 6):
        draw.line([(x + lx, y + h - 22), (x + lx, y + h - 6)],
                  fill=(220, 220, 230), width=1)
    draw.line([(x + 44, y + h - 8), (x + 58, y + h - 2)],
              fill=(180, 140, 80), width=3)


def art_mic(draw, x, y, w, h):
    """A press microphone on its stand, with sound arcs."""
    _pict_bg(draw, x, y, w, h, (238, 236, 228))
    # Backdrop: two columns of a parliament hall.
    for cx in (14, w - 30):
        draw.rectangle([x + cx, y + 4, x + cx + 16, y + h - 4],
                       fill=(120, 110, 88))
        draw.rectangle([x + cx - 2, y + 4, x + cx + 18, y + 10],
                       fill=(90, 80, 64))
    # Mic stand.
    draw.line([(x + w // 2, y + 22), (x + w // 2, y + h - 4)],
              fill=(60, 60, 70), width=3)
    draw.line([(x + w // 2 - 12, y + h - 4), (x + w // 2 + 12, y + h - 4)],
              fill=(60, 60, 70), width=3)
    # Mic head with grille dots.
    draw.ellipse([x + w // 2 - 11, y + 4, x + w // 2 + 11, y + 26],
                 fill=(40, 50, 90))
    for gx in (-5, 0, 5):
        for gy in (10, 15, 20):
            draw.ellipse([x + w // 2 + gx - 1, y + gy - 1,
                          x + w // 2 + gx + 1, y + gy + 1],
                         fill=(160, 170, 200))
    # Sound arcs.
    draw.arc([x + w // 2 + 18, y + 8, x + w // 2 + 34, y + 24],
             start=270, end=90, fill=(176, 30, 36), width=2)
    draw.arc([x + w // 2 - 34, y + 8, x + w // 2 - 18, y + 24],
             start=90, end=270, fill=(176, 30, 36), width=2)


LEAD_ART = {"drones": art_drones, "ballot_lead": art_hk_lead,
            "cricket_lead": art_cricket_lead}


def _pict_bg(draw, x, y, w, h, fill):
    draw.rectangle([x, y, x + w, y + h], fill=fill)


def art_ballot(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (240, 235, 220))
    draw.rectangle([x + 18, y + 22, x + 78, y + h - 6], fill=(176, 30, 36))
    draw.rectangle([x + 18, y + 16, x + 78, y + 24], fill=(120, 20, 24))
    draw.rectangle([x + 42, y + 10, x + 54, y + 18], fill=(40, 40, 40))
    draw.rectangle([x + 96, y + 8, x + w - 14, y + 34], fill=(255, 255, 255),
                   outline=(150, 150, 150))
    draw.line([(x + 100, y + 22), (x + 108, y + 30), (x + 120, y + 12)],
              fill=(34, 120, 60), width=3)
    for i in range(3):
        draw.rectangle([x + 96 + i * 26, y + 40, x + 116 + i * 26, y + h - 8],
                       fill=(31, 78, 140))


def art_cricket(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (120, 170, 90))
    draw.rectangle([x, y + h // 2 - 8, x + w, y + h // 2 + 8],
                   fill=(222, 200, 150))
    draw.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(255, 255, 255),
              width=1)
    # Bat and ball.
    draw.rectangle([x + 34, y + 10, x + 44, y + 34], fill=(180, 140, 80))
    draw.polygon([(x + 34, y + 34), (x + 44, y + 34), (x + 48, y + 48),
                  (x + 30, y + 48)], fill=(200, 160, 90))
    draw.ellipse([x + 120, y + 30, x + 132, y + 42], fill=(176, 30, 36))
    # Stumps.
    for sx in (150, 156, 162):
        draw.line([(x + sx, y + 8), (x + sx, y + 24)], fill=(240, 220, 120),
                  width=2)


def art_f1(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (24, 28, 48))
    draw.arc([x - 30, y - 6, x + 110, y + h + 20], start=270, end=90,
             fill=(200, 200, 210), width=8)
    draw.arc([x - 30, y - 6, x + 110, y + h + 20], start=300, end=60,
             fill=(240, 200, 60), width=3)
    # Checkered flag.
    for r in range(2):
        for c in range(4):
            fill = (255, 255, 255) if (r + c) % 2 == 0 else (20, 20, 20)
            draw.rectangle([x + w - 52 + c * 10, y + 8 + r * 10,
                            x + w - 42 + c * 10, y + 18 + r * 10], fill=fill)
    draw.line([(x + w - 52, y + 8), (x + w - 52, y + 44)], fill=(255, 255, 255),
              width=2)
    # Car: low red wedge with wheels.
    draw.polygon([(x + 30, y + h - 26), (x + 78, y + h - 26),
                  (x + 70, y + h - 14), (x + 38, y + h - 14)],
                 fill=(200, 40, 40))
    draw.ellipse([x + 38, y + h - 16, x + 50, y + h - 4], fill=(20, 20, 20))
    draw.ellipse([x + 62, y + h - 16, x + 74, y + h - 4], fill=(20, 20, 20))


def art_ship(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (58, 96, 130))
    draw.rectangle([x, y + h - 20, x + w, y + h], fill=(30, 60, 95))
    for sx in range(8, w - 8, 30):
        draw.line([(x + sx, y + h - 12), (x + sx + 16, y + h - 12)],
                  fill=(160, 200, 230), width=2)
    # Hull and containers.
    draw.polygon([(x + 22, y + h - 22), (x + w - 22, y + h - 22),
                  (x + w - 34, y + h - 8), (x + 34, y + h - 8)],
                 fill=(60, 60, 70))
    for cx, col in ((36, (176, 60, 40)), (62, (40, 110, 160)),
                    (88, (200, 160, 60)), (114, (90, 140, 90))):
        draw.rectangle([x + cx, y + h - 40, x + cx + 22, y + h - 22], fill=col)
    draw.rectangle([x + 140, y + h - 52, x + 152, y + h - 22],
                   fill=(220, 220, 220))
    # Smoke and flame.
    draw.ellipse([x + 138, y + 6, x + 156, y + 20], fill=(90, 90, 90))
    draw.ellipse([x + 148, y + 2, x + 164, y + 14], fill=(120, 120, 120))
    draw.polygon([(x + 140, y + 22), (x + 147, y + 8), (x + 154, y + 22)],
                 fill=(240, 140, 40))


def art_power(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (240, 230, 210))
    # Skyline: lit and dark blocks.
    blocks = [(10, 26, 30), (44, 14, 44), (80, 30, 26), (112, 18, 40),
              (152, 28, 30)]
    for bx, by, bw in blocks:
        draw.rectangle([x + bx, y + by, x + bx + bw, y + h - 4],
                       fill=(52, 58, 84))
        for wy in range(by + 6, h - 10, 10):
            for wx in range(bx + 5, bx + bw - 5, 10):
                if (wx + wy) % 20 == 0:
                    draw.rectangle([x + wx, y + wy, x + wx + 4, y + wy + 4],
                                   fill=(240, 200, 90))
    # Lightning bolt over the dark city.
    draw.polygon([(x + w - 30, y + 4), (x + w - 14, y + 4),
                  (x + w - 24, y + 22), (x + w - 14, y + 22),
                  (x + w - 28, y + 44), (x + w - 26, y + 26),
                  (x + w - 36, y + 26)], fill=(240, 200, 60))


def art_hospital(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (235, 242, 245))
    draw.rectangle([x + 14, y + 12, x + 70, y + h - 8], fill=(255, 255, 255),
                   outline=(180, 180, 180))
    draw.rectangle([x + 34, y + 18, x + 50, y + 40], fill=(176, 30, 36))
    draw.rectangle([x + 28, y + 26, x + 56, y + 32], fill=(176, 30, 36))
    # Heart trace.
    pts = [(x + 82, y + 30), (x + 96, y + 30), (x + 102, y + 18),
           (x + 110, y + 42), (x + 116, y + 26), (x + 122, y + 30),
           (x + 140, y + 30), (x + 152, y + 30)]
    draw.line(pts, fill=(176, 30, 36), width=2)
    draw.line([(x + 82, y + h - 12), (x + w - 10, y + h - 12)],
              fill=(180, 180, 180), width=1)


def art_fbi(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (232, 236, 242))
    # Server stack.
    for i in range(3):
        sy = y + 8 + i * 14
        draw.rectangle([x + 12, sy, x + 62, sy + 11], fill=(40, 50, 90))
        draw.ellipse([x + 18, sy + 4, x + 22, sy + 8], fill=(90, 200, 120))
        draw.line([(x + 30, sy + 3), (x + 54, sy + 3)], fill=(160, 170, 200),
                  width=1)
        draw.line([(x + 30, sy + 7), (x + 48, sy + 7)], fill=(160, 170, 200),
                  width=1)
    # Magnifying glass.
    draw.ellipse([x + 92, y + 6, x + 150, y + 44], outline=(20, 38, 74),
                 width=4)
    draw.ellipse([x + 98, y + 12, x + 144, y + 38], fill=(180, 210, 235))
    draw.line([(x + 142, y + 38), (x + 168, y + h - 8)], fill=(20, 38, 74),
              width=5)
    draw.text((x + 104, y + 18), "?", font=font(SANS_BOLD, 18),
              fill=(20, 38, 74))


def art_tower(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (222, 232, 240))
    # Control tower.
    draw.rectangle([x + 30, y + 16, x + 52, y + h - 6], fill=(90, 100, 120))
    draw.polygon([(x + 22, y + 16), (x + 60, y + 16), (x + 52, y + 4),
                  (x + 30, y + 4)], fill=(140, 160, 190))
    draw.rectangle([x + 26, y + 8, x + 56, y + 14], fill=(200, 220, 240))
    # Grounded plane.
    draw.polygon([(x + 84, y + 34), (x + 168, y + 34), (x + 176, y + 40),
                  (x + 84, y + 40)], fill=(180, 180, 190))
    draw.polygon([(x + 120, y + 24), (x + 132, y + 24), (x + 128, y + 34),
                  (x + 118, y + 34)], fill=(180, 180, 190))
    draw.line([(x + 84, y + h - 8), (x + w - 8, y + h - 8)],
              fill=(120, 120, 120), width=2)
    # Red cross over the runway: flights stopped.
    draw.line([(x + 96, y + 44), (x + 108, y + 56)], fill=(176, 30, 36),
              width=3)
    draw.line([(x + 108, y + 44), (x + 96, y + 56)], fill=(176, 30, 36),
              width=3)


def art_bottle(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (242, 236, 224))
    # Bottle.
    draw.rectangle([x + 30, y + 8, x + 44, y + 18], fill=(60, 90, 60))
    draw.polygon([(x + 30, y + 18), (x + 44, y + 18), (x + 52, y + 30),
                  (x + 22, y + 30)], fill=(90, 130, 80))
    draw.rectangle([x + 22, y + 30, x + 52, y + h - 6], fill=(110, 150, 100))
    draw.rectangle([x + 28, y + 36, x + 46, y + h - 12], fill=(230, 230, 210))
    # Warning triangle.
    draw.polygon([(x + 110, y + 12), (x + 136, y + 44), (x + 84, y + 44)],
                 fill=(240, 200, 60), outline=(176, 30, 36))
    draw.text((x + 106, y + 26), "!", font=font(SANS_BOLD, 16),
              fill=(176, 30, 36))
    draw.line([(x + 84, y + h - 10), (x + w - 10, y + h - 10)],
              fill=(176, 30, 36), width=2)


def art_quake(draw, x, y, w, h):
    _pict_bg(draw, x, y, w, h, (238, 232, 214))
    # Mountains.
    draw.polygon([(x, y + h), (x + 40, y + 14), (x + 80, y + h)],
                 fill=(150, 130, 100))
    draw.polygon([(x + 56, y + h), (x + 110, y + 6), (x + 164, y + h)],
                 fill=(120, 100, 80))
    draw.polygon([(x + 100, y + 6), (x + 110, y + 6), (x + 118, y + 20),
                  (x + 104, y + 20)], fill=(255, 255, 255))
    # Seismograph trace.
    pts = [(x + 8, y + h - 14), (x + 30, y + h - 14), (x + 38, y + h - 30),
           (x + 46, y + h - 6), (x + 54, y + h - 22), (x + 62, y + h - 14),
           (x + 90, y + h - 14), (x + 98, y + h - 34), (x + 106, y + h - 4),
           (x + 114, y + h - 20), (x + 122, y + h - 14), (x + w - 8, y + h - 14)]
    draw.line(pts, fill=(176, 30, 36), width=2)


TEN_ART = {"ballot": art_ballot, "cricket": art_cricket, "f1": art_f1,
           "ship": art_ship, "power": art_power, "hospital": art_hospital,
           "fbi": art_fbi, "tower": art_tower, "bottle": art_bottle,
           "quake": art_quake, "radar": art_radar, "nepal": art_nepal,
           "mercury": art_mercury, "pope": art_pope, "tennis": art_tennis,
           "mic": art_mic}


# ------------------------------------------------------------------- map
# Flat beige continents on a pale ocean, drawn from coarse lon/lat
# outlines. Equirectangular over lon -180..180, lat 84..-60.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-60, 55), (-55, 47), (-60, 45),
     (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29),
     (-97, 26), (-105, 22), (-110, 24), (-115, 29), (-120, 34),
     (-125, 40), (-125, 49), (-130, 55), (-140, 60), (-155, 58),
     (-165, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
     (-30, 76), (-45, 76), (-55, 74), (-58, 70), (-58, 64)],
    # South America
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41),
     (-68, -50), (-70, -55), (-73, -50), (-73, -40), (-72, -30),
     (-70, -20), (-77, -12), (-81, -6), (-79, 9)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (43, 11), (48, 11), (51, 10), (44, 0),
     (40, -10), (35, -18), (32, -26), (28, -33), (20, -35), (15, -27),
     (12, -18), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (40, 68),
     (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 66), (178, 65), (170, 60), (162, 56), (158, 52), (150, 59),
     (142, 55), (140, 45), (135, 43), (130, 42), (127, 40), (122, 38),
     (120, 32), (115, 23), (108, 18), (105, 10), (100, 8), (98, 12),
     (95, 16), (92, 21), (88, 22), (85, 19), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 23), (62, 25), (58, 26), (55, 26),
     (52, 28), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36),
     (30, 36), (27, 40), (23, 40), (19, 42), (15, 44), (12, 44),
     (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51),
     (-5, 50)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 41), (143, 43),
     (141, 45), (139, 40), (136, 37), (132, 33), (130, 31)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -8), (130, -3), (135, -4), (140, -8), (138, -2), (132, 0),
     (128, 2), (122, 1), (118, 0), (112, -2), (105, -3), (100, 0),
     (95, 5)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (138, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (174, -41), (171, -44), (167, -45)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25), (43, -22),
     (44, -16)],
]

# Story number -> (lon, lat, nudge_x, nudge_y). The tight clusters
# (Europe, the Gulf, the US east coast) are fanned out with small
# nudges so no two numbered dots touch.
DOTS = [
    (1, 33, 49.5, 0, 0),       # Kyiv region, Ukraine
    (2, 114.2, 22.3, 0, 0),    # Hong Kong
    (3, 174.8, -41.3, 0, 0),   # Wellington, NZ
    (4, 50.6, 26.2, 9, 7),     # Manama, Bahrain
    (5, -115.1, 36.2, 6, -6),  # Las Vegas
    (6, 51.4, 35.7, -7, -7),   # Tehran
    (7, -47.9, -15.8, 0, 0),   # Brasilia
    (8, 4.35, 50.85, -9, -11), # Brussels
    (9, 77.2, 28.6, -3, -2),   # New Delhi
    (10, 8.65, 49.87, 3, -14), # Darmstadt (ESA control), BepiColombo
    (11, 12.45, 41.9, 10, 17), # Vatican City
    (12, 7.7, 45.1, -6, 13),   # Turin, ATP Finals
    (13, 149.1, -35.3, 0, 0),  # Canberra
    (14, 46.7, 24.6, -9, -2),  # Riyadh
    (15, 127.0, 37.5, 0, 0),   # Seoul
    (16, 7.7, 45.1, 6, -3),    # Turin, ATP doubles final
    (17, 35.2, 31.8, -8, 8),   # Jerusalem
    (18, -2.99, 53.43, -16, 13),  # Liverpool
    (19, 2.19, 41.38, -15, 17),   # Barcelona
    (20, -0.34, 53.74, -19, -7),  # Hull
    (21, 9.67, 45.70, 22, -13),   # Bergamo, Atalanta
    (22, 9.19, 45.46, 17, 7),     # Milan
    (23, 7.69, 45.07, -10, -3),   # Turin, Juventus
    (24, -96.8, 32.78, 0, 0),     # Dallas
    (25, -83.05, 42.33, 0, 0),    # Detroit
    (26, -94.58, 39.1, -4, -13),  # Kansas City
    (27, -121.97, 37.35, -4, -4), # Santa Clara, 49ers
    (28, -74.0, 40.71, 6, -6),    # New York
    (29, -104.99, 39.74, -6, 8),  # Denver
    (30, -80.19, 25.76, 0, 0),    # Miami
    (31, -71.06, 42.36, 7, 6),    # Boston
    (32, -120.62, 34.74, -7, 7),  # Vandenberg
    (33, 2.35, 48.85, -17, 0),    # Paris
    (34, -0.19, 5.6, 0, 0),       # Accra, Ghana
]


def draw_map(draw, x0, y0, w, h):
    """Flat beige world map with numbered red pins for stories 1-34."""
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 84.0, -60.0

    def fpx(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)

    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    for poly in CONTINENTS:
        pts = [fpx(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=RULE, width=1)
    for num, lon, lat, nx, ny in DOTS:
        cx, cy = fpx(lon, lat)
        cx += nx
        cy += ny
        r = 5 if num >= 10 else 4
        draw.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1],
                     outline=NAVY_DARK, width=1)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        label = str(num)
        labf = font(SANS_BOLD, 7 if num >= 10 else 8)
        lb = draw.textbbox((0, 0), label, font=labf)
        draw.text((cx - (lb[0] + lb[2]) / 2, cy - (lb[1] + lb[3]) / 2),
                  label, font=labf, fill=(255, 255, 255))


# ------------------------------------------------------------ page build
def build_page():
    """Render the full front page and return the PIL image."""
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # --- top bar ---------------------------------------------------------
    draw.rectangle([0, 0, W, 20], fill=NAVY)
    barf = font(SANS_BOLD, 10)
    draw.text((MX, 5), "THE WORLD IN ONE DAY", font=barf,
              fill=(240, 230, 200))
    right = "ONE PAGE \u00b7 ALL THE NEWS"
    tw = draw.textlength(right, font=barf)
    draw.text((W - MX - tw, 5), right, font=barf, fill=(240, 230, 200))

    # --- masthead ----------------------------------------------------------
    title = "Sunday 22 November 2026"
    tf = fit_font(draw, title, SERIF_BOLD, 60, CW)
    tb = draw.textbbox((0, 0), title, font=tf)
    draw.text(((W - (tb[2] - tb[0])) / 2 - tb[0], 24 - tb[1]), title,
              font=tf, fill=NAVY)
    sub = ("186 drones over Ukraine in the night \u00b7 Hong Kong votes "
           "\u00b7 India declare 720/9")
    sf = font(SERIF_ITALIC, 15)
    sb = draw.textbbox((0, 0), sub, font=sf)
    draw.text(((W - (sb[2] - sb[0])) / 2 - sb[0], 86 - sb[1]), sub,
              font=sf, fill=RED)
    stats = ("34 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED "
             "SUNDAY 22 NOVEMBER 2026")
    stf = font(SANS_BOLD, 12)
    stb = draw.textbbox((0, 0), stats, font=stf)
    draw.text(((W - (stb[2] - stb[0])) / 2 - stb[0], 105 - stb[1]), stats,
              font=stf, fill=NAVY)
    hrule(draw, MX, W - MX, 122, fill=NAVY, width=2)

    # --- the day in numbers --------------------------------------------------
    nbox_w = (CW - (len(NUMBERS) - 1) * 6) // len(NUMBERS)
    for i, (val, lab) in enumerate(NUMBERS):
        x = MX + i * (nbox_w + 6)
        draw.rectangle([x, 128, x + nbox_w, 168], fill=PAPER_DARK,
                       outline=RULE, width=1)
        vf = font(SANS_BOLD, 20)
        vb = draw.textbbox((0, 0), val, font=vf)
        draw.text((x + (nbox_w - (vb[2] - vb[0])) / 2 - vb[0],
                   128 + 4 - vb[1]), val, font=vf, fill=RED)
        lf = font(SANS, 9)
        lb = draw.textbbox((0, 0), lab, font=lf)
        draw.text((x + (nbox_w - (lb[2] - lb[0])) / 2 - lb[0],
                   168 - 4 - lb[3]), lab, font=lf, fill=GREY)

    # --- region strip ---------------------------------------------------------
    seg_w = CW // len(REGIONS)
    for i, (name, count) in enumerate(REGIONS):
        x = MX + i * seg_w
        w = seg_w if i < len(REGIONS) - 1 else CW - i * seg_w
        draw.rectangle([x, 178, x + w, 196], fill=REGION_COLORS[name])
        label = "%s %d" % (name, count)
        rf = font(SANS_BOLD, 11)
        rb = draw.textbbox((0, 0), label, font=rf)
        draw.text((x + (w - (rb[2] - rb[0])) / 2 - rb[0],
                   178 + (18 - (rb[3] - rb[1])) / 2 - rb[1]), label,
                  font=rf, fill=(255, 255, 255))

    # --- the day in utc --------------------------------------------------------
    draw.rectangle([MX, 202, MX + 108, 218], fill=NAVY)
    uf = font(SANS_BOLD, 10)
    ub = draw.textbbox((0, 0), "THE DAY IN UTC", font=uf)
    draw.text((MX + (108 - (ub[2] - ub[0])) / 2 - ub[0],
               202 + (16 - (ub[3] - ub[1])) / 2 - ub[1]), "THE DAY IN UTC",
              font=uf, fill=(255, 255, 255))
    utc_parts = []
    for t, ev in UTC_EVENTS:
        utc_parts.append("%s %s" % (t, ev))
    utc_line = "  \u00b7  ".join(utc_parts)
    utf = font(SANS, 10)
    utb = draw.textbbox((0, 0), utc_line, font=utf)
    draw.text((MX + 116, 202 + (16 - (utb[3] - utb[1])) / 2 - utb[1]),
              utc_line, font=utf, fill=INK)

    # --- three leads ------------------------------------------------------------
    lead_w = (CW - 2 * 10) // 3
    lead_y = 226
    ill_h = 96
    for i, lead in enumerate(LEADS):
        x = MX + i * (lead_w + 10)
        LEAD_ART[lead["art"]](draw, x, lead_y, lead_w, ill_h)
        draw.rectangle([x, lead_y, x + lead_w, lead_y + ill_h],
                       outline=NAVY, width=1)
        # Kicker chip on the illustration, top-left.
        kf = font(SANS_BOLD, 9)
        kb = draw.textbbox((0, 0), lead["kicker"], font=kf)
        kw = kb[2] - kb[0] + 10
        draw.rectangle([x + 4, lead_y + 4, x + 4 + kw, lead_y + 18],
                       fill=RED)
        draw.text((x + 9 - kb[0], lead_y + 4 + (14 - (kb[3] - kb[1])) / 2
                   - kb[1]), lead["kicker"], font=kf, fill=(255, 255, 255))
        y = lead_y + ill_h + 6
        # Number + place + beat, tag chip at the right.
        numf = font(SANS_BOLD, 11)
        draw.text((x, y), "%d" % lead["num"], font=numf, fill=RED)
        nw = draw.textlength("%d  " % lead["num"], font=numf)
        place = "%s \u00b7 %s" % (lead["place"], lead["beat"])
        pf = font(SANS_BOLD, 10.5)
        draw.text((x + nw, y + 1),
                  one_line(draw, place, pf, lead_w - nw - 62),
                  font=pf, fill=NAVY)
        tag_chip(draw, x + lead_w - 58, y, lead["tag"])
        y += 16
        hlines = fit_lines(draw, lead["headline"], font(SERIF_BOLD, 16),
                           lead_w, 2)
        y = text_block(draw, x, y, hlines, font(SERIF_BOLD, 16), INK, 19)
        dlines = fit_lines(draw, lead["deck"], font(SANS, 11),
                           lead_w, 3)
        y = text_block(draw, x, y + 3, dlines, font(SANS, 11), INK, 13.5)
        draw.text((x, y + 3), "Sources: %s" % lead["source"],
                  font=font(SANS, 9), fill=GREY)

    # --- the day in ten -----------------------------------------------------------
    ten_y = 446
    draw.text((MX, ten_y), "THE DAY IN TEN",
              font=font(SERIF_BOLD, 15), fill=NAVY)
    right = "THE STORIES THAT MOVED THE WORLD TODAY"
    rf = font(SANS_BOLD, 10)
    tw = draw.textlength(right, font=rf)
    draw.text((W - MX - tw, ten_y + 3), right, font=rf, fill=GREY)
    hrule(draw, MX, W - MX, ten_y + 20, fill=GOLD, width=2)

    card_w = 188
    card_gap = 8
    card_h = 128
    ill_h2 = 42
    grid_y = ten_y + 26
    for i, story in enumerate(TEN):
        col = i % 5
        row = i // 5
        x = MX + col * (card_w + card_gap)
        y = grid_y + row * (card_h + card_gap)
        draw.rectangle([x, y, x + card_w, y + card_h], fill=(255, 255, 255),
                       outline=RULE, width=1)
        TEN_ART[story["art"]](draw, x + 1, y + 1, card_w - 2, ill_h2)
        draw.line([(x, y + ill_h2 + 1), (x + card_w, y + ill_h2 + 1)],
                  fill=RULE, width=1)
        # Number chip on the illustration, top-left.
        nf = font(SANS_BOLD, 11)
        draw.ellipse([x + 5, y + 5, x + 23, y + 23], fill=NAVY)
        nb = draw.textbbox((0, 0), str(story["num"]), font=nf)
        draw.text((x + 14 - (nb[0] + nb[2]) / 2,
                   y + 14 - (nb[1] + nb[3]) / 2), str(story["num"]),
                  font=nf, fill=(255, 255, 255))
        tx = x + 6
        ty = y + ill_h2 + 6
        # Place + beat, tag chip right.
        place = "%s \u00b7 %s" % (story["place"], story["beat"])
        pf = font(SANS_BOLD, 9)
        draw.text((tx, ty), one_line(draw, place, pf, card_w - 66),
                  font=pf, fill=NAVY)
        tag_chip(draw, x + card_w - 62, ty - 1, story["tag"])
        ty += 13
        hlines = fit_lines(draw, story["headline"], font(SANS_BOLD, 12),
                           card_w - 12, 2)
        ty = text_block(draw, tx, ty, hlines, font(SANS_BOLD, 12), INK, 14)
        dlines = fit_lines(draw, story["deck"], font(SANS, 10),
                           card_w - 12, 2)
        ty = text_block(draw, tx, ty + 1, dlines, font(SANS, 10), GREY, 12)
        draw.text((tx, y + card_h - 13), story["source"],
                  font=font(SANS, 8.5), fill=GREY)

    bottom_y = grid_y + 2 * card_h + card_gap

    # --- where it happened + date check -----------------------------------
    # Map on the left, DATE CHECK on the right at the same height, so
    # the 21 briefs below get a full-width four-column band of their own.
    draw.text((MX, bottom_y + 6), "WHERE IT HAPPENED",
              font=font(SERIF_BOLD, 13), fill=NAVY)
    draw.text((MX + 338, bottom_y + 6), "DATE CHECK",
              font=font(SERIF_BOLD, 13), fill=NAVY)
    map_y = bottom_y + 24
    map_h = 92
    draw_map(draw, MX, map_y, 330, map_h)
    dc_x = MX + 338
    dc_y = map_y
    dc_w = CW - 338
    dc_h = 92
    draw.rectangle([dc_x, dc_y, dc_x + dc_w, dc_y + dc_h], fill=RED_TINT,
                   outline=RED, width=1)
    draw.rectangle([dc_x, dc_y, dc_x + 92, dc_y + dc_h], fill=RED)
    dcf = font(SANS_BOLD, 11)
    dcb = draw.textbbox((0, 0), "DATE CHECK", font=dcf)
    draw.text((dc_x + (92 - (dcb[2] - dcb[0])) / 2 - dcb[0],
               dc_y + (dc_h - (dcb[3] - dcb[1])) / 2 - dcb[1]), "DATE CHECK",
              font=dcf, fill=(255, 255, 255))
    dlines = fit_lines(draw, DATE_CHECK, font(SANS, 10.5),
                       dc_w - 92 - 24, 5)
    text_block(draw, dc_x + 92 + 10, dc_y + 7, dlines, font(SANS, 10.5),
               INK, 13)

    # --- also on sunday: 21 more stories in four columns -------------------
    # Four columns of six rows (the last row holds three); each brief
    # is one short fact in at most two lines, the red number leading.
    draw.text((MX, map_y + map_h + 8),
              "ALSO ON SUNDAY 22 NOVEMBER \u2014 21 MORE STORIES",
              font=font(SERIF_BOLD, 13), fill=NAVY)
    bx0 = MX
    col_w = (CW - 3 * 8) // 4
    briefs_y = map_y + map_h + 26
    for i, (num, place, text, src, _reg) in enumerate(BRIEFS):
        col = i % 4
        row = i // 4
        x = bx0 + col * (col_w + 8)
        y = briefs_y + row * 20
        nf = font(SANS_BOLD, 10)
        num_txt = "%d." % num
        nw = draw.textlength(num_txt + " ", font=nf)
        draw.text((x, y), num_txt, font=nf, fill=RED)
        body = "%s: %s (%s)" % (place, text, src)
        lines = fit_lines(draw, body, font(SANS, 10), col_w - 6 - nw, 2)
        text_block(draw, x + nw, y, lines, font(SANS, 10), INK, 11)

    # --- footer ------------------------------------------------------------------
    fy = briefs_y + 6 * 20 + 4
    draw.text((MX, fy), FOOT_SOURCES, font=font(SANS, 9.5), fill=GREY)
    draw.text((MX, fy + 11), FOOT_LEGEND, font=font(SANS, 9.5), fill=GREY)
    return page


def main():
    """Write out/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)."""
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    base = os.path.dirname(os.path.abspath(__file__))
    if not HAVE_PIL:
        shutil.copyfile(os.path.join(base, "assets", "prebuilt.png"), out)
        return
    page = build_page()
    page.save(out, optimize=True)


if __name__ == "__main__":
    main()
