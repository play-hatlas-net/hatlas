# Ruby economy observatory and price indexing (plan, 2026-11-16)

> **Status: plan only, nothing built.** Source: user, round 21: "a tool, in game or on the website, to see how
> many rubies were generated on the whole network, every transaction, rubies in circulation and burned, by
> day / week / month; admins adapt NPC prices automatically in a recession or crisis; if transactions are
> public, show ids but keep players anonymous; maybe index every static price on the rubies in circulation.
> Challenge these questions."
> Builds on what exists: the ruby ledger ([`economy.md`](economy.md)). Open questions in `CLAUDE.md` (OQ 92–93).

---

## 1. What already exists (no need to rebuild)

| Need | Already there |
|---|---|
| Every ruby move | `ruby_ledger` (append-only, kinds `MINE`, `SHOP_BUY`, `TRADE`, …) |
| Generated / burned / supply | `/hatlas economy supply`, view `web_ruby_daily` (emitted, burned, placed, broken, transferred, per **UTC** day) |
| Transactions for the website | view `web_ruby_transactions` (no coordinates) |
| History of one party | `/hatlas economy history <player|faction>` |

So the observatory is mostly **new views and pages on top of the ledger**, plus three gaps to fill first.

## 2. Gaps to fill

1. **The other servers.** Rubies will be created on the mining server. Plan already settled: the mining
   server never writes the ledger; its `MINE` rows travel in the handoff row and are written by the faction
   server ([`mining-world.md`](mining-world.md) M2). With that, **one ledger covers the whole network** (the hub
   and dungeon servers never create or burn rubies: dungeons refuse them, the mining world keeps them in the
   handoff). New kinds to add: `JOB_SWITCH`, `JOB_NODE_REMOVE`, `JOB_RESPEC` (burns), `CITY_TAX` (transfer),
   later Jokeyrini/Wizard payments.
2. **Week and month.** Only daily buckets exist, by UTC day. Proposal: views `web_ruby_weekly` and
   `web_ruby_monthly`, and **days cut at midnight Europe/Paris** (the same zone as play hours and the mining
   reset), so "today" means the same thing in game, on the site and in the reset.
3. **Where the rubies are.** "In circulation" = emitted − burned (known). Where they sit is computable from
   the ledger itself: **the balance of each party = everything received − everything sent**. That gives,
   without scanning inventories:
   - total in **faction vaults**, in **player inventories**, in **placed ruby blocks**, **in transit** (mining
     handoff rows);
   - **concentration**: share held by the top 1 / 3 / 10 factions, a Gini index;
   - **dormant rubies**: balances of players not seen for 14+ days (they inflate the supply without being
     used);
   - **velocity**: transferred per day ÷ supply (is money moving or hoarded?).
   A daily job checks the ledger balances against the real vault contents and logs any gap (leak detector,
   like `UNTRACKED_PICKUP`).

## 3. Who sees what (privacy)

**Challenge: hashing the UUID does not anonymise.** The network runs in offline mode: a player's UUID is
computed from their name ([`identity.md`](identity.md), round 5). Anyone can take a name, compute the UUID,
hash it and find the "anonymous" id. Even a **secret key** (HMAC) only gives a **pseudonym**: one id per
player, the same in every row, so its whole history can be followed and linked to the player by timing
(who was online, who traded with whom, who bought at the shop at 21:03). Under the GDPR a pseudonym is still
personal data.

And faction flows are **strategic**: a public list showing "faction X received 900 rubies yesterday" tells
everyone whom to raid.

| Option | Shows | For | Against |
|---|---|---|---|
| **A. Aggregates public, details private** (recommended) | public: daily/weekly/monthly totals, by kind, supply, concentration, velocity, price index. Each player sees **their own** rows when logged in; faction members see **their faction's vault** rows; admins see everything | no player or faction can be traced; enough for transparency | no public "block explorer" |
| B. Public feed with pseudonyms, 24 h delay | every row, keyed pseudonym (HMAC with a server secret, rotated monthly), amount, kind, no coordinates | "public chain" feel | linkable by timing; strategic leak for factions; GDPR deletion must also cut the pseudonym |
| C. Public feed with real names | everything | full transparency | privacy and raid intelligence: not acceptable |

Proposal: **A**, with an optional B feed limited to **large movements** (e.g. ≥ 500 gems, delayed 24 h,
pseudonyms) if the community wants a "whale watch". A deleted account's rows are already anonymised
([`identity.md`](identity.md) §5).

## 4. Where it is shown

- **Website** `/economy` (public, aggregates): supply curve, emitted vs burned per day/week/month, by kind,
  concentration, velocity, current price index. Logged-in pages: "my rubies" history, "my faction's vault".
- **In game:** `/economy` (players): supply, today's emitted/burned, current price index; `/hatlas economy
  …` (admins) adds `report [day|week|month]`, `top`, `dormant`, `index`.
- **Alerts** (admin, Discord/website): emission spike, burn collapse, concentration over a threshold, a
  ledger-vs-vault gap.

## 5. Automatic prices: challenged

The idea: every price the server sets (shop prices, job switch, Wizard fees, …) follows the rubies in
circulation, so a crisis corrects itself.

**What goes wrong with a naive index (price = base × supply / starting supply):**
1. **It punishes the poor for the rich.** If three big factions hoard rubies, the supply goes up and
   **every** price goes up, including for new and factionless players who own nothing. The rich don't care;
   the poor are priced out. Concentration is not inflation, and higher prices do not fix it.
2. **Dormant rubies count.** Players who quit keep their balance: the supply grows, prices rise, while
   nobody is spending.
3. **It feeds itself.** Higher prices → fewer purchases → less burned → supply stays high → prices stay high.
   Without damping it swings.
4. **It can be played.** A faction that knows the formula can hold or release rubies to move prices before a
   big purchase.
5. **Players hate surprise prices.** A shop item costing 40 on Monday and 55 on Friday feels like a bug.

**What actually controls a closed currency like ours:** the **faucet** (how many rubies are created: ore
weights in the mining world, the travel bag size) and the **drains** (shop burns, job switches, Wizard,
crystal costs). Prices are the last lever, not the first.

**Proposal, in three steps:**

| Step | What | When |
|---|---|---|
| **1. Observe** | the observatory above + alerts; a **suggested index** computed every day but not applied | epic 1 (jobs), so the beta has data |
| **2. Manual index** | admins apply the suggestion with `/hatlas economy index set <value>` (global multiplier on every server-set price, shown on the shops: "price index 1.10") | beta |
| **3. Automatic, damped** | weekly update, **based on active supply** (rubies held by players seen in the last 14 days, vaults of active factions), **max ±5 % per week**, bounded **0.5×–2×**, announced on Monday, frozen during events; the **faucet** adjusts too (ruby weights of the mining world move toward a target: emitted ≈ burned × (1 + target growth)) | after the beta, if step 2 proved the formula |

All values (`economy.yml > index`: window, step, bounds, target growth, mode `off|suggest|manual|auto`)
default to **suggest**.

Which prices follow the index: shop prices, job switch, Wizard fees, Jokeyrini/key costs, crystal skill
ruby costs (if any). Not: auction prices (set by players), city tax (a percentage, it follows by itself).

**Against concentration** (rich factions), better tools than prices: the raid drops already move rubies;
a **vault upkeep** above a size (small % per week burned) or growing costs for big factions (the size
tiers of the city rewards already exist). To discuss only if the beta shows the problem.

## 6. Open questions (mirrored in `CLAUDE.md`)

- **92** Observatory: privacy option **A** (public aggregates, own and faction details when logged in)
  (recommended), or B / C? Days cut at **midnight Europe/Paris** (recommended)? Optional "whale watch" of
  movements ≥ 500 gems, 24 h delay (recommended: later, if asked)?
- **93** Price index: start in **suggest** mode, then manual, automatic only after the beta with damping
  (±5 %/week, 0.5×–2×, active supply) (recommended)? Faucet (mining ruby weights) as the first automatic
  lever (recommended)?
