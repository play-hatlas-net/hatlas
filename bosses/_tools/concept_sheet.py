"""Concept sheet drawer (boss pipeline step 1).

Reads   <boss>/boss.yml            (id, kind, size)
        <boss>/concept/concept.yml (the character as boxes, see below)
        <dungeon>/style.md         (palette)
Writes  <boss>/concept/front.png, side.png, back.png   views with the dashed hitbox and bone names
        <boss>/concept/front_1x.png, side_1x.png, back_1x.png   raw pixel art, 1 px = 1/16 block,
                                                                palette only (checked by validate.py)
        <boss>/concept/palette.png                              the dungeon palette, used colours marked
        <boss>/concept/sheet.png                                everything on one image for the user gate
        <boss>/concept/zones.png          only when boss.yml has hit_zones: front and side views with each
                                          zone in a flat colour (weak / armoured / breakable) and a legend
        <boss>/concept/mutation_<id>.png  one per boss.yml mutation: front and side views after it
                                          (hide_bones removed, show_bones drawn)
Bones named by a mutation's show_bones are hidden by default: they are left out of the normal views.

concept.yml:
    parts:
      - {bone: head, from: [x, y, z], size: [w, h, d], color: stem_pale}                 # a cube
      - {bone: head, from: [x, y, z], size: [2, 2, 0], color: cyan_glow, paint: true}    # texture detail
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
from common import (CUBE_BUDGET, PX_PER_BLOCK, hexa, hidden_bones, load_palette, load_yaml,  # noqa: E402
                    match_bones)

BG = (35, 35, 43)
PANEL = (46, 46, 56)
PANEL_FOR_DARK = (98, 100, 112)  # behind a mostly dark character, so its outline still reads on the sheet
TEXT = (232, 232, 232)
DIM = (150, 150, 162)
HITBOX = (255, 90, 90)
GROUND = (190, 190, 200)
MARGIN = 3  # model pixels around the drawing
# zone overlay colours (annotation only, not part of any dungeon palette)
ZONE_COLOURS = {"weak": (255, 210, 63), "armoured": (120, 150, 235), "breakable": (255, 140, 26),
                "normal": (190, 120, 255), "rest": (58, 60, 70)}
ZONE_WORDS = {"weak": "weak point", "armoured": "armoured", "breakable": "breakable", "normal": "zone"}

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


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def panel_colour(raw):
    """Panel behind a view: lighter when most of the drawn pixels are dark (a night palette)."""
    drawn = [(n, c) for n, c in raw.getcolors(1 << 20) if c[3] > 0]
    total = sum(n for n, _ in drawn) or 1
    dark = sum(n for n, c in drawn if luminance(c) < 60)
    return PANEL_FOR_DARK if dark * 2 > total else PANEL


def annotate(raw, parts, view, bounds, hitbox_px, scale, title):
    """Upscaled view with ground line, dashed hitbox and bone names on both sides."""
    u_min, u_max, y_max = bounds
    label_w, top, bottom = 118, 30, 26
    w, h = raw.width * scale, raw.height * scale
    img = Image.new("RGB", (w + 2 * label_w, h + top + bottom), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((label_w, top, label_w + w, top + h), fill=panel_colour(raw))
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


def plain(raw, scale, title, hitbox_px, bounds, caption=""):
    """Upscaled view with a title, the ground line and the dashed hitbox, no bone names."""
    u_min, _, y_max = bounds
    top, bottom, pad = 30, 26, 12
    w, h = raw.width * scale, raw.height * scale
    img = Image.new("RGB", (w + 2 * pad, h + top + bottom), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((pad, top, pad + w, top + h), fill=PANEL_FOR_DARK)
    big = raw.resize((w, h), Image.NEAREST)
    img.paste(big, (pad, top), big)
    gy = top + y_max * scale
    draw.line((pad, gy, pad + w, gy), fill=GROUND, width=2)
    half = hitbox_px[0] / 2
    dashed_rect(draw, (pad + (-half - u_min) * scale, gy - hitbox_px[1] * scale,
                       pad + (half - u_min) * scale, gy), HITBOX, width=1)
    draw.text((pad + 4, 6), title, font=font(15), fill=TEXT)
    if caption:
        draw.text((pad + 4, top + h + 6), caption, font=font(12), fill=DIM)
    return img


def hstack(images, gap=0):
    h = max(i.height for i in images)
    out = Image.new("RGB", (sum(i.width for i in images) + gap * (len(images) - 1), h), BG)
    x = 0
    for i in images:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def zone_class(zone):
    if zone.get("break_hp") is not None:
        return "breakable"
    m = zone.get("multiplier", 1)
    return "weak" if m > 1 else "armoured" if m < 1 else "normal"


def zones_image(spec, parts, bounds, hitbox_px, scale):
    """Front and side views with every hit zone in a flat colour, and a legend. None without hit_zones."""
    zones = {k: v for k, v in (spec.get("hit_zones") or {}).items() if isinstance(v, dict)}
    if not zones:
        return None
    bones = {p["bone"] for p in parts}
    bone_class = {}
    for zone in zones.values():
        for b in match_bones(zone.get("bones"), bones):
            bone_class[b] = zone_class(zone)
    flat = [dict(p, color=bone_class.get(p["bone"], "rest")) for p in parts]
    views = [plain(render_view(flat, ZONE_COLOURS, v, bounds), scale, t, hitbox_px, bounds)
             for v, t in (("front", "HIT ZONES, front"), ("side", "HIT ZONES, side"))]
    fs, lines = font(13), []
    default = (spec.get("hit_zones") or {}).get("default", 1.0)
    for name, zone in zones.items():
        cls = zone_class(zone)
        text = "%s: x%g (%s)" % (name, zone.get("multiplier", 1), ZONE_WORDS[cls])
        extra = []
        if zone.get("heal_interrupt") is not None:
            extra.append("counts x%g against the heal channel" % zone["heal_interrupt"])
        bh = zone.get("break_hp")
        if bh is not None:
            extra.append("breaks after %s damage" % (
                "%g + %g per player above 2" % (bh.get("base", 0), bh.get("per_extra_player", 0))
                if isinstance(bh, dict) else "%g" % bh))
        lines.append((ZONE_COLOURS[cls], text, "; ".join(extra), "bones: " + ", ".join(map(str, zone.get("bones") or []))))
    lines.append((ZONE_COLOURS["rest"], "everything else: x%g" % default, "", ""))
    legend = Image.new("RGB", (430, views[0].height), BG)
    d = ImageDraw.Draw(legend)
    d.text((8, 6), "damage multiplier per zone (before the per-hit cap)", font=font(13), fill=DIM)
    y = 36
    for colour, text, extra, bones_txt in lines:
        d.rectangle((8, y, 30, y + 22), fill=colour, outline=TEXT)
        d.text((40, y - 2), text, font=font(15), fill=TEXT)
        yy = y + 18
        for more in (extra, bones_txt):
            if more:
                d.text((40, yy), more, font=fs, fill=DIM)
                yy += 16
        y = yy + 14
    return hstack(views + [legend])


def mutation_images(spec, parts, palette, bounds, hitbox_px, scale):
    """{mutation id: image}: front and side views once the mutation has happened."""
    out = {}
    bones = {p["bone"] for p in parts}
    default_hidden = hidden_bones(spec, bones)
    for mid, mut in (spec.get("mutations") or {}).items():
        gone = match_bones(mut.get("hide_bones"), bones) | (default_hidden - match_bones(mut.get("show_bones"), bones))
        left = [p for p in parts if p["bone"] not in gone]
        caption = "hidden: %s" % ", ".join(map(str, mut.get("hide_bones") or ["none"]))
        if mut.get("show_bones"):
            caption += "   shown: %s" % ", ".join(map(str, mut["show_bones"]))
        pair = hstack([plain(render_view(left, palette, v, bounds), scale, "AFTER %s, %s" % (mid, v),
                             hitbox_px, bounds) for v in ("front", "side")])
        img = Image.new("RGB", (max(pair.width, int(ImageDraw.Draw(pair).textlength(caption, font=font(12))) + 24),
                                pair.height), BG)
        img.paste(pair, (0, 0))
        ImageDraw.Draw(img).text((16, pair.height - 20), caption, font=font(12), fill=DIM)
        out[mid] = img
    return out


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
    hidden = hidden_bones(spec, {p["bone"] for p in parts})   # shown only by a mutation
    shown = [p for p in parts if p["bone"] not in hidden]
    views = []
    for view, title in (("front", "FRONT"), ("side", "SIDE (right)"), ("back", "BACK")):
        raw = render_view(shown, palette, view, bounds)
        raw.save(out / f"{view}_1x.png")
        big = annotate(raw, shown, view, bounds, hitbox_px, scale, title)
        big.save(out / f"{view}.png")
        views.append(big)
    used = {p["color"] for p in parts}
    pal = palette_image(palette, used)
    pal.save(out / "palette.png")

    # second row of the sheet: hit zones and mutated views, at a smaller scale
    small = max(2, scale * 3 // 5)
    extras = []
    for stale in list(out.glob("mutation_*.png")) + [out / "zones.png"]:
        if stale.exists():
            stale.unlink()
    zimg = zones_image(spec, shown, bounds, hitbox_px, small)
    if zimg is not None:
        zimg.save(out / "zones.png")
        extras.append(zimg)
    for mid, mimg in mutation_images(spec, parts, palette, bounds, hitbox_px, small).items():
        mimg.save(out / f"mutation_{mid}.png")
        extras.append(mimg)
    row2 = hstack(extras, gap=10) if extras else None

    head = 40
    sheet_w = max(sum(v.width for v in views), pal.width, row2.width if row2 else 0)
    sheet = Image.new("RGB", (sheet_w, head + views[0].height + (row2.height if row2 else 0) + pal.height), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), "%s (%s)   hitbox %g x %g blocks   %d cubes drawn / budget %d%s   1 px = 1/16 block, x%d"
           % (spec["id"], spec["kind"], spec["size"]["width"], spec["size"]["height"], cubes, budget,
              " (%d hidden until a mutation)" % sum(1 for p in parts if not p.get("paint") and p["bone"] in hidden)
              if hidden else "", scale),
           font=font(17), fill=TEXT)
    x = 0
    for v in views:
        sheet.paste(v, (x, head))
        x += v.width
    y = head + views[0].height
    if row2:
        sheet.paste(row2, (0, y))
        y += row2.height
    sheet.paste(pal, (0, y))
    sheet.save(out / "sheet.png")
    print(f"{spec['id']}: {cubes} cubes (budget {budget}), {len(parts) - cubes} painted details, "
          f"{len(used)} colours, scale x{scale} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
