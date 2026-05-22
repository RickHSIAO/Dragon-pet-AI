"""
TASK-085: Create christina_neutral.png from reference image.

Crop strategy:
  Source: apps/desktop/src/renderer/assets/pet/christina/reference/christina_v0_reference.png
          1024×1536 RGBA PNG, full-body portrait, transparent background

  Crop:   cols 59–982 (content width 924 px), rows 0–844 (top 55% = face + upper body)
  Pad:    centre in 924×924 transparent canvas
  Scale:  Lanczos → 512×512

Output: apps/desktop/src/renderer/assets/pet/christina/expressions/christina_neutral.png

Usage (from repo root):
  python apps/desktop/scripts/create-christina-neutral-asset.py

Requirements: Pillow  (pip install Pillow)
"""

from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[3]
REF = REPO_ROOT / "apps/desktop/src/renderer/assets/pet/christina/reference/christina_v0_reference.png"
OUT = REPO_ROOT / "apps/desktop/src/renderer/assets/pet/christina/expressions/christina_neutral.png"
TARGET = 512

# ── Crop parameters ────────────────────────────────────────────────────────
# Content bounding box from alpha inspection: rows 14–1518, cols 59–982
# Top 55% of height (0–844) captures horns, face, and upper-body / dress collar.
C_LEFT = 59
C_RIGHT = 983   # exclusive
C_TOP = 0
C_BOT = int(1536 * 0.55)   # 844

def main():
    img = Image.open(REF).convert("RGBA")
    region = img.crop((C_LEFT, C_TOP, C_RIGHT, C_BOT))
    rW, rH = region.size   # 924 × 844

    # Pad to square with transparent fill
    sq = max(rW, rH)
    square = Image.new("RGBA", (sq, sq), (0, 0, 0, 0))
    square.paste(region, ((sq - rW) // 2, (sq - rH) // 2))

    # Resize to target
    out = square.resize((TARGET, TARGET), Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, "PNG", optimize=False)
    print(f"Written: {OUT}  ({OUT.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
