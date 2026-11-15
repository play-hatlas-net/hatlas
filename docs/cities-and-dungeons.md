# Cities, city zones and the dungeon server (plan, 2026-11-11)

> **Status: plan only, nothing built.** Sources: user, round 17 (request), round 18 (answers, 2026-11-11)
> round 19 (answers, 2026-11-12) and round 20 (answers, 2026-11-13). Mining world (round 20):
> [`mining-world.md`](mining-world.md). Job skill trees: [`job-skills.md`](job-skills.md). Open questions in
> §10, mirrored in `CLAUDE.md`. Nothing here is decided until it is marked ✔.

---

## 0. Summary

| Topic | Status |
|---|---|
| Dungeons are **private PvE instances**, only players of one faction, up to **8** (config) | ✔ round 18 |
| **One dungeon server** for every dungeon, built as a pool (option B) | ✔ round 18 |
| Dungeons rebuilt as **fight zones** (wave / mini-boss / boss) with inner and outer areas | ✔ round 18 (§7) |
| Copies pre-pasted with a **void gap ≥ view and simulation distance** between them | ✔ round 19 (§7.1) |
| **City zone events = one shared dungeon run on the dungeon server**, every faction inside, won by **power score** | ✔ round 19 (§6), replaces the round 18 "fight zone with PvP in the real map" |
| Events triggered at a **random time 24–72 h** after the previous one (config window) | ✔ round 19 |
| City control: **more than half of its zones**; a city **changes hands only when another faction holds more than half** | ✔ rounds 18–20 |
| Event run: **PvP on, no key, max 4 players per faction**, random spawn in an admin-set **circle (radius 8)** per zone | ✔ round 20 (§6.2) |
| Event times: **only inside play hours** (Europe/Paris), announcements **30 / 15 / 5 min** before, **timeout 60 min**, all in yml | ✔ round 20 |
| Power score points go to the faction that deals **the last hit** (makes builds and combos matter) | ✔ round 20 (C33) |
| Rewards of control: daily XP by size tier 1–4 / 5–24 / 25+ (× 1.5 / 1.0 / 0.6), **shop tax** 8 / 5 / 2 %, 5 % discount, own Jokeyrini, Mayor title, +1 dungeon run, +10 % job XP, banners, welcome message, **armour/weapon skins**; all in yml; **no free teleport** | ✔ round 20 (§6.4) |
| **Ruby mining right → the mining world**: ore zones leave the faction server; each city has a mine entrance + a **holder-only entrance to a sealed cave with +70 % ruby** | ✔ round 20 ([`mining-world.md`](mining-world.md)) |
| Dungeon rules: join mid-run, one run per faction, **3 h cooldown per dungeon tied to the player**, **3 runs per day**, keep inventory, no drops, 10 min reconnect | ✔ round 19 (§7.5–7.8) |
| Jokeyrini: own pool per NPC, **one active quest per player network-wide**, daily key cap = **3** | ✔ rounds 18–19 |
| City zones protect blocks like safe zones (ore zones: **obsolete**, round 20 moves mining to the mining world) | ✔ round 18, superseded |
| Job skill trees: personal, **kept when leaving a faction**, jobs without a faction | ✔ round 19 ([`job-skills.md`](job-skills.md)) |
| Custom GUI skins built in our `hatlas` pack; art made by a script (+ AI ornaments), **skill + agent `gui-art`** | ✔ round 19 (§3) |
| Code: **`hatlas-dungeons` plugin + `hatlas-common` library** (Gradle composite build) | ✔ round 19 (§8) |
| Boss look by **BetterModel** (free, MIT), behaviour in our code; **no paid plugin** | ✔ round 19 (§4) |
| **Everything in this plan is needed for the launch**; a **beta test after each epic** (dungeons, mining world, cities) | ✔ rounds 19–20 (§9) |

---

## 1. The game loop

```
              FACTION SERVER (PvP, territory)                         DUNGEON SERVER (PvE, void world)
 ┌─────────────────────────────────────────────────────┐          ┌──────────────────────────────────┐
 │ City (safe zone)                                     │          │ copies of each dungeon, far apart│
 │  ├─ 5 job shops (NPC, skinned menu, Workshop)        │          │                                  │
 │  ├─ Jokeyrini NPCs (own pool each) ─► keys ──────────┼──┐       │ private run (one faction):       │
 │  ├─ Wizard NPC (remove skill nodes, OQ 65)           │  │       │   start → zones → mini-bosses →  │
 │  └─ Mayor NPC (zones, owners, events, timers)        │  │       │   boss; faction XP → outbox      │
 │                                                      │  │       │                                  │
 │ City zones (no block edits): entrance NPC;           │  │       │ city zone event (all factions):  │
 │ when its event runs, players enter from here ────────┼──┼──────►│   power score per faction;       │
 │ zone owner = best power score at the end             │  │       │   boss down → best score wins    │
 └─────────────────────────────────────────────────────┘  │       └──────────────▲───────────────────┘
                                                          └─► each player deposits a key (private runs)
                       ◄── back to the same spot after the end delay (inventory goes both ways) ──┘
```

---

## 2. Challenges after round 21

### 2.1 Round 21 (2026-11-16): answers and new challenges

✔ **Decided by the user (OQ 71, 72, 76, 77):**
- **Spawn protection 5 s**; **no PvP between allies**; a free slot can be taken by another member; a player
  who left can come back after **`event.rejoin_cooldown_seconds: 60`** (yml) if a slot is free.
- **Several spawn circles** per dungeon/city zone (positions by admin command, stored in the database);
  **radius default in yml** (`spawn.default_radius: 8`). A player **never spawns inside a block** that
  suffocates them.
- Admin command **`/dungeon doctor`** checks the whole setup (C40).
- Last hit: **credit rules of C33 ✔**, **3 mini-bosses (30) beat the boss (25) ✔ intended**, **ties: the
  holder keeps, else the first faction to reach the score ✔**, **timed-out event: the holder keeps the zone
  ✔** (explained in C39, user asked).
- Loot: **a personal roll per participant + a bonus roll for the last hitter ✔**. **Participant = dealt
  damage only** (not "was in the outer area"). **Inventory full → the item drops at the player's feet** ✔.
- Skins **only while holding the city, one set per city ✔**.
- User idea: **one command family `/dungeon create <type> <name>` for dungeons and city zones**, since both
  have the same engine (mini-bosses, boss, waves, spawns) with different rules (C41).

**C39. "Timed-out event: the holder keeps the zone", explained.** An event lasts at most
`event.timeout_minutes: 60`. Two endings:
- **The final boss dies before 60 min** → scores are compared, the best faction takes the zone (ties: C33).
- **The boss is still alive at 60 min** → the event ends as **EXPIRED**: **nobody takes the zone**, it stays
  with the faction that held it before the event (or stays **without owner** if it had none). XP and loot
  already won during the event are kept; only the **control** of the zone is not decided.

Why not "best score at the timeout wins"? Because the boss kill is the **closing moment**. If points decided
at the timeout, a faction ahead after the mini-bosses (e.g. 30 points) could **stop everyone from killing the
boss** (stand at the boss and fight every other faction, PvP is on) and win on time. With the rule as
decided, a faction that wants the zone **must** get the boss killed.

What to accept knowingly: **the holder can win by stalling.** Example: faction Red holds the zone; Blue takes
2 mini-bosses (20), Red takes 1 (10). If the boss dies, Blue wins (unless Red gets the last hit: 10 + 25 =
35 > 20). Red's other option is to **keep the boss alive** until 60 min, and Red keeps the zone. This is a
defender's advantage, the same as in real sieges. If it turns out too strong in the beta, the alternative
is: at the timeout, a faction that has **all the mini-bosses** (≥ 30) wins. Default: holder keeps.

**C40. `/dungeon doctor <name>`** (✔ user). Checks and prints ✔ / ⚠ / ✘ with a clickable teleport to each
problem:
- **at least 1 spawn circle**; for each circle: the centre is a safe spot, and a sample of points in the
  radius is tested (two air blocks for feet and head, solid ground below, no lava, fire, magma, cactus,
  powder snow, no void under): prints the **% of safe points** (✘ under 50 %);
- exactly **1 boss zone**, every zone has **≥ 1 wave**, every wave **≥ 1 mob**, every zone **≥ 1 spawn point**
  and no spawn point inside a block;
- mob and boss ids exist, boss models are loaded (BetterModel), loot tables exist;
- outer areas that overlap another zone (⚠);
- **city kind**: power values set, `max_players_per_faction` set, the linked city zone exists on the
  faction server (database check), PvP rules active;
- copies published, and the gap still fits the server's view and simulation distance (§7.1);
- the yml values of this dungeon are valid.

**Safe random spawn** (✔ user: never inside a block): the plugin picks a random point in a random circle,
then tests it with the same rules as the doctor; up to 20 tries, then the **circle centre** (which the
doctor has checked). Proposal: in a **city event** each faction gets **its own circle** (factions spread
round-robin over the circles, members of one faction together), so factions do not land on each other:
spawn killing is reduced even before the 5 s protection ends (OQ 86).

**C41. One engine, one command family (✔ user idea, agreed).** Private dungeons and city zone events are
already the same engine on the dungeon server (§6.2, §7.3). So:
- `/dungeon create <dungeon|city> <name>` creates either kind; every other command (`template`, `spawn`,
  `zone`, `wave`, `doctor`, `publish`) works on both.
- The **kind** picks a **rules profile** in `dungeons.yml > kinds.<kind>`: `pvp` (off / on), `key_required`
  (yes / no), `max_players` (8) or `max_players_per_faction` (4), `power_score` (no / yes), `rejoin_cooldown`,
  `spawn_protection_seconds`, `loot.last_hit_bonus_roll` (no / yes). A dungeon can override any value in
  its own file.
- Private dungeons use **spawn circles too** (radius 0 = an exact point), so there is one spawn system.
- The **city zone** on the faction server (region + entrance NPC) stays a faction-server thing:
  `/cityzone create <zone> <city> <dungeon>` links it to a `city` dungeon. Positions on the faction server,
  dungeon content on the dungeon server.
- The legacy **`/donjon`** command (faction server, §4.5 of `CLAUDE.md`) is **removed** when the dungeon
  epic lands, so admins only learn `/dungeon` (OQ 87). The same "doctor" idea is reused: `/mine doctor`
  ([`mining-world.md`](mining-world.md) §4).

**C42. Rejoin after 60 s = going home to restock.** A player who leaves goes back to the faction server
**with their items** (handoff), can refill potions and gear, and come back after 60 s. In a PvP event this
is a strong trick: leave at low HP, come back full. Options: (a) accept it, the 60 s and the free-slot rule
are the price (user's rule as stated); (b) a longer default (e.g. 300 s); (c) a voluntary leave = out for
this event, only a **disconnect** can come back (10 min window). Recommendation: **(a) with 60 s as
default**, since the slot can be taken meanwhile and the trip costs time, and watch it in the beta; the
value is in yml (OQ 85).

**C43. Participant = dealt damage only.** Tanks and healers who never hit the boss get **no loot**. That
pushes every player to land at least one hit ("tag for loot"), which is easy and fine, but a healer standing
back gets nothing. Proposal: **any damage counts** (no minimum), including damage from a player's effects
(damage over time, thorns), and **a tank's taunt or a healer's heal on a player who hit counts as taking
part** (assist). Without the assist rule, healers in dungeons must tap the boss. OQ 88.

**C44. Loot dropped at the feet in a PvP event.** With PvP on, an item dropped on the ground could be picked
up by an enemy. Proposal: the dropped item is **locked to its owner** (Paper `Item#setOwner`, nobody else
can pick it up), glows, and the player gets a chat warning; anything still on the ground when the player
leaves is lost. With the travel bag ([`cross-server-items.md`](cross-server-items.md)) a full inventory
happens more often, so the warning matters.

### 2.2 Round 20 and earlier

Resolved by round 20: C22 (event run: PvP on, no key, 4 per faction), C23 (city changes hands only when
another faction holds more than half), C25 (last hit, see C33), C26 (play hours, announcements, timeout), C27
(disconnected players count as inside; the inventory is always sent back, never deleted), C30 (mining world).

**C32. A random spawn circle with PvP on = spawn killing.** Every faction lands in the same circle
(radius 8) and PvP is on: a faction that arrives first can kill the next ones as they appear, and a player
who dies respawns in the same circle. **Proposal:** **spawn protection** of `event.spawn_protection_seconds:
5` (no damage taken or dealt, ends early when the player attacks), and respawns after a death also land in
the circle with the same protection. The circle (centre + radius) is set **per city zone by an admin
command** and stored in the database (✔ user: not in a yml file):
`/cityzone spawn set <zone>` (centre = your position, on the dungeon server, stored relative to the build
origin), `/cityzone spawn radius <zone> <blocks>` (default 8). Also to settle: **PvP between allied
factions** in the event (proposal: off, as in today's donjons) and **a free slot when one of the 4 leaves**
(proposal: another member may take it; a player who left cannot come back in the same event). OQ 71.

**C33. Last hit (✔ user).** The faction whose player deals the **killing blow** to a mini-boss or the boss
gets its power points. The user's reason: it makes a faction plan its builds together (burst skills,
combo items, e.g. a Hunter node that adds damage against bosses **only in dungeons and city events**, with
a sword that only a Miner with the right node can craft; see [`job-skills.md`](job-skills.md) §3.4).
What it implies, to accept knowingly:
- **Kill stealing is the game**: around a boss at low HP, factions fight each other (PvP on) and wait for the
  last moment. Expected, and fine with spawn protection (C32).
- **Who owns a hit** must be defined for every damage source: projectiles → the shooter; potion splash,
  poison and other damage over time → the player who applied it; thorns → the wearer; a tamed wolf or a
  faction golem → its owner; fall, void, lava → the **last player who hit the boss in the 10 s before**; no
  player at all → nobody gets the points (proposal, OQ 72).
- **Boss healing or regen** between hits must not undo damage silently: boss HP is shown to all (boss bar).
- Still open from round 19: **3 mini-bosses (30) beat the boss (25)**: intended? Ties on the total score:
  the holder keeps the zone, else the faction that reached the score first (proposal). OQ 72.

**C34. Timed-out event** (round 19 C24). The user agreed with the proposals of OQ 62 for the city; for a
timed-out event the plan keeps **the holder keeps the zone** (same logic). To confirm in OQ 72.

**C35. Loot, clarified (user asked about OQ 70).** "Personal loot" does **not** copy one item for everyone.
It means: when a mini-boss or the boss dies, the loot table is **rolled once for each participant**, and each
player gets **their own result** straight into their inventory (one may get a diamond, another nothing).
Nothing falls on the ground, so nobody fights over a pile and the "no drops" rule holds. Three options:

| Option | What happens | For | Against |
|---|---|---|---|
| **A. Personal roll per participant** (recommended) | each participant rolls the table on their own | fair, no drops, simple to explain | more items in total when more players come (balance with the table) |
| B. One roll, to the last hitter | only the player (or faction) of the killing blow gets loot | matches the last-hit rule | the other players of a private run get nothing |
| C. One roll, shared pool | one result, given to a random participant | fewer items | feels random and unfair |

In a **private run** (one faction) option A is clearly best. In a **city zone event** (several factions)
the user may want the last-hit faction to get more: proposal A for everyone **+ a bonus roll for the
last-hit player**. A *participant* = dealt damage to that mini-boss/boss **or** was inside its fight zone's
outer area when it died (so healers and tanks count). OQ 76.

**C36. Skin rewards (✔ user asked).** Cosmetic skins for armour and weapons: the item keeps its stats, only
its look changes (`item_model` and, for armour, `equippable.asset_id` = `hatlas:<city>_<piece>`). Applied
at the Mayor (skinned menu: put the item, pick the skin), removed for free. To settle (OQ 77): **only while
the faction holds the city** (proposal: yes, skins go back to normal when the city is lost; the look shows
who rules) or **a permanent unlock**. Art: one texture per piece and per city (sword, axe, bow, 4 armour
pieces = ~8 textures + 2 equipment layers per city): the `gui-art` generator only draws flat menus, so a
small **`item-art`** mode is needed (palette, 16 × 16 item textures, armour layers, preview on a model).

**C37. Configurable values.** ✔ user: event play hours, announcements, timeout, size tiers, XP factors, tax,
discount and extra rewards are **in yml** (`cities.yml`); only **positions** (event spawn circles, landings,
entrances) are set by **admin commands** and stored in the database, because they belong to the map.

**C38. The events and the mining world need each other.** The holder's bonus mine entrance (mining world
epic) is a city reward, and city control needs the event runs (dungeon epic). Build order: dungeons →
mining world → cities (§9), with a beta after each.

**C31. Shop tax and the ruby burn.** Today a shop purchase **burns** the rubies (ledger `SHOP_BUY`). A tax
paid to the holder means **8 / 5 / 2 % of each purchase is not burned** but moved to the holder's vault
(new ledger kind `CITY_TAX`, buyer → holder faction). That slightly raises the ruby supply: fine, but watch
`web_ruby_daily` after launch.

**C11'. The inventory transfer** (§7.8): death is settled (keep inventory, items can still break),
disconnect is settled (10 min, C27); crash and ticket expiry keep the round 18 proposals (OQ 46).

**C20. Remembered mobs** (unchanged): living mobs keep their current HP when a zone pauses.

---

## 3. Custom GUI skins: where does the art come from? (✔ round 19)

**Code side** (unchanged): a skin layer on `HatlasGui`. The menu title draws a full background glyph from our
font `hatlas:gui` (negative space to the left edge, `ascent` for the height, then the real title), buttons
are items with `item_model = hatlas:gui/<button>`, tooltips with `tooltip_style`. Known pitfalls to test:
negative spaces in titles shifting with some clients or OptiFine, and very rare crashes reported on some
Intel integrated GPUs with negative-space characters in chat/tab (keep them **only in menu titles**).

**Art side** ✔ round 19: a **generator script + AI-made ornaments**, no bought pack. The user asked for a
**skill and an agent** for it, and an MCP server to **learn from public GUI art**:

| Piece | Plan |
|---|---|
| Skill `.claude/skills/gui-art/SKILL.md` | the contract: one layout file per menu (`resourcepack-src/gui/<menu>.yml`: rows, used slots, buttons, title area, tree lines), the palette (dwarven: stone, iron, gold, amethyst), the generator `scripts/gui-art/generate.py` (Python + Pillow), outputs into `resourcepack/assets/hatlas/` (texture + font provider JSON), previews in git-ignored `resourcepack-src/out/` |
| Agent `.claude/agents/gui-artist.md` | runs the generator, composes a **preview over a vanilla menu screenshot**, checks it (slots on the 18 px grid, palette only, no pixel off the frame), then stops for **the user's approval** (gate) before writing into the pack |
| Ornaments | AI images (e.g. the Figma image generator available in this session) for crests and corners only, **downscaled and reduced to the palette** by the script |
| Learning from public art | **as style references only, with a licence that allows it**: CC0 UI packs (e.g. Kenney's UI packs, OpenGameArt filtered on CC0), kept in `resourcepack-src/gui/references/` with a `LICENSES.md` line each. **No pixels copied from unlicensed packs, no scraping** (same rule as shared maps, `docs/map-building.md`). Claude reads the reference images directly; **no extra MCP server is needed** (an MCP only adds a way to fetch, the licence check stays the same) |
| Skill tree menu | ✔ the tree background (§6 of [`job-skills.md`](job-skills.md)) is made by the same generator, with **connector lines** drawn from the tree file |

When a layout changes, the PNG is regenerated, never redrawn by hand.

---

## 4. Boss models and the boss framework (✔ round 19)

Look and animations by **BetterModel** (free, MIT licence): **pilot first**. **No paid plugin** (✔ user):
ModelEngine is dropped as the fallback; if BetterModel fails the pilot, the fallback is **our own models
with display entities** (more work, no dependency). Behaviour in our code (`bosses.yml`: HP, phases, attacks
with telegraphs and cooldowns, defences such as shield phases, damage cap per hit against 1.8 PvP bursts,
enrage timer). It lives in `hatlas-common` (§8).

---

## 5. Cities

### 5.1 Model
`City` (id, name, safe zone, Mayor NPC, shops, Jokeyrini NPCs, zones, owner faction, owner since). Storage
domain **CITIES**; website views `web_cities`, `web_city_zones`. The spawn city is the first one.

### 5.2 Job shops
The existing job shops are linked to a city (5 per city, own stock rotation each). The shop menu gets a
**Workshop** page for players of that job, listing the actions unlocked by their skill tree
([`job-skills.md`](job-skills.md)). Any ruby spent there records a ledger row. Round 19: a player may now
**have a job without a faction**; today shops are paid from the faction vault, so a player without a faction
cannot pay. ✔ Round 20: a player **without a faction pays with the rubies in their own inventory**
(ledger `SHOP_BUY` from the player). Faction members: OQ 73.

### 5.3 Jokeyrini per NPC (✔ rounds 18–19)
Each Jokeyrini NPC has an id and its own pool (`jobs.yml > jokeyrini.npcs.<id>`, fallback: the global
pool), reset and legendary chance. A player holds **one active Jokeyrini quest network-wide** and earns at
most **`jokeyrini.daily_key_cap: 3`** keys per day (✔ round 19: a player can do **3 dungeons per day**). The
quest shows which NPC gave it. The holder of a city gets an **exclusive Jokeyrini** (§6.4).

### 5.4 The Mayor
Skinned menu: city owner (since when), one item per zone: name, description, owner faction or "none", event
state (none / announced at HH:MM / running: power scores, boss HP %, ends at HH:MM) and the rewards of
control. Read-only text pages may use the Paper Dialog API.

---

## 6. City zones and their events (✔ round 19)

### 6.1 The zone on the faction server
A **city zone** is a region linked to a city: **blocks protected like a safe zone** (✔ round 18; ore zones
leave the faction server in round 20). No claims, no faction creation, no outpost. It holds an **entrance NPC**. It has an
**owner** (a faction or none).

### 6.2 The event = one shared dungeon run
- **When:** after each event, the next one is drawn at a random time between **`event.min_hours: 24`** and
  **`event.max_hours: 72`** (config, ✔ round 19), **only inside play hours** `event.play_hours: "14:00-23:00"`,
  zone `Europe/Paris` (summer time handled) (✔ round 20). Announcements at **`event.announce_minutes: [30, 15,
  5]`** (chat + Mayor + the zone's NPC). **Timeout `event.timeout_minutes: 60`**. All in `cities.yml` (✔).
- **Where:** one copy of the zone's dungeon on the **dungeon server**. Every faction's players enter through
  the zone's entrance NPC; all of them play **the same run**. ✔ Round 20: **PvP on**, **no key**, **at most
  4 players per faction** (`event.max_players_per_faction: 4`).
- **Spawn** (✔ rounds 20–21): players appear at a **safe random point inside one of the spawn circles**
  (centres by admin command, stored in the database; radius default `spawn.default_radius: 8` in yml);
  **5 s spawn protection**, **no PvP between allies**, rejoin after `event.rejoin_cooldown_seconds: 60` if
  a slot is free (C32, C40, C42).
- **During the event the holder keeps the zone** (✔).
- **Power score** (✔ round 19), per faction, config in the zone's dungeon file:
  `power.mini_boss: 10`, `power.boss_multiplier: 2.5` (→ boss = 25), `power.wave: 0`. ✔ Round 20: the points of a
  mini-boss or the boss go to the faction of **the last hit** (C33).
- **End:** when the **final boss dies**, the faction with the **highest total power score** gets the zone;
  then after `boss_exit_delay_seconds` every player goes back to the faction server **at the spot they left**.
- **Timeout:** no boss kill before the event timeout → resolved by nobody, **the holder keeps the zone**
  (✔ round 21, explained in C39).
- Lifecycle: `SCHEDULED → ANNOUNCED → RUNNING → RESOLVED | EXPIRED`. A restart of either server during an
  event = event cancelled and rescheduled, players returned.

### 6.3 City control (✔ rounds 18–19)
**City owner** = the faction holding **more than half** of the city's zones (2 of 3, 3 of 4, 3 of 5). Nobody
above half → **the previous owner keeps it**. ✔ Round 20: a city **changes hands only when another faction
holds more than half**; the owner dropping to half or less is not enough.

### 6.4 Rewards of control (✔ round 20)
Faction size tiers (✔): **small 1–4 members, normal 5–24, big 25+**. **Every value below is in `cities.yml`**
(✔ user).

| Reward | Rule |
|---|---|
| **Daily faction XP per zone held** | `city.rewards.daily_exp.base × tier factor`: small **1.5**, normal **1.0**, big **0.6** (✔) |
| **Tax on the city's job shop sales** | small **8 %**, normal **5 %**, big **2 %** of every purchase in the city's shops goes to the holder's vault (ledger `CITY_TAX`, C31); collected **only on shops whose job a member of the holder has** (✔) |
| **Discount** | **5 %** at the city's shops for the holder's members (and no tax on their own purchases) |
| **Exclusive Jokeyrini** | one Jokeyrini NPC that only the holder's members can use |
| **Mayor's board** | the holder's name, colour and a title |
| **Mine bonus entrance** | the holder's members use the city's **holder-only entrance** to a sealed cave with **+70 % ruby** in the mining world ([`mining-world.md`](mining-world.md)) (✔ replaces the ruby mining right) |
| **+1 dungeon run per day** | 4 instead of 3 for the holder's members (✔) |
| **+10 % job XP** | on quests taken in that city (✔) |
| **Banners** | the holder's banners on the city gates (✔) |
| **Welcome message** | written by the holder, shown on entry (✔) |
| **Armour and weapon skins** | cosmetic city skins (C36, OQ 77) (✔ user) |
| ~~Free teleport~~ | ✘ dropped (user) |

---

## 7. The dungeon server (✔ option B, design of rounds 18–19)

### 7.1 World and copies (✔ round 19)
- One **void world** holding the dungeon builds **floating in the air**, closed builds or open builds fenced
  by **invisible barrier blocks**. Falling out = death in the dungeon (§7.8: keep inventory, respawn at the
  start).
- **Players cannot change blocks** there, so a copy never needs repairing: each dungeon type is **pasted K
  times once**, and an instance is just a **free copy assigned to a run**. Freeing a copy = remove its
  entities. No world copies, no server fork.
- **Gap between copies** (✔ user): the void between two copies (measured between their bounding boxes,
  outer areas included) is **at least the view distance and the simulation distance + 1 chunk**:
  `gap_chunks ≥ max(view-distance, simulation-distance) + 1`. A player standing at the edge of a copy then
  only loads **empty void chunks**, never the next copy: nobody sees another run, and the next copy's mobs
  are never loaded or ticked by them (a void chunk costs almost nothing). The client cannot see further:
  its render distance is capped by the server's view distance.
- **Layout:** a grid of cells, `cell = build size + gap`. Example: view 8, simulation 6 → gap ≥ 9 chunks
  (144 blocks); a 200-block build → copies every 344 blocks.
- **Safety checks:** `/dungeon publish` computes the gap from the server's settings; on start-up, if the view
  or simulation distance was raised above `gap − 1`, the server **refuses to open runs** and logs why. A
  **per-player world border** (Paper `Player#setWorldBorder`) around the copy's cell stops pearls and elytra
  from crossing the gap.
- The whole build area is protected: no break, no place, no interact (except what the build needs, e.g.
  doors, as a per-dungeon allowlist). **No PvP** in private runs; **PvP on** in city zone events (✔ round 20).

### 7.2 Dungeon shape (✔ round 18)
Every dungeon: **an open start area** (spawn) → **connectors and paths** → one or more **open mini-boss
areas** → connectors → **one wide open final boss area**. The builds are made to this shape.

### 7.3 Fight zones (the engine)
| Field | Rule |
|---|---|
| Type | `WAVE`, `MINI_BOSS` or `BOSS`; a dungeon has **exactly one `BOSS` zone** |
| Inner area | cuboid; **one player entering starts** the zone |
| Outer area | inner + `outer_radius` (default in `config.yml`, overridable per zone); **when no player is left in it, the zone pauses** |
| Waves | ordered list, **at least 1**; each wave **at least 1 mob**; a wave may contain a mini-boss or the boss (optional) |
| Spawn points | one or more per zone |
| Once only | a wave cleared stays cleared for the whole run |
| Pause | living mobs removed and **remembered** (type, current HP); they come back on the next entry (C20) |

**When a zone is completed:**
- `WAVE`: bonus faction XP.
- `MINI_BOSS`: **personal loot** for each player who took part (C35, OQ 76) + faction XP (+ power score in an event).
- `BOSS`: personal final loot + faction XP (+ power score), then after **`boss_exit_delay_seconds`** (config)
  every player goes back to the faction server at the position they left.

**Mob kills give faction XP** (to the faction of the run), **not job XP** (✔). **Mobs drop nothing**, only
mini-bosses and bosses give loot (✔ round 19).

### 7.4 Admin setup (editor)
Setup is done once per dungeon **type** on an editor copy; positions are stored **relative to the build's
origin**, so every copy uses the same setup. The content goes to `dungeons/<type>.yml` (versioned, not in
the database).
✔ Round 21: **one command family for private dungeons and city zone events** (C41); `<name>` is the
dungeon (one build + its setup), `<dungeon|city>` its kind (rules profile).
```
/dungeon create <dungeon|city> <name>              new dungeon of that kind
/dungeon template set <name> <structure>           paste the build in the editor area
/dungeon spawn add <name> [radius]                 spawn circle centre = your position (radius default in yml; 0 = exact point)
/dungeon spawn list|remove|radius <name> ...       manage the circles (several per dungeon)
/dungeon zone create <name> <zone> <wave|miniboss|boss>   inner area = pos1/pos2 (wand or look)
/dungeon zone outer <name> <zone> <radius>
/dungeon zone spawn add|clear <name> <zone>        mob spawn point = your position
/dungeon wave add|remove <name> <zone> [index]
/dungeon wave mob add|remove <name> <zone> <wave> <mob|boss:<id>> <count>
/dungeon zone show <name> [zone]                   particle outlines of inner and outer areas
/dungeon doctor <name>                             full check (C40); replaces "validate"
/dungeon publish <name> [copies]                   paste the K play copies on the grid (doctor must pass, gap checked, §7.1)
/dungeon list | info <name> | delete <name>
```

### 7.5 Entry (✔ rounds 18–19)
1. The dungeon is **open** (schedule on the faction server, Ominous keys still force-open).
2. On the faction server, each player right-clicks the **entrance NPC** (small safe zone), puts **their own
   key** in the slot and validates. Refused if: in combat, no faction, carrying rubies, the run is full (8),
   **this player's cooldown for this dungeon is running**, or **this player already did 3 runs today**.
3. ✔ **One run per faction per dungeon at a time.** The first player of a faction creates the run; members
   of the same faction **join it mid-run** while it is active and has room. **Everyone arrives at the same
   start spawn.**
4. The key is consumed when the dungeon server confirms the player arrived; the daily count goes up then.

### 7.6 Cooldown and daily cap (✔ round 19)
- **Cooldown per player per dungeon:** `dungeons.yml > cooldown_hours: 3` after the run ends for that player
  (boss killed, run timed out, or left by choice). Stored on the **player's UUID** (C28).
- **Daily cap:** **3 runs per player per day** (`daily_runs: 3`), also on the UUID; matches the Jokeyrini
  key cap.

### 7.7 Timeouts, AFK, exit (✔ round 19)
- **Run idle timeout:** nobody inside for **5 min** → the run ends and counts as **finished** for every member
  of the faction that started it (cooldown starts, no boss rewards, earned XP kept). Disconnected players in
  their reconnect window count as inside (✔ round 20).
- **AFK:** not moving for **5 min** → sent back to the faction server (✔).
- **Leaving by choice** (exit item or command): **loot and earned XP kept**, no boss reward, and **the
  player's cooldown for this dungeon starts** (✔).
- **Boss killed** → `boss_exit_delay_seconds` → everyone back to the saved position.

### 7.8 Moving the inventory (✔ rounds 18–19)
**User's plan:** the inventory the player has before entering goes with them to the dungeon server; when the
run ends, the dungeon server sends the current inventory (with the loot) back and clears it before the
player leaves.

✔ Round 21: the handoff becomes the shared protocol of
[`cross-server-items.md`](cross-server-items.md) (no duplication by design, and the **travel bag**
proposal: only hotbar + armour + off-hand + bag travel, OQ 98). The text below is the round 18–19 version.

Implementation: a `dungeon_handoffs` row per player (inventory, armour, off-hand as `ItemBytes`, return
position, state). The faction server writes it and clears the player before the transfer; the dungeon
server loads it on join and writes it back before the player leaves; the faction server restores it on
arrival. **Only the server named in the row's state may change it** (one transaction, version check), so
the same items can never exist on both servers. No rubies enter (ledger stays on the faction server). The
ender chest stays on the faction server.

- **Death** ✔: **keep inventory**, nothing drops (players or mobs), respawn at the start spawn. Armour and
  tools **lose durability and can break** as usual. The **drop key is disabled** on the dungeon server.
- **Disconnect** ✔: **10 minutes** to reconnect and get back into the run; after that (or when the run ends)
  the inventory is written back to the faction server and the player is out. ✔ Round 20: the inventory is
  **always sent back, never deleted**.
- **Crash** (proposal kept): the dungeon server saves the row every minute and at each zone completed; if it
  crashes, the faction server restores the last saved copy (lose at most a minute of loot, never duplicate).
- **Ticket expiry inside** (proposal kept): the proxy sends the player to the hub; the dungeon server writes
  the inventory back; the faction server restores it at the next valid login.

### 7.9 Rewards outbox
The dungeon server never writes faction tables. It writes `dungeon_results` (faction, XP, and for an event:
zone, power scores, winner) as it goes; the faction server applies them (LISTEN/NOTIFY + a poll every 10 s).
Loot is already in the returning inventory.

### 7.10 Proxy and deployment
Proxy (`../hatlas-proxy`): new backend `dungeon-1`, ticket gate and expiry cover it, a direct join without a
handoff is refused, a `hatlas:transfer` channel. Compose: service `dungeon` (heap ~3 G); **the RAM kit is
installed** (✔ user, 2026-11-12), so it fits. Tests on the proxy test stack with a `dungeon` backend.

---

## 8. Code split (✔ round 19)

**Confirmed:** a separate **`hatlas-dungeons`** Paper plugin and a **`hatlas-common`** library, included with
a **Gradle composite build** (`includeBuild("../hatlas-common")`, shaded into each plugin jar). Both repos go
into the `play-hatlas-net` organization and `CLAUDE.md` §1.1 (planned, not created yet).

| Piece | Faction server | Dungeon server | Goes to |
|---|---|---|---|
| Fight-zone engine (zones, waves, remembered mobs, power score) | no (round 19: events run on the dungeon server) | private runs and events | `hatlas-dungeons` (move to common only if the faction server needs it later) |
| Boss framework + BetterModel glue | no | yes | `hatlas-dungeons` (same remark) |
| Custom items (keys, siege items, amethyst, Magic reroller…), `ItemBytes` | yes | loot | **`hatlas-common`** |
| GUI framework + skins | yes | yes | `hatlas-common` |
| Job skill effects (attributes, listeners) | yes | yes (read-only from DB) | `hatlas-common` |
| Handoff (`server_handoffs`, dungeon **and mining**), results and cooldown contract | writer/reader | reader/writer | `hatlas-common` |
| Factions, crystals, claims, jobs, shops, cities, economy, event schedule | yes | **no** | `hatlas` |
| Instances, copies, editor commands, AFK/timeout rules | no | yes | `hatlas-dungeons` |

Round 20 adds a third plugin, **`hatlas-mining`** (mining server), on the same `hatlas-common`
([`mining-world.md`](mining-world.md) §6).

Why: the dungeon server **cannot** start a faction manager or save faction data by mistake; it deploys and
restarts on its own; its config stays small.

---

## 9. Build order = the launch plan (✔ round 19: everything at launch; ✔ round 20: beta after each epic)

| Epic | Content | Then |
|---|---|---|
| **1. Foundations + jobs** | `hatlas-common` skeleton, GUI skin framework, `gui-art` skill/agent; jobs without a faction, job XP from quests, **job skill trees** (generated per §3.4–3.6 of [`job-skills.md`](job-skills.md)), Wizard NPC + Alchemist *Magic reroller*, shop Workshop, job switch price; Jokeyrini per NPC + key cap | internal tests |
| **2. Dungeons** | `hatlas-dungeons`: fight zones, bosses + BetterModel pilot, copies, handoff, outbox, cooldowns, proxy `dungeon-1` | **beta** |
| **3. Mining world** | `hatlas-mining`, handoff/ledger to common, ore pass, reset, entrances, ore zones removed, mining map ([`mining-world.md`](mining-world.md) §8) | **beta** |
| **4. Cities** | cities, zones, events (last hit, spawn circles, play hours), Mayor, rewards, skins, holder mine entrance | **beta** |
| **5. Launch** | load test with 40 bots across faction, dungeon and mining servers, then open | — |

---

## 10. Open questions (mirrored in `CLAUDE.md`)

- 45–59 ✔ (rounds 18–19). 53 obsolete (round 20: no ore zones on the faction server).
- 60 ✔ PvP on, no key, max 4 per faction, random spawn in an admin-set circle (radius 8). 61 ✔ play hours
  (Europe/Paris), announcements 30/15/5 min, timeout 60 min, all in yml. 62 ✔ a city changes hands only when
  another faction holds more than half. 63 ✔ last hit. 67 ✔ disconnected = inside for 10 min; inventory
  always sent back. 68 ✔ mining world ([`mining-world.md`](mining-world.md)). 69 ✔ tiers and factors as
  proposed, all in yml, no free teleport, skins added. 70 → clarified in C35, now OQ 76.
- 71 ✔ (round 21) 5 s protection, no PvP between allies, free slot taken by another member, rejoin after
  60 s (yml), several spawn circles, radius in yml, never spawn in a block, `/dungeon doctor`. 72 ✔ credit
  rules, 30 > 25 intended, ties holder then first, timeout holder keeps (C39). 76 ✔ personal roll + last-hit
  bonus roll, participant = dealt damage, full inventory → drop at the feet. 77 ✔ skins while holding, one
  set per city.
- **85** Rejoin after 60 s lets a player restock at home (C42): keep 60 s (recommended), longer, or only after
  a disconnect?
- **86** One spawn circle per faction in city events (factions spread over the circles) (recommended)?
- **87** Unified `/dungeon create <dungeon|city> <name>` with rules profiles in `dungeons.yml > kinds`, city
  zone linked by `/cityzone create <zone> <city> <dungeon>`, legacy `/donjon` removed with the dungeon epic
  (recommended)?
- **88** Participant: any damage counts, no minimum, **+ assists** (a heal or taunt on a player who hit)
  (recommended)? Item dropped at the feet **locked to its owner**, lost if left behind (recommended)?
- 73–75 and 89–91: job questions, in [`job-skills.md`](job-skills.md) §8. 78–84 and 94–97: mining world, in
  [`mining-world.md`](mining-world.md) §10. 92–93: [`economy-observatory.md`](economy-observatory.md).
  98–99: [`cross-server-items.md`](cross-server-items.md).
