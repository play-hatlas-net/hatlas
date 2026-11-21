"""Validator of the boss pipeline (.claude/skills/boss-building/SKILL.md §5).

Usage:
    python bosses/_tools/validate.py bosses/<dungeon>/<boss> --step design [--report FILE] [--iteration N]

Steps (each one also runs the checks of the steps before it):
    design     boss.yml format, names, mechanics (plan §4.1, §4.2, §4.5), hit zones and
               mutations (§4.6) + concept sheet                                              IMPLEMENTED
    model      .bbmodel: format, bones, pivots, cube budget, 1/16 grid, texture, palette,
               UVs, hitbox, hit-zone boxes (one invisible box per zone bone, no overlap
               between zones), mutation bones, outline = concept                             IMPLEMENTED
    animation  one animation per spec name, length = windup + active + recovery              not yet
    sound      .ogg per sound name, mono/stereo, loudness, LICENSES.md                       not yet
The parts marked "not yet" are written by the agent of the step that first needs them; until then
they report NOT YET (and fail the run when that step is asked for, so a gate cannot pass on a stub).

Output: a markdown table of checks (PASS / FAIL / INFO / NOT YET) on stdout and in --report.
Exit code: 0 = no FAIL, 1 = at least one FAIL (or an unimplemented step was asked), 2 = cannot read.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (CUBE_BUDGET, FIXED_BONES, PX_PER_BLOCK, RUNES, hexa, hidden_bones,  # noqa: E402
                    load_palette, load_yaml, match_bones)

STEPS = ["design", "model", "animation", "sound"]
KINDS = ["minion", "mini_boss", "boss"]
MOVE_KINDS = ["attack", "summon", "heal"]
MIN_WINDUP = 10            # ticks, dodgeable hit at 20 Hz with ~100 ms ping (skill §4 step 1)
MIN_PUNISH = 20            # ticks: a boss needs at least one recovery this long
PARTY_MAX = 8
# animations every character must have, and names the code plays without a move naming them
REQUIRED_ANIMS = {"minion": ["spawn", "idle", "walk", "attack", "death"],
                  "mini_boss": ["spawn", "walk", "hit", "death"],
                  "boss": ["spawn", "walk", "hit", "death"]}
ENGINE_ANIMS = {"spawn", "idle", "walk", "run", "jump", "hit", "block", "stagger", "death"}
REQUIRED_SOUNDS = {"minion": ["hurt", "death"], "mini_boss": ["spawn", "hurt", "death", "enrage"],
                   "boss": ["spawn", "hurt", "death", "enrage"]}
BUILTIN_ACTIONS = {"target_healer", "guard_break"}
WAVE_UNTIL = {"phase_end", "boss_death"}
ZONE_MIN, ZONE_MAX = 0.5, 2.0   # hit zone multipliers (plan §4.6)
# hit-zone boxes (skill step 2, ✔ user 2026-11-21): a box players must hit (weak point or breakable part)
# is at least ZONE_BOX_MIN px on every axis, and a weak point shows at least ZONE_WEAK_FACE x ZONE_WEAK_FACE px;
# an armoured box holds at most ZONE_ARMOUR_AIR of air (else split the part into two boxes)
ZONE_BOX_MIN, ZONE_WEAK_FACE, ZONE_ARMOUR_AIR, ZONE_BOXES_PER_BONE = 4, 6, 0.5, 2
PROTECT_TIMEOUT_MAX = 2400      # ticks: a protector shield never lasts longer (plan §4.5)
LATE_MUTATION_HP = 0.40         # every boss mutates at or below this share of HP, in one of its last two phases
# vanilla mobs a summon or a wave may name without a spec of their own
VANILLA_MOBS = {
    "zombie", "husk", "drowned", "skeleton", "stray", "bogged", "wither_skeleton", "spider", "cave_spider",
    "creeper", "slime", "magma_cube", "silverfish", "endermite", "witch", "vex", "pillager", "vindicator",
    "evoker", "ravager", "blaze", "ghast", "piglin", "piglin_brute", "hoglin", "zoglin", "zombified_piglin",
    "phantom", "guardian", "breeze", "creaking", "enderman", "wolf", "bee", "iron_golem", "baby_zombie",
    "chicken_jockey",
}


class Report:
    def __init__(self):
        self.rows: list[tuple[str, str, str, str]] = []

    def add(self, group, check, ok, detail=""):
        status = ok if isinstance(ok, str) else ("PASS" if ok else "FAIL")
        self.rows.append((group, check, status, str(detail)))
        return status == "PASS"

    def count(self, status):
        return sum(1 for r in self.rows if r[2] == status)

    @property
    def failed(self):
        return self.count("FAIL") > 0


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def sound_names(node):
    return [v for v in (node or {}).values() if isinstance(v, str)]


# ---------------------------------------------------------------------------------------- spec
def check_spec(spec, boss_dir: Path, rep: Report):
    g = "format"
    kind = spec.get("kind")
    if not rep.add(g, "kind is minion | mini_boss | boss", kind in KINDS, kind):
        return
    boss = kind != "minion"
    required = ["id", "kind", "dungeon", "name", "lore", "size", "stats", "moves", "animations", "sounds"]
    if boss:
        required += ["phases", "reactions", "defences", "hit_zones"]
    if kind == "mini_boss":
        required += ["rune", "teaches"]
    missing = [k for k in required if k not in spec]
    rep.add(g, "required keys", not missing, "missing: " + ", ".join(missing) if missing else f"{len(required)} keys")
    if missing:
        return
    rep.add(g, "id = folder name", spec["id"] == boss_dir.name, f"{spec['id']} / {boss_dir.name}")
    rep.add(g, "dungeon = parent folder", spec["dungeon"] == boss_dir.parent.name,
            f"{spec['dungeon']} / {boss_dir.parent.name}")
    name = spec["name"]
    rep.add(g, "name has en and fr", isinstance(name, dict) and all(name.get(k) for k in ("en", "fr")), name)
    if kind == "mini_boss":
        rep.add(g, "rune is one of " + "|".join(RUNES), spec["rune"] in RUNES, spec["rune"])
    else:
        rep.add(g, "no rune (mini-bosses only)", "rune" not in spec, spec.get("rune", "none"))
    size = spec["size"]
    size_ok = isinstance(size, dict) and all(is_num(size.get(k)) and size[k] > 0 for k in ("width", "height"))
    on_grid = size_ok and all(float(size[k] * PX_PER_BLOCK).is_integer() for k in ("width", "height"))
    rep.add(g, "size: width and height > 0, on the 1/16 grid", size_ok and on_grid,
            f"{size.get('width')} x {size.get('height')} blocks" if size_ok else size)
    stats = spec["stats"]
    need = ["hp", "armor", "damage_cap_per_hit"] + (["enrage_seconds"] if boss else [])
    bad = [k for k in need if not is_num(stats.get(k)) or (k != "armor" and stats[k] <= 0)]
    rep.add(g, "stats: " + ", ".join(need), not bad, "bad: " + ", ".join(bad) if bad else
            ", ".join(f"{k} {stats[k]}" for k in need))

    anims = spec["animations"]
    moves = spec["moves"] or {}
    rep.add("names", "animations: a list, each name once", isinstance(anims, list) and len(anims) == len(set(anims)),
            f"{len(anims)} animations")
    anim_set = set(anims)
    used_anims: set[str] = set()

    def need_anim(where, name):
        used_anims.add(name)
        if name not in anim_set:
            rep.add("names", f"{where}: animation '{name}' is declared", False, "not in animations")

    # ---- moves
    g = "moves"
    all_sounds: list[tuple[str, str]] = [("sounds." + k, v) for k, v in (spec["sounds"] or {}).items()]
    short, punish = [], 0
    for mid, mv in moves.items():
        mk = mv.get("kind", "attack")
        if mk not in MOVE_KINDS:
            rep.add(g, f"{mid}: kind", False, mk)
            continue
        if not mv.get("animation"):
            rep.add(g, f"{mid}: has an animation", False)
        else:
            need_anim(mid, mv["animation"])
        snd = mv.get("sounds") or {}
        all_sounds += [(f"{mid}.sounds.{k}", v) for k, v in snd.items()]
        tell = bool(snd.get("windup")) and bool((mv.get("particles") or {}).get("windup")) and bool(mv.get("animation"))
        wind = mv.get("windup_ticks")
        if not is_int(wind) or wind <= 0:
            rep.add(g, f"{mid}: windup_ticks", False, wind)
            continue
        if mk == "attack":
            keys = ["active_ticks", "recovery_ticks", "cooldown_ticks"]
            bad = [k for k in keys if not is_int(mv.get(k)) or mv[k] <= 0]
            ok = not bad and isinstance(mv.get("shape"), dict) and "type" in mv["shape"] and is_num(mv.get("damage"))
            total = wind + (mv.get("active_ticks") or 0) + (mv.get("recovery_ticks") or 0)
            rep.add(g, f"{mid}: attack timings, shape, damage", ok,
                    f"{wind} + {mv.get('active_ticks')} + {mv.get('recovery_ticks')} = {total} ticks "
                    f"({total / 20:g} s), cooldown {mv.get('cooldown_ticks')}" if ok else f"bad: {bad or 'shape/damage'}")
            if wind < MIN_WINDUP:
                short.append(f"{mid} {wind}")
            punish = max(punish, mv.get("recovery_ticks") or 0)
            zone = mv.get("zone")
            if zone is not None:
                rep.add(g, f"{mid}: zone has duration, damage, every_ticks, max_alive",
                        all(is_num(zone.get(k)) and zone[k] > 0 for k in ("duration_ticks", "damage", "every_ticks", "max_alive")),
                        zone)
        rep.add(g, f"{mid}: tell = pose + wind-up sound + wind-up particles", tell,
                f"{mv.get('animation')}, {snd.get('windup')}, {(mv.get('particles') or {}).get('windup')}")
    rep.add(g, f"every attack wind-up >= {MIN_WINDUP} ticks", not short, "too short: " + ", ".join(short) if short else
            "shortest %s" % min((m.get("windup_ticks", 0) for m in moves.values()), default=0))
    if boss:
        rep.add(g, f"a punish window: one recovery >= {MIN_PUNISH} ticks", punish >= MIN_PUNISH, f"longest {punish}")

    # ---- phases
    phase_ids: list[str] = []
    used_moves: set[str] = set()
    musics: list[str] = []
    if boss:
        g = "phases"
        phases = spec["phases"] or []
        phase_ids = [p.get("id") for p in phases]
        hps = [p.get("hp_below") for p in phases]
        rep.add(g, "at least 2 phases, ids unique", len(phases) >= 2 and len(set(phase_ids)) == len(phase_ids),
                ", ".join(map(str, phase_ids)))
        ordered = all(is_num(h) for h in hps) and hps and hps[0] == 1.0 and all(a > b > 0 for a, b in zip(hps, hps[1:]))
        rep.add(g, "ordered by hp_below, first = 1.0", bool(ordered), " > ".join(map(str, hps)))
        for i, p in enumerate(phases):
            pid = p.get("id")
            unknown = [m for m in p.get("moves") or [] if m not in moves]
            rep.add(g, f"{pid}: moves exist", bool(p.get("moves")) and not unknown,
                    "unknown: " + ", ".join(unknown) if unknown else ", ".join(p.get("moves") or []))
            used_moves.update(p.get("moves") or [])
            if p.get("idle"):
                need_anim(pid + ".idle", p["idle"])
            else:
                rep.add(g, f"{pid}: has an idle animation", False)
            if i > 0:
                ok = bool(p.get("enter")) and is_int(p.get("enter_ticks")) and p["enter_ticks"] > 0
                rep.add(g, f"{pid}: entry animation + enter_ticks", ok, f"{p.get('enter')}, {p.get('enter_ticks')} ticks")
                if p.get("enter"):
                    need_anim(pid + ".enter", p["enter"])
                prev = phases[i - 1]
                changed = set(p.get("moves") or []) != set(prev.get("moves") or []) or p.get("speed", 1) != prev.get("speed", 1)
                rep.add(g, f"{pid}: changes the move set or the rhythm", changed,
                        "speed %s" % p.get("speed", 1))
            if p.get("music"):
                musics.append(p["music"])
            for w in p.get("waves") or []:
                mobs = w.get("mobs") or {}
                ok = is_int(w.get("max_alive")) and w["max_alive"] > 0 and is_int(w.get("every_ticks")) \
                    and w["every_ticks"] > 0 and w.get("until") in WAVE_UNTIL and bool(mobs)
                rep.add("mechanics", f"{pid} wave: max_alive, every_ticks, until", ok,
                        f"max_alive {w.get('max_alive')}, every {w.get('every_ticks')}, until {w.get('until')}")
                per_spawn = sum(v for v in mobs.values() if is_int(v))
                rep.add("mechanics", f"{pid} wave: one spawn fits in max_alive", ok and per_spawn <= w["max_alive"],
                        f"{per_spawn} per spawn")
                for mob in mobs:
                    check_mob(mob, boss_dir, rep, f"{pid} wave")
        rep.add(g, "every move is used by a phase", set(moves) <= used_moves,
                "unused: " + ", ".join(sorted(set(moves) - used_moves)) if set(moves) - used_moves else f"{len(moves)} moves")

    # ---- mechanics (§4.5)
    g = "mechanics"
    for mid, mv in moves.items():
        mk = mv.get("kind", "attack")
        if mk == "summon":
            check_mob(mv.get("minion"), boss_dir, rep, mid)
            cnt = mv.get("count") or {}
            ok = all(is_int(cnt.get(k)) for k in ("base", "per_extra_player", "max")) and \
                1 <= cnt["base"] <= cnt["max"] <= PARTY_MAX
            at8 = min(cnt["max"], cnt["base"] + cnt["per_extra_player"] * (PARTY_MAX - 2)) if ok else "?"
            rep.add(g, f"{mid}: count base/per_extra_player/max, max <= {PARTY_MAX}", ok,
                    f"{cnt.get('base')} + {cnt.get('per_extra_player')} per player above 2, max {cnt.get('max')} "
                    f"(2 players: {cnt.get('base')}, 8 players: {at8})")
            rep.add(g, f"{mid}: uses_per_phase set", is_int(mv.get("uses_per_phase")), mv.get("uses_per_phase"))
            if mv.get("protect"):
                sh = mv.get("shield") or {}
                rep.add(g, f"{mid}: protect has a shield animation, tethers and an immune sound",
                        bool(sh.get("animation")) and bool(sh.get("immune_sound")) and bool(sh.get("tether_particles")),
                        f"{sh.get('animation')}, {sh.get('tether_particles')}, {sh.get('immune_sound')}")
                for k in ("animation", "break_animation"):
                    if sh.get(k):
                        need_anim(f"{mid}.shield.{k}", sh[k])
                all_sounds += [(f"{mid}.shield.{k}", sh[k]) for k in ("immune_sound", "break_sound") if sh.get(k)]
                pt = mv.get("protect_timeout_ticks")
                rep.add(g, f"{mid}: protect_timeout_ticks set, at most {PROTECT_TIMEOUT_MAX}",
                        is_int(pt) and 0 < pt <= PROTECT_TIMEOUT_MAX, f"{pt} ticks ({pt / 20:g} s)" if is_int(pt) else "missing")
                ws = mv.get("while_shielded") or []
                rep.add(g, f"{mid}: keeps attacking while shielded (moves exist)", bool(ws) and all(m in moves for m in ws),
                        ", ".join(ws))
        elif mk == "heal":
            it = mv.get("interrupt") or {}
            ok = is_num(it.get("damage")) and 0 < it["damage"] < 1 and is_num(it.get("per_extra_player")) \
                and it["per_extra_player"] > 0 and is_int(it.get("stagger_ticks")) and it["stagger_ticks"] > 0
            at8 = it["damage"] + it["per_extra_player"] * (PARTY_MAX - 2) if ok else 0
            rep.add(g, f"{mid}: interrupt damage, per_extra_player, stagger_ticks", ok,
                    f"{it.get('damage', 0) * 100:g} % + {it.get('per_extra_player', 0) * 100:g} % per player above 2 "
                    f"(8 players: {at8 * 100:g} %), stagger {it.get('stagger_ticks')} ticks")
            rep.add(g, f"{mid}: cap = phase", mv.get("cap") == "phase", mv.get("cap"))
            ch, hps_ = mv.get("channel_ticks"), mv.get("heal_per_second")
            ok = is_int(ch) and ch > 0 and is_num(hps_) and 0 < hps_ < 1 and is_int(mv.get("uses_per_phase"))
            rep.add(g, f"{mid}: channel_ticks, heal_per_second, uses_per_phase", ok,
                    f"{ch} ticks x {hps_} = {ch / 20 * hps_ * 100:g} % of max HP per channel, "
                    f"{mv.get('uses_per_phase')} per phase" if ok else "")
            if mv.get("interrupt_animation"):
                need_anim(f"{mid}.interrupt_animation", mv["interrupt_animation"])
            snd = mv.get("sounds") or {}
            rep.add(g, f"{mid}: loop and interrupt sounds", bool(snd.get("loop")) and bool(snd.get("interrupt")),
                    f"{snd.get('loop')}, {snd.get('interrupt')}")
            goto = it.get("goto_phase")
            if goto is not None:
                users = [i for i, p in enumerate(spec.get("phases") or []) if mid in (p.get("moves") or [])]
                later = goto in phase_ids and users and phase_ids.index(goto) > max(users)
                rep.add(g, f"{mid}: goto_phase names a later phase", bool(later),
                        f"{goto} (used in {', '.join(phase_ids[i] for i in users)})")
    if boss:
        waves = [p["id"] for p in spec["phases"] or [] if p.get("waves")]
        protectors = [m for m, mv in moves.items() if mv.get("kind") == "summon" and mv.get("protect") and m in used_moves]
        rep.add(g, "mandatory mob phase: a side wave or a protector summon", bool(waves or protectors),
                "waves in %s; protectors: %s" % (", ".join(waves) or "no phase", ", ".join(protectors) or "none"))
        late = []
        hps_all = [p.get("hp_below") for p in spec["phases"] or []]
        floor = hps_all[-2] if len(hps_all) >= 2 else 1.0     # below this = the last or second-to-last phase
        for mut_id, mut in (spec.get("mutations") or {}).items():
            hp = [c["hp_below"] for c in ((mut.get("when") or {}).get("any") or []) if isinstance(c, dict) and is_num(c.get("hp_below"))]
            body = bool(mut.get("hide_bones") or mut.get("show_bones"))
            fight = bool(mut.get("remove_moves") or mut.get("add_moves") or mut.get("animation_set")) or mut.get("speed", 1) != 1
            if hp and min(hp) <= LATE_MUTATION_HP and min(hp) <= floor and body and fight:
                last = [p["id"] for p in spec["phases"] if is_num(p.get("hp_below")) and p["hp_below"] >= min(hp)][-1]
                late.append(f"{mut_id} at {min(hp):g} (in {last})")
        rep.add(g, f"mandatory mutation: hp_below <= {LATE_MUTATION_HP:g}, in one of the last two phases, changes body and fight",
                bool(late), ", ".join(late) or "none")
        distinct = sorted(set(musics))
        budget = 1 if kind == "mini_boss" else len(spec["phases"])
        rep.add(g, f"music within the budget ({kind}: {budget} track{'s' if budget > 1 else ''})",
                len(distinct) <= budget, ", ".join(distinct) or "none")
        all_sounds += [("music", m) for m in distinct]
    else:
        rep.add(g, "minion: no music, no phases", "phases" not in spec and "music" not in spec)

    # ---- reactions, defences
    if boss:
        g = "reactions"
        reactions = spec["reactions"] or []
        bad = [r for r in reactions if not r.get("when") or (r.get("do") not in moves and r.get("do") not in BUILTIN_ACTIONS)
               or ("phase" in r and r["phase"] not in phase_ids)]
        rep.add(g, "each reaction: when + do (a move or a built-in), known phase", not bad,
                "bad: %s" % bad if bad else f"{len(reactions)} reactions")
        whens = {r.get("when") for r in reactions}
        rep.add(g, "reacts to distance, healers and groups (§4.2)",
                {"players_far", "healed_nearby", "players_grouped"} <= whens, ", ".join(sorted(map(str, whens))))
        for d in spec["defences"] or []:
            rep.add(g, f"defence {d.get('id')}: id + animation", bool(d.get("id")) and bool(d.get("animation")))
            if d.get("animation"):
                need_anim(f"defence {d.get('id')}", d["animation"])

    all_sounds += check_zones(spec, boss_dir, rep, moves, phase_ids, need_anim)

    # ---- names
    g = "names"
    for a in REQUIRED_ANIMS[kind]:
        if a not in anim_set:
            rep.add(g, f"required animation '{a}'", False, "missing")
    rep.add(g, "required animations (" + ", ".join(REQUIRED_ANIMS[kind]) + ")",
            all(a in anim_set for a in REQUIRED_ANIMS[kind]))
    extra = sorted(a for a in anim_set - used_anims if a not in ENGINE_ANIMS)
    rep.add(g, "no animation without a user (move, phase, shield or engine name)", not extra,
            "unused: " + ", ".join(extra) if extra else f"{len(anim_set)} declared, {len(used_anims)} named by moves/phases")
    names = [n for _, n in all_sounds]
    dup = sorted({n for n in names if names.count(n) > 1})
    rep.add(g, "every sound name is written once", not dup, "twice: " + ", ".join(dup) if dup else f"{len(names)} sounds")
    need_s = [s for s in REQUIRED_SOUNDS[kind] if s not in (spec["sounds"] or {})]
    for p in (spec.get("phases") or [])[1:]:
        if p.get("enter") and p["enter"] not in (spec["sounds"] or {}):
            need_s.append(p["enter"])
    rep.add(g, "base sounds (" + ", ".join(REQUIRED_SOUNDS[kind]) + ", one per phase entry)", not need_s,
            "missing: " + ", ".join(need_s) if need_s else "")
    clash = sorted(set(names) & anim_set)
    rep.add(g, "no sound shares a name with an animation", not clash, ", ".join(clash))


def concept_bones(boss_dir: Path) -> set[str]:
    cfile = boss_dir / "concept" / "concept.yml"
    if not cfile.exists():
        return set()
    return {p["bone"] for p in load_yaml(cfile)["parts"]}


def check_zones(spec, boss_dir: Path, rep: Report, moves, phase_ids, need_anim):
    """Hit zones and mutations (plan §4.6). Returns the sounds they name, as (where, name)."""
    sounds: list[tuple[str, str]] = []
    kind = spec["kind"]
    anim_set = set(spec["animations"])
    bones = concept_bones(boss_dir)
    zones_node = spec.get("hit_zones")
    mutations = spec.get("mutations") or {}
    if zones_node is None and not mutations:
        if kind == "minion":
            rep.add("zones", "hit zones and mutations (optional for a minion)", "INFO", "none")
        return sounds

    g = "zones"
    zones_node = zones_node or {}
    default = zones_node.get("default")
    rep.add(g, f"default multiplier within {ZONE_MIN}-{ZONE_MAX}", is_num(default) and ZONE_MIN <= default <= ZONE_MAX, default)
    zones = {k: v for k, v in zones_node.items() if k != "default"}
    broken_by = {c.get("zone_broken") for m in mutations.values() for c in ((m.get("when") or {}).get("any") or [])
                 if isinstance(c, dict) and c.get("zone_broken")}
    has_heal = any(mv.get("kind") == "heal" for mv in moves.values())
    owner: dict[str, str] = {}
    weak, armoured = [], []
    for zid, z in zones.items():
        if not isinstance(z, dict):
            rep.add(g, f"{zid}: a mapping with bones and multiplier", False, z)
            continue
        got = match_bones(z.get("bones"), bones)
        lost = [str(b) for b in z.get("bones") or [] if not match_bones([b], bones)]
        rep.add(g, f"{zid}: every bone exists in concept.yml", bool(z.get("bones")) and not lost,
                "not drawn: " + ", ".join(lost) if lost else ", ".join(sorted(got)))
        twice = sorted(b for b in got if b in owner)
        if twice:
            rep.add(g, f"{zid}: no bone already in another zone", False, ", ".join(f"{b} ({owner[b]})" for b in twice))
        owner.update({b: zid for b in got})
        m = z.get("multiplier")
        ok = is_num(m) and ZONE_MIN <= m <= ZONE_MAX
        rep.add(g, f"{zid}: multiplier within {ZONE_MIN}-{ZONE_MAX}", ok, "x%s" % m)
        if ok and m > 1:
            weak.append(zid)
            reach = z.get("reach") or {}
            melee = reach.get("melee") or []
            bad = [a for a in melee if a not in anim_set]
            rep.add(g, f"{zid}: weak point says how it is reached (ranged and/or melee moments = animations)",
                    bool(reach.get("ranged") or melee) and not bad,
                    "unknown animation: " + ", ".join(bad) if bad else
                    "ranged %s, melee during %s" % (reach.get("ranged", "no"), ", ".join(melee) or "never"))
        if ok and m < 1:
            armoured.append(zid)
        hi = z.get("heal_interrupt")
        if hi is not None:
            rep.add(g, f"{zid}: heal_interrupt within {ZONE_MIN}-{ZONE_MAX}, and the boss has a heal move",
                    is_num(hi) and ZONE_MIN <= hi <= ZONE_MAX and has_heal, "x%s" % hi)
        bh = z.get("break_hp")
        if bh is not None:
            if isinstance(bh, dict):
                ok = is_num(bh.get("base")) and bh["base"] > 0 and is_num(bh.get("per_extra_player", 0)) \
                    and bh.get("per_extra_player", 0) >= 0
                base, at8 = bh.get("base"), (bh.get("base", 0) + bh.get("per_extra_player", 0) * (PARTY_MAX - 2)) if ok else "?"
            else:
                ok, base, at8 = is_num(bh) and bh > 0, bh, bh
            hp = (spec.get("stats") or {}).get("hp") or 0
            rep.add(g, f"{zid}: break_hp > 0 and below the boss's HP", ok and hp and at8 < hp,
                    f"{base} (2 players = {base / hp * 100:.0f} % of max HP), {at8} at 8 players" if ok and hp else bh)
            rw = z.get("reward")
            rep.add(g, f"{zid}: break_hp is used by a mutation (zone_broken) or has a reward",
                    zid in broken_by or bool(rw),
                    ("mutation, " if zid in broken_by else "no mutation, ") + ("reward %s" % rw if rw else "no reward"))
        if z.get("sound"):
            sounds.append((f"hit_zones.{zid}.sound", z["sound"]))
    if kind != "minion":
        rep.add(g, "at least one weak point (> 1) and one armoured part (< 1)", bool(weak) and bool(armoured),
                "weak: %s; armoured: %s" % (", ".join(weak) or "none", ", ".join(armoured) or "none"))

    g = "mutations"
    for mid, mut in mutations.items():
        conds = (mut.get("when") or {}).get("any") or []
        bad = []
        for c in conds:
            if "hp_below" in c:
                if not (is_num(c["hp_below"]) and 0 < c["hp_below"] < 1):
                    bad.append(c)
            elif "zone_broken" in c:
                if (zones.get(c["zone_broken"]) or {}).get("break_hp") is None:
                    bad.append(c)
            else:
                bad.append(c)
        rep.add(g, f"{mid}: when.any = hp_below (0-1) and/or zone_broken (a zone with break_hp)", bool(conds) and not bad,
                "bad: %s" % bad if bad else "; ".join(", ".join(f"{k} {v}" for k, v in c.items()) for c in conds))
        hide, show = mut.get("hide_bones") or [], mut.get("show_bones") or []
        lost = [str(b) for b in hide + show if not match_bones([b], bones)]
        rep.add(g, f"{mid}: every hide/show bone exists in concept.yml", bool(hide or show) and not lost,
                "not drawn: " + ", ".join(lost) if lost else "hide %d, show %d" % (len(match_bones(hide, bones)), len(match_bones(show, bones))))
        both = sorted(match_bones(hide, bones) & match_bones(show, bones))
        rep.add(g, f"{mid}: no bone both hidden and shown; body, head and root stay", not both and
                not match_bones(hide, bones) & {"root", "body", "head"}, ", ".join(both))
        if mut.get("animation"):
            need_anim(f"{mid}.animation", mut["animation"])
        aset = mut.get("animation_set") or {}
        unknown = [k for k in aset if k not in anim_set]
        for v in aset.values():
            need_anim(f"{mid}.animation_set", v)
        ok = bool(mut.get("animation")) and is_int(mut.get("transition_ticks")) and mut["transition_ticks"] > 0 \
            and mut["animation"] in anim_set and not unknown and all(v in anim_set for v in aset.values())
        rep.add(g, f"{mid}: transition animation + transition_ticks, animation_set names exist", ok,
                "unknown: " + ", ".join(unknown) if unknown else
                "%s (%s ticks); %s" % (mut.get("animation"), mut.get("transition_ticks"),
                                       ", ".join(f"{k} -> {v}" for k, v in aset.items()) or "no set change"))
        removed = mut.get("remove_moves") or []
        added = mut.get("add_moves") or []
        sub = mut.get("substitute") or {}
        bad = [m for m in removed + added + list(sub.values()) if m not in moves] + \
              [k for k in sub if k not in removed] + [v for v in sub.values() if v in removed]
        rep.add(g, f"{mid}: remove_moves / add_moves / substitute name existing moves", not bad,
                "bad: " + ", ".join(map(str, bad)) if bad else
                "remove %s; substitute %s" % (", ".join(removed) or "none", ", ".join(f"{k} -> {v}" for k, v in sub.items()) or "none"))

        def after(names):
            return [sub.get(n, n) for n in names if n not in removed or n in sub]

        empty = [p["id"] for p in spec.get("phases") or [] if not (after(p.get("moves") or []) + added)]
        rep.add(g, f"{mid}: every phase still has a move afterwards", not empty, "empty: " + ", ".join(empty) if empty else
                "; ".join("%s: %s" % (p["id"], ", ".join(dict.fromkeys(after(p.get("moves") or []) + added)))
                          for p in spec.get("phases") or []))
        orphan = [f"reaction {r.get('when')}" for r in spec.get("reactions") or [] if r.get("do") in removed and r["do"] not in sub]
        for mv_id, mv in moves.items():
            if mv_id in removed:
                continue
            ws = mv.get("while_shielded")
            if ws and not after(ws):
                orphan.append(f"{mv_id}.while_shielded")
        rep.add(g, f"{mid}: no reaction or shield left with only a removed move", not orphan, ", ".join(orphan))
        sp = mut.get("speed", 1)
        rep.add(g, f"{mid}: speed between 0.5 and 2", is_num(sp) and 0.5 <= sp <= 2, sp)
        sounds += [(f"mutations.{mid}.sounds.{k}", v) for k, v in (mut.get("sounds") or {}).items()]
        rep.add(g, f"{mid}: has a start sound", bool((mut.get("sounds") or {}).get("start")), (mut.get("sounds") or {}).get("start"))
    return sounds


def check_mob(mob, boss_dir: Path, rep: Report, where: str):
    spec_file = boss_dir.parent / str(mob) / "boss.yml"
    if spec_file.exists():
        try:
            k = load_yaml(spec_file).get("kind")
        except Exception as e:  # noqa: BLE001
            k = f"unreadable ({e})"
        rep.add("mechanics", f"{where}: '{mob}' has its own kind: minion spec", k == "minion", f"{spec_file.parent.name}/boss.yml kind {k}")
    else:
        rep.add("mechanics", f"{where}: '{mob}' is vanilla or has a minion spec", mob in VANILLA_MOBS,
                "vanilla" if mob in VANILLA_MOBS else "no spec folder, not a known vanilla mob")


# ---------------------------------------------------------------------------------------- concept
def check_concept(spec, boss_dir: Path, rep: Report):
    from PIL import Image

    g = "concept"
    cdir = boss_dir / "concept"
    files = ["front.png", "side.png", "back.png", "palette.png", "front_1x.png", "side_1x.png", "back_1x.png",
             "concept.yml"]
    missing = [f for f in files if not (cdir / f).exists()]
    if not rep.add(g, "concept sheet files", not missing, "missing: " + ", ".join(missing) if missing else ", ".join(files[:4])):
        return
    style = boss_dir.parent / "style.md"
    palette = load_palette(style) if style.exists() else {}
    if not rep.add(g, "style.md palette (8-16 colours)", 8 <= len(palette) <= 16, f"{len(palette)} colours"):
        return
    allowed = set(palette.values())
    outside = set()
    for v in ("front", "side", "back"):
        img = Image.open(cdir / f"{v}_1x.png").convert("RGBA")
        outside |= {c[:3] for _, c in img.getcolors(1 << 20) if c[3] > 0 and c[:3] not in allowed}
    rep.add(g, "pixel art uses the palette only", not outside,
            "outside: " + ", ".join(hexa(c) for c in sorted(outside)) if outside else "0 colours outside style.md")
    parts = load_yaml(cdir / "concept.yml")["parts"]
    cubes = [p for p in parts if not p.get("paint")]
    kind = spec.get("kind")
    hidden = hidden_bones(spec, {p["bone"] for p in parts})
    extra_files = (["zones.png"] if isinstance(spec.get("hit_zones"), dict) and len(spec["hit_zones"]) > 1 else []) + \
                  [f"mutation_{m}.png" for m in (spec.get("mutations") or {})]
    if extra_files:
        gone = [f for f in extra_files if not (cdir / f).exists()]
        rep.add(g, "zone overlay and mutated views are drawn", not gone,
                "missing: " + ", ".join(gone) if gone else ", ".join(extra_files))
    if hidden:
        rep.add(g, "bones hidden until a mutation are drawn (counted in the cube budget)", "INFO",
                "%s: %d cubes" % (", ".join(sorted(hidden)), sum(1 for p in cubes if p["bone"] in hidden)))
    budget = CUBE_BUDGET.get(kind, 0)
    rep.add(g, f"cubes <= budget ({budget})", len(cubes) <= budget, f"{len(cubes)} cubes, {len(parts) - len(cubes)} painted details")
    used = {p["bone"] for p in parts}
    extras = spec.get("bones") or []
    rep.add(g, "extra bones: each declared once, none is a fixed name",
            len(extras) == len(set(extras)) and not set(extras) & set(FIXED_BONES), f"{len(extras)} extras")
    unknown = sorted(used - set(FIXED_BONES) - set(extras))
    rep.add(g, "every bone drawn is a fixed name or declared in boss.yml > bones", not unknown,
            "undeclared: " + ", ".join(unknown) if unknown else f"{len(used)} bones drawn")
    idle = sorted(set(extras) - used)
    rep.add(g, "every declared extra bone is drawn", not idle, "not drawn: " + ", ".join(idle) if idle else "")
    rep.add(g, "body and head are drawn", {"body", "head"} <= used)
    size = spec.get("size") or {}
    if all(is_num(size.get(k)) for k in ("width", "height")):
        hw, hh = size["width"] * PX_PER_BLOCK / 2, size["height"] * PX_PER_BLOCK
        top = max(p["from"][1] + p["size"][1] for p in cubes)
        reach = max(max(abs(p["from"][a]), abs(p["from"][a] + p["size"][a])) for p in cubes for a in (0, 2))
        core = [p for p in cubes if p["bone"] in ("body", "hip", "chest", "neck") or p["bone"].startswith(("leg", "shin", "foot"))]
        core_reach = max((max(abs(p["from"][a]), abs(p["from"][a] + p["size"][a])) for p in core for a in (0, 2)), default=0)
        rep.add(g, "trunk and legs stay inside the hitbox width", core_reach <= hw,
                f"reach {core_reach} px, half hitbox {hw:g} px")
        rep.add(g, "hitbox height between 75 % and 100 % of the drawn height", 0.75 * top <= hh <= top,
                f"hitbox {hh:g} px, drawn {top} px ({top / PX_PER_BLOCK:g} blocks), widest reach {reach} px")


# ---------------------------------------------------------------------------------------- model
def model_view(model, view, bounds):
    """The model seen straight on (front / side / back) at 1 px = 1/16 block, from the .bbmodel alone:
    same frame and same rule as the concept views (nearest face wins). Cubes are not rotated at rest."""
    from PIL import Image

    u_min, u_max, y_max = bounds
    w, h = u_max - u_min, y_max
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    tex = model.textures[0]
    tpx = tex.load()
    kx = tex.width / model.resolution.get("width", tex.width)
    ky = tex.height / model.resolution.get("height", tex.height)
    zbuf = {}
    face = {"front": "north", "side": "east", "back": "south"}[view]
    for bone, cube in model.cubes():
        if not model.shown(bone) or cube.get("visibility", True) is False:
            continue
        f = (cube.get("faces") or {}).get(face) or {}
        if f.get("texture") is None:
            continue
        (x0, y0, z0), (x1, y1, z1) = cube["from"], cube["to"]
        if view == "front":
            left, depth, fw = -x1, -z0, x1 - x0
        elif view == "side":
            left, depth, fw = -z1, x1, z1 - z0
        else:
            left, depth, fw = x0, z1, x1 - x0
        fh = y1 - y0
        u1, v1, u2, v2 = f["uv"]
        for j in range(int(fh)):
            for i in range(int(fw)):
                sx, sy = int(left) + i - u_min, h - 1 - (int(y1) - 1 - j)
                if not (0 <= sx < w and 0 <= sy < h) or depth < zbuf.get((sx, sy), -10**9):
                    continue
                c = tpx[min(int((u1 + (i + 0.5) / fw * (u2 - u1)) * kx), tex.width - 1),
                        min(int((v1 + (j + 0.5) / fh * (v2 - v1)) * ky), tex.height - 1)]
                if c[3]:
                    zbuf[(sx, sy)] = depth
                    px[sx, sy] = c
    return img


def check_model(spec, boss_dir: Path, rep: Report, step: str):
    from bbmodel import BETTERMODEL_TAGS, FORMAT_VERSION, MODEL_FORMAT, Model, is_helper, sha256
    from common import TEXTURE_BUDGET

    g = "model"
    mid = spec.get("id", boss_dir.name)
    path = boss_dir / f"{mid}.bbmodel"
    if not rep.add(g, f"{mid}.bbmodel exists", path.exists(), path.name):
        return
    try:
        model = Model(path)
    except Exception as e:  # noqa: BLE001
        rep.add(g, ".bbmodel can be read (JSON, embedded texture)", False, f"{type(e).__name__}: {e}")
        return
    meta = model.meta
    rep.add(g, f"Blockbench format pinned ({FORMAT_VERSION}, generic model, per-face UV)",
            str(meta.get("format_version")) == FORMAT_VERSION and meta.get("model_format") == MODEL_FORMAT
            and meta.get("box_uv") is False,
            "format_version %s, model_format %s, box_uv %s" % (meta.get("format_version"), meta.get("model_format"), meta.get("box_uv")))
    sha_path = path.with_name(path.name + ".sha")
    scripted = sha_path.exists() and sha_path.read_text(encoding="utf-8").split()[0] == sha256(path)
    if not sha_path.exists():
        rep.add(g, f"{sha_path.name} exists", False, "the hash of the last script-written version is missing")
    else:
        rep.add(g, "hash file: who wrote the model last", "INFO",
                "the script (sha256 matches)" if scripted else
                "EDITED BY HAND since the last script write: hand edits win, never regenerate over it")

    # ---- bones
    bones = model.bones
    names = {b for b in bones if not is_helper(b)}     # the drawn bones (no hitbox, no hit-zone box)
    extras = set(spec.get("bones") or [])
    rig_file = boss_dir / "model.yml"
    rig = (load_yaml(rig_file) or {}) if rig_file.exists() else {}
    tops = [b for b, v in bones.items() if v["parent"] is None]
    rep.add(g, "one bone tree under `root`, every bone named once, no cube outside a bone",
            tops == ["root"] and not model.duplicates and not model.loose,
            "top: %s; twice: %s; loose cubes: %d" % (", ".join(tops), ", ".join(model.duplicates) or "none", len(model.loose)))
    unknown = sorted(names - set(FIXED_BONES) - extras)
    rep.add(g, "every bone is a fixed name or declared in boss.yml > bones", not unknown,
            "unknown: " + ", ".join(unknown) if unknown else
            f"{len(names)} bones + hitbox + {len(model.zone_boxes())} hit-zone boxes")
    need = sorted(({"root", "body", "head"} | extras | concept_bones(boss_dir)) - names)
    rep.add(g, "root, body, head, every declared bone and every concept bone exist", not need,
            "missing: " + ", ".join(need) if need else "")
    bad = sorted(b for b in bones if ("_" in b and b.split("_")[0] in BETTERMODEL_TAGS) or "glow" in b)
    rep.add(g, "no bone name is read as a BetterModel tag (h_, b_, p_, glow ...)", not bad, ", ".join(bad))
    empty = sorted(b for b in names - {"root"} if not bones[b]["cubes"])
    rep.add(g, "every bone except root has cubes", not empty, "empty: " + ", ".join(empty) if empty else "")

    # ---- cubes
    cubes = model.cubes()
    kind = spec.get("kind")
    budget = CUBE_BUDGET.get(kind, 0)
    cfile = boss_dir / "concept" / "concept.yml"
    drawn = sum(1 for p in load_yaml(cfile)["parts"] if not p.get("paint")) if cfile.exists() else None
    rep.add(g, f"cubes <= budget ({budget})", len(cubes) <= budget,
            f"{len(cubes)} cubes (hitbox and hit-zone boxes not counted)" + (f"; concept: {drawn}" if drawn is not None else ""))
    if drawn is not None and drawn != len(cubes):
        rep.add(g, "cube count differs from the concept", "INFO",
                f"{len(cubes) - drawn:+d} (cubes added or removed at step 2: named in the report of the step)")
    off = [c["name"] for _, c in cubes if any(abs(v - round(v)) > 1e-6 for v in list(c["from"]) + list(c["to"]))
           or any(c["to"][a] - c["from"][a] <= 0 for a in range(3))]
    rep.add(g, "cubes on the 1/16 grid, three sizes > 0", not off, ", ".join(off[:8]))
    turned = [c["name"] for _, c in cubes if any(c.get("rotation") or [])] + \
             [b for b, v in bones.items() if any(v["rotation"] or [])]
    rep.add(g, "no cube or bone rotated at rest", not turned, ", ".join(turned[:8]))
    infl = [c["name"] for _, c in cubes if c.get("inflate")]
    rep.add(g, "no inflated cube", not infl, ", ".join(infl[:8]))

    # ---- pivots
    far = []
    for b in sorted(names - {"root"}):
        cs = bones[b]["cubes"]
        if not cs:
            continue
        pv = bones[b]["pivot"]
        lo = [min(c["from"][a] for c in cs) - 1 for a in range(3)]
        hi = [max(c["to"][a] for c in cs) + 1 for a in range(3)]
        if not all(lo[a] <= pv[a] <= hi[a] for a in range(3)):
            far.append("%s %s" % (b, pv))
    rep.add(g, "every pivot lies on its bone (inside the box of its cubes, 1 px margin)", not far, "; ".join(far))
    rep.add(g, "root pivot at the origin", list(bones.get("root", {}).get("pivot", [1])) == [0, 0, 0])

    # ---- texture
    tb = TEXTURE_BUDGET.get(kind, 0)
    ok_tex = len(model.textures) == 1
    rep.add(g, "one texture", ok_tex, f"{len(model.textures)}")
    if ok_tex:
        tex = model.textures[0]
        res = (model.resolution.get("width"), model.resolution.get("height"))
        rep.add(g, f"texture size <= {tb} x {tb}, = project resolution", tex.width <= tb and tex.height <= tb and res == tex.size,
                f"{tex.width} x {tex.height}, resolution {res[0]} x {res[1]}")
        style = boss_dir.parent / "style.md"
        allowed = set(load_palette(style).values()) if style.exists() else set()
        cols = tex.getcolors(1 << 20)
        outside = sorted({c[:3] for _, c in cols if c[3] > 0 and c[:3] not in allowed})
        half = sum(n for n, c in cols if 0 < c[3] < 255)
        used = {c[:3] for _, c in cols if c[3] > 0}
        rep.add(g, "texture uses the palette only", not outside,
                "outside: " + ", ".join(hexa(c) for c in outside[:10]) if outside else f"{len(used)} palette colours, 0 outside style.md")
        rep.add(g, "texture pixels are opaque or empty (no half transparency)", half == 0, f"{half} half-transparent px")
        tpx = tex.load()
        bad_uv, n_faces, blank = [], 0, 0
        for _, c in cubes:
            for fname, f in (c.get("faces") or {}).items():
                if f.get("texture") is None:
                    continue
                n_faces += 1
                u1, v1, u2, v2 = f["uv"]
                if not (0 <= min(u1, u2) and max(u1, u2) <= res[0] and 0 <= min(v1, v2) and max(v1, v2) <= res[1]) \
                        or u1 == u2 or v1 == v2 or f.get("texture") != 0:
                    bad_uv.append(f"{c['name']}.{fname}")
                    continue
                for x in range(int(min(u1, u2)), int(max(u1, u2))):
                    for y in range(int(min(v1, v2)), int(max(v1, v2))):
                        if tpx[x, y][3] == 0:
                            blank += 1
        rep.add(g, "every textured face has a UV rectangle inside the texture, on painted pixels",
                not bad_uv and blank == 0, f"{n_faces} textured faces" + (f"; bad: {', '.join(bad_uv[:6])}" if bad_uv else "")
                + (f"; {blank} empty px sampled" if blank else ""))
    glow_named = {c["name"] for _, c in cubes if "glow" in c["name"].lower()}
    glow_lit = {c["name"] for _, c in cubes if c.get("light_emission")}
    if scripted:
        rep.add(g, "emissive cubes: `light_emission` 15 and a name with `glow` go together", glow_named == glow_lit,
                f"{len(glow_lit)} emissive cubes" if glow_named == glow_lit else ", ".join(sorted(glow_named ^ glow_lit)[:8]))
    else:
        rep.add(g, "emissive cubes (name with `glow`, the BetterModel rule)", "INFO", f"{len(glow_named)}")

    # ---- hitbox
    size = spec.get("size") or {}
    hb = bones.get("hitbox")
    if rep.add(g, "`hitbox` bone under root with one cube", bool(hb) and hb["parent"] == "root" and len(hb["cubes"]) == 1):
        c = hb["cubes"][0]
        hw, hh = size["width"] * PX_PER_BLOCK / 2, size["height"] * PX_PER_BLOCK
        want = ([-hw, 0, -hw], [hw, hh, hw])
        got = (list(c["from"]), list(c["to"]))
        rep.add(g, "hitbox cube = boss.yml > size, centred, on the ground",
                all(abs(a - b) < 1e-6 for w_, g_ in zip(want, got) for a, b in zip(w_, g_)),
                "%g x %g x %g px (size %g x %g blocks)" % (got[1][0] - got[0][0], got[1][1] - got[0][1], got[1][2] - got[0][2],
                                                          size["width"], size["height"]))
        rep.add(g, "hitbox cube is not drawn (no textured face)",
                all(f.get("texture") is None for f in (c.get("faces") or {}).values()))

    # ---- hit zones and mutations
    zones = {k: v for k, v in (spec.get("hit_zones") or {}).items() if isinstance(v, dict)}
    zmap = rig.get("hit_zone_boxes") or {}
    zboxes = model.zone_boxes()
    mapped = {h: (zid, v) for zid, hs in zmap.items() for h, v in (hs or {}).items()}
    if zones or zboxes or zmap:
        miss = [f"{zid}: {pat}" for zid, zone in zones.items() for pat in zone.get("bones") or []
                if not match_bones([pat], names) or any(not bones[b]["cubes"] for b in match_bones([pat], names))]
        rep.add(g, "every hit-zone bone exists as its own bone with cubes", not miss,
                "missing: " + ", ".join(miss) if miss else "")
        rep.add(g, "model.yml > hit_zone_boxes lists exactly the zones of boss.yml", set(zmap) == set(zones),
                "zones: %s; mapped: %s" % (", ".join(sorted(zones)) or "none", ", ".join(sorted(zmap)) or "none"))
        bad, uncovered, loose_fit, rows, too_small, airy = [], [], [], [], [], []
        held: dict[str, float] = {}
        part_vol: dict[str, float] = {}
        for zid, zone in zones.items():
            want = match_bones(zone.get("bones"), names)
            have: dict[str, list] = {}
            for h, (z, v) in mapped.items():
                if z == zid:
                    have.setdefault((v or {}).get("bone"), []).append(h)
            for b in sorted(want):
                hs = have.get(b, [])
                if not 1 <= len(hs) <= ZONE_BOXES_PER_BONE:
                    uncovered.append(f"{zid}/{b}: {len(hs)} boxes")
            for b, hs in have.items():
                if b not in want:
                    bad.append(f"{hs[0]}: '{b}' is not a bone of zone {zid}")
        for h, (zid, v) in mapped.items():
            if h not in zboxes:
                bad.append(f"{h}: not in the model")
                continue
            parent, cs = zboxes[h]
            target = (v or {}).get("bone")
            if parent != target:
                bad.append(f"{h}: child of {parent}, mapped to {target}")
            if len(cs) != 1:
                bad.append(f"{h}: {len(cs)} cubes")
                continue
            c = cs[0]
            if any(f.get("texture") is not None for f in (c.get("faces") or {}).values()):
                bad.append(f"{h}: has a textured face")
            if c.get("visibility", True) is not False or bones[h]["visibility"]:
                bad.append(f"{h}: visible")
            if c.get("light_emission") or any(c.get("rotation") or []) or bones[h]["cubes"] != cs:
                bad.append(f"{h}: emissive or rotated")
            part = bones.get(target, {}).get("cubes") or []
            zone = zones.get(zid) or {}
            mult = zone.get("multiplier") or 1
            target_zone = mult > 1 or zone.get("break_hp") is not None    # players must reach it
            dims = [c["to"][a] - c["from"][a] for a in range(3)]
            if target_zone:
                need = [ZONE_BOX_MIN] * 3
                if mult > 1:
                    for a in sorted(range(3), key=lambda a: -dims[a])[:2]:
                        need[a] = ZONE_WEAK_FACE
                if any(dims[a] < need[a] for a in range(3)):
                    too_small.append("%s: %gx%gx%g px" % (h, *dims))
            if part:
                lo = [min(q["from"][a] for q in part) for a in range(3)]
                hi = [max(q["to"][a] for q in part) for a in range(3)]
                # an axis grown to the minimum size may stick out further than 1 px
                grown = [target_zone and hi[a] - lo[a] < dims[a] <= ZONE_WEAK_FACE for a in range(3)]
                inside = all(grown[a] or (lo[a] - 1 <= c["from"][a] and c["to"][a] <= hi[a] + 1) for a in range(3))
                vol = sum((q["to"][0] - q["from"][0]) * (q["to"][1] - q["from"][1]) * (q["to"][2] - q["from"][2]) for q in part)
                got = sum(max(0, min(q["to"][0], c["to"][0]) - max(q["from"][0], c["from"][0]))
                          * max(0, min(q["to"][1], c["to"][1]) - max(q["from"][1], c["from"][1]))
                          * max(0, min(q["to"][2], c["to"][2]) - max(q["from"][2], c["from"][2])) for q in part)
                held[target] = held.get(target, 0) + got
                part_vol[target] = vol
                if not inside:
                    loose_fit.append("%s: sticks out > 1 px" % h)
                air = 1 - got / (dims[0] * dims[1] * dims[2])
                if mult < 1 and air > ZONE_ARMOUR_AIR:
                    airy.append("%s: %.0f %% air" % (h, 100 * air))
                rows.append("%s (%s) on %s %gx%gx%g, %.0f %% air" % (h, zid, target, *dims, 100 * air))
        for b, got in held.items():
            if got < 0.6 * part_vol[b]:
                loose_fit.append("%s: boxes hold %.0f %% of the part" % (b, 100 * got / part_vol[b]))
        stray = sorted(set(zboxes) - set(mapped))
        tagged = sorted(h for h in zboxes if not h.startswith("zone_") or h.split("_")[0] in BETTERMODEL_TAGS)
        rep.add(g, f"1-{ZONE_BOXES_PER_BONE} hit-zone boxes per bone of every zone (every zone covered)", not uncovered,
                "; ".join(uncovered) if uncovered else f"{len(mapped)} boxes for {len(zones)} zones")
        rep.add(g, "each box: helper bone `zone_...` under its bone, one cube, invisible, no textured face",
                not bad and not stray and not tagged,
                "; ".join(bad + [f"{h}: not in hit_zone_boxes" for h in stray] + tagged))
        rep.add(g, "each box hugs its part (<= 1 px outside its cubes unless grown to the minimum; "
                   "the boxes of a bone hold >= 60 % of its volume)", not loose_fit, "; ".join(loose_fit))
        rep.add(g, f"weak and breakable boxes >= {ZONE_BOX_MIN} px on every axis, weak points show "
                   f">= {ZONE_WEAK_FACE}x{ZONE_WEAK_FACE} px", not too_small, "; ".join(too_small))
        rep.add(g, f"armoured boxes hold <= {ZONE_ARMOUR_AIR:.0%} air (they would steal hits from the body)",
                not airy, "; ".join(airy))
        clash = []
        hs = [h for h in mapped if h in zboxes and len(zboxes[h][1]) == 1]
        for a_i, a in enumerate(hs):
            for b in hs[a_i + 1:]:
                if mapped[a][0] == mapped[b][0]:
                    continue
                ca, cb = zboxes[a][1][0], zboxes[b][1][0]
                if all(min(ca["to"][k], cb["to"][k]) - max(ca["from"][k], cb["from"][k]) > 1e-6 for k in range(3)):
                    clash.append(f"{a} x {b}")
        rep.add(g, "no overlap between the boxes of two zones (at rest)", not clash, ", ".join(clash))
        wrong_rm = []
        for h, (zid, v) in mapped.items():
            target = (v or {}).get("bone")
            hiders = sorted(m for m, mut in (spec.get("mutations") or {}).items()
                            if target in match_bones(mut.get("hide_bones"), names))
            if ((v or {}).get("removed_by") or None) != (hiders[0] if hiders else None):
                wrong_rm.append(f"{h}: removed_by should be {hiders[0] if hiders else 'absent'}")
        rep.add(g, "boxes on bones hidden by a mutation are marked `removed_by` that mutation", not wrong_rm,
                "; ".join(wrong_rm) if wrong_rm else ", ".join(sorted(h for h, (_, v) in mapped.items() if (v or {}).get("removed_by"))) or "none")
        rep.add(g, "hit-zone boxes (not counted in the cube budget)", "INFO", "; ".join(rows))
    hidden = hidden_bones(spec, names)
    muts = spec.get("mutations") or {}
    if muts:
        miss = []
        for mut_id, mut in muts.items():
            for key in ("hide_bones", "show_bones"):
                for pat in mut.get(key) or []:
                    if not match_bones([pat], names):
                        miss.append(f"{mut_id}.{key}: {pat}")
        rep.add(g, "every bone hidden or shown by a mutation exists", not miss, ", ".join(miss))

    def off_at_rest(b):
        return not bones[b]["visibility"] and all(c.get("visibility", True) is False for c in bones[b]["cubes"])

    wrong = sorted(b for b in hidden if b in bones and not off_at_rest(b))
    wrong += sorted(b for b in names - hidden if not bones[b]["visibility"]
                    or any(c.get("visibility", True) is False for c in bones[b]["cubes"]))
    rep.add(g, "only the bones shown by a mutation are hidden at rest (visibility off)", not wrong,
            "wrong: " + ", ".join(wrong) if wrong else "hidden: " + (", ".join(sorted(hidden)) or "none"))
    if step == "model":
        rep.add(g, "no animation yet (step 3 writes them)", not model.animations, f"{len(model.animations)} animations")

    # ---- same outline as the approved concept
    cdir = boss_dir / "concept"
    if cfile.exists() and ok_tex and all((cdir / f"{v}_1x.png").exists() for v in ("front", "side", "back")):
        from PIL import Image

        added = rig.get("cubes") or []      # cubes added at step 2: the only place the outline may differ
        diffs, same, total, outside_added, on_added = [], 0, 0, 0, 0
        for v in ("front", "side", "back"):
            ref = Image.open(cdir / f"{v}_1x.png").convert("RGBA")
            w, h = ref.size
            u_min = -(w // 2)
            got = model_view(model, v, (u_min, w - w // 2, h))
            allowed = set()
            for q in added:
                (x0, y0, z0), (sx_, sy_, sz_) = q["from"], q["size"]
                left, span = {"front": (-(x0 + sx_), sx_), "side": (-(z0 + sz_), sz_), "back": (x0, sx_)}[v]
                allowed |= {(left + i - u_min, h - 1 - y) for i in range(span) for y in range(y0, y0 + sy_)}
            rp, gp = ref.load(), got.load()
            d = da = 0
            for y in range(h):
                for x in range(w):
                    a, b = rp[x, y], gp[x, y]
                    if (a[3] > 0) != (b[3] > 0):
                        if (x, y) in allowed:
                            da += 1
                        else:
                            d += 1
                    elif a[3] > 0:
                        total += 1
                        same += a[:3] == b[:3]
            outside_added += d
            on_added += da
            diffs.append(f"{v} {d} px" + (f" (+{da} px on the added cubes)" if da else ""))
        rep.add(g, "outline = concept in the front, side and back views (except on cubes added in model.yml)",
                outside_added == 0 if scripted else "INFO", "differs by: " + ", ".join(diffs)
                + ("" if scripted else " (hand-edited model: for information)"))
        rep.add(g, "pixels of the same colour as the concept views", "INFO",
                "%d of %d (%.0f %%); the rest is texture detail added at step 2" % (same, total, 100 * same / max(total, 1)))


def not_yet(rep: Report, step: str, asked: bool):
    what = {"animation": "animations in the model (one per spec name, length = windup + active + recovery)",
            "sound": "sounds/*.ogg (one per spec name, mono/stereo, loudness, LICENSES.md)"}[step]
    rep.add(step, what, "FAIL" if asked else "NOT YET",
            "validator part not written yet (written by the agent of this step, skill §5)")


def render(rep: Report, boss_dir: Path, step: str, iteration, spec) -> str:
    verdict = "FAIL" if rep.failed else "PASS"
    try:
        shown = boss_dir.relative_to(Path.cwd()).as_posix()
    except ValueError:
        shown = boss_dir.as_posix()
    out = [f"# Validator report: {spec.get('id', boss_dir.name)}, step `{step}`"
           + (f", iteration {iteration}" if iteration else ""), "",
           f"- Date: {datetime.date.today().isoformat()}",
           f"- Command: `python bosses/_tools/validate.py {shown} --step {step}`",
           f"- **Verdict: {verdict}** ({rep.count('PASS')} PASS, {rep.count('FAIL')} FAIL, "
           f"{rep.count('NOT YET')} not yet)", "",
           "| Group | Check | Result | Numbers |", "|---|---|---|---|"]
    for grp, check, status, detail in rep.rows:
        out.append("| %s | %s | %s | %s |" % (grp, check.replace("|", "/"), "**FAIL**" if status == "FAIL" else status,
                                               detail.replace("|", "/").replace("\n", " ")))
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Boss pipeline validator")
    ap.add_argument("boss_dir", type=Path)
    ap.add_argument("--step", choices=STEPS, required=True)
    ap.add_argument("--report", type=Path, help="also write the markdown report to this file")
    ap.add_argument("--iteration", type=int, default=0)
    args = ap.parse_args()
    boss_dir = args.boss_dir.resolve()
    rep = Report()
    try:
        spec = load_yaml(boss_dir / "boss.yml")
    except Exception as e:  # noqa: BLE001  (missing file, bad yaml, key written twice)
        print(f"cannot read {boss_dir / 'boss.yml'}: {e}", file=sys.stderr)
        return 2
    rep.add("format", "boss.yml parses, no key written twice", isinstance(spec, dict))
    if isinstance(spec, dict):
        try:
            check_spec(spec, boss_dir, rep)
            check_concept(spec, boss_dir, rep)
        except Exception as e:  # noqa: BLE001  a malformed spec must give a FAIL row, not a traceback
            rep.add("format", "spec can be checked to the end", False, f"{type(e).__name__}: {e}")
    asked_model = STEPS.index(args.step) >= STEPS.index("model")
    if asked_model and isinstance(spec, dict):
        try:
            check_model(spec, boss_dir, rep, args.step)
        except Exception as e:  # noqa: BLE001  a broken model must give a FAIL row, not a traceback
            rep.add("model", "model can be checked to the end", False, f"{type(e).__name__}: {e}")
    elif not asked_model:
        rep.add("model", "<boss>.bbmodel (bones, cube budget, grid, texture, palette, hitbox)", "NOT YET",
                "checked from `--step model` on")
    for step in STEPS[2:]:
        not_yet(rep, step, asked=STEPS.index(step) <= STEPS.index(args.step))
    text = render(rep, boss_dir, args.step, args.iteration, spec if isinstance(spec, dict) else {})
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
