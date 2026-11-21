"""Dark Mushroom concept (iteration 4): a small aggressive mushroom on four root legs. No arms.

Writes concept.yml next to this file. Run:
    bosses/_tools/.venv/Scripts/python bosses/dark_forest/dark_mushroom/concept/design.py
    bosses/_tools/.venv/Scripts/python bosses/_tools/concept_sheet.py bosses/dark_forest/dark_mushroom

Shape: the domed dark blue cap is the head (two glowing cyan eyes with slit pupils and an angry slant,
of different sizes). Under it, a tall open mouth: a black inside, lavender gums, and long sharp fangs
of different lengths that interlock (the four longest stick out in front). A short pale stem behind
the mouth, four small bent root legs, a tiny sprout on top.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_tools"))
from concept_build import Concept  # noqa: E402

c = Concept()
H = 2  # the cap sits 2 px higher than in iteration 3: the mouth is taller

c.note("four small root legs: a knot at the stem, a bent rootlet down, a root toe (no arms)")
c.sym("leg_f{s}", 3, 2, -2, 3, 3, 3, "root")
c.sym("leg_f{s}", 5, 0, -3, 2, 3, 2, "bark")
c.sym("leg_f{s}", 6, 0, -5, 1, 1, 2, "root")
c.sym("leg_b{s}", 3, 2, 3, 3, 3, 3, "root")
c.sym("leg_b{s}", 5, 0, 4, 2, 3, 2, "bark")
c.sym("leg_b{s}", 6, 0, 6, 1, 1, 1, "root")
c.sym("leg_f{s}", 6, 0, -5, 1, 1, 1, "cyan_deep", paint=True)         # glowing root tips
c.sym("leg_b{s}", 6, 0, 6, 1, 1, 1, "cyan_deep", paint=True)

c.note("body: the short pale stem; its front is the tall mouth (black inside)")
c.box("body", -4, 3, -2, 8, 7, 7, "stem_pale")
c.box("body", -5, 3, -7, 10, 7, 5, "void_dark")           # inside of the mouth
for x in (-3, 0, 2):
    c.fz("body", x, 3, 1, 6, 5, "stem_shadow")
for z in (0, 3):
    c.fx("body", z, 3, 1, 6, 4, "stem_shadow")
    c.fx("body", z, 3, 1, 6, -4, "stem_shadow")

# fangs: (x, length). Lower ones rise from the lower gum (y 3), upper ones hang from the upper gum (y 9).
LOWER = [(-5, 4), (-1, 3), (3, 4)]
UPPER = [(-3, 4), (1, 4)]            # one column of black between two fangs, so each one reads
LONG = 4  # fangs of this length are real cubes sticking out in front; the others are painted on the plates

c.note("jaw: dark root lip, lower tooth plate (black, lavender gum, fangs of different lengths)")
c.box("jaw", -5, 1, -8, 10, 2, 6, "bark")
c.box("jaw", -5, 3, -8, 10, 4, 1, "void_dark")            # lower tooth plate
c.note("head: upper tooth plate under the front edge of the cap")
c.box("head", -5, 6, -8, 10, 4, 1, "void_dark")           # upper tooth plate
c.fz("jaw", -5, 3, 10, 1, -8, "lilac_deep")               # gums
c.fz("head", -5, 9, 10, 1, -8, "lilac_deep")
for x, n in LOWER:
    if n >= LONG:
        c.box("jaw", x, 4, -9, 1, n, 1, "glow_core")
    else:
        c.fz("jaw", x, 4, 1, n, -8, "glow_core")
for x, n in UPPER:
    if n >= LONG:
        c.box("head", x, 9 - n, -9, 1, n, 1, "glow_core")
    else:
        c.fz("head", x, 9 - n, 1, n, -8, "glow_core")
c.fz("jaw", -5, 1, 10, 1, -8, "root")
for x in (5, -5):                                         # the mouth seen from the side
    c.fx("jaw", -8, 1, 6, 1, x, "root")
    c.fx("body", -7, 3, 5, 1, x, "lilac_deep")
    c.fx("body", -7, 9, 5, 1, x, "lilac_deep")
    c.fx("body", -6, 4, 1, 2, x, "glow_core")
    c.fx("body", -4, 4, 1, 1, x, "glow_core")
    c.fx("body", -5, 7, 1, 2, x, "glow_core")
    c.fx("body", -3, 6, 1, 3, x, "glow_core")

DEEP = {"cyan_glow": "cyan_deep", "lilac_glow": "lilac_deep"}


def spot(fn, a, y, w, h, p, color):
    """Zone readability (skill step 1): a cap spot is a dim patch with ONE bright pixel; the big bright
    patches belong to the weak points."""
    if w * h > 1:
        fn("head", a, y, w, h, p, DEEP[color])
    fn("head", a, y, 1, 1, p, color)


c.note("head: the cap. Stepped dome, glowing gills, eyes on its front")
c.box("head", -7, 8 + H, -7, 14, 1, 14, "cyan_deep")      # gills
for i, x in enumerate((-6, -4, -2, 0, 2, 4, 6)):          # zone readability: one gill dot in three is bright
    col = "cyan_glow" if i % 3 == 0 else "cyan_deep"
    c.fz("head", x, 8 + H, 1, 1, -7, col)
    c.fz("head", x, 8 + H, 1, 1, 7, col)
    c.fx("head", x, 8 + H, 1, 1, 7, col)
    c.fx("head", x, 8 + H, 1, 1, -7, col)
c.box("head", -8, 9 + H, -6, 16, 2, 12, "cap_deep")       # brim (octagon)
c.box("head", -6, 9 + H, -8, 12, 2, 16, "cap_deep")
c.box("head", -7, 9 + H, -7, 14, 2, 14, "cap_deep")
c.paint("head", -8, 9 + H, -6, 16, 1, 12, "cap_light")    # lighter rim
c.paint("head", -6, 9 + H, -8, 12, 1, 16, "cap_light")
c.paint("head", -7, 9 + H, -7, 14, 1, 14, "cap_light")
c.box("head", -7, 11 + H, -5, 14, 3, 10, "cap_deep")      # second step
c.box("head", -5, 11 + H, -7, 10, 3, 14, "cap_deep")
c.box("head", -6, 11 + H, -6, 12, 3, 12, "cap_deep")
c.box("head", -5, 14 + H, -5, 10, 2, 10, "cap")           # third step
c.box("head", -3, 16 + H, -3, 6, 1, 6, "cap")             # top
c.paint("head", -3, 16 + H, -3, 6, 1, 6, "cap_light")
c.box("head", 2, 10 + H, -9, 4, 4, 2, "cyan_glow")        # right eye: big, bulging
c.fz("head", 3, 10 + H, 1, 4, -9, "void_dark")            # slit pupil
c.fz("head", 4, 12 + H, 1, 1, -9, "glow_core")
c.fz("head", 2, 13 + H, 1, 1, -9, "cap_deep")             # angry slant
c.fx("head", -9, 11 + H, 1, 2, 6, "void_dark")
c.box("head", -5, 11 + H, -9, 3, 3, 2, "cyan_glow")       # left eye: smaller
c.fz("head", -4, 11 + H, 1, 3, -9, "void_dark")
c.fz("head", -3, 13 + H, 1, 1, -9, "cap_deep")
c.fx("head", -9, 12 + H, 1, 1, -5, "void_dark")
spot(c.fz, -1, 12 + H, 2, 1, -7, "lilac_glow")          # spots, cyan and lavender
spot(c.fz, -3, 15 + H, 1, 1, -5, "cyan_glow")
spot(c.fz, 2, 15 + H, 2, 1, -5, "lilac_glow")
spot(c.fx, -3, 10 + H, 2, 1, 8, "cyan_glow")
spot(c.fx, 1, 12 + H, 2, 2, 7, "lilac_glow")
spot(c.fx, -2, 15 + H, 1, 1, 5, "cyan_glow")
spot(c.fx, 4, 10 + H, 1, 1, 8, "cyan_glow")
spot(c.fx, -2, 10 + H, 2, 1, -8, "lilac_glow")
spot(c.fx, 2, 12 + H, 2, 2, -7, "cyan_glow")
spot(c.fx, 0, 15 + H, 1, 1, -5, "cyan_glow")
spot(c.fz, -4, 10 + H, 2, 1, 8, "cyan_glow")
spot(c.fz, 2, 12 + H, 2, 2, 7, "lilac_glow")
spot(c.fz, -2, 13 + H, 1, 1, 7, "cyan_glow")
spot(c.fz, 3, 10 + H, 1, 1, 8, "cyan_glow")
spot(c.fz, -2, 15 + H, 2, 1, 5, "cyan_glow")

c.note("sprout: a tiny mushroom growing on the cap (wobbles when it walks)")
c.box("sprout", 1, 17 + H, 1, 1, 1, 1, "stem_pale")
c.box("sprout", 0, 18 + H, 0, 3, 1, 3, "cap_light")

c.write(Path(__file__).with_name("concept.yml"), "Dark Mushroom")
