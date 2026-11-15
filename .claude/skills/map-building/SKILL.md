---
name: map-building
description: Builds the Hatlas island map with Claude driving WorldPainter: brief (worldgen/map.md) → layout → Python heightmap and biome masks → 2D/3D previews → wpscript export → BlueMap render → in-game check, with one agent per step and user approval between phases. Use when designing, generating, checking or rendering the island (test or production), or when asked how the map pipeline works.
---

# Building the Hatlas island

> **Status: process defined 2026-11-10, tools not built yet.** The scripts, agent files and BlueMap
> compose named below are **to be written** during the test island (`docs/map-building.md` §8). Until
> then, follow this as the plan and create each piece when its step is first run.

The map is **generated from files, not built by hand or by bots**. Every step reads files written by
the previous one and writes its own; agents never pass results through chat, only through these files.
That makes each step re-runnable, reviewable, and checkable by an agent that did not produce it.

## 1. Sources of truth
1. `worldgen/map.md`: the **brief** (ambiance, zones, links, what must be checked). Never contradict it;
   if a step cannot satisfy it, stop and report.
2. `worldgen/islands/<name>/island.json`: the run's parameters (radius, seed, which zones, scale).
   `<name>` = `test` (radius 1,000) or `prod` (radius 4,000).
3. `docs/map-building.md`: research and decisions (why WorldPainter, why no bots, licences).

## 2. Files (the contract between agents)
```
worldgen/
  map.md                         brief (committed)
  islands/<name>/island.json     parameters + seed (committed)
  islands/<name>/layout.json     zones, plots, roads, water, edge segments (committed, reviewed)
  islands/<name>/reports/*.md    verifier reports per iteration (committed)
  scripts/                       Python + wpscript JS (committed)
  bluemap/                       compose.yml + config (committed)
  out/<name>/<iteration>/        GIT-IGNORED: heightmap.png (16-bit), masks/*.png, preview-2d.png,
                                 preview-3d.html, metrics.json, world/ (export), bluemap web data,
                                 screenshots/
```
Generated outputs are rebuilt from `layout.json` + seed, so they stay out of git (they are large). The
approved production heightmap and masks are kept with the backups, not in git.

`layout.json` (shape, refined by the designer): island outline polygon; per zone of the brief: id,
biome list, polygon, target heights (min/max/peak), share; plots (id, centre, size, target y, purpose:
`city`, `event:<site>`, `donjon:<type>`); roads and the tunnel (polylines, max grade); water bodies
(polygon, surface y, kind: fjord/lake/creek); edge segments (`shore` | `low_cliff` | `rock_to_edge`).

## 3. Agents and steps

The **main session orchestrates**: it reads the brief, starts each agent with the file paths, checks the
outputs exist, and **asks the user to approve** at the three gates (★). Agents start cold: give them
the paths and the iteration number, not a summary of the conversation.

| # | Agent (`.claude/agents/`) | Reads | Writes | Tools |
|---|---|---|---|---|
| 1 | `map-designer` | `map.md`, `island.json` (+ footprints of the city/donjon builds, measured from `.nbt`/`.schem`) | `layout.json`, `out/…/layout.png` (top view sketch) | Read, Write in `worldgen/`, Bash (python) |
| ★ | user approves the layout | | | |
| 2 | `terrain-generator` | `layout.json`, `island.json` | heightmap, masks, `preview-2d.png`, `preview-3d.html`, `metrics.json` | Bash (python), Write in `worldgen/out/` |
| 3 | `map-verifier` | `map.md`, `layout.json`, `metrics.json`, the previews (images) | `reports/<iteration>-terrain.md` with PASS/FAIL per check | Read only + Bash (python metrics) |
| ★ | user looks at the previews (2D image + 3D page) and the report | | | |
| 4 | `worldpainter-exporter` | heightmap, masks, `scripts/*.js`, the `.world` template | `out/…/world/`, export log (time, peak RAM) | Bash (`wpscript`) |
| 5a | `bluemap-renderer` (parallel with 5b) | `out/…/world/` | BlueMap tiles + `screenshots/bluemap-*.png` from fixed camera points | Bash (docker compose, headless browser) |
| 5b | `ingame-checker` (parallel with 5a) | `out/…/world/` | `screenshots/ingame-*.png`, edge/void and spawn checks | Bash (island server script), VitaminMCP |
| 6 | `map-verifier` (again) | brief, layout, all screenshots | `reports/<iteration>-world.md` | Read only |
| ★ | user approves the world, or asks for changes → back to 1 (layout) or 2 (terrain) | | | |

Only steps 5a and 5b run in parallel (both only read the exported world). Everything else is
sequential because each step needs the previous one's files. The verifier **never** sees the
generator's reasoning, only its outputs: it judges like a reviewer.

### Step 1 — `map-designer`
- Turn each zone of the brief into polygons on the island, respecting sides, shares and links.
- Plots: measure each build's footprint first (city, donjons, event structures), add 32 blocks of
  margin, choose a target height consistent with the terrain around.
- Roads: from the city to every site of the brief §4, grade ≤ 1/3; the tunnel to the amethyst cave.
- Water: every water body closed (fjord closed by a rock barrier toward the void).
- Edge: mark segments; at least one `rock_to_edge`.
- Output a top-view sketch (zones coloured, plots, roads, names) for the user.

### Step 2 — `terrain-generator`
- Python (numpy, scipy, Pillow; a noise library): base noise per zone (ridged noise for the snowy
  range, rolling noise for hills), blended by distance to zone borders; **hydraulic/thermal erosion**
  for realistic valleys; carve the fjord, lakes and creek to their surface y; **flatten plots** with a
  smooth falloff; grade roads; drop the land to "void" outside the outline (heightmap value 0 + a void
  mask).
- Masks: one 8-bit PNG per biome group and per surface (snow above a height, stone on steep slopes,
  gravel, grass), plus `void.png`, `water.png`.
- Previews: `preview-2d.png` (biome colours + hillshade + 10-block contours + plots and roads drawn);
  `preview-3d.html` (three.js mesh of a downsampled heightmap, coloured by biome, orbit controls;
  three.js from cdnjs, pinned version), small enough to open locally or publish as an artifact.
- `metrics.json`: share per zone, slope histogram per zone, max slope per plot, highest point, water
  bodies and their closure, edge segment kinds and lengths, road grades.
- Same seed + same layout ⇒ same output (record versions of the libraries in `metrics.json`).

### Step 3 and 6 — `map-verifier`
Checks (brief §6 made measurable):
- every zone present, on its side, share within ±30 % of the target;
- plots: max height difference ≤ 1 over 4 blocks, no water inside, target y ± 2;
- water: flood fill from each water cell never reaches the void (closed);
- roads: grade ≤ 1/3 everywhere; summit lake reachable on foot (A* on the heightmap with max step 1);
- edge: ≥ 1 `rock_to_edge` segment; no water at the edge;
- buildable land (slope ≤ 1/2) ≥ 45 % of the island;
- highest point ≤ 300; nothing above the build limit;
- then **look** at the images: does it read as the brief (dwarven mountain, cherry hills, fjord…)? Name
  what looks wrong, with coordinates.
Output: a table of checks with PASS/FAIL and numbers, then remarks. FAIL on a measurable check blocks
the gate; remarks do not.

### Step 4 — `worldpainter-exporter`
- `wpscript worldgen/scripts/build-world.js <iteration dir>` ([scripting API](https://www.worldpainter.net/trac/wiki/Scripting/API)):
  load the heightmap, create the world, apply terrain by masks, biomes by masks, tree layers or the
  "let Minecraft populate" option, resources, void outside; export to `out/…/world/`.
- Export settings come from a `.world` template saved **once by the user in the GUI** (the script cannot
  set them): target version 1.21.11, world border, game rules. WorldPainter 2.27.1 at
  `C:\Program Files\WorldPainter\wpscript.exe`; template `worldgen/template.world` (git-ignored).
- Record export time and the peak memory of the WorldPainter process. Never write into a world the
  test or production server is using.

### Step 5a — `bluemap-renderer`
- **Setup once** (`worldgen/bluemap/`): a compose service with the official image
  `ghcr.io/bluemap-minecraft/bluemap:<pinned version>`, command `-r -u -w` (render, update, web
  server), port `127.0.0.1:8100`, volumes `./config` → `/app/config`, `./data` → `/app/data`, `./web`
  → `/app/web`, and the iteration's world folder mounted **read-only** as `/app/world`
  ([BlueMap docs](https://bluemap.bluecolored.de/wiki/getting-started/Installation.html)). Order: start
  once **to generate the config**, then set `accept-download: true` in `core.conf` (the user agreed,
  2026-11-11: BlueMap downloads Minecraft's client resources), then render.
- Per iteration: point the map config at the new world, re-render, then take screenshots at **fixed
  camera points** (overview, city plot, each event site, the edge) with a headless browser, so the
  verifier compares iterations at the same views.
- Runs on the PC (Docker Desktop). A live BlueMap in **production** is a separate decision: it would show
  every faction base to raiders.

### Step 5b — `ingame-checker`
- Disposable **island test server** (separate folder from the Hatlas test server, so its baseline stays
  untouched): Paper 1.21.11 + VitaminMCP, no Hatlas needed. Copy the world in, start, then with a bot:
  `bot_view` screenshots at the camera points; walk off the edge (dies in the void); check spawn,
  lighting, missing chunks, trees and bees in the cherry grove, creakings area at night.
- Stop the server at the end.

## 4. Rules
- **Gates are the user's**: never skip ★ to "save time".
- Pinned versions everywhere (WorldPainter, BlueMap image, Python packages, three.js).
- Reference builds from the Internet only with a licence that allows a paid server; no scraping
  (`docs/map-building.md` §3).
- Nothing here ever runs on the production machine; production only receives the approved
  `world/` folder (stop → copy → Chunky pass → start).
- Each iteration gets a new `out/<name>/<n>/` folder; never overwrite an approved one.
- Report at the end of each run: iteration, what changed, verifier verdicts, export time/RAM, open
  issues.
