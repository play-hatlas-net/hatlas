# Server tuning and hardening guide (admin, 2026-11-09)

> **Status: guide for the production install** (`docs/deployment.md`, M2 step 7). Nothing here is
> built yet. Values are starting points for **2 × Xeon E5-2698 v3, 16 GB RAM (one CPU holds it all), Debian, docker compose**,
> **40 players** expected. Every change is tried on the test server first, then measured in production
> with spark (§5). Key names follow the Paper 1.21 docs: on the first start, compare with the files
> Paper generates and fix any key that moved.

Contents: 1. machine and compose priorities · 2. JVM flags · 3. Velocity · 4. Paper and server files
· 5. plugins (security, anti-cheat, anti-bot, admin, performance) · 6. launch checklist.

---

## 1. Machine and compose: giving the faction server priority

### 1.1 The real memory layout (measured by the user, 2026-11-10)
- `numactl --hardware`: **one NUMA node**, 64 logical CPUs, 15.9 GB.
- `dmidecode -t memory`: **only two modules**, 2 × 8 GB G.Skill `F4-2133C15-8GNT` (DDR4-2133,
  **non-ECC, unbuffered**). ✔ Second reading (2026-11-10, after the user reseated them): `DIMM_C1`
  (bank "NODE 2") and `DIMM_G1` (bank "NODE 4"). dmidecode lists **24 slot entries = 8 channels × 3**:
  `C1` is entry 7 (channel C, first CPU), `G1` is entry 19 (channel G, second CPU). So today **one
  module per CPU, one channel each**, and the BIOS shows a single NUMA node because it interleaves
  memory across both sockets (NUMA off): every core reaches half of the RAM through QPI.

What it means:
1. **No per-node memory binding**: with one node, `numactl --membind` and `cap_add: SYS_NICE` are
   useless and dropped from this guide.
2. **One CPU is "far" from all the memory.** Its cores reach the RAM through the link between the
   two CPUs (QPI), with more latency. **Pin the faction server to the cores of the CPU that holds the
   modules**; put the services that care less (Postgres, website, Caddy, backups) on the other one.
   Find which CPU it is:
   ```bash
   lscpu -e=CPU,SOCKET,CORE                 # which logical CPUs are socket 0 / socket 1
   sudo apt install sysbench
   taskset -c 0  sysbench memory --memory-block-size=1K --memory-access-mode=rnd --time=10 run
   taskset -c 16 sysbench memory --memory-block-size=1K --memory-access-mode=rnd --time=10 run   # a CPU of the other socket (from lscpu)
   ```
   The socket with the clearly higher MiB/sec owns the modules.
   ✔ Measured 2026-11-10: **socket 0 = CPUs 0–15 + 32–47, socket 1 = CPUs 16–31 + 48–63** (hyper-thread
   siblings offset by 32). Today one module sits on each CPU (see above), so neither socket is
   "near" all the memory until the move. The RAM plan (`docs/deployment.md` §2.6) moves all modules to the first
   CPU (socket 0), so the faction server gets `cpuset: "0-15,32-47"`; the sysbench test confirms it
   after the move.
3. **Single channel per CPU today** (`C1` + `G1`). Until the new modules arrive, putting both in
   `DIMM_C1` + `DIMM_D1` (two channels of the first CPU) already gives dual channel and keeps all the
   memory near socket 0. Minecraft cares more about latency than bandwidth, but GC and chunk loading
   benefit.
4. **No ECC**: a memory error is not detected or corrected. Rare, accepted; the daily backups and
   `pg_dump` verification cover the damage it could do.
5. **Upgrade** (✔ user, Open Question 39): two more identical modules → **4 × 8 GB = 32 GB**, one
   per channel on the first CPU (quad channel). Shopping list and how to move the modules:
   `docs/deployment.md` §2.6. With 32 GB the limits of §1.3 can grow (faction heap 10 GB, more disk
   cache); keep 7 GB until the load test shows a need.

### 1.2 Host settings (`/etc/sysctl.d/90-hatlas.conf`, kernel)
```
vm.swappiness = 10            # swap only under real pressure (a swapping JVM freezes the game)
vm.max_map_count = 262144     # room for the JVMs and Postgres
net.core.somaxconn = 1024
```
- CPU frequency: `sudo apt install linux-cpupower && sudo cpupower frequency-set -g performance`
  (persist with a systemd unit): keeps the cores at turbo speed instead of ramping up on each tick.
- Transparent huge pages: `echo madvise > /sys/kernel/mm/transparent_hugepage/enabled` (persist with
  a systemd unit or the kernel cmdline); the JVM asks for them with `-XX:+UseTransparentHugePages`.
- The 16 GB swap stays as a safety net, but **each container gets a hard memory limit** (§1.3) so one
  service cannot push the faction server into swap.
- Docker uses cgroup v2 on Debian 12/13: `mem_swappiness` per container is ignored there; use
  `memswap_limit` = `mem_limit` (no swap for that container) instead.

### 1.3 Compose keys, per service (`deploy/game/compose.yml` + webapp compose)

| Service | `cpuset` (example) | `mem_limit` / `memswap_limit` | `mem_reservation` | `cpu_shares` | `oom_score_adj` | `stop_grace_period` |
|---|---|---|---|---|---|---|
| **faction** | socket with the RAM, e.g. `"0-15,32-47"` | **8.5g** / 8.5g (heap 7 G + ~1.5 G off-heap) | 8g | 4096 | **-800** | 120s |
| velocity | same socket, e.g. `"12-15,44-47"` (shared, light) | 1g / 1g (heap 512 M) | 768m | 2048 | -500 | 30s |
| hub | other socket, e.g. `"16-31,48-63"` | 1.2g / 1.2g (heap 768 M) | 1g | 1024 | -300 | 60s |
| postgres | other socket | 1.5g / 1.5g | 1g | 2048 | -600 | 60s |
| webapp | other socket | 512m / 512m | 256m | 512 | 0 | 15s |
| caddy (+ static landing) | other socket | 128m / 128m | 64m | 512 | 0 | 10s |
| ovh-ddns | other socket | 64m / 64m | — | 128 | 0 | 5s |
| total limits | | **≈ 12.9 GB** of 15.5 GB usable (leaves ~2.6 GB for the OS and disk cache) | | | | |

Capacity reasoning (40 players): `docs/deployment.md` §2.10.

What each key does:
- **`cpuset`**: the only CPUs the container may run on. The isolation that matters most here.
- No memory-node binding: there is a single node (§1.1); the "priority on memory" is obtained by
  pinning to the socket that holds the modules and by the hard limits below.
- **`mem_limit` / `memswap_limit`**: hard limit, no swap for that container. Set it above the heap:
  a JVM also uses metaspace, thread stacks, direct buffers (Netty), GC structures.
- **`mem_reservation`**: soft floor used when the host is short on memory.
- **`cpu_shares`**: relative weight, only used when CPUs are contended (rare with 64 threads, but
  free to set).
- **`oom_score_adj`**: if the kernel must kill something, it kills the website before Postgres and
  the faction server. Never `oom_kill_disable` (the host could hang).
- **`stop_grace_period`**: time for `docker compose stop` before SIGKILL. Paper must save every world;
  too short = corrupted chunks. `update.sh` stops the game through RCON `stop` first anyway.
- Also on every service: `restart: unless-stopped`, `init: true`, a `healthcheck`,
  `depends_on: { postgres: { condition: service_healthy } }`, `ulimits: { nofile: 65536 }`,
  `logging: { driver: local, options: { max-size: "20m", max-file: "5" } }`.
- **Disk I/O**: `blkio_config.weight` needs the BFQ scheduler; NVMe uses `none`, so it is ignored.
  Instead the backup script runs `ionice -c3 nice -n19` and writes to the second disk (`sda`).
- **No `ports:`** except Caddy (80, 443) and Velocity (25565): Docker bypasses ufw
  (`docs/deployment.md` §2.4).

Example (faction):
```yaml
faction:
  image: hatlas/paper:1.21.11
  cpuset: "0-15,32-47"            # the socket that holds the RAM (§1.1), from lscpu + sysbench
  mem_limit: 8.5g
  memswap_limit: 8.5g
  mem_reservation: 8g
  cpu_shares: 4096
  oom_score_adj: -800
  stop_grace_period: 120s
  init: true
  restart: unless-stopped
  ulimits: { nofile: 65536 }
  environment: { JAVA_HEAP: 7G }
  volumes: [ "/srv/hatlas/faction:/data" ]
  networks: [ hatlas-mc, hatlas-db ]   # no ports: reachable only through Velocity
```

---

## 2. JVM flags

Faction server (Java 25, heap 7 GB): **G1 with the well-known "Aikar" flags**, the most tested set
for Paper.
```
java -Xms7G -Xmx7G -XX:+AlwaysPreTouch -XX:+UseTransparentHugePages \
  -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 \
  -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 \
  -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 \
  -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar paper.jar --nogui
```
- `-Xms` = `-Xmx` + `AlwaysPreTouch`: the whole heap is reserved and touched at start, no surprise
  allocation later (and the container limit is hit at start, not at peak hour, if it is too low).
- If Java 25 refuses a flag at start (removed options), delete that flag; obsolete ones only warn.
- Alternative to measure later: generational ZGC (`-XX:+UseZGC`), shorter pauses, more memory.
  Change only if spark shows GC pauses as the lag source.
- Hub: same flags with `-Xms768M -Xmx768M`. Velocity: `-Xms512M -Xmx512M -XX:+UseG1GC
  -XX:G1HeapRegionSize=4M -XX:+UnlockExperimentalVMOptions -XX:+ParallelRefProcEnabled
  -XX:+AlwaysPreTouch` (Velocity's recommended set).

---

## 3. Velocity (`velocity.toml`), offline network

| Key | Value | Why |
|---|---|---|
| `online-mode` | `false` | decided (Open Question 32); our login replaces Mojang's |
| `force-key-authentication` | `false` | offline clients have no signed chat keys |
| `player-info-forwarding-mode` | `"modern"` | the backends trust only the proxy |
| `forwarding-secret-file` | long random secret, file mode 600 | the same secret on hub and faction |
| `kick-existing-players` | `false` | a second login with an online name is **refused**, it does not kick the real player |
| `prevent-client-proxy-connections` | `false` (offline) | Mojang check, not used offline |
| `[servers] try` | `["hub"]` only | nobody lands on the faction server directly |
| `[advanced] compression-threshold` | `256` | Velocity compresses for players |
| `[advanced] login-ratelimit` | `3000` (ms per IP) | first anti-bot layer (Sonar adds more, §5.1) |
| `[advanced] connection-timeout` / `read-timeout` | `5000` / `30000` | |
| `[advanced] haproxy-protocol` | `false` | no load balancer in front |
| `[advanced] log-command-executions` | `true` | audit of staff commands |
| `[advanced] log-player-connections` | `true` | |
| `[query] enabled` | `false` | nothing to expose |
| `show-max-players` | e.g. `100` | |

---

## 4. Paper and server files (faction server unless noted)

### 4.1 `server.properties` (backends)
```
online-mode=false                   # Velocity handles identity
enforce-secure-profile=false
prevent-proxy-connections=false
server-ip=                          # listens on the Docker network only; never published
server-port=25565                   # inside the container, not the host
network-compression-threshold=-1    # Velocity compresses towards players; backend ↔ proxy on the same host
view-distance=8
simulation-distance=6
sync-chunk-writes=false             # faster saves; backups cover a crash
enable-rcon=true                    # Docker network only, long password from .env
enable-query=false
spawn-protection=0                  # Hatlas safe zones protect the spawn
max-players=100
hide-online-players=false
allow-flight=true                   # let the anti-cheat judge flight; vanilla's check kicks on lag
entity-broadcast-range-percentage=100
```
Hub: `view-distance=6`, `simulation-distance=4`, no mobs (`spawn-monsters=false`,
`spawn-animals=false`), `difficulty=peaceful`.

### 4.2 `config/paper-global.yml`
```yaml
proxies:
  velocity:
    enabled: true
    online-mode: false
    secret: "<same as Velocity's forwarding secret>"
  bungee-cord: { online-mode: false }
chunk-loading-basic:
  player-max-chunk-load-rate: 100.0
  player-max-chunk-generate-rate: -1.0    # the world is pre-generated (Chunky); see world border below
  player-max-chunk-send-rate: 75.0
packet-limiter:
  kick-message: "<red>Too many packets"
  limits:
    all: { interval: 7.0, max-packet-rate: 500.0 }
    ServerboundPlaceRecipePacket: { interval: 4.0, max-packet-rate: 5.0, action: DROP }
spam-limiter:
  incoming-packet-threshold: 300
  tab-spam-increment: 1
  tab-spam-limit: 500
unsupported-settings:
  allow-piston-duplication: false
  allow-permanent-block-break-exploits: false
  allow-headless-pistons: false
collisions:
  enable-player-collisions: true
```

### 4.3 `config/paper-world-defaults.yml`

**Anti-xray** (built into Paper, no plugin needed):
```yaml
anticheat:
  anti-xray:
    enabled: true
    engine-mode: 3            # like 2 (fake ores everywhere) but randomised per chunk layer: ~half the join traffic
    max-block-height: 64      # ores above are not hidden; raise to 128 if players xray diamonds high (1.18+ ore heights)
    update-radius: 2
    lava-obscures: false
    use-permission: false
    hidden-blocks: [air, copper_ore, deepslate_copper_ore, raw_copper_block, diamond_ore, deepslate_diamond_ore,
      gold_ore, deepslate_gold_ore, iron_ore, deepslate_iron_ore, raw_iron_block, lapis_ore, deepslate_lapis_ore,
      redstone_ore, deepslate_redstone_ore]
    replacement-blocks: [chest, amethyst_block, andesite, budding_amethyst, calcite, coal_ore, deepslate_coal_ore,
      deepslate, diorite, dirt, emerald_ore, deepslate_emerald_ore, granite, gravel, oak_planks, smooth_basalt,
      stone, tuff]
```
- `air` in `hidden-blocks` also hides ores next to caves (stronger, can cost FPS on weak PCs): keep
  it, remove it if players complain.
- Nether (`world_nether/paper-world.yml`): `max-block-height: 128`, hide `ancient_debris`,
  `nether_gold_ore`, `nether_quartz_ore`.
- **Hatlas ruby ore is a note block** (§4.10 of `CLAUDE.md`), so anti-xray does not know it. It only
  exists inside **ore zones**; if an ore zone is underground and xray there matters, try adding
  `note_block` to `hidden-blocks` **on the test server first** (the fake blocks would show as plain
  note blocks, and `BlockListener` re-applies the ruby state on updates: check that a revealed ruby
  ore still shows as ruby).
- Optional, stronger: **RayTraceAntiXray** (by the author of Paper's anti-xray) hides ores until a
  player has line of sight; costs CPU on async threads, which this machine has plenty of. Only if
  xray is still seen.

**Performance and gameplay safety:**
```yaml
chunks:
  max-auto-save-chunks-per-tick: 8
  prevent-moving-into-unloaded-chunks: true
  entity-per-chunk-save-limit: { arrow: 16, experience_orb: 16, snowball: 8, ender_pearl: 8, egg: 8,
    small_fireball: 8, fireball: 8, wither_skull: 4, dragon_fireball: 3 }
entities:
  spawning:
    despawn-ranges:
      monster: { soft: 30, hard: 56 }
  armor-stands: { tick: false, do-collision-entity-lookups: false }   # Hatlas uses TextDisplays, not armor stands
  behavior:
    nerf-pigmen-from-nether-portals: true
collisions:
  max-entity-collisions: 2
  fix-climbing-bypassing-cramming-rule: true
environment:
  optimize-explosions: true      # TNT raids and creeper eggs: cheaper explosions (test raids on the test server)
  treasure-maps: { find-already-discovered: { loot-tables: true, villager-trade: true } }
hopper:
  cooldown-when-full: true
  disable-move-event: false      # MUST stay false: RubyRestrictionListener uses InventoryMoveItemEvent to stop rubies in hoppers
  ignore-occluding-blocks: true
tick-rates:
  mob-spawner: 2
  grass-spread: 4
  container-update: 1
misc:
  redstone-implementation: ALTERNATE_CURRENT   # same behaviour as vanilla in practice, much cheaper
  update-pathfinding-on-block-update: false
```
- **Do not add `emerald` to `alt-item-despawn-rate`**: the ruby gem is an emerald item; a dropped ruby
  that vanishes writes a `LOST` row in the ledger. Hatlas's own item clear (`ItemClearManager`,
  every 20 min) already cleans the ground.
- `entities.spawning.spawn-limits` / `bukkit.yml spawn-limits`: start with `monster: 50`,
  `animal: 10`, `water-animal: 5`, `ambient: 1` (vanilla 70/10/5/15), raise if the world feels empty.

### 4.4 `spigot.yml`
```yaml
world-settings:
  default:
    entity-activation-range: { animals: 16, monsters: 24, raiders: 48, misc: 8, water: 8, villagers: 16, flying-monsters: 48 }
    tick-inactive-villagers: false
    merge-radius: { item: 3.0, exp: 4.0 }     # Hatlas keeps rubies of different owners apart itself
    nerf-spawner-mobs: true
    entity-tracking-range: { players: 48, animals: 48, monsters: 48, misc: 32, display: 128, other: 64 }
    hopper-amount: 1
settings:
  log-villager-deaths: false
  log-named-deaths: false
```
Donjon waves spawn mobs next to players, so the activation ranges above do not freeze them.

### 4.5 Pre-generation and world border
1. Set the border first: `/worldborder set 10000` (radius 5,000 blocks around the spawn; size to the
   expected player count, about 2,500–5,000 blocks of radius for a few dozen players).
2. `/chunky radius 5000` → `/chunky start` in the overworld, then Nether (radius 1/8) and End,
   **before opening** (hours; uses many cores, fine here).
3. Keep the border at the pre-generated size (ChunkyBorder or vanilla border) so no player triggers
   generation; enlarge both together later.
4. Back up the pre-generated world: it becomes the restore base.

---

## 5. Plugins

Rules: download only from **Modrinth, Hangar or the project's GitHub releases**, pin versions in
`deploy/game/versions.env`, test every new plugin or update on the test server with Hatlas before
production, read each plugin's permissions and give `*` to nobody.

### 5.1 Security: bots, cheats, xray

| Plugin | Where | Role | Notes |
|---|---|---|---|
| **Sonar** | Velocity | Anti-bot: verifies new connections (gravity / collision checks, optional captcha map) and throttles joins during a bot attack, before players reach the hub | Free, open source, Velocity. Runs **before** our `/register` / `/login` flow: complements the per-IP limits of `docs/identity.md` §2.1. Whitelist verified players so regulars are checked once |
| **GrimAC** | faction server (and hub if wanted) | Anti-cheat (movement, reach, killaura, fly, speed…), prediction-based, few false positives | Free, open source, uses packetevents: check on the test server that it works **next to the standalone packetevents 2.14.0** Hatlas needs. **Test it with OldCombatMechanics** (1.8 PvP changes reach and attack timing; tune or exempt checks that misfire). Start with alerts only (staff), punish later |
| Paper anti-xray | built in | §4.3 | |
| RayTraceAntiXray | faction | optional, §4.3 | |

Paid alternatives if Grim is not enough: Vulcan, Polar (stronger, cost per month).

### 5.2 Administration and moderation

| Plugin | Where | Role | Notes |
|---|---|---|---|
| **LuckPerms** | Velocity + hub + faction | Permissions (Hatlas declares `hatlas.*` nodes); staff groups; **empty `ops.json`** | Stores in **PostgreSQL** (own schema/role, add it to the backups); same data on every server |
| **LibertyBans** | Velocity | Bans, mutes, warnings across the network, history | Free, PostgreSQL. Ban by **UUID** (stable thanks to our accounts); avoid IP bans (shared and dynamic IPs). Later: a ban also cancels the player's subscription (CGU, parked Stripe questions) |
| **CoreProtect** | faction | Block and container logging + rollback: griefing and raid disputes, staff abuse | SQLite file on the faction volume (no PostgreSQL support); `/co purge t:30d` monthly so it does not grow forever; exclude from the hourly copy if large |

### 5.3 Performance and player experience

| Plugin | Role |
|---|---|
| **spark** | Profiler (`/spark profiler`, `/spark health`, `/spark gc`). Paper 1.21 bundles it: if `/spark` already exists, do not install it |
| **Chunky** (+ ChunkyBorder) | Pre-generation and border (§4.5) |
| (none) | No "clear lag" plugin: Hatlas has `ItemClearManager`; Paper's entity limits do the rest |

Not installed on purpose: **ViaVersion** (other client versions; adds attack surface and bugs; only
if players ask), Geyser/Floodgate (Bedrock), anything that edits chat links (D22: player links stay
non-clickable).

### 5.4 Never in production
VitaminMCP (test bots), `/reload`-type plugins (PlugMan), anything giving console access over HTTP.

---

## 6. Launch checklist (admin)

1. `lscpu -e` + the `sysbench` test (§1.1) → the socket that holds the RAM; write the real `cpuset`
   values in compose; CPU governor `performance`.
2. sysctl + THP (§1.2), Docker installed, the old Minecraft server **deleted** (not migrated, Open
   Question 40) and the old nginx/certbot stack stopped (Caddy takes 80/443, Open Question 37).
3. Secrets in `.env` files (mode 600): Velocity forwarding secret, RCON, DB roles, LuckPerms /
   LibertyBans roles.
4. Configs from §3–§4 in `deploy/game/` templates; plugins from `versions.env`.
5. World pre-generated with the border set (§4.5), then a backup.
6. Start: `docker compose up -d`, then check `docker stats`
   (memory under limits), `/spark health`, TPS 20 with a few players.
7. From outside: only 80, 443 and 25565 answer (`docs/deployment.md` §3 task 7).
8. First week: `/spark profiler` during peak hours, Grim alerts reviewed daily before turning on
   punishments, CoreProtect purge scheduled.
