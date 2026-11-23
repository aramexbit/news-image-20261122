"""Compose the 22 November 2026 one-page newspaper image.

Draws a dense broadsheet front page (1024x1024) from the two hero
photos in assets/ plus text drawn in code. Deterministic: no clock,
no randomness, no network. Requires Pillow; main.py falls back to
the prebuilt image when Pillow is missing.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 28  # side margin
CW = W - 2 * MX  # content width, 968

PAPER = (247, 241, 222)
PAPER_DARK = (238, 230, 205)
INK = (20, 20, 22)
NAVY = (20, 38, 74)
NAVY_SOFT = (43, 63, 105)
RED = (176, 30, 36)
RED_TINT = (251, 236, 236)
GOLD = (185, 138, 31)
GOLD_LIGHT = (232, 200, 106)
GREY = (90, 88, 80)
RULE = (120, 110, 88)

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


# ---------------------------------------------------------------- icons
# Small 24x24 glyphs drawn in code, one per featured story.

def _icon_base(draw, x, y, fill=NAVY):
    draw.rectangle([x, y, x + 23, y + 23], outline=fill, width=1)
    draw.rectangle([x + 1, y + 1, x + 22, y + 22], outline=GOLD, width=1)


def icon_quake(draw, x, y):
    _icon_base(draw, x, y)
    pts = [(x + 3, y + 16), (x + 8, y + 7), (x + 12, y + 15),
           (x + 16, y + 6), (x + 21, y + 14)]
    draw.line(pts, fill=RED, width=2)


def icon_missile(draw, x, y):
    _icon_base(draw, x, y)
    draw.line([(x + 5, y + 19), (x + 17, y + 6)], fill=NAVY, width=2)
    draw.polygon([(x + 17, y + 4), (x + 21, y + 8), (x + 16, y + 9)],
                 fill=RED)
    draw.line([(x + 4, y + 20), (x + 8, y + 16)], fill=GOLD, width=2)


def icon_quote(draw, x, y):
    _icon_base(draw, x, y)
    draw.ellipse([x + 5, y + 6, x + 10, y + 11], fill=NAVY)
    draw.polygon([(x + 5, y + 10), (x + 10, y + 10), (x + 6, y + 18)],
                 fill=NAVY)
    draw.ellipse([x + 14, y + 6, x + 19, y + 11], fill=NAVY)
    draw.polygon([(x + 14, y + 10), (x + 19, y + 10), (x + 15, y + 18)],
                 fill=NAVY)


def icon_eye(draw, x, y):
    _icon_base(draw, x, y)
    draw.ellipse([x + 4, y + 8, x + 20, y + 16], outline=NAVY, width=2)
    draw.ellipse([x + 10, y + 9, x + 14, y + 15], fill=RED)


def icon_border(draw, x, y):
    _icon_base(draw, x, y)
    for bx in (6, 11, 16):
        draw.line([(x + bx, y + 5), (x + bx, y + 19)], fill=NAVY, width=2)
    draw.line([(x + 4, y + 5), (x + 20, y + 5)], fill=NAVY, width=2)
    draw.line([(x + 4, y + 19), (x + 20, y + 19)], fill=NAVY, width=2)
    draw.line([(x + 4, y + 20), (x + 20, y + 4)], fill=RED, width=2)


def icon_terminal(draw, x, y):
    _icon_base(draw, x, y)
    draw.rectangle([x + 4, y + 5, x + 20, y + 19], outline=NAVY, width=1)
    draw.line([(x + 6, y + 9), (x + 10, y + 12), (x + 6, y + 15)],
              fill=RED, width=2)
    draw.line([(x + 12, y + 15), (x + 18, y + 15)], fill=NAVY, width=2)


def icon_shield(draw, x, y):
    _icon_base(draw, x, y)
    draw.polygon([(x + 12, y + 4), (x + 19, y + 7), (x + 19, y + 13),
                  (x + 12, y + 20), (x + 5, y + 13), (x + 5, y + 7)],
                 outline=NAVY, width=2)
    draw.ellipse([x + 10, y + 9, x + 14, y + 13], fill=RED)


def icon_globe(draw, x, y):
    _icon_base(draw, x, y)
    draw.ellipse([x + 4, y + 4, x + 20, y + 20], outline=NAVY, width=2)
    draw.ellipse([x + 9, y + 4, x + 15, y + 20], outline=NAVY, width=1)
    draw.line([(x + 4, y + 12), (x + 20, y + 12)], fill=NAVY, width=1)


def icon_scales(draw, x, y):
    _icon_base(draw, x, y)
    draw.line([(x + 12, y + 4), (x + 12, y + 19)], fill=NAVY, width=2)
    draw.line([(x + 5, y + 7), (x + 19, y + 7)], fill=NAVY, width=2)
    draw.polygon([(x + 3, y + 10), (x + 8, y + 10), (x + 5, y + 14)],
                 outline=RED, width=1)
    draw.polygon([(x + 16, y + 10), (x + 21, y + 10), (x + 18, y + 14)],
                 outline=RED, width=1)
    draw.line([(x + 7, y + 19), (x + 17, y + 19)], fill=NAVY, width=2)


def icon_cyclone(draw, x, y):
    _icon_base(draw, x, y)
    for r in (8, 5, 2):
        draw.arc([x + 12 - r, y + 12 - r, x + 12 + r, y + 12 + r],
                 start=40, end=300, fill=NAVY, width=2)
    draw.ellipse([x + 11, y + 11, x + 13, y + 13], fill=RED)


ICONS = [icon_quake, icon_missile, icon_quote, icon_eye, icon_border,
         icon_terminal, icon_shield, icon_globe, icon_scales, icon_cyclone]


# ------------------------------------------------------------------- map
# Simplified continent outlines as (lon, lat) points, equirectangular.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60),
     (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-58, 76)],
    # South America
    [(-80, 9), (-72, 12), (-60, 8), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -40),
     (-73, -20), (-80, -5), (-81, 5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -18),
     (32, -28), (20, -35), (15, -27), (12, -18), (9, -1), (9, 4),
     (-8, 4), (-13, 8)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65),
     (20, 70), (15, 70), (10, 62), (5, 60), (5, 58), (-5, 50), (-10, 44)],
    # Asia
    [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 52), (142, 50), (140, 40), (135, 35), (127, 35), (122, 30),
     (120, 22), (110, 20), (108, 12), (105, 8), (100, 6), (98, 10),
     (95, 15), (92, 21), (88, 22), (85, 19), (80, 13), (77, 8),
     (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (52, 28),
     (50, 30), (48, 30), (44, 29), (40, 32), (36, 36), (33, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
     (137, -35), (140, -38), (147, -39), (150, -37), (153, -27),
     (153, -22), (146, -19), (142, -11), (137, -12), (132, -12),
     (126, -14), (122, -17), (118, -20)],
    # South-East Asian islands
    [(95, -5), (105, -5), (110, -8), (100, -10)],
]

# Story number -> (lon, lat, nudge_x, nudge_y) for the map dots.
DOTS = [
    (1, -77, -10, 0, 0),     # Peru
    (2, 19, 52, 0, 0),       # Poland
    (3, 30, 50, 7, 3),       # Kyiv
    (4, 12, 55, -8, -5),     # Copenhagen
    (5, 25, 59, 0, -8),      # Estonia
    (6, -77, 39, -8, 6),     # Washington
    (7, -75, 45, 2, -8),     # Ottawa
    (8, 114, 22, 0, 0),      # Shenzhen
    (9, 96, 21, -10, 8),     # Myanmar
    (10, 85, 20, 8, -6),      # Odisha
]


def draw_map(draw, x0, y0, w, h):
    """Rough world map with numbered dots 1-10 for the big stories."""
    lon0, lon1 = -170.0, 190.0
    lat0, lat1 = 72.0, -58.0
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(223, 232, 238),
                   outline=RULE, width=1)
    for lon in range(-150, 181, 30):
        gx = x0 + (lon - lon0) / (lon1 - lon0) * w
        draw.line([(gx, y0), (gx, y0 + h)], fill=(210, 220, 228), width=1)
    for lat in range(-50, 71, 25):
        gy = y0 + (lat0 - lat) / (lat0 - lat1) * h
        draw.line([(x0, gy), (x0 + w, gy)], fill=(210, 220, 228), width=1)

    def px(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)

    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(196, 205, 178), outline=(110, 118, 96))
    for num, lon, lat, nx, ny in DOTS:
        cx, cy = px(lon, lat)
        cx += nx
        cy += ny
        r = 7 if num < 10 else 8
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        label = str(num)
        tw = draw.textlength(label, font=font(SANS_BOLD, 9))
        draw.text((cx - tw / 2, cy - 5), label, font=font(SANS_BOLD, 9),
                  fill=(255, 255, 255))


# ------------------------------------------------------------- hero cards
def paste_hero(draw, page, path, x, y, w, h, kicker, headline):
    """Paste a hero photo and caption it with a dark band at the bottom."""
    photo = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    page.paste(photo, (x, y))
    band = Image.new("RGBA", (w, 68), (10, 12, 20, 205))
    page.paste(band, (x, y + h - 68), band)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)
    draw.text((x + 10, y + h - 62), kicker, font=font(SANS_BOLD, 12),
              fill=GOLD_LIGHT)
    lines = fit_lines(draw, headline, font(SANS_BOLD, 17), w - 20, 2)
    text_block(draw, x + 10, y + h - 44, lines, font(SANS_BOLD, 17),
               (255, 255, 255), 20)


# ---------------------------------------------------------------- content
FEATURED = [
    ("M6.9 QUAKE SHAKES PERU'S ANDES",
     "Epicentre 34 km north of Junin, 108 km deep; felt in Lima."),
    ("RUSSIAN MISSILE FALLS IN POLAND",
     "PM Tusk: 'intentional provocation'; NATO: 'grave violation'."),
    ("ZELENSKYY: PUTIN 'A KILLER'",
     "Trump called Putin a friend; Kyiv hit the Crimea bridge."),
    ("DENMARK: PLOT TO KILL RAPPER",
     "Russian intelligence accused of plotting to kill a rapper."),
    ("ESTONIA SHUTS BORDER WITH RUSSIA",
     "Crossings closed over suspected sabotage; Moscow objects."),
    ("FBI PROBES HACK OF CRIME DATABASE",
     "Investigators examine a suspected breach of the database."),
    ("PENTAGON LIMITS U.S.-CANADA TIES",
     "Hegseth memo curbs informal meetings of U.S., Canadian troops."),
    ("TRUMP, XI AND PUTIN MEET IN SHENZHEN",
     "First trilateral summit: 4-point peace plan, no Ukraine result."),
    ("ICJ: MYANMAR COMMITTED GENOCIDE",
     "Historic Hague ruling: genocide against the Rohingya."),
    ("CYCLONE AKVAN HITS INDIA'S EAST COAST",
     "Landfall in Odisha-Andhra Pradesh; 300,000 evacuated."),
]

BRIEFS = [
    "S. Africa: ANC struggles to hold big cities.",
    "Mamdani plans to close Rikers Island prison.",
    "Nepal PM Balendra Shah visits India, meets Modi.",
    "India vs New Zealand, 1st Test in Wellington.",
    "Australia end England's seven straight T20 wins.",
    "Modi inaugurates Nitish Setu, Patna-Vaishali.",
    "Prince William: insurance for 10,000 forest staff.",
    "Air India extends Jeddah suspension to 24 Nov.",
    "Israel accuses Hamas of tightening grip on Gaza.",
    "France, U.S. back UN plan for post-UNIFIL vacuum.",
    "Finland: drone attack on Russian ship in Baltic.",
    "Basra power plant fire: 4 dead, 35 injured.",
    "Sudan pushes peace from within.",
    "$7.25bn Roundup settlement approved by U.S. court.",
    "Man guilty of starting 2025 Palisades fire.",
    "Trump shares senator's 'TrumpCare' plan.",
    "Trump accuses Tehran of violating MOU.",
    "UK-EU trade summit in Brussels (PM Burnham).",
    "Crude oil down more than 3%.",
    "Trump threatens ban on U.S. firms' AI centres abroad.",
    "ADNOC ship attacked in Hormuz; 1 crew missing.",
    "El Chapo Isidro arrested by Mexican army.",
    "Nikhil Gupta jailed ~19 years over Pannun plot.",
]

NUMBERS = [
    ("-3.7%", "S&P 500, Fri 20 Nov"),
    ("-950", "Dow points, Fri 20 Nov"),
    ("35.89", "VIX fear gauge"),
    ("M6.9", "Peru quake, 20 Nov"),
    ("300,000", "evacuated, Cyclone Akvan"),
    ("30+", "strikes on Ali Al Salem"),
]


# ------------------------------------------------------------ page build
HERO_LEFT = (
    "GULF WAR WIDENS: IRAN HITS U.S. BASES IN KUWAIT AND BAHRAIN",
    "Iran fired drones at the U.S. Ali Al Salem base in Kuwait and struck "
    "Bahrain on 18-19 Nov, answering U.S. strikes on Revolutionary Guard "
    "missile sites on Qeshm Island. Kuwait intercepted the drones; no "
    "casualties. Bahrain, home to the U.S. 5th Fleet, was hit four times "
    "in six days.",
)
HERO_RIGHT = (
    "COP31 DEADLOCKED AS CLIMATE TALKS RUN INTO OVERTIME",
    "Climate talks in Turkey have failed to reach a final deal on fossil "
    "fuels and are running into overtime, with negotiators still "
    "deadlocked. A separate deal on artificial intelligence also fell "
    "short, failing to attract the big U.S. tech companies.",
)


def build_page(base_dir):
    """Render the full front page and return the PIL image."""
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # --- masthead ------------------------------------------------------
    hrule(draw, MX, W - MX, 10, fill=GOLD, width=2)
    title = "THE WORLD TODAY"
    tf = font(SERIF_BOLD, 56)
    tw = draw.textlength(title, font=tf)
    draw.text(((W - tw) / 2, 16), title, font=tf, fill=NAVY)
    tag = "One day's news, summed up on a single page"
    tagf = font(SERIF_ITALIC, 14)
    tw = draw.textlength(tag, font=tagf)
    draw.text(((W - tw) / 2, 80), tag, font=tagf, fill=GREY)
    hrule(draw, MX, W - MX, 102, fill=NAVY, width=1)
    hrule(draw, MX, W - MX, 106, fill=NAVY, width=1)
    date = "SUNDAY 22 NOVEMBER 2026"
    df = font(SERIF_BOLD, 25)
    tw = draw.textlength(date, font=df)
    draw.text(((W - tw) / 2, 112), date, font=df, fill=NAVY)
    small = font(SANS_BOLD, 12)
    draw.text((MX, 119), "VOL. I - No. 22", font=small, fill=NAVY)
    right = "ONE PAGE - ALL THE NEWS"
    tw = draw.textlength(right, font=small)
    draw.text((W - MX - tw, 119), right, font=small, fill=NAVY)
    hrule(draw, MX, W - MX, 146, fill=NAVY, width=3)

    # --- hero photos ----------------------------------------------------
    hw = (CW - 8) // 2
    hh = 260
    paste_hero(draw, page, os.path.join(base_dir, "assets", "hero_gulf.jpg"),
               MX, 154, hw, hh, "THE GULF - WAR, MONTH 9",
               "Drones over Kuwait: air defences fire as the Gulf war widens")
    paste_hero(draw, page, os.path.join(base_dir, "assets", "hero_cop31.jpg"),
               MX + hw + 8, 154, hw, hh, "CLIMATE - COP31, TURKEY",
               "Deadlocked in overtime: no fossil-fuel deal in sight")

    # --- hero story text -------------------------------------------------
    for col, (head, body) in enumerate((HERO_LEFT, HERO_RIGHT)):
        x = MX + col * (hw + 8)
        hlines = fit_lines(draw, head, font(SERIF_BOLD, 19), hw, 2)
        y = text_block(draw, x, 422, hlines, font(SERIF_BOLD, 19), NAVY, 21)
        blines = fit_lines(draw, body, font(SANS, 13), hw, 5)
        text_block(draw, x, y + 3, blines, font(SANS, 13), INK, 15)

    # --- markets strip ----------------------------------------------------
    draw.rectangle([MX, 546, W - MX, 604], fill=RED_TINT, outline=RED, width=1)
    draw.rectangle([MX, 546, MX + 6, 604], fill=RED)
    draw.text((MX + 16, 552), "WALL STREET PLUNGES",
              font=font(SERIF_BOLD, 19), fill=RED)
    mlines = [
        "S&P 500 -3.7%, its 7th straight down day  |  Dow -950  |  "
        "Nasdaq -5.3%, worst week since 2020",
        "Nvidia -14% as CEO Jensen Huang resigns  |  Anthropic -9% after "
        "its $83bn IPO  |  $8.7tn gone since 6 Oct  |  VIX 35.89",
    ]
    text_block(draw, MX + 16, 576, mlines, font(SANS, 12), INK, 14)
    # seven descending bars: the S&P's seven straight down days
    bars = [30, 26, 22, 19, 15, 12, 9]
    bx = W - MX - 8 - len(bars) * 13
    for i, bh in enumerate(bars):
        x0 = bx + i * 13
        draw.rectangle([x0, 600 - bh, x0 + 9, 600], fill=RED)
    blab = "S&P: 7 down days"
    tw = draw.textlength(blab, font=font(SANS_BOLD, 9))
    draw.text((W - MX - 8 - tw, 552), blab, font=font(SANS_BOLD, 9),
              fill=RED)

    # --- featured stories --------------------------------------------------
    draw.text((MX, 612), "THE DAY'S BIG STORIES",
              font=font(SERIF_BOLD, 16), fill=NAVY)
    hrule(draw, MX, W - MX, 632, fill=GOLD, width=2)
    row_h = 34
    for i, (head, sub) in enumerate(FEATURED):
        col = i % 2
        row = i // 2
        x = MX + col * (hw + 8)
        y = 638 + row * row_h
        num = str(i + 1)
        draw.ellipse([x, y + 2, x + 20, y + 22], fill=NAVY)
        tw = draw.textlength(num, font=font(SANS_BOLD, 11))
        draw.text((x + 10 - tw / 2, y + 6), num, font=font(SANS_BOLD, 11),
                  fill=(255, 255, 255))
        ICONS[i](draw, x + 26, y + 2)
        tx = x + 58
        twd = hw - 58
        draw.text((tx, y), one_line(draw, head, font(SANS_BOLD, 14), twd),
                  font=font(SANS_BOLD, 14), fill=INK)
        draw.text((tx, y + 17), one_line(draw, sub, font(SANS, 11.5), twd),
                  font=font(SANS, 11.5), fill=GREY)

    # --- map + briefs -------------------------------------------------------
    hrule(draw, MX, W - MX, 806, fill=NAVY, width=1)
    secf = font(SERIF_BOLD, 14)
    draw.text((MX, 812), "WHERE IT HAPPENED", font=secf, fill=NAVY)
    draw.text((MX + 316, 812), "THE DAY IN BRIEF", font=secf, fill=NAVY)
    draw_map(draw, MX, 830, 300, 108)
    leg = "Dots 1-10 match the big stories above."
    draw.text((MX, 942), leg, font=font(SANS, 9), fill=GREY)
    bx0 = MX + 316
    col_w = (CW - 316) // 2
    for i, item in enumerate(BRIEFS):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x = bx0 + col * col_w
        y = 830 + row * 11
        num = str(i + 1) + "."
        draw.text((x, y), num, font=font(SANS_BOLD, 11), fill=RED)
        nw = draw.textlength(num + " ", font=font(SANS_BOLD, 11))
        draw.text((x + nw, y),
                  one_line(draw, item, font(SANS, 11), col_w - nw - 4),
                  font=font(SANS, 11), fill=INK)

    # --- the day in numbers ---------------------------------------------------
    nbox_w = (CW - 5 * 6) // 6
    for i, (val, lab) in enumerate(NUMBERS):
        x = MX + i * (nbox_w + 6)
        draw.rectangle([x, 966, x + nbox_w, 992], fill=PAPER_DARK,
                       outline=RULE, width=1)
        vf = font(SANS_BOLD, 14)
        tw = draw.textlength(val, font=vf)
        draw.text((x + (nbox_w - tw) / 2, 969), val, font=vf, fill=RED)
        lf = font(SANS, 9)
        tw = draw.textlength(lab, font=lf)
        draw.text((x + (nbox_w - tw) / 2, 983), lab, font=lf, fill=GREY)

    # --- footer ----------------------------------------------------------------
    foot1 = ("Sources: AP, Reuters, AFP, BBC, The Guardian, Bloomberg, "
             "Al Jazeera, Hindustan Times - reports of 18-22 Nov 2026.")
    foot2 = ("Hero images are AI-generated illustrations. Disputed claims "
             "are attributed in the text. The World Today is a one-day news "
             "summary, not a real newspaper.")
    draw.text((MX, 998), foot1, font=font(SANS, 9.5), fill=GREY)
    draw.text((MX, 1009), foot2, font=font(SANS, 9.5), fill=GREY)
    return page
