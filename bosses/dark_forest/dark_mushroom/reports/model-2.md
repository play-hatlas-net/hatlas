# Validator report: dark_mushroom, step `model`, iteration 2

- Date: 2026-11-21
- Command: `python bosses/_tools/validate.py dark_forest/dark_mushroom --step model`
- **Verdict: PASS** (54 PASS, 0 FAIL, 2 not yet)

| Group | Check | Result | Numbers |
|---|---|---|---|
| format | boss.yml parses, no key written twice | PASS |  |
| format | kind is minion / mini_boss / boss | PASS | minion |
| format | required keys | PASS | 10 keys |
| format | id = folder name | PASS | dark_mushroom / dark_mushroom |
| format | dungeon = parent folder | PASS | dark_forest / dark_forest |
| format | name has en and fr | PASS | {'en': 'Dark Mushroom', 'fr': 'Champignon noir'} |
| format | no rune (mini-bosses only) | PASS | none |
| format | size: width and height > 0, on the 1/16 grid | PASS | 0.875 x 1.25 blocks |
| format | stats: hp, armor, damage_cap_per_hit | PASS | hp 24, armor 0, damage_cap_per_hit 24 |
| names | animations: a list, each name once | PASS | 6 animations |
| moves | bite: attack timings, shape, damage | PASS | 10 + 3 + 14 = 27 ticks (1.35 s), cooldown 30 |
| moves | bite: tell = pose + wind-up sound + wind-up particles | PASS | attack, mushroom_bite_windup, glow |
| moves | every attack wind-up >= 10 ticks | PASS | shortest 10 |
| mechanics | minion: no music, no phases | PASS |  |
| zones | hit zones and mutations (optional for a minion) | INFO | none |
| names | required animations (spawn, idle, walk, attack, death) | PASS |  |
| names | no animation without a user (move, phase, shield or engine name) | PASS | 6 declared, 1 named by moves/phases |
| names | every sound name is written once | PASS | 6 sounds |
| names | base sounds (hurt, death, one per phase entry) | PASS |  |
| names | no sound shares a name with an animation | PASS |  |
| concept | concept sheet files | PASS | front.png, side.png, back.png, palette.png |
| concept | style.md palette (8-16 colours) | PASS | 15 colours |
| concept | pixel art uses the palette only | PASS | 0 colours outside style.md |
| concept | cubes <= budget (40) | PASS | 34 cubes, 83 painted details |
| concept | extra bones: each declared once, none is a fixed name | PASS | 6 extras |
| concept | every bone drawn is a fixed name or declared in boss.yml > bones | PASS | 8 bones drawn |
| concept | every declared extra bone is drawn | PASS |  |
| concept | body and head are drawn | PASS |  |
| concept | trunk and legs stay inside the hitbox width | PASS | reach 7 px, half hitbox 7 px |
| concept | hitbox height between 75 % and 100 % of the drawn height | PASS | hitbox 20 px, drawn 21 px (1.3125 blocks), widest reach 9 px |
| model | dark_mushroom.bbmodel exists | PASS | dark_mushroom.bbmodel |
| model | Blockbench format pinned (4.10, generic model, per-face UV) | PASS | format_version 4.10, model_format free, box_uv False |
| model | hash file: who wrote the model last | INFO | the script (sha256 matches) |
| model | one bone tree under `root`, every bone named once, no cube outside a bone | PASS | top: root; twice: none; loose cubes: 0 |
| model | every bone is a fixed name or declared in boss.yml > bones | PASS | 9 bones + hitbox + 0 hit-zone boxes |
| model | root, body, head, every declared bone and every concept bone exist | PASS |  |
| model | no bone name is read as a BetterModel tag (h_, b_, p_, glow ...) | PASS |  |
| model | every bone except root has cubes | PASS |  |
| model | cubes <= budget (40) | PASS | 34 cubes (hitbox and hit-zone boxes not counted); concept: 34 |
| model | cubes on the 1/16 grid, three sizes > 0 | PASS |  |
| model | no cube or bone rotated at rest | PASS |  |
| model | no inflated cube | PASS |  |
| model | every pivot lies on its bone (inside the box of its cubes, 1 px margin) | PASS |  |
| model | root pivot at the origin | PASS |  |
| model | one texture | PASS | 1 |
| model | texture size <= 64 x 64, = project resolution | PASS | 64 x 64, resolution 64 x 64 |
| model | texture uses the palette only | PASS | 14 palette colours, 0 outside style.md |
| model | texture pixels are opaque or empty (no half transparency) | PASS | 0 half-transparent px |
| model | every textured face has a UV rectangle inside the texture, on painted pixels | PASS | 189 textured faces |
| model | emissive cubes: `light_emission` 15 and a name with `glow` go together | PASS | 7 emissive cubes |
| model | `hitbox` bone under root with one cube | PASS |  |
| model | hitbox cube = boss.yml > size, centred, on the ground | PASS | 14 x 20 x 14 px (size 0.875 x 1.25 blocks) |
| model | hitbox cube is not drawn (no textured face) | PASS |  |
| model | only the bones shown by a mutation are hidden at rest (visibility off) | PASS | hidden: none |
| model | no animation yet (step 3 writes them) | PASS | 0 animations |
| model | outline = concept in the front, side and back views (except on cubes added in model.yml) | PASS | differs by: front 0 px, side 0 px, back 0 px |
| model | pixels of the same colour as the concept views | INFO | 648 of 699 (93 %); the rest is texture detail added at step 2 |
| animation | animations in the model (one per spec name, length = windup + active + recovery) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| sound | sounds/*.ogg (one per spec name, mono/stereo, loudness, LICENSES.md) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
