# originals/

Archive of full-body source PNGs that were the runtime expressions before normalization.

## Why this directory exists

During TASK-094, the runtime expression PNGs for `focused`, `happy`, `proud`, and
`annoyed` were replaced by 512×512 normalized face/bust crops (see `candidates/` for
the QA pipeline). During TASK-095-RESUME, `worried` and `sleepy` were similarly
normalized. The originals are preserved here so the crop parameters can be audited
and the assets remain recoverable.

## Contents

| File | Source size | Description |
|---|---|---|
| `christina_focused_original.png` | 1024×1536 RGBA, ~2.0 MB | Full-body source for focused expression (TASK-094) |
| `christina_happy_original.png` | 1030×1527 RGBA, ~2.2 MB | Full-body source for happy expression (TASK-094) |
| `christina_proud_original.png` | 1024×1536 RGBA, ~2.1 MB | Full-body source for proud expression (TASK-094) |
| `christina_annoyed_original.png` | 1029×1528 RGBA, ~2.6 MB | Full-body source for annoyed expression (TASK-094) |
| `christina_worried_original.png` | 1030×1527 RGBA, ~2.0 MB | Full-body source for worried expression (TASK-095-RESUME) |
| `christina_sleepy_original.png` | 1024×1536 RGBA, ~1.9 MB | Full-body source for sleepy expression (TASK-095-RESUME) |

## Notes

- These files are **not loaded at runtime** — only the `expressions/christina_<mood>.png`
  files in the parent directory are used by the renderer.
- `christina_neutral.png` was already 512×512 (created in TASK-085) and did not need
  an original backup.
- These originals may be removed from git history if repo size becomes a concern.
  Add to `.gitignore` or move to git-lfs if needed.

## Safety rules

- Do not reference any file in this directory from renderer JavaScript.
- Do not add Ollama URLs, external image URLs, or Live2D/Spine/3D assets here.
