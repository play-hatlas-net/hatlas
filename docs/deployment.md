# Production deployment (plan, 2026-11-08)

> **Status: plan only.** The last task of the identity build order (`docs/identity.md`, `CLAUDE.md` M2):
> deploy every service on the user's private machine and test the whole chain there.
> Decided (✔ user 2026-11-08/09): docker compose, updated by hand with scripts, one private Debian
> machine behind the user's router, no SSH from outside, router opens **80, 443 and 25565** only.

## 1. What runs

```
Internet ─▶ router ─┬─ 80+443/tcp ─▶ caddy (TLS, HTTP→HTTPS) ─▶ hatlas-webapp (Node, :3000)
                    └─ 25565/tcp ─▶ velocity (hatlas-proxy)
                                     ├─ hub      (Paper + hatlas-hub)   not published
                                     └─ faction  (Paper + Hatlas)       not published
                    postgres (schemas hatlas + web)                     not published, 127.0.0.1 only
LAN only: SSH, RCON, VitaminMCP (never installed in production)
```

| Service | Image | Repo that owns it | Networks |
|---|---|---|---|
| postgres | `postgres:17-alpine` | `hatlas/docker/postgres` (+ `init/10-roles.sh`) | `hatlas-db` |
| velocity | `eclipse-temurin:25-jre` + Velocity jar + hatlas-proxy jar | **here**, `deploy/game/` | `hatlas-mc`, `hatlas-db`; publishes 25565 |
| hub, faction | `eclipse-temurin:25-jre` + Paper 1.21.11 + plugins | **here**, `deploy/game/` | `hatlas-mc`, `hatlas-db` |
| webapp | `ghcr.io/play-hatlas-net/hatlas-webapp:sha-…` | `hatlas-webapp/deploy/compose.yml` | `hatlas-db`, `hatlas-web` |
| caddy | `caddy:2-alpine` | `hatlas-webapp/deploy/` (edge, Open Question 15 there) | `hatlas-web`; publishes 80 and 443 |

- Backends bound to the internal network only, Velocity **modern forwarding** with a long random
  secret (`docs/identity.md` §7.5): with offline mode, a reachable backend port would bypass the login.
- Plugin jars come from the GitHub releases / CI artifacts of each repo, pinned by version in
  `deploy/game/versions.env`; worlds and plugin data in named volumes / bind mounts under `/srv/hatlas`.

## 2. The machine (✔ user 2026-11-09) and what it implies

| Fact | Value |
|---|---|
| OS | Debian, private fixed LAN IP behind the user's router |
| CPU | 2 × Intel Xeon E5-2698 v3 (Haswell, 2014): 32 cores / 64 threads, 2.3 GHz base, 3.6 GHz turbo, 2 NUMA nodes |
| RAM | 16 GB = **2 × 8 GB non-ECC DDR4-2133 UDIMM, in `DIMM_C1` (first CPU) and `DIMM_G1` (second CPU)**, one channel each, BIOS interleaves them into one NUMA node (`docs/server-tuning.md` §1.1) (+ 16 GB swap); about 8.5 GB in use today by the **current Minecraft server and website**, freed when they are replaced (✔ user, Open Question 36) |
| Disk | NVMe Crucial P3 1 TB (807 GB free; swap partition 16 GB) + **`sda` PNY 120 GB SATA SSD** |
| Router | NAT to this machine only: **80, 443, 25565** (✔ user checked, Open Question 38) |
| DNS | OVH zone `hatlas.net`; the A record `play` is updated by the user's **`ovh-ddns`** container (OVH API, every 5 min, TTL 300), see §2.5 |
| TLS | Let's Encrypt for `play.hatlas.net` today by the **`landing-website`** stack (nginx + certbot, HTTP-01 webroot), see §2.3 |

Challenges:
1. **RAM budget.** Planned: faction server heap 6 GB (+ ~1 GB JVM overhead), hub 1 GB, Velocity 512 MB,
   Postgres ~1 GB, website ~300 MB, Caddy ~50 MB → **≈ 10 GB**. With 8.5 GB already used, that
   does not fit without swapping, and a swapping JVM freezes the game. ✔ The 8.5 GB belong to the
   current server and website, which the new stack replaces: **the old stack must be stopped before
   the new one starts** (RAM and ports 80/443/25565), see challenge 9. With per-container limits the
   new stack takes about 13 GB, leaving about 3 GB for the OS and the disk cache: it works, without
   margin (no room to run a second test server or raise the faction heap). Adding RAM: challenge 6.
   Set `vm.swappiness=10`; heaps with `-Xms = -Xmx`. Limits per service: `docs/server-tuning.md` §1.3.
2. **CPU: many cores, slow single core.** A Minecraft server ticks a world mostly on one thread, so
   the 3.6 GHz Haswell core sets the limit, not the 64 threads. Fine for a few dozen players with
   Paper; donjon waves and big farms will be the first lag source. Mitigations: pre-generate the
   world (Chunky) before launch, `view-distance` 8 / `simulation-distance` 6, Paper entity limits,
   and **pin the faction server to one CPU socket** (`cpuset` in compose) so its memory stays on one
   NUMA node. The many cores are useful for everything else (Postgres, Node, backups, compression).
   ✔ user: Chunky on every world, view 8 / simulation 6, faction server pinned with priority on its
   memory. How: `docs/server-tuning.md` §1 (measured 2026-11-10: one NUMA node, all the RAM on one
   CPU, so the faction server is pinned to **that CPU's cores**; limits, `oom_score_adj`) and §4.5
   (pre-generation with a world border).
3. **Ports 80/443: Caddy replaces the `landing-website` stack** (✔ user described it, Open Question 37).
   Today `../landing-website` runs **nginx + a certbot container** (HTTP-01 webroot, `certbot renew`
   every 12 h, nginx reloaded every 6 h, first certificate by `init-letsencrypt.sh` with a dummy
   certificate) serving one static `index.html` on `play.hatlas.net`. Only one process can listen on
   80/443, and Caddy does all of that alone (certificate, renewal, reload, HTTP→HTTPS), so:
   - **Phase 1 (any time, before the website exists):** Caddy serves the same `html/` folder
     (`file_server`) on `play.hatlas.net`; nginx and certbot stop; the old `nginx/certbot` folder is
     no longer needed (Caddy gets its own certificate). Same page for visitors, fewer moving parts.
   - **Phase 2 (website ready):** Caddy `reverse_proxy`s `play.hatlas.net` to the SvelteKit website.
     ✔ user (Open Question 37): the new website gets a **fresh design** (new design system) and its own
     home page; `../landing-website` is then **archived on GitHub and deleted from the machine**.
     Phase 1 is optional: nginx + certbot can keep serving the old page until phase 2.
   - Note: the landing page says "Java **1.21.1**"; the network runs **1.21.11**.
4. **Docker bypasses ufw.** A port published by Docker (`ports: "5432:5432"`) is opened in iptables
   before ufw sees it, so ufw rules do not protect it. Rule: publish **only** 80/443 (Caddy) and
   25565 (Velocity); Postgres, RCON, the backends and the website listen on Docker networks only
   (or `127.0.0.1:` for admin tools). The router limits the Internet side, this protects the LAN side.
5. **Dynamic IP: keep the user's `../ovh-ddns`** (python:3.12-alpine + crond, every 5 min: public IP
   from ipify → OVH API `PUT /domain/zone/hatlas.net/record/<id>` for `play` → zone refresh). It works
   and stays a separate small compose project. Small improvements, planned in that repo:
   - **TTL 60 instead of 300**: after an IP change players reconnect after ~1–6 min instead of ~5–10;
   - compare the public IP with **the record's current target** (one GET), not only with the cache
     file in `/tmp`: a record changed by hand or a lost update is fixed on the next run;
   - a **second IP source** when ipify fails (e.g. `https://ifconfig.me/ip`), and check the answer is an IPv4;
   - pin `requests` and `ovh` versions; healthcheck = last success younger than 15 min; memory limit 64 MB;
   - if a second name is needed (Open Question 37 option b), a `SUBDOMAINS` list instead of one name.
   After an IP change players are disconnected and reconnect once DNS follows. Accepted.
6. **Backups and hardware** (Open Question 39; ✔ user: backups on **another disk** than the NVMe).
   - **`sda` (PNY 120 GB SATA SSD) holds `/srv/backups`.** No NVMe needed: backups are written once a
     day and rarely read.
   - 120 GB is enough **with a deduplicating, compressing tool**: **restic** (encrypted repository,
     replaces the `age` step; unchanged region files are stored once). Estimate: world pre-generated
     to a 5,000-block radius ≈ 3–8 GB, dumps tens of MB; 7 daily + 4 weekly snapshots ≈ 10–25 GB in
     restic. ⚠ The island asked in round 13 (radius 625 chunks = **10,000 blocks**) is 4 × that area:
     world ≈ 15–35 GB, restic ≈ 30–60 GB: still fits 120 GB, with less margin
     (`docs/map-building.md` §7). Plain copies (14 × the world) would not fit. Alert when `sda` passes 80 %.
   - It is a cheap entry-level SSD: fine for backups, but **`restic check` weekly** and an off-site copy.
   - ✔ `sda1` holds nothing: it is formatted (ext4, mounted on `/srv/backups`) at install.
   - **Off-site copy: later** (✔ user: after development; an **offline disk saved by hand, about once a
     year**). Challenge for then: once a year means up to a year of data lost if the machine is stolen
     or burns; a copy **after each big update, or monthly**, costs a few minutes with restic
     (`restic copy` to the offline disk). Kept as an open point.
   - **A second disk in the same machine only covers a disk failure**: not a mistake as root,
     ransomware, theft, fire or a power surge; the offline copy covers those.
   - RAID 1 is **not** a backup; not needed at this size.
   - **RAM: 16 → 32 GB** (✔ user: buy two more modules).

     **Shopping list: 2 modules, each:**

     | Spec | Value | Why |
     |---|---|---|
     | Type | **DDR4 desktop DIMM, 288 pins, unbuffered (UDIMM), non-ECC** | same kind as the installed modules; **not** ECC/registered (RDIMM/LRDIMM: cannot be mixed with UDIMM), **not** SO-DIMM (laptop) |
     | Size | **8 GB** per module | four equal modules → symmetric quad channel |
     | Speed | **DDR4-2133 (PC4-17000)**, CL15 | the Xeon E5 v3 runs memory at 2133 at most; faster modules (2400/2666) also work but run at 2133 |
     | Voltage | 1.2 V | DDR4 standard |
     | Rank | single rank (1Rx8) if listed | like the installed ones (Rank: 1) |
     | Best choice | **the same reference: G.Skill Aegis `F4-2133C15-8GNT`** (or the kit `F4-2133C15D-16GNT` = 2 × 8 GB) | identical timings, no compatibility doubt |

     About EUR 10–20 per module used, EUR 25–40 new. Total 32 GB.

     ✔ Listing checked 2026-11-10 (leboncoin, "G.Skill `F4-3000C15S-16GTZ`, 16 GB (2 × 8 GB), 3000 MHz
     CL15"): the **reference and the description disagree**. In G.Skill codes `S` = one module and `D` =
     a kit of two (the letter after `C15`): `F4-3000C15S-16GTZ` would be **one 16 GB module**; the
     2 × 8 GB Trident Z kit is `F4-3000C15D-16GTZ`. No `…S-16GTZ` sheet was found. Ask the seller for a **photo of each
     module's label**. If it is the 2 × 8 GB kit: compatible (desktop, unbuffered, non-ECC); the Xeon
     ignores XMP and runs it at its standard profile, **DDR4-2133 at 1.2 V** (the 3000 MHz is an
     overclock profile, unused here); timings differ from the Aegis modules but the board picks the
     slowest common one. Trident Z heat spreaders are **tall (~44 mm)**: check the CPU coolers leave
     room above slots A–D. If it is one 16 GB module (usually dual rank): it works too, but the
     channels are unequal (8/8/16 or 8/8/8/16); prefer the 2 × 8 GB.
     ✔ Seller's photo (2026-11-10): label **`F4-2133C15D-16GNT`, DDR4-2133 CL15** = the G.Skill Aegis
     2 × 8 GB kit, **exactly the recommended reference** (same speed, timings and voltage as the
     installed modules). Buy if the price is fair (EUR 20–40 used), then memtest86+ (step 7).

     **Moving the modules (about 30 min):**
     1. Find the board's real model: the generic BIOS says only "INTEL X99" (a Chinese dual-socket
        X99 board, e.g. Huananzhi, Jingsha, Machinist…). Look at the name printed on the board or its
        box, then get its **manual** (memory population table). The rules below are the general Intel
        ones; the manual wins if it differs.
     2. Shut down (`sudo poweroff`), unplug, press the power button to drain, touch the metal case
        before touching parts (static).
     3. Each CPU has its own slots, usually labelled near the socket: the first CPU (`CPU0`/`CPU1`, the
        one the board needs to boot) with channels **A, B, C, D**, the second with **E, F, G, H**
        (or A–D again with a CPU prefix); slot **1** of each channel (often the coloured one, or the one
        farthest from the CPU) is filled first.
     4. Put **the 4 modules in slot 1 of channels A, B, C and D of the first CPU** (one per channel =
        quad channel). Nothing on the second CPU: the faction server runs on the first CPU's cores, and
        all memory is then "near" it. Today one module is in `DIMM_C1` (first CPU) and one in
        `DIMM_G1` (second CPU). ✔ The board itself (user, 2026-11-10) has **8 slots printed
        `DIMM1`…`DIMM8`, 4 per CPU, one slot per channel**; the modules are in `DIMM1` and `DIMM5`,
        which match dmidecode's `C1` (first CPU) and `G1` (second CPU). So **`DIMM1`–`DIMM4` = first
        CPU, `DIMM5`–`DIMM8` = second CPU** (check on the board: the four slots beside the socket
        printed `CPU1`/`CPU0`, the one next to `DIMM1`).
        - ✔ User (round 14): dual channel now, then the kit for quad channel.
        - **Now:** move the module from `DIMM5` to **`DIMM2`** → `DIMM1` + `DIMM2` = dual channel on the
          first CPU (if the manual lists a 2-module order such as `DIMM1` + `DIMM3`, use that).
        - **With the kit:** **`DIMM1`, `DIMM2`, `DIMM3`, `DIMM4`** → quad channel; `DIMM5`–`DIMM8` empty.
        - Check after boot: dmidecode shows the modules on **different channel letters** and none on
          `E`–`H`; sysbench bandwidth roughly doubles (2 modules) or 3–4 × (4 modules). If the board does
          not boot with the second CPU's slots empty (rare), put one module back on `DIMM5`.
     5. Push each module straight down until both clips click.
     6. Boot, then check:
        - `sudo dmidecode -t memory | grep -E "Locator|Size|Speed"` → 4 × 8 GB, 2133 MT/s, four different
          channel letters;
        - `numactl --hardware` → about 31.9 GB;
        - the sysbench test of `docs/server-tuning.md` §1.1: socket 0 (CPU 0) now the fast one;
        - a bandwidth check before/after: `sysbench memory --memory-block-size=1M --threads=8 --time=10 run`
          (quad channel should show roughly 2–4 × the MiB/sec of today).
     7. **Run one full pass of memtest86+** (`sudo apt install memtest86+`, then pick it in the boot
        menu): non-ECC used modules must be tested once before holding the game and the database.
7. **Testing from home**: check the router's NAT loopback (open `https://play.hatlas.net` from the
   LAN); else a local DNS override.
8. Outgoing mail (OVH SMTP 465/587) + **SPF, DKIM, DMARC** records on `hatlas.net` before the first
   verification email.
9. **Cutover** (✔ user, Open Question 40): **no migration**: the current Minecraft server is not
   maintained and will be **deleted**; the new network starts on a fresh world. Order on install day:
   stop and delete the old Minecraft stack → stop `landing-website` (nginx/certbot) → start Caddy
   (phase 1 of challenge 3) and the new stacks → smoke test. `ovh-ddns` keeps running throughout.
10. **Capacity: 40 players** (user target). Everything that is not the faction server is subtracted
    first (estimates, measured again at the load test):

    | Item | RAM |
    |---|---|
    | Usable RAM (`numactl`) | 15.5 GB |
    | Debian, Docker, sshd, journald | − 0.8 |
    | **Website** (SvelteKit/Node) | − 0.5 |
    | Caddy + static landing, ovh-ddns | − 0.2 |
    | PostgreSQL (shared_buffers 512 MB + connections) | − 1.5 |
    | Velocity (heap 512 MB + overhead) | − 1.0 |
    | Hub (heap 768 MB + overhead) | − 1.2 |
    | Minimum disk cache (region files, Postgres) | − 1.5 |
    | **Left for the faction server** | **≈ 8.8 GB → heap 7 GB + ~1.5 GB off-heap (limit 8.5 GB)** |

    What 40 players need on the faction server: base (Paper, Hatlas, plugins, worlds) ≈ 1.5–2 GB;
    each player at view distance 8 keeps 17 × 17 = 289 chunks loaded, ≈ 25–60 MB per player when
    spread out, less when they sit in the same base; entities, items, donjon waves and GC headroom on
    top (G1 wants about 30 % free). **40 players ≈ 4.5–5.5 GB in use at peak → a 7 GB heap is enough**
    (~60 players before memory is the limit).

    **The CPU is the real limit, not the RAM.** A world ticks on one main thread; this Haswell core
    (3.6 GHz turbo, less when many cores are busy) is about 40 % slower than a recent desktop core.
    The tick budget is 50 ms (20 TPS). Rough guide for a survival/faction server with Paper at
    simulation distance 6: about 0.5–1 ms of main-thread time per active player on a modern core, so
    **40 players ≈ 25–55 ms here**: **40 is OK but close to the limit**, and it depends more on
    *what* players build (mob farms, redstone, hoppers, many entities, donjon waves, TNT raids) than
    on their number. Levers, in order: pre-generation (✔), simulation distance 6 → 5, entity and
    hopper limits (`docs/server-tuning.md` §4), `performance` governor, pinning (✔), then 4 → 3
    chunks of `simulation-distance` in the Nether/End. **Measure before launch: a load test** (§3 task
    6b) with 40 bots spread over the map and spark running. Set `max-players` 50 on the faction server
    and 60 on Velocity; above 50 needs a faster CPU, not more RAM.
11. **Electricity is 80 % of the running costs** (`docs/funding.md` §1: ~170 kWh a month ≈ 236 W
    around the clock). Measure the machine with a **wall power meter** (idle, and with players). The
    second CPU holds no RAM after the move and is not needed for 40 players (16 cores / 32 threads
    on the first CPU are plenty): options, after measuring, (a) leave it (simplest), (b) remove it if
    the board boots with one CPU (saves its idle power, maybe 15–30 W ≈ EUR 2–4 a month), (c) BIOS
    power settings (C-states on). The `performance` governor (§server-tuning 1.2) costs a little
    power; keep it only on if the load test shows a gain.

Admin tuning (compose priorities, JVM flags, Velocity, Paper configs, anti-bot, anti-cheat, anti-xray,
moderation plugins, launch checklist): [`docs/server-tuning.md`](server-tuning.md).

## 3. Tasks (build order step 7)

1. `deploy/game/` here: `compose.yml` (velocity, hub, faction; networks; healthchecks; restart
   policies; log rotation), config templates (velocity.toml, paper-global.yml forwarding, plugin
   configs with `access.renew-url` = `https://play.hatlas.net/renew` and the auth URLs, production roles `hatlas_proxy` /
   `hatlas_hub` / `hatlas`), `.env.example`, README.
2. `deploy/game/update.sh` here (decided earlier): announce the restart in game (countdown) →
   `hatlas-backup.sh backup` → pull/swap jars from `versions.env` → `docker compose up -d` → wait for
   health → print versions; `--rollback` to the previous `versions.env`.
3. Backups (`docs/identity.md` §7.6): `hatlas-backup.sh` also dumps schema `web`, encrypts with `age`
   (key kept off the machine), systemd timer installed; restore tested once on the machine.
4. Website: `hatlas-webapp/deploy/update.sh` (webapp step 5b) + Caddy with TLS on 443 + DB-IP `.mmdb`
   volume refresh.
5. First install runbook (`docs/deployment.md` §4, to write): machine prep, clone, `.env` files,
   `db-up` + roles, webapp migrations, game stack, router port forwards (443, 25565), DNS, certificate.
6b. **Load test before opening** (on the production machine, before the first player): 40 offline
   bots (VitaminMCP on a temporary copy of the faction server, removed afterwards; never left in
   production) spread over the map, walking and fighting mobs, one donjon run; target MSPT < 40 with
   `/spark tps` and `/spark profiler`; adjust §2.10 levers if not.
6. **Production smoke test** (with the user, real clients, not bots): register a new account in game →
   verification email → `/login` approval with the code → pay a chosen amount in Stripe **test mode** (sandbox "Hatlas") →
   compass → faction server → ticket expiry back to the hub → log out everywhere kicks → export and
   delete the test account. From outside the LAN (phone on mobile data) for the router/DNS/TLS part.
   Then switch Stripe to live mode.
7. Port check from outside: only 80, 443 and 25565 answer (`nmap` from a remote host); RCON, Postgres and
   backend ports closed.
