---
name: boss-building
description: Builds a Hatlas dungeon boss or mini-boss end to end: references + style guide → boss.yml spec and concept sheet → Blockbench .bbmodel (script-written, user-polished) → animations → AI-generated sounds → behaviour code in hatlas-dungeons → bot fight test, with one agent per step and the user's approval between steps. Use when designing, modelling, animating, sounding, coding or testing a boss, or when asked how the boss pipeline works.
---

# Building a Hatlas boss

> **Status: process defined 2026-11-18 (round 22, `docs/cities-and-dungeons.md` §4.1–4.4), tools not
> built yet.** The scripts named below (`bosses/_tools/`) are **to be written** during the pilot (the
> **Fungal Root**, `dark_forest`) by the agent of the step that first needs them, then reused. Until
> then, follow this file as the plan.

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
    bbmodel.py                    writes/reads .bbmodel JSON (cubes, bones, pivots, texture, keyframes)
    texture.py                    pixel-art texture from a palette + UV layout (Pillow)
    render.mjs / preview.html     three.js preview of a .bbmodel (turntable PNGs, animation GIF/MP4)
    sound.py                      trim, loudnorm, mono/stereo, ogg (ffmpeg), sounds.json entries
  <dungeon>/
    style.md                      style guide of the dungeon (committed, approved)
    <boss>/
      refs/                       user's images + README.md (committed)
      boss.yml                    spec (committed, approved)
      concept/                    concept sheet: front.png, side.png, back.png, palette.png (committed)
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
  folder): write the minion's `boss.yml` and concept sheet in the same step.
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
- Hitbox = `boss.yml > size`, drawn as a `hitbox` bone (BetterModel's convention, checked in the pilot).
- Previews: turntable (8 angles) + front/side next to the concept sheet, so the gate compares them.
- Blockbench MCP (if installed): only to screenshot the model as Blockbench shows it and to apply small
  edits while the user watches; the file stays the source of truth.

### Step 3: `boss-animator`
- One animation per name of `boss.yml > animations`. A move's animation length **equals**
  `windup + active + recovery` ticks (÷ 20 = seconds), with the wind-up pose readable from 10 blocks
  away. Loops: `idle_*`, `walk`, `run`. One-shots: everything else.
- Keyframes on bones only (no scale on the root), easing kept simple; no clipping through the body.
- Previews: one GIF/MP4 per animation from `_tools/render.mjs`.

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
