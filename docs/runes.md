# Runes: elements, effects and counters for the job skill trees (plan, 2026-11-19)

> **Status: plan only, nothing built.** Source: user, round 23 (2026-11-19): add element types called
> **Runes** (fire, water, air, nature…, adapted to Minecraft) that specialise skills; each job tree has one
> or more **specialities** (groups of skills) based on runes; the player picks a branch of one speciality or
> the other; some nodes **join** to unlock skills of another rune; every effect has a **counter effect**;
> effects on self, ally, enemy or a location; effects classified by **type**, **target** and **timing**;
> **every buff has an opposite debuff**; no composition may be unbeatable. Research asked: League of Legends
> (AP/AD, dragon souls, champion effects) and Magic: The Gathering (colours, card effects). Special effect
> **Summoner** for the Alchemist only. Mini-bosses give **rune souls** (round 23 change of OQ 72).
> Linked plans: [`job-skills.md`](job-skills.md) (trees, method §3.6), [`cities-and-dungeons.md`](cities-and-dungeons.md)
> (events, souls, boss pipeline §4). Open questions in §12, mirrored in `CLAUDE.md` (OQ 105–117).

---

## 1. What the research gives us

### 1.1 League of Legends

| LoL idea | What it is | What we take |
|---|---|---|
| **AD / AP** | two damage types: physical (attacks, reduced by armour) and magic (abilities, reduced by magic resist) | **weapon damage** (vanilla, reduced by armour) vs **rune damage** (our effects, reduced by a new **rune resistance** stat). A tank chooses what to resist: an anti-Hunter tank (armour) or an anti-caster tank (rune resistance) |
| **Dragon souls** ([wiki: Dragon Slayer]) | killing elemental drakes gives the team a lasting elemental buff; the 4th of one element gives a "soul" with a strong effect: Infernal = explosions on hit, Ocean = heal after dealing damage, Mountain = shield out of combat, Cloud = movement speed, Hextech = chain lightning that slows, Chemtech = damage and reduction at low HP | **rune souls** from mini-bosses (§9), one per element, each with its own perk |
| **Crowd control types** ([wiki: Types of CC]) | slow, root, stun, silence, knock-up, taunt, suppression… | our control family (§4) |
| **Tenacity / Cleanse / Unstoppable / spell shield** ([LoL CC guide], [tenacity]) | tenacity shortens controls; Cleanse removes most controls; "unstoppable" blocks **new** controls but does not remove the current ones; a spell shield blocks **one** ability and breaks | our counters: **tenacity**, **cleanse**, **unstoppable**, **ward** (§4) |
| **Grievous wounds** | reduces healing received | our **anti-heal** debuff, the counter of healers |
| **Readable fights** | abilities show where they land before they hit | our **telegraph rule**: zones show on the ground before they act (§6) |

### 1.2 Magic: The Gathering

| MTG idea | What it is | What we take |
|---|---|---|
| **The colour pie** ([colour pie explained], [colour wheel]) | five colours, each with clear **strengths** and **blind spots** ("a mono-red deck can't deal with enchantments") | each rune has a list of what it does well **and what it can never do** (§2.2): that is what makes counters real |
| **Two-colour decks** | most decks use two colours to cover each other's blind spots | each job has **two runes** (§3); a faction combines runes across players |
| **Hexproof / ward / protection** ([MTG keywords]) | hexproof: cannot be targeted; ward: can be targeted at a cost; protection from a colour | our **ward** (blocks the next enemy effect) and **rune resistance** against one element |
| **Counterspell, removal, board wipe** | answers to what the other player does; a board wipe hits everything without targeting | **silence**, **dispel**, **banish** (vs summons), **area damage** (vs summons and groups) |
| **Anthems and auras** | "creatures of colour X get +1/+1" | **rune boost**: allies' skills of one rune are stronger for a few seconds |
| **Tokens** | small creatures created by spells | **Summoner** minions (§8) |

## 2. The runes

### 2.1 Four runes adapted to Minecraft (proposal)

| Rune | Minecraft feel (vanilla hooks) | Strong at | Never does (blind spots) |
|---|---|---|---|
| **Fire** 🔥 | fire ticks, explosions, lava, blaze | damage over time (burn), area bursts, **breaking shields**, damage reflection when hit (user's "fire defense") | no control (no slow, no stun), no direct heal |
| **Frost** ❄ (water and ice) | freezing (vanilla `freeze ticks`: slow + frost overlay), powder snow, ice | **slows, roots, stuns**, damage reduction (ice armour), putting out burns | little burst damage, little mobility |
| **Storm** 🌪 (air and lightning) | wind charge, knockback, levitation, lightning, speed | **mobility** (dash, speed, jump), **displacement** (knockback, pull), **scattering zones**, **banishing summons** | no healing, no damage reduction |
| **Nature** 🌿 (earth and life) | regeneration, poison, vines, thorns, absorption, moss, mushrooms | **sustain** (heal over time, cleanse), roots by vines, poison, **summons** | no burst, no mobility |

A 5th rune (**Arcane / Ender**: teleport, silence, the Wizard) is possible later; four keep the first
trees small (OQ 105).

### 2.2 The rune wheel (soft counters)

```
        Fire ──melts──► Frost
         ▲                │
     smothers           freezes
         │                ▼
       Nature ◄─uproots── Storm
```
**Fire > Frost > Storm > Nature > Fire.** Fire melts ice (the user's example: an Alchemist *fire* shield
removes the Miner's *frost* slow); Frost freezes the wind (grounds dashes, stops knockback); Storm uproots
plants and scatters spore clouds; Nature (earth) smothers fire.

**Soft, not hard:** a rune's effects are **+15 %** stronger (damage, duration) against a target whose
active effects come from the rune it beats, and **−15 %** against the one that beats it (yml). Like LoL,
counters give an edge, never an automatic win; the main counters are **effect counters** (§4), not elements.

## 3. Runes per job = the specialities

Each job has **two runes** (two specialities), chosen so that every rune exists in at least two jobs and two
roles (proposal, OQ 106):

| Job (role) | Rune A | Rune B | Why |
|---|---|---|---|
| **Miner** (tank: the wall) | **Frost** — slows and freezes attackers, ice armour | **Fire** — forge fire, burning retaliation when hit ("fire defense") | the wall either slows the line or punishes hitting it |
| **Lumberjack** (tank: the bodyguard) | **Nature** — vines that root, thorns, wooden barricades | **Storm** — pushes enemies away from allies, wind wall against arrows | protects by holding or by pushing |
| **Hunter** (damage) | **Fire** — burning and explosive arrows, burst | **Storm** — lightning, speed, dashes, piercing shots | burst or mobility |
| **Farmer** (healer: slow healing) | **Nature** — regeneration, feasts, cleanse poison | **Frost** — water: put out burns, cooling shields, slows to protect | sustain or protective control |
| **Alchemist** (healer: instant saves) | **Fire** — burning shields (the user's example), cauterising heals | **Nature** — healing clouds, poisons, **Summoner** | burst saves or attrition and minions |

Count: Fire 3 jobs (tank, damage, healer), Nature 3 (tank, 2 healers), Frost 2 (tank, healer), Storm 2
(tank, damage). Each rune has both an offensive and a protective use.

## 4. Effects: classification, opposites and counters

### 4.1 How an effect is described

| Axis | Values |
|---|---|
| **Type** | damage · control · defence · sustain · buff · debuff · summon · utility |
| **Target** | **self** · **ally** (one player) · **enemy** (one player or mob) · **zone** (a location, a radius) · **aura** (around the caster, moves with them) |
| **Timing** | **instant** · **over time** (a tick every second for a duration) · **state** (lasts a duration) · **delayed** (telegraphed, then acts) |
| **Trigger** | **cast** (active skill) · **on hit** (when the player hits) · **when hit** (reactive) · **passive** |
| **Rune** | Fire · Frost · Storm · Nature (sets the colour of particles, the wheel bonus, the soul that boosts it) |

### 4.2 Every buff has an opposite debuff

| Buff | ⇄ | Debuff |
|---|---|---|
| **Haste** (speed) | ⇄ | **Slow** |
| **Unstoppable** (immune to new controls, LoL) | ⇄ | **Stun / Root** |
| **Fortify** (damage taken −x %) | ⇄ | **Expose** (damage taken +x %) |
| **Shield** (absorbs damage) | ⇄ | **Sunder** (extra damage to shields, shields break faster) |
| **Regeneration / heal** | ⇄ | **Anti-heal** (healing received −40 %, LoL grievous wounds) |
| **Rune boost** (allies' skills of one rune stronger, MTG anthem) | ⇄ | **Rune suppress** (enemies' skills of one rune weaker) |
| **Cleanse** (removes debuffs) | ⇄ | **Dispel** (removes buffs) |
| **Anchor** (knockback immunity) | ⇄ | **Knockback / Pull** |
| **Veil** (hidden from marks, no glow) | ⇄ | **Mark / Reveal** (glow, locator) |
| **Ward** (blocks the next enemy effect, LoL spell shield / MTG ward) | ⇄ | **Silence** (cannot cast rune skills) |
| **Summon** (minions) | ⇄ | **Banish** (removes summons) |

### 4.3 The effect catalogue (with the user's examples)

| Effect | Type | Target | Timing | Default (PvE / PvP) | Countered by | Runes |
|---|---|---|---|---|---|---|
| **Slow zone** (user) | control | zone | state | slowness in radius 4, **3 s** | haste, unstoppable, cleanse, Fire (wheel) | Frost, Nature (mud/vines) |
| **Damage zone** (user) | damage | zone | delayed + over time | 1 heart/s, **3 s**, radius 3, telegraph 0.5 s | leaving the zone (haste, dash), shield, Storm *scatter* | Fire, Nature (poison), Storm (lightning) |
| **Shield** (user) | defence | self, ally | state | absorbs **2 hearts** (a 5-heart hit → 3 pass), **blocks controls** (stun, burn, slow) while it holds, 6 s | sunder, Fire (wheel), many small hits | Frost (ice), Fire (burning shield), Nature (bark) |
| **Rune boost** (user) | buff | ally (aura) | state | skills of one rune +20 %, **5 s** | rune suppress, dispel | each rune boosts itself |
| **Stun** (user) | control | enemy | state | cannot move or attack, **2 s PvE / 1 s PvP** (§6) | unstoppable, ward, tenacity, cleanse, diminishing returns | Frost (freeze), Storm (lightning) |
| Burn | damage | enemy | over time | 0.5 heart/s, 4 s | cleanse, Frost *put out*, fire resistance | Fire |
| Root | control | enemy | state | cannot move, can attack, 1.5 s | unstoppable, cleanse, Fire *burn the vines* | Nature, Frost |
| Knockback / pull | control | enemy, zone | instant | 4 blocks | anchor, Frost (wheel) | Storm |
| Silence | debuff | enemy | state | no rune skills, 1.5 s | ward, cleanse | Storm (thunder) |
| Expose | debuff | enemy | state | +15 % damage taken, 4 s | fortify, cleanse | Fire, Storm (marks) |
| Anti-heal | debuff | enemy, zone | state | healing −40 %, 5 s | cleanse | Fire, Nature (rot) |
| Fortify | defence | self, ally | state | −15 % damage taken, 5 s (user's fire-shield example) | expose, sunder, dispel | Frost, Nature, Fire |
| Haste / dash | buff | self, ally | instant / state | +30 % speed 3 s, or a 5-block dash | slow, root, Frost | Storm, Fire |
| Heal / regen | sustain | self, ally, zone | instant / over time | 3 hearts, or 1 heart/s 4 s | anti-heal | Nature, Frost (water), Fire (cauterise: heals + burns a little) |
| Cleanse | sustain | self, ally | instant | removes debuffs and controls | dispel, re-applying | Nature, Frost |
| Dispel | debuff | enemy | instant | removes buffs and shields | ward, re-casting | Storm, Fire |
| Reflect ("fire defense", user) | defence | self | when hit | burns melee attackers | ranged attacks, Frost | Fire |
| Taunt | control | enemy (mobs; players: forced to face, PvP off by default) | state | 3 s | unstoppable, ward | Nature, Frost, Storm (tanks) |
| Mark / reveal | debuff | enemy | state | glow, +damage from the Hunter | veil, cleanse | Storm, Fire |
| **Summon** | summon | zone | state | §8 | area damage, banish, taunt | Alchemist only (Fire or Nature look) |

The catalogue becomes **step 1 of the tree method** ([`job-skills.md`](job-skills.md) §3.6.1): every
node is built only from these effects.

## 5. Specialities in the trees

The tree shape stays as approved (start → 3 branches → forks). Runes are added like this (proposal, OQ 107):
- **The forks become rune choices.** In each branch, one side of a fork is rune A, the other rune B. The
  sample forks of [`job-skills.md`](job-skills.md) §3.2.1 already fit: Miner *Bulwark* → **Iron wall
  (Frost: attackers are slowed)** or **Juggernaut (Fire: a burning charge)**.
- A player can mix runes **across branches** (Frost in *Bulwark*, Fire in *Forge*), but going deep in **one
  rune** gives that rune's bonuses (rune power +x % per node of that rune).
- **Bridge nodes** (user: "nodes that join"): near the end of the tree, a bridge node **requires nodes in
  two different branches** and unlocks a skill of **another rune** (one the job does not have) or a
  **dual-rune** skill. Example: Miner *Frost* + *Fire* nodes → bridge *Steam vent* (a **Storm**-type
  knockback zone made of steam). Limit: **2 bridge nodes per tree**, cost 3+, weaker than the rune's own
  jobs (a borrowed rune never beats its specialist).

## 6. Combat rules (so no composition is unbeatable)

1. **No stacking of the same effect:** two slows on one target → only the **strongest** applies, durations
   refresh but do not add. Four Frost players cannot freeze someone forever.
2. **Diminishing returns on controls** (stun, root, silence, strong slow): on the same target within 10 s,
   the 2nd control lasts **half**, the 3rd does nothing (immune until the 10 s pass). Shown on the target's
   action bar. Without it, a faction with 3 stuns locks a player until death.
3. **PvP values are lower than PvE values** (yml `effects.<id>.pvp`). Example: **stun 1 s in PvP** (1.8 combat
   is fast: 2 s of stun is almost a kill), 2 s on mobs and bosses.
4. **Telegraphs:** zones show on the ground (particles in the rune's colour) **0.5 s before they act**, so a
   player can step out. Same rule as the boss pipeline (§4.2 of the cities plan).
5. **One active zone per skill per player**; allies are never hit by their own side's zones.
6. **Caps** per stat and per effect in `job-skills.yml > caps` (already planned), plus a **rune power cap**.
7. **No casting in safe zones**; spawn protection (city events) blocks effects both ways.

## 7. Rune power and rune resistance (AP/AD)

- **Weapon damage** = vanilla attacks (sword, axe, bow), reduced by armour, as today.
- **Rune damage** = our effects (burn, zones, lightning), scaled by the caster's **rune power** (from nodes,
  souls, boosts) and reduced by the target's **rune resistance** (new stat, from tank nodes and later from
  gear). Rune damage ignores armour.
- So **tanks choose**: armour against the Hunter's weapons, or rune resistance against casters. A faction
  heavy on rune damage is countered by rune-resistant tanks, and the other way round.

## 8. Summoner (Alchemist only, user)

- An Alchemist node calls **golem-like minions** (vanilla iron golems scaled down with the `scale`
  attribute, rune look: magma for Fire, moss for Nature). They **follow the Alchemist** and **attack the
  last target the Alchemist hit**.
- Limits (yml): **max 2 minions**, **15 s** life, low HP and low damage (counted in the healer damage cap:
  a healer never out-damages the Hunter), cooldown 30 s, not in safe zones, removed when the Alchemist
  leaves the zone/server.
- Use: body-block arrows, distract, protect the Alchemist. Counters: **area damage** (minions are weak),
  **banish** (Storm), **taunt** (the tank pulls them).
- Note: the existing faction golems (`GolemType`) are a different feature (built with blocks, permanent).

## 9. Rune souls from mini-bosses (round 23, replaces mini-boss points)

✔ User (round 23, change of OQ 72): **the zone only changes hands when the final boss dies**; holding all
the mini-bosses must **not** win by itself. Instead:
- Each **mini-boss has a rune** (new field `rune:` in `boss.yml`, boss pipeline §4.1; the pilot **Fungal
  Witch** is naturally **Nature**: spores, mushrooms).
- The faction of **the last hit** on a mini-boss gets **that rune's soul until the end of the event**.
- The soul boosts **only that faction's players whose skills use that rune** (user's example: the Fire soul
  boosts a tank who took the Fire node *fire defense*). Others in the faction get nothing from it.
- Proposal per soul (inspired by LoL souls, all yml): **+10 % rune power** for that rune, and one perk:
  - **Fire soul:** hits with Fire skills leave a small burn;
  - **Frost soul:** Frost slows last 20 % longer;
  - **Storm soul:** +10 % speed while a Storm skill is ready;
  - **Nature soul:** heals over time out of combat (5 s without damage).
- **The final boss decides the zone:** the faction with the **last hit on the boss** takes it (proposal:
  the power score is removed; souls are the reward of mini-bosses). Timeout: the holder keeps the zone (✔).
- **Snowball check:** souls are small, each mini-boss has a different rune (drawn per event among the 4, or
  fixed per mini-boss: OQ 112), and a soul helps only players of that rune, so a faction with many runes
  benefits more than a faction that only kills.
- Private dungeons: the same soul for the run's faction for the rest of the run (proposal, small values).

## 10. Casting in Minecraft

- **Passives and procs** (on hit, when hit) work by themselves.
- **Active skills:** one custom item, the **Rune focus**, in the hotbar (1 slot, important with the travel
  bag rule: only the hotbar travels). **Right-click casts** the selected skill, **the swap-hand key (F)
  while holding the focus cycles** between the player's **3 active skills** (shown on the action bar).
  Cooldowns use the item's native cooldown display (1.21 `use_cooldown` component with a cooldown group per
  skill).
- Zone skills aim where the player looks (ray up to 16 blocks), with the telegraph of §6.

## 11. Proving that compositions are counterable

Balance cannot be proven on paper, but the **validator** of the tree method (step 5) is extended:
1. Every effect in the catalogue has **≥ 1 counter**, available in **≥ 2 jobs** and **≥ 2 runes**.
2. Every rune has its **blind spots** respected (no Fire node that slows, no Storm node that heals…).
3. For every possible **4-player faction composition** (jobs × rune choices), the script lists which enemy
   compositions counter it, and **flags** any composition with no counter or that counters everything.
4. Caps and diminishing returns (§6) are checked on the strongest 50-point build per job.
Then the beta (✔ beta after each epic) tunes the numbers in yml.

**Challenges to accept:**
- **More content per tree.** Runes double the fork content; the method (catalogue first, Miner + Hunter
  first) keeps it manageable.
- **Readability in a block game:** many effects at once become noise. Particles per rune colour, action-bar
  icons for active effects, and a short list of effects (the catalogue, not 100 unique ones).
- **Server load:** zones and procs run on the dungeon and faction servers; zones are checked every 5 ticks,
  not every tick, with a cap on active zones per region.
- **Bosses must respect the same rules** (they can be stunned? proposal: bosses are immune to stun and root,
  slows reduced by 50 %, like most games).

## 12. Open questions (mirrored in `CLAUDE.md`)

- **105** Runes: **Fire, Frost, Storm, Nature** with the wheel Fire > Frost > Storm > Nature > Fire, soft
  ±15 % (recommended)? A 5th rune Arcane/Ender later (recommended: later)?
- **106** Runes per job (Miner Frost + Fire, Lumberjack Nature + Storm, Hunter Fire + Storm, Farmer Nature +
  Frost, Alchemist Fire + Nature) (recommended), or changes?
- **107** Specialities: forks become rune choices, rune power per node of one rune, **max 2 bridge nodes**
  per tree that unlock another rune's skill (recommended)?
- **108** Effect catalogue §4 and combat rules §6 (no stacking, diminishing returns on controls, stun 1 s in
  PvP / 2 s PvE, telegraph 0.5 s, PvP values lower) (recommended)?
- **109** Casting: one **Rune focus** item, right-click casts, F cycles 3 active skills, native cooldowns
  (recommended)?
- **110** Rune power and a new **rune resistance** stat (AP/AD idea) (recommended)?
- **111** Summoner: max 2 minions, 15 s, weak, follow and attack the Alchemist's target, counters area
  damage / banish / taunt (recommended)?
- **112** Souls: mini-boss rune in `boss.yml`, soul to the last-hit faction until the event ends, +10 %
  rune power + one perk, only for that rune's players; **zone to the last hit on the final boss** (power
  score removed) (recommended)? Mini-boss runes **drawn per event** (recommended) or fixed per mini-boss?
  Also in private dungeons (recommended)?
- **113** Composition validator §11 (recommended)? Bosses immune to stun and root, slows halved
  (recommended)?

[wiki: Dragon Slayer]: https://wiki.leagueoflegends.com/en-us/Dragon_Slayer
[wiki: Types of CC]: https://wiki.leagueoflegends.com/en-us/Types_of_Crowd_Control/Summary
[LoL CC guide]: https://tracker.gg/lol/articles/every-crowd-controls-in-lol-and-how-to-counter-them
[tenacity]: https://www.esports.net/news/lol/what-is-tenacity-in-lol
[colour pie explained]: https://casualplaneswalker.com/wiki/color-pie
[colour wheel]: https://draftsim.com/mtg-color-wheel/
[MTG keywords]: https://gamertagmythras.com/blog/magic-the-gathering/mtg-keywords-explained
