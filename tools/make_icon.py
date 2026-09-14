#!/usr/bin/env python3
"""Draw the application icon and write it to src/liu_analyzer/resources/icon.ico.

    .venv\\Scripts\\python.exe tools\\make_icon.py

The mark is a U: the third letter of Liu, and the cross-section of the crater
a pulse leaves, which is what the whole program is about. It is drawn here
rather than kept as a binary source so that it can be changed with a diff.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "src" / "liu_analyzer" / "resources" / "icon.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]
BLUE = (37, 99, 184, 255)   # the same blue as the README badges
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def draw(size: int) -> Image.Image:
    # Draw at 4x and shrink, so that the edges are smooth at every size.
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.22, fill=BLUE)

    # A crater profile: a round bowl with walls that flare out to the rim.
    # Built from filled shapes, because a thick polyline leaves hairlines at
    # its joints.
    w = s * 0.11
    left, right = s * 0.25, s * 0.75
    top, bowl_top = s * 0.21, s * 0.47
    flare = s * 0.045
    cx = s / 2
    r = (right - left) / 2 - flare

    # The bowl: a white disc, the middle cut out, the top half cut away. Drawn
    # on its own layer so the cuts do not touch the rounded background.
    ro, ri = r + w / 2, r - w / 2
    bowl = Image.new("RGBA", (s, s), CLEAR)
    b = ImageDraw.Draw(bowl)
    b.ellipse((cx - ro, bowl_top - ro, cx + ro, bowl_top + ro), fill=WHITE)
    b.ellipse((cx - ri, bowl_top - ri, cx + ri, bowl_top + ri), fill=CLEAR)
    b.rectangle((0, 0, s, bowl_top), fill=CLEAR)
    img.alpha_composite(bowl)

    # The walls, with round ends at the rim and round joints at the bowl.
    for x_top, x_bottom in ((left, left + flare), (right, right - flare)):
        d.line([(x_top, top), (x_bottom, bowl_top)], fill=WHITE, width=int(w))
        for x, y in ((x_top, top), (x_bottom, bowl_top)):
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=WHITE)

    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    frames = [draw(size) for size in SIZES]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[-1].save(OUT, format="ICO", sizes=[(s, s) for s in SIZES], append_images=frames[:-1])
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(SIZES)} sizes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
