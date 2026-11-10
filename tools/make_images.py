#!/usr/bin/env python3
"""Build web images (ID badge burned in, metadata stripped) and catalog sheets from raw/ + items.csv.

Usage: python3 tools/make_images.py     (needs Pillow; raw/ is not in git)
"""
import csv, glob, os
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "/System/Library/Fonts/Helvetica.ttc"
# Per-photo crop as fractions (left, top, right, bottom) of the upright image.
CROPS = {
    "4140": (0, 0.42, 1, 1),  # cuts the monitor screen out of the table shot
    "4133": (0, 0.45, 1, 1),  # bench only; the TV has its own entry
}


def badge(im, text, size):
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, size)
    w = d.textlength(text, font=font)
    pad = size // 3
    d.rounded_rectangle([pad, pad, pad * 3 + w, pad * 2.6 + size], radius=pad, fill=(20, 20, 20), outline="white", width=3)
    d.text((pad * 2, pad * 1.6), text, fill="white", font=font)


def load(num):
    im = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, "raw", f"IMG_{num}.jpeg"))).convert("RGB")
    if num in CROPS:
        l, t, r, b = CROPS[num]
        im = im.crop((int(l * im.width), int(t * im.height), int(r * im.width), int(b * im.height)))
    im.thumbnail((1600, 1600))
    return im


def main():
    for old in glob.glob(os.path.join(ROOT, "images", "*.jpg")) + glob.glob(os.path.join(ROOT, "catalog", "*.jpg")):
        os.remove(old)
    rows = list(csv.DictReader(open(os.path.join(ROOT, "items.csv"), encoding="utf-8")))
    heroes = []
    for row in rows:
        for i, num in enumerate(row["photos"].split(";"), 1):
            im = load(num)
            badge(im, row["id"], 90)
            im.save(os.path.join(ROOT, "images", f"{row['id']}_{i}.jpg"), quality=85)
            if i == 1:
                heroes.append((row, im))
    # Catalog sheets: 3x3 grid of hero shots, for a single multi-item Marketplace post.
    cell, cols, per = 700, 3, 9
    cap_font = ImageFont.truetype(FONT, 30)
    for s in range(0, len(heroes), per):
        chunk = heroes[s:s + per]
        nrows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, nrows * (cell + 50)), "white")
        d = ImageDraw.Draw(sheet)
        for k, (row, im) in enumerate(chunk):
            x, y = (k % cols) * cell, (k // cols) * (cell + 50)
            sheet.paste(ImageOps.fit(im, (cell - 10, cell - 10), centering=(0, 0)), (x + 5, y + 5))
            price = f"${row['price_usd']}" if row["price_usd"] else "ask"
            cap = f"{row['id']} · {row['title']}"
            while d.textlength(cap + f" · {price}", font=cap_font) > cell - 20:
                cap = cap[:-2].rstrip() + "…"
            d.text((x + 10, y + cell + 6), f"{cap} · {price}", fill="black", font=cap_font)
        sheet.save(os.path.join(ROOT, "catalog", f"catalog_{s // per + 1}.jpg"), quality=85)


if __name__ == "__main__":
    main()
