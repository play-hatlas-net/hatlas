# Job skill trees (plan, 2026-11-11)

> **Status: plan only, nothing built.** Sources: user, round 18 (2026-11-11, answer to Open Question 47) and
> round 19 (2026-11-12, answers 47a–e and 59), round 20 (2026-11-13: roles, combos, generation method). Linked plan: [`cities-and-dungeons.md`](cities-and-dungeons.md)
> (shop Workshop actions, dungeons, Wizard NPC).

---

## 1. What the user asked (✔ rounds 18–19)

- Each player has a **personal job XP and level** for the job they chose (a progression like the faction's).
- ✔ Round 19: **the job belongs to the player, with or without a faction.** A player can take a job
  **without a faction**, and **leaving a faction no longer resets** the job XP or the tree (replaces round 18).
- Job XP is won **only by completing quests of that job** (✔ 47a), with the configurable exp multiplier and
  the other parameters of the faction XP formula.
- **Being in a faction is a plus:** the XP a player wins by finishing a quest is **also won by their faction**
  (faction XP, as today).
- Each new job level gives **skill points**, spent to unlock skills **permanently** (until a reset).
- Skills depend on the job and improve combat, speed, jump, tank, healing, defence, throwing…, or change what
  the player can craft and do; some **link with other jobs' skills** (§3.3).
- **Goal:** a faction builds a **team composition** across its members' jobs (tank, heal, damage), and
  other factions build a **counter**. A complex tree is wanted: it makes players think about their build,
  alone and as a team.
- Display: a skinned chest menu (✔ 59), art by the `gui-art` generator.

---

## 2. Progression

| | Today | Planned |
|---|---|---|
| Job needs a faction | yes; leaving the faction removes the job | **no** (✔ round 19) |
| Job XP source | +1 per job action (break, kill, harvest, brew, craft) | **quest completion only** (✔ 47a) |
| Formula | level-up at `(level+1) × 64` | `job_exp = job_exp.base_reward × Σ(difficulty × multiplier_exp) × √(jobLevel+1)`, the same shape as faction XP, own keys in `jobs.yml > job_exp` |
| Curve | linear | like factions: `first_level_exp`, then `× growth` per level (e.g. 1.09), **`max_level: 50`** (✔ 47d) |
| Points | none | **1 per level** (✔ 47d) → 50 points at max level |
| Reset | job switch (24 h cooldown) | the Wizard (§5). **Job switch resets job XP and tree** (✔ round 20); the **first switch is free**, every next one **costs rubies** (✔ round 20, `job_switch.cost`, burned, ledger `JOB_SWITCH`). **Leaving the faction: nothing is reset** (✔) |

Completing a quest gives job XP to the player and, **if they are in a faction**, faction XP to the faction.

**Challenges**
- **Code that assumes a faction** (✔ round 20): a player without a faction has **jobs and daily quests**,
  pays shops **with the rubies in their own inventory** (ledger `SHOP_BUY` from the player), and **cannot use
  Jokeyrini** (Jokeyrini is for factions only). Dungeons stay per faction.
- **Shops for faction members** (✔ round 21, OQ 73): **every player pays from their own inventory**,
  whatever their faction role. The **faction vault is a chest only**: the owner and BANKERs may **deposit
  and take out**, members may **only deposit** (as today). The vault **no longer pays shops directly**: a
  BANKER who wants to buy with faction money takes rubies out first (one `VAULT_WITHDRAW` row, then a
  `SHOP_BUY` row from that player: the ledger still shows who spent what). Auction house: OQ 89.
- **Job switch** (✔ round 21): price **default in yml** (`job_switch.cost`, set by admins, burned, ledger
  `JOB_SWITCH`), **24 h cooldown** kept. The first job pick is **not** a switch, the first switch is free
  (✔ round 20). A switch also drops the *Magic reroller* recipe if the player was an Alchemist with that
  node.
- **Faction hopping is free now.** A level-50 player keeps their build when they leave, so strong players
  can move to the winning faction. Accepted by design (round 19); the dungeon cooldown and daily cap on the
  player (C28 of the cities plan) stop the farming side of it.
- **Job level also scales quest amounts** (`BASE[d] + jobLevel × PER_LEVEL[d]`): higher level = longer
  quests = more XP per quest. Keep it, or the curve must account for it.

---

## 3. The trees

### 3.1 Shape (✔ round 19)

> **Round 26 (user):** the start node now opens **2+ exclusive roots** (primary specialisations: Hunter Crit / Vampire, tanks Regen / Big health, healers Mender / Warder), each with **5+ dedicated nodes**, rune forks inside, and a **shared secondary pool** (crit guard, the former utility branches). Proposal in [`builds-and-stats.md`](builds-and-stats.md) §2 (OQ 134); the shape below is the round 19–21 version.

- A **start node**, then **2 or more branches** start from it.
- **Each branch splits into at least 2** sub-branches, again and again: at every fork the player **chooses
  one path**.
- **A choice cannot be undone**, except through the Wizard (§5).
- Nodes cost **1 point or more**: big skills (strong effects, links with other jobs) cost more (e.g. 2–5).
- About **40 % of one tree** is reachable at max level (✔ 47d): e.g. ~120 points of nodes per tree, 50 points
  at level 50.

```
                         ┌─ Bulwark (absorption bar) ─┬─ Iron wall ……
            ┌─ Tank ─────┤                            └─ Shield bash ……
            │            └─ Forge master (repairs) ───┬─ Masterwork gear ……
 [start] ───┤                                         └─ Field smith ……
            └─ Siege ─── … (2 forks)
```
(Miner example, updated round 20: Bulwark and Forge are the forks of the tank branch; each `┬` is a fork
where only one side can be taken. Full branches: §3.2.)

### 3.2 Roles per job (✔ round 20: roles fixed by the user)

✔ User, round 20: **Miner + Lumberjack = tanks**, **Alchemist + Farmer = healers**, **Hunter = damage**. Every
node of a tree must serve its job's role (the round 19 table, where the Lumberjack was a damage job, is
replaced). Five jobs, three roles: **two tanks and two healers must not be copies of each other**, so each
pair gets two different flavours:

| Job | Role | Flavour (proposal) | Branches from the start node (proposal, OQ 75) |
|---|---|---|---|
| **Miner** | Tank | **Bulwark**: raw defence, absorption hearts, armour, stands still and holds a line; **forges** the heavy gear and the combo weapons other jobs use | *Bulwark* (absorption, armour, knockback resistance) · *Forge* (crafts: combo weapons, reinforced armour, repairs) · *Siege* (obsidian, Raider's Pickaxe, breaching in raids: tank of the attack) |
| **Lumberjack** | Tank | **Guardian / disruptor**: shields, protecting allies (takes part of their damage), taunting mobs, slowing enemies, barricades | *Shieldwall* (shield block, damage taken for allies near) · *Warden* (mob taunt in PvE, roots/slows in PvP) · *Carpenter* (barricades, scaffolds, wooden traps, bows/arrow shafts for the Hunter) |
| **Hunter** | Damage | **the only damage job**: ranged and melee burst, marks, **boss damage in dungeons/events** | *Marksman* (bow/crossbow/trident, piercing, headshots) · *Slayer* (melee burst, boss/mini-boss damage, last-hit tools) · *Tracker* (marks, glow, locator, speed) |
| **Farmer** | Healer | **Sustain**: heals over time through food, saturation, regen, absorption refill for tanks, team buffs out of combat | *Kitchen* (healing foods, feasts for the team) · *Herbalist* (regen auras, cleanse of hunger/poison) · *Ranch* (animals: mounts, wolves that guard, honey) |
| **Alchemist** | Healer | **Burst support**: splash heals, cleanse, buffs in combat, debuffs on enemies; **the Wizard** (✔ round 20) | *Healer* (splash heals, lingering clouds, cleanse) · *Brewer* (buffs, longer potions, combo potions) · *Arcane = the Wizard* (enchant work, damage-over-time debuffs, far end: *Magic reroller*) |

Proposal: the **main branch is the role**, the two other branches are utility for the same role (no
Hunter-level damage on a healer). A healer can still **enable** damage through combos (buffs, marks),
never by out-damaging the Hunter.

**The tank's extra heart bar:** the **vanilla absorption hearts** (yellow) with the `max_absorption`
attribute. *Bulwark* raises the max, crafted items (Farmer foods, Miner rations) refill it.

#### 3.2.1 The roles explained (round 21, user asked)

**Why flavours?** With five jobs and three roles, two jobs share "tank" and two share "healer". If both
tanks only had "more armour", a faction would never need both. So each job of a pair does its role **in a
different way**, and a full faction wants **both**:

| Pair | Job A | Job B | In one sentence |
|---|---|---|---|
| Tanks | **Miner = the wall** | **Lumberjack = the bodyguard** | the Miner **takes** the hits himself; the Lumberjack **moves** hits away from his friends and **controls** enemies |
| Healers | **Farmer = sustain** | **Alchemist = burst** | the Farmer keeps everyone topped up **slowly, before and between fights**; the Alchemist saves people **instantly, during the fight** |
| Damage | **Hunter** | — | the only job that really kills; the others make his kills possible |

**What "branches" and "forks" mean.** From the start node, a tree has **3 branches**. The **first branch is
the role** (the core of the job), the two others are **utility for the same role**. Each branch then
**forks** (the player picks one side, for good, unless the Wizard removes nodes). The examples below are
**samples to show the idea**, not the final trees (those come from the method of §3.6):

**Miner — tank "the wall"** (front line, stands still and holds; also the smith of the faction)
- *Bulwark* (role): more absorption hearts, armour, knockback resistance. Fork: **Iron wall** (stronger
  when standing still: +armour after 2 s without moving) **or Juggernaut** (a short charge that knocks
  enemies back, for a moving tank).
- *Forge* (utility): crafts what other jobs need. Fork: **Masterwork** (combo weapons such as the
  *Boss-forged blade* for the Hunter, reinforced armour for tanks) **or Field smith** (repair kits usable in
  dungeons and the mining world, no anvil needed).
- *Siege* (utility, the tank of a raid): Fork: **Breacher** (more Raider's Pickaxe uses, obsidian breaks
  faster in enemy claims) **or Sapper** (crafts creeper eggs/TNT bundles, takes less explosion damage).

**Lumberjack — tank "the bodyguard"** (protects others, disrupts enemies)
- *Shieldwall* (role): Fork: **Bodyguard** (takes 20–30 % of the damage of allies within 6 blocks on
  himself) **or Bastion** (much stronger shield block, reflects arrows).
- *Warden* (utility, control): Fork: **Taunt** (PvE: mobs and bosses attack him for a few seconds; the key
  to safe boss fights) **or Snare** (PvP: axe hits slow, then root a marked enemy 1 s; combo with the
  Hunter's *Mark*).
- *Carpenter* (utility, crafts): Fork: **Barricades** (temporary wooden walls placeable in dungeons and
  events, they break after 20 s) **or Fletcher** (special arrows and bows for the Hunter: craft combo).

**Hunter — damage** (ranged and melee burst, boss killer)
- *Slayer* (role): Fork: **Bossbreaker** (the reference combo: + damage to bosses and mini-bosses, only in
  dungeons and city events, only with the Miner's sword) **or Duelist** (PvP burst: combo damage after 3
  hits in a row, capped).
- *Marksman* (utility, range): Fork: **Sniper** (more bow damage at long range, headshots) **or Volley**
  (crossbow multishot and piercing).
- *Tracker* (utility, information): Fork: **Mark** (a hit marks the target: glow, faction deals +x % to it;
  feeds the Lumberjack's *Snare* and the Alchemist's *Exposed*) **or Pathfinder** (speed, a compass to the
  nearest mini-boss or structure, useful in the mining world).

**Farmer — healer "sustain"** (slow, steady healing; prepares the team)
- *Kitchen* (role): Fork: **Feast** (a placeable feast: every ally who eats gets regeneration and
  saturation) **or Rations** (portable foods that **refill tank absorption hearts**: combo with the Miner's
  *Bulwark*).
- *Herbalist* (utility): Fork: **Regrowth** (a regeneration aura around the Farmer, 8 blocks) **or Purifier**
  (removes poison, hunger, wither; short immunity).
- *Ranch* (utility, animals): Fork: **Beastmaster** (wolves that follow and draw mobs) **or Stablemaster**
  (better mounts; honey that heals).

**Alchemist — healer "burst"** (instant saves, buffs and debuffs during the fight; the Wizard)
- *Healer* (role): Fork: **Splash medic** (strong instant splash heals) **or Lingering** (healing clouds that
  hold an area, good on a boss platform).
- *Brewer* (utility): Fork: **Buffer** (longer, stronger buffs for allies, combo potions like *Tank tonic*)
  **or Toxicologist** (debuffs on enemies: weakness, slowness, *Exposed* = takes more damage from the
  Hunter).
- *Arcane = the Wizard* (utility): Fork: **Enchanter** (enchanting work; its far end is the **Magic
  reroller**, §5) **or Hexer** (curses that deal damage over time, capped so it never matches the Hunter).

**Rules that keep roles honest** (rules sheet, §3.6 step 2): healers and tanks never reach the Hunter's
damage; healing in PvP is capped and reduced while combat-tagged (otherwise two healers make a fight
endless); every number is in `job-skills.yml` and can change after the beta.

### 3.3 Skills that link jobs (✔ round 19)

Some nodes are only worth it **with another player's node**, so a faction plans its builds together.
Proposed rule: a link works with **faction members** (or the dungeon run's members) **within 24 blocks**;
another reason to have a faction. Examples:
- Farmer *Hearty meals* + Miner *Bulwark*: Farmer foods refill 2 more absorption hearts for that Miner.
- Hunter *Mark* + Lumberjack *Warden's grip*: marked enemies are rooted 1 s by the Lumberjack (round 20: the
  Lumberjack is a tank, so it controls instead of dealing damage).
- Alchemist *Catalyst* + Farmer *Team buffs*: splash heals are stronger on allies under a Farmer buff.
- Alchemist *Magic reroller* (the Wizard, ✔ round 20): unlocks a craft whose item serves **every** player (§5).

Each node lists its links in its lore ("works with: Miner — Bulwark"), so players can find the combos.

### 3.4 The reference combo (✔ user, round 20)

The user's example, kept as **the model every generated combo must match in depth**:

> A **Hunter** node (*Bossbreaker*, cost **2**) adds extra damage **to bosses and mini-bosses only, only in
> dungeons and city zone events**, and **only with a dedicated sword**. That sword can only be **crafted by a
> Miner** who took the matching node in his *Forge* branch (*Boss-forged blade*, cost 2).

What it teaches, as rules for every tree:
1. **Context-scoped effects**: a node can say where it works: `open_world`, `dungeon`, `city_event`,
   `mining_world`, `pvp`, `pve`, and on which targets (`boss`, `mini_boss`, `mob`, `player`).
2. **Combos across players**: one player's choice is only worth it with another player's choice, so the
   faction decides **who takes what**.
3. **Cost follows power and dependency**: a node that needs another job's node costs **2+**; a node another
   job depends on also costs **2+** (the Miner gives up something to serve the Hunter).
4. **The last-hit rule** (cities plan C33) makes these combos decide city control.

### 3.5 Kinds of combo

| Kind | How it works | Example | Scope |
|---|---|---|---|
| **Craft combo** | job A's node unlocks a recipe; job B's node needs that item in hand/armour | Miner *Boss-forged blade* → Hunter *Bossbreaker* | works across factions (items can be traded) |
| **Presence combo** | A's node is stronger when a player with B's node is **within 24 blocks**, same faction or same run | Farmer *Hearty meals* + Miner *Bulwark*: food refills 2 more absorption hearts | same faction / same run |
| **Setup → payoff** | A puts a state on a target (mark, slow, wet, burning), B's node consumes it for a bonus | Hunter *Mark* → Lumberjack *Warden's grip* roots marked enemies 1 s | same faction / same run |
| **Item → buff** | A crafts a consumable that only gives its full effect to B's node | Alchemist *Tank tonic* → Miner/Lumberjack get +4 absorption, others +1 | anyone holding the item |
| **Team chain (3 jobs)** | rare, expensive capstones that need 3 roles | Lumberjack taunts the boss, Alchemist *Exposed* debuff on taunted targets, Hunter last-hit bonus on exposed targets | same run |

Target per tree: **6–8 combo nodes**, every **pair of jobs linked at least twice** (10 pairs → ≥ 20 links),
and **2–3 team chains** in total.

### 3.6 How the trees will be generated (challenge, ✔ user asked)

Writing ~5 trees × ~40 nodes = **~200 nodes** in one go would give nice names and effects that **cannot be
built** or that **break PvP**. So the trees are produced in this order, each step checked before the next:

1. **Effect catalogue** (`docs/job-skills-effects.md`): the small list of effect **primitives** the code
   will support, each with its Paper implementation and its risk: stat modifiers (`AttributeModifier`),
   conditional damage (`EntityDamageByEntityEvent` + context + target filters), heals and heal over time,
   absorption refill, auras (periodic scan of allies within N blocks), marks/states on targets (PDC + glow),
   mob taunt (`Mob#setTarget`), damage share (part of an ally's damage moved to the tank), crowd control
   (slowness, root via speed 0, knockback), crafts (`PrepareItemCraftEvent`), consumables, cooldown-based
   actives (sneak + right-click with a job item). **Every node is a combination of these primitives**; no
   effect outside the catalogue without adding a primitive first.
2. **Rules sheet**: point budget (≈ 120–130 points per tree, 50 earned → ~40 %), costs (1 = small stat,
   2 = combo or conditional power, 3–5 = capstone), caps per stat in PvP vs PvE (`job-skills.yml > caps`),
   OldCombatMechanics limits (no attack-speed effects, crits and burst capped by the boss damage cap),
   healing in PvP capped and reduced while combat-tagged (otherwise two healers make a fight endless).
3. **Combo matrix**: a 5 × 5 table of every job pair with the planned links (§3.5), before any tree, so no
   pair is forgotten and no job is only a giver.
4. **One tree per job** as data: `job-skills.yml` draft + a readable table (id, name, cost, requires, fork
   group, role, context, primitives, links). Fork rule (start → ≥ 2 branches, each splitting into ≥ 2).
5. **Validator script** (`scripts/job-skills/validate.py`): checks the shape (one start node, forks ≥ 2,
   no cycle), the budget (max reachable ≈ 40 %), that every link points to an existing node of another job
   and is listed on both sides, that every primitive exists, and that no PvP value exceeds its cap. It also
   prints the **strongest 50-point build per job** for a manual balance read.
6. **Your review, one job at a time** (gate), then the combo matrix is re-checked, then the gui-art
   generator draws the tree from the same file.

> ✔ Round 23: method approved, Miner + Hunter first. **Runes** ([`runes.md`](runes.md)) are part of steps 1–3:
> the effect catalogue = [`runes.md`](runes.md) §4, the rules sheet adds §6 (no stacking, diminishing
> returns, PvP values), the combo matrix adds the rune wheel and the counter check of §11.

#### 3.6.1 The six steps in detail (round 21, user asked)

The idea in one line: **first decide what the code can do, then the rules, then who combines with whom,
and only then write nodes; a script checks every tree, and you approve one job at a time.**

| Step | What is produced | File | Checked by | Why it comes before the next |
|---|---|---|---|---|
| 1. Effect catalogue | the list of **building blocks** (primitives) the plugin will support: what each does, how it is coded in Paper, its PvP risk | `docs/job-skills-effects.md` | you read it, Claude checks each primitive against the Paper API | a node that uses an effect we cannot code is wasted work |
| 2. Rules sheet | point budget, cost scale, caps per stat (PvP vs PvE), healing limits | `docs/job-skills-rules.md` + `job-skills.yml > caps` | you approve the numbers | without caps, trees are written "too strong" and must be redone |
| 3. Combo matrix | a 5 × 5 table: for each pair of jobs, which links exist (craft, presence, setup→payoff, item→buff) | `docs/job-skills-combos.md` | you approve | makes sure no job is left alone or only gives |
| 4. Trees as data | one tree per job: nodes with id, name, cost, requires, fork group, context, primitives, links | `job-skills.yml` + a readable table per job | the validator (step 5) | this is the real game content |
| 5. Validator | a script that refuses broken trees | `scripts/job-skills/validate.py` | runs on every change | catches mistakes a human misses in 40 nodes |
| 6. Review per job | you play-read one job, ask changes, approve; then the next job | — | you | balance and fun need a human |

**Worked example, the reference combo through the steps:**
1. **Catalogue** gets the primitives `conditional_damage` (Paper `EntityDamageByEntityEvent`; filters:
   context `dungeon|city_event`, target `boss|mini_boss`, item in hand `hatlas:boss_forged_blade`) and
   `craft_unlock` (`PrepareItemCraftEvent`: the recipe works only if the crafter has a node).
2. **Rules** say: a conditional damage bonus costs 2 points, is capped at +25 % against bosses, and is
   **0 in PvP** by definition.
3. **Combo matrix**, cell Miner × Hunter: "craft combo — Boss-forged blade → Bossbreaker".
4. **Trees**: Hunter node `hunter.slayer.bossbreaker` (cost 2, requires `hunter.slayer`, fork group
   `slayer`, primitive `conditional_damage +20 %`, link `miner.forge.boss_forged_blade`); Miner node
   `miner.forge.boss_forged_blade` (cost 2, primitive `craft_unlock`, link back to the Hunter node).
5. **Validator** checks: both nodes exist, the link is written on both sides, +20 % ≤ the 25 % cap, the
   Hunter can still reach ~40 % of his tree with 50 points, no cycle in "requires".
6. **You** read the Hunter tree and say "OK" or "Bossbreaker should be +15 %"; the yml changes, the
   validator runs again.

**Order** (recommended, OQ 90): steps 1–3 for all jobs at once (they are short), then steps 4–6 for **Miner
and Hunter** first (they hold the reference combo), then Lumberjack, Farmer, Alchemist. ✔ User (round 21):
combo items are usable by **any player who has the required node, whatever their faction**.

Challenges to accept:
- **Balance cannot be proven on paper.** The validator catches broken shapes and caps; real balance needs the
  beta (✔ beta after each epic). All numbers stay in yml.
- **Two healers in Minecraft PvP with 1.8 combat** can make players unkillable. Hence PvP heal caps and a
  heal reduction while combat-tagged (rules sheet).
- **Tank "protect an ally" has no vanilla equivalent**: damage share and taunt are custom code (primitives),
  tested early.
- **Factionless players** only get craft combos and item → buff combos (presence and setup combos need a
  faction or a run). That is consistent with "a faction is a plus".

---

## 4. How skills are applied

- **Stats** through Paper `AttributeModifier`s keyed `hatlas:job/<node>`, reapplied on join and on each
  server (the dungeon server reads the player's nodes from the database): `max_health`, `armor`,
  `armor_toughness`, `knockback_resistance`, `movement_speed`, `jump_strength`, `safe_fall_distance`,
  `attack_damage`, `max_absorption`, `step_height`, `block_break_speed`…
- **Effects** (heals, marks, auras, projectile damage, special foods, links) through listeners.
- **New crafts** (e.g. the Magic reroller): recipes registered for everyone, the craft refused unless the
  crafter has the node (`PrepareItemCraftEvent`).
- **Attack speed does not work here**: the server uses OldCombatMechanics (1.8 PvP, no cooldown), which
  sets attack speed itself. Replaced by crit chance, combo damage or shield break.
- **Caps**: each stat has a maximum in `job-skills.yml` (e.g. +4 hearts, +20 % speed), whatever the build,
  so a veteran is stronger but not untouchable in PvP. Dungeon-only values can differ from PvP values.

---

## 5. The Wizard and the Magic reroller (✔ round 19)

- ✔ Round 20: **the Wizard is the Alchemist.** There is no 6th job: the Alchemist's *Arcane* branch (§3.2)
  ends with the node *Magic reroller*. The **Wizard NPC** in the city stays.
- **Magic reroller**: an item that only an **Alchemist** with the node *Magic reroller* (very far in the
  tree) can craft. It can be **given or traded to anyone** (trade window, auction house).
- **Wizard NPC** (in the city): a player brings **1 Magic reroller + rubies** (`wizard.remove_node_cost`) and
  asks to **remove one node** of their tree; the points come back.
- **Full tree reset**: **3 Magic rerollers + 3 × the ruby cost** of one node removal, then a **7-day
  cooldown** before the next full reset (✔ 47d).
- Rubies paid to the Wizard are **burned** (ledger kinds `JOB_NODE_REMOVE`, `JOB_RESPEC`).

**Which node can be removed?** ✔ Round 20 (OQ 66): only an **end node** (an unlocked node with no unlocked node after
it); to change a fork choice, remove back to the fork one node at a time (one reroller each), or do a full
reset. That keeps the reroller valuable and the trade of rerollers alive.

---

## 6. Data and storage

- Table `job_skills (uuid, node_id, unlocked_at)` + `player_jobs` gets `job_exp`, `job_level`,
  `skill_points`, `last_full_reset_at`. Domain JOBS. **Keyed on the player only** (no faction column).
  Website view `web_player_job_skills` (later, if builds are public).
- Trees in `job-skills.yml`: `trees.<JOB>.nodes.<id>` (name, icon item model, cost, requires, fork group,
  links, position x/y in the menu, effects, recipes).
- **Seeing other builds** ✔ 47e: the faction info shows each member's job and main branch; an enemy
  faction's info shows only role counts ("2 tanks, 1 healer").

---

## 7. Display (✔ 59)

**Skinned chest menu** to view and spend points (same GUI framework as the crystal skills): the background
is drawn as a tree by the **`gui-art` generator** from `job-skills.yml` (node positions, connector lines,
locked forks greyed), scrolled by arrow buttons. Clicking a node = unlock, with a confirm screen. The vanilla
advancement screen cannot send clicks to the server, so it is only a possible **read-only tab later**
(UltimateAdvancementAPI), not in v1.

---

## 8. Open questions

- 47a ✔ quests only. 47b ✔ obsolete (nothing resets on leaving). 47c ✔ base table + fork structure.
  47d ✔ max 50, 1 point per level, nodes cost 1+, ~40 %, rerollers and 7-day cooldown. 47e ✔.
- 64 ✔ round 20: factionless players pay from their own inventory, no Jokeyrini; switch resets XP and tree,
  first switch free, then rubies. 65 ✔ the Wizard is the Alchemist (*Arcane* branch). 66 ✔ end node only.
- 73 ✔ (round 21): every player pays shops from their own inventory; the vault is a chest (owner/BANKER
  deposit and take out, members deposit only); job switch price default in yml, 24 h cooldown. 74 →
  details given in §3.6.1, approval re-asked (OQ 90); ✔ combo items usable by anyone with the node, any
  faction. 75 → explained in §3.2.1, re-asked (OQ 91).
- 89 ✔ (round 23): auction buyers pay from their own inventory, the money still goes to the seller's faction
  vault. 90 ✔ the 6-step method, steps 1–3 for all jobs, then **Miner + Hunter first**. 91 ✔ roles and
  sample branches OK.
- Round 23 adds **Runes** (two rune specialities per job, rune forks, bridge nodes, effect catalogue with
  counters, Summoner for the Alchemist): [`runes.md`](runes.md), questions 105–113. The effect catalogue of
  step 1 starts from [`runes.md`](runes.md) §4.
