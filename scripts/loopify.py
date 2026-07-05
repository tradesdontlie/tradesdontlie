#!/usr/bin/env python3
"""Make the 3D contribution graph's grow animation loop forever.

The github-profile-3d-contrib action emits SMIL animations that all share
dur="3s" repeatCount="1" with no begin offsets, freezing after one play.
Rewrite each one to: grow (3s) -> hold (5s) -> restart, indefinitely.
"""
import re
import sys

GROW = 3.0
CYCLE = 8.0


def loopify_tag(tag: str) -> str:
    m = re.search(r'values="([^"]*)"', tag)
    if not m or 'repeatCount="1"' not in tag:
        return tag
    vals = m.group(1).split(";")
    # hold the final value for the rest of the cycle
    vals.append(vals[-1])
    n = len(vals)
    grow_frac = GROW / CYCLE
    key_times = [f"{i * grow_frac / (n - 2):.4f}" for i in range(n - 1)] + ["1"]
    tag = tag.replace(m.group(0), f'values="{";".join(vals)}" keyTimes="{";".join(key_times)}"')
    tag = re.sub(r'dur="[^"]*"', f'dur="{CYCLE:g}s"', tag)
    tag = tag.replace('repeatCount="1"', 'repeatCount="indefinite"')
    return tag


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    out, count = re.subn(r"<animate(?:Transform)?[^>]*>", lambda m: loopify_tag(m.group(0)), svg)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"loopified {count} animations in {path}")


if __name__ == "__main__":
    main(sys.argv[1])
