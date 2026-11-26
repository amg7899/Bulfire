"""Draws the transparent landscape behind the hero, the page heads, the menu and the footer:
forested hills in layers of translucent white with white edges. A sister of the wind-farm
landscape on ecoes.eu (tools/landscape.py there); here the ridges carry conifer forest, the
forests BULFIRE's trucks and tractors protect. White, so it only lightens the light it sits on.

    python3 tools/forest.py        (writes assets/img/deco/forest.svg and forest-hero.svg)

Two scenes, each 2400 x 520 units:
- forest.svg (page heads, menu, footer): forest on the far and middle ridges, densest on the
  right; the canvas reaches 3200 units further left, so it covers wide screens when it is
  anchored bottom right.
- forest-hero.svg (Home): symmetrical for the centred headline, a low clearing in the middle
  and forest on the ridges at each side; scaled to the width of the hero.
Standard library only. Trees are placed by a seeded random generator, so reruns give the same
drawing; change SEED or the stands below to change the forest.
"""
import math
import os
import random

W, H = 2400, 520
SEED = 1997                 # the year BULFIRE started


def num(v):
    s = f"{v:.1f}"
    s = s[:-2] if s.endswith(".0") else s
    return "0" if s == "-0" else s


def bump(x, c, h, w):
    return h * math.exp(-((x - c) / w) ** 2)


def far(x):
    return (420 - bump(x, 1950, 64, 620) - bump(x, 1150, 26, 300) - bump(x, -700, 24, 420)
            - bump(x, -2300, 30, 520) - 8 * math.sin(x / 230) - 5 * math.sin(x / 101 + 1.3))


def mid(x):
    return (456 - bump(x, 1650, 36, 380) - bump(x, 2300, 30, 260) - bump(x, 700, 24, 330)
            - bump(x, -1300, 22, 380) - bump(x, -2800, 18, 420) - 6 * math.sin(x / 170 + .4))


def near(x):
    return (494 - bump(x, 2150, 34, 420) - bump(x, 950, 16, 380) - bump(x, -1800, 14, 500)
            - 4 * math.sin(x / 140 + 2.1))


def hero_far(x):
    return (442 - bump(x, 320, 86, 380) - bump(x, 2080, 92, 420) - 8 * math.sin(x / 230)
            - 4 * math.sin(x / 101 + 1.3))


def hero_mid(x):
    return (468 - bump(x, 640, 30, 340) - bump(x, 1760, 34, 360) - 6 * math.sin(x / 170 + .4))


def hero_near(x):
    return 496 - bump(x, 1200, 12, 620) - 4 * math.sin(x / 140 + 2.1)


# Conifer silhouette, one side from the tip down: (distance from the trunk axis as a share of the
# tree's width, height as a share of the tree's height). Monotonic, so overlapping trees merge into
# one treeline; the short flat steps are the tiers of a spruce.
PROFILE = [(0, 1), (.13, .74), (.18, .72), (.31, .44), (.36, .42), (.5, .04), (.56, 0)]


def tree_height(dx, w, h):
    u = abs(dx) / w
    for (u0, v0), (u1, v1) in zip(PROFILE, PROFILE[1:]):
        if u <= u1:
            return h * (v0 + (v1 - v0) * (u - u0) / (u1 - u0))
    return 0.0


def stand(rng, x0, x1, h0, h1, gap=(.5, .95), skip=.08, taper=.22):
    """Trees from x0 to x1, heights between h0 and h1, spaced by a share of their width. Towards
    both ends of the stand the trees get smaller (over `taper` of its length), so a forest thins
    out into the open hill instead of ending in a wall."""
    trees, x = [], x0
    span = x1 - x0
    while x < x1:
        edge = min(x - x0, x1 - x) / (span * taper)
        k = .35 + .65 * min(1, edge) ** .7
        h = rng.uniform(h0, h1) * k
        w = h * rng.uniform(.44, .54)
        if rng.random() > skip:
            trees.append((x, w, h))
        x += w * rng.uniform(*gap)
    return trees


def treeline(fn, trees, ext, step=3):
    """The ridge with its trees as one outline (the highest point at each x), simplified."""
    x0, x1 = -ext - 40, W + 40
    trees = sorted(trees)
    pts, i = [], 0
    x = x0
    while x <= x1:
        top = 0.0
        while i < len(trees) and trees[i][0] + trees[i][1] < x:
            i += 1
        j = i
        while j < len(trees) and trees[j][0] - trees[j][1] <= x:
            tx, tw, th = trees[j]
            top = max(top, tree_height(x - tx, tw, th))
            j += 1
        pts.append((x, fn(x) - top))
        x += step
    # tree tips need their exact points, the sampling may step over them
    for tx, tw, th in trees:
        pts.append((tx, fn(tx) - th))
    pts.sort()
    return simplify(pts, .35)


def simplify(pts, tol):
    """Ramer-Douglas-Peucker, iterative."""
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1
        best, idx = 0, None
        for k in range(a + 1, b):
            px, py = pts[k]
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm
            if d > best:
                best, idx = d, k
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def path(pts):
    d = [f"M{num(pts[0][0])} {num(pts[0][1])}"]
    px, py = pts[0]
    for x, y in pts[1:]:
        d.append(f"l{num(x - px)} {num(y - py)}")
        px, py = px + float(num(x - px)), py + float(num(y - py))
    d.append(f"V{H + 40}H{num(pts[0][0])}Z")
    return "".join(d)


def opacity(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def draw(ext, layers, label):
    ns = ' vector-effect="non-scaling-stroke"'
    edge = f'stroke="#fff" stroke-opacity=".95" stroke-width="1.3" stroke-linejoin="round"{ns}'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-ext} 0 {W + ext} {H}" width="{W + ext}" height="{H}">',
         f"<!-- BULFIRE site: transparent landscape ({label}), drawn by tools/forest.py -->", "<defs>"]
    outlines = [treeline(fn, trees, ext) for fn, trees in layers]
    # each layer is most opaque along its highest point and fades towards the bottom
    for gid, pts, (a0, a1) in zip("fmn", outlines, ((.5, .12), (.56, .16), (.62, .22))):
        top = min(y for x, y in pts if -ext <= x <= W)
        o.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{num(top)}" x2="0" y2="{H}">'
                 f'<stop offset="0" stop-color="#fff" stop-opacity="{opacity(a0)}"/>'
                 f'<stop offset="1" stop-color="#fff" stop-opacity="{opacity(a1)}"/></linearGradient>')
    o.append("</defs>")
    for gid, pts in zip("fmn", outlines):
        o.append(f'<path d="{path(pts)}" fill="url(#{gid})" {edge}/>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main_scene():
    rng = random.Random(SEED)
    ext = 3200
    far_trees = (stand(rng, -3100, -2000, 24, 40, skip=.25) + stand(rng, -900, 250, 22, 38, skip=.3)
                 + stand(rng, 1150, 2440, 30, 54, skip=.05))
    mid_trees = (stand(rng, -2500, -1800, 34, 52, skip=.2) + stand(rng, 420, 900, 34, 54, skip=.2)
                 + stand(rng, 1480, 1900, 44, 72, skip=.05) + stand(rng, 2160, 2440, 44, 70, skip=.05))
    near_trees = stand(rng, 2200, 2470, 90, 130, gap=(.6, .95), skip=0, taper=.12)
    return draw(ext, [(far, far_trees), (mid, mid_trees), (near, near_trees)], "page heads, menu, footer")


def hero_scene():
    rng = random.Random(SEED + 1)
    # forest outside the middle 50% (the centred headline stands there), a clearing under it
    far_trees = stand(rng, -60, 780, 30, 56, skip=.05) + stand(rng, 1620, 2460, 30, 56, skip=.05)
    mid_trees = stand(rng, 100, 580, 44, 74, skip=.08) + stand(rng, 1820, 2320, 44, 74, skip=.08)
    near_trees = (stand(rng, -80, 190, 96, 140, gap=(.6, .95), skip=0, taper=.12)
                  + stand(rng, 2210, 2480, 96, 140, gap=(.6, .95), skip=0, taper=.12))
    return draw(0, [(hero_far, far_trees), (hero_mid, mid_trees), (hero_near, near_trees)], "Home")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img", "deco")
    os.makedirs(out, exist_ok=True)
    for name, svg in (("forest.svg", main_scene()), ("forest-hero.svg", hero_scene())):
        with open(os.path.join(out, name), "w") as fh:
            fh.write(svg)
        print(name, round(len(svg.encode()) / 1024, 1), "KB")
