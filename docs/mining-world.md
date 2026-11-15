# The mining world (plan, 2026-11-13, updated round 21 2026-11-16)

> **Status: plan only, nothing built.** Source: user, round 20 (2026-11-13, answer to Open Question 68) and
> round 21 (2026-11-16, answers to OQ 78–84 + cave generation request).
> Replaces the ore zones of the faction server. Linked plans: [`cities-and-dungeons.md`](cities-and-dungeons.md)
> (proxy, city rewards), [`cross-server-items.md`](cross-server-items.md) (handoff, travel bag),
> [`economy-observatory.md`](economy-observatory.md) (ruby supply), [`job-skills.md`](job-skills.md),
> map brief [`../worldgen/map.md`](../worldgen/map.md).
> Open questions in §10, mirrored in `CLAUDE.md`. Nothing here is decided until it is marked ✔.

---

## 0. Summary

| Topic | Status |
|---|---|
| **Ore zones leave the faction server.** All ore-zone mining (vanilla ores + ruby) moves to a **dedicated mining server** with its own map | ✔ user, round 20 |
| Own plugin (`hatlas-mining`, proposed), not in `hatlas` | ✔ user ("another plugin"), name proposed |
| Enter by talking to an **entrance NPC**, **no key** | ✔ user |
| Items travel by the **handoff** (moved, never copied); what travels: [`cross-server-items.md`](cross-server-items.md) (travel bag, OQ 98) | ✔ user (round 21: avoid duplication) |
| **No PvP, PvE yes** | ✔ user (rounds 20, 21) |
| **A new map every day** at **06:00 Europe/Paris**, mine **closed 5 min** during the swap | ✔ user, round 21 (replaces "same map, ores regrown") |
| Map = a **closed "potato"** of 2,000 × 2,000 blocks: no surface, **unbreakable limit all around**, cheese + spaghetti + noodle caves, **bigger cheese caves**, cave **structures** (forest hollow, farming village, alchemist ruins, vanilla structures) | ✔ user, round 21 |
| Ores: vanilla + **ruby** + future custom ores; **daily variation up to +30 %**; **+30 % of all ores inside structure caves**; all in yml | ✔ user, round 21 (variation reading: OQ 95) |
| **No nether portals** (mining and dungeon servers) | ✔ user, round 21 |
| **Several entrances** on the faction map; **each city has one**; **holder-only entrance** per city to a **sealed cave with +70 % ruby** | ✔ user (round 20) |
| **3 wild entrances** at the free event sites, each to its own landing at the **most opposite points** of the map | ✔ user, round 21 |
| The **amethyst cave** of the faction map becomes an **entrance to an amethyst region** of the mining world | ✔ user, round 21 |
| Warnings **−60, −30, −15, −5 min** before the reset; everyone is **sent back with what they carry** | ✔ user (round 20) |
| **Miner quests** counted in the mining world, like every job quest | ✔ user, round 21 |
| Faction island keeps **vanilla ores** | ✔ user, round 21 |
| **Low ruby weights at launch**; optional **daily ruby cap per player** (anti-cheat), **off by default** in yml | ✔ user, round 21 |
| Beta test after this epic | ✔ user (beta after each epic) |

---

## 1. The loop

```
 FACTION SERVER                                     MINING SERVER (PvE, no PvP, new map every day)
 ┌───────────────────────────────┐                  ┌───────────────────────────────────────────┐
 │ City: public entrance ────────┼─── handoff ─────►│ landing "city-<id>" ── caves ── falls ── … │
 │ City: holder-only entrance ───┼─── handoff ─────►│ landing "city-<id>-holder" (sealed cave,  │
 │ Wild entrances ×3 ────────────┼─── handoff ─────►│   ruby × 1.7)   landings "wild-1..3"      │
 │ Amethyst cave entrance ───────┼─── handoff ─────►│ landing "amethyst" (amethyst region)      │
 │                               │◄── exit NPC / reset kick ── hotbar + armour + travel bag ─┤
 └───────────────────────────────┘                  └───────────────────────────────────────────┘
          04:45 generator container builds tomorrow's map ──► 06:00 swap (5 min closed)
```

---

## 2. Challenges (rounds 20–21)

**M1. "Inventory copied" must mean *moved*** (round 20; round 21 user question on duplication). Answered in
full in [`cross-server-items.md`](cross-server-items.md): one owner at a time (compare-and-set row), the
target never trusts its vanilla player file, ender chest/containers/drops off, crash = restore the last save
(lose ≤ 1 min, never gain), and a daily duplicate scan of unique item ids. The travel bag (OQ 98) limits
what comes back.

**M2. Rubies created on another server and the ledger** (unchanged): `MINE` rows are kept in the handoff
row (`pending_ledger`) and written to `ruby_ledger` by the faction server in the same transaction that
restores the items. One ledger for the whole network ([`economy-observatory.md`](economy-observatory.md)).

**M3. Rubies may enter** (unchanged): factionless players only have their inventory. Drop disabled, no
containers.

**M4'. A new map every day (round 21, replaces the "pristine copy").** The user wants a fresh, different
cave network each day. Generating 2,000 × 2,000 blocks (≈ 15,600 chunks) takes time, and the speed on our
CPU is **unknown until measured**: published pre-generator figures range from ~30 to ~200 chunks per second
depending on hardware and settings ([Chunksmith], [Chunker]), i.e. **between ~1.5 and ~9 minutes** without
structures and our own passes. That does not fit safely in a 5-minute window on the live server.
**Proposal: build tomorrow's map ahead of time.**
1. At **04:45** (after the 04:30 backup, outside play hours), a **short-lived generator container**
   (same Paper + `hatlas-mining` in `generator` mode + our datapack) starts with a new seed and pre-generates
   the whole map with Chunky, runs our passes (§7.5), pastes the landing halls, checks it (§7.6) and stops.
   Result: a ready world folder `mine-next/`.
2. At **06:00** the mining server sends everyone back, stops, swaps `mine-next/` in, starts. The **5 minutes**
   (✔ user) are a safe margin for a ~1–2 min swap.
3. If generation failed or the checks failed: **yesterday's map is kept** (reset of the ore pass only is not
   possible on a used map, so the mine reopens as it is) and admins get an alert. A broken map never
   goes live.

**M5. The bonus cave must stay closed** (unchanged idea, new map each day): the holder caves are **fixed
regions** of the map that the generator always carves the same way (or pastes from a structure), with a
**bedrock shell** around them and only their landing inside. The entrance checks the holder **at entry**.

**M6. +70 % ruby** = ruby weight × 1.7 in the holder regions (yml).

**M7. Ruby supply.** One open mine for everybody, reset daily, makes many rubies. Levers: **low ruby
weights at launch** (✔), the daily variation capped at +30 %, the **travel bag size** (what can be carried
back per trip, OQ 98), the **daily ruby cap per player** (✔ off by default, for cheating cases), and the
observatory's alerts ([`economy-observatory.md`](economy-observatory.md)).

**M8. Custom ore blocks at scale.** A ruby ore is a note block with a special state. On a map rebuilt every
day there is **no need to track ruby ore positions**: the block state itself says "ruby ore", and nothing is
written to the `BLOCKS` domain. Anti-xray (Paper engine-mode 2) hides the note block too.

**M9. Job quests** ✔: break counters travel in the handoff row (and every minute by outbox for long visits);
the faction server applies them to quests. Same for every job action done there (e.g. Hunter kills of cave
mobs), not only the Miner.

**M10. A fourth game server + a nightly generator.** Hub + faction + dungeon + mining on one machine; the
generator runs only at night (04:45, no players). Mining heap ~3 GB, view distance 6, simulation 4, mob
spawning capped per world, 40-bot load test across all servers. **No new chunks at runtime**: the world
border sits on the map edge.

**M11. The faction world loses its ore zones** (✔): `orezone/` removed from `hatlas`; the island keeps its
vanilla ores (✔). The **amethyst cave** stays on the island map as a place (and event site), and now holds
the **entrance to the amethyst region** of the mining world (✔ user, round 21). Its future "custom crystal
item and shard" (`worldgen/map.md` §3.3) moves to that region: crystals regrow by themselves every day.

**M12. No nether portals (round 21).** Obsidian frames can be built in the mining world (blocks may be
placed). Proposal: `allow-nether=false` and `allow-end: false` on the mining and dungeon servers (no Nether
or End world at all), plus `PortalCreateEvent` cancelled as a second lock. Ender pearls work but cannot
cross the bedrock shell or the world border. (Dungeons: blocks cannot be changed there anyway.)

**M13. Structures with villagers (round 21).** A farming village in a cave brings **villagers**, and
villager trading would be a second economy beside rubies (emeralds, mending books, cheap food), plus iron
golems to farm. Proposal: structure pieces **without villagers and golems** (or villagers that do not trade:
no profession, `setAI(false)` decoration). Same for wandering traders: no spawn. Loot chests in structures
use **our loot tables** (no rubies in chests, so `MINE` stays the only source).

**M14. Landings on random terrain.** Each day's terrain is new, but landings must be in the same place (the
entrance NPCs point to them). The generator **carves a hall** (sphere/room) at each fixed landing position
and pastes the landing build (`.nbt`: floor, light, exit NPC spot), then **guarantees a path** from each
landing to the main network (§7.4).

---

## 3. Rules inside the mining world

| Rule | Plan |
|---|---|
| PvP | **off** (✔) |
| PvE | **on** (✔): vanilla cave mobs, spawning capped by config |
| Blocks | break (ruby: iron+ pickaxe) and **place** (ladders, torches, pillars) — wiped by tomorrow's map (OQ 94) |
| Death | proposal: **keep inventory**, respawn at the landing used (OQ 94, not answered yet) |
| Fall damage | on; big falls end in water pools (OQ 94) |
| Limit | **bedrock shell** all around the potato + world border; no surface (✔) |
| Portals | **none** (✔, M12) |
| Drop key | disabled; containers refused; ender chest off |
| AFK | sent back after 10 min (config) |
| Combat | entering refused while combat-tagged on the faction server |
| Factionless players | may enter (✔); travel bag of 4 slots (OQ 99) |

## 4. Entrances and landings

- **Entrance** (faction server): an NPC in a small protected area; `id`, landing, `holder_only_city`.
  Admin: `/mine entrance create <id> <landing> [holder-of <city>]`, `remove`, `list`.
- **Landing** (mining server): a **fixed position** in map coordinates + an exit NPC. Admin: `/mine landing
  set <id>` (stored in the database); the generator carves and builds it every day (M14).
- **Exit:** exit NPC or `/mine leave` → back **to the entrance used**.
- Per city: one public entrance + one holder entrance. **Wild entrances (✔ round 21): 3**, at the summit
  lake, the cherry top and the dark forest heart (not in safe zones), **each to its own landing**. Amethyst
  cave: one entrance to the amethyst region.
- **Landing layout (proposal):** the landings sit on a **ring** inside the potato. The 3 wild landings are
  spread **120° apart near the edge** (the most opposite points); city landings between them; holder caves
  and the amethyst region in their own sectors. So a player choosing an entrance chooses a part of the map.
- **`/mine doctor`** (same idea as `/dungeon doctor`): every landing set and inside the potato, every
  entrance linked to a landing, holder regions sealed (shell continuity), `ores.yml` and `generation.yml`
  valid, `mine-next/` ready or the last generation's report, reset schedule.

## 5. Daily reset

1. `mining.yml > reset.time: "06:00"`, zone `Europe/Paris` (✔); `reset.closed_minutes: 5` (✔).
2. Warnings `reset.warn_minutes: [60, 30, 15, 5]` (✔) in chat + title, and on the entrance NPCs.
3. 04:45: generator container builds `mine-next/` (M4').
4. 06:00: entrances close, everyone sent back with what they carry (✔), world swap, entrances open. The
   entrance NPCs show **today's ore bonus** ("rich veins today: +18 %").

## 6. Code and data

| Piece | Where |
|---|---|
| Handoff, stash, travel bag, pending ledger, outbox, proxy transfer | `hatlas-common` ([`cross-server-items.md`](cross-server-items.md)) |
| Ruby item + note-block custom block + ledger writer | `hatlas-common` (today in `hatlas`) |
| Entrances, entrance NPCs, holder check | `hatlas` (faction server) |
| Landings, exit NPCs, rules, AFK, reset, warnings, **generator mode** (passes, checks), `/mine doctor` | **`hatlas-mining`** |
| **Datapack `hatlas-mine`** (dimension type, noise settings, density functions, cave biomes, structures) | `hatlas-mining/datapack/`, versioned |
| `generation.yml` (shape, cave sizes, structure chances), `ores.yml` (weights per region, daily variation, structure bonus), `mining.yml` (reset, warnings, AFK, mobs, caps) | `hatlas-mining` |
| Removed: `orezone/`, `orezones.yml`, OREZONES domain, `/orezone` | `hatlas` |

---

## 7. Cave generation (round 21: research and design)

User request: a new map each day "using noise density to connect caves, bigger cheese caves, spaghetti and
noodle caves, terraformed terrain, new ores, rubies"; structures inside caves (a large pillar cave with a
wooden forest, a village with farming or alchemists, any vanilla structure); "do research on existing
algorithms on the web or in mods and reverse engineer open-source repos to create our own".

### 7.1 What exists

| Approach | How it works | Use for us |
|---|---|---|
| **Vanilla 1.18+ noise caves** ([wiki: Caves]) | a 3D **density function**: each block gets a value, above 0 = stone, below = air. **Cheese** = a low-frequency noise cut at a threshold (big rooms with pillars); **spaghetti** = the thin band where a noise is close to 0 (long tunnels); **noodles** = thinner, toggled tunnels; **noise pillars** inside cheese rooms. All tunable (frequency, hollowness, thickness) | **the base.** Everything is data in a datapack (`worldgen/noise_settings`, `density_function`), no Java generator to maintain |
| **Carvers / Perlin worms** (pre-1.18 caves, ravines) | a "worm" walks through the volume and carves a tube | to **guarantee links** between landings and big rooms (noise alone does not guarantee connectivity) |
| **Cellular / Worley noise** (e.g. Worlium, YUNG's Better Caves style caverns) | distance-to-nearest-point noise gives cell-shaped caverns and walls | optional extra cave style ("cell caverns") |
| **Cellular automata** ([RogueBasin], [gridbugs]) | random fill + smoothing rules → organic cave shapes | good in 2D games; in 3D at our scale too slow and hard to control: **not used** |
| **Terra** (PolyhedralDev; API MIT, core MIT/GPL-3; [Terra]) and its underground pack **Substratum** (GPL-3; [Substratum]) | a full generator plugin with config packs; Substratum makes a completely underground world | **study only.** A whole extra generator to run and update for each Minecraft version; its pack is GPL-3 |
| **YUNG's Better Caves** (LGPL-3.0, [Better Caves]) | mod with cavern/lake/flooded variants | **ideas only** (it is a mod, not a Paper plugin) |

**Licence rule for "reverse engineering":** we **read** these projects to learn the techniques and the
parameters that look good, then **write our own** datapack and passes. We do **not copy code or config
files** from GPL/LGPL projects into ours (it would put our plugin under their licence terms). Mojang's own
worldgen JSON (exported from the server jar with the data generator) is the standard reference for writing
datapacks and is what we start from.

### 7.2 Choice: datapack noise + our own passes (recommended)

**Not a Java chunk generator from scratch** (slow to write, must be redone at each Minecraft version) and
**not Terra** (extra plugin, licence, upgrades). Instead:

1. **Datapack `hatlas-mine`** with a custom **dimension type**: `has_skylight: false`, `has_ceiling: true`
   (cheaper lighting, no sky anywhere), `bed_works` irrelevant (beds refused by the plugin), height
   **y −64 to 256**.
2. **Noise settings** with our own `final_density`, built from vanilla density-function types (`noise`,
   `add`, `mul`, `min`, `max`, `abs`, `range_choice`, `y_clamped_gradient`, `interpolated`, `cache_2d`…).
3. **Our own passes in `hatlas-mining`** (Paper `ChunkGenerator` that keeps vanilla noise, caves,
   decorations and structures, plus `BlockPopulator`s): ores, the shell, landings, connectivity.

### 7.3 The shape: a "potato geode"

```
final_density = min( potato(x,y,z) , caves(x,y,z) )      (solid where > 0)

potato   = 1 − ellipsoid_distance(x/1000, (y−96)/150, z/1000) + 0.15 × low_noise(x,y,z)
           → solid inside, the edge wobbles by ±~80 blocks (not a perfect egg)
outside  = air (cheaper region files, nobody can get there)
shell    = the plugin turns a 3-block band at the potato edge into bedrock (unbreakable, vanilla)
caves    = max( cheese, spaghetti, noodles, cell_caverns )   with weights per depth layer
```
- **Bigger cheese caves** (✔ user): lower frequency and higher hollowness than vanilla, scaled up in the
  middle layers (giant halls), smaller near the bottom.
- **Spaghetti and noodles**: vanilla-like, slightly wider spaghetti so players can follow them.
- **Pillars**: vanilla noise pillars in the big halls ("large pillar cave").
- **Depth layers** (themes): top = stone and dripstone; middle = giant halls (forest hollow, villages);
  deep = deepslate, lava lakes, deep-dark-like rooms; one sector = **amethyst region** (geodes at high
  frequency, future custom crystal); holder sectors = sealed caves.
- **Falls**: tall shafts where cheese rooms stack; big falls end in water (✔ round 20 plan, OQ 94).

### 7.4 Connectivity (the part noise cannot do)

Noise caves are beautiful but **not guaranteed connected**: a landing can end in a closed pocket. Our pass:
1. Sample the map on a coarse grid (4 × 4 × 4 cells: air or not) and **flood-fill** to find connected
   cave networks and their volume.
2. Build a graph: landings + the 20–40 largest rooms. Compute a **minimum spanning tree** (+ a few extra
   edges so there are loops).
3. **Carve worm tunnels** (Perlin-worm style, 3–5 blocks wide, gentle slopes, ladders on steep parts) along
   the edges that are not already connected.
4. Check again: **every landing reaches the main network**, the holder regions reach **only** their landing.

### 7.5 Structures in caves

| Structure | How | Notes |
|---|---|---|
| **Forest hollow** (large pillar cave with a wooden forest) | a custom **cave biome** where trees grow on the cave floor (placed features with the `environment_scan` modifier, the way vanilla lush caves place moss and azaleas), moss/grass floor, glow lichen light | pure datapack |
| **Farming village / alchemist ruins / dwarven halls** | our own **jigsaw structures** with a fixed `start_height` in the middle layers, `terrain_adaptation: beard_box` or `encapsulate` (the structure clears its own room, like ancient cities and trial chambers), pieces with **rigid projection**; they can **reference vanilla village pieces by id** (no Mojang files copied) or our `.nbt` builds | villagers/golems removed (M13) |
| **Vanilla structures that work underground** | mineshafts, monster rooms, geodes, ancient cities, trial chambers: enabled by structure sets in the datapack | trial chambers: their vaults and keys must not clash with our key items (check) |
| Vanilla structures that need a surface | villages, mansions, temples | not usable as-is (they snap to the surface); hence our own versions above |

**Ores in structure caves: +30 % of all ores** by default (✔ user), `ores.yml > structure_bonus: 0.30`: the
ore pass reads the structure bounding boxes of the chunk (Paper exposes generated structures) and applies
the multiplier there.

### 7.6 Ores and the daily variation

- Vanilla ore features are **turned off** in the datapack; **our ore pass places every ore** (vanilla +
  ruby + future custom ores) from `ores.yml`: weight per ore, per depth layer, per region (holder × 1.7 for
  ruby, structures +30 %), vein size.
- **Daily variation** (✔ user: "up to 30 % more max"): each day a factor between **1.00 and 1.30** is drawn
  (`ores.yml > daily_variation_max: 0.30`) and applied to all ores, shown on the entrance NPCs. Reading to
  confirm in OQ 95 (alternative: each ore gets its own daily factor).
- **Ruby weight low at launch** (✔), tuned during the beta with the observatory.

### 7.7 Checks before a map goes live

The generator writes a report and refuses to publish `mine-next/` if: a landing is not connected, a holder
region is reachable from outside, the shell has a hole, ore counts are outside ±20 % of the expected
amounts, or a structure is missing. Admins get the report (and a few **slice images**: horizontal cuts at
several heights rendered from the region files by `scripts/mining/preview.py`, since a cave world cannot be
seen from above on BlueMap).

### 7.8 How we build it (tooling)

1. Export Mojang's worldgen reports from the server jar (data generator) as the reference.
2. Write the datapack step by step: shape → cheese → spaghetti/noodles → layers → biomes → structures.
3. For each step: generate a small test potato (radius 200) on the test server, render slices, look,
   adjust. Then the full size, **measure generation time on the production machine** (decides if 04:45 is
   early enough).
4. Then the passes (ores, shell, landings, connectivity) and the checks.

This replaces the round 20 idea of building the mining map in the WorldPainter pipeline: a map rebuilt
every day must be generated, not painted.

---

## 8. The map (summary)

**2,000 × 2,000** blocks (✔), y −64 to 256, a closed potato with a bedrock shell, no surface (✔), new every
day, landings on a ring, holder sectors sealed, amethyst sector, cave layers and structures (§7).

## 9. Build order

Epic **mining world** (after the dungeon epic, which builds the handoff; beta at the end, ✔ user):
1. Handoff, stash, travel bag, ruby items/blocks and ledger writer in `hatlas-common`.
2. Datapack prototype (shape + caves) and slice previews; generation time measured.
3. `hatlas-mining`: landings, exit, rules, AFK, reset + warnings, world swap, generator mode.
4. Passes: ores, shell, connectivity, landings; structures; checks; `/mine doctor`.
5. Faction side: entrances + holder check; ore zones removed; quest progress from the mining server.
6. Proxy backend `mining-1`, compose services `mining` + `mining-generator`, load test, **beta**.

## 10. Open questions (mirrored in `CLAUDE.md`)

- 78 ✔ partly: no PvP, PvE on; items moved by the handoff (what travels: OQ 98). **Death rule not
  answered** → OQ 94. 79 ✔ 06:00 Paris, closed 5 min, **new map every day**. 80 ✔ 2,000 × 2,000 potato,
  unbreakable limit, no surface, no nether portals. 81 ✔. 82 ✔ vanilla ores on the island; amethyst cave =
  entrance to an amethyst region. 83 ✔ low ruby weights, daily cap off by default. 84 ✔ 3 wild entrances to
  3 opposite landings.
- **94** Death in the mining world: keep inventory, respawn at the landing (recommended)? Fall damage on with
  water at big falls (recommended)? Block placing allowed (recommended)?
- **95** Generation: tomorrow's map built at 04:45 by a generator container, yesterday's kept if it fails
  (recommended)? Datapack noise + our passes, not Terra or a Java generator (recommended)? Daily ore
  variation = **one factor 1.00–1.30 for all ores** (recommended) or one factor per ore?
- **96** Villages in caves without villagers or golems, structure chests with our loot tables (no rubies)
  (recommended)? Which structures at launch: forest hollow, farming village, alchemist ruins, mineshafts,
  geodes (recommended), + ancient city / trial chambers?
- **97** Landing ring layout: 3 wild landings 120° apart near the edge, city landings between, holder and
  amethyst sectors apart (recommended)? The amethyst region open to everyone (recommended) or a city reward?

[wiki: Caves]: https://minecraft.wiki/w/Caves
[Chunksmith]: https://modrinth.com/mod/chunksmith
[Chunker]: https://modrinth.com/plugin/chunker/changelog
[RogueBasin]: https://chizaruu.github.io/roguebasin/cellular_automata_method_for_generating_random_cave-like_levels
[gridbugs]: https://gridbugs.nfshost.com/cellular-automata-cave-generation/
[Terra]: https://www.github.com/PolyhedralDev/Terra
[Substratum]: https://github.com/DeathShadez/Substratum
[Better Caves]: https://modrinth.com/mod/yungs-better-caves
