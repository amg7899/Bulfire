"""Builds the BULFIRE document pages (About us, the vehicle pages, Contact, the legal pages).

    python3 tools/pages/build.py tools/pages/content/*.en.html tools/pages/content/*.bg.html

Run it after changing a content file, or after changing the header or footer of index.html / bg/index.html
(every page takes its header and footer from the Home page of its language). The shop pages are built
separately (fire-shop/, tools/shop.py); give them the same header and footer by hand.

A content file starts with a comment holding key: value lines (slug, lang, title, description, h1,
lead, current, quote, cta, scripts), then the body HTML. <figure class="figure plate" data-img="ID">
gets its <picture> from the image manifest (assets/img/pages/manifest.json). Header and footer come
from the Home page of the same language, one or two folders deeper.
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + os.sep
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" '
         'aria-hidden="true" focusable="false"><path d="M4 12h15M13 6l6 6-6 6"/></svg>')
TEXT = {
    'en': {'quote': 'Get a quote', 'cta': 'Get a quote', 'scroll': 'Table: scroll sideways to see all columns'},
    'bg': {'quote': 'Вземете оферта', 'cta': 'Вземете оферта', 'scroll': 'Таблица: превъртете настрани, за да видите всички колони'},
}
SIZES = {
    'single': '(min-width: 1100px) 860px, calc(100vw - 2 * var(--gutter, 16px))',
    'pair': '(min-width: 1100px) 480px, (min-width: 640px) 46vw, 100vw',
    'three': '(min-width: 1100px) 320px, (min-width: 900px) 31vw, (min-width: 640px) 46vw, 100vw',
    'portrait': '300px',
    'gallery': '(min-width: 1100px) 240px, (min-width: 1000px) 23vw, (min-width: 640px) 31vw, 46vw',
}
VIEWER = {   # the viewer's button labels (viewer.js), on <main>
    'en': 'data-close="Close" data-prev="Previous" data-next="Next"',
    'bg': 'data-close="Затвори" data-prev="Предишна" data-next="Следваща"',
}


def deeper(fragment, levels=1):
    up = '../' * levels
    def fix(url):
        if re.match(r'(https?:|mailto:|tel:|#|//|data:)', url):
            return url
        if url.startswith('./'):
            url = url[2:]
        return up + url
    fragment = re.sub(r'(href|src)="([^"]*)"', lambda m: f'{m.group(1)}="{fix(m.group(2))}"', fragment)
    fragment = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + ', '.join(
        ' '.join([fix(p.strip().split()[0])] + p.strip().split()[1:]) for p in m.group(1).split(',')) + '"', fragment)
    return fragment


def picture(img_id, alt, kind, prefix, manifest, zoom=False):
    m = manifest.get(str(img_id))
    if not m:
        return f'<img src="{prefix}assets/img/pages/missing.svg" alt="{alt}" width="800" height="500" loading="lazy">'
    base = f'{prefix}assets/img/pages/{m["name"]}'
    widths = m['widths']
    w, h = m['w'], m['h']
    small = widths[0]
    webp = ', '.join(f'{base}-{x}.webp {x}w' for x in widths)
    jpg = ', '.join(f'{base}-{x}.jpg {x}w' for x in widths)
    sizes = SIZES[kind]
    pic = (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
           f'<img src="{base}-{small}.jpg" srcset="{jpg}" sizes="{sizes}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></picture>')
    if zoom:   # the picture opens full size (viewer.js); without JavaScript the link opens the image
        big = widths[-1]
        pic = f'<a class="zoom" href="{base}-{big}.jpg" data-webp="{base}-{big}.webp">{pic}</a>'
    return pic


def build(path, manifest):
    raw = open(path, encoding='utf-8').read()
    meta_txt, body = re.match(r'\s*<!--(.*?)-->\s*(.*)', raw, re.S).groups()
    meta = {}
    for line in meta_txt.strip().splitlines():
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip()
    lang, slug = meta['lang'], meta['slug']
    T = TEXT[lang]
    depth = slug.count('/') + 1 + (1 if lang == 'bg' else 0)     # folders below the site root
    prefix = '../' * depth
    # figures: put the picture in front of the caption
    def fig(m):
        attrs, inner = m.group(1), m.group(2)
        img_id = re.search(r'data-img="(\d+)"', attrs).group(1)
        alt = (re.search(r'data-alt="([^"]*)"', attrs) or [None, ''])[1]
        kind = (re.search(r'data-size="([^"]*)"', attrs) or [None, 'single'])[1]
        zoom = 'data-zoom' in attrs
        attrs = re.sub(r'\s*data-(img|alt|size)="[^"]*"', '', attrs).replace(' data-zoom', '')
        m = manifest.get(str(img_id))
        if kind == 'single' and m and m['w'] < 860:     # never wider than the picture itself (+ the card's padding)
            attrs += f' style="max-width: {m["w"] + 26}px"'
        return f'<figure{attrs}>{picture(img_id, alt, kind, prefix, manifest, zoom)}{inner}</figure>'
    body = re.sub(r'<figure([^>]*data-img="\d+"[^>]*)>(.*?)</figure>', fig, body, flags=re.S)
    # tables: in a card that scrolls sideways, announced as such
    n = [0]
    def wrap(m):
        n[0] += 1
        return (f'<div class="table-wrap" role="region" tabindex="0" aria-label="{T["scroll"]}">{m.group(0)}</div>')
    body = re.sub(r'<table class="spec">.*?</table>', wrap, body, flags=re.S)
    # page head
    quote = meta.get('quote', '')
    head_btn = (f'\n        <a class="btn" href="{prefix}{"bg/" if lang == "bg" else ""}{quote}"><span>{T["quote"]}</span>{ARROW}</a>'
                if quote else '')
    lead = f'\n        <p class="page-lead">{meta["lead"]}</p>' if meta.get('lead') else ''
    cta = ''
    if meta.get('cta') and quote:
        cta = (f'\n        <a class="cta" href="{prefix}{"bg/" if lang == "bg" else ""}{quote}">'
               f'<span class="cta-text">{T["cta"]}</span><span class="cta-go" aria-hidden="true">{ARROW}</span></a>')
    viewer = f' {VIEWER[lang]}' if 'class="zoom"' in body else ''
    main = f'''  <main id="main"{viewer}>
    <section class="page-head">
      <div class="container">
        <h1>{meta["h1"]}</h1>{lead}{head_btn}
      </div>
    </section>

    <div class="page-body">
      <div class="container">
{body.rstrip()}{cta}
      </div>
    </div>
  </main>

'''
    # header and footer from Home
    home = ROOT + ('bg/index.html' if lang == 'bg' else 'index.html')
    s = open(home, encoding='utf-8').read()
    head = s[:s.index('</head>')]
    header = s[s.index('  <a class="skip-link"'):s.index('  <main id="main">')]
    footer = s[s.index('  <footer class="site-footer">'):s.index('  <script src=')]
    base = 'https://bulfire.ecoes.eu/'
    head = re.sub(r'<title>.*?</title>', f'<title>{meta["title"]}</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta["description"]}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{base}{"bg/" if lang == "bg" else ""}{slug}/">', head)
    head = re.sub(r'(hreflang="en" href=")[^"]*', rf'\g<1>{base}{slug}/', head)
    head = re.sub(r'(hreflang="bg" href=")[^"]*', rf'\g<1>{base}bg/{slug}/', head)
    head = re.sub(r'(hreflang="x-default" href=")[^"]*', rf'\g<1>{base}{slug}/', head)
    levels = slug.count('/') + 1
    head, header, footer = deeper(head, levels), deeper(header, levels), deeper(footer, levels)
    # current page: Home loses its mark; the page's own link (and its menu group) gets it
    header = header.replace(' aria-current="page"><span', '><span', 1)
    cur = meta.get('current')
    if cur:
        target = f'<li><a href="{cur}">'
        assert target in header, f'{path}: current link {cur} not in header'
        header = header.replace(target, f'<li><a href="{cur}" aria-current="page">', 1)
        idx = header.index(f'href="{cur}" aria-current')
        sub_start = header.rfind('<li class="has-sub">', 0, idx)
        if sub_start != -1 and header.find('</ul>', sub_start) > idx and '<ul class="sub-nav">' in header[sub_start:idx]:
            header = header[:sub_start] + '<li class="has-sub is-current">' + header[sub_start + len('<li class="has-sub">'):]
    # language switch: the twin page
    up_other = '../' * levels
    if lang == 'en':
        header = re.sub(r'<a href="[^"]*" hreflang="en" lang="en" aria-current="page">', '<a href="./" hreflang="en" lang="en" aria-current="page">', header)
        header = re.sub(r'<a href="[^"]*" hreflang="bg" lang="bg">', f'<a href="{up_other}bg/{slug}/" hreflang="bg" lang="bg">', header)
    else:
        header = re.sub(r'<a href="[^"]*" hreflang="en" lang="en">', f'<a href="{up_other}../{slug}/" hreflang="en" lang="en">', header)
        header = re.sub(r'<a href="[^"]*" hreflang="bg" lang="bg" aria-current="page">', '<a href="./" hreflang="bg" lang="bg" aria-current="page">', header)
    # a page without a Bulgarian twin (the legal texts, until the client sends theirs): no bg alternate,
    # and the BG button leads to the Bulgarian home page, marked so main.js does not follow it on translation
    if meta.get('twin') == 'none':
        head = re.sub(r'\s*<link rel="alternate" hreflang="bg" href="[^"]*">', '', head)
        header = re.sub(r'<a href="[^"]*" hreflang="bg" lang="bg">', f'<a href="{up_other}bg/" hreflang="bg" lang="bg" data-no-twin>', header)
    scripts = f'  <script src="{prefix}assets/js/main.js" defer></script>\n'
    for extra in filter(None, (x.strip() for x in meta.get('scripts', '').split(','))):
        scripts += f'  <script src="{prefix}{extra}" defer></script>\n'
    page = head + '</head>\n' + s[s.index('<body>'):s.index('  <a class="skip-link"')] + header + main + footer + scripts + '</body>\n</html>\n'
    out = ROOT + ('bg/' if lang == 'bg' else '') + slug + '/index.html'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(page)
    return out


if __name__ == '__main__':
    try:
        manifest = json.load(open(ROOT + 'assets/img/pages/manifest.json'))
    except FileNotFoundError:
        manifest = {}
    for p in sys.argv[1:]:
        print('built', build(p, manifest))
