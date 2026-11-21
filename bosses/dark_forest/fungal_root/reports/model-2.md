# Validator report: fungal_root, step `model`, iteration 2

- Date: 2026-11-21
- Command: `python bosses/_tools/validate.py dark_forest/fungal_root --step model`
- **Verdict: PASS** (127 PASS, 0 FAIL, 2 not yet)

| Group | Check | Result | Numbers |
|---|---|---|---|
| format | boss.yml parses, no key written twice | PASS |  |
| format | kind is minion / mini_boss / boss | PASS | mini_boss |
| format | required keys | PASS | 16 keys |
| format | id = folder name | PASS | fungal_root / fungal_root |
| format | dungeon = parent folder | PASS | dark_forest / dark_forest |
| format | name has en and fr | PASS | {'en': 'Fungal Root', 'fr': 'Racine fongique'} |
| format | rune is one of fire/frost/storm/nature | PASS | nature |
| format | size: width and height > 0, on the 1/16 grid | PASS | 1.75 x 4.5 blocks |
| format | stats: hp, armor, damage_cap_per_hit, enrage_seconds | PASS | hp 600, armor 6, damage_cap_per_hit 12, enrage_seconds 300 |
| names | animations: a list, each name once | PASS | 18 animations |
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
| mechanics | call_brood: protect_timeout_ticks set, at most 2400 | PASS | 1200 ticks (60 s) |
| mechanics | call_brood: keeps attacking while shielded (moves exist) | PASS | spore_cloud, tree_step |
| mechanics | brew_mend: interrupt damage, per_extra_player, stagger_ticks | PASS | 8 % + 2 % per player above 2 (8 players: 20 %), stagger 60 ticks |
| mechanics | brew_mend: cap = phase | PASS | phase |
| mechanics | brew_mend: channel_ticks, heal_per_second, uses_per_phase | PASS | 160 ticks x 0.02 = 16 % of max HP per channel, 2 per phase |
| mechanics | brew_mend: loop and interrupt sounds | PASS | root_gulping, root_bulb_burst |
| mechanics | brew_mend: goto_phase names a later phase | PASS | p3 (used in p2) |
| mechanics | mandatory mob phase: a side wave or a protector summon | PASS | waves in p3; protectors: call_brood |
| mechanics | mandatory mutation: hp_below <= 0.4, in one of the last two phases, changes body and fight | PASS | torn_spit_root at 0.1 (in p3) |
| mechanics | music within the budget (mini_boss: 1 track) | PASS | fungal_root_music |
| reactions | each reaction: when + do (a move or a built-in), known phase | PASS | 6 reactions |
| reactions | reacts to distance, healers and groups (§4.2) | PASS | healed_nearby, hits_taken, hp_lost_in_phase, phase_entered, players_far, players_grouped |
| zones | default multiplier within 0.5-2.0 | PASS | 1.0 |
| zones | eyes: every bone exists in concept.yml | PASS | eyes |
| zones | eyes: multiplier within 0.5-2.0 | PASS | x1.75 |
| zones | eyes: weak point says how it is reached (ranged and/or melee moments = animations) | PASS | ranged always, melee during stagger, cast_rain, drink_sap |
| zones | sap_bulb: every bone exists in concept.yml | PASS | bulb |
| zones | sap_bulb: multiplier within 0.5-2.0 | PASS | x1.5 |
| zones | sap_bulb: weak point says how it is reached (ranged and/or melee moments = animations) | PASS | ranged always, melee during drink_sap, stagger, cast_rain |
| zones | sap_bulb: heal_interrupt within 0.5-2.0, and the boss has a heal move | PASS | x2.0 |
| zones | legs: every bone exists in concept.yml | PASS | foot_bl, foot_br, foot_fl, foot_fr, shin_bl, shin_br, shin_fl, shin_fr |
| zones | legs: multiplier within 0.5-2.0 | PASS | x0.5 |
| zones | spit_root: every bone exists in concept.yml | PASS | spit_jaw_l, spit_jaw_r, spit_pod, spit_root |
| zones | spit_root: multiplier within 0.5-2.0 | PASS | x1.0 |
| zones | spit_root: break_hp > 0 and below the boss's HP | PASS | 90 (2 players = 15 % of max HP), 180 at 8 players |
| zones | spit_root: break_hp is used by a mutation (zone_broken) or has a reward | PASS | mutation, reward {'loot_rolls': 1, 'to': 'breaker_party', 'only_before_hp': 0.1} |
| zones | at least one weak point (> 1) and one armoured part (< 1) | PASS | weak: eyes, sap_bulb; armoured: legs |
| mutations | torn_spit_root: when.any = hp_below (0-1) and/or zone_broken (a zone with break_hp) | PASS | hp_below 0.1; zone_broken spit_root |
| mutations | torn_spit_root: every hide/show bone exists in concept.yml | PASS | hide 4, show 1 |
| mutations | torn_spit_root: no bone both hidden and shown; body, head and root stay | PASS |  |
| mutations | torn_spit_root: transition animation + transition_ticks, animation_set names exist | PASS | spit_root_torn (40 ticks); walk -> run_wild |
| mutations | torn_spit_root: remove_moves / add_moves / substitute name existing moves | PASS | remove spore_cloud; substitute spore_cloud -> spore_rain |
| mutations | torn_spit_root: every phase still has a move afterwards | PASS | p1: maw_lash, spore_rain, tree_step; p2: maw_lash, spore_rain, tree_step, call_brood, brew_mend; p3: maw_lash, spore_rain, tree_step |
| mutations | torn_spit_root: no reaction or shield left with only a removed move | PASS |  |
| mutations | torn_spit_root: speed between 0.5 and 2 | PASS | 1.3 |
| mutations | torn_spit_root: has a start sound | PASS | root_tear |
| names | required animations (spawn, walk, hit, death) | PASS |  |
| names | no animation without a user (move, phase, shield or engine name) | PASS | 18 declared, 14 named by moves/phases |
| names | every sound name is written once | PASS | 29 sounds |
| names | base sounds (spawn, hurt, death, enrage, one per phase entry) | PASS |  |
| names | no sound shares a name with an animation | PASS |  |
| concept | concept sheet files | PASS | front.png, side.png, back.png, palette.png |
| concept | style.md palette (8-16 colours) | PASS | 15 colours |
| concept | pixel art uses the palette only | PASS | 0 colours outside style.md |
| concept | zone overlay and mutated views are drawn | PASS | zones.png, mutation_torn_spit_root.png |
| concept | bones hidden until a mutation are drawn (counted in the cube budget) | INFO | spit_stump: 3 cubes |
| concept | cubes <= budget (120) | PASS | 117 cubes, 277 painted details |
| concept | extra bones: each declared once, none is a fixed name | PASS | 32 extras |
| concept | every bone drawn is a fixed name or declared in boss.yml > bones | PASS | 34 bones drawn |
| concept | every declared extra bone is drawn | PASS |  |
| concept | body and head are drawn | PASS |  |
| concept | trunk and legs stay inside the hitbox width | PASS | reach 14 px, half hitbox 14 px |
| concept | hitbox height between 75 % and 100 % of the drawn height | PASS | hitbox 72 px, drawn 80 px (5 blocks), widest reach 29 px |
| model | fungal_root.bbmodel exists | PASS | fungal_root.bbmodel |
| model | Blockbench format pinned (4.10, generic model, per-face UV) | PASS | format_version 4.10, model_format free, box_uv False |
| model | hash file: who wrote the model last | INFO | the script (sha256 matches) |
| model | one bone tree under `root`, every bone named once, no cube outside a bone | PASS | top: root; twice: none; loose cubes: 0 |
| model | every bone is a fixed name or declared in boss.yml > bones | PASS | 35 bones + hitbox + 14 hit-zone boxes |
| model | root, body, head, every declared bone and every concept bone exist | PASS |  |
| model | no bone name is read as a BetterModel tag (h_, b_, p_, glow ...) | PASS |  |
| model | every bone except root has cubes | PASS |  |
| model | cubes <= budget (120) | PASS | 120 cubes (hitbox and hit-zone boxes not counted); concept: 117 |
| model | cube count differs from the concept | INFO | +3 (cubes added or removed at step 2: named in the report of the step) |
| model | cubes on the 1/16 grid, three sizes > 0 | PASS |  |
| model | no cube or bone rotated at rest | PASS |  |
| model | no inflated cube | PASS |  |
| model | every pivot lies on its bone (inside the box of its cubes, 1 px margin) | PASS |  |
| model | root pivot at the origin | PASS |  |
| model | one texture | PASS | 1 |
| model | texture size <= 128 x 128, = project resolution | PASS | 128 x 128, resolution 128 x 128 |
| model | texture uses the palette only | PASS | 15 palette colours, 0 outside style.md |
| model | texture pixels are opaque or empty (no half transparency) | PASS | 0 half-transparent px |
| model | every textured face has a UV rectangle inside the texture, on painted pixels | PASS | 661 textured faces |
| model | emissive cubes: `light_emission` 15 and a name with `glow` go together | PASS | 22 emissive cubes |
| model | `hitbox` bone under root with one cube | PASS |  |
| model | hitbox cube = boss.yml > size, centred, on the ground | PASS | 28 x 72 x 28 px (size 1.75 x 4.5 blocks) |
| model | hitbox cube is not drawn (no textured face) | PASS |  |
| model | every hit-zone bone exists as its own bone with cubes | PASS |  |
| model | model.yml > hit_zone_boxes lists exactly the zones of boss.yml | PASS | zones: eyes, legs, sap_bulb, spit_root; mapped: eyes, legs, sap_bulb, spit_root |
| model | one hit-zone box per bone of every zone (every zone covered) | PASS | 14 boxes for 4 zones |
| model | each box: helper bone `zone_...` under its bone, one cube, invisible, no textured face | PASS |  |
| model | each box hugs its part (<= 1 px outside its cubes, holds >= 60 % of their volume) | PASS |  |
| model | no overlap between the boxes of two zones (at rest) | PASS |  |
| model | boxes on bones hidden by a mutation are marked `removed_by` that mutation | PASS | zone_spit_jaw_l, zone_spit_jaw_r, zone_spit_pod, zone_spit_root |
| model | hit-zone boxes (not counted in the cube budget) | INFO | zone_eyes (eyes) on eyes 8x12x1, 100 % of the part; zone_sap_bulb (sap_bulb) on bulb 5x6x5, 86 % of the part; zone_legs_shin_fl (legs) on shin_fl 6x44x7, 100 % of the part; zone_legs_shin_fr (legs) on shin_fr 6x44x7, 100 % of the part; zone_legs_shin_bl (legs) on shin_bl 4x33x6, 100 % of the part; zone_legs_shin_br (legs) on shin_br 4x33x6, 100 % of the part; zone_legs_foot_fl (legs) on foot_fl 6x3x4, 100 % of the part; zone_legs_foot_fr (legs) on foot_fr 6x3x4, 100 % of the part; zone_legs_foot_bl (legs) on foot_bl 4x12x5, 100 % of the part; zone_legs_foot_br (legs) on foot_br 4x12x5, 100 % of the part; zone_spit_root (spit_root) on spit_root 8x34x6, 100 % of the part; zone_spit_jaw_l (spit_root) on spit_jaw_l 4x13x5, 100 % of the part; zone_spit_jaw_r (spit_root) on spit_jaw_r 6x13x5, 100 % of the part; zone_spit_pod (spit_root) on spit_pod 3x3x3, 100 % of the part |
| model | every bone hidden or shown by a mutation exists | PASS |  |
| model | only the bones shown by a mutation are hidden at rest (visibility off) | PASS | hidden: spit_stump |
| model | no animation yet (step 3 writes them) | PASS | 0 animations |
| model | outline = concept in the front, side and back views (except on cubes added in model.yml) | PASS | differs by: front 0 px, side 0 px, back 0 px |
| model | pixels of the same colour as the concept views | INFO | 4348 of 4988 (87 %); the rest is texture detail added at step 2 |
| animation | animations in the model (one per spec name, length = windup + active + recovery) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
| sound | sounds/*.ogg (one per spec name, mono/stereo, loudness, LICENSES.md) | NOT YET | validator part not written yet (written by the agent of this step, skill §5) |
