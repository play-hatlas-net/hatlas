"""Fungal Root concept (iteration 5): a walking root mass under a heavy glowing cap. No humanoid part.

Writes concept.yml next to this file. Run:
    bosses/_tools/.venv/Scripts/python bosses/dark_forest/fungal_root/concept/design.py
    bosses/_tools/.venv/Scripts/python bosses/_tools/concept_sheet.py bosses/dark_forest/fungal_root

Shape: FOUR stilt root legs around a root mass (front legs: knee knot above the hip like a spider's;
back legs: bent backwards at a hock like an animal's), a thin bark trunk that leans forward under the
weight of a wide stepped cap, static glowing knot-hole eyes in the trunk. 5 blocks tall.
Its two attacking limbs both grow from the RIGHT side of the root mass (nothing on the left: from the
front it is a lopsided growth, not a figure with two arms), and both end in jaws:
  - the lash root: arches forward and ends in a long horizontal jaw (uneven fangs, lavender gums,
    split bark, boils, strands of glowing drool);
  - the spit root (the old staff): stands taller than the cap and splits open at its tip into two
    peeled halves lined with teeth, the glowing spore pod sitting inside the gape. Nothing is held.
A lavender sap bulb hangs under the cap on the left, fed into the trunk by a sap vein (the heal channel).
Iteration 5: the eyes sit on their own static bone `eyes` (a hit zone), and `spit_stump` is drawn but
hidden until the mutation `torn_spit_root` (boss.yml) removes the spit root.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_tools"))
from concept_build import Concept  # noqa: E402

c = Concept()
CZ = -9  # the cap is centred well in front of the root mass: the trunk leans forward

# ------------------------------------------------------------------ front legs: spider stilts
c.note("front legs: thigh rises from the root mass to a knee knot ABOVE the hip, shin drops to the ground")
c.sym("leg_f{s}", 5, 34, -6, 4, 4, 3, "root")
c.sym("leg_f{s}", 8, 37, -9, 3, 7, 3, "bark")
c.sym("shin_f{s}", 8, 43, -11, 4, 4, 4, "root")           # knee knot
c.sym("shin_f{s}", 10, 24, -12, 3, 19, 3, "bark")
c.sym("shin_f{s}", 11, 3, -14, 3, 21, 3, "bark")
c.sym("foot_f{s}", 10, 0, -14, 4, 3, 4, "root")
c.sym("foot_f{s}", 8, 0, -13, 2, 1, 2, "root")            # rootlet toe
c.sym("shin_f{s}", 12, 5, -14, 1, 17, 0, "cyan_deep", paint=True)     # mycelium vein, front
c.sym("shin_f{s}", 11, 26, -12, 1, 15, 0, "night_bark", paint=True)
c.sym("shin_f{s}", 14, 6, -13, 0, 16, 1, "cyan_deep", paint=True)     # vein, outer side
c.sym("shin_f{s}", 13, 26, -11, 0, 15, 1, "night_bark", paint=True)
c.sym("shin_f{s}", 11, 5, -11, 1, 17, 0, "night_bark", paint=True)    # back face

# ------------------------------------------------------------------ back legs: bent backwards (hock)
c.note("back legs: knee knot high and behind, shin steps forward to a hock, then back down (digitigrade)")
c.sym("leg_b{s}", 4, 32, 6, 4, 4, 4, "root")             # set closer together than the front legs:
c.sym("leg_b{s}", 5, 35, 9, 3, 6, 3, "bark")             # the four stilts show from the front
c.sym("shin_b{s}", 4, 40, 10, 4, 4, 4, "root")            # knee knot
c.sym("shin_b{s}", 5, 22, 11, 3, 18, 3, "bark")
c.sym("shin_b{s}", 5, 11, 8, 3, 12, 3, "bark")            # hock: the leg bends forward here
c.sym("foot_b{s}", 5, 2, 10, 3, 10, 3, "root")
c.sym("foot_b{s}", 4, 0, 9, 4, 2, 5, "root")
c.sym("shin_b{s}", 6, 23, 14, 1, 16, 0, "cyan_deep", paint=True)      # vein, back face
c.sym("shin_b{s}", 8, 24, 12, 0, 15, 1, "cyan_deep", paint=True)      # vein, outer side
c.sym("shin_b{s}", 8, 12, 9, 0, 10, 1, "night_bark", paint=True)
c.sym("shin_b{s}", 6, 12, 8, 1, 10, 0, "cyan_deep", paint=True)       # vein, front of the hock

# ------------------------------------------------------------------ lash root and its jaw (right, front)
c.note("lash root: rises from the right of the root mass (lash_base), arches forward (lash_mid), ends in a jaw")
c.box("lash_base", 6, 30, -3, 6, 4, 4, "root")
c.box("lash_base", 11, 31, -4, 5, 5, 4, "root")
c.box("lash_base", 15, 35, -5, 3, 13, 3, "bark")
c.box("lash_base", 18, 41, -5, 2, 2, 2, "cap")            # boil
c.fx("lash_base", -5, 42, 1, 1, 20, "cyan_glow")
c.fx("lash_base", -4, 37, 1, 10, 18, "cyan_deep")
c.fz("lash_base", 16, 37, 1, 10, -5, "night_bark")
c.box("lash_mid", 14, 47, -7, 5, 5, 5, "root")            # the knot it whips from
c.box("lash_mid", 15, 48, -17, 3, 3, 10, "bark")
c.box("lash_mid", 15, 40, -19, 3, 9, 3, "bark")
c.fx("lash_mid", -16, 49, 8, 1, 18, "cyan_deep")
c.fx("lash_mid", -18, 41, 1, 7, 18, "cyan_deep")
c.fz("lash_mid", 16, 41, 1, 7, -19, "cyan_deep")
c.note("maw (upper jaw) and jaw (long lower jaw): split bark, lavender gums, uneven fangs, boils, glowing drool")
c.box("maw", 12, 35, -27, 8, 5, 10, "bark")
c.box("maw", 13, 31, -26, 6, 4, 8, "void_dark")           # throat
c.box("maw", 13, 33, -27, 1, 2, 1, "glow_core")           # upper fangs, all different
c.box("maw", 15, 31, -27, 1, 4, 1, "glow_core")
c.box("maw", 17, 32, -27, 1, 3, 1, "glow_core")
c.box("maw", 20, 37, -23, 2, 2, 2, "cap")                 # boil
c.box("maw", 14, 40, -23, 3, 1, 3, "cap_deep")            # shelf fungus growing on it
c.box("jaw", 13, 28, -28, 6, 3, 10, "bark")
c.box("jaw", 14, 31, -28, 1, 3, 1, "glow_core")           # lower fangs
c.box("jaw", 18, 31, -28, 1, 2, 1, "glow_core")
c.box("jaw", 15, 24, -28, 1, 4, 1, "cyan_deep")           # drool
c.box("jaw", 18, 26, -27, 1, 2, 1, "cyan_deep")
c.paint("jaw", 15, 24, -28, 1, 1, 1, "cyan_glow")
c.paint("jaw", 18, 26, -27, 1, 1, 1, "cyan_glow")
c.fz("maw", 12, 35, 8, 1, -27, "lilac_deep")              # gums
c.fz("maw", 14, 36, 1, 4, -27, "night_bark")              # split bark
c.fz("maw", 18, 37, 1, 3, -27, "night_bark")
c.fz("maw", 16, 38, 1, 2, -27, "stem_pale")               # peeled to the pale wood
c.fz("jaw", 13, 30, 6, 1, -28, "lilac_deep")
c.fz("jaw", 16, 28, 1, 2, -28, "night_bark")
c.fz("jaw", 16, 31, 1, 1, -28, "glow_core")
for x in (20, 12):
    c.fx("maw", -27, 35, 10, 1, x, "lilac_deep")
    c.fx("maw", -24, 36, 1, 4, x, "night_bark")
    c.fx("maw", -20, 37, 2, 1, x, "stem_pale")
    c.fx("maw", -19, 38, 1, 2, x, "night_bark")
for x in (19, 13):                                         # teeth along the side of the gape, uneven
    c.fx("maw", -25, 33, 1, 2, x, "glow_core")
    c.fx("maw", -23, 32, 1, 3, x, "glow_core")
    c.fx("maw", -21, 34, 1, 1, x, "glow_core")
    c.fx("maw", -20, 33, 1, 2, x, "glow_core")
    c.fx("jaw", -24, 31, 1, 2, x, "glow_core")
    c.fx("jaw", -22, 31, 1, 1, x, "glow_core")
    c.fx("jaw", -19, 31, 1, 2, x, "glow_core")
    c.fx("jaw", -28, 30, 10, 1, x, "lilac_deep")
    c.fx("jaw", -25, 28, 1, 2, x, "night_bark")
c.fx("maw", -23, 38, 1, 1, 22, "cyan_glow")
c.fz("maw", 15, 40, 1, 1, -23, "lilac_glow")
c.fz("maw", 14, 37, 3, 1, -17, "night_bark")

# ------------------------------------------------------------------ spit root (right, back): the old staff
c.note("spit root: grows from the right of the root mass (spit_base), stands taller than the cap (spit_root)")
c.box("spit_base", 6, 31, 2, 8, 4, 4, "root")
c.box("spit_base", 13, 30, 4, 6, 5, 5, "root")
c.box("spit_root", 18, 29, 5, 6, 6, 6, "root")            # the knot it bends on
c.box("spit_root", 20, 35, 7, 3, 12, 3, "bark")
c.box("spit_root", 21, 47, 6, 3, 12, 3, "bark")
c.box("spit_root", 19, 58, 5, 7, 3, 5, "root")            # swelling under the split
c.box("spit_root", 20, 61, 6, 5, 2, 3, "void_dark")       # throat
c.box("spit_root", 23, 40, 8, 2, 2, 2, "cap")             # boils
c.box("spit_root", 19, 51, 7, 2, 2, 2, "lilac_deep")
c.box("spit_root", 25, 54, 5, 1, 4, 1, "cyan_deep")       # drool
c.paint("spit_root", 25, 54, 5, 1, 1, 1, "cyan_glow")
c.fz("spit_root", 21, 37, 1, 9, 7, "cyan_deep")
c.fz("spit_root", 22, 49, 1, 8, 6, "cyan_deep")
c.fz("spit_root", 21, 37, 1, 9, 10, "night_bark")
c.fz("spit_root", 22, 49, 1, 8, 9, "night_bark")
c.fx("spit_root", 8, 37, 1, 9, 23, "cyan_deep")
c.fx("spit_root", 7, 49, 1, 8, 24, "cyan_deep")
c.fx("spit_root", 9, 41, 1, 1, 25, "cyan_glow")
c.fz("spit_root", 19, 52, 1, 1, 7, "lilac_glow")
c.fz("spit_root", 22, 58, 1, 3, 5, "night_bark")
c.fz("spit_root", 22, 58, 1, 3, 10, "night_bark")
c.fx("spit_root", 7, 58, 1, 3, 26, "night_bark")
c.note("spit_jaw_l / spit_jaw_r: the tip split into two peeled halves lined with teeth; spit_pod glows in the gape")
c.box("spit_jaw_l", 18, 61, 5, 2, 11, 5, "bark")
c.box("spit_jaw_l", 20, 65, 5, 2, 1, 1, "glow_core")
c.box("spit_jaw_l", 20, 68, 8, 1, 1, 1, "glow_core")
c.box("spit_jaw_l", 20, 70, 6, 2, 1, 1, "glow_core")
c.box("spit_jaw_l", 18, 72, 6, 1, 2, 1, "glow_core")      # tip fang
c.box("spit_jaw_r", 25, 61, 5, 2, 8, 5, "bark")
c.box("spit_jaw_r", 27, 67, 5, 2, 5, 5, "bark")           # the outer half peels outward
c.box("spit_jaw_r", 23, 66, 5, 2, 1, 1, "glow_core")
c.box("spit_jaw_r", 24, 63, 8, 1, 1, 1, "glow_core")
c.box("spit_jaw_r", 26, 70, 7, 1, 1, 1, "glow_core")
c.box("spit_jaw_r", 28, 72, 8, 1, 2, 1, "glow_core")      # tip fang
c.box("spit_pod", 21, 63, 6, 3, 3, 3, "cyan_glow")
c.fz("spit_pod", 22, 64, 1, 1, 6, "glow_core")
c.fz("spit_pod", 22, 64, 1, 1, 9, "glow_core")
c.fx("spit_pod", 7, 64, 1, 1, 24, "glow_core")
for z in (5, 10):
    c.fz("spit_jaw_l", 19, 62, 1, 10, z, "lilac_deep")    # gums on the inner edge
    c.fz("spit_jaw_l", 18, 70, 1, 2, z, "stem_pale")      # peeled tip
    c.fz("spit_jaw_l", 18, 63, 1, 4, z, "night_bark")
    c.fz("spit_jaw_r", 25, 62, 1, 6, z, "lilac_deep")
    c.fz("spit_jaw_r", 27, 68, 1, 4, z, "lilac_deep")
    c.fz("spit_jaw_r", 28, 70, 1, 2, z, "stem_pale")
    c.fz("spit_jaw_r", 26, 62, 1, 3, z, "night_bark")
c.fx("spit_jaw_r", 7, 68, 1, 3, 29, "night_bark")
c.fx("spit_jaw_r", 6, 62, 1, 4, 27, "night_bark")
c.fx("spit_jaw_r", 8, 63, 1, 3, 27, "stem_pale")
c.fx("spit_jaw_r", 9, 70, 1, 1, 29, "cyan_glow")
c.note("spit_stump: HIDDEN until the mutation torn_spit_root shows it: the splintered stub left on spit_base")
c.box("spit_stump", 18, 30, 5, 4, 5, 5, "root")
c.box("spit_stump", 19, 35, 6, 1, 3, 1, "stem_pale")      # splinters of pale wood
c.box("spit_stump", 21, 35, 8, 1, 2, 1, "stem_pale")
c.fz("spit_stump", 18, 34, 4, 1, 5, "lilac_deep")         # sap bleeding from the tear
c.fz("spit_stump", 20, 31, 1, 3, 5, "lilac_deep")
c.fz("spit_stump", 20, 31, 1, 1, 5, "lilac_glow")
c.fz("spit_stump", 18, 34, 4, 1, 10, "lilac_deep")
c.fx("spit_stump", 5, 34, 5, 1, 22, "lilac_deep")
c.fx("spit_stump", 7, 32, 1, 2, 22, "lilac_deep")
c.fx("spit_stump", 7, 32, 1, 1, 22, "lilac_glow")


class Lift:
    """Everything above the legs is written as in iteration 3 and raised by UP pixels (longer legs)."""
    UP = 8

    def __init__(self, inner):
        self.inner = inner

    def __getattr__(self, name):
        fn = getattr(self.inner, name)
        if name not in ("box", "paint", "sym", "fz", "fx"):
            return fn
        return lambda bone, a, y, *rest, **kw: fn(bone, a, y + self.UP, *rest, **kw)


c = Lift(c)


def cap(y, h, w, d, color, cz=CZ, paint=False):
    c.box("head", -w // 2, y, cz - d // 2, w, h, d, color, paint)


# ------------------------------------------------------------------ root mass and trunk
c.note("hip: the root mass the four legs and the two jaw roots grow from, rootlets dangling under it")
c.box("hip", -6, 22, -3, 12, 8, 10, "night_bark")
c.box("hip", -4, 19, -1, 8, 3, 6, "root")
c.box("hip", -2, 14, 0, 1, 5, 1, "root")
c.box("hip", 2, 12, 3, 1, 7, 1, "root")
c.box("hip", -4, 16, 4, 1, 3, 1, "root")
c.paint("hip", -2, 14, 0, 1, 1, 1, "cyan_deep")
c.paint("hip", 2, 12, 3, 1, 1, 1, "cyan_deep")
c.fz("hip", -4, 23, 1, 5, -3, "bark")
c.fz("hip", 1, 24, 1, 5, -3, "bark")
c.fz("hip", 4, 23, 1, 3, -3, "root")
c.fz("hip", -3, 23, 1, 5, 7, "bark")
c.fz("hip", 2, 24, 1, 4, 7, "bark")
c.fx("hip", 0, 24, 1, 5, 6, "bark")
c.fx("hip", 4, 23, 1, 4, 6, "bark")

c.note("body: the lower trunk, upright over the root mass")
c.box("body", -4, 29, -2, 8, 12, 7, "bark")
c.fz("body", -2, 30, 1, 8, -2, "night_bark")
c.fz("body", 1, 31, 1, 7, -2, "night_bark")
c.fz("body", -1, 33, 1, 5, -2, "cyan_deep")              # mycelium vein up the trunk
c.fx("body", 0, 30, 1, 9, 4, "night_bark")
c.fx("body", 3, 31, 1, 8, 4, "night_bark")
c.fz("body", -2, 30, 1, 9, 5, "night_bark")
c.fz("body", 1, 31, 1, 6, 5, "night_bark")
c.box("body", -3, 33, 5, 5, 1, 2, "cap")                  # shelf fungi
c.box("body", -6, 36, 0, 2, 1, 3, "cap")

c.note("chest: the upper trunk, shifted forward (the lean); the eyes are static knot-holes painted on it")
c.box("chest", -4, 39, -7, 8, 12, 8, "bark")
c.box("chest", -3, 41, 1, 6, 5, 3, "root")                # burl on the back of the bend
c.box("chest", -4, 46, 1, 6, 1, 4, "cap_deep")            # shelf fungus on the burl
c.box("chest", 4, 47, -5, 2, 1, 4, "lichen")
c.box("eyes", -4, 39, -8, 8, 12, 1, "bark")              # eye plate: the front of the upper trunk, its own
                                                          # bone only to be a hit zone (weak point); never animated
c.fz("eyes", 1, 43, 3, 7, -8, "void_dark")               # right eye: tall knot-hole
c.fz("eyes", 1, 44, 2, 5, -8, "cyan_glow")
c.fz("eyes", 2, 46, 1, 2, -8, "glow_core")
c.fz("eyes", -4, 41, 3, 5, -8, "void_dark")              # left eye: lower, smaller
c.fz("eyes", -3, 42, 2, 3, -8, "cyan_glow")
c.fz("eyes", -3, 43, 1, 1, -8, "glow_core")
c.fz("eyes", -2, 47, 3, 3, -8, "void_dark")              # third, tiny
c.fz("eyes", -1, 48, 1, 1, -8, "cyan_glow")
c.fz("eyes", -4, 39, 8, 1, -8, "night_bark")
c.fz("eyes", 0, 40, 1, 3, -8, "night_bark")
c.fz("eyes", -1, 39, 1, 2, -8, "cyan_deep")              # the trunk vein reaches the eyes
c.fx("chest", -5, 40, 1, 9, 4, "night_bark")
c.fx("chest", -2, 39, 1, 7, 4, "night_bark")
c.fz("chest", -2, 46, 1, 5, 1, "night_bark")
c.fz("chest", 2, 47, 1, 4, 1, "night_bark")
c.fz("chest", -1, 42, 2, 1, 4, "night_bark")
c.fz("chest", -3, 46, 1, 1, 5, "cyan_glow")
c.fz("chest", 0, 46, 1, 1, 5, "lilac_glow")
c.fx("chest", 2, 46, 1, 1, 2, "cyan_glow")

c.note("neck: pale stem under the cap, pushed forward")
c.box("neck", -3, 50, -12, 6, 4, 6, "stem_pale")
c.fz("neck", -2, 50, 1, 4, -12, "stem_shadow")
c.fz("neck", 1, 50, 1, 3, -12, "stem_shadow")
c.fx("neck", -10, 50, 1, 4, 3, "stem_shadow")
c.fx("neck", -8, 50, 1, 3, 3, "stem_shadow")
c.fz("neck", -1, 50, 1, 4, -6, "stem_shadow")

# ------------------------------------------------------------------ the cap
c.note("head: the cap. Stepped dome hanging forward (front lip lower, each step set back), glowing gills below")
cap(54, 1, 28, 26, "cyan_deep")                           # gills: the glowing underside
for x in range(-13, 14, 2):
    c.fz("head", x, 54, 1, 1, CZ - 13, "cyan_glow")
    c.fz("head", x, 54, 1, 1, CZ + 13, "cyan_glow")
for z in range(-12, 13, 2):
    c.fx("head", CZ + z, 54, 1, 1, 14, "cyan_glow")
    c.fx("head", CZ + z, 54, 1, 1, -14, "cyan_glow")
cap(55, 3, 34, 26, "cap_deep")                            # brim (octagon)
cap(55, 3, 26, 34, "cap_deep")
cap(55, 3, 30, 30, "cap_deep")
cap(55, 1, 34, 26, "cap_light", paint=True)               # lighter rim
cap(55, 1, 26, 34, "cap_light", paint=True)
cap(55, 1, 30, 30, "cap_light", paint=True)
c.box("head", -12, 52, -26, 24, 3, 5, "cap_deep")         # front lip: the cap droops forward
c.paint("head", -12, 52, -26, 24, 1, 5, "cap_light")
for x in range(-11, 12, 2):
    c.fz("head", x, 53, 1, 1, -26, "cyan_deep")
cap(58, 4, 30, 22, "cap_deep", cz=-8)                     # second step
cap(58, 4, 22, 30, "cap_deep", cz=-8)
cap(58, 4, 26, 26, "cap_deep", cz=-8)
cap(62, 3, 22, 22, "cap", cz=-7)                          # third step
cap(65, 2, 14, 14, "cap", cz=-6)                          # top
cap(66, 1, 14, 14, "cap_light", cz=-6, paint=True)
# glowing spots, cyan and lavender. Front planes: brim z -26, second step z -23, third step z -18
c.fz("head", -9, 56, 2, 2, -26, "cyan_glow")
c.fz("head", 6, 56, 2, 1, -26, "lilac_glow")
c.fz("head", 0, 56, 1, 1, -26, "cyan_glow")
c.fz("head", -3, 59, 3, 2, -23, "cyan_glow")
c.fz("head", 7, 60, 1, 1, -23, "cyan_glow")
c.fz("head", -9, 60, 2, 1, -23, "lilac_glow")
c.fz("head", 3, 63, 2, 1, -18, "lilac_glow")
c.fz("head", -6, 63, 1, 1, -18, "cyan_glow")
c.fz("head", 9, 63, 1, 1, -18, "cyan_glow")
# back planes: brim z 8, second step z 7, third step z 4
c.fz("head", -8, 56, 2, 1, 8, "cyan_glow")
c.fz("head", 4, 56, 2, 2, 8, "lilac_glow")
c.fz("head", 0, 59, 2, 2, 7, "cyan_glow")
c.fz("head", -8, 60, 1, 1, 7, "lilac_glow")
c.fz("head", 7, 60, 1, 1, 7, "cyan_glow")
c.fz("head", 5, 63, 1, 1, 4, "cyan_glow")
c.fz("head", -4, 63, 2, 1, 4, "cyan_glow")
# sides: brim x +-17, second step x +-15, third step x +-11
for x, s in ((17, 1), (-17, -1)):
    c.fx("head", -18, 56, 2, 2, x, "cyan_glow")
    c.fx("head", -5, 56, 2, 1, x, "lilac_glow")
    c.fx("head", 1, 56, 1, 1, x, "cyan_glow")
    c.fx("head", -12, 59, 2, 2, x - 2 * s, "lilac_glow")
    c.fx("head", -2, 60, 1, 1, x - 2 * s, "cyan_glow")
    c.fx("head", -15, 63, 1, 1, x - 6 * s, "cyan_glow")
    c.fx("head", -7, 63, 2, 1, x - 6 * s, "cyan_glow")

c.note("cap_sprouts: young mushrooms growing on the cap (they shake when it casts)")
c.box("cap_sprouts", 8, 65, -1, 1, 5, 1, "stem_pale")
c.box("cap_sprouts", 6, 70, -3, 5, 1, 5, "cap")
c.box("cap_sprouts", 7, 71, -2, 3, 1, 3, "cap_light")
c.box("cap_sprouts", -12, 62, 2, 1, 2, 1, "stem_pale")
c.box("cap_sprouts", -13, 64, 1, 3, 1, 3, "cap_light")
c.box("cap_sprouts", -3, 67, -8, 1, 2, 1, "stem_pale")
c.box("cap_sprouts", -4, 69, -9, 3, 1, 3, "cap_light")
c.fz("cap_sprouts", 8, 70, 1, 1, -3, "cyan_glow")
c.fx("cap_sprouts", -1, 70, 1, 1, 11, "cyan_glow")
c.fz("cap_sprouts", 8, 70, 1, 1, 2, "lilac_glow")
c.fz("cap_sprouts", -3, 69, 1, 1, -9, "lilac_glow")

c.note("tendrils: glowing strands dripping from the brim (four bones so they can sway and spread)")


def tendril(bone, x, z, length, top=55):
    c.box(bone, x, top - length, z, 1, length, 1, "cyan_deep")
    c.paint(bone, x, top - length, z, 1, 2, 1, "cyan_glow")
    c.paint(bone, x, top - length, z, 1, 1, 1, "glow_core")


tendril("tendrils_f", 11, -26, 6, top=52)                 # kept away from the eyes and the bulb
tendril("tendrils_f", 7, -26, 10, top=52)
tendril("tendrils_f", -12, -26, 8, top=52)
tendril("tendrils_b", -10, 7, 8)
tendril("tendrils_b", -3, 7, 14)
tendril("tendrils_b", 5, 7, 7)
tendril("tendrils_b", 11, 7, 11)
tendril("tendrils_r", 16, -17, 7)
tendril("tendrils_r", 16, -9, 10)
tendril("tendrils_l", -17, -14, 5)
tendril("tendrils_l", -17, 0, 10)

c.note("bulb: the lavender sap sac under the cap, and the sap vein that feeds the trunk (heal channel)")
c.box("bulb", -8, 49, -19, 1, 5, 1, "cap_deep")
c.box("bulb", -10, 43, -21, 5, 6, 5, "lilac_deep")
c.box("bulb", -6, 45, -16, 2, 1, 10, "lilac_deep")         # sap vein from the sac to the trunk
c.fz("bulb", -9, 44, 3, 4, -21, "lilac_glow")
c.fz("bulb", -8, 46, 1, 1, -21, "glow_core")
c.fx("bulb", -20, 44, 3, 4, -10, "lilac_glow")
c.fx("bulb", -19, 46, 1, 1, -10, "glow_core")
c.fx("bulb", -20, 44, 3, 4, -5, "lilac_glow")
c.fz("bulb", -9, 44, 3, 3, -16, "lilac_glow")
c.fx("bulb", -14, 45, 2, 1, -6, "lilac_glow")              # a pulse of sap in the vein
c.fx("bulb", -10, 45, 1, 1, -6, "lilac_glow")

c.write(Path(__file__).with_name("concept.yml"), "Fungal Root")
