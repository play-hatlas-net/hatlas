# Dark Forest: style guide

Read by every agent of the boss pipeline (`.claude/skills/boss-building/SKILL.md`). Written at the first
boss of the dungeon (Fungal Witch, 2026-11-20). **Status: proposed, waiting for the user's approval.**

## 1. Ambiance
The dark forest heart of the island (`worldgen/map.md` §3.6): a `dark_forest` along a creek, with a small
`pale_garden` in its middle, the darkest place of the map. Everything here **rots and feeds mushrooms**:
wet bark, moss, pale mycelium threads, caps that glow faintly in the dark. The mood is **eerie and
patient**, not gory: things watch from under their caps and wait. Light comes from the creatures
themselves (glowing spots, amber eyes), never from the sky.

Characters of this dungeon are **fungus that took the shape of something else** (a witch, a brute, a
hound…), never a plain animal or a human in a costume.

## 2. Palette
The only colours allowed in concept sheets, textures and particles tints of this dungeon (the validator
checks it). Names are used by the concept files (`concept/concept.yml`).

| Name | Hex | Use |
|---|---|---|
| `maw_dark` | `#1a1218` | mouth insides, deepest shadow, pupils |
| `night_bark` | `#2b2130` | darkest bark, belts, shadow side of wood |
| `bark` | `#4a3540` | bark and trunk bodies |
| `root` | `#6b4e4a` | roots, staffs, hands, light side of wood |
| `moss_dark` | `#2f4a3a` | cloth, robes, shadowed moss |
| `moss` | `#4f7a4e` | moss, lichen, shawls |
| `cap_deep` | `#3c2452` | mushroom caps: main colour of the dungeon |
| `cap` | `#5e3a7a` | caps, lit side |
| `cap_light` | `#8a5aa8` | cap edges, highlights |
| `stem_shadow` | `#8f8378` | stems and gills in shadow, old bone |
| `gill_pale` | `#cdbfae` | stems, gills, mycelium, faces, bone |
| `spore_glow` | `#b8f2c8` | glowing spots, spores, tethers (emissive) |
| `glow_core` | `#eaffef` | centre of a glow, teeth (emissive) |
| `eye_amber` | `#f2b632` | eyes, lantern light (emissive) |
| `potion_red` | `#b3263a` | potions, tongues, the rare warm accent |
| `resin_orange` | `#c8642a` | resin, shelf fungus of the brutes and the final boss |

Rules:
- **Purple caps, pale glowing spots.** No red amanita with white dots (the cliché, and too close to the
  references).
- At most **two emissive colours** on one character, and `eye_amber` is always the eyes.
- `potion_red` and `resin_orange` are accents: a few pixels, never a main surface.
- Shading is done with the neighbouring palette colour (`bark` → `night_bark`), never with a new colour.

## 3. Silhouette and proportions
- 1 px = 1/16 block. Cubes on the pixel grid, no rotation at rest except caps and tips.
- **The cap is the widest part** of every character and sits on top: a player recognises the dungeon
  by the "T" outline from far away. Each character has its own cap shape (the witch: a pointed, bent
  hat; the Dark Mushroom: a flat lid).
- Thin below, heavy above; limbs are roots (thin, long). Faces are small and pale, eyes glow.
- Readable from 10 blocks: one main mass, at most 3 colour families per character, glow only where the
  player must look (eyes, weapon, weak point).

## 4. Scale
| Kind | Hitbox height | Hitbox width | Cubes | Texture |
|---|---|---|---|---|
| Minion | 0.75–1.25 blocks | 0.75–1.0 | ≤ 40 | ≤ 64×64 |
| Mini-boss | 2.75–3.5 blocks | 1.0–1.75 | ≤ 120 | ≤ 128×128 |
| Final boss | 4.5–6 blocks | 2.5–3.5 | ≤ 250 | ≤ 256×256 |

A mini-boss is clearly taller than a player (1.8) but never fills a path; the final boss dominates its
arena. Caps and weapons may reach outside the hitbox, bodies may not.

## 5. Materials
Wet bark (vertical grain, 2 shades), moss cloth (ragged edges, holes), cap skin (smooth, a lighter rim,
glowing spots of 1–2 px), pale gills (vertical stripes of `gill_pale` / `stem_shadow`), mycelium threads
(1 px `gill_pale` lines), glass (a `potion_red` body with one `glow_core` pixel). No metal, no stone
weapons, no leather: everything grew.

## 6. Particles
Spores `spore_glow` (vanilla `spore_blossom_air`, `falling_spore_blossom`, tinted `dust` or
`entity_effect`), mycelium (`mycelium`), rot (`mushroom`-coloured `dust`), warm accents `eye_amber` only
for the witch's lantern and for "look here" warnings. Ground warnings of this dungeon are **rings of
spores** that thicken until the hit.

## 7. Sound palette
What the dark forest sounds like, for every `boss-sound` prompt of this dungeon:
- **Wet and woody**: creaking trunks, snapping roots, squelching fungus, dripping water. No metal, no
  fire, no clean magic "zap".
- **Breath and spores**: soft puffs, hisses, a dry rattle of spores like seeds in a gourd.
- **Voices**: low, cracked, close to the ear (whispers, chuckles, a wheeze); small creatures chitter and
  click with a wet mouth. No words.
- **Glass and liquid** belong to the witch only (corks, gulps, breaking flasks).
- **Music**: slow, low strings and bowed wood, a music-box or kalimba motif for the fungus, hand drums
  that speed up in later phases; 60–90 s loops, instrumental.
- Wind-up sounds rise in pitch or density until the hit, so the ear alone tells when to move.
