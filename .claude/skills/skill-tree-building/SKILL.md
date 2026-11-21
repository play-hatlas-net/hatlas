---
name: skill-tree-building
description: Builds the Hatlas job skill trees (Miner, Lumberjack, Hunter, Farmer, Alchemist) from files: effect catalogue → rules sheet → combo matrix → one tree per job in job-skills.yml → validator → user review per job. Holds every tree rule decided in rounds 19–27 (exclusive roots, node counts, rune forks, secondary pool, cooldown tiers, uptime cap, shield timeout, crit/vampire/regen/health/crit guard/anti-regen, counters, effect display). Use when designing, writing, changing, checking or explaining a skill tree or a skill node, or when asked how trees are made.
---

# Building a Hatlas skill tree

> **Status: process defined 2026-11-21 (round 27); rules confirmed round 28 (OQ 137–141).** No tree is written yet.
> - Sources: [`docs/job-skills.md`](../../../docs/job-skills.md) §3 (shape, roles, method §3.6), [`docs/runes.md`](../../../docs/runes.md) (runes, effects, counters) and [`docs/builds-and-stats.md`](../../../docs/builds-and-stats.md) (roots, stats, cooldowns, display).
> - Rules marked *(OQ n)* are proposals still waiting for the user. Use the proposed value, and flag it in the step report.
> - `scripts/job-skills/validate.py` is written at step 5 of the first job (Miner).

Trees are **made from files, not from chat**. Each step reads the files of the previous steps and writes its own, so a step can be re-run and checked by someone who did not make it. **No tree goes into code before the user approves it** (step 6).

## 1. Sources of truth (never contradict them; if a rule cannot be met, stop and report)
1. `docs/job-skills.md` §3:
   - roles: Miner + Lumberjack = tanks, Farmer + Alchemist = healers, Hunter = the only damage job;
   - role flavours, combo kinds, method.
2. `docs/runes.md`:
   - runes per job (OQ 106);
   - effect catalogue with opposites and counters (§4);
   - combat rules (§6, without diminishing returns);
   - rune power and resistance, Summoner, souls.
3. `docs/builds-and-stats.md`: roots and stats (§2, §4), cooldown tiers (§3), damage order (§4.6), round 27 rules (§10).
4. The files this skill writes (§2). Once approved, they win over chat.

## 2. Files (the contract between steps)
```
docs/job-skills-effects.md     step 1: effect primitives (what the code can do), Paper implementation, PvP risk
docs/job-skills-rules.md       step 2: budget, costs, caps, cooldown tiers, uptime and healing limits
docs/job-skills-combos.md      step 3: 5 × 5 combo matrix + counter map
src/main/resources/job-skills.yml   step 4: every tree as data (also read by hatlas-common later)
docs/trees/<job>.md            step 4: readable table + ASCII tree per job (generated from the yml)
scripts/job-skills/validate.py step 5: refuses broken trees; prints the strongest 50-point build per root
scripts/job-skills/reports/<job>-<n>.md   validator output per iteration
```

## 3. The tree rules (rounds 19–27)

### 3.1 Shape
- **Start node → 2 exclusive roots** (more only after the beta). Each root is a **primary specialisation**. The first point spent picks the root and locks the other one.

  | Role | Root A | Root B |
  |---|---|---|
  | Hunter (damage) | **Crit** | **Vampire** |
  | Tanks (Miner, Lumberjack) | **Regen**: holds absorption, the Miner eats stone, the Lumberjack eats sap | **Big health** |
  | Healers (Farmer, Alchemist) | **Mender** (heals) | **Warder** (shields) |

- **Both jobs of a pair share the root names, never the nodes.**
  - Tanks: the Miner is the wall that takes the hits; the Lumberjack is the bodyguard (damage share, taunt, snares).
  - Healers: the Farmer is slow sustain; the Alchemist is burst and the Wizard.
- **Node counts per root (minimum 30, ✔ user):**
  - 12 primary dedicated nodes, including ≥ 2 combo nodes with other roles and 1 capstone;
  - 6 rune fork nodes (3 forks × 2 sides, one rune per side);
  - 12 **secondary pool** nodes, the **same set in both roots**, (✔ OQ 141: the pool counts **inside** the 30).
  - So a tree has ≥ 60 node slots and ≥ 48 different nodes.
- **Secondary pool** (independent of the root):
  - crit guard (tanks only, several nodes, ✔);
  - tenacity (tanks);
  - anti-regen (healers, ✔);
  - the former utility branches (Miner *Forge* with **Forger** ✔ and *Siege*; Lumberjack *Carpenter*; Hunter *Tracker*; Farmer *Ranch*; Alchemist *Brewer* / *Arcane*).
- **Rune forks sit inside each root.** The root sets the style, the rune sets the element.
- **Bridge nodes:** max 2 per tree, cost ≥ 3. Each needs one rune side + 3 secondary nodes (taken as accepted with OQ 141, round 28) and unlocks a weaker skill of a rune the job does not have.
- **Choices are permanent.**
  - The Wizard can remove an end node.
  - **Changing root resets the whole tree** (✔ OQ 136).

### 3.2 Points and costs
- 1 point per job level, max level 50 → **50 points**.
- Costs: 1 = small stat, 2 = combo or conditional power, 3–5 = capstone or bridge.
- One root with one side of each fork costs **75–85 points**, so ≈ 60 % of a root is reachable (✔ OQ 141). The validator refuses less than 50 % or more than 70 %.

### 3.3 Stats and caps (PvP / PvE, all in `job-skills.yml > caps`)

| Stat | Root | Cap | Notes |
|---|---|---|---|
| Crit chance | Hunter Crit | 40 % | random roll on any hit |
| Crit damage `M` | Hunter Crit | ×1.8 (start ×1.5) | also boosts the vanilla **jump crit** to ×M (✔). Jump + random crit on one hit = ×(M + 0.5), cap ×2.3 (✔) |
| Vampire | Hunter Vampire | 10 % / 18 % | from final damage |
| Regen | tank Regen | 0.5 heart/s out of combat, half in combat | job food has a 10 s cooldown; the overflow fills absorption, cap 3 / 5 hearts, decay 0.5/5 s (✔) |
| Max health | tank Big health | +5 / +8 hearts | `max_health` attribute |
| Crit guard | tank pool | −50 % of the crit bonus (−10 %/node) | ✔ named *Crit guard* |
| Tenacity | tank pool | −30 % control time, never < 0.5 s | |
| Anti-regen | healer pool | −40 % healing for 4 s, cap −60 % | hits regen, vampire, heals and absorption refill |
| Healing received from players (PvP) | — | 4 hearts per 10 s (✔) | heals reduced while combat-tagged |
| Healer and tank damage | — | never reaches the Hunter's | |

**Rune damage never crits and never leeches.**

Damage order (`builds-and-stats.md` §4.6):
1. base;
2. hit zone;
3. crit;
4. rune wheel;
5. armour / rune resistance;
6. crit guard;
7. damage cap;
8. vampire;
9. anti-regen.

### 3.4 Active skills, cooldowns and effects
- Every active node has an **impact tier**. Cooldowns are **halved** (✔ round 27). PvP ranges, with PvE in brackets:
  1. light: 2.5–4 s (2–3 s);
  2. sustain: 6–10 s (5–7.5 s);
  3. soft control / zone: 7.5–12.5 s (6–9 s);
  4. **hard control: 15–22.5 s** (10–15 s);
  5. team / big: 30–60 s (22.5–45 s).

  A control-blocking shield is tier 5.
- **Uptime cap:** a self or ally buff lasts ≤ 50 % of its cooldown (✔).
- **Shields always time out:** `absorb`, `duration`, `blocks` (✔ round 27). Defaults:
  - plain shield: 2 hearts, 4 s;
  - *Burning shield*: 1.5 hearts, 3 s;
  - control-blocking shield: 1 heart + the first stun/root, 3 s.

  Shields never stack (the strongest stays).
- **Stuns always work.** No diminishing returns. A **1 s stun guard** follows a hard control: a cast during it is refused and its cooldown is kept (✔ OQ 128). Stun lasts 1 s in PvP and 2 s in PvE.
- No stacking of the same effect (the strongest applies). Zones are telegraphed 0.5 s before they act. PvP values are lower than PvE values.
- **No cooldown-reduction stat** at launch.
- **Every effect is visible** (✔). A node must name its display:
  - `icon` (glyph in the font `hatlas:effects`);
  - `particles` (shape + rune colour);
  - for shields, `bubble`;
  - `glow` only for the stun guard (white) and marks (red).
- Every effect of a node must exist in the **effect catalogue** with its **opposite** and its **counter** (`runes.md` §4). No effect outside the catalogue; add the primitive at step 1 first.

### 3.5 Combos and counters
- Combo kinds (`job-skills.md` §3.5): craft, presence, setup → payoff, item → buff. Each root has ≥ 2 combo nodes, and every combo is written **on both sides** (`links`).
- Combo items are usable by **anyone with the required node, any faction**.
- **Keen weapons** (✔): Hunter crit swords forged by *Masterwork* lose 2 durability per crit and cannot take Mending. **Forger** (Miner secondary pool) repairs them in 3 s with iron and adds *Honed* (+5 % crit chance for 10 min, under the cap).
- **Counter map:** every root must have a counter in **another job's** tree.
  - crit → crit guard, Warder;
  - vampire → anti-regen;
  - regen → anti-regen, crit burst;
  - big health → *Giant slayer* (% max health);
  - Mender → anti-regen;
  - Warder → shield breaker.

  A full faction (one per job) cannot stack two counters against the same root.

## 4. Steps (one job at a time from step 4; order: steps 1–3 for all jobs, then **Miner + Hunter**, then Lumberjack, Farmer, Alchemist)
1. **Effect catalogue** → `docs/job-skills-effects.md`.
   - One row per primitive: id, what it does, Paper implementation, PvP risk, opposite, counter, display.
   - Includes `crit`, `jump_crit_boost`, `vampire`, `regen`, `absorption_overflow`, `max_health`, `crit_guard`, `tenacity`, `anti_regen`, `shield{absorb,duration,blocks}`, `stun_guard`, `durability_cost`, `repair`, plus the runes §4 catalogue.
   - Check each implementation against the Paper 1.21.11 API (`papermc-docs` MCP), for example the `consumable` component for edible stone, `setVisualFire`, `TextDisplay` passengers.
2. **Rules sheet** → `docs/job-skills-rules.md` + `job-skills.yml > caps, cooldowns`: the numbers of §3.2–3.4. User gate.
3. **Combo matrix** → `docs/job-skills-combos.md`: a 5 × 5 table of combos plus the counter map of §3.5. No job may only give. User gate.
4. **Tree as data** → `job-skills.yml > trees.<job>` and `docs/trees/<job>.md`. Node format:
   ```yaml
   miner.regen.stone_eater:
     name: Stone eater
     root: regen            # regen|big_health|crit|vampire|mender|warder|pool|start
     kind: primary          # primary|rune_fork|pool|bridge|capstone
     fork: null             # fork group id for rune forks (one side only)
     rune: null             # fire|frost|storm|nature for rune nodes
     cost: 2
     requires: [miner.regen]
     context: [any]         # any|pvp|pve|dungeon|city_event|mining
     active: null           # or {tier: 2, cooldown_pvp: 8, cooldown_pve: 6, duration: 3}
     primitives: [{regen: {source: eat, items: [cobblestone, deepslate, tuff], seconds: 6}}]
     pvp: {regen_per_s: 0.25}
     pve: {regen_per_s: 0.5}
     display: {icon: regen, particles: {shape: rise, colour: nature}}
     links: []              # combo partners (node ids of other jobs), listed on both sides
     counters: [anti_regen] # catalogue effects that answer this node
   ```
   - Names are short and in-world (no "+5 % stat II").
   - Pool nodes are written once under `root: pool` and reachable from both roots.
5. **Validator** → `python scripts/job-skills/validate.py <job>` writes `reports/<job>-<n>.md` and must PASS. It checks:
   - **shape:** one start node, exactly 2 roots, no cycle, fork groups have ≥ 2 sides, pool nodes are reachable from both roots, ≤ 2 bridges;
   - **counts:** ≥ 30 per root, 12 primary (≥ 2 combos, 1 capstone), 6 rune fork nodes in 3 forks, 12 pool;
   - **budget:** one root + one side per fork = 75–85 points, 50–70 % reachable at 50 points;
   - **numbers:**
     - every PvP and PvE value ≤ its cap;
     - cooldown inside its tier range;
     - buff `duration ≤ 0.5 × cooldown`;
     - every shield has `duration`;
     - stun ≤ 1 s PvP;
   - **references:**
     - every primitive exists in the catalogue;
     - every link exists in the other job's tree and points back;
     - every node with an effect has `display` and ≥ 1 `counter`;
     - crit guard and tenacity only in tank pools, anti-regen only in healer pools;
   - **roles:**
     - healer or tank damage stays under the Hunter's;
     - the two jobs of a pair share no node id or identical primitive set;
   - **output:** the strongest 50-point build of each root, with its damage, effective health and healing per 10 s, for a manual read.
6. **User review** (gate): show the readable table, the ASCII tree and the validator's strongest builds. The user approves or asks changes; change the yml and re-run step 5. Max 3 iterations per job unless the user says more. Then re-check the combo matrix and move to the next job.

## 5. Writing rules
- **No node the code cannot do:** if a node needs a new primitive, add it at step 1 and say so in the report.
- Every number lives in yml. Docs show the number and the yml key.
- Keep PvE generous and PvP tight: the boss damage cap and PvP caps apply after the multipliers.
- Never copy skills, names or icons from existing games. Research (LoL, MTG) gives mechanics, not content.
- Each step ends with a short report (what was written, what failed, open points) and an entry in `docs/claude-changelog.md`.
