---
name: boss-building
description: Builds a Hatlas dungeon boss or mini-boss end to end: references + style guide → boss.yml spec and concept sheet → Blockbench .bbmodel (script-written, user-polished) → animations → AI-generated sounds → behaviour code in hatlas-dungeons → bot fight test, with one agent per step and the user's approval between steps. Use when designing, modelling, animating, sounding, coding or testing a boss, or when asked how the boss pipeline works.
---

# Building a Hatlas boss

> **Status: process defined 2026-11-18 (round 22, `docs/cities-and-dungeons.md` §4.1–4.4).** The
> scripts of `bosses/_tools/` are written during the pilot (the **Fungal Root**, `dark_forest`) by the
> agent of the step that first needs them, then reused. **Built:** step 1 (`concept_build.py`,
> `concept_sheet.py`, `validate.py --step design`) and step 2 (`bbmodel.py`, `texture.py`, `render.py`,
> `validate.py --step model`, 2026-11-21). **To write:** animation previews and `sound.py`.

Every boss is **made from files, not from chat**. Each step reads the files of the previous steps and
writes its own; agents never pass results through the conversation. That keeps each step re-runnable,
reviewable, and checkable by someone who did not make it.

## 1. Sources of truth
1. `docs/cities-and-dungeons.md` §4 (pipeline, fight design rules §4.2, sound §4.3, pilot §4.4) and
   §7.3 (fight zones: where bosses live). Never contradict them; if a step cannot satisfy them, stop
   and report.
2. `bosses/<dungeon>/style.md`: the dungeon's **style guide** (ambiance, palette as hex codes,
   proportions, scale, materials, sound palette). Read by **every** agent. Written by the designer at
   the first boss of a dungeon, approved by the user.
3. `bosses/<dungeon>/<boss>/boss.yml`: the **spec**. Every animation, sound and move name is written
   there once; every later step reuses those names exactly.
4. `bosses/<dungeon>/<boss>/refs/`: the user's reference images (+ `refs/README.md`: one line per
   image: what to take from it, source, licence). Only own images or images whose licence allows use on
   a paid server. Third-party images without such a licence are **mood references only**, kept in the
   git-ignored `refs/private/`: take general ideas (palette family, materials, mood), **never copy a
   design** (silhouette, face, weapon, details) — the character must be our own. **Never download
   references from the Internet** without the user.

## 2. Files (the contract between agents)
```
bosses/
  _tools/                         scripts shared by every boss (committed)
    validate.py                   checks boss.yml + bbmodel + sounds against each other (§5)
    bbmodel.py                    writes/reads .bbmodel JSON (cubes, bones, pivots, texture; keyframes: step 3).
                                  `build <boss>`: concept.yml + model.yml -> .bbmodel + .sha; refuses a
                                  hand-edited file. Format and BetterModel conventions in its header
    texture.py                    pixel-art texture from a palette + UV layout (Pillow)
    render.py                     preview of a .bbmodel without Blockbench (Pillow software renderer, reads
                                  only the file): turntable, model beside concept, from below, mutations,
                                  pivot-check poses. Replaces the planned three.js render.mjs for stills;
                                  animation GIFs (step 3) extend it
    sound.py                      trim, loudnorm, mono/stereo, ogg (ffmpeg), sounds.json entries
  <dungeon>/
    style.md                      style guide of the dungeon (committed, approved)
    <boss>/
      refs/                       user's images + README.md (committed)
      boss.yml                    spec (committed, approved)
      concept/                    concept sheet: front.png, side.png, back.png, palette.png (committed)
      model.yml                   the rig of step 2 (committed): parent + pivot per bone, texture size,
                                  extra painted details, emissive bones, pivot-check poses
      <boss>.bbmodel              the model (committed; after the user's polish, the user's file wins)
      <boss>.bbmodel.sha          hash of the last script-written version (committed)
      sounds/*.ogg                final sounds (committed)
      sounds/LICENSES.md          per sound: tool, plan, date, prompt, take kept (committed)
      reports/<step>-<n>.md       validator + review report per iteration (committed)
      out/                        GIT-IGNORED: renders, turntables, animation previews, raw sound takes
```
- **Hand edits win:** before writing `<boss>.bbmodel`, compare its hash with `<boss>.bbmodel.sha`. If
  they differ, the user edited it in Blockbench: **do not overwrite**. Read the user's version, apply
  changes on top of it (or ask), and record the new hash.
- Pinned versions everywhere (Python packages, three.js from cdnjs, BetterModel, the Blockbench MCP
  plugin).

## 3. Agents and steps

The **main session orchestrates**: it starts each agent with the paths, the iteration number and the
user's last remarks (not a summary of the conversation), checks the outputs exist, runs the validator,
and **asks the user to approve** at each gate (★). Agents start cold.

| # | Agent (`.claude/agents/`) | Model | Reads | Writes |
|---|---|---|---|---|
| 0 | user | | | `refs/` + `refs/README.md` (**the pipeline waits for them**) |
| 1 | `boss-designer` | Fable 5.2 | §4 of the plan, `style.md` (or writes it), `refs/`, the other bosses of the dungeon | `style.md` (first boss only), `boss.yml`, `concept/*.png` |
| ★ | user approves spec + concept sheet (or names changes → 1) | | | |
| 2 | `boss-modeler` | Fable 5.2 (pilot), then Opus 5.5 if the pilot shows no gap | `boss.yml`, `concept/`, `style.md`, `refs/` | `<boss>.bbmodel` (bones, cubes, pivots, hitbox, texture), turntable renders in `out/` |
| ★ | user approves the model (may polish it in Blockbench first) | | | |
| 3 | `boss-animator` | Opus 5.5 | `boss.yml`, `<boss>.bbmodel` | keyframes for every animation of the spec, previews in `out/` |
| ★ | user approves the animations | | | |
| 4 | `boss-sound` | Opus 5.5 | `boss.yml`, `style.md` (sound palette) | prompts, takes in `out/`, final `sounds/*.ogg`, `LICENSES.md`, `sounds.json` fragment |
| ★ | user **listens** and approves (Claude cannot hear) | | | |
| 5 | `boss-coder` | Opus 5.5 | `boss.yml`, the model, the sounds, `hatlas-dungeons` code | behaviour (state machine), config, pack wiring, BetterModel import |
| 6 | `ingame-tester` (exists) | Opus 5.5 | `boss.yml` + the code | bot fights on the test stack: phases, tells, punish windows, enrage, minions, death, loot |
| ★ | user fights it in game and approves, or asks for changes → back to the step concerned | | | |

All steps are sequential (each needs the previous one's files). Steps 3 and 4 may run in parallel once
the model is approved, because they only read it. The validator (§5) runs after **every** step; a FAIL
blocks the gate.

## 4. Steps in detail

### Step 1: `boss-designer`
- If `style.md` is missing for the dungeon, write it first from the dungeon's ambiance (`worldgen/map.md`,
  `donjons.yml > types`, its build) and the refs: palette (8–16 hex colours), silhouette rules,
  scale of mini-bosses vs the final boss, materials, **sound palette** (what this dungeon sounds like).
- Write `boss.yml` in the format of plan §4.1. Apply the fight design rules of §4.2: a distinct tell per
  attack (pose + sound + particles), long enough for 20 Hz with ~100 ms ping (wind-up ≥ 10 ticks for a
  dodgeable hit); phases by HP each changing moves or rhythm, with an entry animation; reactions to
  distance, blocking, healers and groups (party roles of `docs/job-skills.md`); punish windows after
  big moves; damage cap per hit; enrage timer. A mini-boss teaches **one** mechanic; the final boss mixes
  the three mini-bosses' mechanics.
- **Phase mechanics** (plan §4.5), used where they fit the character:
  - **protectors** (`kind: summon`, `protect: true`): the boss is immune until every protector is dead;
    shield animation, tethers, immune sound, count scaled by party size, enrage keeps running;
  - **heal channel** (`kind: heal`): heals for a while, stopped by `interrupt.damage` dealt during it →
    stagger, optionally `goto_phase`; never above the phase ceiling;
  - **side waves** (`phases[].waves`): optional adds, never required, capped by `max_alive`.
  Each summoned or wave mob that is not vanilla is a **minion** with its own spec (`kind: minion`, own
  folder): write the minion's `boss.yml` and concept sheet in the same step. Any boss may summon when
  the creature fits it; say why, or why not.
- **Mandatory for every mini-boss and final boss** (✔ user 2026-11-20, round 25; minions exempt):
  - **at least one mob phase**: either side waves running **in parallel** with the boss's attacks
    (`phases[].waves`), or a **protector** summon (`protect: true`) whose minions shield the boss's
    health while any of them is alive. Both may exist.
  - **every protector summon has a timeout** `protect_timeout_ticks` (default **1200 = 60 s**, at most
    2400) in case a minion is bugged (stuck in a wall, out of the arena, unreachable): when it ends the
    shield drops, the remaining protectors die with an effect (no XP, no drop), and the fight goes on.
    A protector that leaves the arena or cannot path to a player for 10 s is teleported back to its
    spawn point first. The enrage timer keeps running during the shield, so waiting out the timeout is
    never the better play.
  - **at least one mutation** (plan §4.6) that triggers **in one of the last phases** (the last or the
    second-to-last), by `hp_below` (≤ 0.40) and optionally earlier by a broken part; it must visibly
    change the body (hidden/shown bones) and the fight (moves, speed or rhythm).
- **Hit zones** (plan §4.6, ✔ OQ 123): `hit_zones` maps bones to damage multipliers 0.5–2.0 (applied
  before the per-hit cap); at least one **weak point** (glows, reachable in melee at some moment or by
  bow) and one **armoured** part per boss/mini-boss (minions: optional). A zone may have `break_hp`
  (✔ OQ 125): breaking it triggers a mutation early and gives a reward.
- **Mutations** (plan §4.6, ✔ OQ 124): `mutations` on the **same entity**: `hide_bones` / `show_bones`
  of the same model (mutated parts are drawn in the concept and built in step 2, hidden ones marked),
  a transition `animation`, an `animation_set` swap, moves removed/added, speed. Never kill and respawn.
  A second model only for a whole new body, swapped on the same entity.
- Music per phase (`phases[].music`) only within the budget of plan §4.3 (final boss: one per phase;
  mini-boss: one; minion: none).
- Concept sheet: front, side, back views as **pixel art at the model's scale** (1 px = 1/16 block),
  palette only, with the hitbox drawn as a dashed frame and the bone names written beside. Generated by
  script (Pillow), not by an image AI.
- Report: the fight described as a player would live it (30 s per phase), and the open choices.

### Step 2: `boss-modeler`
- Build the model with `_tools/bbmodel.py` from the concept sheet: a bone per moving part (names from a
  fixed list: `root`, `body`, `head`, `arm_l`, `arm_r`, `leg_l`, `leg_r`, + extras declared in
  `boss.yml > bones`), pivots at the joints, cubes on the 1/16 grid, **cube budget** (minion ≤ 40,
  mini-boss ≤ 120, boss ≤ 250, to confirm in the pilot), one texture (minion ≤ 64×64, mini-boss
  ≤ 128×128, boss ≤ 256×256) painted with
  `_tools/texture.py` from the palette.
- Hitbox = `boss.yml > size`, drawn as a `hitbox` bone (BetterModel 3.7.1 creates its hitbox from a
  bone named `hitbox` or tagged `b_`/`ob_`; a bone's box is **its largest cube**). Bone names are the
  spec's, never with a BetterModel tag prefix (`h_`, `b_`, `p_`, `glow` ... would be parsed and renamed);
  hit-zone bones get their hitbox from the code (`EntityTracker.createHitBox(listener, BonePredicate)`).
  Bones shown only by a mutation are written with `visibility: false` (shown at runtime with
  `TrackerUpdateAction.togglePart`). Emissive cubes: `light_emission: 15` + a name ending in `_glow`.
- **Hit-zone boxes** (✔ user 2026-11-21, plan §4.6): because a bone's hitbox is only its largest cube,
  **every hit zone gets one invisible box that covers the whole part**, never a visible cube:
  - one helper bone per zone, child of the zone's main bone (so it follows the animations), holding
    **one untextured cube** with `visibility: false`, named after the zone (e.g. `zone_eyes`,
    `zone_sap_bulb`, `zone_legs_fl`…; a zone over several moving bones, like four legs, gets one box per
    moving bone, all mapped to the same zone); no BetterModel tag prefix;
  - the box hugs the part's visible cubes (≤ 1 px margin) and never overlaps another zone's box: the
    smaller (weak) zone wins where they touch; weak points should stay a little smaller than they look;
  - **zone boxes do not count in the cube budget** and are not painted; the validator checks one box
    per zone bone, inside the main hitbox or touching the part, and no overlap between zones;
  - the mapping zone → box bones is written in `model.yml` (`hit_zone_boxes`), read by the coder, who
    creates them with `EntityTracker.createHitBox(listener, BonePredicate.name(...))`;
  - the main `hitbox` bone stays the body hitbox (×1.0 default zone);
  - fallback if the pilot shows BetterModel zone hitboxes do not work: a ray test from the player's eye
    (or the projectile path) against the same boxes, so the boxes are useful either way.
- Previews: turntable (8 angles) + front/side next to the concept sheet, so the gate compares them.
- Blockbench MCP (if installed): only to screenshot the model as Blockbench shows it and to apply small
  edits while the user watches; the file stays the source of truth.

### Step 3: `boss-animator`
- One animation per name of `boss.yml > animations`. A move's animation length **equals**
  `windup + active + recovery` ticks (÷ 20 = seconds), with the wind-up pose readable from 10 blocks
  away. Loops: `idle_*`, `walk`, `run`. One-shots: everything else.
- Keyframes on bones only (no scale on the root), easing kept simple; no clipping through the body.
- Previews: one GIF/MP4 per animation (extend `_tools/render.py`, which already poses bones).

### Step 4: `boss-sound` (✔ OQ 103: mostly AI generated; tools: plan §4.3, OQ 121)
- Effects and voices: ElevenLabs Sound Effects (paid plan, API, the agent may generate). Music: Suno
  Pro/Premier **by the user** on the website from the agent's prompts (no unofficial API); the user
  keeps the download record.
- One prompt per sound name of `boss.yml` (`moves.*.sounds`, phase entries, idle, hurt, death, music for
  a final boss), written from the dungeon's sound palette so all bosses of a dungeon sound related.
- Generate with an AI tool **whose plan allows commercial use**. The agent needs the user's API key in
  the environment (never in a file, never printed); without it, it writes `out/prompts.md` and **stops**
  so the user can generate the takes and drop them in `out/takes/`.
- 3 takes per sound when possible; `_tools/sound.py` trims, normalizes (ffmpeg `loudnorm`, −16 LUFS for
  effects, −20 for music), converts to `.ogg` (mono for positional sounds, stereo music), and writes the
  `sounds.json` fragment and subtitle keys (EN + FR).
- `LICENSES.md`: tool, plan, generation date, prompt, take kept. Vanilla sounds only as filler.
- The gate is the user's ears: list each sound with what it should evoke.

### Step 5: `boss-coder`
- Works in `../hatlas-dungeons` (boss framework, plan §8) on its own `feat/` branch; until that repo
  exists, it **stops** and reports what it needs.
- Reads `boss.yml` at runtime (no hard-coded numbers): state machine phases → moves → wind-up (play
  animation + sound + particles + ground warning) → active (hit shape) → recovery; reactions; defences;
  enrage; damage cap. Animations through BetterModel, sounds through the `hatlas` pack.
- Never changes `boss.yml` on its own: if the spec cannot be built, report it.

### Step 6: `ingame-tester`
- Scenarios per boss: spawn, each phase reached by damage, each tell fires before its hit (wind-up ≥ the
  spec), a bot standing still gets hit and a bot moving away in the wind-up does not, punish window
  open, enrage after the timer, minions despawn with the boss, death drops loot, no exception.
- Phase mechanics: hits on a protected boss do no damage; killing the last protector drops the shield; a
  protector pushed out of the zone respawns; a heal channel completes when ignored and is interrupted
  (stagger, `goto_phase`) when the bots deal the threshold; healing never crosses the phase ceiling; side
  waves never exceed `max_alive` and the boss stays damageable while they live.

## 5. Validator (`_tools/validate.py`), run after every step
- `boss.yml` matches the format (required keys, types, phases ordered by `hp_below`, every move and
  defence used by a phase, every name unique).
- Every animation and sound named in `boss.yml` exists in the model / `sounds/`, and nothing extra.
- Mechanics: every `minion` of a summon and every non-vanilla wave mob has its own `kind: minion` spec;
  `protect: true` has a shield animation and an immune sound; `kind: heal` has `interrupt.damage` and
  `cap: phase`; a `goto_phase` names a later phase; `max_alive` is set on every wave; music only within
  the budget of plan §4.3.
- Mandatory mechanics (mini-boss and final boss): at least one side wave or protector summon; every
  `protect: true` has `protect_timeout_ticks` (≤ 2400); at least one mutation whose `hp_below` is ≤ 0.40
  and falls in the last or second-to-last phase, with `hide_bones` or `show_bones` and a fight change.
- Animation length = `windup + active + recovery` for each move (± 1 tick).
- Model: bone names, cube count ≤ budget, cubes on the 1/16 grid, texture size, palette only (± 0 colours
  outside `style.md`), hitbox = `size`.
- Sounds: `.ogg`, mono/stereo as required, loudness in range, a `LICENSES.md` line each.
- Output: table of checks PASS/FAIL with numbers → `reports/<step>-<n>.md`.

## 6. Rules
- **Gates are the user's**: never skip ★ to save time. **Step 1 never starts before the user's refs are
  in `refs/`** (unless the user says to start without them).
- **At most 3 fix iterations per step**, then stop and ask with what is still wrong.
- **One boss at a time, one dungeon first** (pilot: Fungal Root), then scale to 3 mini-bosses + 1 boss
  per dungeon type.
- No AI 3D-mesh generators (cubes only). No image AI for the concept sheet or textures (palette-exact
  pixel art by script). AI only for sounds (OQ 103).
- Agents do not commit, push or open PRs: the main session does it after the gate.
- Report at the end of each step: iteration, files written, validator verdict, what the user should
  look at, open choices.
