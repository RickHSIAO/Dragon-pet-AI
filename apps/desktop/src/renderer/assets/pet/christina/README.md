# Christina Visual Assets

Character: **Christina** ??the dragon pet AI companion.

---

## Reference Image

| File | Purpose |
|---|---|
| `reference/christina_v0_reference.png` | v0 visual reference ??removed background, RGBA PNG, 1024?1536 |

`christina_v0_reference.png` is the canonical baseline for all expression artwork.
It is a **local file only** ??never reference external image URLs anywhere in renderer code.

---

## Expression Asset Spec

### Directory

```
assets/pet/christina/expressions/
```

### Naming convention

```
christina_<mood>.png
```

One file per mood. The `<mood>` token must match exactly the mood string returned by the
`/chat` backend response and used as a key in `PET_EXPRESSIONS` / `KNOWN_MOODS`
in `renderer.js`.

### Required moods (10)

| Mood | Filename | Description |
|---|---|---|
| `neutral` | `christina_neutral.png` | Default resting expression |
| `focused` | `christina_focused.png` | Narrowed eyes, concentrating |
| `happy` | `christina_happy.png` | Closed curved eyes, smile |
| `proud` | `christina_proud.png` | Confident smug expression |
| `annoyed` | `christina_annoyed.png` | Furrowed brow, puffed cheek |
| `sleepy` | `christina_sleepy.png` | Half-closed eyes, drowsy |
| `worried` | `christina_worried.png` | Raised inner brows, uncertain |
| `pending` | `christina_pending.png` | Thinking / waiting expression |
| `error` | `christina_error.png` | Pained or alarmed expression |
| `offline` | `christina_offline.png` | Dim / greyed-out expression |

### Image requirements

- **Format:** PNG with alpha (RGBA, colour type 6)
- **Background:** fully transparent ??no white or grey fill
- **Recommended canvas size:** 512?512 px (square crop of the character face/bust)
- **Bit depth:** 8-bit
- **Colour space:** sRGB
- **No external URLs** ??all assets must be local files under this directory tree

### Current v0 expression assets (TASK-095-RESUME)

All 7 active runtime expression PNGs are now 512×512 RGBA face/bust crops:

- `christina_neutral.png`: 512×512 face/bust crop (TASK-085, 337 KB).
- `christina_focused.png`: 512×512 normalized face/bust (TASK-094, 396 KB).
- `christina_happy.png`: 512×512 normalized face/bust (TASK-094, 398 KB).
- `christina_proud.png`: 512×512 normalized face/bust (TASK-094, 380 KB).
- `christina_annoyed.png`: 512×512 normalized face/bust (TASK-094, 384 KB).
- `christina_worried.png`: 512×512 normalized face/bust (TASK-095-RESUME, 325 KB).
- `christina_sleepy.png`: 512×512 normalized face/bust (TASK-095-RESUME, 302 KB).
- `christina_pending.png`, `christina_error.png`, and `christina_offline.png`:
  not present yet; renderer falls back to inline SVG placeholders for these moods.

Pre-promotion full-body originals (1024×1536, ~2–2.6 MB each) are archived in
`expressions/originals/` and are not loaded at runtime. Normalization candidates
used for QA are retained in `expressions/candidates/`.

### TASK-092 → TASK-095-RESUME visual QA summary

- `neutral` fills 80×80 as face/bust (96%×90% fill). ✅
- `focused`, `happy`, `proud`, `annoyed` originally rendered at ~54×80 as tall
  full-body images. TASK-093 normalized them to 512×512 face/bust crops.
  TASK-094 promoted these candidates to runtime; all now fill ~92–98%×90% at
  80×80. ✅
- `worried`, `sleepy` integrated as full-body source images in TASK-095-RESUME.
  Normalized to 512×512 face/bust crops; fill 86–96%×90% at 80×80. ✅

### TASK-093 normalization candidates

Normalization script:
`../../../../../scripts/normalize-christina-expression-assets.py`

Candidate output directory:
`expressions/candidates/`

Preview file:
`expression-normalization-preview.html`

TASK-093 produced 512x512 RGBA face/bust candidates for:

- `focused`
- `happy`
- `proud`
- `annoyed`

These candidates are derived from the existing user-provided full-body PNGs.
They are not active runtime assets yet; the renderer still uses the original
`expressions/christina_<mood>.png` files. TASK-094 should decide whether the
candidates are good enough to replace the runtime PNGs.

### Renderer fallback behaviour

The renderer (`renderer.js`) probes local PNG files for known Christina moods and
falls back to inline SVG placeholder expressions when a PNG is missing. The UI is
never broken by a missing expression file.

Current behavior:
- If the mood PNG file is found, display the PNG expression.
- If the mood PNG file is missing, fall back to the inline SVG placeholder.
- Never show a broken-image icon.

---

## Rollout Strategy

TASK-091 integrated the existing user-provided `happy`, `proud`, `annoyed`, and
real `focused` PNG assets. TASK-093 produced QA-only normalized candidates for
those four moods. TASK-094 promoted all four candidates to runtime. TASK-095-RESUME
integrated `worried` and `sleepy` using the same normalization pipeline. Next steps:

1. Add remaining real mood-specific PNGs one at a time:
   `pending`, `error`, `offline`.

See `EXPRESSION_GENERATION_GUIDE.md` for the prompt drafts and production rules.

---

## What Not To Do

- Do not reference any Ollama runtime URL in renderer assets or code
- Do not use external image URLs or web-hosted artwork
- ??Do not add Live2D / Spine / 3D rigs
- ??Do not commit large binary test renders into `reference/`
- ??Do not change the `/chat` API schema to accommodate artwork changes
