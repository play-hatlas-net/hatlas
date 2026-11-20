"""Concept sheet drawer (boss pipeline step 1).

Reads   <boss>/boss.yml            (id, kind, size)
        <boss>/concept/concept.yml (the character as boxes, see below)
        <dungeon>/style.md         (palette)
Writes  <boss>/concept/front.png, side.png, back.png   views with the dashed hitbox and bone names
        <boss>/concept/front_1x.png, side_1x.png, back_1x.png   raw pixel art, 1 px = 1/16 block,
                                                                palette only (checked by validate.py)
        <boss>/concept/palette.png                              the dungeon palette, used colours marked
        <boss>/concept/sheet.png                                everything on one image for the user gate

concept.yml:
    parts:
      - {bone: head, from: [x, y, z], size: [w, h, d], color: gill_pale}                 # a cube
      - {bone: head, from: [x, y, z], size: [2, 2, 0], color: eye_amber, paint: true}    # texture detail
Units are pixels (1/16 block). y is up from the ground, the character faces -z, its right side is +x
(Blockbench: a model faces north). `paint: true` parts are details painted on the texture: they are
drawn but not counted as cubes, and one of their sizes may be 0 (a flat decal on a face).
Views: front (seen from -z), side (seen from +x, the character faces right), back (seen from +z).

Usage: python bosses/_tools/concept_sheet.py bosses/<dungeon>/<boss> [--scale N]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from common import CUBE_BUDGET, PX_PER_BLOCK, hexa, load_palette, load_yaml  # noqa: E402

BG = (35, 35, 43)
PANEL = (46, 46, 56)
TEXT = (232, 232, 232)
DIM = (150, 150, 162)
HITBOX = (255, 90, 90)
GROUND = (110, 110, 122)
MARGIN = 3  # model pixels around the drawing

# view -> (screen axis, sign), (depth axis, sign): a bigger depth value is nearer to the viewer
VIEWS = {
    "front": ((0, -1), (2, -1)),
    "side": ((2, -1), (0, +1)),
    "back": ((0, +1), (2, +1)),
}


def font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


def part_rect(part, view):
    """Screen rectangle (u0, u1, y0, y1) and depth of a part in a view, in model pixels."""
    (ua, us), (da, ds) = VIEWS[view]
    lo = part["from"]
    hi = [lo[i] + part["size"][i] for i in range(3)]
    u0, u1 = sorted((us * lo[ua], us * hi[ua]))
    depth = max(ds * lo[da], ds * hi[da])
    return u0, u1, lo[1], hi[1], depth


def render_view(parts, palette, view, bounds):
    """Z-buffered orthographic view. Returns an RGBA image at 1 px = 1/16 block."""
    u_min, u_max, y_max = bounds
    w, h = u_max - u_min, y_max
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    zbuf = {}
    for part in parts:
        u0, u1, y0, y1, depth = part_rect(part, view)
        if u1 <= u0 or y1 <= y0:
            continue  # a decal seen edge-on
        rgb = palette[part["color"]]
        for u in range(u0, u1):
            for y in range(y0, y1):
                sx, sy = u - u_min, h - 1 - y
                if 0 <= sx < w and 0 <= sy < h and depth >= zbuf.get((sx, sy), -10**9):
                    zbuf[(sx, sy)] = depth
                    px[sx, sy] = (*rgb, 255)
    return img


def dashed_rect(draw, box, color, dash=6, width=2):
    x0, y0, x1, y1 = box
    for xa, ya, xb, yb in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        length = max(abs(xb - xa), abs(yb - ya))
        steps = max(1, int(length // dash))
        for i in range(0, steps, 2):
            t0, t1 = i / steps, min(1, (i + 1) / steps)
            draw.line((xa + (xb - xa) * t0, ya + (yb - ya) * t0, xa + (xb - xa) * t1, ya + (yb - ya) * t1),
                      fill=color, width=width)


def annotate(raw, parts, view, bounds, hitbox_px, scale, title):
    """Upscaled view with ground line, dashed hitbox and bone names on both sides."""
    u_min, u_max, y_max = bounds
    label_w, top, bottom = 118, 30, 26
    w, h = raw.width * scale, raw.height * scale
    img = Image.new("RGB", (w + 2 * label_w, h + top + bottom), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((label_w, top, label_w + w, top + h), fill=PANEL)
    img.paste(raw.resize((w, h), Image.NEAREST), (label_w, top), raw.resize((w, h), Image.NEAREST))
    f, fs = font(15), font(12)

    def sx(u):
        return label_w + (u - u_min) * scale

    def sy(y):
        return top + (y_max - y) * scale

    draw.line((label_w, sy(0), label_w + w, sy(0)), fill=GROUND, width=2)
    half = hitbox_px[0] / 2
    dashed_rect(draw, (sx(-half), sy(hitbox_px[1]), sx(half), sy(0)), HITBOX)
    draw.text((label_w + 4, 6), title, font=f, fill=TEXT)
    draw.text((label_w + 4, top + h + 6), "dashed = hitbox %g x %g px" % hitbox_px, font=fs, fill=HITBOX)

    # bone labels: centre of each bone's cubes in this view, alternating sides, no overlap
    boxes = {}
    for part in parts:
        if part.get("paint"):
            continue
        u0, u1, y0, y1, _ = part_rect(part, view)
        b = boxes.setdefault(part["bone"], [u0, u1, y0, y1])
        b[0], b[1], b[2], b[3] = min(b[0], u0), max(b[1], u1), min(b[2], y0), max(b[3], y1)
    sides = {"l": [], "r": []}
    for bone, (u0, u1, y0, y1) in boxes.items():
        cu, cy = (u0 + u1) / 2, (y0 + y1) / 2
        sides["l" if cu < 0 else "r"].append((sy(cy), sx(cu), bone))
    for side, items in sides.items():
        last = -100
        for ty, tx, bone in sorted(items):
            ly = max(ty - 7, last + 15, top)
            last = ly
            if side == "l":
                tw = draw.textlength(bone, font=fs)
                lx = label_w - 10 - tw
                draw.line((lx + tw + 3, ly + 7, tx, ty), fill=DIM, width=1)
            else:
                lx = label_w + w + 10
                draw.line((lx - 3, ly + 7, tx, ty), fill=DIM, width=1)
            draw.ellipse((tx - 2, ty - 2, tx + 2, ty + 2), fill=TEXT)
            draw.text((lx, ly), bone, font=fs, fill=TEXT)
    return img


def palette_image(palette, used):
    sw, row_h, cols = 30, 38, 4
    col_w = 230
    rows = (len(palette) + cols - 1) // cols
    img = Image.new("RGB", (cols * col_w + 16, rows * row_h + 16), BG)
    draw = ImageDraw.Draw(img)
    fs = font(13)
    for i, (name, rgb) in enumerate(palette.items()):
        x, y = 8 + (i % cols) * col_w, 8 + (i // cols) * row_h
        draw.rectangle((x, y, x + sw, y + sw), fill=rgb, outline=TEXT if name in used else DIM)
        draw.text((x + sw + 8, y), name + ("" if name in used else "  (unused)"), font=fs,
                  fill=TEXT if name in used else DIM)
        draw.text((x + sw + 8, y + 15), hexa(rgb), font=fs, fill=DIM)
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("boss_dir", type=Path)
    ap.add_argument("--scale", type=int, default=0, help="screen pixels per model pixel (default: auto)")
    args = ap.parse_args()
    boss_dir = args.boss_dir.resolve()
    spec = load_yaml(boss_dir / "boss.yml")
    concept = load_yaml(boss_dir / "concept" / "concept.yml")
    palette = load_palette(boss_dir.parent / "style.md")
    parts = concept["parts"]

    for i, p in enumerate(parts):
        if p["color"] not in palette:
            print(f"part {i} ({p['bone']}): colour '{p['color']}' is not in style.md", file=sys.stderr)
            return 1
        if any(not isinstance(v, int) for v in p["from"] + p["size"]):
            print(f"part {i} ({p['bone']}): from/size must be whole pixels (1/16 grid)", file=sys.stderr)
            return 1
        if not p.get("paint") and min(p["size"]) <= 0:
            print(f"part {i} ({p['bone']}): a cube needs three sizes > 0", file=sys.stderr)
            return 1

    hitbox_px = (spec["size"]["width"] * PX_PER_BLOCK, spec["size"]["height"] * PX_PER_BLOCK)
    # same frame for the three views, so they line up on the sheet
    reach = max(max(abs(p["from"][a]), abs(p["from"][a] + p["size"][a])) for p in parts for a in (0, 2))
    reach = int(max(reach, hitbox_px[0] / 2)) + MARGIN
    top_y = int(max(max(p["from"][1] + p["size"][1] for p in parts), hitbox_px[1])) + MARGIN
    bounds = (-reach, reach, top_y)
    scale = args.scale or max(4, min(24, 620 // top_y))

    out = boss_dir / "concept"
    cubes = sum(1 for p in parts if not p.get("paint"))
    budget = CUBE_BUDGET[spec["kind"]]
    views = []
    for view, title in (("front", "FRONT"), ("side", "SIDE (right)"), ("back", "BACK")):
        raw = render_view(parts, palette, view, bounds)
        raw.save(out / f"{view}_1x.png")
        big = annotate(raw, parts, view, bounds, hitbox_px, scale, title)
        big.save(out / f"{view}.png")
        views.append(big)
    used = {p["color"] for p in parts}
    pal = palette_image(palette, used)
    pal.save(out / "palette.png")

    head = 40
    sheet_w = max(sum(v.width for v in views), pal.width)
    sheet = Image.new("RGB", (sheet_w, head + views[0].height + pal.height), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), "%s (%s)   hitbox %g x %g blocks   %d cubes drawn / budget %d   1 px = 1/16 block, x%d"
           % (spec["id"], spec["kind"], spec["size"]["width"], spec["size"]["height"], cubes, budget, scale),
           font=font(17), fill=TEXT)
    x = 0
    for v in views:
        sheet.paste(v, (x, head))
        x += v.width
    sheet.paste(pal, (0, head + views[0].height))
    sheet.save(out / "sheet.png")
    print(f"{spec['id']}: {cubes} cubes (budget {budget}), {len(parts) - cubes} painted details, "
          f"{len(used)} colours, scale x{scale} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
