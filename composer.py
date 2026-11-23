"""Compose the 22 November 2026 one-page newspaper image.

Draws a dense broadsheet front page (1024x1024) from the two hero
photos in assets/ plus text drawn in code. Deterministic: no clock,
no randomness, no network. Requires Pillow; main.py falls back to
the prebuilt image when Pillow is missing.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
    # North America: Alaska, Arctic coast with a Hudson Bay dent,
    # Labrador, Florida, Gulf coast, Mexico, Central America.
    [(-168, 66), (-163, 60), (-156, 58), (-149, 60), (-142, 60),
     (-136, 58), (-131, 55), (-127, 51), (-124, 44), (-121, 36),
     (-116, 31), (-112, 28), (-109, 24), (-106, 21), (-101, 18),
     (-95, 18), (-91, 15), (-87, 13), (-83, 9), (-79, 9), (-80, 13),
     (-84, 16), (-87, 21), (-90, 21), (-91, 19), (-96, 19), (-97, 24),
     (-94, 29), (-90, 30), (-85, 30), (-82, 28), (-80, 26), (-80, 31),
     (-76, 35), (-75, 38), (-73, 41), (-70, 42), (-68, 44), (-65, 44),
     (-60, 46), (-56, 50), (-59, 54), (-62, 57), (-66, 59), (-70, 61),
     (-76, 62), (-80, 63), (-83, 58), (-85, 56), (-88, 58), (-91, 61),
     (-94, 65), (-98, 67), (-105, 68), (-115, 69), (-125, 70),
     (-135, 69), (-148, 70), (-158, 71), (-165, 69)],
    # Greenland
    [(-46, 60), (-42, 64), (-36, 66), (-30, 68), (-24, 70), (-20, 73),
     (-25, 76), (-32, 77), (-42, 78), (-52, 77), (-58, 75), (-57, 71),
     (-54, 67), (-50, 63)],
    # South America: Caribbean coast, Brazilian bulge, taper to the south.
    [(-77, 7), (-74, 10), (-70, 11), (-64, 10), (-59, 8), (-54, 6),
     (-51, 4), (-50, 0), (-46, -2), (-41, -4), (-36, -7), (-35, -9),
     (-37, -12), (-39, -16), (-40, -20), (-42, -23), (-46, -25),
     (-49, -28), (-52, -32), (-55, -35), (-58, -38), (-62, -40),
     (-65, -43), (-67, -47), (-69, -50), (-70, -53), (-72, -54),
     (-73, -50), (-73, -45), (-73, -40), (-72, -35), (-71, -30),
     (-70, -25), (-70, -20), (-73, -16), (-76, -13), (-79, -8),
     (-81, -5), (-81, -1), (-80, 2), (-78, 5)],
    # Africa: west bulge, Mediterranean coast, Horn, southern taper.
    [(-17, 15), (-16, 19), (-15, 23), (-14, 27), (-11, 30), (-7, 33),
     (-4, 35), (0, 36), (5, 37), (9, 37), (11, 34), (15, 32), (19, 32),
     (23, 32), (27, 31), (30, 31), (32, 31), (34, 28), (36, 25),
     (37, 22), (38, 19), (40, 16), (41, 13), (43, 12), (46, 11),
     (48, 11), (51, 11), (51, 8), (50, 4), (48, 0), (46, -3), (43, -7),
     (40, -10), (39, -14), (37, -18), (35, -21), (34, -25), (32, -28),
     (30, -31), (27, -33), (23, -34), (19, -35), (17, -33), (15, -30),
     (14, -26), (13, -22), (12, -18), (12, -14), (12, -10), (12, -6),
     (10, -2), (9, 1), (9, 4), (6, 4), (3, 6), (-1, 5), (-5, 5),
     (-8, 4), (-11, 6), (-13, 8), (-15, 11)],
    # Madagascar
    [(44, -16), (46, -15), (49, -16), (50, -18), (49, -21), (47, -24),
     (45, -25), (43, -22), (43, -19)],
    # Europe: Iberia, Brittany, Low Countries, Jutland, Norway, North
    # Cape, down the Russian west to the Caucasus, Black Sea north
    # coast, Greece, Adriatic, the Italian boot, back along the Med.
    [(-9, 37), (-9, 41), (-9, 43), (-5, 44), (-2, 44), (-2, 47),
     (-1, 49), (0, 50), (2, 51), (4, 52), (6, 54), (8, 55), (8, 57),
     (10, 58), (8, 59), (6, 60), (5, 61), (6, 62), (8, 63), (11, 65),
     (13, 67), (16, 68), (19, 70), (23, 71), (27, 71), (30, 70),
     (31, 69), (32, 67), (33, 65), (34, 63), (35, 61), (36, 59),
     (38, 57), (40, 55), (42, 53), (43, 51), (44, 49), (43, 47),
     (41, 45), (39, 47), (36, 46), (33, 46), (30, 46), (28, 44),
     (27, 42), (26, 40), (24, 39), (23, 37), (22, 38), (21, 39),
     (20, 41), (19, 42), (18, 44), (16, 44), (14, 45), (15, 43),
     (16, 42), (17, 41), (18, 40), (17, 39), (16, 38), (15, 39),
     (15, 41), (14, 42), (13, 44), (11, 44), (9, 44), (7, 44), (6, 43),
     (4, 43), (3, 42), (2, 41), (0, 39), (-1, 38), (-3, 37), (-5, 36),
     (-7, 36)],
    # United Kingdom
    [(-5, 50), (-4, 52), (-5, 54), (-4, 56), (-3, 58), (-1, 57),
     (0, 54), (1, 52), (0, 50)],
    # Ireland
    [(-10, 52), (-9, 54), (-7, 55), (-6, 54), (-6, 52), (-8, 51)],
    # Sicily
    [(12, 37), (14, 38), (15, 37), (13, 36)],
    # Asia: Turkey, Caucasus, Siberia, Chukotka, Pacific coast with
    # Korea, south China coast, Vietnam, Malay peninsula spike,
    # Myanmar, the Indian triangle, Arabia, Red Sea, Levant.
    [(28, 41), (30, 41), (33, 42), (36, 42), (39, 41), (41, 41),
     (43, 43), (45, 45), (47, 46), (49, 47), (51, 49), (54, 51),
     (57, 53), (60, 55), (63, 57), (66, 59), (68, 61), (68, 65),
     (69, 68), (71, 71), (74, 73), (78, 73), (82, 74), (87, 75),
     (92, 75), (97, 76), (102, 76), (107, 75), (112, 74), (117, 73),
     (122, 73), (127, 72), (132, 72), (137, 72), (142, 72), (147, 71),
     (152, 70), (157, 70), (162, 69), (167, 68), (172, 67), (177, 66),
     (178, 65), (178, 63), (175, 62), (170, 60), (166, 59), (162, 57),
     (158, 53), (156, 52), (152, 50), (148, 49), (144, 48), (141, 46),
     (140, 43), (138, 40), (136, 37), (134, 35), (132, 34), (130, 33),
     (128, 34), (127, 36), (129, 38), (127, 40), (125, 40), (123, 39),
     (121, 38), (120, 35), (121, 32), (120, 29), (119, 26), (117, 24),
     (115, 23), (113, 22), (111, 21), (109, 20), (108, 18), (107, 16),
     (109, 13), (109, 11), (107, 10), (105, 9), (104, 9), (103, 8),
     (102, 6), (101, 4), (100, 2), (99, 4), (99, 7), (98, 10), (98, 12),
     (97, 14), (96, 15), (95, 16), (94, 17), (93, 19), (92, 21),
     (91, 22), (89, 22), (87, 21), (85, 19), (83, 17), (81, 15),
     (80, 12), (80, 10), (78, 8), (77, 9), (76, 11), (74, 14), (73, 16),
     (72, 19), (71, 20), (69, 22), (67, 24), (65, 25), (63, 25),
     (61, 25), (59, 26), (57, 26), (55, 27), (53, 27), (51, 28),
     (49, 29), (48, 30), (50, 28), (52, 26), (54, 25), (56, 24),
     (58, 23), (59, 22), (58, 20), (56, 18), (54, 16), (52, 15),
     (50, 14), (48, 14), (45, 13), (43, 12), (42, 14), (41, 16),
     (40, 19), (39, 22), (38, 25), (37, 28), (36, 30), (35, 32),
     (34, 34), (34, 36), (32, 36), (30, 36), (28, 37), (27, 39),
     (27, 41)],
    # Australia: west coast, Great Australian Bight, east coast, Cape York.
    [(113, -22), (114, -28), (115, -32), (115, -35), (118, -35),
     (121, -34), (124, -33), (127, -32), (129, -32), (132, -32),
     (134, -33), (136, -35), (137, -35), (139, -37), (140, -38),
     (144, -38), (146, -39), (148, -38), (150, -37), (151, -35),
     (153, -32), (153, -29), (153, -26), (152, -24), (150, -22),
     (148, -20), (146, -19), (144, -17), (142, -14), (142, -11),
     (141, -13), (139, -15), (137, -13), (136, -12), (134, -12),
     (132, -12), (130, -13), (128, -14), (126, -14), (124, -16),
     (122, -17), (120, -19), (117, -20), (115, -21)],
    # Tasmania
    [(145, -41), (147, -41), (148, -42), (147, -43), (146, -43),
     (145, -42)],
    # New Zealand
    [(167, -45), (169, -43), (171, -42), (173, -41), (174, -39),
     (176, -38), (177, -38), (175, -40), (173, -41), (171, -43),
     (169, -45), (167, -46)],
    # Japan: Honshu
    [(129, 31), (131, 33), (133, 34), (135, 34), (137, 35), (139, 35),
     (140, 37), (141, 39), (141, 41), (140, 40), (138, 38), (136, 37),
     (134, 35), (132, 34), (130, 32)],
    # Japan: Hokkaido
    [(140, 42), (142, 42), (144, 43), (145, 44), (143, 44), (141, 43)],
    # Sumatra
    [(95, 5), (97, 4), (99, 2), (101, 0), (103, -2), (105, -4),
     (106, -6), (104, -5), (102, -3), (100, -1), (98, 1), (96, 4)],
    # Borneo
    [(109, 1), (111, 2), (113, 4), (116, 6), (118, 4), (119, 1),
     (118, -1), (117, -3), (115, -4), (113, -3), (111, -1), (109, 0)],
    # Java
    [(105, -6), (107, -7), (109, -7), (111, -7), (113, -7), (114, -8),
     (112, -8), (110, -8), (108, -7), (106, -7)],
    # New Guinea
    [(131, -1), (133, -2), (136, -2), (138, -3), (140, -3), (141, -4),
     (141, -7), (139, -8), (137, -7), (135, -5), (133, -3), (131, -2)],
    # Sulawesi
    [(119, 0), (121, 1), (120, -1), (119, -3), (120, -5), (121, -3)],
    # Philippines
    [(120, 18), (122, 18), (122, 16), (121, 14), (122, 12), (123, 11),
     (122, 9), (121, 7), (122, 6), (123, 8), (124, 10), (125, 9),
     (126, 7), (125, 5)],
]

# Inland seas cut back into the land after the continents are drawn.
INLAND_SEAS = [
    # Baltic Sea
    [(12, 55), (14, 57), (17, 59), (20, 61), (22, 63), (24, 65),
     (23, 63), (21, 61), (19, 59), (16, 57), (13, 55)],
    # Caspian Sea
    [(47, 42), (49, 40), (51, 41), (52, 43), (51, 46), (49, 47),
     (47, 45)],
    # Great Lakes
    [(-87, 42), (-85, 42), (-83, 43), (-81, 44), (-83, 46),
     (-86, 46), (-88, 45)],
]

# Story number -> (lon, lat, nudge_x, nudge_y) for the map dots.
# No nudges. The true places cluster too tightly for legible numbered
# dots at this size (Washington/Ottawa are 4 px apart, as are the four
# European stories), so each dot sits at the nearest on-land point in
# the same region that keeps every number readable: Poland central,
# eastern Ukraine, Jutland, north-eastern Estonia, Virginia, the
# Maine / Quebec border, eastern Myanmar, western Odisha.
DOTS = [
    (1, -75, -10, 0, 0),    # Peru, west coast of South America
    (2, 19, 51, 0, 0),      # Poland
    (3, 33, 49, 0, 0),      # Ukraine
    (4, 10, 56, 0, 0),      # Denmark
    (5, 27, 60, 0, 0),      # Estonia
    (6, -80, 37, 0, 0),     # US east coast
    (7, -70, 48, 0, 0),     # Canada / US border
    (8, 113, 24, 0, 0),     # Shenzhen, China coast
    (9, 98, 21, 0, 0),      # Myanmar
    (10, 82, 19, 0, 0),     # Odisha, east coast of India
]


def draw_map(draw, page, x0, y0, w, h):
    """World map with numbered dots 1-10 for the big stories.

    Printed-atlas look: a deep blue ocean that lightens over the
    continental shelf near the coasts and darkens toward the open
    sea and the frame edges, terrain-coloured land (green lowlands,
    tan arid belts, darker boreal north) with soft hill-shading
    from the upper left, a faint drop shadow under each continent
    so the land reads as raised above the sea, and a very subtle
    graticule. Equirectangular, with a margin around the inhabited
    latitudes so no dot touches the frame. The map is rendered
    supersampled and downscaled so the dense coastlines stay
    smooth; inland seas are cut back in after the land, and the
    numbered dots are drawn last, crisp, on top of the shading.
    """
    SS = 3  # supersample factor: coastlines stay smooth at 300x92
    Wm, Hm = w * SS, h * SS
    lon0, lon1 = -175.0, 185.0
    lat0, lat1 = 84.0, -62.0

    def px(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * Wm,
                (lat0 - lat) / (lat0 - lat1) * Hm)

    def fpx(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)

    polys = [[px(lon, lat) for lon, lat in poly] for poly in CONTINENTS]
    seas = [[px(lon, lat) for lon, lat in sea] for sea in INLAND_SEAS]
    blank = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))

    # --- ocean: deep blue gradient, darker toward the open sea -------
    ocean = Image.new("RGB", (Wm, Hm))
    od = ImageDraw.Draw(ocean)
    top = (36, 88, 142)
    mid = (23, 64, 114)
    bot = (13, 40, 82)
    for yy in range(Hm):
        t = yy / max(Hm - 1, 1)
        if t < 0.5:
            c = tuple(int(top[i] + (mid[i] - top[i]) * t * 2)
                      for i in range(3))
        else:
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * (t - 0.5) * 2)
                      for i in range(3))
        od.line([(0, yy), (Wm, yy)], fill=c)

    # --- land mask, and the continental shelf glowing around it ------
    mask = Image.new("L", (Wm, Hm), 0)
    md = ImageDraw.Draw(mask)
    for pts in polys:
        md.polygon(pts, fill=255)
    shelf = mask.filter(ImageFilter.GaussianBlur(SS * 4))
    shelf_rgb = Image.new("RGB", (Wm, Hm), (74, 130, 174))
    ocean = Image.composite(shelf_rgb, ocean,
                            shelf.point(lambda v: v * 3 // 4))
    ocean = ocean.convert("RGBA")

    # --- graticule: very faint, ocean only ---------------------------
    grat = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grat)
    for lon in range(-150, 181, 30):
        gx = (lon - lon0) / (lon1 - lon0) * Wm
        gd.line([(gx, 0), (gx, Hm)], fill=(170, 200, 228, 44), width=1)
    for lat in range(-50, 71, 25):
        gy = (lat0 - lat) / (lat0 - lat1) * Hm
        gd.line([(0, gy), (Wm, gy)], fill=(170, 200, 228, 44), width=1)
    ocean = Image.alpha_composite(ocean, grat)

    # --- land layer: drop shadow (lower right), rim light (upper left)
    land = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for pts in polys:
        sd.polygon([(x + 2 * SS, y + 3 * SS) for x, y in pts],
                   fill=(8, 24, 52, 135))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SS * 1.5))
    land = Image.alpha_composite(land, shadow)
    rim = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    for pts in polys:
        rd.polygon([(x - 2 * SS, y - 2 * SS) for x, y in pts],
                   fill=(255, 244, 214, 70))
    rim = rim.filter(ImageFilter.GaussianBlur(SS * 1.2))
    land = Image.alpha_composite(land, rim)

    # --- base land fill: mid green, deep enough to hold the tints -----
    ld = ImageDraw.Draw(land)
    for pts in polys:
        ld.polygon(pts, fill=(140, 162, 104, 255))

    def clip(layer):
        """Keep a full-frame overlay only where land is."""
        return Image.composite(layer, blank, mask)

    def tint_band(lat_a, lat_b, color, alpha):
        """Soft horizontal terrain tint between two latitudes."""
        layer = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
        td = ImageDraw.Draw(layer)
        _, ya = px(0, lat_a)
        _, yb = px(0, lat_b)
        td.rectangle([0, min(ya, yb), Wm, max(ya, yb)],
                     fill=color + (alpha,))
        return layer.filter(ImageFilter.GaussianBlur(SS * 2))

    # Arid belts tan, tropics lush green, far north darker boreal.
    land = Image.alpha_composite(land, clip(tint_band(14, 31,
                                 (198, 172, 120), 60)))
    land = Image.alpha_composite(land, clip(tint_band(-30, -13,
                                 (198, 172, 120), 55)))
    land = Image.alpha_composite(land, clip(tint_band(-12, 12,
                                 (88, 138, 78), 95)))
    land = Image.alpha_composite(land, clip(tint_band(58, 84,
                                 (104, 124, 94), 70)))

    # --- high ground: soft brown blotches on the great ranges ---------
    peaks = [(-72, -18, 6, 12), (-112, 44, 8, 7), (84, 30, 10, 5),
             (10, 46, 5, 3), (-6, 31, 5, 3), (37, 2, 6, 6),
             (-105, 38, 7, 6)]
    mlayer = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    md2 = ImageDraw.Draw(mlayer)
    for lon, lat, rx, ry in peaks:
        cx, cy = px(lon, lat)
        md2.ellipse([cx - rx * SS, cy - ry * SS,
                     cx + rx * SS, cy + ry * SS],
                    fill=(148, 126, 90, 110))
    mlayer = mlayer.filter(ImageFilter.GaussianBlur(SS * 3))
    land = Image.alpha_composite(land, clip(mlayer))

    # --- grain: deterministic speckles so no expanse stays flat -------
    rng = random.Random(20261122)
    sp = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    spd = ImageDraw.Draw(sp)
    mpx = mask.load()
    tones = [(255, 255, 240, 34), (60, 70, 40, 34),
             (210, 190, 140, 32), (90, 110, 70, 32)]
    for _ in range(3200):
        x = rng.randrange(Wm)
        y = rng.randrange(Hm)
        if mpx[x, y]:
            r = rng.choice([1, 1, 2])
            spd.ellipse([x - r, y - r, x + r, y + r],
                        fill=rng.choice(tones))
    sp = sp.filter(ImageFilter.GaussianBlur(0.6))
    land = Image.alpha_composite(land, sp)

    # --- hill-shading: light from the upper left ----------------------
    grad = Image.new("L", (24, 24))
    grad.putdata([int(255 * (1 - 0.45 * ((x / 23 + y / 23) / 2)))
                  for y in range(24) for x in range(24)])
    grad = grad.resize((Wm, Hm), Image.BICUBIC)
    light = Image.new("RGBA", (Wm, Hm), (255, 250, 230, 0))
    light.putalpha(grad.point(lambda v: (v - 140) * 18 // 115))
    land = Image.alpha_composite(land, clip(light))
    shade = Image.new("RGBA", (Wm, Hm), (10, 20, 44, 0))
    shade.putalpha(grad.point(lambda v: (255 - v) * 26 // 115))
    land = Image.alpha_composite(land, clip(shade))

    # --- coastline stroke, then inland seas cut back in ---------------
    for pts in polys:
        ld.line(pts + [pts[0]], fill=(58, 68, 48, 255), width=SS)
    for pts in seas:
        ld.polygon(pts, fill=(56, 108, 156, 255))
        ld.line(pts + [pts[0]], fill=(44, 84, 128, 255), width=SS)

    # --- compose, vignette, downscale ---------------------------------
    map_img = Image.alpha_composite(ocean, land)
    vig = Image.new("L", (Wm, Hm), 0)
    vd = ImageDraw.Draw(vig)
    vd.rectangle([SS * 10, SS * 8, Wm - SS * 10, Hm - SS * 8], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(SS * 12))
    dark = Image.new("RGBA", (Wm, Hm), (6, 14, 34, 255))
    dark.putalpha(vig.point(lambda v: (255 - v) * 70 // 255))
    map_img = Image.alpha_composite(map_img, dark)
    map_img = map_img.convert("RGB").resize((w, h), Image.LANCZOS)
    page.paste(map_img, (x0, y0))
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=RULE, width=1)

    # --- dots: crisp, on top of all shading ---------------------------
    for num, lon, lat, nx, ny in DOTS:
        cx, cy = fpx(lon, lat)
        cx += nx
        cy += ny
        # Small dots: the European stories and Washington/Ottawa sit
        # only ~8 px apart, so a radius of 5 (7 for two-digit 10) is
        # what keeps every number readable without overlap.
        r = 5 if num < 10 else 7
        # Thin dark ring only (no filled halo disc): neighbours sit
        # ~8 px apart, so a disc would merge them into one blob.
        draw.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1],
                     outline=(16, 32, 64), width=1)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        label = str(num)
        tw = draw.textlength(label, font=font(SANS_BOLD, 8))
        draw.text((cx - tw / 2, cy - 4), label, font=font(SANS_BOLD, 8),
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
    hrule(draw, MX, W - MX, 812, fill=NAVY, width=1)
    secf = font(SERIF_BOLD, 14)
    draw.text((MX, 818), "WHERE IT HAPPENED", font=secf, fill=NAVY)
    draw.text((MX + 316, 818), "THE DAY IN BRIEF", font=secf, fill=NAVY)
    draw_map(draw, page, MX, 840, 300, 92)
    leg = "Dots 1-10 match the big stories above."
    draw.text((MX, 936), leg, font=font(SANS, 9), fill=GREY)
    bx0 = MX + 316
    col_w = (CW - 316) // 2
    for i, item in enumerate(BRIEFS):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x = bx0 + col * col_w
        y = 840 + row * 10
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
