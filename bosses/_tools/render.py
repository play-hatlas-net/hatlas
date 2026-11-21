"""Preview renders of a boss `.bbmodel` (boss pipeline step 2), without Blockbench.

It reads ONLY the .bbmodel (cubes, per-face UV, embedded texture, bone tree, visibility), so the pictures
show what the file holds, not what the builder meant. A small software renderer (Pillow, painter's
algorithm on texture pixels): the skill names a three.js `render.mjs`; this Python script replaces it
for still pictures because it needs no browser or GPU. Animation previews (step 3) can extend `pose`.

Usage: python bosses/_tools/render.py bosses/<dungeon>/<boss> [--scale N]
Writes into <boss>/out/model/ (git-ignored):
    turntable.png              8 angles (every 45 degrees), seen slightly from above, lit
    turn_<angle>.png           the same 8 pictures, one per file
    compare.png                front / side / back of the model (flat colours, straight on) beside the
                               concept views (concept/*_1x.png)
    below.png                  seen from a player's eye height in front of it, looking up (gills, bulb, eyes)
    mutation_<id>.png          4 angles after each mutation of boss.yml (hide_bones gone, show_bones shown)
    zones.png                  the hit-zone boxes (invisible in game) outlined in their zone colour over
                               the model: front, side, top, three-quarter
    poses.png                  model.yml > pose_checks: rough poses that test the pivots (NOT animations)
    texture_x6.png             the texture, enlarged
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from bbmodel import Model  # noqa: E402
from common import load_yaml, match_bones  # noqa: E402

BG = (35, 35, 43)
PANEL = (98, 100, 112)
TEXT = (232, 232, 232)
DIM = (160, 160, 172)

# face -> (top-left corner selector, U direction, V direction, normal); selectors pick lo (0) or hi (1)
FACE_GEOM = {
    "north": ((1, 1, 0), (-1, 0, 0), (0, -1, 0), (0, 0, -1)),
    "south": ((0, 1, 1), (1, 0, 0), (0, -1, 0), (0, 0, 1)),
    "east": ((1, 1, 1), (0, 0, -1), (0, -1, 0), (1, 0, 0)),
    "west": ((0, 1, 0), (0, 0, 1), (0, -1, 0), (-1, 0, 0)),
    "up": ((0, 1, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)),
    "down": ((0, 0, 1), (1, 0, 0), (0, 0, -1), (0, -1, 0)),
}


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------------------- maths
def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_identity():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def mat_rot_about(pivot, deg):
    """Rotation by [x, y, z] degrees (Rz * Ry * Rx, right-handed) about a pivot."""
    rx, ry, rz = (math.radians(d) for d in deg)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    r = [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
         [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
         [-sy, cy * sx, cy * cx]]
    m = mat_identity()
    for i in range(3):
        for j in range(3):
            m[i][j] = r[i][j]
        m[i][3] = pivot[i] - sum(r[i][j] * pivot[j] for j in range(3))
    return m


def apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3] for i in range(3))


def rotate(m, v):
    return tuple(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


# ---------------------------------------------------------------------------------------- scene
class Scene:
    """Texture pixels of the visible cubes as world quads: [(4 corners, normal, rgb, emissive)]."""

    def __init__(self, model: Model, hide=(), show=(), pose=None):
        self.model = model
        pose = pose or {}
        tex = model.textures[0]
        tw, th = tex.size
        rw = model.resolution.get("width", tw)
        rh = model.resolution.get("height", th)
        px = tex.load()
        world: dict[str, list] = {}

        def bone_matrix(b):
            if b in world:
                return world[b]
            v = model.bones[b]
            local = mat_rot_about(v["pivot"], pose[b]) if b in pose else mat_identity()
            world[b] = mat_mul(bone_matrix(v["parent"]), local) if v["parent"] else local
            return world[b]

        self.quads = []
        for bone, cube in model.cubes():
            vis = (model.shown(bone) and cube.get("visibility", True) is not False and bone not in hide) or bone in show
            if not vis:
                continue
            m = bone_matrix(bone)
            lo, hi = cube["from"], cube["to"]
            size = [hi[a] - lo[a] for a in range(3)]
            glow = bool(cube.get("light_emission")) or "glow" in cube["name"].lower()
            for face, (sel, du, dv, n) in FACE_GEOM.items():
                f = cube["faces"].get(face) or {}
                if f.get("texture") is None:
                    continue
                u1, v1, u2, v2 = f["uv"]
                w = int(round(abs(du[0]) * size[0] + abs(du[1]) * size[1] + abs(du[2]) * size[2]))
                h = int(round(abs(dv[0]) * size[0] + abs(dv[1]) * size[1] + abs(dv[2]) * size[2]))
                tl = [hi[a] if sel[a] else lo[a] for a in range(3)]
                wn = rotate(m, n)
                # grid of transformed corner points
                grid = [[apply(m, (tl[0] + du[0] * i + dv[0] * j, tl[1] + du[1] * i + dv[1] * j,
                                   tl[2] + du[2] * i + dv[2] * j)) for i in range(w + 1)] for j in range(h + 1)]
                for j in range(h):
                    for i in range(w):
                        tx = int((u1 + (i + 0.5) / w * (u2 - u1)) * tw / rw)
                        ty = int((v1 + (j + 0.5) / h * (v2 - v1)) * th / rh)
                        c = px[min(max(tx, 0), tw - 1), min(max(ty, 0), th - 1)]
                        if c[3] == 0:
                            continue
                        self.quads.append(((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]),
                                           wn, c[:3], glow))
        pts = [p for q in self.quads for p in q[0]]
        self.radius = max((math.hypot(p[0], p[2]) for p in pts), default=1.0)
        self.top = max((p[1] for p in pts), default=1.0)
        self.bottom = min(min((p[1] for p in pts), default=0.0), 0.0)

    def camera(self, yaw, pitch, scale, frame=None):
        """(right, up, fwd, project(point) -> screen xy, picture size) of an orthographic view."""
        a, p = math.radians(yaw), math.radians(pitch)
        fh = (math.sin(a), 0.0, math.cos(a))
        right = (-math.cos(a), 0.0, math.sin(a))
        fwd = (fh[0] * math.cos(p), -math.sin(p), fh[2] * math.cos(p))
        up = (fh[0] * math.sin(p), math.cos(p), fh[2] * math.sin(p))
        radius, top, bottom = frame or (self.radius, self.top, self.bottom)
        margin = 3
        half_w = radius + margin
        y_hi = top * math.cos(p) + radius * abs(math.sin(p)) + margin
        y_lo = bottom * math.cos(p) - radius * abs(math.sin(p)) - margin
        size = (int(2 * half_w * scale), int((y_hi - y_lo) * scale))
        return right, up, fwd, (lambda c: ((dot(c, right) + half_w) * scale, (y_hi - dot(c, up)) * scale)), size

    def draw(self, yaw, pitch, scale, lit=True, frame=None, dim=1.0):
        """Orthographic picture. yaw 0 = seen from the front (-z); 270 = from its right side (+x)."""
        right, up, fwd, project, (w, h) = self.camera(yaw, pitch, scale, frame)
        light = (-fwd[0] * 0.6 + right[0] * 0.5, 0.75, -fwd[2] * 0.6 + right[2] * 0.5)
        ln = math.sqrt(dot(light, light))
        light = tuple(v / ln for v in light)
        img = Image.new("RGB", (w, h), PANEL)
        d = ImageDraw.Draw(img)
        items = []
        for corners, n, rgb, glow in self.quads:
            if dot(n, fwd) >= -1e-6:
                continue
            depth = sum(dot(c, fwd) for c in corners) / 4
            if lit and not glow:
                k = 0.55 + 0.45 * max(0.0, dot(n, light))
                rgb = tuple(int(v * k) for v in rgb)
            if dim != 1.0:
                rgb = tuple(int(PANEL[k] + (v - PANEL[k]) * dim) for k, v in enumerate(rgb))
            poly = [project(c) for c in corners]
            items.append((depth, poly, rgb))
        items.sort(key=lambda t: -t[0])
        for _, poly, rgb in items:
            d.polygon(poly, fill=rgb, outline=rgb)
        return img


def tile(img, title, caption=""):
    top, bottom = 26, 20 if caption else 6
    out = Image.new("RGB", (img.width + 12, img.height + top + bottom), BG)
    out.paste(img, (6, top))
    d = ImageDraw.Draw(out)
    d.text((8, 5), title, font=font(15), fill=TEXT)
    if caption:
        d.text((8, top + img.height + 3), caption, font=font(12), fill=DIM)
    return out


def grid(tiles, cols):
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    w = max(sum(t.width for t in r) for r in rows)
    h = sum(max(t.height for t in r) for r in rows)
    out = Image.new("RGB", (w, h), BG)
    y = 0
    for r in rows:
        x = 0
        for t in r:
            out.paste(t, (x, y))
            x += t.width
        y += max(t.height for t in r)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("boss_dir", type=Path)
    ap.add_argument("--scale", type=float, default=0, help="screen pixels per model pixel (default: auto)")
    args = ap.parse_args()
    boss_dir = args.boss_dir.resolve()
    spec = load_yaml(boss_dir / "boss.yml")
    mid = spec["id"]
    model = Model(boss_dir / f"{mid}.bbmodel")
    rig = load_yaml(boss_dir / "model.yml") if (boss_dir / "model.yml").exists() else {}
    out = boss_dir / "out" / "model"
    out.mkdir(parents=True, exist_ok=True)
    rest = Scene(model)
    scale = args.scale or max(3.0, min(14.0, round(420 / (rest.top + rest.radius * 0.35))))
    frame = (rest.radius, rest.top, rest.bottom)

    # turntable
    tiles = []
    names = {0: "front", 45: "front, its left", 90: "its left side", 135: "back, its left", 180: "back",
             225: "back, its right", 270: "its right side", 315: "front, its right"}
    for yaw in range(0, 360, 45):
        img = rest.draw(yaw, 18, scale, frame=frame)
        img.save(out / f"turn_{yaw:03d}.png")
        tiles.append(tile(img, f"{yaw} deg: {names[yaw]}"))
    grid(tiles, 4).save(out / "turntable.png")

    # model beside the concept
    cdir = boss_dir / "concept"
    tiles = []
    cs = max(2.0, scale * 0.8)
    for view, yaw in (("front", 0), ("side", 270), ("back", 180)):
        m_img = rest.draw(yaw, 0, cs, lit=False, frame=frame)
        tiles.append(tile(m_img, f"MODEL {view}", "flat colours, straight on"))
        cfile = cdir / f"{view}_1x.png"
        if cfile.exists():
            c = Image.open(cfile).convert("RGBA")
            big = c.resize((int(c.width * cs), int(c.height * cs)), Image.NEAREST)
            panel = Image.new("RGB", big.size, PANEL)
            panel.paste(big, (0, 0), big)
            tiles.append(tile(panel, f"CONCEPT {view}", "approved at the design gate"))
    grid(tiles, 2 if rest.radius * cs > 330 else 6).save(out / "compare.png")

    # from below (what a player standing in front of it sees)
    tiles = [tile(rest.draw(yaw, -35, scale, frame=frame), f"from below, {label}")
             for yaw, label in ((0, "front"), (315, "front, its right"), (45, "front, its left"), (180, "back"))]
    grid(tiles, 4).save(out / "below.png")

    # after each mutation
    bones = set(model.bones)
    for mut_id, mut in (spec.get("mutations") or {}).items():
        hide = match_bones(mut.get("hide_bones"), bones)
        show = match_bones(mut.get("show_bones"), bones)
        sc = Scene(model, hide=hide, show=show)
        tiles = [tile(sc.draw(yaw, 18, scale, frame=frame), f"AFTER {mut_id}: {names[yaw]}")
                 for yaw in (0, 315, 270, 180)]
        sheet = grid(tiles, 4)
        cap = Image.new("RGB", (sheet.width, sheet.height + 22), BG)
        cap.paste(sheet, (0, 0))
        ImageDraw.Draw(cap).text((8, sheet.height + 3), "hidden: %s   shown: %s" % (
            ", ".join(sorted(hide)) or "none", ", ".join(sorted(show)) or "none"), font=font(12), fill=DIM)
        cap.save(out / f"mutation_{mut_id}.png")

    # hit-zone boxes over the model
    zboxes = model.zone_boxes()
    zmap = rig.get("hit_zone_boxes") or {}
    if zboxes:
        zone_of = {h: z for z, hs in zmap.items() for h in hs}
        zspec = spec.get("hit_zones") or {}

        def zclass(z):
            zone = zspec.get(z) or {}
            if zone.get("break_hp") is not None:
                return "breakable"
            m = zone.get("multiplier", 1)
            return "weak" if m > 1 else "armoured" if m < 1 else "normal"

        colours = {"weak": (255, 210, 63), "armoured": (120, 150, 235), "breakable": (255, 140, 26),
                   "normal": (190, 120, 255), None: (255, 60, 60)}
        tiles = []
        for title, yaw, pitch in (("front", 0, 0), ("its right side", 270, 0), ("top (its front at the bottom)", 0, 90),
                                  ("front, its right", 315, 18), ("back, its left", 135, 18)):
            img = rest.draw(yaw, pitch, scale, lit=pitch not in (0, 90), frame=frame, dim=0.55)
            _, _, _, project, _ = rest.camera(yaw, pitch, scale, frame)
            d = ImageDraw.Draw(img)
            for h, (_, cs) in zboxes.items():
                col = colours[zclass(zone_of[h]) if h in zone_of else None]
                for c in cs:
                    lo, hi = c["from"], c["to"]
                    pt = lambda i, j, k: project((hi[0] if i else lo[0], hi[1] if j else lo[1], hi[2] if k else lo[2]))  # noqa: E731
                    for a in range(3):
                        for u in (0, 1):
                            for v in (0, 1):
                                e0 = [u, v]
                                e0.insert(a, 0)
                                e1 = [u, v]
                                e1.insert(a, 1)
                                d.line((*pt(*e0), *pt(*e1)), fill=col, width=2)
            tiles.append(tile(img, f"HIT-ZONE BOXES, {title}"))
        leg_w = 430
        legend = Image.new("RGB", (leg_w, tiles[0].height), BG)
        d = ImageDraw.Draw(legend)
        d.text((8, 6), "one invisible box per bone of each zone (not drawn in game)", font=font(13), fill=DIM)
        y = 34
        for z, hs in zmap.items():
            zone = zspec.get(z) or {}
            d.rectangle((8, y, 28, y + 18), fill=colours[zclass(z)], outline=TEXT)
            d.text((36, y - 1), "%s: x%g (%s)" % (z, zone.get("multiplier", 1), zclass(z)), font=font(15), fill=TEXT)
            y += 22
            for h, v in hs.items():
                cs = zboxes.get(h, (None, []))[1]
                dims = "%gx%gx%g px" % tuple(cs[0]["to"][a] - cs[0]["from"][a] for a in range(3)) if cs else "MISSING"
                d.text((36, y), "%s on %s: %s%s" % (h, v.get("bone"), dims,
                                                    ", removed by " + v["removed_by"] if v.get("removed_by") else ""),
                       font=font(12), fill=DIM)
                y += 15
            y += 8
        grid(tiles + [legend], 3).save(out / "zones.png")

    # pivot checks
    poses = rig.get("pose_checks") or {}
    if poses:
        tiles = []
        big = (rest.radius * 1.5, rest.top * 1.25, rest.bottom - rest.top * 0.1)
        for name, pose in poses.items():
            unknown = sorted(set(pose) - bones)
            if unknown:
                print(f"pose_checks.{name}: unknown bones {unknown}", file=sys.stderr)
                return 1
            sc = Scene(model, pose=pose)
            for yaw in (315, 270):
                tiles.append(tile(sc.draw(yaw, 12, scale * 0.75, frame=big), f"pivot check '{name}': {names[yaw]}",
                                  "rough pose, not an animation: " + ", ".join(pose)))
        grid(tiles, 4).save(out / "poses.png")

    tex = model.textures[0]
    k = 6 if tex.width <= 128 else 3
    big = tex.resize((tex.width * k, tex.height * k), Image.NEAREST)
    bgi = Image.new("RGB", big.size, (60, 20, 60))     # magenta = unused texture space
    bgi.paste(big, (0, 0), big)
    bgi.save(out / f"texture_x{k}.png")
    print(f"{mid}: {len(rest.quads)} texture pixels drawn, scale x{scale:g} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
