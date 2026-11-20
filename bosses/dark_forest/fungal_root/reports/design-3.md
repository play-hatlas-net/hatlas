# Validator report: fungal_root, step `design`, iteration 3

- Date: 2026-11-20
- Command: `python bosses/_tools/validate.py bosses/dark_forest/fungal_root --step design`
- **Verdict: PASS** (66 PASS, 0 FAIL, 3 not yet)

| Group | Check | Result | Numbers |
|---|---|---|---|
| format | boss.yml parses, no key written twice | PASS |  |
| format | kind is minion / mini_boss / boss | PASS | mini_boss |
| format | required keys | PASS | 15 keys |
| format | id = folder name | PASS | fungal_root / fungal_root |
| format | dungeon = parent folder | PASS | dark_forest / dark_forest |
| format | name has en and fr | PASS | {'en': 'Fungal Root', 'fr': 'Racine fongique'} |
| format | rune is one of fire/frost/storm/nature | PASS | nature |
| format | size: width and height > 0, on the 1/16 grid | PASS | 1.75 x 4.0 blocks |
| format | stats: hp, armor, damage_cap_per_hit, enrage_seconds | PASS | hp 600, armor 6, damage_cap_per_hit 12, enrage_seconds 300 |
| names | animations: a list, each name once | PASS | 16 animations |
| moves | maw_lash: attack timings, shape, damage | PASS | 14 + 4 + 20 = 38 ticks (1.9 s), cooldown 40 |
| moves | maw_lash: tell = pose + wind-up sound + wind-up particles | PASS | attack_lash, root_lash_windup, crit |
| moves | spore_cloud: attack timings, shape, damage | PASS | 20 + 2 + 16 = 38 ticks (1.9 s), cooldown 70 |
| moves | spore_cloud: zone has duration, damage, every_ticks, max_alive | PASS | {'duration_ticks': 100, 'damage': 2, 'every_ticks': 20, 'max_alive': 3} |
| moves | spore_cloud: tell = pose + wind-up sound + wind-up particles | PASS | cast_cloud, root_cloud_windup, glow |
| moves | spore_rain: attack timings, shape, damage | PASS | 26 + 4 + 30 = 60 ticks (3 s), cooldown 160 |
| moves | spore_rain: zone has duration, damage, every_ticks, max_alive | PASS | {'duration_ticks': 80, 'damage': 2, 'every_ticks': 20, 'max_alive': 5} |
| moves | spore_rain: tell = pose + wind-up sound + wind-up particles | PASS | cast_rain, root_rain_windup, glow |
| moves | tree_step: attack timings, shape, damage | PASS | 16 + 4 + 24 = 44 ticks (2.2 s), cooldown 120 |
| moves | tree_step: tell = pose + wind-up sound + wind-up particles | PASS | tree_step, root_step_sink, mycelium |
| moves | call_brood: tell = pose + wind-up sound + wind-up particles | PASS | summon, root_summon_cry, mycelium |
| moves | brew_mend: tell = pose + wind-up sound + wind-up particles | PASS | drink_sap, root_bulb_swell, falling_obsidian_tear |
| moves | every attack wind-up >= 10 ticks | PASS | shortest 14 |
| moves | a punish window: one recovery >= 20 ticks | PASS | longest 30 |
| phases | at least 2 phases, ids unique | PASS | p1, p2, p3 |
| phases | ordered by hp_below, first = 1.0 | PASS | 1.0 > 0.7 > 0.4 |
| phases | p1: moves exist | PASS | maw_lash, spore_cloud, tree_step |
| phases | p2: moves exist | PASS | maw_lash, spore_cloud, tree_step, call_brood, brew_mend |
| phases | p2: entry animation + enter_ticks | PASS | phase2_enter, 40 ticks |
| phases | p2: changes the move set or the rhythm | PASS | speed 1 |
| phases | p3: moves exist | PASS | maw_lash, spore_cloud, spore_rain, tree_step |
| phases | p3: entry animation + enter_ticks | PASS | phase3_enter, 40 ticks |
| phases | p3: changes the move set or the rhythm | PASS | speed 1.25 |
| mechanics | p3 wave: max_alive, every_ticks, until | PASS | max_alive 5, every 300, until boss_death |
| mechanics | p3 wave: one spawn fits in max_alive | PASS | 3 per spawn |
| mechanics | p3 wave: 'dark_mushroom' has its own kind: minion spec | PASS | dark_mushroom/boss.yml kind minion |
| mechanics | p3 wave: 'cave_spider' is vanilla or has a minion spec | PASS | vanilla |
| phases | every move is used by a phase | PASS | 6 moves |
| mechanics | call_brood: 'dark_mushroom' has its own kind: minion spec | PASS | dark_mushroom/boss.yml kind minion |
| mechanics | call_brood: count base/per_extra_player/max, max <= 8 | PASS | 3 + 1 per player above 2, max 8 (2 players: 3, 8 players: 8) |
| mechanics | call_brood: uses_per_phase set | PASS | 1 |
| mechanics | call_brood: protect has a shield animation, tethers and an immune sound | PASS | spore_shield, glow, root_shield_hit |
| mechanics | call_brood: keeps attacking while shielded (moves exist) | PASS | spore_cloud, tree_step |
| mechanics | brew_mend: interrupt damage, per_extra_player, stagger_ticks | PASS | 8 % + 2 % per player above 2 (8 players: 20 %), stagger 60 ticks |
| mechanics | brew_mend: cap = phase | PASS | phase |
| mechanics | brew_mend: channel_ticks, heal_per_second, uses_per_phase | PASS | 160 ticks x 0.02 = 16 % of max HP per channel, 2 per phase |
| mechanics | brew_mend: loop and interrupt sounds | PASS | root_gulping, root_bulb_burst |
| mechanics | brew_mend: goto_phase names a later phase | PASS | p3 (used in p2) |
| mechanics | music within the budget (mini_boss: 1 track) | PASS | fungal_root_music |
| reactions | each reaction: when + do (a move or a built-in), known phase | PASS | 6 reactions |
| reactions | reacts to distance, healers and groups (§4.2) | PASS | healed_nearby, hits_taken, hp_lost_in_phase, phase_entered, players_far, players_grouped |
| names | required animations (spawn, walk, hit, death) | PASS |  |
| names | no animation without a user (move, phase, shield or engine name) | PASS | 16 declared, 12 named by moves/phases |
| names | every sound name is written once | PASS | 23 sounds |
| names | base sounds (spawn, hurt, death, enrage, one per phase entry) | PASS |  |
| names | no sound shares a name with an animation | PASS |  |
| concept | concept sheet files | PASS | front.png, side.png, back.png, palette.png |
| concept | style.md palette (8-16 colours) | PASS | 15 colours |
| concept | pixel art uses the palette only | PASS | 0 colours outside style.md |
| concept | cubes <= budget (120) | PASS | 98 cubes, 227 painted details |
| concept | extra bones: each declared once, none is a fixed name | PASS | 28 extras |
| concept | every bone drawn is a fixed name or declared in boss.yml > bones | PASS | 30 bones drawn |
| concept | every declared extra bone is drawn | PASS |  |
| concept | body and head are drawn | PASS |  |
| concept | trunk and legs stay inside the hitbox width | PASS | reach 14 px, half hitbox 14 px |
| concept | hitbox height between 75 % and 100 % of the drawn height | PASS | hitbox 64 px, drawn 70 px (4.375 blocks), widest reach 27 px |
| model | <boss>.bbmodel (bones, cube budget, grid, texture, palette, hitbox) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| animation | animations in the model (one per spec name, length = windup + active + recovery) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| sound | sounds/*.ogg (one per spec name, mono/stereo, loudness, LICENSES.md) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
