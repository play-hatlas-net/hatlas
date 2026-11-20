"""Shared helpers of the boss pipeline tools (.claude/skills/boss-building/SKILL.md).

Run every tool with the pinned venv:
    python -m venv bosses/_tools/.venv
    bosses/_tools/.venv/Scripts/python -m pip install -r bosses/_tools/requirements.txt
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

PX_PER_BLOCK = 16
FIXED_BONES = ["root", "body", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
CUBE_BUDGET = {"minion": 40, "mini_boss": 120, "boss": 250}
TEXTURE_BUDGET = {"minion": 64, "mini_boss": 128, "boss": 256}
RUNES = ["fire", "frost", "storm", "nature"]


class DuplicateKeyError(yaml.YAMLError):
    pass


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that refuses a key written twice in the same mapping ("every name once")."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise DuplicateKeyError(f"key '{key}' written twice (line {key_node.start_mark.line + 1})")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=_UniqueKeyLoader)


_PALETTE_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*`(#[0-9a-fA-F]{6})`\s*\|")


def load_palette(style_md: Path) -> dict[str, tuple[int, int, int]]:
    """Palette of a dungeon: the rows `| `name` | `#rrggbb` | use |` of its style.md, in order."""
    palette: dict[str, tuple[int, int, int]] = {}
    for line in style_md.read_text(encoding="utf-8").splitlines():
        m = _PALETTE_ROW.match(line.strip())
        if m:
            h = m.group(2).lstrip("#")
            palette[m.group(1)] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return palette


def hexa(rgb) -> str:
    return "#%02x%02x%02x" % tuple(rgb[:3])
