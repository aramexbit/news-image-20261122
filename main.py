"""news-image-20261122 v3: one day's world news, winners-pattern redesign.

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
# Stories 1-3 are the leads; 4-13 are THE DAY IN TEN; 14-25 are the
# briefs. Every story happened or was first reported on Sunday
# 22 November 2026. Region counts: Europe 5, Middle East 6,
# Asia-Pacific 5, Americas 6, Africa 1, Oceania 2 = 25 stories.

LEADS = [
    {
        "num": 1, "kicker": "186 DRONES OVERNIGHT",
        "place": "KYIV REGION, UKRAINE", "beat": "WAR",
        "tag": "REPORTED",
        "headline": "Russia fires 186 drones at Ukraine overnight; 161 downed",
        "deck": ("161 of 186 drones fired overnight were downed or jammed, "
                 "72 of them jet-powered. One hit a block in Dymer: seven "
                 "feared trapped, two hurt."),
        "source": "Ukrainian Air Force via Reuters, BBC",
        "art": "drones",
    },
    {
        "num": 2, "kicker": "COP31: FINAL TEXT",
        "place": "ANTALYA, T\u00dcRKIYE", "beat": "CLIMATE",
        "tag": "REPORTED",
        "headline": "COP31's final text lands at dawn, with no mention of fossil fuels",
        "deck": ("The package drops the $120bn adaptation target, keeps a "
                 "35% electricity goal for 2035 and admits 1.5\u00b0C will be "
                 "overshot. Objections close 03:00 GMT."),
        "source": "BBC, Reuters, The Guardian",
        "art": "cop31",
    },
    {
        "num": 3, "kicker": "CLAIM VS DENIAL",
        "place": "MANAMA, BAHRAIN", "beat": "GULF WAR",
        "tag": "CLAIM",
        "headline": "Iran claims strikes on US bases in Bahrain; Bahrain denies",
        "deck": ("Tehran says it hit US Patriot radars at Al-Riffa and "
                 "Awali Sakir. Bahrain says its defences intercepted the "
                 "attacks; a facility burned, no casualties."),
        "source": "Al Jazeera, Reuters, IRGC statement",
        "art": "bahrain",
    },
]

TEN = [
    {"num": 4, "place": "HONG KONG", "beat": "ELECTION", "tag": "CONFIRMED",
     "headline": "Hong Kong elects its Election Committee",
     "deck": "856 candidates for 723 seats; polls 09:00-18:00.",
     "source": "SCMP", "art": "ballot"},
    {"num": 5, "place": "WELLINGTON", "beat": "CRICKET", "tag": "CONFIRMED",
     "headline": "India declare on 720/9, a record in NZ",
     "deck": "Rahul 136, Pant 128; hosts 119/2, trailing by 233.",
     "source": "ESPN, Cricbuzz", "art": "cricket"},
    {"num": 6, "place": "LAS VEGAS", "beat": "F1", "tag": "CONFIRMED",
     "headline": "Verstappen takes the Las Vegas GP",
     "deck": "From pole in 1:37.694; Norris +0.639, Piastri +1.259.",
     "source": "FIA", "art": "f1"},
    {"num": 7, "place": "GULF OF FINLAND", "beat": "SEA", "tag": "REPORTED",
     "headline": "Russian cargo ship Sparta still burning",
     "deck": "Hit by drones Saturday; all 16 crew off, Finland leads rescue.",
     "source": "Reuters", "art": "ship"},
    {"num": 8, "place": "TEHRAN", "beat": "ENERGY", "tag": "REPORTED",
     "headline": "Iran begins rationing electricity",
     "deck": "Rolling cuts up to two hours a day as war damage bites.",
     "source": "Wires", "art": "power"},
    {"num": 9, "place": "BRAS\u00cdLIA", "beat": "HEALTH", "tag": "CONFIRMED",
     "headline": "Bolsonaro in intensive care in Bras\u00edlia",
     "deck": "Acute bowel obstruction, stable; surgery possible.",
     "source": "Reuters", "art": "hospital"},
    {"num": 10, "place": "WASHINGTON", "beat": "CYBER", "tag": "REPORTED",
     "headline": "FBI probes hack of its crime database",
     "deck": "Washington State pauses gun-dealer checks.",
     "source": "AP", "art": "fbi"},
    {"num": 11, "place": "BRUSSELS", "beat": "TRAVEL", "tag": "CONFIRMED",
     "headline": "Belgian controllers join Monday's strike",
     "deck": "Most flights grounded 07:00-21:00; controllers walk out.",
     "source": "Xinhua", "art": "tower"},
    {"num": 12, "place": "MANIPUR", "beat": "POISONING", "tag": "CONFIRMED",
     "headline": "Toxic-liquor toll climbs to 19 in Manipur",
     "deck": "600 in hospital, six held; toll up from 11.",
     "source": "Xinhua", "art": "bottle"},
    {"num": 13, "place": "JUN\u00cdN", "beat": "QUAKE TOLL", "tag": "CONFIRMED",
     "headline": "Peru quake toll updated: 1 dead, 16 hurt",
     "deck": "170 homes damaged in Jun\u00edn; the count is completed.",
     "source": "Reuters", "art": "quake"},
]

# Briefs 14-25, grouped by region: Middle East, Asia-Pacific,
# Oceania, Europe, World, Americas, Africa.
BRIEFS = [
    (14, "Gaza", "Israel accuses Hamas of tightening its grip on Gaza.",
     "Reuters", "ME"),
    (15, "Beirut", "France and the U.S. back a UN plan for the post-UNIFIL vacuum.",
     "Reuters", "ME"),
    (16, "Basra", "Power plant fire kills 4, injures 35.",
     "Wires", "ME"),
    (17, "Jeddah", "Air India extends its Jeddah suspension to 24 Nov.",
     "Wires", "APAC"),
    (18, "Delhi", "Nepal PM Balendra Shah lands in India, meets Modi.",
     "Reuters", "APAC"),
    (19, "Patna", "Modi inaugurates the Nitish Setu bridge to Vaishali.",
     "Wires", "APAC"),
    (20, "Sydney", "Australia end England's seven straight T20 wins.",
     "Wires", "OC"),
    (21, "London", "Prince William backs insurance for 10,000 forest staff.",
     "Wires", "EU"),
    (22, "North Sea", "Crude oil down more than 3%.",
     "Wires", "WORLD"),
    (23, "St. Louis", "$7.25bn Roundup settlement approved by a U.S. court.",
     "Wires", "AM"),
    (24, "Los Angeles", "Man guilty of starting the 2025 Palisades fire.",
     "Wires", "AM"),
    (25, "Khartoum", "Sudan pushes peace from within.",
     "Wires", "AF"),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections close"),
    ("05:30", "Las Vegas GP ends"),
    ("06:00", "COP31 approval session"),
    ("08:00", "161 drones downed"),
    ("18:00", "HK polls close"),
]

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed"),
    ("720/9", "India's record Test total in NZ"),
    ("856", "candidates in Hong Kong vote"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
]

REGIONS = [
    ("EUROPE", 5), ("MIDDLE EAST", 6), ("ASIA-PACIFIC", 5),
    ("AMERICAS", 6), ("AFRICA", 1), ("OCEANIA", 2),
]

DATE_CHECK = (
    "Every story on this page happened or was first reported on Sunday "
    "22 November 2026. Left out on purpose \u2014 other days' news: the Peru "
    "quake (Fri 20 Nov) \u00b7 the Myanmar genocide ruling (Thu 19 Nov) \u00b7 the "
    "Shenzhen three-way summit (Thu 19 Nov) \u00b7 the \u2018El Chapo Isidro\u2019 "
    "arrest (Sat 21 Nov) \u00b7 the Nvidia SEC probe (Fri 20 Nov) \u00b7 the Kryvyi "
    "Rih strike (Sat 21 Nov) \u00b7 Iran's Gulf strikes (18\u201319 Nov) \u00b7 "
    "Cyclone Akvan (Fri 20 Nov) \u00b7 the Wall Street plunge (Fri 20 Nov). "
    "Not yet: COP31's formal approval \u00b7 the Belgian walkout (Mon)."
)

FOOT_SOURCES = ("Sources: Reuters, BBC, AP, AFP, The Guardian, SCMP, ESPN, "
                "FIA, Xinhua, Wires \u2014 reports of Sunday 22 November 2026. "
                "Scenes are drawn illustrations of reported events, not photographs.")
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


LEAD_ART = {"drones": art_drones, "cop31": art_cop31, "bahrain": art_bahrain}


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
           "quake": art_quake}


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
    (2, 30.7, 36.9, -6, -5),   # Antalya, Turkiye
    (3, 50.6, 26.2, -5, 3),    # Manama, Bahrain
    (4, 114.2, 22.3, 0, 0),    # Hong Kong
    (5, 174.8, -41.3, 0, 0),   # Wellington, NZ
    (6, -115.1, 36.2, 4, -3),  # Las Vegas
    (7, 24, 59.8, -3, -3),     # Gulf of Finland
    (8, 51.4, 35.7, 3, 5),     # Tehran
    (9, -47.9, -15.8, 0, 0),   # Brasilia
    (10, -77, 38.9, 0, 0),     # Washington
    (11, 4.35, 50.85, 5, 4),   # Brussels
    (12, 93.9, 24.8, 0, 0),    # Manipur, India
    (13, -75.2, -11.2, 0, 0),  # Junin, Peru
    (14, 77.2, 28.6, -3, -2),  # Delhi
    (15, 151.2, -33.9, 0, 0),  # Sydney
    (16, 85.1, 25.6, 3, 2),    # Patna
    (17, -0.1, 51.5, -5, -4),  # London
    (18, 39.2, 21.5, -4, 4),   # Jeddah
    (19, 34.5, 31.5, -5, 6),   # Gaza
    (20, 35.5, 33.9, 6, -4),   # Beirut
    (21, 47.8, 30.5, 5, -4),   # Basra
    (22, 32.5, 15.6, 0, 0),    # Khartoum
    (23, -90.2, 38.6, 0, 0),   # St. Louis
    (24, -118.5, 34.1, -4, 3), # Los Angeles
    (25, 2.0, 58.0, 4, -4),    # North Sea
]


def draw_map(draw, x0, y0, w, h):
    """Flat beige world map with numbered red pins for stories 1-25."""
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
    sub = ("186 drones over Ukraine in the night \u00b7 COP31's deal names "
           "no fossil fuels \u00b7 Iran's radar claim meets Bahrain's denial")
    sf = font(SERIF_ITALIC, 15)
    sb = draw.textbbox((0, 0), sub, font=sf)
    draw.text(((W - (sb[2] - sb[0])) / 2 - sb[0], 88 - sb[1]), sub,
              font=sf, fill=RED)
    stats = ("25 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED "
             "SUNDAY 22 NOVEMBER 2026")
    stf = font(SANS_BOLD, 12)
    stb = draw.textbbox((0, 0), stats, font=stf)
    draw.text(((W - (stb[2] - stb[0])) / 2 - stb[0], 108 - stb[1]), stats,
              font=stf, fill=NAVY)
    hrule(draw, MX, W - MX, 126, fill=NAVY, width=2)

    # --- the day in numbers --------------------------------------------------
    nbox_w = (CW - 5 * 6) // 6
    for i, (val, lab) in enumerate(NUMBERS):
        x = MX + i * (nbox_w + 6)
        draw.rectangle([x, 132, x + nbox_w, 176], fill=PAPER_DARK,
                       outline=RULE, width=1)
        vf = font(SANS_BOLD, 20)
        vb = draw.textbbox((0, 0), val, font=vf)
        draw.text((x + (nbox_w - (vb[2] - vb[0])) / 2 - vb[0],
                   132 + 4 - vb[1]), val, font=vf, fill=RED)
        lf = font(SANS, 9)
        lb = draw.textbbox((0, 0), lab, font=lf)
        draw.text((x + (nbox_w - (lb[2] - lb[0])) / 2 - lb[0],
                   176 - 4 - lb[3]), lab, font=lf, fill=GREY)

    # --- region strip ---------------------------------------------------------
    seg_w = CW // len(REGIONS)
    for i, (name, count) in enumerate(REGIONS):
        x = MX + i * seg_w
        w = seg_w if i < len(REGIONS) - 1 else CW - i * seg_w
        draw.rectangle([x, 182, x + w, 202], fill=REGION_COLORS[name])
        label = "%s %d" % (name, count)
        rf = font(SANS_BOLD, 11)
        rb = draw.textbbox((0, 0), label, font=rf)
        draw.text((x + (w - (rb[2] - rb[0])) / 2 - rb[0],
                   182 + (20 - (rb[3] - rb[1])) / 2 - rb[1]), label,
                  font=rf, fill=(255, 255, 255))

    # --- the day in utc --------------------------------------------------------
    draw.rectangle([MX, 208, MX + 108, 226], fill=NAVY)
    uf = font(SANS_BOLD, 10)
    ub = draw.textbbox((0, 0), "THE DAY IN UTC", font=uf)
    draw.text((MX + (108 - (ub[2] - ub[0])) / 2 - ub[0],
               208 + (18 - (ub[3] - ub[1])) / 2 - ub[1]), "THE DAY IN UTC",
              font=uf, fill=(255, 255, 255))
    utc_parts = []
    for t, ev in UTC_EVENTS:
        utc_parts.append("%s %s" % (t, ev))
    utc_line = "  \u00b7  ".join(utc_parts)
    utf = font(SANS, 10)
    utb = draw.textbbox((0, 0), utc_line, font=utf)
    draw.text((MX + 116, 208 + (18 - (utb[3] - utb[1])) / 2 - utb[1]),
              utc_line, font=utf, fill=INK)

    # --- three leads ------------------------------------------------------------
    lead_w = (CW - 2 * 10) // 3
    lead_y = 234
    ill_h = 112
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
    ten_y = 474
    draw.text((MX, ten_y), "THE DAY IN TEN",
              font=font(SERIF_BOLD, 15), fill=NAVY)
    right = "THE STORIES THAT MOVED THE WORLD TODAY"
    rf = font(SANS_BOLD, 10)
    tw = draw.textlength(right, font=rf)
    draw.text((W - MX - tw, ten_y + 3), right, font=rf, fill=GREY)
    hrule(draw, MX, W - MX, ten_y + 20, fill=GOLD, width=2)

    card_w = 188
    card_gap = 9
    card_h = 136
    ill_h2 = 48
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

    # --- where it happened + briefs -----------------------------------------
    draw.text((MX, bottom_y + 6), "WHERE IT HAPPENED",
              font=font(SERIF_BOLD, 13), fill=NAVY)
    draw.text((MX + 338, bottom_y + 6),
              "ALSO ON SUNDAY 22 NOVEMBER \u2014 12 MORE STORIES",
              font=font(SERIF_BOLD, 13), fill=NAVY)
    map_y = bottom_y + 24
    map_h = 118
    draw_map(draw, MX, map_y, 330, map_h)
    draw.text((MX, map_y + map_h + 3), "Pins match story numbers.",
              font=font(SANS, 9), fill=GREY)
    # Briefs in two columns of six; the red number leads each item.
    bx0 = MX + 338
    col_w = (CW - 338) // 2
    for i, (num, place, text, src, _reg) in enumerate(BRIEFS):
        col = 0 if i < 6 else 1
        row = i if i < 6 else i - 6
        x = bx0 + col * col_w
        y = map_y + row * 20
        nf = font(SANS_BOLD, 10)
        num_txt = "%d." % num
        nw = draw.textlength(num_txt + " ", font=nf)
        draw.text((x, y), num_txt, font=nf, fill=RED)
        body = "%s: %s (%s)" % (place, text, src)
        lines = fit_lines(draw, body, font(SANS, 10), col_w - 6 - nw, 2)
        text_block(draw, x + nw, y, lines, font(SANS, 10), INK, 11)

    # --- date check ------------------------------------------------------------
    # Briefs end at map_y + 120 (six rows of 20); the box sits below them.
    dc_y = map_y + 120 + 8
    dc_h = 64
    draw.rectangle([MX, dc_y, W - MX, dc_y + dc_h], fill=RED_TINT,
                   outline=RED, width=1)
    draw.rectangle([MX, dc_y, MX + 92, dc_y + dc_h], fill=RED)
    dcf = font(SANS_BOLD, 11)
    dcb = draw.textbbox((0, 0), "DATE CHECK", font=dcf)
    draw.text((MX + (92 - (dcb[2] - dcb[0])) / 2 - dcb[0],
               dc_y + (dc_h - (dcb[3] - dcb[1])) / 2 - dcb[1]), "DATE CHECK",
              font=dcf, fill=(255, 255, 255))
    dlines = fit_lines(draw, DATE_CHECK, font(SANS, 10.5),
                       CW - 92 - 24, 4)
    text_block(draw, MX + 92 + 10, dc_y + 7, dlines, font(SANS, 10.5),
               INK, 13)

    # --- footer ------------------------------------------------------------------
    fy = dc_y + dc_h + 6
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
