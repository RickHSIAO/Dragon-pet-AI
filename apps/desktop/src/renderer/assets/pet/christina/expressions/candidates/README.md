# Christina 512x512 Expression Candidates

Tasks: TASK-093 (generation), TASK-094 (approval and promotion)

This directory contains normalized 512×512 face/bust candidates derived from the
original full-body expression PNGs. They were generated in TASK-093 as QA artifacts.

**TASK-094 status: ALL FOUR CANDIDATES APPROVED AND PROMOTED.**

The candidates in this directory have been copied to the runtime expression files:

```text
apps/desktop/src/renderer/assets/pet/christina/expressions/christina_<mood>.png
```

The files here are retained as QA/audit artifacts. The pre-promotion full-body
originals are archived in `../originals/`.

## Source and Output

| Mood | Source runtime file | Candidate file | Crop strategy |
|---|---|---|---|
| `focused` | `../christina_focused.png` | `christina_focused_512_candidate.png` | x50-y0 to x973-y843, then square pad and resize |
| `happy` | `../christina_happy.png` | `christina_happy_512_candidate.png` | x53-y0 to x976-y843, then square pad and resize |
| `proud` | `../christina_proud.png` | `christina_proud_512_candidate.png` | x50-y0 to x973-y843, then square pad and resize |
| `annoyed` | `../christina_annoyed.png` | `christina_annoyed_512_candidate.png` | x52-y0 to x975-y843, then square pad and resize |

The crop strategy follows the existing neutral asset approach: use the top
face/bust area, preserve horns, pad to square on transparent alpha, and resize
to 512x512. The script also removes edge-connected white/gray checker remnants
from sources that contain baked background artifacts.

## Candidate QA

| Mood | Size | Mode | Alpha | Alpha bbox | Transparent corners | Edge risk | 80x80 render |
|---|---:|---|---|---|---|---|---:|
| `focused` | 512x512 | RGBA | min 0 / max 255 | x9-y31 to x511-y489 | yes | near-white 0 / near-black 0 | 80.0x80.0 |
| `happy` | 512x512 | RGBA | min 0 / max 255 | x30-y27 to x511-y489 | yes | near-white 0 / near-black 0 | 80.0x80.0 |
| `proud` | 512x512 | RGBA | min 0 / max 255 | x20-y26 to x511-y489 | yes | near-white 0 / near-black 0 | 80.0x80.0 |
| `annoyed` | 512x512 | RGBA | min 0 / max 255 | x42-y31 to x511-y489 | yes | near-white 0 / near-black 0 | 80.0x80.0 |

## Preview

Open:

```text
apps/desktop/src/renderer/assets/pet/christina/expression-normalization-preview.html
```

The preview compares original full-body runtime PNGs against these normalized
candidates at the 80x80 pet display size.
