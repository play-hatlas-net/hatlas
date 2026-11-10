# Building the production map with Claude (research, 2026-11-10)

> **Status: research and plan only** (Open Question 42, round 12). The user asked: can Claude connect to
> a server through an MCP server, learn building styles from maps shared online (e.g. Planet
> Minecraft), design unique buildings and terrain, simulate them in another tool first (like the Figma
> board), then deploy several bots to place the blocks?

## 1. Short answer

- **Yes for "Claude designs, a tool previews, the server builds"**, no for "bots place the blocks".
  Bots placing blocks one by one is the slowest and least reliable way to build: a server pastes a
  whole schematic in seconds (FastAsyncWorldEdit, or vanilla `/place template` for `.nbt`, which this
  project already uses for the donjon gallery). Bots are useful to **look** at the result
  (screenshots, walking through) and to test gameplay, not to lay blocks.
- **Claude does not "learn" from downloaded maps** (no training on them). It can read a few
  **reference builds** placed in its context (block palette, proportions, layer slices, screenshots)
  and imitate a style. The best references are **your own builds** (the spawn city and the 7 donjon
  `.nbt`): same style, no licence issue.
- **Most of #42 is not new buildings.** ✔ Open Question 41: production keeps **the same city and
  donjons, at other places**. The real work is (1) terrain, (2) moving existing builds, (3) the
  production fixtures. AI-generated buildings are an extra, for decoration and later content.

## 2. Options compared

Scores: ★ poor … ★★★ good, for **this** project (Paper 1.21.11, one admin, a fixed city to relocate).

| # | Approach | How Claude acts | Speed for a map | Build quality | Fits Paper 1.21.11 | Setup / risk |
|---|---|---|---|---|---|---|
| A | **Bots place blocks** (Mineflayer: [Mindcraft](https://mindcraft-minecollab.github.io), [yuniko-software minecraft-mcp-server](https://www.getdrio.com/mcp/minecraft-mcp-server-yuniko-software), VitaminMCP bots) | Claude steers one or more players | ★ (hours for one house; reach and pathing limits) | ★ (the Mindcraft paper reports agents undoing each other's work and a drop when they must share detailed plans) | ★★ (protocol-level) | anti-cheat must be off; many agents = many tokens |
| B | **Console commands** (VitaminMCP `command_exec` / RCON: `/fill`, `/setblock`, `/place template`, FAWE `//paste`) | Claude sends commands to the **test** server, already wired in this repo | ★★★ | depends on the plan it pastes | ★★★ | none new; never on production |
| C | **File-first builder MCP**: [minecraft-builder-claude-mcp-server](https://glama.ai/mcp/servers/JesperMorais/minecraft-builder-claude-mcp-server) (MIT) | Claude writes a JSON of shapes (cuboid, sphere, dome…) + blocks → `.schem`/`.litematic`; 3D browser viewer, headless renders so Claude reviews its own work, user notes on the model mapped back to the shape that made it, a build **style guide** tool | ★★★ (paste the file with B) | ★★ (good for structures; organic shapes weaker) | ★★ (targets any version 1.13–26.x; its schematic library's version list stops at 1.21.5: test a 1.21.11 paste) | Python 3.10+, install from GitHub, unmaintained-grade unknown: pilot first |
| D | **GDMC toolkit**: [GDMC HTTP Interface](https://modrinth.com/mod/gdmc-http-interface) mod (1.8.4 for 1.21.11) + [GDPC](https://gdpc.readthedocs.io/en/stable/) Python | Claude writes Python generators that read the terrain and build **settlements adapted to it** (the yearly GDMC competition's goal) | ★★★ | ★★ to ★★★ (procedural, consistent) | ★ directly: it is a **Fabric/Forge mod**, not a Paper plugin → generate on a local modded 1.21.11 copy of the world, then copy the region files to Paper | separate modded instance; strongest for "unique village/roads that follow the land" |
| E | **WorldPainter** (desktop, you drive it) | Claude prepares inputs: heightmap PNGs, biome masks, object sets (`.schem`/`.nbt` custom objects), a written terrain brief | ★★★ (whole world at once) | ★★★ terrain | ★★ (1.21 supported per the community; test object import with a small file first) | your time in a GUI; Claude cannot click in it |
| F | **Custom world generator** (datapack / Terra / Iris) | Claude writes the generator config (noise, biomes, structures) | ★★★ (generated as chunks load, then Chunky) | ★★ | ★★★ (datapack) / ★★ (plugins) | tuning loops; less control over exact spots |

Planning step "like the Figma board": a **FigJam board of the map seen from above** (zones: spawn,
city, ore zones, donjons, wilderness, world border) is the right place to agree on the layout before
any block. 3D preview of single builds: the builder MCP's viewer, or browser viewers such as
[Shulkr](https://www.shulkr.com/en/schem-viewer) (`.schem`, `.litematic`, `.nbt`, files stay local).

## 3. Using maps shared online

- Planet Minecraft has **no site-wide licence for user builds**: each creator sets their own terms on
  the project page. Some allow server use with credit; others explicitly forbid **commercial use**
  and **AI training datasets** ([example terms](https://www.planetminecraft.com/project/prison-mine---basicminej/download/schematic/)).
  Hatlas charges for access, so it is commercial use.
- Rules for this project:
  1. **No scraping.** You pick and download a few builds by hand, and only those whose terms allow
     use on a paid server (or with the creator's written permission, kept in `deploy/game/world/LICENCES.md`).
  2. They are used as **style references** (Claude reads palette, proportions and slices), never pasted
     as-is unless the licence allows it; credit the creator where asked.
  3. Paid packs (mob models, builds) follow the same check (`docs/funding.md`).
- A small script (to write when approved) turns a reference `.schem`/`.nbt` into a text summary
  Claude can read: size, block palette with counts, one slice per few layers.

## 4. Recommended pipeline

1. **Layout** (you + Claude): FigJam board of the production map from above; world size/border.
2. **Terrain**: WorldPainter (E) driven by you from Claude's brief and heightmaps, **or** a datapack
   generator (F) if you prefer generated land. Choose after a 1-hour try of each on a copy.
3. **Existing builds**: export the city and donjons from the test map as `.schem` (FAWE `//copy` +
   `//schem save`) or `.nbt`, paste them at the new places (B) on a copy of the production world on
   the test server; then the production fixtures (`deploy/game/world/fixtures.prod.json`) + the
   generator for safe zones, ore zones, donjon points, NPCs, shops.
4. **New buildings** (optional): Claude designs with the builder MCP (C) using your builds as style
   references → you review in the 3D viewer → paste with B → a VitaminMCP bot (`bot_view`) takes
   screenshots for a second review. For a whole village that follows the land: D on a modded copy.
5. **Pre-generation** (Chunky) and copy of the finished world to production (`docs/deployment.md`).

Tools to add, **test server only** at first: **FastAsyncWorldEdit** (Paper build listed for
1.20.6–1.21.11, check the exact version on Modrinth) and the builder MCP. FAWE is also a normal admin
tool in production; MCP servers and bots never touch production (same rule as VitaminMCP).

## 5. Pilot before choosing (proposed)

One small build, end to end, on the test server: a market stall or a guard tower in the city's style.
- C: Claude designs it from the city's palette, renders, you comment, it fixes, `.schem` out.
- B: pasted with FAWE next to the city; `bot_view` screenshots.
- Measure: your time, number of review rounds, whether it looks like it belongs.
If it is good enough → use C for decoration; if not → keep builds hand-made and use Claude for
terrain inputs, fixtures and pasting only.

## 6. Open points (Open Question 42)
- ✔ Terrain route: **WorldPainter driven by Claude** (`wpscript`), island over the void (round 13).
- ✔ Radius 4,000 blocks; falling into the void allowed (round 14).
- ✔ Brief: **`worldgen/map.md`** (dwarven ambiance, zones, event sites); process and agents:
  **`.claude/skills/map-building/SKILL.md`**; test island: §8 (round 14).
- ✔ Round 15: fjord closed toward the void for the port; `desert` donjon in a **volcano crater**; the
  cave is an **amethyst** mine (not rubies); city control by events = Open Question 44 (later).
- ✔ Round 16: `nether_castle` **inside the volcano**; the **spawn city is controllable**; the cave holds
  a **custom crystal item and shard** (future feature; vanilla amethyst as stand-in on the map);
  `worldgen/template.world` saved by the user (prerequisites complete).
- Run the pilot (§5)? It installs FAWE and the builder MCP on the test server only.
- Builds and NPCs: placed by hand, or by the fixtures generator (recommended: generator, so the
  production setup can be rebuilt).

## 7. The production island (✔ user, round 13) and the plan

**Asked:** one **giant island surrounded by void** (no other land), border radius about **625 chunks**;
terrain made with **WorldPainter driven by Claude**; biomes: **snowy mountains (main)**, rocky areas,
small hills with **oak**, **cherry grove**, **pale garden** (dark); a **2D and 3D render** to iterate;
maybe a **modded server** for villages that follow the terrain; then copy the world to production.

### 7.1 Challenge: the size
625 chunks of radius = **10,000 blocks** → a 20,000 × 20,000 square = **400 km²**, 1.56 million chunks.
- **40 players on 400 km²** is about 10 km² each: factions rarely meet, raids need long trips, the map
  feels empty. Faction servers of this size usually use a radius of **2,500–5,000 blocks**.
- **Disk and backups**: ≈ 15–35 GB of world (4 × the earlier estimate), restic ≈ 30–60 GB on the
  120 GB backup SSD; the BlueMap render and the first backup take hours.
- **WorldPainter** keeps the whole world in memory: a 20k × 20k world needs a lot of RAM on the PC
  that runs it (test first), and the export takes hours.
- What it does **not** cost: server RAM/CPU depends on the chunks **near players**, not the map size.
- ✔ **Decided (user, round 14): radius 4,000 blocks (250 chunks)**, island ≈ 7.5 km across.
  WorldPainter can enlarge a world later (more land at the coast); shrinking is not possible.

### 7.2 Challenge: an island over the void
- The coast ends in a **cliff straight down to the void**: anyone who falls dies and **loses the items**.
  ✔ User (round 14): **accepted as a game rule**; the coast is mostly shore and low cliffs, and
  sometimes rocks or a mountain run straight to the edge (not required everywhere). A line in the wiki.
- Underside: a straight wall down to y −64 is free; a rounded rock "bottom" seen from the edge is
  carved after the export with a FAWE script. Proposed: straight wall first, shaped later if wanted.
- Nether and End: kept vanilla unless you want them closed or limited (to decide later).

### 7.3 How Claude drives WorldPainter (no clicking)
WorldPainter has a **scripting command, `wpscript`** (JavaScript): load a heightmap image, create a
world from it, apply layers, export a Minecraft map
([scripting API](https://www.worldpainter.net/trac/wiki/Scripting/API)). Export settings live in a
`.world` template saved once from the GUI. The loop:

1. **Layout** (you + Claude): a top-view sketch: island outline, where each biome goes, **flat plots
   reserved for the city and each donjon** (so their builds sit on matching ground), ore-zone sites.
2. **Claude generates the heightmap and masks** with Python (16-bit PNG: noise + ridges for the snowy
   range + erosion for realistic valleys; one mask PNG per biome; plots flattened).
3. **Preview before Minecraft** (seconds):
   - **2D**: a colour map (biomes + hillshade + contour lines + plots);
   - **3D**: a mesh of the heightmap in a browser viewer (three.js page) coloured by biome, that you
     rotate. Claude looks at the same images and challenges them (too steep, plot on a slope, biome
     too small…).
4. **`wpscript`** builds the `.world`: heightmap → terrain, biome masks → biomes and surface blocks
   (snow, stone, gravel, grass), tree layers, resources, **void outside the island**; exports a
   Minecraft 1.21.11 world.
5. **Preview in Minecraft form**: **BlueMap CLI** renders the exported folder as a 3D web map without a
   server ([BlueMap](https://bluemap.bluecolored.de/wiki/getting-started/Installation.html)) + a 2D top
   view; screenshots on the test server with a VitaminMCP bot (`bot_view`). Iterate from step 2.
6. Paste the **city and donjons** on their plots, write the fixtures (§4), copy to production.

### 7.4 Biomes (Minecraft 1.21.11 ids)
| Wish | Biomes | Notes |
|---|---|---|
| Snowy mountains (main) | `jagged_peaks`, `frozen_peaks`, `snowy_slopes`, `grove` (spruce at the foot) | the central range |
| Rocks | `stony_peaks`, `windswept_gravelly_hills`, `stony_shore` on the coast | between the range and the hills |
| Small hills with oak | `windswept_forest`, `forest`, `meadow` | gentle ground: good for faction bases |
| Cherry trees | `cherry_grove` | on a high meadow |
| Dark garden | `pale_garden` | **creakings spawn at night** near creaking hearts: a dangerous zone (fits a donjon) |

Not confirmed by the research, checked in the test island: the WorldPainter version supports the
1.21.11 format and the **`cherry_grove` / `pale_garden` ids**; trees: WorldPainter's own tree layers
have no cherry or pale oak, so either **let Minecraft decorate the chunks** (WorldPainter's "populate"
option, vanilla trees per biome) or custom-object layers with tree `.schem` files.

### 7.5 Advice on a separate modded server for villages
- **Not now.** The spawn city and donjons are the settlements; realism comes mostly from the terrain
  (erosion, a coherent order of biomes) and from plots made for those builds.
- **Later, if the island feels empty**: a **local** Fabric 1.21.11 copy (on the PC, never on the
  production machine) with the GDMC HTTP mod; Claude writes GDPC scripts that build small villages and
  roads following the land. Only vanilla blocks, so the folder goes back to Paper as is. One evening of
  setup; never runs in production.
- Rule: everything that **makes** the map runs on the PC; production only receives the finished world
  folder (stop server → copy → Chunky pass for missing chunks/light → start).

### 7.6 First step proposed
A **small test island (radius 1,000 blocks)** through the whole loop (heightmap → 2D/3D preview →
`wpscript` export → BlueMap → test server). It answers the open checks (version, biome ids, trees,
void edge, export time and RAM on your PC) before hours are spent on the real size.

## 8. Test island plan (✔ user asked, round 14)

**Goal: prove the pipeline, not make a beautiful map.** Every tool, agent and check of the skill
(`.claude/skills/map-building/SKILL.md`) runs once end to end on a small island, and the numbers needed
for the real one are measured.

### 8.1 Content (`worldgen/islands/test/island.json`)
Radius **1,000 blocks** (2 × 2 km; 1/16 of the production area), one small sample of each risky feature:

| Sample | Tests |
|---|---|
| A snowy peak (≈ 200) with a **summit lake** | ridged noise, snow by height, high water closed, path to the lake |
| A cherry hill | `cherry_grove` id, cherry trees, **bee nests** |
| A small **fjord closed toward the void** | water closure check, rock barrier, port plot by the water |
| A small **volcano with a crater** | basalt/blackstone surface masks, crater plot (desert donjon), distance to forests |
| A dark forest with a **creek** into the fjord + a small `pale_garden` | `dark_forest` / `pale_garden` ids, creek carving, creakings |
| Oak hills, meadow, rock outcrops | the faction land, slopes |
| One **flat plot 160 × 160** (city stand-in) + one 64 × 64 event plot | plot flattening, paste of a real build |
| A **cave test**: one cavern ~40 × 20 × 40 carved after export | how the amethyst cave will be made (FAWE script or structure) |
| Edge: shore, low cliff, one **rock face to the edge** | void edge, falling |

### 8.2 Prerequisites (user, once)
Status 2026-11-11 (round 15): WorldPainter **2.27.1** installed (`C:\Program Files\WorldPainter`,
`wpscript.exe` present); a world exported to `worldgen/template/` (level.dat `DataVersion` 4671 =
1.21.11, border 1024); Python **3.15.2** (`py -3.15`); BlueMap: config generated on first start, then
`accept-download` set. ✔ `worldgen/template.world` saved (1.9 MB, 2026-11-11): the project that holds
the export settings. `worldgen/template/` (17 MB) and `*.world` go in `.gitignore` (not
committed). Python 3.15 is recent: if numpy/scipy have no wheels for it, the venv uses 3.13/3.14.
1. **WorldPainter** installed on the PC, latest version; tell Claude the version. In the GUI: create a
   tiny world, set export to **1.21.11**, save it as `worldgen/scripts/template.world` (export
   settings cannot be set from a script).
2. **Python 3.12** available (Claude creates a venv in `worldgen/.venv`, git-ignored).
3. **Docker Desktop** running (BlueMap), ~5 GB free disk on the PC.
4. A folder for the disposable island server (e.g. `…\servers\island-test`, Paper 1.21.11 +
   VitaminMCP); Claude prepares it with a script.
5. OK to let BlueMap download Minecraft's client resources (its `accept-download` setting).

### 8.3 Steps
| Step | Who | Output | Gate |
|---|---|---|---|
| 0 | main session | branch `feat/map-pipeline`; `worldgen/` folders, `.gitignore` (`worldgen/out/`, `worldgen/.venv/`), venv, the 6 agent files | |
| 1 | `map-designer` | `layout.json` + sketch | ★ user approves the sketch |
| 2 | `terrain-generator` | heightmap, masks, 2D + 3D previews, metrics | |
| 3 | `map-verifier` | terrain report | ★ user looks at previews + report |
| 4 | `worldpainter-exporter` | world folder, export time + RAM | |
| 5 | `bluemap-renderer` ∥ `ingame-checker` | BlueMap web map + screenshots; edge, trees, bees, creakings, cave test | |
| 6 | `map-verifier` | world report | ★ user approves or asks for a 2nd iteration |
| 7 | main session | **findings report** (below), commit of scripts/agents/layout/reports, PR | |

At least **two iterations** are expected (the first one always teaches something).

### 8.4 Pass criteria (the pipeline is good when…)
- Same seed + layout gives the same heightmap (run twice, compare hashes).
- All verifier checks PASS on the second iteration, or each FAIL is understood and fixable.
- The exported world opens on Paper 1.21.11 without errors; the biome ids `cherry_grove`,
  `pale_garden`, `dark_forest`, `jagged_peaks` are correct in game (F3).
- Trees appear in every forest biome, cherry trees carry bee nests, the void edge kills a bot.
- The fjord does not leak; the summit lake stays put.
- A real build (e.g. one donjon `.nbt`) pasted on the event plot sits flat.
- BlueMap renders it and the screenshots at fixed points are usable by the verifier.
- One full iteration (steps 2–6) takes **under ~1 hour** of machine time.

### 8.5 What it measures for production (radius 4,000 = 16 × the area)
Export time and WorldPainter peak RAM (× 16 to estimate production: if the PC cannot hold it, export
in tiles or raise WorldPainter's memory), world size on disk (× 16 → backup sizing,
`docs/deployment.md` §2.6), BlueMap render time, which tree method works for cherry/pale oak, the cave
method. Then the production layout starts from `worldgen/map.md` with these numbers.

### 8.6 Not in the test
The real city paste, the amethyst cave's final design, roads at full length, the production
fixtures, any Hatlas plugin setup.
