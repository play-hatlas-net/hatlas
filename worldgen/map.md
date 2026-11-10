# The Hatlas island: map brief (design, 2026-11-10)

> **Status: design brief, not built.** This file is the **source of intent** for every map agent
> (`.claude/skills/map-building/SKILL.md`): it says what the island must feel like, what lies where and
> why. Layouts, heightmaps and worlds are generated **from** it; when they disagree with it, they are
> wrong, or this file is updated first (with the user's approval).
> Research and choices: `docs/map-building.md`. Open points: Open Question 42 in `CLAUDE.md`.

## 1. Frame

| Rule | Value |
|---|---|
| Shape | **one giant island over the void**, no other land |
| Size | world border radius **4,000 blocks** (250 chunks) ✔ user round 14; island ≈ 7.5 km across, its coast a little inside the border |
| Edge | players **can fall into the void and die with their items** ✔; the coast is mostly shore and low cliffs; **sometimes a mountain or rock face runs straight to the edge** (not required everywhere) |
| Under the island | straight rock wall down to y −64 first; a shaped underside later if wanted |
| Height | sea/lake level y 63; land mostly 64–140; main summit ≈ 250–280 (build limit 319) |
| Version | Minecraft / Paper **1.21.11**, vanilla blocks only (resource-pack models for custom items only) |
| Players | ~40, factions: **most of the land must stay buildable** (gentle hills, forests, meadows) |

## 2. Main ambiance: **dwarven**
A land shaped by a people who dig: the city sits at the **foot of the great mountain** and opens into
it; stone roads and **tunnels** link it to the places where things happen; **amethyst and ruby** are
the treasures of the deep. Materials to favour in builds and paths: deepslate, stone bricks,
polished blackstone, copper (oxidised accents), amethyst, dark oak, lanterns and chains, banners.
Rubies (`hatlas:ruby_ore`) appear **only in ore zones** (game rule, `CLAUDE.md` §4.6): the city's
`city_mine`. The amethyst cave (§3.3) is the island's amethyst mine.

## 3. Zones

Positions are **intents** (compass side relative to the centre), refined in `layout.json` by the
designer agent. Share = rough part of the island's land.

### 3.1 The dwarven city (spawn), centre / south of the great mountain, ~4 %
- **The existing spawn city** from the test map, pasted on a **flat plot made for it** (its exact
  footprint measured from the build, + 32-block margin), safe zone `spawn` + `city`.
- Its gates open toward every event site: **stone roads** above ground, and **one dwarven tunnel**
  into the mountain to the amethyst cave.
- Ruby mine `city_mine` (ore zone) stays inside the city as today.

### 3.2 The great snowy mountain, centre / north, **main biome**, ~30 %
- Biomes: `jagged_peaks`, `frozen_peaks`, `snowy_slopes`, `grove` at the foot (spruce).
- **A frozen lake near the summit** (snow lake with a summit above it): a hanging valley, reachable on
  foot, the highest water on the island.
- Rocky shoulders: `stony_peaks`, `windswept_gravelly_hills`. On one side the range **runs to the edge**
  and ends in a cliff over the void.

### 3.3 The mysterious amethyst cave (amethyst mine), inside the great mountain, underground
- A **large natural cavern** lined with amethyst (geode-like walls, budding amethyst, calcite, smooth
  basalt), reached by the dwarven tunnel from the city and by one hidden entrance on the slope.
- Inside: a **strange old house** still standing, and **ruined, destroyed buildings** (collapsed dwarven
  halls, broken pillars, rubble): the remains of a mine that dug too deep.
- ✔ **Crystal mine** (user, rounds 15–16): not ruby ore; the cave will hold **Hatlas's own crystal
  item and shard** (a custom "ruby crystal" and its shard, a future feature like the vanilla amethyst
  cluster/shard). Until it exists the map places vanilla amethyst as a stand-in. To define with the
  feature: whether the shard is ruby currency (then it goes through the ruby ledger as a source, like
  `MINE`), how it grows/regrows, and its link to the amethyst gear.
- Event site (see §5). Made by carving after the export (FAWE/structure), not by WorldPainter.

### 3.4 The cherry mountain, east, ~10 %
- A **big separate mountain** (green, lower than the snowy range) with **hills all around**.
- `cherry_grove` on the hills and high meadows, **bees and bee nests** in the cherry trees (vanilla
  cherry trees can carry nests), `meadow` with flowers between groves.
- Calm, bright, good land for factions who want beauty.

### 3.5 The fjord: port and viking village, north-west coast, ~6 %
- An island over the void has no sea, so the water is a **fjord**: a long deep inlet cut into the
  coast, **closed toward the void by a rock barrier/arch** (water placed at the edge would pour into the
  void). Steep rocky sides, a narrow beach at its end.
- **The port**: docks, a few ships, warehouses, at the inner end of the fjord.
- **The viking village**: longhouses, a mead hall, palisade, on the slope above the port; spruce and
  stripped logs, cobblestone bases.
- Event site (see §5).

### 3.6 The dark forest creek, next to the port, west, ~8 %
- `dark_forest` along a **creek** (narrow stream) that runs down from the hills and **flows into the
  fjord** beside the port.
- At its heart, a small **`pale_garden`** (creakings at night): the darkest place of the island, a fit
  for the `dark_forest` donjon build.

### 3.7 The volcano, south-east among the rocks, ~4 %
- ✔ User (round 15): a **volcano of stone and rock** with a **crater**; the **`desert` donjon** stands in
  the crater (sand/red sand floor, `desert` or `badlands` biome inside the crater, `stony_peaks` /
  `windswept_gravelly_hills` on the cone).
- Surface by masks: basalt, blackstone, tuff, smooth basalt streaks, magma blocks, some cold lava
  (obsidian); **little or no open lava**, and the volcano kept **away from forests** (lava sets nearby
  wood on fire).
- ✔ User (round 16): the **`nether_castle` donjon inside the volcano** (a chamber in the cone, reached
  from the crater or a flank gate).

### 3.8 The oak hills and rocks, south and the rest, ~36 %
- `forest`, `windswept_forest` (small mountains with oak), `meadow`, `plains` patches: the **main faction
  land**, gentle slopes, some flat valleys.
- Scattered rock outcrops (`stony_peaks` islands, gravel hills), small lakes and streams.
- The coast here is mostly a **stony shore** and low cliffs; one stretch where rocks run to the edge.

## 4. Links and travel
- Roads from the city to: the fjord (port + village), the cherry mountain, the dark forest creek; the
  tunnel to the amethyst cave; a mountain path to the summit lake.
- Each road: ≤ 1 block up per 3 blocks along (walkable, horse-friendly), signposts, a dwarven milestone
  every ~250 blocks.
- No point of the island farther than ~4 km from the city by road.

## 5. Event sites (structures where things happen)
| Site | Zone | Notes |
|---|---|---|
| Amethyst cave + old house + ruins | §3.3 | ruby mine, the "mystery" place |
| Viking village | §3.5 | |
| Port | §3.5 | |
| Summit lake | §3.2 | |
| Cherry mountain top | §3.4 | |
| Dark forest heart (pale garden) | §3.6 | `dark_forest` donjon |
| Volcano crater | §3.7 | `desert` donjon |
| Inside the volcano | §3.7 | `nether_castle` donjon |

"Events" are **new gameplay**, described later by the user (✔ round 15, Open Question 44): **a city is
linked to 3 small places** (village, cave, …) where events happen; a faction that completes **more than
50 % of all the events controls the city for a while (e.g. 3 days)**. For the map: the city gets
**exactly 3 linked sites** (proposed: **viking village, amethyst cave, port**), each with a flat plot and
an anchor point; the other places (summit lake, cherry top, dark forest heart) stay free sites for
later. ✔ User (round 16): **the spawn city can be controlled** (it stays a safe zone: the fights happen
at the 3 sites, control only changes who owns/benefits from the city).

**Existing donjon builds** (`src/main/resources/structures/`) to place: `dark_forest` → dark forest heart
(§3.6); `ocean` → the fjord (in or by the water); `sky` → **floating off the void edge**, fits the island
well; `plain` → oak hills; `desert` → the **volcano crater** (§3.7, ✔ user); `nether_castle` → **inside the
volcano** (✔ user).

## 6. What the agents must check (summary; details in the skill)
- Every zone of §3 exists, on its side, with roughly its share.
- City and event plots flat (max 1 block of difference over 4 blocks), not crossed by water.
- Every water body is **closed** (no path from water to the void edge).
- Roads of §4 walkable; the summit lake reachable on foot.
- At least one stretch of rock/mountain runs to the edge; the rest is shore or low cliff.
- Most of the land (§3.8 + §3.4) has gentle slopes for faction bases.
- The volcano is at least ~100 blocks from any forest.
