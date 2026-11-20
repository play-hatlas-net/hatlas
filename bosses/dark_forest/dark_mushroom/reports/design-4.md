# Validator report: dark_mushroom, step `design`, iteration 4

- Date: 2026-11-20
- Command: `python bosses/_tools/validate.py bosses/dark_forest/dark_mushroom --step design`
- **Verdict: PASS** (29 PASS, 0 FAIL, 3 not yet)

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
| model | <boss>.bbmodel (bones, cube budget, grid, texture, palette, hitbox) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| animation | animations in the model (one per spec name, length = windup + active + recovery) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| sound | sounds/*.ogg (one per spec name, mono/stereo, loudness, LICENSES.md) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
