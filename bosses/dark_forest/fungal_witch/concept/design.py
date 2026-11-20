"""Fungal Witch concept (iteration 2): a tall, thin fungal creature, no human part.

Writes concept.yml next to this file. Run:
    bosses/_tools/.venv/Scripts/python bosses/dark_forest/fungal_witch/concept/design.py
    bosses/_tools/.venv/Scripts/python bosses/_tools/concept_sheet.py bosses/dark_forest/fungal_witch

Shape: two stilt root legs, a narrow bark stalk with glowing eye slits, a wide stepped mushroom cap as
the head (dripping tendrils, a pointed young mushroom on top = the "witch" outline), two long root arms
ending in blind snapping maws. The left maw clamps a forked root staff with a glowing spore pod; a red
sap bulb hangs under the cap (the heal channel: the right maw bites it and drinks).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_tools"))
from concept_build import Concept  # noqa: E402

c = Concept()
CZ = -1  # the cap is centred a little forward: the stalk is hunched


def cap(y, h, w, d, color, paint=False):
    c.box("head", -w // 2, y, CZ - d // 2, w, h, d, color, paint)


# ------------------------------------------------------------------ legs (stilts, knees forward)
c.note("feet: spread roots (foot_r / foot_l)")
c.sym("foot_{s}", 6, 0, -5, 4, 2, 6, "root")
c.sym("foot_{s}", 6, 0, -7, 1, 1, 2, "root")
c.sym("foot_{s}", 9, 0, -7, 1, 1, 2, "root")
c.sym("foot_{s}", 7, 0, 1, 2, 1, 2, "root")
c.note("shins and knee knots (shin_r / shin_l)")
c.sym("shin_{s}", 6, 2, -2, 3, 13, 3, "bark")
c.sym("shin_{s}", 5, 15, -3, 4, 4, 4, "root")
c.box("shin_r", 6, 17, -5, 3, 1, 2, "cap_deep")          # small shelf fungus on the front of the right knee
c.box("shin_l", -10, 9, -1, 2, 1, 3, "cap")              # and lower on the left shin
c.sym("shin_{s}", 7, 4, -2, 1, 9, 0, "gill_pale", paint=True)     # mycelium vein
c.sym("shin_{s}", 6, 2, -2, 3, 1, 0, "night_bark", paint=True)
c.sym("shin_{s}", 9, 3, -1, 0, 10, 1, "night_bark", paint=True)
c.note("thighs (leg_r / leg_l)")
c.sym("leg_{s}", 4, 19, -1, 3, 6, 3, "bark")
c.sym("leg_{s}", 2, 25, -1, 3, 6, 3, "bark")
c.sym("leg_{s}", 5, 20, -1, 1, 4, 0, "night_bark", paint=True)
c.sym("leg_{s}", 3, 26, -1, 1, 4, 0, "night_bark", paint=True)

# ------------------------------------------------------------------ trunk
c.note("hip knot")
c.box("hip", -5, 29, -3, 10, 4, 6, "night_bark")
c.fz("hip", -3, 30, 2, 1, -3, "root")
c.fz("hip", 2, 31, 2, 1, -3, "root")
c.note("body: the thin lower stalk")
c.box("body", -3, 33, -2, 6, 11, 5, "bark")
c.fz("body", -2, 34, 1, 8, -2, "night_bark")
c.fz("body", 1, 36, 1, 6, -2, "night_bark")
c.fz("body", 0, 39, 1, 4, -2, "gill_pale")
c.fx("body", 0, 34, 1, 9, 3, "night_bark")
c.fz("body", -1, 35, 1, 7, 3, "night_bark")
c.box("body", -2, 37, 3, 4, 1, 2, "cap")                 # shelf fungi down the back
c.box("body", -3, 42, 3, 5, 1, 2, "cap_deep")
c.note("chest: upper stalk, hunched forward; the eyes are slits in the bark (no face, no mouth)")
c.box("chest", -4, 44, -4, 8, 10, 7, "bark")
c.sym("chest", 4, 50, -3, 3, 4, 5, "root")               # shoulder knots
c.box("chest", -7, 54, -3, 3, 1, 5, "moss")              # moss on the left shoulder
c.box("chest", -3, 48, 3, 6, 1, 3, "cap")                # big shelf fungus on the back
c.fz("chest", 0, 46, 5, 7, -4, "night_bark")             # eye sockets
c.fz("chest", -4, 45, 4, 6, -4, "night_bark")
c.fz("chest", 1, 47, 2, 5, -4, "eye_amber")              # right eye: tall slit
c.fz("chest", 2, 48, 1, 3, -4, "maw_dark")
c.fz("chest", -3, 46, 2, 3, -4, "eye_amber")             # left eye: lower, smaller
c.fz("chest", -3, 47, 1, 1, -4, "maw_dark")
c.fz("chest", -1, 52, 1, 1, -4, "eye_amber")             # third, tiny
c.fz("chest", -4, 44, 8, 1, -4, "night_bark")
c.fz("chest", 3, 44, 1, 4, -4, "night_bark")
c.fx("chest", -2, 45, 1, 6, 4, "night_bark")
c.fx("chest", 1, 44, 1, 8, 4, "night_bark")
c.fz("chest", -2, 44, 1, 4, 3, "night_bark")
c.fz("chest", 2, 44, 1, 3, 3, "night_bark")
c.fz("chest", -2, 48, 1, 1, 6, "spore_glow")
c.fz("chest", 1, 48, 1, 1, 6, "spore_glow")
c.fz("chest", 5, 51, 1, 2, -3, "moss")
c.note("neck: pale stem under the cap")
c.box("neck", -2, 54, -3, 4, 4, 4, "gill_pale")
c.fz("neck", -1, 54, 1, 4, -3, "stem_shadow")
c.fz("neck", 1, 54, 1, 3, -3, "stem_shadow")
c.fx("neck", -2, 54, 1, 4, 2, "stem_shadow")
c.fz("neck", 0, 54, 1, 4, 1, "stem_shadow")

# ------------------------------------------------------------------ right arm: hangs to the ground, maw
c.note("right arm (arm_r, forearm_r) and its maw (maw_r upper jaw, jaw_r lower jaw)")
c.box("arm_r", 7, 45, -2, 3, 8, 3, "bark")
c.box("arm_r", 9, 37, -2, 3, 9, 3, "bark")
c.fz("arm_r", 8, 46, 1, 5, -2, "night_bark")
c.fz("arm_r", 10, 38, 1, 6, -2, "night_bark")
c.box("forearm_r", 9, 33, -3, 4, 4, 4, "root")           # elbow knot
c.box("forearm_r", 10, 20, -4, 3, 13, 3, "bark")
c.fz("forearm_r", 11, 22, 1, 9, -4, "gill_pale")
c.fx("forearm_r", -3, 21, 1, 10, 13, "night_bark")
c.box("maw_r", 8, 14, -10, 7, 5, 8, "cap_deep")          # upper jaw: a closed cap
c.box("maw_r", 9, 19, -9, 5, 1, 6, "cap")
c.box("maw_r", 9, 12, -9, 5, 2, 6, "maw_dark")           # throat
c.box("maw_r", 9, 12, -10, 1, 2, 1, "glow_core")         # fangs
c.box("maw_r", 13, 12, -10, 1, 2, 1, "glow_core")
c.box("jaw_r", 9, 10, -10, 5, 2, 7, "gill_pale")
c.box("jaw_r", 11, 12, -12, 2, 1, 3, "potion_red")       # tongue
c.fz("maw_r", 8, 14, 7, 1, -10, "cap")                   # lip
c.fz("maw_r", 11, 16, 2, 1, -10, "spore_glow")
c.fx("maw_r", -10, 14, 8, 1, 15, "cap")
c.fx("maw_r", -8, 13, 1, 1, 14, "glow_core")
c.fx("maw_r", -6, 13, 1, 1, 14, "glow_core")
c.fx("maw_r", -4, 13, 1, 1, 14, "glow_core")
c.fx("maw_r", -6, 16, 2, 2, 15, "spore_glow")
c.fz("jaw_r", 10, 11, 1, 1, -10, "glow_core")
c.fz("jaw_r", 12, 11, 1, 1, -10, "glow_core")
c.fx("jaw_r", -8, 10, 5, 1, 14, "stem_shadow")
c.fz("maw_r", 10, 16, 3, 1, -2, "cap")

# ------------------------------------------------------------------ left arm: bent forward, clamps the staff
c.note("left arm (arm_l, forearm_l); its maw (maw_l outer jaw, jaw_l inner jaw) clamps the staff sideways")
c.box("arm_l", -10, 45, -2, 3, 8, 3, "bark")
c.box("arm_l", -12, 38, -2, 3, 8, 3, "bark")
c.fz("arm_l", -9, 46, 1, 5, -2, "night_bark")
c.fz("arm_l", -11, 39, 1, 5, -2, "night_bark")
c.box("forearm_l", -13, 34, -3, 4, 5, 4, "root")         # elbow knot
c.box("forearm_l", -14, 36, -9, 3, 3, 6, "bark")         # forearm reaching forward
c.box("maw_l", -18, 34, -16, 5, 7, 7, "cap_deep")        # outer jaw
c.box("maw_l", -19, 35, -15, 1, 5, 5, "cap")
c.box("maw_l", -13, 35, -11, 3, 5, 2, "maw_dark")        # throat behind the staff
c.box("jaw_l", -10, 35, -16, 2, 5, 7, "gill_pale")       # inner jaw
c.fz("maw_l", -14, 35, 1, 1, -16, "glow_core")
c.fz("maw_l", -14, 37, 1, 1, -16, "glow_core")
c.fz("maw_l", -14, 39, 1, 1, -16, "glow_core")
c.fz("maw_l", -17, 37, 2, 2, -16, "spore_glow")
c.fz("jaw_l", -10, 36, 1, 1, -16, "glow_core")
c.fz("jaw_l", -10, 38, 1, 1, -16, "glow_core")
c.fz("maw_l", -17, 36, 2, 1, -9, "cap")

c.note("staff: a forked root planted in the ground, a glowing spore pod between its prongs")
c.box("staff", -14, 0, -15, 5, 1, 5, "root")             # spread root tip
c.box("staff", -13, 1, -14, 3, 19, 3, "root")
c.box("staff", -14, 20, -14, 3, 14, 3, "root")
c.box("staff", -13, 34, -14, 3, 10, 3, "root")
c.box("staff", -16, 44, -14, 8, 2, 3, "root")            # fork
c.box("staff", -16, 46, -14, 2, 8, 2, "root")
c.box("staff", -10, 46, -14, 2, 5, 2, "root")
c.box("staff", -11, 12, -13, 2, 1, 3, "cap_deep")        # tiny shelf fungi on the shaft
c.box("staff", -16, 26, -13, 2, 1, 3, "cap")
c.box("staff_pod", -14, 47, -15, 4, 4, 4, "spore_glow")
c.fz("staff_pod", -13, 48, 2, 2, -15, "glow_core")
c.fx("staff_pod", -14, 48, 2, 2, -10, "glow_core")
c.fz("staff_pod", -13, 48, 2, 2, -11, "glow_core")
c.fz("staff", -12, 3, 1, 14, -14, "bark")
c.fz("staff", -13, 22, 1, 10, -14, "bark")
c.fz("staff", -12, 36, 1, 7, -14, "bark")
c.fz("staff", -13, 22, 1, 10, -11, "bark")
c.fz("staff", -12, 3, 1, 14, -11, "bark")

# ------------------------------------------------------------------ the cap = the head
c.note("head: the cap. Stepped dome, octagonal footprint, pale gills below, glowing spots")
cap(57, 1, 26, 26, "gill_pale")
for x in range(-12, 13, 3):                               # gill stripes on the visible edges
    c.fz("head", x, 57, 1, 1, CZ - 13, "stem_shadow")
    c.fz("head", x, 57, 1, 1, CZ + 13, "stem_shadow")
    c.fx("head", CZ + x, 57, 1, 1, 13, "stem_shadow")
cap(58, 3, 32, 24, "cap_deep")                           # brim
cap(58, 3, 24, 32, "cap_deep")
cap(58, 3, 28, 28, "cap_deep")
cap(58, 1, 32, 24, "cap", paint=True)                    # lighter rim
cap(58, 1, 24, 32, "cap", paint=True)
cap(58, 1, 28, 28, "cap", paint=True)
cap(61, 4, 28, 20, "cap_deep")                           # second step
cap(61, 4, 20, 28, "cap_deep")
cap(61, 4, 24, 24, "cap_deep")
cap(65, 3, 20, 20, "cap")                                # third step
cap(68, 2, 12, 12, "cap")                                # top
cap(69, 1, 12, 12, "cap_light", paint=True)
# glowing spots: front (z = CZ - 16 / -14 / -10), back, right side
c.fz("head", -9, 59, 2, 2, CZ - 16, "spore_glow")
c.fz("head", 6, 59, 2, 1, CZ - 16, "spore_glow")
c.fz("head", -2, 62, 3, 2, CZ - 14, "spore_glow")
c.fz("head", 6, 63, 1, 1, CZ - 14, "spore_glow")
c.fz("head", -8, 63, 1, 1, CZ - 14, "spore_glow")
c.fz("head", 3, 66, 2, 1, CZ - 10, "spore_glow")
c.fz("head", -6, 66, 1, 1, CZ - 10, "spore_glow")
c.fz("head", -7, 59, 2, 1, CZ + 16, "spore_glow")
c.fz("head", 4, 59, 2, 2, CZ + 16, "spore_glow")
c.fz("head", 0, 62, 2, 2, CZ + 14, "spore_glow")
c.fz("head", -8, 63, 1, 1, CZ + 14, "spore_glow")
c.fz("head", 5, 66, 1, 1, CZ + 10, "spore_glow")
c.fx("head", -8, 59, 2, 2, 16, "spore_glow")
c.fx("head", 5, 59, 2, 1, 16, "spore_glow")
c.fx("head", -3, 62, 2, 2, 14, "spore_glow")
c.fx("head", 6, 63, 1, 1, 14, "spore_glow")
c.fx("head", 1, 66, 2, 1, 10, "spore_glow")

c.note("cap_crown: the pointed young mushroom (bent back) that gives the 'witch' outline, and two small ones")
c.box("cap_crown", -3, 70, 0, 2, 3, 2, "gill_pale")
c.box("cap_crown", -5, 73, -2, 6, 2, 6, "cap_deep")
c.box("cap_crown", -4, 75, 0, 4, 2, 4, "cap_deep")
c.box("cap_crown", -3, 77, 2, 2, 2, 2, "cap")
c.box("cap_crown", -3, 76, 4, 2, 2, 1, "cap")            # the tip droops backward
c.fz("cap_crown", -4, 73, 1, 1, -2, "spore_glow")
c.fx("cap_crown", 1, 74, 1, 1, 1, "spore_glow")
c.box("cap_crown", 7, 68, -6, 1, 2, 1, "gill_pale")
c.box("cap_crown", 5, 70, -8, 4, 1, 4, "cap_light")
c.box("cap_crown", 11, 65, 6, 1, 2, 1, "gill_pale")
c.box("cap_crown", 10, 67, 5, 3, 1, 3, "cap_light")

c.note("tendrils: strands dripping from the brim, glowing tips (four bones so they can sway and spread)")


def tendril(bone, x, z, length):
    c.box(bone, x, 58 - length, z, 1, length, 1, "cap_deep")
    c.paint(bone, x, 58 - length, z, 1, 1, 1, "spore_glow")


tendril("tendrils_f", -11, CZ - 16, 5)
tendril("tendrils_f", -4, CZ - 16, 9)
tendril("tendrils_f", 2, CZ - 16, 5)
tendril("tendrils_f", 10, CZ - 16, 12)
tendril("tendrils_b", -10, CZ + 15, 8)
tendril("tendrils_b", -3, CZ + 15, 15)
tendril("tendrils_b", 5, CZ + 15, 7)
tendril("tendrils_b", 11, CZ + 15, 11)
tendril("tendrils_r", 15, CZ - 7, 7)
tendril("tendrils_r", 15, CZ + 5, 13)
tendril("tendrils_l", -16, CZ - 5, 5)
tendril("tendrils_l", -16, CZ + 7, 10)

c.note("bulb: the sap sac hanging under the cap (heal channel: the right maw bites it and drinks)")
c.box("bulb", 5, 51, -9, 1, 6, 1, "cap_deep")
c.box("bulb", 3, 46, -11, 4, 5, 4, "potion_red")
c.fz("bulb", 4, 49, 1, 1, -11, "glow_core")
c.fx("bulb", -10, 48, 1, 1, 7, "glow_core")

c.write(Path(__file__).with_name("concept.yml"), "Fungal Witch")
