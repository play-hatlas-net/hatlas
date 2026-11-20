# Dark Forest: style guide

Read by every agent of the boss pipeline (`.claude/skills/boss-building/SKILL.md`). Written at the first
boss of the dungeon (Fungal Witch, 2026-11-20); **iteration 2** after the user's remarks (non-humanoid
fungal creatures). **Status: proposed, waiting for the user's approval.**

## 1. Ambiance
The dark forest heart of the island (`worldgen/map.md` §3.6): a `dark_forest` along a creek, with a small
`pale_garden` in its middle, the darkest place of the map. Everything here **rots and feeds mushrooms**:
wet bark, moss, pale mycelium threads, caps that glow faintly in the dark. The mood is **eerie and
patient**, not gory: things watch from under their caps and wait. Light comes from the creatures
themselves (glowing spots, amber eyes), never from the sky.

Characters of this dungeon are **fungal creatures, never humanoid** (✔ user, 2026-11-20): mushrooms and
roots that stood up and walk. **No human head or face, no hat, no clothes, no hands.** The cap is the
head; eyes are slits or bulbs that glow in the stalk or on the cap; mouths are maws (under a cap, or at
the end of a limb). A name like "witch" or "brute" is what the forest calls the creature, said by its
outline and its behaviour, not by a costume.

## 2. Palette
The only colours allowed in concept sheets, textures and particles tints of this dungeon (the validator
checks it). Names are used by the concept files (`concept/concept.yml`).

| Name | Hex | Use |
|---|---|---|
| `maw_dark` | `#1a1218` | mouth insides, deepest shadow, pupils |
| `night_bark` | `#2b2130` | darkest bark, belts, shadow side of wood |
| `bark` | `#4a3540` | bark and trunk bodies |
| `root` | `#6b4e4a` | roots, root staffs, knots (knees, elbows), light side of wood |
| `moss_dark` | `#2f4a3a` | shadowed moss |
| `moss` | `#4f7a4e` | moss and lichen patches |
| `cap_deep` | `#3c2452` | mushroom caps: main colour of the dungeon |
| `cap` | `#5e3a7a` | caps, lit side |
| `cap_light` | `#8a5aa8` | cap edges, highlights |
| `stem_shadow` | `#8f8378` | stems and gills in shadow, old bone |
| `gill_pale` | `#cdbfae` | stems, gills, mycelium veins, jaws |
| `spore_glow` | `#b8f2c8` | glowing spots, spores, tethers (emissive) |
| `glow_core` | `#eaffef` | centre of a glow, teeth (emissive) |
| `eye_amber` | `#f2b632` | eyes only (emissive) |
| `potion_red` | `#b3263a` | red sap (the witch's bulb), tongues, the rare warm accent |
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
  by the "T" outline from far away. Caps are **stepped domes** (3–4 steps, octagonal footprint), never one
  flat box. Each character has its own cap: the witch a wide dome with dripping tendrils and a pointed
  young mushroom on top; the Dark Mushroom a small round dome with its eyes on it.
- **Tall and thin, not thick**: a narrow stalk, long root limbs with knots at the joints. Mass is in the
  cap, never in the trunk.
- No face: eyes glow in the bark or on the cap, mouths are toothed maws with `glow_core` teeth.
- Slightly asymmetric (one eye bigger, shelf fungi on one side) so nothing looks built.
- Readable from 10 blocks: one main mass, at most 3 colour families per character, glow only where the
  player must look (eyes, weapon, weak point).

## 4. Scale
| Kind | Hitbox height | Hitbox width | Cubes | Texture |
|---|---|---|---|---|
| Minion | 0.75–1.25 blocks | 0.75–1.0 | ≤ 40 | ≤ 64×64 |
| Mini-boss | 3.5–4.5 blocks (4–5 drawn) | 1.0–1.5 | ≤ 120 | ≤ 128×128 |
| Final boss | 5.5–7 blocks | 2.5–3.5 | ≤ 250 | ≤ 256×256 |

A mini-boss **towers over a player** (1.8): 4–5 blocks drawn (✔ user: large but not thick), on a narrow
hitbox so it never fills a path; its fight zone needs 5.5 blocks of free height. The final boss dominates
its arena and is the only thick character. Caps, arms, tendrils and staffs may reach outside the hitbox;
the trunk and the legs may not (the validator checks it).

## 5. Materials
Wet bark (vertical grain, 2 shades), moss patches (never cloth), cap skin (smooth, a lighter rim,
glowing spots of 1–2 px), pale gills (vertical stripes of `gill_pale` / `stem_shadow`), mycelium threads
(1 px `gill_pale` lines), sap sacs (a `potion_red` body with one `glow_core` pixel). No metal, no glass,
no stone weapons, no leather, no cloth: everything grew.

## 6. Particles
Spores `spore_glow` (vanilla `spore_blossom_air`, `falling_spore_blossom`, tinted `dust` or
`entity_effect`), mycelium (`mycelium`), rot (`mushroom`-coloured `dust`), warm accents `eye_amber` only
for "look here" warnings. Ground warnings of this dungeon are **rings of
spores** that thicken until the hit.

## 7. Sound palette
What the dark forest sounds like, for every `boss-sound` prompt of this dungeon:
- **Wet and woody**: creaking trunks, snapping roots, squelching fungus, dripping water. No metal, no
  fire, no clean magic "zap".
- **Breath and spores**: soft puffs, hisses, a dry rattle of spores like seeds in a gourd.
- **Voices**: never human. Low creaks and groans of wood, a wheeze through gills, wet clicks of jaws;
  small creatures chitter and click with a wet mouth. No words, no laughter.
- **Sap** belongs to the witch only (a wet bite, thick gulps, a sac that bursts). No glass.
- **Music**: slow, low strings and bowed wood, a music-box or kalimba motif for the fungus, hand drums
  that speed up in later phases; 60–90 s loops, instrumental.
- Wind-up sounds rise in pitch or density until the hit, so the ear alone tells when to move.
