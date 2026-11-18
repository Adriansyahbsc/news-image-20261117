#!/usr/bin/env python3
"""Render the 17 November 2026 world-news infographic (1024x1024 PNG).

Deterministic: pure PIL drawing from fixed strings, no clock, no randomness.
Text is code-rendered with Liberation Sans (bold for headlines) so every
letter is crisp and exact.
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "entry.png"

REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

BG = (12, 17, 24)          # near-black navy
CARD = (21, 28, 38)        # panel fill
CARD_EDGE = (43, 54, 70)
WHITE = (240, 244, 248)
BODY = (199, 207, 216)
MUTED = (139, 148, 158)
GOLD = (232, 177, 60)

# headline_lines: manual wraps (44px bold); support auto-fits 27->25px.
STORIES = [
    {
        "accent": (232, 177, 60),
        "headline": ["TRUMP'S ASIA TOUR"],
        "support": ("ASEAN summit in Manila. Next: APEC in Shenzhen \u2014 a "
                    "Trump\u2013Xi\u2013Putin trilateral is planned for 19 Nov."),
        "max_lines": 3,
    },
    {
        "accent": (229, 83, 75),
        "headline": ["IRAN\u2013US TENSIONS", "RISE"],
        "support": ("Iranian drone downed near US radar site in Bahrain; no "
                    "casualties. US reports plot vs officials (unconfirmed)."),
        "max_lines": 3,
    },
    {
        "accent": (88, 166, 255),
        "headline": ["UKRAINE:", "BRIDGE CLAIMS"],
        "support": ("Kyiv claims heavy damage to Crimea's Kerch Bridge. Russia "
                    "hits a Kyiv bridge, claims 1,400+ drones intercepted."),
        "max_lines": 3,
    },
    {
        "accent": (63, 185, 80),
        "headline": ["ISRAEL & GAZA"],
        "support": ("UK sanctions 8 settlement firms; settler attack kills a "
                    "72-year-old near Jericho. UK, Australia, Canada & Italy "
                    "urge Gaza crossings opened."),
        "max_lines": 4,
    },
    {
        "accent": (188, 140, 255),
        "headline": ["JAPAN & ESTONIA", "ON ALERT"],
        "support": ("Jets scrambled over reported Russian airspace breach. "
                    "Estonia shuts Russia border posts 1 Dec, citing sabotage plot."),
        "max_lines": 3,
    },
    {
        "accent": (247, 120, 186),
        "headline": ["EUROPE\u2013RWANDA", "DEAL"],
        "support": ("Germany, Denmark, Austria, Greece & the Netherlands back "
                    "a Rwanda hub for deporting rejected asylum seekers."),
        "max_lines": 3,
    },
]


def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_support(text, max_w, draw, max_lines):
    """Largest size in 27..25 whose wrap fits max_lines; else 25px wrap."""
    for size in (27, 26, 25):
        font = ImageFont.truetype(REG, size)
        lines = wrap(text, font, max_w, draw)
        if len(lines) <= max_lines:
            return font, size, lines
    font = ImageFont.truetype(REG, 25)
    return font, 25, wrap(text, font, max_w, draw)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- header ------------------------------------------------------
    title_font = ImageFont.truetype(BOLD, 60)
    sub_font = ImageFont.truetype(REG, 29)
    title = "TUESDAY 17 NOVEMBER 2026"
    tw = d.textlength(title, font=title_font)
    d.text(((W - tw) / 2, 30), title, font=title_font, fill=WHITE)
    sub = "THE WORLD IN ONE IMAGE \u2014 the day\u2019s top stories"
    sw = d.textlength(sub, font=sub_font)
    d.text(((W - sw) / 2, 108), sub, font=sub_font, fill=(170, 180, 192))
    d.line([(28, 158), (W - 28, 158)], fill=GOLD, width=3)

    # ---- grid ---------------------------------------------------------
    margin, gap = 18, 14
    card_w = (W - 2 * margin - gap) // 2          # 487
    grid_top, grid_bottom = 174, 970
    card_h = (grid_bottom - grid_top - 2 * gap) // 3   # 256
    pad = 16
    text_w = card_w - 2 * pad                     # 455
    head_font = ImageFont.truetype(BOLD, 44)
    num_font = ImageFont.truetype(BOLD, 26)

    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (card_w + gap)
        y0 = grid_top + row * (card_h + gap)
        x1, y1 = x0 + card_w, y0 + card_h
        accent = story["accent"]

        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CARD,
                            outline=CARD_EDGE, width=1)
        # accent strip across the card top (rounded top, squared bottom),
        # carrying the story number in dark type at its right end
        d.rounded_rectangle([x0, y0, x1, y0 + 30], radius=14, fill=accent)
        d.rectangle([x0, y0 + 15, x1, y0 + 30], fill=accent)
        num = str(i + 1)
        nw = d.textlength(num, font=num_font)
        d.text((x1 - pad - nw, y0 + 2), num, font=num_font, fill=BG)

        # headline (44px bold, manual wraps)
        y = y0 + 40
        for line in story["headline"]:
            d.text((x0 + pad, y), line, font=head_font, fill=WHITE)
            y += 49
        y += 8

        # support text, auto-fitted
        font, size, lines = fit_support(story["support"], text_w, d,
                                        story["max_lines"])
        leading = size + 8
        print(f"story {i + 1}: support {size}px, {len(lines)} line(s), "
              f"bottom={y + leading * len(lines)} (card bottom {y1})")
        for line in lines:
            d.text((x0 + pad, y), line, font=font, fill=BODY)
            y += leading

    # ---- footer -------------------------------------------------------
    foot_font = ImageFont.truetype(REG, 21)
    foot = ("As reported on 17 Nov 2026 \u00b7 Unconfirmed claims are "
            "labelled as reported")
    fw = d.textlength(foot, font=foot_font)
    d.text(((W - fw) / 2, 984), foot, font=foot_font, fill=MUTED)

    img.save(OUT, format="PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
