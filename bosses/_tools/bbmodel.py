"""Writes and reads a boss `.bbmodel` (boss pipeline step 2, .claude/skills/boss-building/SKILL.md).

Build:  python bosses/_tools/bbmodel.py build bosses/<dungeon>/<boss>
Reads   <boss>/boss.yml             id, kind, size (hitbox), bones, mutations (show_bones = hidden at rest)
        <boss>/concept/concept.yml  the cubes (and the painted details) approved at the design gate
        <boss>/model.yml            the rig: parent and pivot of every bone, texture size, extra paint,
                                    emissive bones (format below)
        <dungeon>/style.md          palette
Writes  <boss>/<id>.bbmodel         Blockbench project, plain JSON (format pinned below)
        <boss>/<id>.bbmodel.sha     sha256 of the file as written by this script
        <boss>/out/model/texture.png  copy of the embedded texture (git-ignored)

HAND EDITS WIN: if <id>.bbmodel exists and its sha256 is not the one in <id>.bbmodel.sha, the user
edited it in Blockbench. This script then REFUSES to write (exit code 3). There is no --force.

Pinned format: Blockbench project format_version "4.10", model_format "free" (Generic Model), per-face
UV (box_uv false), one embedded PNG texture. Blockbench 4.10+ and 5.x open it; BetterModel 3.7.1 reads
it (its parser: api/.../data/raw/ModelData.java; format major < 5 = its "legacy" keyframe axes).

Conventions (units = pixels = 1/16 block, y up, the model faces north = -z, its right side is +x):
  - one outliner group per bone, named exactly as in boss.yml (no BetterModel tag prefix: a name whose
    first `_` segment is a BetterModel tag such as h, hi, b, ob, p, sp, tag, glow ... would be parsed as
    a tag and renamed, so such names are refused);
  - `hitbox` bone under `root`: one cube of boss.yml > size, no textured face, hidden in Blockbench.
    BetterModel creates its hitbox from a bone named `hitbox` (EntityTracker.CREATE_HITBOX_PREDICATE);
  - bones shown only by a mutation (boss.yml > mutations.*.show_bones): group and cubes written with
    `visibility: false`. BetterModel spawns such a bone invisible (RenderedBone: display.invisible(
    !group.visibility())); the code shows it at the mutation;
  - hit-zone boxes (skill step 2): for every zone of boss.yml > hit_zones and every bone of that zone,
    a helper bone `zone_<...>` (child of the zone bone, so it follows its animation) holding ONE cube with
    no textured face and `visibility: false`. BetterModel builds a bone's hitbox from its largest cube:
    the helper has only this cube, so the box is the hitbox. Names and boxes: model.yml > hit_zone_boxes.
    The code creates them with EntityTracker.createHitBox(listener, BonePredicate.name("zone_...")) and
    maps the hit helper bone back to its zone with the same table. They are not cubes of the budget;
  - emissive cubes: `light_emission: 15` and a cube name ending in `_glow` (BetterModel: a cube whose
    name contains "glow" is full bright). No other cube name contains "glow";
  - cubes are never rotated; pivots (group origins) come from model.yml.

model.yml:
    format_version: "4.10"
    texture: {width: 128, height: 128}
    emissive_bones: [eyes, bulb]         # every cube of these bones is full bright (weak points glow)
    plain: {head: ["up:cap_deep"]}       # faces (of that base colour) left without procedural detail:
                                         # a one-colour face costs no texture space (shared swatch)
    gill_centre: [0, -9]                 # x, z the gill stripes run away from (centre of the cap)
    bones:
      root: {pivot: [0, 0, 0]}
      hip:  {parent: root, pivot: [0, 34, 2]}
    cubes:                               # cubes added at step 2 (rare; each one is a difference from the
      - {bone: jaw, from: [16, 31, -28], size: [1, 1, 1], color: glow_core}   # concept, to name at the gate)
    paint:                               # texture details added at step 2, same format as concept.yml
      - {bone: maw, from: [20, 38, -23], size: [2, 1, 0], color: lilac_glow}
    hit_zone_boxes:                      # zone of boss.yml -> helper bones (one per bone of the zone)
      eyes:
        zone_eyes: {bone: eyes}          # box = the box around the cubes of the bone, unless from/to given
      spit_root:
        zone_spit_root: {bone: spit_root, removed_by: torn_spit_root}   # required when a mutation hides
                                         # the bone: the code removes this hitbox at that mutation
    pose_checks: {...}                   # preview only (render.py), never written to the .bbmodel
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import PX_PER_BLOCK, hidden_bones, load_palette, load_yaml, match_bones  # noqa: E402

FORMAT_VERSION = "4.10"
MODEL_FORMAT = "free"
NS = uuid.UUID("6f1d2c1e-8a57-4b0f-9b0e-0b5522b0a001")   # fixed: uuids are the same on every run
BETTERMODEL_TAGS = {"h", "hi", "b", "ob", "p", "sp", "tag", "mtag", "ptag", "glow", "pli", "li", "pri", "ri",
                    "ph", "pra", "prfa", "pla", "plfa", "phip", "pw", "pc", "prl", "prfl", "pll", "plfl", "cape"}
FACE_ORDER = ["north", "east", "south", "west", "up", "down"]
EMISSIVE_SHARE = 0.4      # a cube is full bright when this share of its visible pixels is a glow colour


def is_helper(bone: str) -> bool:
    """Bones that are not part of the drawn model: the main hitbox and the hit-zone boxes."""
    return bone == "hitbox" or bone.startswith("zone_")


def uid(*parts) -> str:
    return str(uuid.uuid5(NS, "/".join(map(str, parts))))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hand_edited(model_path: Path) -> bool:
    """True when the .bbmodel exists and is not the file this script last wrote."""
    if not model_path.exists():
        return False
    sha_path = model_path.with_name(model_path.name + ".sha")
    if not sha_path.exists():
        return True
    return sha_path.read_text(encoding="utf-8").split()[0] != sha256(model_path)


def mirror_twins(by_bone) -> set[str]:
    """Bones `x_l`/`x_r` (or `_fl`/`_fr` ...) whose cubes are exact mirror images of each other."""
    out = set()
    for name, cubes in by_bone.items():
        if not name.endswith("r"):
            continue
        twin = name[:-1] + "l"
        if twin not in by_bone:
            continue
        a = sorted((tuple(c["from"]), tuple(c["size"]), c["color"]) for c in cubes)
        b = sorted(((-(c["from"][0] + c["size"][0]), c["from"][1], c["from"][2]), tuple(c["size"]), c["color"])
                   for c in by_bone[twin])
        if a == b:
            out |= {name, twin}
    return out


def build(boss_dir: Path):
    from texture import FACES, Painter

    spec = load_yaml(boss_dir / "boss.yml")
    concept = load_yaml(boss_dir / "concept" / "concept.yml")
    rig = load_yaml(boss_dir / "model.yml")
    palette = load_palette(boss_dir.parent / "style.md")
    mid = spec["id"]
    if str(rig.get("format_version")) != FORMAT_VERSION:
        raise ValueError(f"model.yml format_version must be \"{FORMAT_VERSION}\" (pinned)")

    parts = concept["parts"]
    cubes = [p for p in parts if not p.get("paint")] + list(rig.get("cubes") or [])
    paints = [p for p in parts if p.get("paint")] + list(rig.get("paint") or [])
    for p in cubes + paints:
        if p["color"] not in palette:
            raise ValueError(f"colour '{p['color']}' ({p['bone']}) is not in style.md")
        if any(not isinstance(v, int) for v in p["from"] + p["size"]):
            raise ValueError(f"{p['bone']}: from/size must be whole pixels")
    bones = rig["bones"]
    used = {p["bone"] for p in cubes}
    for b in used | {p["bone"] for p in paints}:
        if b not in bones:
            raise ValueError(f"bone '{b}' has cubes or paint but no entry in model.yml > bones")
    for b, v in bones.items():
        if b != "root" and v.get("parent") not in bones:
            raise ValueError(f"bone '{b}': parent '{v.get('parent')}' is not a bone")
        if b.split("_")[0] in BETTERMODEL_TAGS and "_" in b:
            raise ValueError(f"bone '{b}' starts with a BetterModel tag ('{b.split('_')[0]}_'): it would be renamed")
        if "glow" in b:
            raise ValueError(f"bone '{b}': 'glow' in a bone name would make all its cube names emissive")
    if "hitbox" in bones:
        raise ValueError("the hitbox bone is written by the script from boss.yml > size; remove it from model.yml")

    by_bone: dict[str, list] = {}
    for c in cubes:
        by_bone.setdefault(c["bone"], []).append(c)
    painter = Painter(cubes, paints, palette, mirror_twins(by_bone), rig.get("plain"),
                      rig.get("gill_centre") or (0, 0))
    tw, th = rig["texture"]["width"], rig["texture"]["height"]
    image, uv, stats = painter.build(tw, th)
    orphans = painter.orphans(paints)
    if orphans:   # details the concept draws over a neighbouring bone: paint them where they lie
        painter = Painter(cubes, paints, palette, mirror_twins(by_bone), rig.get("plain"),
                          rig.get("gill_centre") or (0, 0))
        painter.fallback = orphans
        image, uv, stats = painter.build(tw, th)
    notes = []
    for p in orphans:
        hit = painter.paint_hits.get(id(p), 0)
        notes.append("paint %s %s %s %s: %s" % (p["bone"], p["from"], p["size"], p["color"],
                     "painted on another bone (%d px)" % hit if hit else "touches no visible face (hidden, not painted)"))

    hidden = hidden_bones(spec, set(bones))
    emissive_bones = set(rig.get("emissive_bones") or [])
    elements, cube_ids = [], {}
    counters: dict[str, int] = {}
    for ci, c in enumerate(cubes):
        bone = c["bone"]
        counters[bone] = n = counters.get(bone, 0) + 1
        glow = bone in emissive_bones or stats["emissive"][ci] >= EMISSIVE_SHARE
        name = f"{bone}_{n}" + ("_glow" if glow else "")
        lo = c["from"]
        hi = [lo[a] + c["size"][a] for a in range(3)]
        faces = {}
        for f in FACE_ORDER:
            r = uv[(ci, f)]
            faces[f] = {"uv": r, "texture": 0} if r else {"uv": [0, 0, 0, 0], "texture": None}
        cid = uid(mid, "cube", bone, n)
        cube_ids.setdefault(bone, []).append(cid)
        elements.append({
            "name": name, "box_uv": False, "rescale": False, "locked": False,
            "light_emission": 15 if glow else 0, "render_order": "default", "allow_mirror_modeling": True,
            "from": lo, "to": hi, "autouv": 0, "color": ci % 8, "visibility": bone not in hidden,
            "origin": list(bones[bone]["pivot"]), "faces": faces, "type": "cube", "uuid": cid,
        })
    # hitbox: boss.yml > size, centred on the model, standing on the ground
    hw = spec["size"]["width"] * PX_PER_BLOCK / 2
    hh = spec["size"]["height"] * PX_PER_BLOCK
    hid = uid(mid, "cube", "hitbox", 1)
    elements.append({
        "name": "hitbox", "box_uv": False, "rescale": False, "locked": True, "light_emission": 0,
        "render_order": "default", "allow_mirror_modeling": False,
        "from": [-hw, 0, -hw], "to": [hw, hh, hw], "autouv": 0, "color": 0, "visibility": False,
        "origin": [0, 0, 0], "faces": {f: {"uv": [0, 0, 0, 0], "texture": None} for f in FACE_ORDER},
        "type": "cube", "uuid": hid,
    })
    cube_ids["hitbox"] = [hid]

    # hit-zone boxes: one invisible, untextured box per bone of every zone, in a helper bone under it
    zones = {k: v for k, v in (spec.get("hit_zones") or {}).items() if isinstance(v, dict)}
    zmap = rig.get("hit_zone_boxes") or {}
    if set(zmap) != set(zones):
        raise ValueError("model.yml > hit_zone_boxes must list exactly the zones of boss.yml > hit_zones: "
                         f"{sorted(zones)} (got {sorted(zmap)})")
    helpers: dict[str, dict] = {}
    zone_rows = []
    for zid, zone in zones.items():
        want = match_bones(zone.get("bones"), set(bones))
        got = set()
        for hname, h in zmap[zid].items():
            target = h.get("bone")
            if not hname.startswith("zone_") or hname in bones or hname in helpers:
                raise ValueError(f"hit_zone_boxes.{zid}.{hname}: helper bones are named zone_<...>, each once")
            if target not in want or target in got:
                raise ValueError(f"hit_zone_boxes.{zid}.{hname}: bone '{target}' is not a bone of this zone, or has two boxes")
            got.add(target)
            cs = by_bone.get(target) or []
            lo = list(h.get("from") or [min(c["from"][a] for c in cs) for a in range(3)])
            hi = list(h.get("to") or [max(c["from"][a] + c["size"][a] for c in cs) for a in range(3)])
            hiders = sorted(m for m, mut in (spec.get("mutations") or {}).items()
                            if target in match_bones(mut.get("hide_bones"), set(bones)))
            if (h.get("removed_by") or None) != (hiders[0] if hiders else None):
                raise ValueError(f"hit_zone_boxes.{zid}.{hname}: removed_by must be "
                                 f"{hiders[0] if hiders else 'absent'} (the mutation that hides '{target}')")
            helpers[hname] = {"parent": target, "pivot": [(lo[a] + hi[a]) / 2 for a in range(3)], "zone": zid,
                              "from": lo, "to": hi}
            zone_rows.append((zid, hname, target, lo, hi, h.get("removed_by")))
        if got != want:
            raise ValueError(f"hit_zone_boxes.{zid}: no box for {sorted(want - got)}")
    names_h = list(helpers)
    for i, a in enumerate(names_h):
        for b in names_h[i + 1:]:
            A, B = helpers[a], helpers[b]
            if A["zone"] != B["zone"] and all(min(A["to"][k], B["to"][k]) - max(A["from"][k], B["from"][k]) > 0 for k in range(3)):
                raise ValueError(f"hit-zone boxes {a} and {b} overlap: shrink the bigger zone (the weak point wins)")
    for hname, h in helpers.items():
        zc = uid(mid, "cube", hname, 1)
        elements.append({
            "name": hname, "box_uv": False, "rescale": False, "locked": True, "light_emission": 0,
            "render_order": "default", "allow_mirror_modeling": False,
            "from": h["from"], "to": h["to"], "autouv": 0, "color": 0, "visibility": False,
            "origin": h["pivot"], "faces": {f: {"uv": [0, 0, 0, 0], "texture": None} for f in FACE_ORDER},
            "type": "cube", "uuid": zc,
        })
        cube_ids[hname] = [zc]

    children: dict[str, list] = {}
    for b, v in bones.items():
        if b != "root":
            children.setdefault(v["parent"], []).append(b)
    children.setdefault("root", []).append("hitbox")
    for hname, h in helpers.items():
        children.setdefault(h["parent"], []).append(hname)
    all_bones = dict(bones, hitbox={"parent": "root", "pivot": [0, 0, 0]}, **helpers)

    def group(b):
        return {
            "name": b, "origin": list(all_bones[b]["pivot"]), "color": 0, "uuid": uid(mid, "bone", b),
            "export": True, "mirror_uv": False, "isOpen": b in ("root", "hip", "body"), "locked": is_helper(b),
            "visibility": b not in hidden and not is_helper(b), "autouv": 0,
            "children": [group(k) for k in children.get(b, [])] + cube_ids.get(b, []),
        }

    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    model = {
        "meta": {"format_version": FORMAT_VERSION, "model_format": MODEL_FORMAT, "box_uv": False},
        "name": mid, "model_identifier": "", "visible_box": [1, 1, 0], "variable_placeholders": "",
        "variable_placeholder_buttons": [], "timeline_setups": [], "unhandled_root_fields": {},
        "resolution": {"width": tw, "height": th},
        "elements": elements,
        "outliner": [group("root")],
        "textures": [{
            "path": "", "name": f"{mid}.png", "folder": "", "namespace": "", "id": "0",
            "width": tw, "height": th, "uv_width": tw, "uv_height": th, "particle": False,
            "use_as_default": False, "layers_enabled": False, "sync_to_project": "", "render_mode": "default",
            "render_sides": "auto", "frame_time": 1, "frame_order_type": "loop", "frame_order": "",
            "frame_interpolate": False, "visible": True, "internal": True, "saved": False,
            "uuid": uid(mid, "texture"), "source": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
        }],
        "animations": [],
    }
    info = {"cubes": len(cubes), "bones": len(all_bones), "zone_rows": zone_rows, "hidden": sorted(hidden), "stats": stats,
            "glow_cubes": sum(1 for e in elements if e["light_emission"]), "png": png, "notes": notes}
    return mid, model, info


# ---------------------------------------------------------------------------------------- reading
class Model:
    """A .bbmodel as the other tools need it (validate.py, render.py). Reads only what the file says."""

    def __init__(self, path: Path):
        from PIL import Image

        self.path = path
        self.data = data = json.loads(path.read_text(encoding="utf-8"))
        self.meta = data.get("meta", {})
        self.resolution = data.get("resolution", {})
        self.elements = {e["uuid"]: e for e in data.get("elements", [])}
        self.bones: dict[str, dict] = {}     # name -> {parent, pivot, rotation, visibility, cubes: [element]}
        self.duplicates: list[str] = []
        self.loose: list = []                # elements outside any group

        def walk(node, parent):
            if isinstance(node, str):
                if parent is None:
                    self.loose.append(node)
                return
            name = node["name"]
            if name in self.bones:
                self.duplicates.append(name)
            cubes = [self.elements[c] for c in node.get("children", []) if isinstance(c, str) and c in self.elements]
            self.bones[name] = {"parent": parent, "pivot": node.get("origin", [0, 0, 0]),
                                "rotation": node.get("rotation", [0, 0, 0]),
                                "visibility": node.get("visibility", True) is not False, "cubes": cubes}
            for c in node.get("children", []):
                walk(c, name)

        for n in data.get("outliner", []):
            walk(n, None)
        self.textures = []
        for t in data.get("textures", []):
            raw = base64.b64decode(t["source"].split(",", 1)[1])
            self.textures.append(Image.open(io.BytesIO(raw)).convert("RGBA"))
        self.animations = data.get("animations") or []

    def cubes(self, with_helpers=False):
        """(bone, cube) of the drawn model; the hitbox and the hit-zone boxes only with with_helpers."""
        return [(b, c) for b, v in self.bones.items() if with_helpers or not is_helper(b) for c in v["cubes"]
                if c.get("type", "cube") == "cube"]

    def zone_boxes(self):
        """{helper bone: (parent bone, cubes)} of the hit-zone boxes."""
        return {b: (v["parent"], v["cubes"]) for b, v in self.bones.items() if b.startswith("zone_")}

    def shown(self, bone: str) -> bool:
        return self.bones[bone]["visibility"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Boss .bbmodel writer")
    ap.add_argument("action", choices=["build"])
    ap.add_argument("boss_dir", type=Path)
    args = ap.parse_args()
    boss_dir = args.boss_dir.resolve()
    spec_id = load_yaml(boss_dir / "boss.yml")["id"]
    path = boss_dir / f"{spec_id}.bbmodel"
    if hand_edited(path):
        print(f"REFUSED: {path} was edited by hand (its sha256 is not the one in {path.name}.sha).\n"
              "Hand edits win: apply the change on top of the user's file, or ask.", file=sys.stderr)
        return 3
    try:
        mid, model, info = build(boss_dir)
    except ValueError as e:
        print(f"cannot build: {e}", file=sys.stderr)
        return 1
    path.write_text(json.dumps(model, indent=1) + "\n", encoding="utf-8", newline="\n")
    path.with_name(path.name + ".sha").write_text(f"{sha256(path)}  {path.name}\n", encoding="utf-8", newline="\n")
    out = boss_dir / "out" / "model"
    out.mkdir(parents=True, exist_ok=True)
    (out / "texture.png").write_bytes(info["png"])
    (out / "build_notes.txt").write_text("".join(n + "\n" for n in info["notes"]), encoding="utf-8")
    for n in info["notes"]:
        print("  note:", n)
    s = info["stats"]
    for zid, hname, target, lo, hi, gone in info["zone_rows"]:
        print("  zone %-9s %-20s on %-11s %gx%gx%g px%s" % (zid, hname, target, *(hi[a] - lo[a] for a in range(3)),
                                                          f"  (removed by {gone})" if gone else ""))
    print(f"{mid}: {info['cubes']} cubes + hitbox + {len(info['zone_rows'])} zone boxes, {info['bones']} bones, hidden at rest: {info['hidden'] or 'none'}, "
          f"{info['glow_cubes']} emissive cubes\n"
          f"  texture {model['resolution']['width']}x{model['resolution']['height']}: {s['faces']} faces = "
          f"{s['hidden']} never visible (no texture) + {s['swatch']} on colour swatches + {s['shared']} shared + "
          f"{s['unique']} own rectangles ({s['area']} px), fill {s['fill']:.0%}\n  -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
