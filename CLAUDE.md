# CLAUDE.md

This file guides Claude Code (claude.ai/code) when working in this repository.

> **Working agreement for Claude**
> 1. **Read this file fully at the start of every session.** It is the source of truth for project goals, features and known issues.
> 2. **Every time you modify the project, append an entry to [`docs/claude-changelog.md`](docs/claude-changelog.md)** (date, branch, what changed, files touched) and update any section that is now out of date.
> 3. **When a request is vague or a design choice isn't settled, add it to [Open Questions](#open-questions)** and ask the user, instead of guessing. Move answered questions into the relevant feature section, marked `✔ answered <date>`.
> 4. For Paper API questions, use the `papermc-docs` MCP server (`.mcp.json`) or the 1.21.11 Javadocs at `https://jd.papermc.io/paper/1.21.11/`.
> 5. **When a feature is finished (its PR is opened), the player wiki is updated by the `wiki-writer` agent**, started in the background by the `wiki-on-feature` hook (§2). Review its edits, commit them as `docs(wiki): …` on the feature branch and push. Never skip it for a PR that changes `src/main/`.
> 6. **A feature is only finished when its in-game suites pass.** Before `gh pr create`, the `ingame-gate` hook (§2) denies the PR until the `ingame-tester` agent has written a PASS verdict for the change. When denied, run that agent in the foreground with the features it names, fix any FAIL, commit (incl. new scenarios), then retry. `WAIVED` only when the user explicitly says to skip.
> 7. **This is the control repo of the whole Hatlas network** (✔ user, 2026-11-08): this session coordinates every project of §1.1, merges their PRs in a sensible order, and owns the cross-repo contracts. Other sessions may work in the sibling repos, but decisions and merges are regrouped here.

---

## 1. Project Overview

`hatlas` ("Hatlas") is a **PaperMC 1.21.11 plugin (Java 25)** that turns a survival server into a **faction-war progression game**. Group `org.minecraft`, artifact `hatlas`, version `1.0-SNAPSHOT`, root package `org.minecraft.hatlas`.

> **Renamed 2026-11-07:** the project was called **Atlas** (`play.mc.atlas`, package `org.minecraft.atlas`, plugin `atlas`). Everything is now **Hatlas** (`org.minecraft.hatlas`, plugin `hatlas`, data folder `plugins/hatlas`, permissions `hatlas.*`, command `/hatlas`, persistent-data keys `hatlas:*`, database/user `hatlas`, `HATLAS_DB_PASSWORD`; the in-game **Hatlas Crystal**). `migration/LegacyAtlas` upgrades an old install on first start: it moves `plugins/atlas`, renames `atlas_schema_version`, renames `atlas:*` keys on entities (when they load), players (on join), opened containers and stored items, and still reads `ATLAS_DB_PASSWORD`. Not migrated: permission nodes in a permission plugin, items inside shulker boxes/bundles. Checked in game on the old test baseline (folder, table, keys, NPC menus). The local folder is to be renamed `../hatlas` by the user after the merge. Minecraft's *block atlas* (resource-pack textures) is unrelated and keeps its name.

### Gameplay goals
- **Factions are the core.** Every progression system feeds into a faction's shared XP pool. The faction levels up (0 → 99), earns **Skill Points**, and spends them in the **Hatlas Crystal** GUI (HP, claims, chests, protections, homes, vault, outpost).
- **Territory is defended by Hatlas Crystals** (ender crystals with custom HP). Destroying an enemy's last crystal disbands that faction.
- **Rubies are the economy.** Ruby gems are mined in Ore Zones, kept in a ruby-only faction vault, used to pay at Shops and on the Auction House, and dropped when a crystal's protection breaks.
- **PvE progression** goes through Jobs (daily quests), Jokeyrini (hard quests that give Donjon Keys) and Donjons (wave dungeons with a boss that give big faction XP and siege items).
- **PvP/raiding** goes through siege items from donjons (Raider's Pickaxe, creeper eggs, TNT), the combat-log penalty, faction golems and a locator bar that shows faction members only.

Player-facing docs: `WIKI.md` (EN) and `WIKI-FR.md` (FR). Some values there are out of date; see [Open Questions](#open-questions).

### 1.1 The Hatlas network: projects controlled from here

All repos are in the GitHub organization **`play-hatlas-net`** (moved there by the user 2026-11-08), cloned side by side:

| Repo | What | Own tests | Merge style |
|---|---|---|---|
| `hatlas` (this one) | Paper plugin of the faction server; schema `hatlas`, `web_*` views; `docker/postgres` (DB + roles init script) | in-game gate on the Hatlas test server (§2) | merge commit |
| `../hatlas-proxy` | Velocity plugin: `/link`, ticket gate, expiry back to the hub, `web.presence` | JUnit + in-game on its own **test stack** (`scripts/test-stack.ps1`; `hatlas on` = full chain with this plugin) | merge commit |
| `../hatlas-hub` | Paper plugin of the hub: selector compass, server menu (players online, access status), no drop | JUnit + in-game on the proxy test stack (`scripts/stack.ps1 deploy`) | merge commit |
| `../hatlas-webapp` | SvelteKit website (accounts, link page, Stripe tickets, dashboard); owns schema `web` | GitHub Actions CI (lint, typecheck, unit, build, e2e, migrations, docker) | squash |
| `../ovh-ddns` | Container updating the OVH A record `play.hatlas.net` (dynamic IP), kept in production ([`docs/deployment.md`](docs/deployment.md) §2.5) | none | — |
| `../hatlas-common` (**planned**, ✔ 2026-11-12) | Java library shared by the Paper plugins (items, GUI framework + skins, job skill effects, handoff/results/cooldown contract), **Gradle composite build**, shaded into each jar | JUnit | — |
| `../hatlas-dungeons` (**planned**, ✔ 2026-11-12) | Paper plugin of the dungeon server (copies, fight zones, bosses, city zone events), plan [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) | JUnit + in-game on the proxy test stack | — |
| `../hatlas-mining` (**planned**, round 20, 2026-11-13) | Paper plugin of the **mining server** (daily-reset cave map, ruby and vanilla ores, entrances/landings, no PvP), plan [`docs/mining-world.md`](docs/mining-world.md); replaces the ore zones of `hatlas` | JUnit + in-game on the proxy test stack | — |
| `../landing-website` | Static landing page (nginx + certbot today); replaced by Caddy, content to move into the website ([`docs/deployment.md`](docs/deployment.md) §2.3) | none | — |

**Cross-repo contracts** (change them only from here, then update every side): `web.tickets` (`docs/access.md`), `web.link_codes` and `web.presence` (hatlas-proxy `db/web-schema.sql` ↔ webapp migrations), `hatlas.web_*` views (`docs/storage.md` §5, `docs/economy.md`), database roles (`docker/postgres/init/10-roles.sh` ↔ webapp Decision 6), the website URLs used by the plugins (✔ user 2026-11-08: `https://play.hatlas.net/link` and `https://play.hatlas.net/renew`), player identity and login (`web.game_accounts`, `web.auth_requests`, `web.deleted_accounts`, planned in [`docs/identity.md`](docs/identity.md)).

**Merge order rule:** contracts and providers first (Hatlas views / roles, then the proxy, then the hub), then the website; Dependabot PRs only with a green CI; a PR rebased on newer work needs a new campaign before merge.

**Deployment** (✔ user, 2026-11-08): one private machine behind the user's router, no SSH from outside. Everything runs with docker compose; the user updates by hand with scripts on the machine: the website with `hatlas-webapp/deploy/update.sh` (planned), the game servers with a script to write here (plugin jars, backup first with `scripts/backup/hatlas-backup.sh`, announced restart). k3s was considered and rejected for one machine.

---

## 2. Build, Run, Tooling

```bash
./gradlew build        # compile + package the plugin JAR (build/libs)
./gradlew assemble     # build without tests
./gradlew compileJava  # fast compile check (use after every change)
./gradlew runServer    # local Paper 1.21.11 test server in ./run (2 GB heap)
```

- **No automated tests.** Check changes with `compileJava`, then manually on `runServer` (or the `paper-ingame-test` skill with offline bots).
- **Java 25** (LTS) toolchain and **Gradle 9.9.0**, the same as `../hatlas-proxy`; the foojay resolver downloads a JDK 25 if none is installed (IntelliJ's are in `~/.jdks`). Paper 1.21.11 runs on Java 21+, but the jar now needs **Java 25 at runtime**.
- Gradle plugins: `java-library`, `xyz.jpenilla.run-paper 3.0.2`. Repos: Maven Central, PaperMC, CodeMC.
- Dependencies (both `compileOnly`): `io.papermc.paper:paper-api:1.21.11-R0.1-SNAPSHOT` and `com.github.retrooper:packetevents-spigot:2.14.0`. **packetevents must be installed on the server as its own plugin.** It is declared as a required `server` dependency (`load: BEFORE`, `join-classpath: true`) in `paper-plugin.yml`.
- Descriptor: **`src/main/resources/paper-plugin.yml`** (Paper plugin, not `plugin.yml`), `load: POSTWORLD`, `api-version: '1.21'`, `loader: org.minecraft.hatlas.HatlasLoader`. All permission nodes are declared there.
- Database drivers: **SQLite** uses the `sqlite-jdbc` that Paper ships on the server classpath (no dependency). **PostgreSQL**'s driver (`org.postgresql:postgresql:42.7.7`) is downloaded at startup by `HatlasLoader` (Paper `MavenLibraryResolver`) **when `storage.type: postgresql`** (the default, so also on a first start without `config.yml`). A `runServer` dev server can set `storage.type: sqlite` to run without PostgreSQL.
- **Local PostgreSQL:** `docker compose -f docker/postgres/docker-compose.yml up -d --wait` (password in the git-ignored `docker/postgres/.env`, see `.env.example`). Usage and test recipe: `docs/storage.md` §4.
- `run/` (test server and world) is git-ignored. **No world or map save is committed.**
- **Boss pipeline** (round 22): skill `.claude/skills/boss-building/SKILL.md` + agents `boss-designer` (Fable), `boss-modeler` (Fable, pilot), `boss-animator`, `boss-sound`, `boss-coder` (Opus) and the existing `ingame-tester`; one folder per boss in `bosses/<dungeon>/<boss>/` (refs, `boss.yml`, `.bbmodel`, sounds), user gate after each step. Pilot: `bosses/dark_forest/fungal_root/`, waiting for the user's reference images.
- **Map pipeline** (planned): brief `worldgen/map.md`, skill `.claude/skills/map-building/SKILL.md` (WorldPainter driven by scripts, agents per step, BlueMap), generated outputs in git-ignored `worldgen/out/`.
- MCP: `.mcp.json` declares `papermc-docs` → `https://gitmcp.io/PaperMC/docs` (GitMCP view of the PaperMC docs repo) and `vitaminmcp` (`cmd /c npx -y vitaminmcp@3.2.2`, pinned; bots + server observation for in-game tests).

### In-game test server (used by the `paper-ingame-test` skill)
- `TEST_SERVER_DIR=C:\Users\lloyet\Documents\Projects\servers\minecraft-paper1.21.11` (outside the repo, not in git). `PLUGIN_NAME=hatlas`. **Disposable: test world only, no real data, no real players** (✔ 2026-11-07), so tests never back up or restore anything. Runs `online-mode=false`: anyone who reaches the port can join under any name.
- Hatlas there runs on **PostgreSQL** (`docker/postgres`, database `hatlas_test`), like production will (M2). Its Hatlas config is `scripts/test-world/hatlas-config.yml` (PostgreSQL + AFK kick off).
- Control script (Windows, PowerShell 5.1): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/test-server.ps1 <action>`. Reads `MC_RCON_PASSWORD`, `HATLAS_DB_PASSWORD`… from `.env` / `docker/postgres/.env`.
  - `start|stop|restart|status|console "<cmd>"`, `deploy` (gradle build → replace `plugins/hatlas-*.jar` → restart). Stop goes through RCON so `onDisable` saves data; the script never kills the process. `start` also starts the database.
  - **`reset`**: restores the **baseline** (worlds + `plugins/hatlas` + a `pg_dump` of `hatlas_test`, kept in `<TEST_SERVER_DIR>\baseline`) and starts (~25 s). Run before every test campaign or after a run left a mess.
  - Building the baseline (only when the map, `fixtures.json` or the setup change): `rebuild-from-map` (raw map from `run/world`, empty DB, structures installed), `node scripts/test-world/build-setup.mjs`, connect bot `Builder`, `run-console src/test/ingame/_setup/build-baseline.json`, check, `baseline`. Also `db-up`, `install-structures`.
- **Test world** (✔ Open Questions 10/15): the user's map (`run/world`, git-ignored) + the setup, named in **`src/test/ingame/fixtures.json`**:
  - safe zones `spawn` (world spawn -4956 80 -3044; 9 job/quest/smuggler/explorer/auction NPCs) and `city` (210 chunks, shop house `miner_shop`, ore zone `city_mine` inside it, mineable because ore zones win over safe zones);
  - donjon `dark_forest` (map build, type `trial`, vault -4985 86 -2994) and a **structure gallery** at x -6400…-5969, y 200, z -3200: the 7 `.nbt` placed with `/place template hatlas:<name>`; `desert/nether_castle/ocean/plain_gallery` are registered donjons, `sky_donjon` has no vault (gallery only), `world_spawn` is the spawn build;
  - `sandbox` (x 1000, z 1000) for scenarios that build their own setup. Gamerules: no mob/patrol/trader spawning, fixed day and weather.
- Scenarios use `{{fixture.path}}` placeholders, rendered by `node scripts/test-world/render.mjs <file>` before `bot_run_scenario`.
- **Never `/reload`.** Always restart.
- The server runs on **JDK 25**: `test-server.ps1` uses `TEST_SERVER_JAVA`, else the newest JDK 25 in `~/.jdks` (the `java` on PATH is 21). `deploy` also removes a leftover `atlas-*.jar`.
- Server plugins: hatlas, packetevents 2.14.0, VitaminMCP (`read-only: false`), OldCombatMechanics.
- Bots: offline names `Tester1`, `Tester2`… (`Builder` for the setup). Hatlas gotchas: most features need a faction first (`/f create` or `/f join <bot> <faction>` from console); disconnecting within `combat_log.timeout_seconds` of PvP kills the bot.

### Wiki automation (Open Question 12)
- **Skill** `.claude/skills/wiki-writer/SKILL.md`: how to write `WIKI.md` (EN) + `WIKI-FR.md` (FR) for players. Sources: code, shipped `src/main/resources/*.yml`, `paper-plugin.yml`. Both files kept in sync, no internals, admin commands left out.
- **Agent** `.claude/agents/wiki-writer.md`: preloads the skill, may only edit the two WIKI files, read-only Bash (`git diff/log/show`, `gh pr view`), never commits.
- **Hook** `.claude/settings.json` → PostToolUse on `Bash(gh pr create*)` runs `.claude/hooks/wiki-on-feature.mjs` (Node). If a segment of the command really is `gh pr create`, its stdout has the new PR URL, and the diff of the PR's `--head/-H` branch (default: the checked-out branch) against its `--base` (default `main`) touches `src/main/`, it injects context asking the main session to launch `wiki-writer` in the background (in a worktree of that branch when it is not checked out). Otherwise it does nothing.
- `.gitignore` now versions `.claude/settings.json`, `agents/`, `skills/` and `hooks/` (so `paper-ingame-test` is versioned too); `settings.local.json` stays personal.

### In-game test gate (Open Question 20)
- **Suites:** `src/test/ingame/<feature>/<case>.json` (step arrays for VitaminMCP `bot_run_scenario`), `*-before-restart.json` / `*-after-restart.json` pairs for persistence. Format, conventions and pitfalls: `paper-ingame-test` skill, section "Suites de scénarios du projet Hatlas".
- **Map:** `src/test/ingame/features.yml` (feature → globs; `shared` globs run all suites). Selection is per feature (✔ Open Question 17). `node .claude/hooks/affected-features.mjs --base <branch>` prints the affected features, `uncovered` src/main files and `missingSuites`.
- **Agent** `.claude/agents/ingame-tester.md`: writes missing scenarios, resets and deploys the test server (§2), runs the suites, writes the verdict `.claude/state/ingame/<sha>.json` (git-ignored), then **stops the test server** (clean RCON `stop`; the PostgreSQL container stays up) unless told to keep it running.
- **Hook** `.claude/settings.json` → PreToolUse on `Bash(gh pr create*)` runs `.claude/hooks/ingame-gate.mjs`: no feature touched → allowed; otherwise needs a PASS/WAIVED verdict covering every affected feature, for the PR's head (`--head/-H` branch, else the checked-out HEAD) or for an ancestor of it with identical `src/main/`, and (for the checked-out branch) no uncommitted `src/main/` change. `--base origin/main` and `main` are the same. Both hooks judge the `--head` branch's own content (feature map, suites, diff), so a PR from a worktree or another branch is checked correctly (fixed 2026-11-07). Else the call is denied with the exact agent prompt to run.

---

## 3. Architecture

### 3.1 Entry point: `Hatlas.java`
`Hatlas extends JavaPlugin`, singleton `Hatlas.instance`. Its `onEnable()` runs these steps in order:
1. Registers `LocatorBarListener` with the packetevents API.
2. Loads the tuning YAML files (see §5) into `public static YamlConfiguration xxxConfig` fields (`loadTuning`), copies new `config.yml` defaults (e.g. `storage`), and calls the managers' `loadConfig(...)` and `init()` methods (keys, item registries, recipes).
3. **Storage** (`storage/`, see [`docs/storage.md`](docs/storage.md)): `Storage.start()` opens the backend chosen in `config.yml > storage` (sqlite | postgresql), imports the `*-data.yml` files once into a fresh database, and loads every domain. If this fails, the plugin disables itself (nothing is written).
4. Registers one snapshot supplier per domain, then calls each manager's `restore(...)` in dependency order (factions → crystals → … → shops), then `Storage.markReady()` (writes allowed from here on, autosave started).
5. Registers 18 listeners (incl. `AfkManager`, `CombatLogListener`, `ResourcePackManager`, which are listeners themselves) and calls `ResourcePackManager.sendToAll()`.
6. Starts the schedulers: Golem, Crystal, Donjon, Quest expiry, ItemClear, Afk, CombatLog, ClaimBorder, NpcLook, OreZone, Shop.
7. Registers the Brigadier commands through `LifecycleEvents.COMMANDS`.

`onDisable()` sets `CombatLogManager.setShuttingDown(true)` first, then `Storage.shutdown()` (waits for pending async writes, then saves every domain synchronously).

### 3.2 Conventions
- **Static managers** hold in-memory state with static methods (`FactionManager.getFaction(name)`). There is no DI and no instances.
- **Config vs data split:** `xxx.yml` holds tuning and is shipped in resources (`saveResource` if missing). Runtime state goes through the **storage adapter**: managers keep their in-memory state and expose `snapshot()` (immutable records from `storage/model`) and `restore(data)`. To persist after a mutation, call `Storage.save(DataDomain.X, …)` (async, one transaction). **Never write `*-data.yml` files directly**, and always save `FACTIONS` and `CRYSTALS` together. Autosave runs every `storage.autosave_minutes`.
- **Items in storage** are serialized with `ItemBytes` (Paper `serializeAsBytes`, version-safe), on the main thread only.
- **Brigadier:** each command class has a static `build()` returning `LiteralCommandNode<CommandSourceStack>`. Helpers `error()/success()/info()` return red/green/gold `Component`s.
- **Adventure API only** (`Component`, `NamedTextColor`). Never use legacy `ChatColor`.
- **PDC** (`NamespacedKey`) tags custom entities and items. Keys are lazily created static fields on the owning manager.
- **Custom items** use data components (`ITEM_MODEL` = `hatlas:<id>`, `ITEM_NAME`, `LORE`, `EQUIPPABLE`) on a vanilla base material. Identity is checked through the `ITEM_MODEL` key (e.g. `RubyItem.isRubyGem`).
- **NPCs** are vanilla entities with `setAI(false)`, invulnerable and persistent, tagged in PDC. They persist with the world and are not saved to YAML (except shop NPCs). `NpcLookHelper` turns Smugglers and Explorers toward the nearest player.
- **GUIs** implement `HatlasGui extends InventoryHolder`. `GuiListener` routes click, close and drag to the holder. `GuiNavigator` keeps a per-player back stack (`push`/`back`/`pop`). The last slot is always the "Back" barrier (`finishGui()`). `GuiUtil` has the layout, format and pane helpers. Paper `Dialog` is used for text input (crystal rename).
- **Titles:** use `TitleUtil` (word-wraps to title and subtitle, never embeds `\n`).
- Use `ConcurrentHashMap` for state touched from async events (chat, AFK, combat).

---

## 4. Features

### 4.1 Factions (`faction/`, `FactionCommand`, `FactionListener`, `ChatListener`)
- **Model `Faction`:** name, `owner` (UUID, stored separately from `members`), members, `roles` (`FactionRole` = MEMBER < BANKER < MODERATOR < LEADER; there is **no OWNER enum value**), color (`NamedTextColor`), description, level, exp, skillPoints, allies, `outpostUnlocked`, purchased home/vault tier indices, vault size + contents, downgrade fields (legacy, unused).
- **Levels:** `FactionLevelManager.MAX_LEVEL = 99`. XP to level 1 = 100, then each level costs `ceil(prev × 1.09)`. Overflow carries over. Each level gives `skill_points_per_level` SP (default 1). XP sources are quest completion and donjon boss-damage share.
- **Permissions by role:** spend the vault (take gems out of `CrystalVaultGui`, buy in a job shop or on the auction house) = owner or BANKER+ (`FactionManager.canSpendVault`; any member may deposit; ✔ answered 2026-11-07, Open Question 6); invite = MODERATOR+; kick = MODERATOR may kick BANKER/MEMBER, LEADER may kick MODERATOR/BANKER/MEMBER, owner may kick anyone; rename/description/color = LEADER+; promote/demote/transfer/disband = owner only (transfer turns the old owner into LEADER); claim, sethome, outpost, ally, sell on auction = owner or LEADER. A BANKER has no right other than spending the vault.
- **Creating a faction** (`/f create <name>`) spawns the **main crystal** at the player's position, claims that chunk, names it `main` and sets its home there. It is refused inside an existing claim, a donjon chunk or a safe zone.
- **Claims** (`FactionClaimManager`, runtime key `world:cx:cz`): a new claim must be side-adjacent to the faction's territory and needs a crystal with free `claimCapacity` (`findCrystalForClaim` picks the nearest one). Claims belong to a crystal and are persisted per crystal. `/f showclaim true|false` draws GLOW_SQUID_INK borders within 3 chunks (`FactionClaimBorderRenderer`).
- **Territory protection** (`FactionListener`): outsiders cannot break, place or interact in a claim. Exceptions: TNT placement, creeper spawn eggs, flint & steel or fire charge on TNT, and the **Raider's Pickaxe** (break only in enemy claims, consumes uses; anvils and smithing are blocked and it takes no durability damage). Entering or leaving a territory shows a title.
- **Allies:** requests are in-memory only (`pendingAllyRequests`). `areAllied()` requires both sides to list each other and treats the same faction as allied. Allies cannot hurt each other in donjons.
- **Faction chat formatting** (`ChatListener`): ops show in dark red, faction tag in the faction color. `/f msg` sends to online members only.
- **Leaving or losing faction membership** removes the player's job, removes secondary homes (main home is kept) and refreshes the locator bar.
- **Vault** (`FactionVault`, `CrystalVaultGui`): a **ruby-gem-only** shared inventory per faction. While a vault GUI is open, its inventory is the live vault: every `FactionVault` helper (payments, drops) and the FACTIONS snapshot pull from it first and push their change back (`CrystalVaultGui.pullLive/pushLive/pullAllLive`), so a purchase made while someone has the vault open is not undone on close (ruby duplication, fixed 2026-11-07). Non-ruby items are refused too. Members can deposit by click, shift-click, number key onto an empty slot or drag; only owner/BANKER+ can take items out. Default size from `vault.default_size`, can be expanded with the Vault skill. When a crystal protection breaks, `max(ceil(total × protection_break_drop_percent), protection_break_drop_min)` gems drop. All gems drop when the faction is disbanded through crystal loss. `/f balance` shows the gem count.
- **Admin/debug:** `/f level set`, `/f exp set|add`, `/f skillpoints set` (`hatlas.faction.debug`), `/f disband <faction>` (`hatlas.faction.admin.disband`), `/f join <player> <faction>` (`hatlas.faction.admin.join`).

### 4.2 Hatlas Crystal: core, skills, chests, outpost (`crystal/`, `Crystal*Gui`, `FactionListener`, `CrystalListener`)
- `HatlasCrystal` wraps an `EnderCrystal` with its own HP (`BASE_MAX_HP = 50`). State is split between entity PDC (hp, max_hp, immunity, bonuses, protections) and `factions-data.yml` → `crystals.<entityUUID>` (faction, name, hp, home, outpost flag, claimed chunks per world as chunk-key longs, chest sizes and contents, purchased and broken protections). Crystals in unloaded chunks stay as **stubs** (`isLoaded()==false`) and get reattached on `EntitiesLoadEvent`.
- **Nametag:** a TextDisplay showing `name [Faction]` / `LvL.x` / `hp/max ♥` / `IMMUNITY - [ready/total]` (aqua while immune, yellow while reloading).
- **Damage:** only enemy-faction players can damage a crystal, at most 1 hit/s per attacker. Non-entity damage is cancelled. Members are alerted. Regen is `regen_per_second + regenBonus` per second after `regen_timeout_seconds` without being hit.
- **When HP reaches 0:**
  - If a protection is available, the **longest** one is consumed: HP is refilled, the crystal becomes immune for that duration, a small explosion plays and vault rubies drop. Broken protections regenerate **one at a time, shortest first**. Each one's watch window is `crystal.protection_watch_multiplier × duration` after it broke (default 2: immunity + a regen window as long as the protection). If the crystal was hit during that window, the protection is **lost forever**.
  - If no protection is left, a big explosion plays and `destroyCrystal()` runs: the crystal's claims are removed, its chests drop, the faction loses `spentSkillPoints / skill_points_per_level` levels (an outpost also refunds the outpost cost) and its exp resets to 0. If the main crystal died, the outpost becomes main. If it was the last crystal, all vault gems drop and the faction is disbanded with a global broadcast.
- **Skills** (`CrystalSkillListGui` → `CrystalSkillConfirmGui`, tiers from `factions.yml > skills`):
  | Skill | Scope | Effect |
  |---|---|---|
  | `hp` | per crystal | +max HP, +regen/s |
  | `claims` | per crystal | +claim capacity |
  | `chest` | per crystal | new virtual chest (size 9/18/27/54) |
  | `protection` | per crystal | stockpiled immunity (minutes). Each duration can be bought once |
  | `homes` | faction | +1 personal home slot for every member (one-shot per tier) |
  | `vault` | faction | vault size upgrade (one-shot per tier) |
  | `outpost` | faction | unlocks a 2nd crystal through `/f outpost` (max 2 crystals) |
  A skill with no tiers in the YAML is hidden from the GUI.
- **CrystalMainGui** (right-click your own crystal) has: crystal list, faction info (click = promote this outpost to main, shift-click = rename dialog), color, chests, upgrades, vault, quests.
- `/crystal list`, `/crystal rename <old> <new>`. `/f home [crystal]` uses a countdown (`HomeTeleportManager`, `factions.yml > faction_home`). `/f sethome <crystal>` works only inside your own claim.

### 4.3 Jobs & daily quests (`job/`, `quest/`, `JobListener`, `Job*Gui`, `NpcJobSwitchGui`)
- `Job` enum: **MINER, LUMBERJACK, HUNTER, FARMER, ALCHEMIST** (playable) plus **JOKEYRINI** (pseudo-job, used only for Jokeyrini task templates and its NPC).
- You must be in a faction to get a job. You get it by right-clicking a job NPC (villager tagged `job_npc_type`, spawned with `/job npc spawn <job>`). Switching jobs resets your job data, and after a reset there is a **24 h cooldown** before you can pick a new one.
- **Job XP:** +1 per relevant action. Level-up needs `(level+1) × 64`.
  - MINER: ores, stone variants and glowstone. LUMBERJACK: logs and stems. FARMER: crops (`harvest_crop`), sugar cane and kelp, sweet berries, glow berries. HUNTER: kills (`kill_entity`). ALCHEMIST: only `brew_potion` (brewing-stand pickup) and `craft_item` (✔ decided 2026-11-07, Open Question 7; its old kill tasks and 3 never-progressing `break_block` gather tasks were replaced by brew/craft tasks).
- **Daily quests** (`QuestManager`): every `daily_reset_hours` you are offered 3 quests, each with 1–2 tasks at random difficulty 1–4. You can select **2**. Selecting a new day's offer clears your active quests.
  - Task amount = `BASE[d] + jobLevel × PER_LEVEL[d]` (Hunter ×0.9). Time limit is 15/30/60/120/180 min for difficulty 1–5, summed across the quest's tasks. Item rewards are scaled (Hunter ×1.1).
  - Faction XP = `exp_base_reward × Σ(difficulty × expMultiplier) × √(factionLevel+1)`.
  - `jobs.yml` has 85 job tasks (16 per job) with action types `break_block`, `kill_entity`, `harvest_crop`, `craft_item`, `brew_potion`, plus the `jokeyrini.tasks` pool.
- `/quest` opens `JobMainGui`. `/job level` shows progress. Admin: `/job set|remove|level add/set/remove|npc spawn`.

### 4.4 Quests with NPC: Jokeyrini (`JokeyriniManager`, `JokeyriniQuestGui`)
- A Wandering Trader NPC (`/job npc spawn jokeyrini`, PDC `jokeyrini_npc`). Requires a faction.
- One offer per `jokeyrini.daily_reset_hours`: 2–3 tasks at difficulty 3–4, or with `special_quest_chance` (0.15) a **Legendary** quest of 3 tasks at difficulty 5. Progress shows in the action bar with a `[Jokeyrini]` prefix and works whatever your job is.
- Reward: **Donjon Trial Keys**. Max difficulty 3 gives 1, 4 gives 2, 5 gives 3.

### 4.5 Donjons (`donjon/`, `DonjonCommand`, `DonjonListener`, `DonjonListGui`)
- **Instance `Donjon`:** id, name, type (key in `donjons.yml > types`), world, level 0–99, `DonjonRarity`, `DonjonStatus` (**IDLE / ACTIVE only**), protected chunks (chunk-key longs), wave spawn points (id → loc), vault block (the trigger), teleport spawn, nametag TextDisplay, waves, boss damage per faction.
- **Admin setup:** `/donjon create <type> <name>` claims the current chunk. Names are unique and every `<id>` argument also accepts the name (case-insensitive). Then use `claim/unclaim/unclaimall`, `set spawn`, `set vault [x y z]` (the given block, or the one you look at), `wavespawn add/list/delete/clear`, `set difficulty|rarity`, `doctor <id>` (checks vault, teleport spawn and wave spawns), `activate|deactivate|reset|tp|delete|list|info`, `give <player> key|ominouskey [lvl] [rarity] [n]|creeper_egg|powered_creeper_egg|raider_diamond_pickaxe`, `npc summon smuggler`.
- **Schedule:** every `activation_interval_hours` a random idle donjon is activated (up to `max_active_donjons`) with a weighted level (`difficulty` ranges) and rarity (`rarity` weights). An active donjon times out after `idle_timeout_hours`, with a warning 1 h before.
- **Starting a run:** right-click the **vault block**.
  - On an ACTIVE donjon, a Donjon Key (Trial or Ominous, PDC `donjon_key_marker`) starts it. An Ominous key overrides the level and rarity.
  - On an IDLE donjon, only an **Ominous Trial Key** works. It force-activates the donjon with the level and rarity stored on the key.
- **Waves:** the number of waves and mobs per wave scale with level. HP and attack multipliers scale with level, and the boss wave gets extra boss multipliers. Mobs spawn round-robin across spawn points. Special mob tokens are `BABY_ZOMBIE` and `CHICKEN_JOCKEY`. After a wave there is a 5 s pause. When 5 or fewer mobs are left they glow.
  - Only kills by a player, or by a different mob, count. Environmental deaths respawn the mob.
  - Slime and magma splits and zombie→drowned conversions keep being tracked.
  - If no player is inside, the run resets (checked every 2 s).
- **Completion:** total XP = `(min_exp + level/99 × (max_exp−min_exp)) × rarity multiplier`, shared by **boss damage per faction**. The top damager gets the broadcast. Drops at the anchor:
  - creeper eggs and TNT (`1 + level/99 × (rarity+1)`)
  - rare chance of a powered creeper egg (0.5%–3%)
  - wither skulls for EPIC+
  - a chance of an Ominous key for EPIC+
  - boss loot from `boss_drops.<rarity>` (`BossDropConfig`, which can include a powered egg or a Raider pickaxe level)
- **Rarities:** COMMON ×1, RARE ×1.5, EPIC ×2.5, LEGENDARY ×5, MYSTIC ×10, GODDESS ×20.
- **Types in `donjons.yml`:** trial, desert, nether_castle, plain, sky, ocean.
- **Protection in donjon chunks:** non-admins cannot break, place, empty buckets or use interactive blocks. Explosions are filtered. Allied factions don't damage each other. Vanilla drops and XP from donjon mobs are cleared.
- **Locator / navigation:**
  - The **Smuggler** NPC (Illusioner, PDC `smuggler_npc`) opens `DonjonListGui` ("Smuggler's Chart"), which shows a countdown to the next activation and teleports you to donjons you have visited, with a cooldown of `smuggler_teleport_cooldown_seconds`.
  - Entering a donjon chunk records a visit and shows a title.
- **Siege items:**
  - `RaiderPickaxe`: Raider I/II/III gives 5/10/20 breaks in enemy claims.
  - `ElectricalCreeperManager`: the Powered Creeper Egg spawns a charged creeper. 3 charged explosions break 1 obsidian block (hit map is in memory only).
- **The 7 `.nbt` files in `resources/structures/` are storage only**: saved arena/donjon builds kept so they can be imported onto a server (e.g. with `/place template` or a structure block). No Java code loads them, and none should be added unless requested. (✔ answered 2026-11-05)

### 4.6 Ore Zones (`orezone/`, `OreZoneCommand`)
> **Planned removal** (round 20, 2026-11-13): mining moves to a dedicated mining server (`hatlas-mining`, [`docs/mining-world.md`](docs/mining-world.md)); `orezone/`, `orezones.yml` and the OREZONES domain leave `hatlas` in that epic.
- Cuboid regions refilled every `interval_reset_hours` with a weighted roll per block over `OreType` (diamond, gold, emerald, iron, copper, coal, **stone**, **ruby**). Ruby is placed through `RubyBlockManager`.
- Admin: `/orezone pos1|pos2 [x y z]` (the given block, or the block you look at, up to 100 blocks), `add <name>`, `remove`, `reset`, `list`. New zones copy `default_ore_weights`. Weights per zone are saved in `orezones-data.yml`.
- Status: verified in game (refill and STONE weights, PR #22; `city_mine` suites on the test world, PR #34). Default weights put stone at 75 %. Ore zones win over safe zones for mining (PR #33).

### 4.7 Safe Zones (`safezone/`, `SafeZoneCommand`, `SpawnCommand`, `SafeZoneListener`, `SafeZoneGui`)
- Named sets of chunks with an optional spawn point and description.
- **Inside a safe zone:** players take no damage, players inside cannot hit players outside, blocks cannot be broken (**except inside an ore zone**: ore zones win over safe zones, so an ore zone can sit in a city; ✔ decided 2026-11-07) or interacted with, and explosions skip safe-zone blocks. Factions cannot be created, claimed or outposted there.
- Entering a zone records a visit. The **Explorer** NPC (Illusioner on a Camel, `/safezone npc summon`) opens `SafeZoneGui`, which teleports you to zones you have visited.
- `/safezone tp <name>` and `/spawn` (= `/safezone tp spawn`) use a countdown that is cancelled if you move, followed by a cooldown. Ops bypass both. `/spawn <zone>` works if you have visited the zone (or are admin). `/spawn set` writes the legacy `SpawnManager` spawn to config.yml.

### 4.8 Auction House (`auction/`, `AuctionCommand`, `Auction*Gui`)
- **Selling:** `/auction sell <price> [description]` lists the whole main-hand stack. You must be the owner or a LEADER, and you can have at most `max_listings_per_player` listings. **Ruby items cannot be listed.**
- **Buying:** payment goes from the **buyer's faction vault to the seller's faction vault** (the faction recorded on the listing). Overflow drops as gems. Only the owner or a BANKER+ can buy.
- Listings from disbanded factions are hidden from the market but can still be taken back through `/auction sales`.
- The Auctioneer NPC (librarian villager, `/auction npc spawn`) opens `AuctionMainGui`, which leads to market and sales lists (paged, 45 per page) and `AuctionConfirmGui` (BUY/REMOVE).

### 4.9 Job Shops (`shop/`, `ShopCommand`, `Shop*Gui`), newest feature on branch `feat/add-shop-manager`
- Each shop is a villager NPC tied to a job and has two weighted pools: **common** (any faction member with a job) and **rare** (members whose job matches the shop). Prices are **ruby gems taken from the buyer's faction vault**, like the auction house (✔ decided 2026-11-07, Open Question 6); the buyer needs access to the tier **and** must be the owner or a BANKER+.
- Every `reset_interval_hours` (168 h) up to `items_per_shop.<tier>` (max 28) items are drawn. Shops (job, NPC, pools), the rotation and the last reset time are stored in the **SHOPS** storage domain (✔ decided 2026-11-06).
- `shops.yml` keeps only tuning and `job_defaults.<JOB>` (templates copied into a new shop by `/shop create`; entries are `material/amount/potion/enchantments` or a serialized `item:`). A shop still hand-written under `shops.yml > shops` is **imported once** at startup, then that section is emptied.
- Admin: `/shop create <name> <job>`, `delete`, `list`, `additem <name> <common|rare> <weight> <price>`, `reset [name]`. Shop NPCs are immune to all damage and transformations.

### 4.10 Ruby (new item) & custom blocks (`Item/RubyItem`, `block/RubyBlockManager`, `BlockListener`, `RubyRestrictionListener`)
- Items (namespace `hatlas`):
  - `ruby` (EMERALD base)
  - `ruby_block` (EMERALD_BLOCK base)
  - `ruby_ore` and `deepslate_ruby_ore` (emerald-ore bases)
  - Recipes: 9 rubies ↔ 1 block.
- **Placed blocks** use the note-block trick: a NOTE_BLOCK with `instrument=pling`, note 0/1/2 → ruby_block / ruby_ore / deepslate_ruby_ore, overridden in `resourcepack/assets/minecraft/blockstates/note_block.json`. Locations are tracked in `blocks-data.yml`. `BlockListener` blocks note play, redstone, physics and pistons, re-applies the state on chunk load and on neighbor updates, and handles pick-block and step sounds.
  - Ores need an iron+ pickaxe and drop a gem.
  - Ruby blocks and ores can only be placed **in your own faction's claim**.
- `RubyRestrictionListener` (allowlist):
  - Any ruby item is allowed in the player inventory, 2×2 crafting grid and creative menu.
  - Gems and blocks are allowed in a crafting table.
  - Only gems are allowed in the faction vault.
  - Everything else (chests, shulkers, hoppers, crystal chests…) rejects all ruby items.
- `AmethystItem`: a netherite-based gear set re-skinned as amethyst (sword, tools, spear/trident, armor via equipment asset `hatlas:amethyst`, rod, horse armor), crafted from amethyst shards. Stats are the base item's **+`config.yml > amethyst.stat_bonus_percent`** (default 15 %): attack damage (total, fist included), armor, toughness, knockback resistance, correct-tool mining speed (huge speeds such as the sword's instant-mine rule are kept, else the item cannot be saved) and durability; attack speed and default mining speed unchanged. No ruby-style restrictions (✔ answered 2026-11-07, Open Question 8).
- `/item give <player> <id> [amount]` (`hatlas.item.admin`).

### 4.11 Trade (`trade/`, `TradeCommand`, `TradeListener`, `TradeGui`)
- Right-clicking a player sends a trade request (clickable accept/decline, expires after 60 s). `/trade accept|decline [player]`.
- The GUI has a left half for your offer and a right half for theirs. Changing items resets both accepts. When both accept, a 3 s countdown (shown on the XP bar) runs and then the items swap. Quitting, dying or closing cancels the trade and returns the items.

### 4.12 Teleports
- **`/rtp`** (`RandomTeleportManager`): countdown, cooldown, radius around world spawn, safe solid ground. Blocked in the Nether and End.
- **`/tpa <player>`, `/tpa accept|deny`** (`TeleportAtManager`): requests expire after 30 s, then countdown, then cooldown.
- **`/sethome [name]`, `/home [name]`, `/delhome <name>`** (`HomeManager`): reserved `main` home plus secondary homes up to `1 + faction homes-skill bonus`. Cannot be set in another faction's claim.
- **`DeathTeleportCooldownManager`:** an escalating teleport ban after death (base × multiplier while inside the escalation window) for /home, /f home and /tpa. Ops bypass it.

### 4.13 Combat (`combat/`, `CombatLogListener`)
- Any PvP hit (melee or projectile) marks both players as in combat for `combat_log.timeout_seconds`. Quitting while marked drops your inventory and armor, kills you and broadcasts it. Timers survive a restart (`combats-data.yml`) and are not applied during shutdown.
- 1.8-style PvP comes from an **external plugin** (per WIKI), not from Hatlas.

### 4.14 Golems (`golem/`, `GolemListener`)
- Building the T-pattern with a carved pumpkin on top of a body block creates a faction-tagged Iron Golem with stats from `GolemType`:
  | Body block | Stats / special effect |
  |---|---|
  | Iron | base stats |
  | Soul Sand | Slowness |
  | Amethyst | 0 damage, Glowing |
  | Gold | high damage, low HP |
  | Emerald | heals nearby faction members (Regen II) |
  | Crying Obsidian | 200 HP, slow, 5% chance to send the target to the Nether |
- Golems attack non-faction players within range and alert the faction (throttled). Right-click with the body material heals 10%. A golem killed by a player drops 0–5 of its material.

### 4.15 Locator bar (`LocatorBarListener`, packetevents)
- Intercepts outgoing WAYPOINT packets so a player only sees locator-bar markers of **their own faction**. `refresh(players)` must be called whenever faction membership changes (already done in `FactionManager`).

### 4.16 Paid access (`access/`, M2)
- `AccessManager` listens to `AsyncPlayerPreLoginEvent`: with `access.require_ticket: true` a login needs `max(valid_until) > now()` in `<access.web_schema>.tickets` for the player's UUID (own JDBC connection via `Storage.newConnection()`, query off the main thread). No/expired ticket → refused with the renew link; query error or SQLite → refused (fails closed); operators bypass (`ops_bypass`). `/hatlas access check <player|uuid>` (`hatlas.access.admin`). The real gate is `hatlas-proxy`. Test server: check off, ticket fixture `scripts/test-world/web-tickets.sql` loaded on `reset`. See [`docs/access.md`](docs/access.md).

### 4.17 Ruby ledger (`economy/`, ✔ requested 2026-11-07, **merged 2026-11-08**, PR #44)
- Append-only table `ruby_ledger` (V3): every ruby move with a sender and a receiver (player or faction; none = created/destroyed), amount in gems (block = 9), actor, `ref`, place. Kinds: `MINE` (the only natural source; ruby ore + valid pickaxe), `ADMIN_GIVE`, `ADMIN_CLEAR`, `BLOCK_PLACE` (player → faction: a placed ruby block belongs to the faction whose claim holds it, `custom_blocks.owner`)/`BLOCK_BREAK` (faction → breaker), `UNTRACKED_BLOCK`, `VAULT_DEPOSIT`/`VAULT_WITHDRAW`, `SHOP_BUY` (sink), `AUCTION_BUY` (faction → faction), `TRADE` (player → player, trade window), `PICKUP` (owner → picker), `LOST`, `UNTRACKED_PICKUP` (leak detector).
- **Dropped rubies keep their owner** (PDC tag on the item entity: owner + origin such as `PROTECTION_BREAK`, `DEATH`, `DROP`): no row on the drop, a `PICKUP` row when another party picks them up, `LOST` when they vanish; different owners never merge, mobs cannot pick rubies up. Rubies cannot move otherwise (refused in every container but the vault, crafting grids and the trade window). `ADMIN_GIVE` also covers vanilla `/give` (`GiveCommandListener`, measured one tick later). **Emitted** = MINE/ADMIN_GIVE/UNTRACKED_PICKUP/UNTRACKED_BLOCK, **burned** = SHOP_BUY/LOST/ADMIN_CLEAR, everything else is a transfer; crafting gems ↔ blocks writes nothing (✔ 2026-11-07). Exploded ruby blocks drop as the faction's (`EXPLOSION`).
- `RubyLedger.record(...)` buffers, flushed by the storage writer every second and before the final save (`Storage.appendLedger`). Vault moves are measured from the vault's and the player's gems one tick after each click/drag. Use `RubyLedger.drop(...)` (not `dropItemNaturally`) for any new code that drops rubies, and `record(...)` for any new payment.
- Website views `web_ruby_transactions` (no coordinates) and `web_ruby_daily` (emitted/burned/placed/broken/transferred per UTC day). Admin `/hatlas economy history <player|faction> [n]`, `/hatlas economy supply` (`hatlas.economy.admin`). Doc: [`docs/economy.md`](docs/economy.md).

### 4.18 Utilities
- `TagManager` / `/tag create|delete|add|edit|list`: multi-line TextDisplay holograms (`tags-data.yml`).
- `AfkManager`: kicks after `afk.timeout_seconds` without activity.
- `ItemClearManager`: clears dropped items every 20 min with warnings.
- `TabListManager`: tab names colored by faction, admins in dark red.
- `ResourcePackManager`: pushes the `hatlas` pack on join (url, sha1, required, prompt in config.yml).

---

## 5. Configuration & data files (`plugins/hatlas/`)

| Config (shipped) | Content |
|---|---|
| `config.yml` | `storage` (backend), `access` (login ticket check, `docs/access.md`), `amethyst`, `tpa`, `random_teleport`, `afk`, `death_teleport_cooldown`, `resourcepack` (legacy `spawn.*` is only read once, for the import) |
| `factions.yml` | `faction_home`, `skill_points_per_level`, `vault`, `skills.{homes,hp,claims,chest,protection,outpost,vault}`, `crystal.*` |
| `jobs.yml` | `quests.{daily_reset_hours,exp_base_reward,tasks[]}`, `jokeyrini.{daily_reset_hours,special_quest_chance,tasks[]}` |
| `donjons.yml` | activation/timeout/max active, smuggler cooldown, `difficulty[]`, `rarity`, `ominous_key`, `types.<type>` (mobs, bosses, waves, multipliers, exp, `boss_drops.<rarity>`) |
| `homes.yml` | `home_teleport` |
| `safezones.yml` | `safezone` teleport delay/cooldown |
| `combats.yml` | `combat_log.timeout_seconds` |
| `auctions.yml` | `max_listings_per_player` |
| `orezones.yml` | `interval_reset_hours`, `default_ore_weights` |
| `shops.yml` | `reset_interval_hours`, `items_per_shop`, `job_defaults` (+ `shops`: import-only, emptied after import) |

**Runtime data** goes through the storage adapter (`config.yml > storage.type`, default **postgresql** since 2026-11-07; `sqlite` → `plugins/hatlas/hatlas.db` for dev servers). An unreachable database disables Hatlas with a message naming the database, the cause and what to check. Full audit, schema and operating notes: [`docs/storage.md`](docs/storage.md). 13 domains: FACTIONS, CRYSTALS, JOBS (incl. Jokeyrini), DONJONS, HOMES, SAFEZONES, COMBAT, BLOCKS, AUCTIONS, OREZONES, SHOPS, TAGS, SPAWN, plus the append-only **ruby ledger** (`ruby_ledger`, V3, [`docs/economy.md`](docs/economy.md)). Schema files: `src/main/resources/db/V<n>__*.sql`, applied by `SchemaMigrator`.
- YAML is no longer a backend: `storage.type: yaml` is read as `sqlite` with a warning. The backend is chosen once (no SQLite ↔ PostgreSQL migration). `/hatlas storage info` (`hatlas.storage.admin`) shows the backend; `/hatlas storage save` writes every domain synchronously (used by the backup script); `/hatlas storage export` was **removed** 2026-11-07 (Open Question 25). **Backups:** `scripts/backup/hatlas-backup.sh` (DB dump + world copy taken together, daily systemd timer, restore), see [`docs/backup.md`](docs/backup.md).
- On the first start with a database, the `*-data.yml` files are imported and renamed `*.yml.migrated` (backup).
- **PostgreSQL schema `hatlas`** (`storage.postgresql.schema`): every connection uses it as `search_path`; an older install's tables in `public` are moved there on start. **Website read model** (V2): the website reads only the `web_*` views (`web_factions`, `web_faction_members`, `web_faction_allies`, `web_crystals`, `web_player_jobs`, `web_shops`, `web_shop_items`, and since V3 `web_ruby_transactions`, `web_ruby_daily`), through the read-only role `storage.postgresql.web_role` (default `hatlas_web`; created by an admin, granted SELECT on the views by Hatlas on every start). Readable columns `factions.vault_gems`, `shop_items.material/amount` are written by the snapshots. See `docs/storage.md` §5.
- Saves happen right after important mutations, then every `autosave_minutes` (5) for all domains, and at shutdown. **A crash loses at most the last autosave interval** for data without an immediate save (job XP, quest progress, custom blocks, combat timers).

---

## 6. Resource pack (`resourcepack/`, namespace `hatlas`)
- `pack.mcmeta`: `min_format = max_format = 75` (1.21.11).
- `assets/hatlas/items/*.json` → `models/item|block/*.json` → `textures/item|block/*.png`. Armor uses `equipment/amethyst.json` plus `textures/entity/equipment/{humanoid,humanoid_leggings,horse_body}/amethyst.png`.
- `assets/minecraft/blockstates/note_block.json` overrides pling notes 0–2.
- **Gotcha:** block textures must be under `textures/block/` (the vanilla block atlas does not include `item/`).
- The pack is zipped and hosted outside the repo. `config.yml > resourcepack.url/sha1` are placeholders.

---

## 7. Known issues / technical debt (found during analysis, 2026-11-05)
1. ~~`jobs.yml` uses `multiplier_exp:` but the code read `exp_multiplier`~~ — **fixed 2026-11-05**: `QuestManager.expMultiplierSection()` reads `multiplier_exp` (legacy `exp_multiplier` still accepted) for job and Jokeyrini tasks.
2. ~~`TagCommand` `delete`/`edit` saved tags to `config.yml`~~ — **fixed 2026-11-05**: all `/tag` subcommands now save to `tags-data.yml`.
3. `ElectricalCreeperManager.OBSIDIAN_HITS_REQUIRED = 3`, but a listener comment says "4 hits". The WIKI also contradicts itself on creeper eggs.
4. ~~Faction max level 99 in code, 100 in the WIKI and `/f level set` help~~ — **fixed 2026-11-07**: 99 is the max (Open Question 4); help text and both WIKIs say 99.
5. ~~`factions.yml` `crystal.immunity_base_seconds` / `immunity_multiplier` loaded but unused~~ — **fixed 2026-11-07** (Open Question 5): removed; the watch-window factor is now `crystal.protection_watch_multiplier` (default 2, min 1). The `Faction` downgrade fields are still unused.
6. The `config.yml` comment says "/air tp" for random teleport. The WIKI values (tpa cooldown 30 s, 5 s countdowns) differ from the configs (tpa 60 s, 10 s countdowns).
7. The `structures/*.nbt` files are unused by the code **by design** (see §4.5).
8. Typo `maxActiveDonjonons` in `DonjonManager`.
9. ~~`FactionClaimManager.saveClaims/loadClaims` are legacy~~ — **removed 2026-11-06**: claims are persisted per crystal (CRYSTALS domain, `crystal_claims`).
10. ~~**Orphan crystals keep claims**~~ — **fixed 2026-11-06**: `FactionManager.persist()` saves factions + crystals right after create/delete/disband; `loadCrystalData` drops crystals of unknown factions (WARN log + file rewrite); `restore()` removes orphan crystal entities when their chunk loads.
11. ~~**Crystals in chunks already loaded at enable are never restored**~~ — **fixed 2026-11-07**: `FactionListener.onEntitiesLoad` only saw chunks whose entities loaded after the listener was registered, so a force-loaded chunk's crystal stayed a stub (and an orphan entity stayed in the world). `Hatlas.onEnable` now calls `HatlasCrystalManager.restoreLoadedEntities()` after registering listeners; the listener and the scan share `restoreIfNeeded()`.

---

## 8. Milestones

### M1 — Regression tests: local in-game gate + CI unit tests (status: **in progress**, redesigned 2026-11-07)

**Decisions (Open Questions 13–16, 20):** no MCP server and no Minecraft server in CI (token and CI-time cost).
1. **Local, in game, before every feature PR** — done on `feat/ingame-test-agent`: JSON suites per feature, `features.yml` selection, `ingame-tester` agent, `ingame-gate` hook (§2). Runs on the Windows test server until the dedicated test world lands (Open Questions 10/15), then on that world.
2. **CI on every PR to `main`** — planned: a GitHub Actions workflow running `./gradlew build` + **unit tests** (JUnit 5, MockBukkit where Bukkit types are needed) for pure logic: faction XP curve and level-ups, quest amounts / time limits / rewards, donjon XP and rarity rolls, ore-zone weighted roll, storage round-trip (YAML ↔ SQLite on a temp folder). Required status check before merge.

**Coverage target:** per feature of §4, one nominal + one refusal/edge + one persistence scenario, plus E2E flows ("create faction → job quest → faction XP → crystal skill", "mine ruby in an ore zone → buy in a shop", "run donjon → raid with the Raider's Pickaxe"). Current suites: faction, storage, orezone (+ shop and job on their PR branches).

### M2 — Website, proxy and paid access (status: **planned**, decided 2026-11-07, Open Questions 21–25)

**Goal:** a SvelteKit SSR website (same machine as the servers) where a player links their Minecraft account, buys a monthly ticket that gives access to the faction server, and sees read-only data: their faction (level, rubies, members…), shops, their job XP, online players.

**Architecture**
```
player ─▶ Velocity proxy (online-mode, only public port)
            ├─ hub (default server, no Hatlas) ── /link
            └─ faction server (Hatlas, bound to localhost, Velocity modern forwarding)
SvelteKit SSR ─▶ PostgreSQL ◀─ Hatlas (schema hatlas) / hatlas-proxy (schema web: read tickets, write link codes + presence)
Stripe ─webhook▶ SvelteKit (writes web.tickets)
```
- **PostgreSQL is the production backend and becomes the default `storage.type`** (SQLite kept as an option for `runServer`/dev). A missing database disables Hatlas with a clear message.
- **Two schemas, enforced by roles:** `hatlas` (owned by the plugin; the website reads only **views**, never internal tables) and `web` (owned by SvelteKit: accounts, links, tickets, payments). The plugin writes readable columns for the website (e.g. faction `vault_gems`, shop item material/name/amount) because vault and item contents are Paper item bytes.
- **No HTTP API in the plugin** (Open Question 22). Reads go through views; **online players** through a presence table written by `hatlas-proxy` on join/quit/server switch (`LISTEN/NOTIFY` for live updates if needed). An API is only added later for live game state the DB cannot hold.
- **Writes happen only on the website side** (Open Question 21): ticket purchase = Stripe Checkout → webhook → SvelteKit writes `web.tickets`; link = `/link` writes a single-use code (5–10 min) to `web.link_codes`, the player (logged in on the site) enters it, SvelteKit records the link. Payments never depend on the game server being up.
- **`hatlas-proxy` (Velocity plugin)** owns `/link`, the ticket check when moving hub → faction server ("access expired, renew at <url>"), the mid-session expiry (warn, then **send back to the hub**), and the presence table. Hatlas also refuses a login without a valid ticket (defence in depth), switchable for the test server (`access.require_ticket: false`, bots connect directly).
- **A ticket belongs to a Minecraft UUID** (Open Question 24), not to the web account.
- **Backups** (Open Question 25): daily `pg_dump -Fc` + world copy taken together (`save-off` → `save-all flush` → dump → copy → `save-on`), restored together by one script, kept **on the same machine in a dedicated folder** for now (rotation e.g. 7 daily + 4 weekly). Data loss ≤ 24 h accepted.
- **`/hatlas storage export` is removed** (replaced by the backups above); `/hatlas storage info` stays.

**Planned PRs (in order)**
1. `feat/postgres-default` (**merged 2026-11-07**, PR #40): default `storage.type: postgresql` (driver loaded on a first start too), clear startup error, `/hatlas storage export` + portable SQLite mode removed, docs.
2. `feat/backup-script` (**merged 2026-11-07**, PR #41): `scripts/backup/hatlas-backup.sh` (Bash, Linux prod with PostgreSQL in docker compose, ✔ 2026-11-07) `backup|list|verify|restore|prune`, systemd timer (daily 04:30), rotation 7 daily + 4 weekly (+3 pre-restore), new `/hatlas storage save` (sync write before the dump). A restore replaces only `GAME_SCHEMAS` (website tickets kept) unless `--full`. Doc: [`docs/backup.md`](docs/backup.md).
3. `feat/web-read-model` (**merged 2026-11-07**, PR #42): tables moved to schema `hatlas`, readable columns (`vault_gems`, shop item `material`/`amount`), 7 `hatlas.web_*` views, read-only role `hatlas_web` granted SELECT on the views only (Hatlas never creates the role). Backup `GAME_SCHEMAS` default → `hatlas`; restore now recreates any schema before `pg_restore -n` (it only worked for `public`).
4. **Proxy and access** (✔ 2026-11-07: **separate repo `../hatlas-proxy`**, no multi-module build here). The Velocity plugin (`/link` merged, proxy PR #2; ticket gate + mid-session expiry on its `feat/ticket-gate`, 2026-11-08, built by this session after the user paused the proxy session; presence still to do) is developed in that repo with its own CLAUDE.md, test stack (`scripts/test-stack.ps1`: Velocity 25577 offline + hub + faction backends, DB `hatlas_proxy_dev`) and gate. **Hatlas side: `feat/access-ticket-check`** (**merged 2026-11-08**, PR #43): login check behind `access.require_ticket` (default off, fails closed, ops bypass), `/hatlas access check`, ticket contract `web.tickets (uuid, valid_until)` = latest `valid_until > now()`. Doc: [`docs/access.md`](docs/access.md).
5. Website (separate repo): SvelteKit + Drizzle/postgres.js on schema `web`, Stripe Checkout + webhook, link page, dashboard.
5b. **Identity** (planned 2026-11-08, [`docs/identity.md`](docs/identity.md), ready to build; legal points in Open Questions 32–34): the network runs **offline mode** (✔ user), so a name proves nothing; a login must come before the ticket gate: `/register` / `/login` in hatlas-proxy give single-use links to the website (account created at registration, email verified before playing, every connection approved on the site, 2FA there, no IP session), `/link` retired; GDPR export/delete. **One web account ↔ one game account** (✔ user). Hatlas side: schema V4 `players` + view **`web_players (uuid, name, first_seen, last_seen)`** (✔ user, webapp Open Question 22).
6. **`test/e2e-access-chain`** (task added 2026-11-07, user request): an **end-to-end check of the whole access chain** through Velocity, needed before launch. **Built in `../hatlas-proxy`** on its test stack (its task 1, `test-stack.ps1 install faction --with-hatlas`, unblocked by step 4's Hatlas login check); needs the proxy's ticket gate first (in progress there, 2026-11-08). Website plan: `../hatlas-webapp/CLAUDE.md` (written 2026-11-08, no code yet). A local test stack: Velocity (`hatlas-proxy`) + hub + faction server (Hatlas with `access.require_ticket: true`) + PostgreSQL (`hatlas` and `web` schemas) + the website (or a stub writing `web.link_codes` / `web.tickets`). Scenarios with bots connecting **through the proxy**:
   - **Login and `/link`:** a new player joins → lands on the hub → `/link` gives a single-use code (5–10 min) → the code is redeemed on the site (or stub) → the link is recorded; an expired or reused code is refused.
   - **Ticket validation:** no ticket / expired ticket → stays on the hub with "access expired, renew at <url>"; valid ticket (bought via Stripe test mode → webhook → `web.tickets`) → may move hub → faction server; Hatlas itself refuses a direct login without a ticket (defence in depth).
   - **Mid-session expiry:** a ticket expiring while on the faction server → warning, then sent back to the hub; **ticket tied to the UUID** (another account linked to the same web account gets no access).
   - **Presence:** join / quit / server switch update the presence table read by the website.
   Settled by the proxy repo's stack: the test proxy runs offline-mode with modern forwarding, local processes (not compose), suites behind its gate. Still open: Stripe test mode vs. a stub writing `web.tickets` (stub until the website exists).

7. **Production deployment** (task added 2026-11-08, user request; plan [`docs/deployment.md`](docs/deployment.md)): every service in docker compose on the private machine, router opens **only 443 (HTTPS) and 25565 (proxy)**; game stack compose + `update.sh` here, website `update.sh` + Caddy in the webapp; encrypted backups; production smoke test with real clients (register → verify → login code → Stripe test ticket → faction → expiry → log out everywhere → export/delete), outside port scan.
**Shared code with `../hatlas-proxy`** (✔ decided 2026-11-07): for now the small ticket check is **duplicated** in each plugin. If more code has to be shared later (config models, link-code logic, constants), extract a library `../hatlas-common` and include it with a **Gradle composite build** (`includeBuild("../hatlas-common")`, built from source, no publishing); publish it (e.g. GitHub Packages) only when CI needs it.

**Funding and transparency** (✔ user 2026-11-10): free price, minimum EUR 1, presets 5/10/20; the website shows the monthly running costs and a progress bar, surplus reinvested: [`docs/funding.md`](docs/funding.md).

**Map building research:** [`docs/map-building.md`](docs/map-building.md) (Open Question 42).

**Cities, city zones, dungeon server, skinned GUIs** (plan, rounds 17–18, 2026-11-11): [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md); job skill trees: [`docs/job-skills.md`](docs/job-skills.md) (Open Questions 44–70). ✔ Round 19 (2026-11-12): **all of it ships at launch**. Round 20 (2026-11-13): **mining world** [`docs/mining-world.md`](docs/mining-world.md); epics jobs → dungeons → mining world → cities, **beta after each**. Round 21 (2026-11-16): items across servers + travel bag [`docs/cross-server-items.md`](docs/cross-server-items.md), ruby observatory [`docs/economy-observatory.md`](docs/economy-observatory.md). Round 23 (2026-11-19): **Runes** [`docs/runes.md`](docs/runes.md).

**Admin tuning guide:** [`docs/server-tuning.md`](docs/server-tuning.md) (compose priorities and NUMA pinning, JVM flags, Velocity/Paper configs, Sonar, GrimAC, anti-xray, LuckPerms, LibertyBans, CoreProtect).

**Before launch:** check Mojang's Minecraft Usage Guidelines for paid server access, EU VAT on digital services (e.g. Stripe Tax), refunds/chargebacks (webhook revokes the ticket).

---

## Open Questions

> Claude: add a question here whenever a request is unclear. Ask the user, and record the answer.

1. ~~Exp multiplier key~~ — ✔ answered 2026-11-05: user asked to fix; code now reads `multiplier_exp`.
2. ~~Structures~~ — ✔ answered 2026-11-05: archives of arena/donjon builds for manual import; not loaded by code.
3. ~~**Donjon types**~~ — ✔ answered 2026-11-07: all 6 types in `donjons.yml` are live. There is no `COOLDOWN` status: it was only written in the old CLAUDE.md (commit c9d9685, `DonjonStatus — IDLE, ACTIVE, COOLDOWN`) and never existed in code. `DonjonStatus` stays IDLE / ACTIVE.
4. ~~**Faction max level**~~ — ✔ answered 2026-11-07: **99** (known issue §7.4 fixed).
5. ~~**Crystal immunity escalation**~~ — ✔ answered 2026-11-07: the dead `immunity_base_seconds` / `immunity_multiplier` keys are removed; the protection watch window (hard-coded `2 × duration` before) is configurable as `crystal.protection_watch_multiplier`, default 2 = previous behaviour.
6. ~~**Shop payment**~~ — ✔ answered 2026-11-07: shops are paid from the **faction vault** like the auction house (no difference intended). New role **BANKER** (MEMBER < BANKER < MODERATOR < LEADER) that may only spend the vault's rubies; spending the vault (withdraw, shop, auction buy) = owner or BANKER+ (see §4.1).
7. ~~**ALCHEMIST job**~~ — ✔ answered 2026-11-07: tracks **only brewing and crafting**. Kills no longer give Alchemist XP; the 7 kill/gather tasks in `jobs.yml` were replaced by 7 brew/craft tasks (still 16 per job).
8. ~~**Amethyst gear**~~ — ✔ answered 2026-11-07: custom stats, by default **15 % above netherite** (configurable `amethyst.stat_bonus_percent`); **no** ruby-style restrictions. See §4.10.
9. ~~**"Rubis Ruins" safe zone**~~ — ✔ answered 2026-11-07: **Ruby Ruins** is the name of the current update (ruby, amethyst, ore zones, auction house, shops), not a safe zone. WIKI EN/FR fixed (banner at the top, wrong safe-zone mention removed).
10. ~~**Map/world**~~ — ✔ answered 2026-11-07: the user will add an **empty world save** plus **schematics of the spawn city and the donjons** to the repo (for saves/tests); see also Open Question 15. — *done 2026-11-07:* map in `run/world` (git-ignored), fixtures + generated setup + baseline/reset (§2).
11. ~~**Persistence:** autosave?~~ — ✔ answered 2026-11-06: storage adapter with async saves after mutations + autosave every `storage.autosave_minutes` (5) + sync save at shutdown.
12. ~~**WIKI maintenance**~~ — ✔ answered 2026-11-07: a dedicated **wiki-writer agent + skill**, started by a **hook** each time a feature is finished, writes player-facing docs (features, commands, what players can do) in `WIKI.md` / `WIKI-FR.md`. Built on its own branch (`feat/wiki-agent`).
13. ~~**M1 — who drives the tests in CI?**~~ — ✔ answered 2026-11-07: nobody; no MCP in CI (see M1).
14. ~~**M1 — VitaminMCP in CI**~~ — ✔ answered 2026-11-07: not needed, no MCP in CI.
15. ~~**M1 — test world**~~ — ✔ answered 2026-11-07: a dedicated test world, copied into the repo by the user in the next PR. — *done 2026-11-07:* disposable test server, reset to baseline, fixtures (§2).
16. ~~**M1 — CI host**~~ — ✔ answered 2026-11-07: no Minecraft server in CI, so no runner choice needed.
17. ~~**M1 — "part of a feature" granularity**~~ — ✔ answered 2026-11-07: test selection **by feature**, feature-level (every scenario of a touched feature runs), as implemented in `src/test/ingame/features.yml`.
18. ~~**Storage backend**~~ — ✔ answered 2026-11-06: adapter `DataStore` with YAML, SQLite (default) and PostgreSQL (later) backends; full relational schema; automatic one-time import of `*-data.yml`; shops moved to storage; async writes + autosave. See [`docs/storage.md`](docs/storage.md).
19. ~~**Storage — PostgreSQL / export**~~ — ✔ answered 2026-11-07: PostgreSQL is covered by a **local docker-compose** (`docker/postgres/`, see `docs/storage.md` §4), tested end to end. YAML storage is removed (legacy `*-data.yml` are only imported once); once an admin picks sqlite or postgresql there is **no migration** between them; `/hatlas storage export` writes a **whole-database backup to a portable SQLite file** (see §5) — *superseded 2026-11-07 by Open Question 25: export to be removed, PostgreSQL default, daily dumps (M2).*
20. ~~**M1 — what should CI check instead?**~~ — ✔ answered 2026-11-07: **`./gradlew build` + unit tests** (JUnit + MockBukkit) for pure logic on each PR. In-game scenarios stay local. See M1.
21. ~~**Website writes**~~ — ✔ answered 2026-11-07: link and ticket purchase are handled by **SvelteKit + PostgreSQL**; nothing writes through the plugin. See M2.
22. ~~**HTTP API in the plugin**~~ — ✔ answered 2026-11-07: **not needed** for now; DB views + a presence table + a Velocity plugin instead. See M2.
23. ~~**Proxy**~~ — ✔ answered 2026-11-07: **Velocity** in front (hub + faction server) with a small **`hatlas-proxy`** plugin owning `/link` and the ticket check. See M2.
24. ~~**Ticket expiry / ownership**~~ — ✔ answered 2026-11-07: expiry mid-session **sends the player back to the hub**; a ticket is **tied to the Minecraft UUID**.
25. ~~**Backups**~~ — ✔ answered 2026-11-07: **daily dump** (≤ 24 h loss), stored **on the same machine in a dedicated folder** for now; `/hatlas storage export` will be removed. PostgreSQL becomes the default backend.
26. ~~**Login in offline mode**~~ — ✔ answered 2026-11-08: **own login in hatlas-proxy** (no AuthMe), **fresh start** (no import), **2 h IP session** after the last quit (superseded by Open Question 27: no IP session), **password reset from the website** (or an admin), **2FA from the website**; registering in game creates the website account. Challenged and designed in [`docs/identity.md`](docs/identity.md) §2–3: no password or 2FA code ever typed in game, `/register` and `/login` give a chat link to the site (a login link is only approved by a browser logged in to that account), `/link` and `web.link_codes` retired.
27. ~~**Identity, open points**~~ — ✔ answered 2026-11-08: no credential in game (`/register` and `/login` only give a **single-use** link); email **OVH SMTP `no-reply@hatlas.net`**; **email verified before playing**; **no IP session**: every connection is approved on the site by a browser signed in to the account, plus **"log out of the game everywhere"**; **GDPR**: privacy page, data export and account deletion in the profile. Design: [`docs/identity.md`](docs/identity.md) §2–5 (a single-use link alone does not stop bots in offline mode: per-IP limits, verification and a sign-up proof-of-work too).
28. ~~**Identity, last points**~~ — ✔ answered 2026-11-08 (round 4): **ALTCHA** on sign-up (and sign-in); website session **7 days renewed daily**; the **4 anti-abuse measures** for registration and login (proxy per-IP limits, verified email, ALTCHA, website limits); **approximate IP location from a local database** on the approval page and the profile; **log out of the game everywhere kicks at once** (`NOTIFY hatlas_logout`). See [`docs/identity.md`](docs/identity.md) §2.1, §3.4, §3.5.
29. ~~**Identity, remaining points**~~ — ✔ answered 2026-11-08 (round 5): deletion = out of the faction (owner → next rank, disband if alone), every related data deleted, ruby transactions kept anonymous (UUID replaced, since an offline UUID is recomputable from the name); **DB-IP City Lite self-hosted**; activity history **90 days**; **argon2id**; **2FA by authenticator app (QR) or email code** + backup codes; **"Download my data"** button. See [`docs/identity.md`](docs/identity.md) §2, §5, §7.
30. ~~**Identity, security choices**~~ — ✔ answered 2026-11-08 (round 6): security emails on a game login from a new location, password reset, email or 2FA change; deletion loses a running ticket without refund (warning on the page); passwords found in known leaks refused (Have I Been Pwned, k-anonymity); player links never clickable; **CGU + CGV + legal notice in French and English** to write. See [`docs/identity.md`](docs/identity.md) §2, §7, §8.
31. ~~**Identity, last two points**~~ — ✔ answered 2026-11-08 (round 7): **a code typed in game on every approval**, whatever the IPs; seller = the user, **micro-entrepreneur** (SIRET 887 895 878 00015). Identity plan complete: [`docs/identity.md`](docs/identity.md).
32. ~~**Offline mode vs Mojang's terms**~~ — ✔ answered 2026-11-09: **keep offline mode** (current players have no premium account); risk accepted; the stored UUID keeps a premium/hybrid switch possible later ([`docs/identity.md`](docs/identity.md) §8).
33. ~~**Ticket price**~~ — ✔ answered 2026-11-10 (replaces the EUR 5 subscription of 2026-11-09): **the player chooses the price, minimum EUR 1, presets EUR 5 (default) / 10 / 20, for 30 days of access, paid once, no subscription, no auto-renewal, Stripe receipt only**; goal = transparency on costs ([`docs/funding.md`](docs/funding.md)). Stripe Checkout `mode=payment`, amount chosen and validated on our `/renew` page, webhook `checkout.session.completed` adds 30 days to `web.tickets` (contract unchanged); sandbox "Hatlas"; no VAT (franchise), Stripe Tax off. Challenges in [`docs/identity.md`](docs/identity.md) §8: EUR 1 loses ~48 % to fees; a chosen price vs Mojang's "same price" wording. Amount presets/maximum, stacking, reminder email and CGV points are **parked until the webapp payment step** (§8).
34. ~~**VAT, URSSAF category and consumer mediator**~~ — ✔ answered 2026-11-09/10: mediator **CNPM Médiation Consommation** (confirmed), activity **BIC services**. One accountant check of the VAT thresholds (and whether each sale needs an invoice) before launch stays in §8 of the identity plan.
35. ~~**Production machine**~~ — ✔ answered 2026-11-09: Debian, 2 × Xeon E5-2698 v3, 16 GB RAM, NVMe 1 TB + SATA SSD `sda` 120 GB; router opens **80, 443, 25565** to it; dynamic IP via the user's `ovh-ddns` container on `play.hatlas.net`. Consequences in [`docs/deployment.md`](docs/deployment.md) §2.
36. ~~**RAM already in use**~~ — ✔ answered 2026-11-09: the 8.5 GB are the **current Minecraft server and website**, freed when they are replaced. User also chose Chunky pre-generation, view 8 / simulation 6 and the faction server pinned with memory priority: admin guide [`docs/server-tuning.md`](docs/server-tuning.md). **Capacity** (asked 2026-11-10): 40 players fit in RAM (faction heap 7 GB after subtracting the website and the other services); the CPU is the limit, 40 is OK but close: load test with 40 bots before opening ([`docs/deployment.md`](docs/deployment.md) §2.10).
37. ~~**Landing page and certificates**~~ — ✔ answered 2026-11-10: today `../landing-website` (nginx + certbot) and `../ovh-ddns` (OVH API). Caddy replaces nginx + certbot; `ovh-ddns` kept with small fixes; the new website gets a **fresh design** and its own home page on `play.hatlas.net`; then `../landing-website` is **archived and deleted** from the machine ([`docs/deployment.md`](docs/deployment.md) §2.3, §2.5).
38. ~~**Minecraft port**~~ — ✔ answered 2026-11-10: the router forwards **25565, 80 and 443** to the same ports on the machine (checked by the user).
39. ~~**Backup disk and RAM**~~ — ✔ answered 2026-11-10 (modules today in `DIMM_C1` + `DIMM_G1`, one per CPU; a leboncoin Trident Z listing checked in [`docs/deployment.md`](docs/deployment.md) §2.6): `sda` (PNY 120 GB SATA SSD, `sda1` empty) is formatted for **restic** backups; **two more RAM modules** bought (→ 4 × 8 GB on the first CPU, quad channel; shopping list and procedure in [`docs/deployment.md`](docs/deployment.md) §2.6); sockets: 0 = CPUs 0–15/32–47, 1 = 16–31/48–63; board = generic "INTEL X99" (real model to read on the board for its manual). **Off-site copy: later**, after development (offline disk saved by hand, about yearly; monthly suggested). ✔ 2026-11-12: **the RAM kit is installed** (user); checks after boot in [`docs/deployment.md`](docs/deployment.md) §2.6 still to run.
40. ~~**Cutover from the current server**~~ — ✔ answered 2026-11-10: **no migration**; the current server is not maintained and will be **deleted**; the new network starts on a fresh world ([`docs/deployment.md`](docs/deployment.md) §2.9).
41. ~~**Production world**~~ — ✔ answered 2026-11-10: **another map** than the test one, with the same spawn city and donjons **at other places**. `run/world` stays the test map only.
42. **Production world setup** (asked 2026-11-10; research 2026-11-10 round 12: [`docs/map-building.md`](docs/map-building.md)): the test setup (`src/test/ingame/fixtures.json` + `build-setup.mjs`) is tied to the test map's coordinates. Plan: a **production fixtures file** (`deploy/game/world/fixtures.prod.json`) and the same generator. The user asked whether Claude could build the map through an MCP server, learning from shared maps, with bots placing blocks: research says **design as files, preview, paste with FAWE/`/place template`** (bots only to review), shared maps only as **licensed style references** (no scraping; many Planet Minecraft builds forbid commercial or AI use), terrain by WorldPainter or a datapack generator; proposed **pilot** of one small build with a builder MCP on the test server. ✔ Round 13: **one giant island over the void**, terrain by **WorldPainter driven by Claude** (`wpscript` + Python heightmaps and biome masks, 2D/3D previews, BlueMap render), biomes snowy mountains (main), rocks, oak hills, cherry grove, pale garden; modded GDMC server postponed (local only, if the island feels empty) ([`docs/map-building.md`](docs/map-building.md) §7). ✔ Round 14: radius **4,000 blocks**; falling into the void with items allowed (rocks sometimes run to the edge); brief **`worldgen/map.md`** (dwarven ambiance: city at the foot of the great snowy mountain, amethyst cave with ruby mine, old house and ruins, cherry mountain with bees, fjord with port and viking village, dark forest creek, summit lake); **skill `map-building`** (one agent per step: designer, terrain generator, verifier, WorldPainter exporter, BlueMap renderer in docker compose, in-game checker; user gates); **test island** (radius 1,000) planned in [`docs/map-building.md`](docs/map-building.md) §8. ✔ Round 15: fjord closed toward the void for the port; `desert` donjon in a **volcano crater** (stone/rock volcano); the cave is an **amethyst mine** (rubies stay in `city_mine`); WorldPainter 2.27.1, Python 3.15.2, exported 1.21.11 template in `worldgen/template/`. ✔ Round 16: `worldgen/template.world` saved (test-island prerequisites complete); `nether_castle` **inside the volcano**; the cave holds a **custom crystal item + shard** (future feature, vanilla amethyst as stand-in). Still open: the builder-MCP pilot, builds/NPCs by hand or by the generator.
43. ~~**Funding page**~~ — ✔ answered 2026-11-10 (round 12, [`docs/funding.md`](docs/funding.md)): electricity **EUR 0.15 / kWh** (→ EUR 25.50 / month; running costs ≈ **EUR 32.70 / month**, goal ≈ **EUR 46 collected / month**); the EUR 22.90 is the **15 GB mailbox only**; **maximum EUR 100** per payment; a **top-25 supporters list** (highest first), planned **opt-in only** (GDPR consent, unchecked by default, Minecraft name only, 15+ or parent's agreement, nothing in game), ranked on the last 12 months with rounded totals (defaults, changeable).

44. **City control by events** (user idea 2026-11-11): a city is linked to **3 small places** (village, cave, …) where events happen; a faction that completes **more than 50 % of all the events controls the city for a limited time (e.g. 3 days)**. The map already reserves the 3 sites (`worldgen/map.md` §5). ✔ 2026-11-11: **the spawn city can be controlled**. **Described by the user 2026-11-11 (round 17)** and planned in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md): city zones (PvP + PvE, no block edits) with an event = waves + a big custom boss; the faction that resolves it controls the zone; > 50 % of the zones = the city. Remaining points are Open Questions 49–53.

**Round 17 (2026-11-11): cities, city zones, dungeon server, skinned GUIs** — plan [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) (§9 has the details of each question). Recommendations: own GUI skins in the `hatlas` pack (no ItemsAdder/Nexo); boss look by a model plugin, behaviour in our `boss/` code; **one dungeon server for all dungeons** (option B, as a pool), same jar with `server.role`; own handoff in PostgreSQL, no rubies in dungeons.
**Round 18 (2026-11-11)**: answers recorded in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) and the new [`docs/job-skills.md`](docs/job-skills.md). ✔ **option B** (one dungeon server).
45. ~~**Dungeons private PvE**~~ — ✔ answered 2026-11-11: private instances, **only players of the same faction**, party max **8** (config), **each player needs a key** validated at the entrance NPC; the damage-share calculation is dropped for dungeons. Dungeons rebuilt as **fight zones** (wave / mini-boss / boss, inner area starts, outer area = inner + radius pauses, waves cleared once, remaining mobs remembered, mob kills = faction XP only), void world with floating builds, run timeout 5 min, AFK 5 min, return after a configurable delay after the boss.
**Round 19 (2026-11-12)**: answers recorded in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) (§2 challenges C22–C31) and [`docs/job-skills.md`](docs/job-skills.md). Copies of a dungeon pasted with a void gap ≥ `max(view, simulation distance) + 1` chunks (✔ user); **city zone events become one shared dungeon run on the dungeon server, won by power score** (replaces round 18's fight zones with PvP in the real map).
46. ~~**Dungeon details**~~ — ✔ answered 2026-11-12: join mid-run while the faction's run is active, everyone at the same start spawn; **one run per faction per dungeon**; **cooldown 3 h per dungeon (config), tied to the player** (leaving/disbanding cannot skip it); death = keep inventory, **no drops at all** (players and mobs; only mini-boss/boss loot), gear can break; **10 min to reconnect**; run with nobody inside for 5 min = finished for the faction's members (cooldown starts); AFK 5 min = sent back; leaving by choice keeps loot and XP, no boss reward, cooldown starts. Open: OQ 67, 70.
47. ~~**Job skill trees**~~ — ✔ answered 2026-11-12: XP **from job quests only**; **the job and its tree belong to the player, with or without a faction, never reset on leaving** (replaces round 18); in a faction, quest XP is also won by the faction; tree = start node → ≥ 2 branches, each splitting into ≥ 2, choices permanent; nodes cost 1+ points, some link with other jobs' nodes; max level 50, 1 point per level, ~40 % of a tree; **Wizard NPC** removes one node for 1 *Magic reroller* (crafted by a Wizard with that node) + rubies; full reset = 3 rerollers + 3 × rubies, 7-day cooldown; others see role counts only. Open: OQ 64–66.
48. ~~**Jokeyrini per NPC**~~ — ✔ answered 2026-11-11/12: own pool per NPC, one active quest per player network-wide, **3 dungeon runs (and keys) per player per day**.
49. ~~**City control**~~ — ✔ answered 2026-11-11/12: **more than half** of the city's zones; nobody above half → **the previous owner keeps it**. Wording conflict with "kept while holding more than half": OQ 62.
50. ~~**City zone event winner**~~ — ✔ answered 2026-11-12: the event is **one dungeon run shared by every faction** on the dungeon server; **power score** per faction (mini-boss 10, boss × 2.5 = 25, config); when the boss dies, the best score takes the zone; then everyone back to where they entered. The holder keeps the zone during the event. Open: OQ 60, 62, 63.
51. ~~**Control duration and frequency**~~ — ✔ answered 2026-11-12: the zone is held until the next event is won by another faction; events trigger at a **random time 24–72 h** after the previous one (config). Open: play hours, announcement, timeout (OQ 61).
52. ~~**Rewards of control**~~ — ✔ answered 2026-11-12: daily faction XP by faction size (small / normal / big), **tax on the city's job shop sales 8 / 5 / 2 %** by size (config), **5 % discount**, exclusive Jokeyrini, title on the Mayor's board, **ruby mining right** in the city's ore zone; more proposals in the plan §6.4. Open: OQ 68, 69.
53. ~~**Mine zone**~~ — ✔ answered 2026-11-11: city zones protect blocks like safe zones, **ore zones stay minable** in every city zone.
54. ~~**GUI art**~~ — ✔ answered 2026-11-12: generator script + AI ornaments, no bought pack; a **skill `gui-art` + agent `gui-artist`** (with a user approval gate) to build; public art only as **CC0/licensed style references**, no extra MCP needed (plan §3).
55. ~~**Model plugin**~~ — ✔ answered 2026-11-12: **BetterModel** pilot; **no paid plugin** (ModelEngine dropped; fallback = our own display-entity models).
56. ~~**Instances**~~ — superseded 2026-11-11: blocks never change in a dungeon, so each type is **pre-pasted K times** and a party gets a free slot.
57. ~~**Launch scope**~~ — ✔ answered 2026-11-12: **everything** (cities, zones, events, dungeon server, job trees) ships at launch; the RAM kit is installed. Build order = plan §9 (closed beta suggested).
58. ~~**Code split**~~ — ✔ answered 2026-11-12: **`hatlas-dungeons`** plugin + **`hatlas-common`** library, Gradle composite build (§1.1, planned).
59. ~~**Skill tree display**~~ — ✔ answered 2026-11-12: skinned chest menu, background drawn by the `gui-art` generator; advancement tab maybe later (read-only).
60. ~~**City zone event run**~~ — ✔ answered 2026-11-13: **PvP on**, **no key**, **max 4 players per faction**; players spawn at a **random point in a circle** (centre + radius, default 8) set **per city zone by admin command** (stored in the database, not yml). Spawn protection etc.: OQ 71.
61. ~~**Event times**~~ — ✔ answered 2026-11-13: random time **only inside play hours** (Europe/Paris), announcements **30, 15 and 5 min** before, **timeout 60 min**; all in yml.
62. ~~**Keeping a city**~~ — ✔ answered 2026-11-13: a city **changes hands only when another faction holds more than half**. Timed-out event (holder keeps the zone): to confirm in OQ 72.
63. ~~**Power score**~~ — ✔ answered 2026-11-13: points to the faction of **the last hit** (so builds and cross-job combos matter, see [`docs/job-skills.md`](docs/job-skills.md) §3.4). Credit rules, 30 vs 25, ties: OQ 72.
64. ~~**Players without a faction**~~ — ✔ answered 2026-11-13: pay shops with **rubies in their own inventory**; **no Jokeyrini** (factions only); job switch **resets XP and tree**, **first switch free, then rubies**. Faction members' payment and price details: OQ 73.
65. ~~**Wizard**~~ — ✔ answered 2026-11-13: **the Wizard is the Alchemist**: a node (branch *Arcane*) of the Alchemist tree, no 6th job; the Wizard NPC stays.
66. ~~**Wizard node removal**~~ — ✔ answered 2026-11-13: **only an end node**.
67. ~~**Disconnect vs idle timeout**~~ — ✔ answered 2026-11-13: a disconnected player **counts as inside** during their 10 min; the inventory is **always sent back**, never deleted.
68. ~~**Ruby monopoly**~~ — ✔ answered 2026-11-13: **ore zones leave the faction server**; a **dedicated mining server** (own plugin, daily ore reset with warnings −1 h/−30/−15/−5 min and everyone sent back with their inventory, no PvP, PvE, caves linked by falls, vanilla + ruby ores, entrance NPCs without key, inventory moved by handoff); **each city has an entrance**, plus a **holder-only entrance to a sealed cave with +70 % ruby**. Plan [`docs/mining-world.md`](docs/mining-world.md); open points OQ 78–84.
69. ~~**Rewards details**~~ — ✔ answered 2026-11-13: tiers 1–4 / 5–24 / 25+, daily XP × 1.5 / 1.0 / 0.6, tax only on shops of jobs present in the holder; extras **+1 dungeon run, +10 % job XP, banners, welcome message, armour/weapon skins**; **no free teleport**; everything in yml. Skins: OQ 77.
70. ~~**Mini-boss and boss loot**~~ — clarified 2026-11-13 (user asked): "personal" = the loot table **rolled once per participant**, not one item copied; options in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) C35 → OQ 76.

**Round 20 (2026-11-13)**: answers recorded in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) (§2 challenges C32–C38), [`docs/job-skills.md`](docs/job-skills.md) (roles, combo kinds, generation method §3.4–3.6) and the new [`docs/mining-world.md`](docs/mining-world.md). Roles ✔ user: **Miner + Lumberjack = tanks, Alchemist + Farmer = healers, Hunter = damage**. Build order: epics jobs → dungeons → mining world → cities, **beta after each epic**.
71. ~~**Event spawn**~~ — ✔ answered 2026-11-16: **5 s spawn protection**, **no PvP between allies**, a free slot can be taken by another member, a player who left may come back after **`event.rejoin_cooldown_seconds: 60`** (yml); **several spawn circles** per dungeon (positions by command, DB), **radius default in yml**; never spawn inside a block; **`/dungeon doctor`** checks the setup ([`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) C40). Open: OQ 85, 86.
72. ~~**Last hit details**~~ — ✔ answered 2026-11-16: credit rules of C33; **3 mini-bosses (30) beat the boss (25), intended**; ties: holder keeps, else first to reach; **timed-out event: holder keeps the zone** (explained in C39, incl. the holder's stalling advantage). **Changed 2026-11-19 (round 23):** mini-bosses no longer give points but a **rune soul** to the last-hit faction; the zone changes hands only when the final boss dies (OQ 112, [`docs/runes.md`](docs/runes.md) §9).
73. ~~**Shops and job switch**~~ — ✔ answered 2026-11-16: **every player pays shops from their own inventory** (any role); the **vault is a chest only** (owner/BANKER deposit and take out, members deposit only), it no longer pays shops; job switch price **default in yml**, **24 h cooldown**. Auction house: OQ 89.
74. ~~**Skill tree generation**~~ — detailed 2026-11-16 ([`docs/job-skills.md`](docs/job-skills.md) §3.6.1, worked example); ✔ combo items usable by **any player with the node, any faction**. Approval: OQ 90.
75. ~~**Role flavours and branches**~~ — explained 2026-11-16 ([`docs/job-skills.md`](docs/job-skills.md) §3.2.1, sample branches and forks per job). Approval: OQ 91.
76. ~~**Loot**~~ — ✔ answered 2026-11-16: personal roll per participant + **bonus roll for the last hitter**; **participant = dealt damage** (not presence); inventory full → **drop at the player's feet**. Open: OQ 88.
77. ~~**Skins**~~ — ✔ answered 2026-11-16: only while the faction holds the city; one set per city.
78. ~~**Mining rules**~~ — ✔ partly 2026-11-16: no PvP, PvE on; items moved by the handoff (duplication question → [`docs/cross-server-items.md`](docs/cross-server-items.md)). Death rule not answered: OQ 94.
79. ~~**Mining reset**~~ — ✔ answered 2026-11-16: **06:00 Paris**, mine **closed 5 min**, **a new map every day** (noise caves: bigger cheese, spaghetti, noodles; structures in caves; ores up to +30 %; **+30 % of all ores in structure caves**, yml). Research and design: [`docs/mining-world.md`](docs/mining-world.md) §7. Open: OQ 95, 96.
80. ~~**Mining map**~~ — ✔ answered 2026-11-16: 2,000 × 2,000, a closed **"potato geode"** with an **unbreakable limit** all around, no surface; **no nether portals** in the mining and dungeon servers.
81. ~~**Miner quests**~~ — ✔ answered 2026-11-16: counted in the mining world like every job quest.
82. ~~**Faction island ores / amethyst cave**~~ — ✔ answered 2026-11-16: the island keeps vanilla ores; the **amethyst cave becomes an entrance to an amethyst region of the mining world**. Open: OQ 97.
83. ~~**Ruby supply**~~ — ✔ answered 2026-11-16: low ruby weights at launch; optional daily ruby cap per player (anti-cheat), **off by default** in yml.
84. ~~**Wild mine entrances**~~ — ✔ answered 2026-11-16: 3 at the free event sites, each to **its own landing at the most opposite points** of the mining map. Open: OQ 97.

**Round 21 (2026-11-16)**: answers recorded in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) (§2.1, C39–C44: timeout explained, `/dungeon doctor`, unified `/dungeon create <dungeon|city>`), [`docs/job-skills.md`](docs/job-skills.md) (§3.2.1 roles explained, §3.6.1 method in detail), [`docs/mining-world.md`](docs/mining-world.md) (daily new map, cave generation research §7) and two new plans: [`docs/cross-server-items.md`](docs/cross-server-items.md) (no duplication by design + **travel bag** faction skill) and [`docs/economy-observatory.md`](docs/economy-observatory.md) (ruby observatory, privacy, price index challenged).
85. ~~**Event rejoin**~~ — ✔ answered 2026-11-19: rejoin after **60 s** (yml); restocking at home accepted.
86. ~~**Spawn circles per faction**~~ — ✔ answered 2026-11-19: each faction spawns in **its own circle, picked at random** from the dungeon's circles.
87. ~~**Unified dungeon commands**~~ — ✔ answered 2026-11-19: `/dungeon create <dungeon|city> <name>`, **`/donjon` removed**, **`/dungeon doctor <name>`** for dungeons and city dungeons.
88. ~~**Loot participant**~~ — ✔ answered 2026-11-19: any damage + assists (heal or taunt on a player who hit); a dropped item is locked to its owner.
89. ~~**Auction house payment**~~ — ✔ answered 2026-11-19: buyers pay from their own inventory; the money still goes to the seller's faction vault.
90. ~~**Tree method**~~ — ✔ answered 2026-11-19: approved; steps 1–3 for all jobs, then **Miner + Hunter first**. Runes join steps 1–3 ([`docs/runes.md`](docs/runes.md)).
91. ~~**Role flavours**~~ — ✔ answered 2026-11-19: OK as written ([`docs/job-skills.md`](docs/job-skills.md) §3.2.1).
92. ~~**Economy observatory**~~ — ✔ answered 2026-11-19: **public totals only**; each player sees their own history and their faction's vault when logged in.
93. ~~**Price index**~~ — ✔ answered 2026-11-19: **no price index**; prices are yml values, the observatory suggests, admins apply by hand; automatic ±5 %/week only after the beta; **mining output is the first lever**.
94. ~~**Mining death**~~ — ✔ answered 2026-11-19: armour, hotbar and off-hand kept; **loot goes only into the travel bag**; on death the bag drops as a **lost bag** any player can loot, **despawn time in yml** ([`docs/mining-world.md`](docs/mining-world.md) M15). Details: OQ 114.
95. ~~**Mining generation**~~ — ✔ answered 2026-11-19: next map built at 04:45 by a generator container; datapack + our own passes; **one daily ore factor 1.00–1.30**.
96. ~~**Cave structures**~~ — ✔ partly 2026-11-19: **only our own structures** (no vanilla ancient cities, trial chambers…), no villagers or golems; user idea: a skill + agent to generate them. Which ones: OQ 116.
97. ~~**Landings**~~ — ✔ answered 2026-11-19: ring layout; each entrance leads to **its own spot chosen by each day's generation** (skinned entrance menu). Details: OQ 115. **All portals** (nether, end, any) blocked on the mining and dungeon servers.
98. ~~**Travel bag**~~ — ✔ answered 2026-11-19: the duplication protocol of [`docs/cross-server-items.md`](docs/cross-server-items.md) §2; only **hotbar, armour, off-hand and the travel bag** travel, the main inventory stays home.
99. ~~**Bag sizes**~~ — ✔ answered 2026-11-19: **4 / 8 / 12 / 18 / 27** as a faction skill like the vault.

**Round 22 (2026-11-17)**: **boss pipeline** (user request: 3 mini-bosses + 1 boss per dungeon type, full Blockbench models, animations, sounds, Dark Souls-like phases) planned in [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) §4.1–4.4: `boss.yml` spec per boss, `.bbmodel` written by script then polished by the user, skill `boss-building` with one agent per step and user gates, no AI mesh generators.
100. ~~**Boss agents and models**~~ — ✔ answered 2026-11-18: one agent per step with a user gate; **Fable 5.2** for the designer (and the modeler in the pilot, then compared with Opus), **Opus 5.5** for animator, sound, coder, tester.
101. ~~**Blockbench MCP**~~ — ✔ answered 2026-11-18: `.bbmodel` written by script, polished by the user; a pinned community Blockbench MCP plugin **for previews and small live edits only**.
102. ~~**`boss.yml` format**~~ — ✔ answered 2026-11-18: the draft of [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) §4.1 is approved (tuned by the pilot).
103. ~~**Boss sounds**~~ — ✔ answered 2026-11-18: **mostly AI generated** (tool plan allowing commercial use, prompt + plan + date in `sounds/LICENSES.md`), vanilla only as filler, AI music loop per final boss (§4.3).
104. ~~**Pilot boss**~~ — ✔ answered 2026-11-18: the **Fungal Root** (called Fungal Witch until 2026-11-20), a `dark_forest` mini-boss (spore poison zones, mushroom minions, teleports between trees), through the whole pipeline first (§4.4).

**Round 23 (2026-11-19)**: answers to OQ 85–99 recorded; **OQ 72 changed**: mini-bosses give **rune souls** instead of power points, the zone changes hands only when the final boss dies. New feature **Runes** (elements Fire / Frost / Storm / Nature for the job skills, effect catalogue with buff ⇄ debuff opposites and counters, combat rules, Summoner for the Alchemist; research from League of Legends and Magic: The Gathering): [`docs/runes.md`](docs/runes.md). Mining: death and lost bag, landings chosen each day, own structures only + a structure skill/agent ([`docs/mining-world.md`](docs/mining-world.md) M12–M16).
105. **Runes**: Fire, Frost, Storm, Nature with the wheel Fire > Frost > Storm > Nature > Fire, soft ±15 % (recommended)? A 5th rune (Arcane/Ender) later (recommended)?
106. **Runes per job**: Miner Frost + Fire, Lumberjack Nature + Storm, Hunter Fire + Storm, Farmer Nature + Frost, Alchemist Fire + Nature (recommended), or changes?
107. **Specialities in the trees**: forks become rune choices, rune power per node of one rune, max 2 bridge nodes per tree unlocking another rune's skill (recommended)?
108. **Effects and combat rules** ([`docs/runes.md`](docs/runes.md) §4, §6): catalogue with opposites and counters; no stacking of the same effect, diminishing returns on controls, stun 1 s PvP / 2 s PvE, 0.5 s telegraph on zones, lower PvP values (recommended)?
109. **Casting**: one Rune focus item, right-click casts, F cycles 3 active skills, native cooldowns (recommended)?
110. **Rune power / rune resistance** (AP/AD idea): rune damage ignores armour but is reduced by a new rune resistance stat (recommended)?
111. **Summoner** (Alchemist only): max 2 minions, 15 s, weak, follow and attack the Alchemist's target; countered by area damage, banish, taunt (recommended)?
112. **Rune souls**: rune per mini-boss in `boss.yml` (the Fungal Root = Nature), soul to the last-hit faction until the event ends, +10 % rune power + one perk, only for that rune's players; **zone to the faction of the last hit on the final boss** (power score removed) (recommended)? Mini-boss runes drawn per event (recommended) or fixed? Same in private dungeons (recommended)?
113. **Balance**: composition validator ([`docs/runes.md`](docs/runes.md) §11) (recommended)? Bosses immune to stun and root, slows halved (recommended)?
114. **Mining death details**: bag full → items stay on the ground; lost bag despawns after 300 s; items packed in the bag before entering are lost too; fall damage on with water at big falls; block placing allowed (all recommended)?
115. **Mining landings**: one sector of the ring per entrance, the generator picks the spot; skinned entrance menu (destination, today's ore bonus, closing time) (recommended)? Amethyst region open to everyone (recommended) or a city reward?
116. **Cave structures**: skill `cave-structures` + agent `structure-builder` with a user gate (recommended)? At launch: forest hollow, farming village, alchemist ruins, dwarven halls (recommended)? Amethyst geodes (a vanilla feature) allowed in the amethyst region (recommended)?

**Round 24 (2026-11-20)**: boss **phase mechanics** (user): protector minions that must all die before the boss can be damaged, a heal channel stopped by damage (may start the next phase), optional side waves; minions are pipeline characters (`kind: minion`), the **Dark Mushroom** first, with the Fungal Root; sound tools and music budget. Plan [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) §4.3–4.5.
117. ~~**Protectors**~~ — ✔ answered 2026-11-20: as proposed (immune until all dead, 3 + 1 per player above 2, max 8, any death counts, lost ones respawn, enrage runs, Banish damages instead of removing).
118. ~~**Heal channel**~~ — ✔ answered 2026-11-20: threshold **scaled by party**: 8 % + 2 % per player above 2, after the damage cap; 3 s stagger; never above the phase ceiling.
119. ~~**Side waves**~~ — ✔ answered 2026-11-20: optional, mob cap, despawn at phase end, **no faction XP** and no drops.
120. ~~**Minions in the pipeline**~~ — ✔ answered 2026-11-20: `kind: minion` (≤ 40 cubes, ≤ 64×64, 5 animations), Dark Mushroom made with the Fungal Root.
121. ~~**Sound tools**~~ — ✔ answered 2026-11-20: ElevenLabs Sound Effects (paid, API) for effects and voices, Suno Pro/Premier by the user for music; final boss one track per phase, mini-boss one, minions none.
122. ~~**Reference images**~~ — ✔ answered 2026-11-20: third-party refs are mood only, kept in git-ignored `bosses/**/refs/private/`; the design stays our own.

**Round 25 (2026-11-20)**: Fungal Witch renamed **Fungal Root**; step 1 iteration 4 choices ✔ (spit jaw opens sideways, jaws kept, Dark Mushroom 5 long fangs, **final bosses 6–7 blocks tall**). User ideas: any boss may summon when it fits; **hit zones** (weak points, armoured parts) and **mutations** during a fight. Plan [`docs/cities-and-dungeons.md`](docs/cities-and-dungeons.md) §4.5–4.6.
123. **Hit zones**: per-bone hitboxes of BetterModel (ray test fallback), multipliers 0.5–2.0 before the damage cap, weak points visible and reachable, at least one weak and one armoured zone per boss (recommended)?
124. **Mutations**: same entity, hidden/shown bones of the same `.bbmodel` + transition animation + another animation set, behaviour changed in code; a second model only for a whole new body, swapped on the same entity (recommended)?
125. **Breakable parts**: a zone with its own HP whose break triggers the mutation early, with a reward (recommended)?
126. **Fungal Root**: add hit zones (eyes ×1.75, sap bulb ×1.5 and double against the heal, legs ×0.5) and the mutation "spit root torn off" (below 10 % HP or when broken: no more `spore_cloud`, faster) in an extra step 1 round, beyond the cap of 3 (recommended), or after the pilot?

## Changelog

The changelog lives in [`docs/claude-changelog.md`](docs/claude-changelog.md). Read it at session start and append an entry (newest first) after every change.
