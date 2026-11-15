# Player identity and login (plan, 2026-11-08)

> **Status: plan only, nothing built.** Written from the control repo over three rounds with the user
> (2026-11-08): round 1 = webapp Open Questions 22–24; round 2 = Hatlas Open Question 26 and the
> user's login ideas, challenged; round 3 = Open Question 27 answered; round 4 = Open Question 28; round 5 = Open Question 29 + security choices (§2, §7); round 6 = Open Question 30
> (§2, §8); round 7 = Open Question 31 (code always asked, seller).

## 1. The problem

The network runs in **offline mode** (non-premium clients accepted, ✔ user). Velocity gives every
player the offline UUID `UUID.nameUUIDFromBytes("OfflinePlayer:" + name)`: **anyone can join under any
name**, and every contract (`web.tickets`, presence, all Hatlas data) keys on that UUID. A login must
come **before** the ticket gate.

## 2. Decisions

| # | Decision (✔ user 2026-11-08) | Notes from the challenge |
|---|---|---|
| D1 | **Own login in hatlas-proxy** (no AuthMe), **fresh start** (no import) | |
| D2 | **Registering in game creates the website account**; one web account ↔ one game account | `/link` and `web.link_codes` retired |
| D3 | **No credential ever passes through Minecraft**: the proxy and the hub never see a password, a hash or a 2FA code. `/register` and `/login` only put a **single-use link** in chat | The proxy never touches better-auth's tables |
| D4 | **Email verified before playing** | A chat link proves you hold the game session, not that you own the email |
| D5 | **No IP session**: every connection needs `/login` → link → approved on the site by a browser **logged in to that account** (2FA there) | User's proposal, round 3. Agreed: simpler (no `game_sessions` table, no shared-IP hole) and safer. Cost: one browser click per connection; the website session lifetime becomes the security knob (§3.4) |
| D6 | **"Log out of the game everywhere"** on the site | With D5 it means: end the website sessions **and** kick the player from the game (§3.4) |
| D7 | **Email: OVH SMTP, `no-reply@hatlas.net`**, same as the website | SPF + DKIM records on `hatlas.net` (OVH zone) |
| D8 | **GDPR: privacy page, account deletion, data export** in the site profile | §5 |
| D9 | 2FA and password reset only on the website (admin fallback on the server) | |
| D10 | **Anti-abuse: the 4 measures of §2.1**, for account creation **and** login (round 4) | The single-use link closes the website side; these close the game side |
| D11 | **Website session 7 days, renewed each day the site is used** (round 4) | §3.4 |
| D12 | **Approximate location of IPs from a local database**, shown on the approval page and in the profile (round 4) | §3.5 |
| D13 | **Log out of the game everywhere kicks the player at once** (round 4) | §3.4 |
| D14 | **Account deletion** (round 5): out of the faction (owner → next highest rank, disband if alone), **every related data deleted**, ruby transactions kept **anonymous** | §5: a UUID alone is *not* anonymous in offline mode |
| D15 | **IP location: DB-IP City Lite, self-hosted** (round 5); **activity history 90 days** (masked IP, city, country) | §3.5 |
| D16 | **Passwords hashed with argon2id** (round 5) | §7.1 |
| D17 | **2FA: authenticator app (QR code, TOTP) or a code sent by email**, + backup codes (round 5) | §7.2: email codes are the weaker option |
| D18 | **"Download my data" button** on the profile (round 5, GDPR access + portability) | §5 |
| D19 | **Security emails** (round 6): game login from a **new location**, password reset, email change, 2FA change, account deleted | New location = city + country not in the last 90 days of activity (§3.5) |
| D20 | **Deleting the account loses a running ticket, no refund**, with a warning on the page (round 6) | Must also be in the CGV (§8) |
| D21 | **Refuse passwords found in known leaks** (Have I Been Pwned) (round 6) | §7.1 |
| D22 | **Links typed by players are never clickable**; only server messages carry links (round 6) | §7.5 |
| D23 | **CGU + CGV (+ legal notice), French and English** (round 6) | §8 |
| D24 | **Every approval asks for a code typed in game**, whatever the IPs (round 7, user: "better security") | §7.3 |
| D25 | **Seller: the user as micro-entrepreneur** (SIRET 887 895 878 00015) (round 7) | §8 |

### 2.1 Anti-abuse (✔ user 2026-11-08, round 4)

The single-use token closes the website side (no sign-up page without a live token from the game). In
offline mode a bot can still join under any name and type `/register` or `/login` itself (our test
bots do), so four measures together:

1. **Proxy limits** (config `auth.limits.*`): per IP, 3 `/register` per hour and 10 `/login` per hour;
   one open request per name (a new one replaces the old one); max 3 GUEST connections per IP at once.
2. **Email verified before playing** (D4): an unverified account never plays and is deleted after
   24 h with its name.
3. **ALTCHA** (✔ user): self-hosted proof-of-work (server secret in the site, no third party, nothing
   for the privacy page) on the **sign-up** page and on the website **sign-in** form (the password
   step before an approval).
4. **Website limits**: per IP on sign-up, sign-in (better-auth rate limit), approval pages and email
   sending (stay under the OVH SMTP quota; at most 1 verification email per account per 5 min).

## 3. Design

### 3.1 Flow

```
join ─▶ hub, GUEST (frozen, no compass; chat and commands blocked but /register /login)

/register (name not registered)
  ─▶ proxy: web.auth_requests(kind=REGISTER, token_hash, uuid, name, ip, expires 10 min) ─▶ link in chat
  ─▶ site /register?token=…   (single use, ALTCHA) email + password
  ─▶ better-auth user (unverified) + web.game_accounts(uuid, user_id, name, verified_at NULL) ─▶ verification email
  ─▶ player clicks the email link ─▶ verified_at = now()
  ─▶ proxy (polls the open requests of its GUEST players every 2 s) ─▶ LOGGED_IN, request deleted

/login (name registered and verified)
  ─▶ proxy: web.auth_requests(kind=LOGIN, …) ─▶ link in chat
  ─▶ site /login/approve?token=…  must be signed in as THIS account (password, 2FA if on)
     page: "Approve the login of Steve from <ip>, <place>, <time>?" ─▶ Approve (POST)
     page then shows a 6-digit code (D24) ─▶ player types /confirm <code> in game
  ─▶ proxy checks the code ─▶ LOGGED_IN, request deleted, last_login_at

LOGGED_IN ─▶ compass, ticket gate (unchanged), presence
```

- GUEST timeout `auth.timeout-seconds`: **600** (time to read an email). A player who leaves before
  verifying just comes back and types `/login` once verified.
- `/register` on a registered name → "use /login"; on a name with an unverified registration →
  "check your email (sent to j***@…)". `/login` on an unknown name → "use /register".
- Unverified registrations are deleted after **24 h** (better-auth user + `game_accounts` row): the name
  is free again.
- A website account can **only be created in game** (it needs a Minecraft name). The site's sign-up
  page without a token says "join `play.hatlas.net` and type /register".

### 3.2 UUID

On `GameProfileRequestEvent` the proxy looks the name up case-insensitively: registered, same case →
the stored UUID; other case → refused ("registered as `Steve`"); unknown → the offline UUID, stored at
registration. Today's UUIDs stay valid (Hatlas data, fixtures, bots); an admin rename keeps the UUID.

### 3.3 Tables (contract, created by the webapp migrations like every `web` table)

```sql
web.game_accounts (                 -- written by the SITE; proxy SELECT + UPDATE(last_login_at)
  uuid          uuid PRIMARY KEY,
  user_id       text NOT NULL UNIQUE REFERENCES web."user"(id) ON DELETE CASCADE,
  name          text NOT NULL,
  name_lower    text NOT NULL UNIQUE,
  registered_at timestamptz NOT NULL DEFAULT now(),
  verified_at   timestamptz,        -- email verified; NULL = cannot play
  logout_at     timestamptz,        -- "log out of the game everywhere" (D6)
  last_login_at timestamptz
)
web.auth_requests (                 -- proxy INSERT/DELETE, site SELECT + UPDATE(approved_at)
  token_hash  bytea PRIMARY KEY,    -- sha256 of the token; the token itself only exists in the chat link
  kind        text NOT NULL CHECK (kind IN ('REGISTER','LOGIN')),
  uuid        uuid NOT NULL,
  name        text NOT NULL,
  ip          inet NOT NULL,        -- shown on the approval page, deleted with the row
  created_at  timestamptz NOT NULL DEFAULT now(),
  expires_at  timestamptz NOT NULL, -- 10 min
  approved_at timestamptz,
  confirm_hash bytea               -- sha256 of the 6-digit code shown after approval (D24), LOGIN only
)
```

- Token: 32 random bytes, base64url, in the URL only; the site hashes what it receives. Used once: the
  site refuses a token already used (REGISTER: `game_accounts` row exists; LOGIN: `approved_at` set),
  the proxy deletes the row when it logs the player in, and cleans expired rows.
- One open request per name; a LOGIN request is approved only by the session of
  `game_accounts.user_id`; a REGISTER token is refused if the name was registered meanwhile.
- Grants: `hatlas_proxy` SELECT on `game_accounts` + UPDATE (`last_login_at`), DML on `auth_requests`;
  **nothing** on `user` / `account` / `session` / `verification` / `twoFactor` / payments.
- Retired: `web.link_codes`, the proxy's `/link`, the site's link page. Gone from round 2:
  `web.game_sessions` (D5).

### 3.4 Sessions, log out everywhere, lost credentials

- **The game login lasts the connection.** Next connection → `/login` again (D5).
- **Website session** (D11): better-auth `session.expiresIn` = 7 days, `updateAge` = 1 day (renewed
  each day the site is used). It decides how often the player retypes the password (+ 2FA) when
  approving. The approval page shows name, IP, approximate location (§3.5) and time, so a link sent by
  someone else is visible as such.
- **Log out of the game everywhere** (D6, D13): the site revokes every better-auth session of the
  account, deletes its pending LOGIN requests, sets `game_accounts.logout_at = now()` and sends
  `NOTIFY hatlas_logout, '<uuid>'`. The proxy `LISTEN`s on that channel and **kicks the player at once**
  ("You were logged out from the website"); the periodic check it already runs for ticket expiry also
  compares `logout_at` with the login time, as a fallback if a notification is missed (proxy
  reconnecting to the database). The next connection needs `/login` and a new website sign-in.
- Lost password: website "forgot password" (email via OVH SMTP). Lost 2FA: backup codes. Admin
  fallback: a webapp CLI on the server (`npm run admin -- reset-password|disable-2fa|logout <name>`).

### 3.5 Approximate IP location (D12)

- **Local database, no online lookup** (no IP sent to a third party): an IP → city/country file in
  MaxMind's `.mmdb` format, read by the site with the `maxmind` npm reader. Recommended **DB-IP "IP to
  City Lite"** **?**: CC BY 4.0, free, no account, monthly update (the site credits "IP geolocation by
  DB-IP"). Alternative: MaxMind GeoLite2 City (needs an account, a licence key and its EULA).
- The file lives in a volume of the website's compose, refreshed by `deploy/update.sh` when older than
  a month (not baked into the image).
- **Only the site resolves locations**; the proxy only writes the raw IP in `auth_requests` (10 min).
- Shown on the **approval page** ("Steve from Lyon, France, 2 min ago") and in the profile's **activity
  list**: game logins (approved requests) and website sign-ins (better-auth `session.ipAddress`), with
  date, approximate city/country and a masked IP (`92.184.x.x`).
- Stored for the history: `web.login_history (id, user_id, at, kind GAME|WEB, ip_masked, city, country)`,
  written by the site, **kept 90 days** **?**; the full IP is not kept beyond the request and the live
  website session.

### 3.6 What changes where

| Repo | Change |
|---|---|
| hatlas-proxy | `auth/`: GUEST/LOGGED_IN, `/register` `/login`, tokens + `auth_requests`, 2 s poll, `LISTEN hatlas_logout` kick + `logout_at` fallback check, UUID mapping, gate and server switch need LOGGED_IN, per-IP limits (§2.1), `hatlas:auth` messages; **remove `/link`**; dev tables in `web-schema.sql`; suites `auth/` (approval / verification done by an SQL step) |
| hatlas-hub | GUEST: freeze, no compass, instructions (title + chat); suites |
| hatlas-webapp | better-auth email + password with **required verification**, `twoFactor`, session 7 days; OVH SMTP mailer; ALTCHA on sign-up and sign-in, rate limits (§2.1); pages `/register?token=`, `/login/approve?token=` (with location); profile: 2FA, password, **activity list** (§3.5), **log out of the game everywhere** (+ `NOTIFY hatlas_logout`), **export**, **delete**; privacy page; IP location `.mmdb` volume refreshed by `deploy/update.sh`; `login_history` (90 days); migrations §3.3 + grants; 24 h clean-up job; admin CLI; drop `link_codes` and the link page |
| hatlas (here) | §1.1 contracts; `players` table + `web_players` view (§4); deletion hook (§5); production configs with `https://play.hatlas.net/…` |
| test stack | fixture `game_accounts` (verified) for Tester1–4; a scenario step approves the request in SQL |

Hatlas' own login check stays a ticket check (the faction server is only reachable through the proxy).

## 4. Player names (✔ user, webapp Open Question 22)

Hatlas schema V4: table `players (uuid PRIMARY KEY, name, first_seen, last_seen)` written on join and
quit, view **`web_players`** granted to `hatlas_web`. The site joins every `web_*` UUID on it.

## 5. GDPR (D8)

**Privacy page** (`/privacy`, fr/en): controller and contact, data kept and why (email, password
hash, 2FA secret, Minecraft name/UUID, IPs of login requests ≤ 10 min, tickets and payments, game
data and ruby history, login activity: masked IP + approximate location for 90 days), processors (OVH
SMTP, Stripe; hosting on the operator's own machine; IP location computed locally, credit "IP
geolocation by DB-IP"), retention,
rights (access, export, rectify, delete, complain to the CNIL). Only the session cookie (strictly
necessary) → no cookie banner, as long as no analytics are added.

**Export** (D18, profile → **"Download my data"** button, JSON): account (email, created, 2FA
method, never secrets), activity list, game account (name, UUID, dates), tickets and payments, and
**all** the game data about that UUID, not only what the current `web_*` views show: Hatlas adds a
`web_player_data(uuid)` function (faction and role, homes, job and quests, auction listings, ruby
transactions as sender or receiver), granted to `hatlas_web`.
Rate-limited (e.g. once per hour).

**Delete** (profile → confirm with password, + 2FA):
- Website: better-auth user, sessions, 2FA, `game_accounts` (cascade) deleted; open requests deleted;
  the player is kicked if online; the name is free again.
- Payments: **kept** as long as accounting law requires (invoices), detached from the account
  (no email); Stripe customer deleted or anonymized.
- Game data in Hatlas (D14, ✔ user): the player leaves their faction (an owner's faction passes to
  its highest-ranked member, or is **disbanded** if alone, with the usual disband rules), and **every
  row about the player is deleted**: membership and role, homes, job and quests, Jokeyrini, combat
  timer, auction listings (the items are deleted), visits, `players` row.
- **Ruby ledger anonymized, not just kept** (challenge): in offline mode the UUID is
  `nameUUIDFromBytes("OfflinePlayer:" + name)`, so anyone who knows the name recomputes it: keeping
  the UUID is pseudonymous, not anonymous. Hatlas replaces the player's UUID in `ruby_ledger`
  (sender, receiver, actor) by **one new random UUID per deleted player** (flows stay consistent for
  the economy stats) and clears the names; `web_ruby_transactions` shows "deleted player". This is
  the only UPDATE ever made on the append-only ledger, and it is logged.
- Hatlas learns about deletions from `web.deleted_accounts (uuid, deleted_at, done_at)` (site INSERT,
  Hatlas SELECT + UPDATE `done_at`), read at start and every minute; the site removes the row once
  `done_at` is set. A player online on the faction server is kicked by the proxy first.
- Backups: deleted data stays in the backups until rotation (7 daily + 4 weekly, about 5 weeks); the
  privacy page says so. The website schema `web` must be in the backups too (§7.6).
- The page warns that a running ticket is lost, without refund (D20, also in the CGV).

## 6. Open points

All identity questions are answered (round 7, 2026-11-08). What stays open is listed in `CLAUDE.md`
(Open Questions 32–35): Mojang terms vs offline mode, the ticket price, VAT/mediator with an
accountant, the production machine details (`docs/deployment.md` §2).

## 7. Security review before code (round 5)

### 7.1 Passwords (D16)
- argon2id through better-auth's custom `password.hash` / `verify` with `@node-rs/argon2`; PHC string
  stored; parameters **m = 19 MiB, t = 2, p = 1** (OWASP minimum), raised if the machine allows
  (about 50 ms per hash); rehash on sign-in when the parameters change.
- Memory per hash × concurrent sign-ins: the sign-in rate limit (§2.1) also protects the machine.
- Rules: 10 to 128 characters, no composition rules; **refused if found in known leaks** (D21):
  Pwned Passwords range API, k-anonymity (only the first 5 hex chars of the SHA-1 leave the server,
  never the password or the email), better-auth `haveIBeenPwned` plugin, on sign-up, reset and change.
  If the API is unreachable the password is **accepted** and the failure logged (sign-up never blocked
  by a third party). Named on the privacy page.
- Never logged: the site's and the proxy's logs never contain a password, a token or a full email.

### 7.2 2FA (D17)
- better-auth `twoFactor`: **TOTP** (QR code + manual key, 6 digits, 30 s) **or email code** (6
  digits, 10 min, 5 attempts), + 10 single-use **backup codes** shown once.
- **Challenge:** an email code is a weak second factor here, because the email is also the password
  reset channel: whoever controls the mailbox can reset the password *and* receive the code. The page
  recommends the app, labels email as "basic" and says why. Passkeys (WebAuthn) later.
- Turning 2FA off or changing its method needs the password **and** a current code.

### 7.3 The main remaining risk: approval phishing
An attacker joins as `Steve`, types `/login`, and sends Steve the link ("click to get a reward").
Steve, signed in on the site, clicks Approve → the attacker plays as Steve. This is the known weak
point of every "approve on another device" login. Mitigations:
- approval only by **POST with an explicit button** (SvelteKit form action, origin check), never on
  GET; page with `Referrer-Policy: no-referrer` and `Cache-Control: no-store`; the reverse proxy does
  not log query strings;
- the page shows name, IP, location, time, and "only approve if YOU just typed /login";
- **a 6-digit code on every approval** (D24): after Approve, the page shows a code that must be typed
  in game (`/confirm 123456`, 3 attempts, valid until the request expires). The attacker would also
  have to get Steve to send the code back. A different IP adds a red warning on the page. Stored as
  `auth_requests.confirm_hash` (sha256), written by the site, checked by the proxy.

### 7.4 Account changes
- Email change: verify the new address, notify the old one, needs password + 2FA.
- Security emails (D19): game login from a new location, password reset, email change (to both
  addresses), 2FA change, account deleted. Each says when, where (approximate) and what to do if it
  was not you (link: log out of the game everywhere + change password).
- Generic answers on sign-in and "forgot password" (no "unknown email"). In game, names are public
  anyway, so `/register` saying "name taken" leaks nothing.

### 7.5 Network (offline mode makes this critical)
- **The hub and the faction server must only be reachable through Velocity**: bound to the Docker
  network / 127.0.0.1, never published; the router forwards only the proxy port (and HTTPS for the
  site). Velocity **modern forwarding** with a long random `forwarding.secret`, Paper
  `proxies.velocity.enabled: true`. An exposed backend port would let anyone join directly under any
  name and UUID, skipping the login.
- Names limited to `[A-Za-z0-9_]{3,16}` at the proxy.
- Player chat (D22): links typed by players are never clickable, against fake login links. Player
  text is rendered as plain text (no click events) by the chat renderers of Hatlas (`ChatListener`, `/f
  msg`) and hatlas-hub, and by private messages; only server messages (proxy auth links, renew link)
  carry `ClickEvent.openUrl`. Checked in game with a bot sending a URL.

### 7.6 Secrets, backups, availability
- `.env` files (better-auth secret, ALTCHA HMAC key, SMTP, DB passwords, Stripe keys, Velocity
  forwarding secret) readable by the owner only, never in git; rotating the better-auth secret ends
  every session.
- **Backups now hold personal data** (emails, hashes, 2FA secrets): include schema `web` in
  `hatlas-backup.sh` and **encrypt** the dumps (e.g. `age`, key kept off the machine).
- **Website down = nobody can log in to the game** (D5: every connection is approved on the site).
  Accepted trade-off: the hub says "website unreachable, try again in a few minutes",
  `deploy/update.sh` waits for `/healthz` and rolls back fast. Players already in game are not affected.
- Card data never touches our server (Stripe Checkout).

## 8. Legal pages: CGU, CGV, legal notice (D23, round 6)

> Plan for the content; the final texts should be checked by a lawyer or a recognised template
> service before taking money. Claude is not a legal advisor.

Pages on the site, **fr and en** (French version authoritative), linked in the footer, accepted with a
checkbox at sign-up (CGU) and at checkout (CGV), version + acceptance date stored on the account:

- **Mentions légales / Legal notice** (required in France, LCEN): operator identity (name or company,
  address, SIRET if any, contact), publication director, host (here: self-hosted, the operator).
- **CGU / Terms of use**: the account (one per person, one Minecraft name, created in game), rules of
  conduct and sanctions (ban, account closure), the game is provided as is, availability not
  guaranteed (maintenance, website down blocks game login), the operator may reset or change gameplay,
  ruby and in-game items have **no money value** and cannot be sold or exchanged for money, account
  deletion and its effects, the privacy page for data.
- **CGV / Terms of sale**: **what can be bought** = only **30 days of access** to the faction server,
  **at a price the player chooses, minimum EUR 1**, paid once, **no automatic renewal** (the player
  pays again when they want to keep playing); paying more gives **nothing more in game**; payment by
  Stripe; **right of withdrawal**: an EU consumer has 14 days, which can only
  be lost if they **expressly ask for immediate access and acknowledge losing it** (a mandatory, unticked
  checkbox at checkout, plus a confirmation email); **no refund** after that, nor on a ban for breaking
  the CGU or on account deletion (D20); chargebacks revoke the ticket; legal warranties stay; the
  **consumer mediator** (mandatory for B2C sales in France); applicable law and court.
- **Privacy** (§5) completed with: Pwned Passwords, DB-IP (local), OVH SMTP, Stripe, retention table.

**Seller (D25):** the user, **micro-entrepreneur** (entrepreneur individuel), SIRET
**887 895 878 00015**. Consequences for the pages and invoices:
- name followed by **"EI"** (or "Entrepreneur individuel") on the legal notice, CGV and invoices;
  SIRET and a postal address on the legal notice (a **domiciliation** address avoids publishing the
  home address);
- **Price: chosen by the player, minimum EUR 1, for 30 days of access, paid once, no subscription**
  (✔ user, round 10; replaces round 9's EUR 5 subscription). Under the VAT franchise **no VAT is
  charged**: "TVA non applicable, art. 293 B du CGI". The whole amount is turnover (the part above
  EUR 1 is **not a donation**: a micro-entrepreneur cannot receive donations, and the player buys
  access): it counts for URSSAF and for the VAT thresholds (about EUR 37,500 a year for services; EUR
  10,000 a year of sales to consumers in other EU countries, OSS). Activity **BIC services** (✔ user).
  One accountant check of the thresholds before launch.
- **What changes with Stripe** (round 10):
  - Checkout **`mode=payment`** (one-time) instead of `mode=subscription`: no Stripe Billing fee, no
    customer portal, no renewal webhooks (`invoice.paid`), no failed renewals to handle.
  - **The amount is chosen on our page**, not on Stripe's: our `/renew` page already needs the CGV
    checkbox and the withdrawal-waiver checkbox, so it gets the amount too (preset buttons + a free
    field). The server **validates** it (whole cents, ≥ EUR 1, ≤ a maximum against typos and card
    testing) and creates the Checkout Session with `price_data.unit_amount`. (Stripe's own "customers
    choose what to pay" price, `custom_unit_amount`, also works with `mode=payment`, but would split
    the form across two pages.)
  - Webhook **`checkout.session.completed`** with `payment_status = paid` (and
    `checkout.session.async_payment_succeeded` if slow methods are enabled) → one `web.tickets` row:
    `valid_until = max(now, current valid_until) + 30 days` (paying early **adds** 30 days; contract
    `web.tickets (uuid, valid_until)` unchanged). Refund or dispute → `valid_until = now()` (unchanged).
  - **Stripe Tax stays off** (no VAT to collect; it would add its fee and print VAT lines).
  - Receipts: Stripe's email receipt for every payment; numbered **invoices** for one-time Checkout
    payments are an option (`invoice_creation`) that Stripe bills as Invoicing (small % per invoice,
    check the current price). Whether an invoice is required for each B2C sale of this size, or only
    on request, is **for the accountant**; the micro-entrepreneur's receipts register can be exported
    from Stripe.
- **Money per payment** (standard EEA card: 1.5 % + EUR 0.25; URSSAF BIC services ≈ 21.2 % + 0.1 %
  training contribution; rates to re-check at launch):

  | Player pays | Stripe | URSSAF | **Left** | Lost to fees |
  |---|---|---|---|---|
  | EUR 1 | 0.27 | 0.21 | **≈ EUR 0.52** | 48 % |
  | EUR 2 | 0.28 | 0.43 | **≈ EUR 1.29** | 36 % |
  | EUR 3 | 0.30 | 0.64 | **≈ EUR 2.06** | 31 % |
  | EUR 5 | 0.33 | 1.07 | **≈ EUR 3.60** | 28 % |
  | EUR 10 | 0.40 | 2.13 | **≈ EUR 7.47** | 25 % |

  **Challenge:** the fixed EUR 0.25 makes EUR 1 payments lose a quarter to Stripe alone (non-EEA or
  UK cards cost more: up to ~3.25 % + 0.25). Keep the minimum at EUR 1 if access for everyone matters
  most, but **pre-select a higher suggested amount** (e.g. EUR 5) on the page.
- **Challenge, Mojang's terms:** the round-7 research said paid access is allowed when **every player
  pays the same price** and gets the same gameplay. A chosen price breaks the "same price" wording
  even if gameplay is equal. Lower-risk shape: "Access: EUR 1 for 30 days; pay more if you want to
  support the server, it gives nothing in game" (minimum = the access price, the rest is an optional
  extra, never shown in game: no rank, badge or colour). To check in the official text with the rest
  of §8 before launch.
- a **consumer mediator** must be chosen and paid for, and named in the CGV and on the site (fine up
  to EUR 3,000 without one). ✔ **Chosen: CNPM Médiation Consommation** (user, confirmed round 10); its name, address and website go in the CGV and the legal notice once the membership is
  signed. Comparison (round 8, prices from secondary sources, to confirm on each
  site and on the official CECMC list `economie.gouv.fr/mediation-conso`):

  | Mediator | Membership | Per case | Fit here |
  |---|---|---|---|
  | **CNPM Médiation Consommation** | about EUR 48–60 excl. VAT for 3 years (negotiated rates seen) | about EUR 60 excl. VAT | all sectors incl. online services; cheap; online filing — **recommended** |
  | **CM2C** | one payment for 3 years, scaled on the number of employees (0 here) | per case, scale on their site | all sectors, widely used by micro-entrepreneurs and e-commerce; online filing — good alternative |
  | **AME Conso** | about EUR 150 seen; charges VAT since 2022 | per case | general, more expensive for a one-person business |
  | Médiateur FEVAD | only for FEVAD members (paid membership) | — | not worth it here |
  | Medicys | — | — | **removed from the official list by the CECMC (decision of 15 Feb 2021)**: do not use unless it is listed again |

  Criteria: listed by the CECMC, covers online services sold to consumers, online filing (players
  everywhere), low fixed cost (few cases expected at EUR 5 a ticket), the cost of a case is always paid
  by the seller.
- the EU online dispute resolution (ODR) platform link is no longer required (platform closed in 2025).
- invoices numbered without gaps, if invoices are issued (accountant), numbered without gaps (Stripe invoices can carry these mentions).

**Parked payment and CGV/CGU points** (round 9–10, user: "keep your questions for when we need
them"; to answer at the webapp payment step and before the legal texts are written; the subscription
items of round 9 are gone with the subscription):
1. ✔ **Amounts** (round 11): minimum **EUR 1**, presets **EUR 5 (selected by default), 10, 20**, free
   field. ✔ **Maximum EUR 100** per payment (round 12).
   Why a free price: transparency on the network's costs, `docs/funding.md`.
2. **Duration**: 30 days from payment, **stacked** on remaining time when paying early (planned), or
   calendar months? A cap on how far ahead one can pay (e.g. 90 days)?
3. **Reminder email** a few days before access ends (no auto-renewal, so it helps players come back)?
4. **Withdrawal right**: waiver checkbox before each payment; wording by the template/lawyer.
5. **Ban** (CGU breach): remaining days lost, no refund?
6. **Account deletion**: remaining days lost, no refund (D20, unchanged); nothing to cancel at Stripe.
7. **Legal texts**: a template service or a lawyer for the CGU/CGV/privacy before taking money.
8. Stripe live activation (identity, SIRET, IBAN), Stripe Tax off, **Stripe receipts only, no
   invoices** (✔ user round 11, "I think": one confirmation with the accountant).

**To check before selling anything** (already listed under M2 "Before launch" in `CLAUDE.md`):
- **Minecraft Usage Guidelines (round 7 research, secondary sources):** charging for **access to a
  whole server** is allowed if **every player pays the same price** and all paying players get the
  **same gameplay** (no paid areas, ranks or items); timed access is allowed. Our model fits: one
  ticket, same price, same access to the faction server; the hub is free. One third-party site claims
  fees are limited to running costs — contradicted by the others, **to check in the official text**.
- **Offline mode: kept** (✔ user, round 8: the current players have no premium account). Risk
  accepted knowingly; the stored-UUID design (§3.2) keeps a premium or hybrid switch possible later.
  The analysis that led there:
- **Offline mode is the real risk, not the payment.** "Every player pays" settles the equal-price rule,
  not this: we would sell access to players who may not own Minecraft. Offline mode itself is not
  forbidden (proxies use it), but letting non-premium clients in is commonly reported as against
  Mojang's EULA, and Mojang can blacklist servers. Charging money for it makes the server more visible
  and the risk higher. Options **?**: (a) read the official EULA + guidelines (and ask Mojang if in
  doubt) before launch; (b) premium only (`online-mode = true` on Velocity: no impersonation, no
  `/register` password needed, simpler login); (c) hybrid (premium names verified with Mojang,
  others refused or free-only).
