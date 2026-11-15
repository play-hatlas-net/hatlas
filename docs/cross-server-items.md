# Items across servers: no duplication, and the travel bag (plan, 2026-11-16)

> **Status: plan only, nothing built.** Source: user, round 21 (question on duplication glitches between the
> faction server and the dungeon / mining servers, and the idea of a travel bag as a faction skill).
> Applies to [`cities-and-dungeons.md`](cities-and-dungeons.md) §7.8 (dungeons) and
> [`mining-world.md`](mining-world.md) (mining). Open questions mirrored in `CLAUDE.md` (OQ 98–99).

---

## 1. What really causes a duplication

A duplication happens when **two places both believe they own the same item at the same time**, and both
let the player use it. Between servers it happens in these cases:

| Cause | Example |
|---|---|
| **Copy instead of move** | the faction server keeps the inventory and the mining server gets a copy: the player now has it twice |
| **Two writers** | the mining server writes the inventory back, the faction server also saves its own (old) copy later and overwrites or adds |
| **The vanilla player file on the target server** | Paper saves `world/playerdata/<uuid>.dat` on the mining server too. If the plugin fails to load the handoff row, the player gets the old vanilla file: items from a previous visit come back |
| **Crash in the middle** | the inventory was written to the row, the target crashed after the player picked items up, and both an old and a new copy get restored |
| **Double join / quick reconnect** | the player joins the faction server while the mining server still thinks they are inside |
| **Containers and drops** | items thrown on the ground or put in a chest on the target server just before leaving, picked up after the inventory was written |
| **Vanilla or plugin bugs** | the same bugs as on any single server (shulker tricks, piston bugs…) |

**Copy in one direction only** (faction → mining, nothing comes back) removes every case above, but then
nothing mined or looted can come back, which kills the point of the mining world and of dungeons. So
items must come back, and the protocol below is what makes it safe.

## 2. The protocol (one owner at a time)

One row per player in `server_handoffs` (`hatlas-common`, already planned):
`uuid, state, owner_server, version, items (ItemBytes), return_position, pending_ledger, updated_at`.

```
AT_HOME ──(faction server: write items, clear player, commit)──► TO_TARGET
TO_TARGET ──(target: load items on join, commit)───────────────► AT_TARGET
AT_TARGET ──(target: write items, clear player, commit)────────► TO_HOME
TO_HOME ──(faction server: restore items on join, commit)──────► AT_HOME
```

Rules (each is needed; together they make a duplication impossible by design):
1. **Every change is a compare-and-set** on `(state, version)` in one transaction. A server that reads an
   old version cannot write. Only the server named in `owner_server` may change the items.
2. **The source clears the player and commits before the proxy transfer.** If the commit fails, the
   transfer does not happen and nothing moved.
3. **The target never trusts its vanilla player file.** On join: clear the inventory, armour, off-hand and
   ender chest **first**, then load the row. On quit: write the row, then clear. Paper's `playerdata` on the
   dungeon and mining servers is never a source of truth (it can even be deleted at each start).
4. **Ender chest, containers, drop key and item frames are off** on the target servers, so an item can only
   be in the player's inventory (or the travel bag, §3).
5. **Crash:** the target saves the row every minute and at key moments (zone cleared, bag change). After a
   crash the faction server restores **the last saved copy**: the player can lose up to a minute of items,
   **never gain**.
6. **Join gate:** the proxy refuses a join to the faction server while the row is `AT_TARGET` or
   `TO_TARGET` (the player is sent back to the target, or waits until the target writes the row).
7. **Item fingerprints (detection):** valuable custom items (keys, combo weapons, Magic rerollers, skins)
   get a unique id in their data. A daily job reads all saved inventories, vaults and handoff rows and
   **reports any id seen twice**. It catches duplicates from vanilla bugs too, not only server hops.

Rubies follow the same rows: mined rubies are kept in `pending_ledger` and written to `ruby_ledger` by the
faction server in the same transaction that restores the items ([`mining-world.md`](mining-world.md) M2).

**Conclusion:** safety comes from **the protocol**, not from which items travel. A bag (below) does not
make transfers safer on its own; it changes **how much** travels and **what the player can bring back**.
That is a game design choice, and a good one.

## 3. The travel bag (user's idea, challenged)

### 3.1 Options

| Option | What travels | For | Against |
|---|---|---|---|
| **A. Whole inventory moves** (plan of rounds 18–20) | everything the player carries, both ways | simple for the player | the whole inventory is "in transit" at each hop; no limit on what comes back (economy faucet wide open); no progression |
| **B. One direction only** | a copy goes in, nothing comes back | no duplication possible | loot and ores cannot come back: unusable |
| **C. Empty inventory + bag only** | nothing but the bag | very little in transit | the player arrives with no pickaxe, sword or food: needs a kit system |
| **D. Expedition loadout = hotbar + armour + off-hand + travel bag** (recommended) | what the player holds ready to use, plus the bag | most valuable items stay home; what comes back is limited by the bag size (faucet control); a faction skill to level | locked slots in the menu (more code), the player must prepare before entering |

### 3.2 Option D in detail (recommended)

- **Before entering**, the main inventory (the 27 slots above the hotbar) **stays on the faction server**
  in a stash row (owner = faction server, it never moves). Only the **hotbar (9), armour (4), off-hand (1)**
  and the **travel bag** travel.
- On the target server the 27 main slots are **locked**: the unlocked ones are the **bag slots**, the rest
  show a grey "locked" pane (clicks refused). The player sees the bag as part of the normal inventory, no
  extra menu needed.
- **The bag works both ways:** what is put in the bag slots before leaving (extra potions, torches, food)
  goes in; what is mined or looted can fill empty hotbar slots and bag slots and comes back.
- **On return:** the stash comes back to its slots, then the bag content fills the free main slots.
  **What does not fit** stays in the player's **travel bag storage**, opened at any entrance NPC or with
  `/bag` in a safe zone (take only). **The player cannot enter again while the bag storage holds items**
  (otherwise it becomes free storage).
- **Rubies** mined go in the bag like any item (stack 64 gems). The bag size therefore also caps the rubies a
  player can bring back per trip: a natural brake on ruby supply ([`economy-observatory.md`](economy-observatory.md)).
- **Inventory full during a dungeon loot roll** (user, round 21): the item **drops at the player's feet,
  locked to that player** (Paper `Item#setOwner`: nobody else can pick it up, important with PvP on in
  city events), with a warning. Items left on the ground when the player leaves are lost.

### 3.3 Bag size: a faction skill

| Tier | Bag slots | Cost (proposal, like the vault skill) |
|---|---|---|
| base (every player, factionless too) | **4** | — |
| Travel bag I | 8 | faction skill, one-shot |
| Travel bag II | 12 | " |
| Travel bag III | 18 | " |
| Travel bag IV | 27 (whole main inventory) | " |

All in `factions.yml > skills.travel_bag` (sizes and costs), same model as the vault skill. A **factionless
player keeps 4 slots**: consistent with "a faction is a plus, not required".

Optional combo for the job trees ([`job-skills.md`](job-skills.md)): a Miner node *Deep pockets* (+2 bag
slots in the mining world only) — to decide when the Miner tree is generated.

### 3.4 Challenges

- **Junk fills the bag** (cobblestone, deepslate, dirt). Proposal: a per-player **junk filter** in the bag
  menu (tick blocks that are never picked up in the mining world). Without it, players spend the trip
  throwing items, and the drop key is disabled.
- **Dungeons need potions.** Nine hotbar slots + 4 bag slots is tight for a dungeon. The bag answers it
  (pack potions into the bag before entering), and that makes the faction skill matter in dungeons too.
  Same rule on both servers keeps one protocol and one menu.
- **The stash is a second inventory to protect.** It never moves (owner = faction server only), it is
  written in the same transaction as the handoff row, and the player cannot join the faction server
  without getting it back, so it cannot be lost or duplicated.
- **Death on the target server:** keep inventory (dungeons ✔; mining: OQ 94), so the bag content is never
  dropped.
- **Disconnect, reset kick, crash:** the hotbar + armour + bag content is written back exactly like the
  full inventory of option A; nothing else changes in the protocol.

## 4. Open questions (mirrored in `CLAUDE.md`)

- **98** Option D (hotbar + armour + off-hand + travel bag travel; the main inventory stays home), the same
  for dungeons and the mining world (recommended)? Cannot enter again while the bag storage holds items
  (recommended)? Junk filter (recommended)?
- **99** Bag sizes 4 / 8 / 12 / 18 / 27 as a faction skill, factionless players keep 4 (recommended)?
  Daily duplicate scan of unique item ids (recommended)?
