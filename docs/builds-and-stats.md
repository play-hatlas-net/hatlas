# Builds and combat stats: roots, crit, vampire, regen, health, crit guard, cooldowns, damage numbers (plan, 2026-11-21)

Round 26. User request (2026-11-21):
- Every skill gets a cooldown that grows with its impact (a stun waits longer than a shield). Look at League of Legends cooldowns.
- Stuns must never fail because the target was already stunned twice. This replaces the diminishing returns of [`runes.md`](runes.md) §6.2.
- Damage on bosses and mini-bosses shows as floating numbers.
- New stats:
  - damage dealers: **critical** and **vampire**;
  - tanks: **regen** (for example a Miner eating stone) and **HP** (more hearts);
  - tanks also get **armour against critical hits**;
  - healers get **anti-regen** against tanks.
- Exclusive builds:
  - damage dealer: crit **or** vampire;
  - tank: regen **or** big health;
  - "do the same for healers".
  - Armour can be taken on several nodes in every root.
- New tree rule:
  - 2 or more **roots**, and each root is a **primary specialisation**;
  - inside every root, **secondary specialisations** that do not depend on the root;
  - each root has **5+ dedicated nodes** with extra gameplay or combos with other roles. Example: a Miner tank on the big-health root has a **Forger** node that repairs a Hunter's crit sword.
- OQ 72 changed again: the final boss only spawns when all mini-bosses are dead.

Status: **round 27 (2026-11-21): OQ 127–136 answered**, the numbers below are updated (cooldowns halved, crit on jump crits, absorption in the Regen root, Forger in the secondary pool). New topics (effect display, shield timeout, node counts) and OQ 137–142 in §10–§11.

## 1. What the research says

| Source | Fact | What we take |
|---|---|---|
| LoL summoner spells | Big one-button effects carry the longest cooldowns: Flash 300 s, Cleanse 210 s, Heal and Exhaust 240 s, Barrier and Ignite 180 s | The strongest effects (a full cleanse, a team heal, a summon) wait minutes, not seconds |
| LoL [spell shields](https://wiki.leagueoflegends.com/en-us/Crowd_Control) | The Edge of Night shield blocks one whole ability, CC included, every 40 s | A "blocks one control" shield is high impact and gets a long cooldown |
| LoL [crowd control](https://wiki.leagueoflegends.com/en-us/Crowd_Control) | Hard CC (stun, root) removes control of the character; soft CC (slow) leaves movement. Tenacity shortens hard CC | Hard controls form the highest combat tier; tenacity becomes a tank option, not a hidden rule |
| LoL [critical strike](https://wiki.leagueoflegends.com/en-us/Critical_strike) | Crit is a chance per attack to deal bonus damage; it scales damage and nothing else | Crit = burst, no sustain |
| LoL [Randuin's Omen](https://lol.fandom.com/wiki/Randuin%27s_Omen) | Health + armour, and its passive cuts **crit damage taken by 30 %**. It is the only anti-crit item, and it does not reduce ability damage | Our **crit guard** cuts only the *bonus* part of a crit, never normal hits or rune damage |
| LoL bruisers and [grievous wounds](https://mobalytics.gg/blog/league-of-legends-bruiser-items-guide/) | Life steal suits fighters who trade blows; grievous wounds cut healing for a few seconds | Vampire = sustain through fights; **anti-regen** counters both vampire and regen tanks |

LoL basic abilities do **not** always give stuns longer cooldowns than shields (Leona's 1 s stun returns in about 5 s). LoL limits stuns with short durations and with tenacity, not with cooldowns alone. Our 1.8-style combat is faster, so the user's rule (impact → cooldown) is the better fit here, plus a guard against chains (§3.2).

## 2. The new tree rule: roots, primary and secondary specialisations

This changes the tree shape of [`job-skills.md`](job-skills.md) §3.1 (start → 3 branches → forks) and the rune forks of [`runes.md`](runes.md) §5 (proposal, OQ 134):

```
Start node
├── Root A  (primary specialisation, e.g. Regen)      ← picking it locks Root B
│   ├── 5+ dedicated nodes: the root's stat, its combos with other roles
│   ├── rune fork(s): rune 1 or rune 2 for the root's active skills
│   └── secondary pool: crit guard, utility (Forge, Siege…), the same nodes as in Root B
└── Root B  (primary specialisation, e.g. Big health)
    ├── 5+ dedicated nodes
    ├── rune fork(s)
    └── secondary pool (the same nodes)
Bridge nodes (max 2, runes.md §5): still at the end, need two rune paths
```

- **One root per tree**, chosen at the first point spent. That rules out "regen and big health" by construction, and the server needs no extra check.
- **The secondary pool is the same set in every root.** It holds:
  - crit guard (several nodes, see §4.3);
  - the former utility branches (Miner *Forge* and *Siege*, Lumberjack *Carpenter*, Hunter *Tracker*, and so on).

  So a utility build does not depend on the root.
- **Runes move inside the roots.** The root picks the **style** (regen or health), and the rune fork picks the **element** (Frost or Fire). Each job then has 2 roots × 2 runes = **4 builds**, plus the secondary pool.
- **5+ dedicated nodes per root.** At least 2 of them must be **combo nodes** with another role (rules sheet, step 2 of the method), for example:
  - Forger (tank → damage);
  - Rations (healer → tank).
- **Two tanks and two healers must not be copies** (round 20). They share the root *names* (Regen / Big health, Mender / Warder) but **not the nodes**:
  - The Miner's regen comes from eating stone; the Lumberjack's comes from sap, and he shares part of it with the ally he guards.
  - The Miner's big health makes him a wall; the Lumberjack's big health feeds his *Bodyguard* damage share.
- **Challenge, more roots later:** 2 roots per tree at launch. A 3rd root (for example a *Thorns* tank) only after the beta data, because every root doubles the balance work of step 4.

## 3. Cooldowns by impact

### 3.1 Tiers

Every active skill gets an **impact tier**. The tier sets the cooldown range in `job-skills.yml > cooldowns` (✔ OQ 128; **✔ round 27: all cooldowns halved**, user: "I want the game dynamic and fast"):

| Tier | What it does | Examples | PvP cooldown | PvE cooldown |
|---|---|---|---|---|
| 1. Light | small effect on self | small dash, self haste 3 s, mark | 2.5–4 s | 2–3 s |
| 2. Sustain | protects or heals one player | 2-heart shield, single heal, self cleanse | 6–10 s | 5–7.5 s |
| 3. Soft control / zone | slows, damage zones, anti-regen | slow zone 3 s, damage zone 3 s, anti-regen hit | 7.5–12.5 s | 6–9 s |
| 4. Hard control | removes control from a target | **stun**, root, silence, knock-up | **15–22.5 s** | 10–15 s |
| 5. Team / big | changes a whole fight | rune boost for allies, team cleanse, summon 2 minions, shield that blocks a control | **30–60 s** | 22.5–45 s |

- The validator of [`runes.md`](runes.md) §11 computes an **impact score**: tier × duration × targets × value. It refuses a skill whose cooldown is below its tier's range. Numbers can only be tuned inside the range.
- **No cooldown reduction stat at launch.** It is the stat that breaks every LoL patch. Maybe one capped node (−10 %) after the beta.
- Cooldowns run per skill. The Rune focus shows them on the item's cooldown bar (native `use_cooldown`, [`runes.md`](runes.md) §10).
- **Results with the user's catalogue:**
  - stun 2 s PvE / 1 s PvP → tier 4, 15–22.5 s PvP (halved, round 27);
  - shield absorbing 2 hearts → tier 2;
  - shield that **also blocks stun/burn/slow** → tier 5. Blocking a control beats a stun: it cancels a 15 s cooldown.

### 3.2 Stuns always work, but no chains (replaces diminishing returns)

The user does not want "my stun did nothing because the target was already stunned twice". The diminishing returns of [`runes.md`](runes.md) §6.2 are **removed**: a stun that lands always lasts its full time.

**Challenge:** without any rule, a group chains stuns. Three Lumberjacks with a 1 s stun each lock a player for 3 s, which is a sure kill in 1.8 combat, and the target cannot answer at all. Long cooldowns alone do not prevent this, because three players each have their own cooldown.

**Proposal (OQ 128): a stun guard of 1 s.**
- When a hard control **ends**, the target has 1 s during which a new hard control **cannot be cast on them**.
- The cast is **refused**: the cooldown is **not spent**, and the caster hears a "blocked" sound.
- So a stun is **never wasted**, which is what the user asked. It only waits 1 s.
- The guarded target shows a **white outline** (glow seen only by enemies), so players learn the timing.
- Slows and zones ignore the guard; the "no stacking" rule (runes §6.1) still applies.
- Counters stay explicit:
  - cleanse and the control-blocking shield (healers);
  - **tenacity**, an optional tank secondary node: −15 % control duration per node, at most −30 %, never below 0.5 s.

## 4. The new stats

### 4.1 Damage dealer (Hunter): Crit root or Vampire root

| | **Crit** (burst) | **Vampire** (sustain) |
|---|---|---|
| What | each melee or bow hit has a chance to deal ×multiplier | heals a part of the damage dealt (after every reduction) |
| Start | 5 % chance, ×1.5 | 3 % of damage |
| Cap | **40 % chance, ×1.8**, PvP and PvE | **10 % PvP, 18 % PvE** |
| Feedback | gold damage number with ✦, crit sound | small red heart particles, number in green on the attacker |
| Countered by | **crit guard** (tanks), shields, the stun guard does not matter | **anti-regen** (healers), burst (it needs time) |
| Combo nodes (examples) | *Keen edge*: crit swords from the Miner's Forger crit more but wear faster (§4.4) | *Blood pact*: the Farmer's feast also heals the vampire's next 3 hits |

- **Vanilla jump crits** (✔ user, round 27): our crit stays a **random roll with its own chance** on any hit, and the crit stat **also boosts the vanilla jump crit** (×1.5 → up to ×1.8 with crit-damage nodes). A hit that is both a jump crit and a random crit: formula in §10.3, OQ 139.
- Rune damage (skills) **never crits** and **never leeches**. Crit and vampire are weapon stats, like LoL attack damage; rune power stays the skill stat ([`runes.md`](runes.md) §7).

### 4.2 Tank: Regen root or Big health root

| | **Regen** (the one who lasts) | **Big health** (the one who absorbs) |
|---|---|---|
| What | heals over time; strongest when eating the job food | more max hearts (vanilla `max_health` attribute) |
| Miner | **eats stone**: cobblestone, deepslate and tuff become edible with the 1.21 `consumable` component (eat time 1.6 s), giving regeneration for 6 s. Only Miners with the node can eat it; others see plain stone | +2 hearts per node |
| Lumberjack | eats **sap** (from logs, a carpenter by-product); a part of his regen goes to the ally he guards | his hearts feed *Bodyguard* (takes allies' damage) |
| Cap | 0.5 heart / s **out of combat**, half while combat-tagged; eating has a 10 s cooldown | **+8 hearts PvE, +5 hearts PvP** (yml) |
| Countered by | **anti-regen** (healers), burst | **% max-health damage** (a Hunter node, *Giant slayer*: +1 % of the target's max health per hit, capped) |

- **Absorption hearts** (✔ user round 27: "absorption is regen"): they move into the **Regen root**; proposal in §10.4 (regen overflow fills absorption, OQ 140). Big health only raises max hearts. Healers (Warder, Farmer *Rations*) can still give absorption to anyone.
- **Challenge, eating stone in combat:** 1.6 s of eating already slows the player (vanilla eating slowdown), which is the right risk. A shorter eat time would make regen tanks unkillable in 1v1.

### 4.3 Crit guard (the user's "armour", a secondary for every tank root)

- It reduces **only the bonus part** of a critical hit. A ×1.8 crit with 50 % crit guard deals ×1.4. Normal hits and rune damage are untouched, as with Randuin's Omen.
- **−10 % per node, nodes in every root**, cap **−50 %**. Several nodes can be taken, as the user asked.
- **Name:** "armour" collides with vanilla armour points and with the armour of the Miner's *Bulwark*. I recommend **"Crit guard"** (in-game: *Hardened*) (OQ 132).
- Healers and the Hunter cannot take it: it is a tank tool, so a crit Hunter fears tanks, not everyone.

### 4.4 Healer: Mender root or Warder root ("do the same for healers")

| | **Mender** (heals after the hit) | **Warder** (prevents the hit) |
|---|---|---|
| What | direct heals and heals over time | shields, absorption hearts given to allies, damage reduction on an ally |
| Farmer | *Feast* (regen for everyone who eats), *Regrowth* aura | *Rations* (refill tanks' absorption), a hay-bale barrier |
| Alchemist | *Splash medic* (instant splash heal), *Lingering* clouds | *Burning shield* (the user's round 23 example: anti-slow shield, −15 % damage), shield that blocks one control |
| Countered by | anti-regen, burst | **shield breaker** (catalogue opposite), true damage over time |

- **Anti-regen** goes in the **healer secondary pool**, available in both roots:
  - −40 % healing received for 4 s (−60 % cap), applied by a hit or a potion;
  - it reduces regen, vampire healing **and** enemy heals;
  - its catalogue opposite is *Vitality* (+healing received), and it is countered by cleanse.
  - It has to be a secondary. If only Menders had it, Warder healers would have no answer to regen tanks.
- The healer **damage cap** still holds: anti-regen deals no damage.

### 4.5 The counter map (every build has an answer)

| Build | Strong against | Countered by |
|---|---|---|
| Crit Hunter | Big health tank (burst through hearts), Mender healers | Crit guard, Warder shields |
| Vampire Hunter | Long fights, Regen tank trades | Anti-regen, burst |
| Regen tank | Poke and zones, long sieges | Anti-regen, crit burst |
| Big health tank | Burst, stun-and-kill | % max-health damage (*Giant slayer*), long fights |
| Mender healer | Damage over time, zones | Anti-regen, burst |
| Warder healer | Burst, crit, controls (shield that blocks one) | Shield breaker, damage over time |

The validator ([`runes.md`](runes.md) §11) gets two new checks:
- every root has at least one counter in **another job's** tree;
- no faction of 5 (one per job) can stack two counters against the same root.

### 4.6 Damage order (one place, so the numbers stay readable)

`base weapon or skill` → `hit zone ×` (boss only, cities plan §4.6) → **crit** (weapon hits) → `rune wheel ±15 %` (rune damage) → `armour` or `rune resistance` → **crit guard** (on the crit bonus) → `damage cap` → **vampire** heal (from the final number) → **anti-regen** on any heal.

## 5. The Forger combo (user example) and durability

User example: a Miner **Forger** node repairs a Hunter's critical sword. **✔ Round 27: keen weapons and repair approved; Forger is in the secondary pool** (*Forge*), so both Miner roots can take it (OQ 135). Rules:
- **Keen weapons** (Hunter crit combo, forged by the Miner's *Masterwork*) lose **2 durability per crit**. Vanilla Mending is not allowed on them (they are combo items).
- The **Forger** repairs a keen weapon from any faction member in 3 s with iron; the weapon gains **Honed** (+5 % crit chance for 10 min, under the cap).
- ~~Challenge: Forger only in the big-health root~~ → solved: Forger is a secondary-pool node.

## 6. Floating damage numbers

- On every hit **dealt by a player** to a boss, mini-boss, minion or player, a **TextDisplay** entity is spawned at the hit point:
  - it is visible **only to the attacker** (`setVisibleByDefault(false)` + `player.showEntity`);
  - it floats up 0.6 blocks and fades over 0.8 s.
- **Colours:**
  - white: normal hit;
  - **gold ✦**: crit;
  - rune colour: rune damage;
  - grey: reduced by an armoured hit zone;
  - green on the attacker: vampire heal.
- Hits within 0.2 s on one target **merge** into one number. At most 8 live numbers per player.
- `/settings damage-numbers on|off|bosses` (default `bosses` on the faction server, `on` in dungeons).
- At the end of a boss fight, the chat shows each player's **total damage and share**. The data already exists for loot participation (C43).
- **Cost:** TextDisplays are client-side display entities with no AI. 8 per player × a 10-player event is fine. A packet-only version (no server entity) is possible later if profiling asks for it.

## 7. OQ 72, changed again: the final boss spawns only after every mini-boss is dead

User 2026-11-21: the boss only spawns when **all** mini-bosses are dead. It fits souls well: the factions fight over the souls first, then use them on the boss.

**Challenge: stalling.** A faction holding the zone could **refuse to kill the last mini-boss** (or kite it) so that the final boss never spawns and the zone never changes hands. Proposal (OQ 127):
- After `final_boss_gate_seconds` (default **15 min** after the event start), any mini-boss still alive **enrages**: +50 % damage, and it no longer regenerates. After **20 min**, the final boss spawns anyway.
- A mini-boss reset (all players gone) does not reset the timer.

## 8. Effect on earlier rounds

- [`runes.md`](runes.md) §6 rule 2 (diminishing returns) → replaced by §3.2 here. §5 rune forks → forks inside the roots. §10 Rune focus → cooldowns come from §3.1.
- [`job-skills.md`](job-skills.md) §3.1 shape → roots (§2). §3.2.1 forks → most samples become root nodes or secondary nodes:
  - *Iron wall* → Big health;
  - *Feast* → Mender;
  - *Rations* → Warder.
- Tree method §3.6 step 1 (effect catalogue) now includes crit, vampire, regen, max health, crit guard, tenacity, anti-regen and *Vitality*.
- Cities plan OQ 72 → §7 here.

## 9. Open questions of round 26 (✔ all answered 2026-11-21, round 27)

127 ✔ enrage 15 min, forced boss 20 min · 128 ✔ approved, **cooldowns halved** · 129 ✔ damage numbers in PvE **and PvP** · 130 ✔ random crit keeps its chance **and boosts the vanilla jump crit** · 131 ✔ absorption belongs to Regen · 132 ✔ · 133 ✔ · 134 ✔ shape, **min 60 nodes per tree, 30 per root** · 135 ✔ Forger in the secondary pool · 136 ✔ changing root resets the whole tree.

Original wording:

127. **Final boss gate:** final boss only after all mini-bosses die, mini-boss enrage at 15 min, final boss forced at 20 min (recommended)?
128. **Cooldown tiers** (§3.1), no cooldown-reduction stat at launch, and the **1 s stun guard** instead of diminishing returns, with refused casts not spending the cooldown; tenacity as a tank secondary (recommended)?
129. **Damage numbers:** attacker only, colours, merging, `/settings damage-numbers`, totals at the end of a boss fight (recommended)?
130. **Hunter roots:** Crit (cap 40 % ×1.8) or Vampire (cap 10 % PvP / 18 % PvE); no double-dip with vanilla jump crits; rune damage never crits or leeches (recommended)?
131. **Tank roots:** Regen (Miner eats stone, Lumberjack eats sap, half regen in combat) or Big health (+5 hearts PvP / +8 PvE); absorption stays a third thing given by others (recommended)?
132. **Crit guard:** reduces only the crit bonus, −10 % per node, cap −50 %, nodes in every tank root, named *Crit guard* rather than "armour" (recommended)?
133. **Healer roots:** Mender or Warder; anti-regen (−40 %, cap −60 %) in the secondary pool of both roots (recommended)?
134. **Tree shape:** one root per tree (2 at launch), 5+ dedicated nodes with 2+ combos, rune forks inside the roots, shared secondary pool, tanks and healers share root names but not nodes (recommended)?
135. **Forger:** keen weapons lose 2 durability per crit, the Forger repairs them and adds *Honed*; Forger stays in the big-health root **with an equal combo in the regen root** (recommended), or Forger moves to the secondary pool?
136. **Changing root:** a full reset of that tree (the Wizard's tree reset, §5 of job-skills), no partial switch (recommended)?

## 10. Round 27 (2026-11-21): answers and new design

✔ **User decisions:**
- OQ 127–136 answered (§9).
- **Cooldowns halved.**
- **Shields expire after a timeout.**
- Every effect must be **visible to other players**.
- Forger is in the secondary pool.
- Changing root resets the whole tree.
- Trees: **at least 60 nodes, 30 per root**.
- The tree-building method becomes a skill, `skill-tree-building` (§10.6).

### 10.1 Halved cooldowns: what changes (challenge)

Halving every cooldown doubles the **uptime** of every effect, so three things need a rule:
1. **Uptime cap.** A defensive effect (shield, damage reduction, haste) can last **at most 50 % of its cooldown**. A 2-heart shield on an 8 s cooldown lasts ≤ 4 s. Without this, a 6 s shield that lasts 6 s is always on. The validator checks `duration ≤ 0.5 × cooldown` for every self or ally buff.
2. **Healing per window.** Twice as many heals per minute makes two healers unkillable. The rules sheet adds a PvP cap **per 10 s window**: healing received from players ≤ 4 hearts per 10 s (yml), regen and vampire included.
3. **Stun chains.** Three stunners with 15 s cooldowns and the 1 s guard give a target stun 1 s → free 1 s → stun 1 s → free 1 s → stun 1 s, then 10 s free. A 1v3 losing is fine. The guard still prevents a 3 s lock.

### 10.2 Shields expire

Every shield is in `job-skills.yml > effects.<id>`:
- `absorb` (hearts);
- `duration` (it disappears at the end even if not broken);
- `blocks` (the controls it blocks, if any).

Defaults (PvP):

| Shield | Absorbs | Lasts | Tier |
|---|---|---|---|
| Plain shield (self or ally) | 2 hearts | 4 s | 2 |
| *Burning shield* (Alchemist, anti-slow, −15 % damage) | 1.5 hearts | 3 s | 3 |
| Control-blocking shield | 1 heart + blocks the **first** stun/root | 3 s | 5 |

- Shields never stack. A new shield replaces a weaker one, and the strongest one stays.
- Shield breaker (catalogue opposite) removes it at once.
- Absorption hearts given by healers also time out (Warder `duration`). Only the Regen root's own absorption decays slowly (§10.4).

### 10.3 Crit on vanilla jump crits (user answer to OQ 130)

User: "crit will add a boost to the vanilla crit when jumping, our crit is random and keeps its percentage chance". Proposal (OQ 139):
- **Random crit:** chance from nodes (5 % → cap 40 %), multiplier `M` from crit-damage nodes (×1.5 → cap ×1.8). It works on any hit, jumping or not.
- **Jump crit:** vanilla ×1.5 becomes ×M too: the crit-damage nodes boost it.
- **Both on one hit** (jump crit + random crit roll): ×(M + 0.5), **capped at ×2.3**.
  - Multiplying would give ×1.8 × 1.8 = ×3.24, a one-shot in 1.8 combat, which is too much.
  - Crit guard reduces the whole part above ×1.0.
- Damage numbers show a **double ✦✦** for that hit, so players learn the timing.

### 10.4 Absorption in the Regen root (user answer to OQ 131)

User: "absorption hearts is regen I think". I agree, with one nuance: absorption is a **buffer**, not healing. Proposal (OQ 140):
- In the Regen root, **regen that would overflow full health fills absorption** (yellow hearts), up to a cap: **3 hearts PvP, 5 PvE**.
- While not hit, the absorption decays 0.5 heart every 5 s, so it is not a permanent extra bar.
- Anti-regen also stops the refill. Shield breaker removes it.
- **Big health** does not get absorption from its own nodes. Absorption given by healers works on everyone.
- Miner *Bulwark* (absorption max) nodes move from Big health to Regen. Big health keeps the armour and the *Iron wall*-style nodes.

### 10.5 Showing effects on players (vanilla client + our resource pack, no mods)

User: "a sign of effect so other players understand what effect a player has, e.g. a glowing circle around a shielded player; I don't know if it is possible without mods". It is possible with the server and the `hatlas` resource pack the players already download. Four tools exist, and I recommend combining them:

| Tool | How it works in vanilla | Good for | Limits |
|---|---|---|---|
| **A. Icon row above the head** | A `TextDisplay` riding the player (passenger, follows smoothly), text = small icons from a **custom font** in the pack (`assets/hatlas/font/effects.json`: one glyph per effect) | Every effect at once: shield, stun, slow, burn, anti-regen, rune boost, soul… up to 4 icons, most important first, coloured by rune | Hidden behind walls (`see_through: false`); sits above the name tag |
| **B. Particle shapes** | Server particles around the player, seen by everyone within 24 blocks | Big, readable states: **shield = rotating ring of dust in the rune's colour at waist height**; stun = stars circling the head; slow = snowflakes at the feet; anti-regen = dark smoke; burn = **visual fire without damage** (Paper `setVisualFire`) | Budget: ≤ 4 particles per tick per effect, none beyond 24 blocks |
| **C. Shield bubble** | An `ItemDisplay` riding the player with a translucent sphere **item model** from the pack (scaled ×2.2) | The shield only: the most important thing to read in a fight; it fades out in the last second before the timeout | One entity per shield; the model is drawn by the `gui-art` step |
| **D. Glow outline** | The vanilla glowing outline, coloured per viewer through team packets (packetevents) | Reserved: **white = stun guard** (§3.2), **red = Hunter's mark** | Only one colour per player at a time, so it cannot show many effects |

- **Your own effects:**
  - Effects that match a vanilla potion (slowness, resistance) use the real potion effect with its particles hidden, so you get the **vanilla icon** in the top-right corner for free.
  - Custom effects show in the **action bar** as glyph + seconds.
- **Allies and enemies see the same icons.** A small coloured frame (green ally / red enemy) is added on the glyphs, so a healer knows whom to cleanse.
- `/settings effect-icons on|off` hides A for the viewer; B and C always stay on, because they are gameplay information.
- **Recommendation (OQ 138):** A + B for every effect, C for shields, D only for the guard and marks.

### 10.6 Node counts and the tree skill

User: "at least a minimum of total nodes per tree? Let's start with 60? 30 into each root?" Proposal (OQ 141):

| Part of a root | Nodes (min) | Notes |
|---|---|---|
| Primary dedicated nodes | **12** | the root's stat (crit, regen…), ≥ 2 combo nodes with other roles, 1 capstone |
| Rune forks | **6** (3 forks × 2 sides) | the player takes one side per fork, so 3 of the 6 |
| Shared nodes counted in the root | **12** | the secondary pool, the **same 12** in both roots: crit guard, tenacity, anti-regen, utility (*Forge* with Forger, *Siege*…) |
| **Root total** | **30** | |

- The tree then has 2 × 18 own nodes + 12 shared = **48 different nodes**, i.e. 60 node slots. 5 jobs × 48 = **240 nodes** to write and check.
- If you want **60 different nodes** per tree, the pool comes on top of the 30. That makes 72 per tree and 360 in total: more content, but twice the balance work.
- **Points:** 50 points at level 50. One root (with one side of each fork) costs about **75–85 points**, so a max-level player owns **≈ 60 %** of what their root offers.
  - That replaces the old "≈ 40 % of the whole tree". Picking a root already removes half the tree, so 40 % of the rest would feel thin.
  - Choices still matter: which secondary nodes, which rune side, which capstone.
- **Bridge nodes** (max 2): the round 23 rule ("nodes of two runes") no longer works inside one root, because a player takes only one side of each rune fork.
  - Proposal: a bridge needs **one rune side + 3 secondary nodes**, and it unlocks a weaker skill of another rune (OQ 141).

**The skill** `.claude/skills/skill-tree-building/SKILL.md` (new, round 27) turns the tree method of [`job-skills.md`](job-skills.md) §3.6 into steps an agent follows. It holds every rule of rounds 19–27:
- roots, node counts, costs, caps;
- cooldown tiers, uptime cap, shield timeout, effect display;
- counters, the Forger in the pool.

The validator script `scripts/job-skills/validate.py` enforces these rules. One job is approved at a time (user gate).

## 11. Open questions of round 27

✔ **Round 28 (2026-11-21, user):** 137 yes (uptime cap 50 %, PvP healing 4 hearts / 10 s, PvE cooldowns halved too) · 138 yes (icons + particles + shield bubble + glow for guard and marks) · 139 yes (×(M + 0.5), cap ×2.3, ✦✦) · 140 yes (regen overflow → absorption 3 / 5 hearts, decay) · 141 **pool inside the 30** (12 primary + 6 rune fork sides + 12 shared = 48 different nodes per tree, ≈ 60 % of a root at level 50). The bridge rule (one rune side + 3 pool nodes) was not answered: ✔ confirmed by the user. 142 ✔ **main session** runs the skill (no separate agent).

Original wording:

137. **Halved cooldowns, side rules:** defensive effects last at most 50 % of their cooldown; PvP healing received capped at 4 hearts per 10 s; PvE cooldowns halved too (recommended)?
138. **Effect display:** icon row above the head (custom font) + particle shapes for every effect, a translucent bubble for shields, glow only for the stun guard (white) and marks (red), own effects as vanilla icons or in the action bar (recommended)?
139. **Jump crit + random crit on the same hit:** ×(M + 0.5), capped ×2.3, shown as ✦✦ (recommended), or plain multiplication (up to ×3.24)?
140. **Absorption in the Regen root:** regen overflow fills absorption (cap 3 hearts PvP / 5 PvE), decays 0.5 heart / 5 s while not hit; healer-given absorption times out (recommended)?
141. **Node counts:** 30 per root = 12 primary + 6 rune fork sides + 12 shared secondary nodes (48 different nodes per tree) (recommended), or 30 own + 12 shared on top (60 different)? ≈ 60 % of a root reachable at level 50; bridge nodes need one rune side + 3 secondary nodes (recommended)?
142. **Skill `skill-tree-building`:** run by the main session with the validator and a user gate per job, no separate agent (recommended), or a `tree-designer` agent like the boss pipeline?
