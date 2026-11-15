# Funding and transparency (plan, 2026-11-10)

> **Status: plan only.** Decided by the user (round 11): access costs what the player chooses,
> **minimum EUR 1**, presets **EUR 5 (default), 10, 20**, for 30 days, one-time payment, **Stripe
> receipt only** (no invoice). The point of the free price is **transparency**: the website shows what
> the whole network costs each month and a **progress bar** towards that amount; anything above it is
> put back into the server (hardware, mob models, maps, new gameplay).
> Payment mechanics: `docs/identity.md` §8. Website side: `../hatlas-webapp/CLAUDE.md` (Decision 9,
> transparency page).

## 1. What the network costs (user's figures, round 11)

The seller is under the VAT franchise, so VAT paid on costs **cannot be recovered**: the real cost is
the amount **incl. VAT (TTC)**.

| Item | User's figure | Per month (TTC) |
|---|---|---|
| Domain `hatlas.net` + DynHost (OVH) | EUR 12.08 HT = **14.50 TTC / year** | 1.21 |
| Email `no-reply@hatlas.net`, OVH mailbox 15 GB (✔ user: mail only) | EUR 19.08 HT = **22.90 TTC / year** | 1.91 |
| Electricity: ~170 kWh / month × **EUR 0.15 / kWh** (✔ user, round 12) | **EUR 25.50 / month** | 25.50 |
| Hardware maintenance (thermal paste, parts…) | **EUR 25 / year** | 2.08 |
| **Added:** consumer mediator CNPM (about EUR 60 HT for 3 years, + per-case fee only if a dispute) | ≈ 24 TTC / year | 2.00 |
| **Running costs** | | **≈ EUR 32.70 / month** (≈ EUR 392 / year) |

Remarks:
- **Electricity** (✔ user, round 12): the price is **EUR 0.15 per kWh as paid**, so 170 × 0.15 =
  **EUR 25.50 / month** (replaces the 29.65 TTC first given). If 0.15 turns out to be before tax,
  the line becomes ≈ EUR 30.60 and the goal ≈ EUR 53. 170 kWh a month is about **236 W around the
  clock**: by far the biggest cost (78 %). The second CPU holds no RAM and is not needed
  for 40 players; removing it or limiting its power could save a few euros a month: measure with a
  wall power meter first (`docs/deployment.md` §2.11).
- **TLS/HTTPS costs nothing**: Caddy gets free Let's Encrypt certificates. ✔ The EUR 22.90 is the
  mailbox only (15 GB, one year), so it stays and no TLS line is needed.
- Not counted (the user's own costs): the home internet connection; one-time purchases (the RAM,
  the offline backup disk) are shown as **investments** (§3), not running costs.
- CFE (local business tax): micro-entrepreneurs with turnover **≤ EUR 5,000 a year are exempt**;
  this network stays far below.

## 2. The monthly goal: costs are paid **after** Stripe and URSSAF

Each payment loses Stripe's fee (EEA card 1.5 % + EUR 0.25) and the URSSAF contributions (BIC services
≈ 21.2 % + 0.1 % training ≈ **21.3 %**) before it can pay a bill. With EUR 5 payments on average,
fees ≈ 6.5 % + 21.3 % ≈ **27.8 %**:

> goal = 32.70 / (1 − 0.278) ≈ **EUR 46 collected per month** ≈ 10 payments of EUR 5
> (≈ EUR 1.15 per player per month for 40 players).

- Income tax on the surplus (micro-BIC: 50 % allowance then the household rate, or the optional
  *versement libératoire* ≈ 1.7 % of turnover for services) is **not** in the goal; if the
  versement libératoire is chosen, the goal rises to ≈ EUR 47. To confirm with the accountant.
- The page computes the **real** numbers from each payment (Stripe gives the exact fee of every
  payment), not this estimate.

## 3. On the website (`/transparency`, fr/en, linked from the home page and `/renew`)

1. **Progress bar of the current month**: "EUR X of EUR 46 collected this month", from the payments of
   the calendar month (counted when paid, even if the 30 days run into the next month). Above 100 %:
   the extra goes to the **improvement fund**.
2. **Where EUR 5 goes**: Stripe ≈ 0.33, URSSAF ≈ 1.07, server costs ≈ 3.60, shown next to the amount
   choice on `/renew` too (preset buttons 5 / 10 / 20, free field from EUR 1 **to EUR 100**: ✔ user,
   round 12, maximum per payment; checked on our page and again in the webhook).
3. **Cost table** (§1) with the date of the last update.
4. **History** of the last 12 months: collected, fees, costs, surplus or shortfall.
5. **Improvement fund**: balance, and every spending with its date and what it bought (e.g. "2 × 8 GB
   RAM, EUR 35", "mob models pack", "map commission").
6. Everything above shows **totals** only.
7. **Supporters list** (✔ user, round 12): the **25 biggest supporters, highest first**, on the
   transparency page. Conditions, because a name next to an amount paid is personal data made public:
   - **opt-in only**: a checkbox on `/renew` ("show my Minecraft name on the supporters list"),
     **unchecked by default**, changeable any time in the profile (GDPR consent, art. 6.1.a and 7);
     players who did not opt in are skipped, not shown as "anonymous" with their amount;
   - **Minecraft name only** (never email or real name); a deleted account disappears from the list;
   - **minors**: in France consent to an online service alone is valid **from 15** (art. 45 loi
     Informatique et Libertés); the checkbox says "15 or older, or with a parent's agreement" (no age is
     collected otherwise);
   - **refunded or disputed payments are removed** from the totals;
   - it **gives nothing in game** (no rank, no tag, no colour: Mojang's terms forbid paid advantages
     and visible paid perks are risky); written on the page;
   - privacy policy: one paragraph (purpose, basis = consent, withdrawal, kept while the account
     exists).
   Defaults chosen (change if wanted): ranking by **total over the last 12 months** (an all-time list
   freezes the top forever), showing **name + total rounded to the euro**; a second tab "this month".
   Data: a `show_in_supporters boolean default false` (+ `consented_at`) on the web account;
   the ranking is a SQL view over the payments.

Data (schema `web`, owned by the website; edited by SQL or a later admin page):
- `web.costs (id, label_fr, label_en, amount_cents, period 'month'|'year', valid_from, valid_to)`;
- `web.investments (id, spent_on, label_fr, label_en, amount_cents)`;
- payments from the website's payment table (amount, Stripe fee from the balance transaction, paid_at).

Wording (legal):
- "Surplus is reinvested in the server" is an **intention**, not a contract term; say it as such.
  Legally the money is the micro-entrepreneur's turnover, not a fund held for players.
- The price stays the price of **30 days of access**, not a donation (`docs/identity.md` §8).
- Paying more gives nothing in game (Mojang's terms; showing that prices cover running costs fits the
  strictest reading of those terms).

Bought assets (mob models, maps, plugins): check that each licence allows use on a **server that
charges for access**.
