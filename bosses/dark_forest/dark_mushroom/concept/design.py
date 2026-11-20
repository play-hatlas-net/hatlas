"""Dark Mushroom concept (iteration 2): a little mushroom creature, not humanoid.

Writes concept.yml next to this file. Run:
    bosses/_tools/.venv/Scripts/python bosses/dark_forest/dark_mushroom/concept/design.py
    bosses/_tools/.venv/Scripts/python bosses/_tools/concept_sheet.py bosses/dark_forest/dark_mushroom

Shape: the domed cap is the head (two bulging eyes of different sizes on its front), a wide toothed
mouth opens under the cap (underbite jaw, fangs, tongue), a short pale stem, four stubby legs, a tiny
sprout on top.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_tools"))
from concept_build import Concept  # noqa: E402

c = Concept()

c.note("four stubby legs with a toe")
for name, z, toe_z in (("leg_f{s}", -5, -6), ("leg_b{s}", 2, 5)):
    c.sym(name, 3, 0, z, 3, 4, 3, "stem_shadow")
    c.sym(name, 3, 0, toe_z, 3, 1, 1, "gill_pale")
    c.sym(name, 6, 1, z + 1, 0, 2, 1, "gill_pale", paint=True)

c.note("body: the short pale stem; its front is the throat")
c.box("body", -5, 3, -3, 10, 5, 8, "gill_pale")
c.box("body", -5, 4, -6, 10, 4, 3, "maw_dark")           # inside of the mouth
for x in (-4, -1, 2):
    c.fz("body", x, 3, 1, 3, 5, "stem_shadow")
for z in (-1, 2):
    c.fx("body", z, 3, 1, 4, 5, "stem_shadow")
    c.fx("body", z, 3, 1, 4, -5, "stem_shadow")
c.fx("body", -6, 4, 3, 4, 5, "maw_dark")                 # mouth corners seen from the side
c.fx("body", -6, 4, 3, 4, -5, "maw_dark")

c.note("jaw: wide underbite with a tooth row, two fangs and a lolling tongue")
c.box("jaw", -5, 2, -7, 10, 2, 5, "gill_pale")
c.box("jaw", -4, 4, -7, 8, 1, 1, "glow_core")            # tooth row
c.box("jaw", -5, 4, -7, 1, 2, 1, "glow_core")            # fangs
c.box("jaw", 4, 4, -7, 1, 2, 1, "glow_core")
c.box("jaw", -1, 5, -8, 2, 1, 4, "potion_red")           # tongue
for x in (-3, -1, 1, 3):
    c.paint("jaw", x, 4, -7, 1, 1, 1, "maw_dark")        # gaps between the teeth
c.fz("jaw", -5, 2, 10, 1, -7, "stem_shadow")
c.fx("jaw", -7, 2, 5, 1, 5, "stem_shadow")
c.fx("jaw", -7, 2, 5, 1, -5, "stem_shadow")

c.note("head: the cap. Stepped dome, upper teeth under its front edge, glowing spots")
c.box("head", -7, 7, -7, 14, 1, 14, "gill_pale")         # gills
for x in (-6, -3, 0, 3, 6):
    c.fz("head", x, 7, 1, 1, 7, "stem_shadow")
    c.fx("head", x, 7, 1, 1, 7, "stem_shadow")
    c.fx("head", x, 7, 1, 1, -7, "stem_shadow")
c.box("head", -5, 7, -7, 10, 1, 1, "glow_core")          # upper tooth row
c.box("head", -4, 6, -7, 1, 1, 1, "glow_core")           # upper fangs
c.box("head", 3, 6, -7, 1, 1, 1, "glow_core")
for x in (-2, 0, 2):
    c.paint("head", x, 7, -7, 1, 1, 1, "maw_dark")
c.box("head", -8, 8, -6, 16, 2, 12, "cap_deep")          # brim (octagon)
c.box("head", -6, 8, -8, 12, 2, 16, "cap_deep")
c.box("head", -7, 8, -7, 14, 2, 14, "cap_deep")
c.paint("head", -8, 8, -6, 16, 1, 12, "cap")             # lighter rim
c.paint("head", -6, 8, -8, 12, 1, 16, "cap")
c.paint("head", -7, 8, -7, 14, 1, 14, "cap")
c.box("head", -7, 10, -5, 14, 3, 10, "cap_deep")         # second step
c.box("head", -5, 10, -7, 10, 3, 14, "cap_deep")
c.box("head", -6, 10, -6, 12, 3, 12, "cap_deep")
c.box("head", -5, 13, -5, 10, 2, 10, "cap")              # third step
c.box("head", -3, 15, -3, 6, 1, 6, "cap")                # top
c.paint("head", -3, 15, -3, 6, 1, 6, "cap_light")
c.box("head", 2, 9, -9, 4, 4, 2, "eye_amber")            # right eye: big, bulging
c.fz("head", 3, 10, 2, 2, -9, "maw_dark")
c.fz("head", 3, 11, 1, 1, -9, "glow_core")
c.fx("head", -9, 10, 1, 2, 6, "maw_dark")
c.box("head", -5, 10, -9, 3, 3, 2, "eye_amber")          # left eye: smaller (a mad look)
c.fz("head", -4, 10, 1, 2, -9, "maw_dark")
c.fz("head", -1, 11, 2, 1, -7, "spore_glow")             # spots
c.fz("head", -3, 14, 1, 1, -5, "spore_glow")
c.fz("head", 2, 13, 2, 1, -5, "spore_glow")
c.fx("head", -3, 9, 2, 1, 8, "spore_glow")
c.fx("head", 1, 11, 2, 2, 7, "spore_glow")
c.fx("head", -2, 14, 1, 1, 5, "spore_glow")
c.fx("head", 4, 9, 1, 1, 8, "spore_glow")
c.fz("head", -4, 9, 2, 1, 8, "spore_glow")
c.fz("head", 2, 11, 2, 2, 7, "spore_glow")
c.fz("head", -2, 12, 1, 1, 7, "spore_glow")
c.fz("head", 3, 9, 1, 1, 8, "spore_glow")
c.fz("head", -2, 14, 2, 1, 5, "spore_glow")

c.note("sprout: a tiny mushroom growing on the cap (wobbles when it walks)")
c.box("sprout", 1, 16, 1, 1, 2, 1, "gill_pale")
c.box("sprout", 0, 18, 0, 3, 1, 3, "cap_light")

c.write(Path(__file__).with_name("concept.yml"), "Dark Mushroom")
