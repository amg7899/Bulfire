"""Writes the product cards of the online fire shops into fire-shop/index.html and
bg/fire-shop/index.html, between the markers <!-- products:companies --> ... <!-- /products:companies -->
and <!-- products:departments --> ... <!-- /products:departments -->, from tools/products.json.

    python3 tools/shop.py

tools/products.json holds one entry per product, in the order of the old shop's tables:
  id          the old WooCommerce product id (kept as a stable key; the quote request uses it)
  section     "companies" (Online fire shop for fire companies) or "departments" (... for fire departments)
  en, bg      the name in English (the client's, typos fixed: see CLAUDE.md) and in Bulgarian (ours)
  image       the picture in assets/img/shop/ (<image>.webp + <image>.jpg), with width w and height h
No prices anywhere (client, 2026-11-26): every product has a "Get a quote" button instead, which
assets/js/shop.js shows and wires up. Standard library only.
"""
import html
import json
import os
import re
import unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAGES = {"en": "fire-shop/index.html", "bg": "bg/fire-shop/index.html"}
BUTTON = {
    "en": ("Get a quote", "Added to quote"),
    "bg": ("Вземете оферта", "Добавено"),   # short: the cards are narrow on phones
}
PLUS = ('<svg class="quote-btn-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M12 5v14M5 12h14"/></svg>')
CHECK = ('<svg class="quote-btn-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>')


def search_key(*names):
    """Lower case, without accents (Dräger = drager), both languages, so either can be searched."""
    text = " ".join(names).lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def card(p, lang, prefix):
    name = p[lang]
    add, added = BUTTON[lang]
    img = f"{prefix}assets/img/shop/{p['image']}"
    w, h = p.get("w", 300), p.get("h", 300)
    return (
        f'            <li class="product" data-id="{p["id"]}" data-en="{html.escape(p["en"])}" data-search="{html.escape(search_key(p["en"], p["bg"]))}">\n'
        f'              <div class="product-card plate">\n'
        f'                <div class="product-media"><picture><source type="image/webp" srcset="{img}.webp">'
        f'<img src="{img}.jpg" alt="" width="{w}" height="{h}" loading="lazy" decoding="async"></picture></div>\n'
        f'                <h3 class="product-name">{html.escape(name, quote=False)}</h3>\n'
        f'                <button class="quote-btn" type="button" hidden>{PLUS}{CHECK}'
        f'<span class="quote-btn-add">{add}</span><span class="quote-btn-added">{added}</span></button>\n'
        f'              </div>\n'
        f'            </li>\n'
    )


def main():
    with open(os.path.join(ROOT, "tools", "products.json"), encoding="utf-8") as fh:
        products = json.load(fh)
    for lang, rel in PAGES.items():
        path = os.path.join(ROOT, rel)
        prefix = "../" * rel.count("/")
        with open(path, encoding="utf-8") as fh:
            page = fh.read()
        for section in ("companies", "departments"):
            cards = "".join(card(p, lang, prefix) for p in products if p["section"] == section)
            start, end = f"<!-- products:{section} -->", f"<!-- /products:{section} -->"
            pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
            if not pattern.search(page):
                raise SystemExit(f"{rel}: markers for {section} not found")
            page = pattern.sub(lambda m: f"{start}\n{cards}            {end}", page)
            count = sum(1 for p in products if p["section"] == section)
            page = re.sub(rf'(<span class="shop-count" data-count="{section}">)\d+(</span>)', rf"\g<1>{count}\2", page)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(rel, len(products), "products")


if __name__ == "__main__":
    main()
