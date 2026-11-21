"""Pixel-art texture of a boss model (boss pipeline step 2), palette only.

Used by bbmodel.py. From the cubes of a model (concept boxes), the paint details (concept `paint: true`
parts + the extra `paint` list of model.yml) and the dungeon palette, it paints every cube face at
1 px = 1/16 block, then packs the faces into one texture and returns the UV rectangle of each face.

How a face pixel gets its colour (always a palette colour):
  1. the cube's colour;
  2. a small procedural material detail for that colour (bark grain, flecks, gill stripes ...), from a
     hash of the pixel's position, so it is the same on every run and continuous over neighbouring faces;
  3. every paint part of the SAME bone that covers the pixel, in order (the last one wins). A paint part
     is a volume: it colours the face pixels lying on or inside it (a flat decal has one size of 0).
     A paint part that touches no visible face of its own bone is then tried on the other bones (the
     concept draws a few details over the neighbouring bone); bbmodel.py prints which ones.

How the texture stays small (a mini-boss must fit 128 x 128):
  - a face that no player can ever see (every pixel covered by another cube of the same bone) gets no
    texture at all;
  - a face whose visible pixels all have one colour is mapped on a shared 8 x 8 swatch of that colour
    (8 x 8 aligned blocks, so the colour survives mipmaps);
  - faces with identical pixels (also mirrored) share one rectangle;
  - everything else gets its own rectangle at 1:1.

Face orientation = Blockbench / Java model convention (u left to right, v top to bottom):
    north (-z): u = +x -> -x, v = +y -> -y      south (+z): u = -x -> +x, v = +y -> -y
    east  (+x): u = +z -> -z, v = +y -> -y      west  (-x): u = -z -> +z, v = +y -> -y
    up    (+y): u = -x -> +x, v = -z -> +z      down  (-y): u = -x -> +x, v = +z -> -z
"""
from __future__ import annotations

from PIL import Image

# face -> (axis of the normal, sign)
FACES = {"north": (2, -1), "south": (2, 1), "east": (0, 1), "west": (0, -1), "up": (1, 1), "down": (1, -1)}
EMISSIVE = {"cyan_glow", "glow_core", "lilac_glow"}   # style guides: the *_glow colours and glow_core
SWATCH = 8


def face_size(size, face):
    w, h, d = size
    return {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}[face]


def face_cell(lo, size, face, i, j):
    """World cell (lower corner x, y, z) of the face pixel (i, j). On the normal axis: the face plane."""
    x0, y0, z0 = lo
    x1, y1, z1 = x0 + size[0], y0 + size[1], z0 + size[2]
    if face == "north":
        return (x1 - 1 - i, y1 - 1 - j, z0)
    if face == "south":
        return (x0 + i, y1 - 1 - j, z1)
    if face == "east":
        return (x1, y1 - 1 - j, z1 - 1 - i)
    if face == "west":
        return (x0, y1 - 1 - j, z0 + i)
    if face == "up":
        return (x0 + i, y1, z0 + j)
    return (x0 + i, y0, z1 - 1 - j)   # down


def _h(*vals) -> float:
    """Deterministic hash of integers -> [0, 1)."""
    x = 0x9E3779B9
    for v in vals:
        x ^= (int(v) + 0x7F4A7C15) & 0xFFFFFFFF
        x = (x * 0x85EBCA6B) & 0xFFFFFFFF
        x ^= x >> 13
        x = (x * 0xC2B2AE35) & 0xFFFFFFFF
        x ^= x >> 16
    return x / 4294967296.0


def material(color, cell, axis, salt, centre=(0, 0)):
    """Procedural detail of a base colour at a world cell. Neighbouring palette shades only (style rule)."""
    x, y, z = cell
    side = axis != 1
    if color == "bark":
        if side:
            col = _h(x, z, salt, 1)
            if col < 0.34 and _h(x, z, y // 6, salt, 2) < 0.72:
                return "night_bark"                      # vertical grain, broken every few pixels
            if _h(x, y, z, salt, 3) < 0.035:
                return "root"                            # a small knot catching the light
        elif _h(x, y, z, salt, 4) < 0.22:
            return "night_bark"
    elif color == "night_bark":
        if _h(x, z, salt, 5) < 0.25 and _h(x, y // 4, z, salt, 6) < 0.5:
            return "bark"
    elif color == "root":
        r = _h(x, y, z, salt, 7)
        if r < 0.10:
            return "bark"                                # worn, pitted knots
        if r > 0.97:
            return "stem_shadow"
    elif color == "cap_deep":
        r = _h(x, y, z, salt, 8)
        if r < 0.05:
            return "cap"
    elif color == "cap":
        if _h(x, y, z, salt, 9) < 0.08:
            return "cap_light"
    elif color == "stem_pale":
        if side and _h(x, z, salt, 10) < 0.3 and _h(x, y // 3, z, salt, 11) < 0.7:
            return "stem_shadow"
    elif color == "lilac_deep":
        if _h(x, y, z, salt, 12) < 0.1:
            return "lilac_glow"                          # sap glints
    elif color == "cyan_deep":
        if not side:                                     # gills seen from below: stripes running outwards
            dx, dz = x - centre[0], z - centre[1]
            stripe = (z if abs(dx) >= abs(dz) else x) % 2 == 0
            if stripe and _h(x, z, salt, 13) < 0.92:
                return "cyan_glow"
    return color


class Painter:
    """Paints the faces of a list of cubes and packs them.

    cubes:  [{bone, from: [x, y, z], size: [w, h, d], color}]   (whole pixels)
    paints: [{bone, from, size, color}]                          (volumes or flat decals)
    palette: {name: (r, g, b)}
    mirror_bones: bones painted with a left/right symmetric hash (mirror twins share texture space)
    plain: {bone: [faces]} faces left without procedural detail; `up` or `up:cap_deep` (that colour only)
    """

    def __init__(self, cubes, paints, palette, mirror_bones=(), plain=None, gill_centre=(0, 0)):
        self.gill_centre = tuple(gill_centre)
        self.cubes, self.palette = cubes, palette
        self.mirror_bones = set(mirror_bones)
        self.plain = plain or {}
        self.paints: dict[str, list] = {}
        for p in paints:
            self.paints.setdefault(p["bone"], []).append(p)
        self.paint_hits = {id(p): 0 for p in paints}
        self.fallback: list = []   # paints applied whatever the bone (see Painter.orphans)
        self.by_bone: dict[str, list] = {}
        for c in cubes:
            self.by_bone.setdefault(c["bone"], []).append(c)

    # ------------------------------------------------------------------ one face
    def visible(self, cube, face, cell):
        """False when the pixel is buried in another cube of the same bone."""
        axis, sign = FACES[face]
        q = [cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5]
        q[axis] = cell[axis] + 0.5 * sign
        for o in self.by_bone[cube["bone"]]:
            if o is cube:
                continue
            lo, s = o["from"], o["size"]
            if all(lo[a] < q[a] < lo[a] + s[a] for a in range(3)):
                return False
        return True

    def colour(self, cube, face, cell):
        axis, _ = FACES[face]
        bone = cube["bone"]
        name = cube["color"]
        plain = self.plain.get(bone, ())
        if face not in plain and f"{face}:{cube['color']}" not in plain:
            mc = cell
            if bone in self.mirror_bones and cell[0] < 0:
                mc = (-cell[0] - (0 if axis == 0 else 1), cell[1], cell[2])
            name = material(name, mc, axis, 0, self.gill_centre)
        for p in list(self.paints.get(bone, ())) + [q for q in self.fallback if q["bone"] != bone]:
            lo, s = p["from"], p["size"]
            ok = True
            for a in range(3):
                if a == axis:
                    if not lo[a] <= cell[a] <= lo[a] + s[a]:
                        ok = False
                        break
                elif not (lo[a] <= cell[a] and cell[a] + 1 <= lo[a] + s[a]):
                    ok = False
                    break
            if ok:
                name = p["color"]
                self.paint_hits[id(p)] += 1
        return name

    def paint_face(self, cube, face):
        """(w, h, pixels, mask): pixels = colour names row by row, mask = visible flags."""
        w, h = face_size(cube["size"], face)
        px, mask = [], []
        for j in range(h):
            for i in range(w):
                cell = face_cell(cube["from"], cube["size"], face, i, j)
                v = self.visible(cube, face, cell)
                mask.append(v)
                px.append(self.colour(cube, face, cell) if v else cube["color"])
        return w, h, px, mask

    # ------------------------------------------------------------------ all faces + packing
    def build(self, width, height):
        """Returns (image, uv, stats). uv[(cube index, face)] = [u1, v1, u2, v2] or None (no texture)."""
        uv: dict = {}
        rects: list = []          # [w, h, px, users[(key, flipped)]]
        index: dict = {}
        swatch_users: dict[str, list] = {}
        emissive_share: dict[int, list] = {}
        stats = {"faces": 0, "hidden": 0, "swatch": 0, "shared": 0, "unique": 0}
        for ci, cube in enumerate(self.cubes):
            em = emissive_share.setdefault(ci, [0, 0])
            for face in FACES:
                stats["faces"] += 1
                w, h, px, mask = self.paint_face(cube, face)
                seen = [c for c, m in zip(px, mask) if m]
                if not seen:
                    uv[(ci, face)] = None
                    stats["hidden"] += 1
                    continue
                em[0] += sum(1 for c in seen if c in EMISSIVE)
                em[1] += len(seen)
                if len(set(seen)) == 1:
                    swatch_users.setdefault(seen[0], []).append((ci, face))
                    stats["swatch"] += 1
                    continue
                key = (w, h, tuple(px))
                flipped = (w, h, tuple(c for j in range(h) for c in reversed(px[j * w:(j + 1) * w])))
                if key in index:
                    rects[index[key]][3].append(((ci, face), False))
                    stats["shared"] += 1
                elif flipped in index:
                    rects[index[flipped]][3].append(((ci, face), True))
                    stats["shared"] += 1
                else:
                    index[key] = len(rects)
                    rects.append([w, h, px, [((ci, face), False)]])
                    stats["unique"] += 1

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        # swatches: one row of aligned 8 x 8 blocks at the top
        names = sorted(swatch_users, key=list(self.palette).index)
        per_row = width // SWATCH
        rows = (len(names) + per_row - 1) // per_row
        for n, name in enumerate(names):
            x, y = (n % per_row) * SWATCH, (n // per_row) * SWATCH
            img.paste((*self.palette[name], 255), (x, y, x + SWATCH, y + SWATCH))
            for key in swatch_users[name]:
                uv[key] = [x + 2, y + 2, x + SWATCH - 2, y + SWATCH - 2]
        top = rows * SWATCH
        placed = _pack([(r[0], r[1]) for r in rects], width, height - top)
        area = sum(r[0] * r[1] for r in rects)
        if placed is None:
            raise ValueError(f"texture {width}x{height} is too small: {area} px of faces to pack "
                             f"({len(rects)} rectangles) in {width * (height - top)} px")
        pix = img.load()
        for (w, h, px, users), (x, y) in zip(rects, placed):
            y += top
            for j in range(h):
                for i in range(w):
                    pix[x + i, y + j] = (*self.palette[px[j * w + i]], 255)
            for key, flip in users:
                uv[key] = [x + w, y, x, y + h] if flip else [x, y, x + w, y + h]
        stats["area"] = area
        stats["fill"] = (area + len(names) * SWATCH * SWATCH) / (width * height)
        stats["emissive"] = {ci: (e / t if t else 0.0) for ci, (e, t) in emissive_share.items()}
        return img, uv, stats

    def orphans(self, paints):
        """Paints that touch no visible face of their own bone (call after a first build()). The concept
        draws some details over a neighbouring bone (teeth of a jaw seen against the throat behind it):
        pass them back as `fallback` to a new Painter and they are painted on whatever face they lie on."""
        return [p for p in paints if self.paint_hits.get(id(p), 0) == 0]

    def unused_paints(self, paints):
        return [p for p in paints if self.paint_hits.get(id(p), 0) == 0]


def _pack(sizes, width, height):
    """Skyline (bottom-left) packing. Returns [(x, y)] in the order of `sizes`, or None if it does not fit."""
    order = sorted(range(len(sizes)), key=lambda k: (-sizes[k][1], -sizes[k][0]))
    sky = [0] * width
    out: list = [None] * len(sizes)
    for k in order:
        w, h = sizes[k]
        if w > width:
            return None
        best = None
        for x in range(0, width - w + 1):
            y = max(sky[x:x + w])
            waste = sum(y - s for s in sky[x:x + w])
            if y + h <= height and (best is None or (y, waste) < best[0]):
                best = ((y, waste), x)
        if best is None:
            return None
        (y, _), x = best
        for i in range(x, x + w):
            sky[i] = y + h
        out[k] = (x, y)
    return out
