#!/usr/bin/env python3
"""Builds favicon set from assets/brand/favicon.png (or logo-mark.png). Needs Pillow. Run before build.py."""
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent
src = next((R / "assets/brand" / n for n in ("favicon.png", "logo-mark.png") if (R / "assets/brand" / n).exists()), None)
if not src:
    raise SystemExit("Put assets/brand/favicon.png (square PNG, 512+ px) first")
im = Image.open(src).convert("RGBA")
side = max(im.size)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
out = R / "assets/brand"
for n, s in (("favicon-32.png", 32), ("favicon-192.png", 192), ("favicon-512.png", 512)):
    sq.resize((s, s), Image.LANCZOS).save(out / n, optimize=True)
bg = Image.new("RGBA", (180, 180), (7, 12, 32, 255))
t = sq.resize((150, 150), Image.LANCZOS); bg.paste(t, (15, 15), t)
bg.convert("RGB").save(out / "apple-touch-icon.png", optimize=True)
sq.save(R / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("icons written")
