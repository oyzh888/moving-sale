#!/usr/bin/env python3
"""Regenerate README.md from items.csv. Edit items.csv (price / status), then run this.

status: available | pending | sold | draft (draft = not ready to sell yet, still shown as "details coming")
"""
import csv, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = {"available": "🟢 Available", "pending": "🟡 Pending pickup", "sold": "🔴 SOLD", "draft": "⚪ Details coming"}


def price(row):
    return f"${row['price_usd']}" if row["price_usd"] else "ask"


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "items.csv"), encoding="utf-8")))
    out = [
        "# Moving Sale / 搬家出售",
        "",
        "Everything here is used and pickup only. "
        "**Message me on Facebook Marketplace with the item number** (e.g. `F01`) — the number is printed on every photo.",
        "",
        "所有物品均为二手自提。**请在 Facebook Marketplace 上发消息并注明编号**（如 `F01`），每张图左上角都有编号。",
        "",
        "## Index",
        "",
        "| # | Item | 中文 | Price | Status |",
        "|---|------|------|-------|--------|",
    ]
    for r in rows:
        title = f"~~{r['title']}~~" if r["status"] == "sold" else r["title"]
        out.append(f"| [{r['id']}](#{r['id'].lower()}) | {title} | {r['title_zh']} | {price(r)} | {STATUS[r['status']]} |")
    cats = []
    for r in rows:
        if r["category"] not in cats:
            cats.append(r["category"])
    for cat in cats:
        out += ["", f"## {cat}"]
        for r in (x for x in rows if x["category"] == cat):
            imgs = sorted(glob.glob(os.path.join(ROOT, "images", f"{r['id']}_*.jpg")))
            out += ["", f'<a id="{r["id"].lower()}"></a>', f"### {r['id']} · {r['title']} · {price(r)} · {STATUS[r['status']]}", "",
                    r["title_zh"], "", r["notes"], ""]
            out.append(" ".join(f'<img src="images/{os.path.basename(p)}" width="360">' for p in imgs))
    out.append("")
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    main()
