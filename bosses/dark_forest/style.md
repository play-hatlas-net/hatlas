# Dark Forest: style guide

Read by every agent of the boss pipeline (`.claude/skills/boss-building/SKILL.md`). Written at the first
boss of the dungeon (Fungal Root, 2026-11-20); **iteration 5** after the user's remarks (no humanoid part
at all, bioluminescent blue palette, final boss 5–7 blocks, jaws in the limbs, taller characters). **Status: proposed, waiting for the user's
approval.**

## 1. Ambiance
The dark forest heart of the island (`worldgen/map.md` §3.6): a `dark_forest` along a creek, with a small
`pale_garden` in its middle, the darkest place of the map. Under the canopy it is as dark as a cave, and
everything **rots and feeds mushrooms**: wet bark, roots, mycelium threads. The only light is
**bioluminescence**: caps, gills and dripping tendrils that glow **cyan**, with a softer **lavender**
glow as the second light. The mood is **eerie and patient**, not gory: things watch from the dark and
wait. Light comes from the creatures themselves, never from the sky.

Characters of this dungeon are **fungal creatures with no humanoid part at all** (✔ user, 2026-11-20,
iterations 2 and 3): mushrooms and roots that pulled themselves out of the ground and walk. **No human
head, face, hat, clothes, hands, arms or legs, and no upright two-legged stance.** Only tree roots,
mushroom parts, bark, fungus and other natural shapes. A name is what the forest calls the creature,
said by its outline and its behaviour, not by a costume.

## 2. Palette
The only colours allowed in concept sheets, textures and particle tints of this dungeon (the validator
checks it). Names are used by the concept files (`concept/concept.yml`). **Iteration 3 (user): glowing
mushrooms in a dark cave**: navy-black shadows and bark, bright cyan light, lavender as the second light.
15 colours; one slot is left free for the later bosses of the dungeon.

| Name | Hex | Use |
|---|---|---|
| `void_dark` | `#05070f` | mouth insides, eye sockets, pupils, deepest shadow |
| `night_bark` | `#0c1424` | darkest bark, root masses, shadow side of wood |
| `bark` | `#17243d` | bark and trunk bodies, root limbs |
| `root` | `#2c4166` | knots (joints), feet, root tips, the lit side of wood |
| `lichen` | `#1d6b6b` | lichen and moss patches (rare, never cloth) |
| `cap_deep` | `#121d4a` | mushroom caps: main colour of the dungeon |
| `cap` | `#20337a` | caps, lit side |
| `cap_light` | `#3d5cc0` | cap rims and highlights (the outline that reads in the dark) |
| `stem_shadow` | `#45587e` | stems in shadow |
| `stem_pale` | `#a9bedb` | stems, jaws, young sprouts |
| `cyan_deep` | `#178ea6` | dim cyan: gills, tendril strands, mycelium veins, the falloff of a glow |
| `cyan_glow` | `#38e8f5` | bright cyan: spots, gill stripes, tendril tips, eyes, spore pods (emissive) |
| `glow_core` | `#e6fcff` | centre of a glow, teeth (emissive) |
| `lilac_deep` | `#7458c2` | dim lavender: gums, sap sacs and sap veins, the falloff of a lavender glow |
| `lilac_glow` | `#c9a8ff` | bright lavender: the second light: sap, some cap spots (emissive) |

Rules:
- **Dark blue caps with cyan and lavender glowing spots; undersides (gills) and tendrils glow cyan.** No
  red, no amber, no green glow, no red amanita with white dots.
- **Two glows, two meanings.** Cyan is the forest's own light and its danger: **eyes are always cyan**,
  and so are spores, pods, tethers and ground warnings. Lavender is **sap**: what a creature drinks or
  stores to mend itself, so a lavender light that swells means "it is healing, hit it now". Cap spots
  may mix both. No third emissive colour on a character.
- Bodies are nearly black on purpose. A character must still read in the dark **by its lights and its
  rims**: a `cap_light` rim on every cap, `root` on knots and feet, a `cyan_deep` vein along long limbs,
  and glow where the player must look (eyes, weapon, weak point).
- Shading is done with the neighbouring palette colour (`bark` → `night_bark`), never with a new colour.
- **Hit zones follow the lights** (plan §4.6): a weak point is always one of the glowing things (cyan eyes,
  a lavender sap sac); armoured parts are the dark, hard ones (`root` knots, shins, feet). What a
  mutation tears off leaves a splintered `stem_pale` stump bleeding `lilac_deep` sap.
- **Zone readability** (skill step 1, ✔ user 2026-11-21): weak-point lights = `cyan_glow` and
  `lilac_glow` patches of 2 × 2 px or more, with a `glow_core` heart and a `void_dark` socket. Elsewhere
  these colours appear only as 1 px dots; gill stripes, veins and tendrils use `cyan_deep` with a rare
  bright pixel. Armour = `bark`/`night_bark`/`root`, no bright glow. A breakable part shows a `stem_pale`
  seam at its joint. Hit feedback: weak = burst of the zone's glow colour + wet pop; armour = `root`
  splinters (`dust`/`block` particles) + dull wooden thunk.

## 3. Silhouette and proportions
- 1 px = 1/16 block. Cubes on the pixel grid, no rotation at rest except caps and tips.
- **The cap is the widest part** of every character and sits on top: a player recognises the dungeon
  by the "T" outline from far away. Caps are **stepped domes** (3–4 steps, octagonal footprint), never one
  flat box. Each character has its own cap: the Fungal Root a wide dome that hangs forward, with dripping
  tendrils; the Dark Mushroom a small round dome with its eyes on it.
- **Never a person's outline** (✔ user, iteration 3). No character stands upright on two straight legs
  with two arms. Use at least one of: **four or more root legs** (stilts with the knee knot above the
  hip, like a walking root mass), **legs bent backwards** like an animal's, a body that **leans forward
  under the weight of its cap**. Limbs that attack are **roots and tendrils**, growing from the root
  mass, never from "shoulders" and **never one on each side of the trunk** (✔ user, iteration 4: put
  them on the same side); they end in **jaws**, never in a hand.
- **Jaws are freaky and disgusting** (✔ user, iteration 4): bark split and peeled back to the pale
  wood, `lilac_deep` gums, too many `glow_core` teeth and no two of the same length, boils and shelf
  fungi growing on the limb, strands of `cyan_deep` drool with a `cyan_glow` drop at the end. A mouth is
  always black inside (`void_dark`) so the teeth read; never a white block of teeth.
- **Nothing is held.** A weapon or tool is a part of the body that grew there (a jaw, a pod in a
  throat, a sac).
- No face. **Eyes are static**: glowing knot-holes in the trunk (or bulbs on the cap for small
  creatures); they are painted, they do not move, blink or look around. Mouths are toothed maws with
  `glow_core` teeth, pointed for aggressive creatures.
- Mass is in the cap, never in the trunk; legs and limbs are thin, with knots at the joints.
- Slightly asymmetric (one eye bigger, a different limb on each side, shelf fungi on one side) so
  nothing looks built.
- Readable from 10 blocks: one main mass, at most 3 colour families per character.

## 4. Scale
| Kind | Height | Hitbox width | Cubes | Texture |
|---|---|---|---|---|
| Minion | hitbox 0.75–1.25 blocks (up to 1.35 drawn) | 0.75–1.0 | ≤ 40 | ≤ 64×64 |
| Mini-boss | 4–5 blocks drawn, never more (hitbox 3.5–4.5) | 1.0–1.75 | ≤ 120 | ≤ 128×128 |
| Final boss | **6–7 blocks tall** (✔ user, iteration 4; was 5–7) | 2.5–3.5 | ≤ 250 | ≤ 256×256 |

A mini-boss **towers over a player** (1.8) but always stays **smaller than the final boss of its
dungeon**, which is 6–7 blocks tall (✔ user, 2026-11-20) and the only thick character. The Fungal Root is at the top of the
mini-boss band (5.0 drawn, hitbox 1.75 × 4.5, ✔ user, iteration 4), so the final boss of every dungeon
is drawn at **6 blocks or more, up to 7** (✔ user). The Dark Mushroom is 1.3 drawn, hitbox 0.875 × 1.25. **Free height is not a constraint**:
the combat areas of a dungeon have more than 50 blocks of free height (✔ user), so no boss needs a
clearance value. A walker on four stilt legs needs a wider hitbox than a biped (up to 1.75 blocks); its
legs are thin, so it still does not look thick. Caps, attacking roots, tendrils and sprouts may reach
outside the hitbox; the trunk and the legs may not (the validator checks it).

## 5. Materials
Wet bark (vertical grain, 2 shades), roots (knots lighter than the limb), lichen patches (never cloth),
cap skin (smooth, a lighter rim, glowing spots of 1–2 px), glowing gills (stripes of `cyan_deep` /
`cyan_glow`), mycelium veins (1 px `cyan_deep` lines), pale stems, sap sacs (a `lilac_deep` body with a
`lilac_glow` heart and one `glow_core` pixel). No metal, no glass, no stone weapons, no leather, no
cloth: everything grew. Emissive parts (the three `*_glow` colours and `glow_core`) are meant to be
full-bright in game; the dim `*_deep` colours are not.

## 6. Particles
Cyan for spores and danger: vanilla `glow`, `warped_spore`, `glow_squid_ink`, `sculk_soul`, or `dust`
tinted `cyan_glow`. Lavender for sap and healing: `falling_obsidian_tear`, `reverse_portal`,
`dragon_breath`, or `dust` tinted `lilac_glow`. Soil and roots: `mycelium`, `dust_plume`. No red, orange
or green particles. Ground warnings of this dungeon are **rings of cyan spores** that thicken until the
hit.

## 7. Sound palette
What the dark forest sounds like, for every `boss-sound` prompt of this dungeon:
- **Wet and woody**: creaking trunks, snapping roots, squelching fungus, dripping water. No metal, no
  fire, no clean magic "zap".
- **Breath and spores**: soft puffs, hisses, a dry rattle of spores like seeds in a gourd.
- **Glow**: light has a sound here, a faint wet shimmer or a low hum that swells with the light; never
  a bright chime.
- **Voices**: never human. Low creaks and groans of wood, a wheeze through gills, wet clicks of jaws;
  small creatures chitter, hiss and snap with a wet mouth. No words, no laughter.
- **Sap** belongs to the Fungal Root only (thick gulps drawn through a root, a sac that bursts). No glass.
- **Music**: slow, low strings and bowed wood, a music-box or kalimba motif for the fungus, hand drums
  that speed up in later phases; 60–90 s loops, instrumental.
- Wind-up sounds rise in pitch or density until the hit, so the ear alone tells when to move.
