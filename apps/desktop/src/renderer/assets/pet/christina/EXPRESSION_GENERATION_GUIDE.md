# Christina Expression Generation Guide

Tasks: TASK-090 (original), TASK-097 (status update)

This guide prepares real mood-specific Christina expression PNGs. It does not
add renderer behavior, change `/chat`, or create additional placeholder images.

## Current Expression State (as of TASK-097)

| Mood | PNG state | Runtime behavior |
|---|---|---|
| `neutral` | ✅ real v0 asset (512×512, TASK-085) | PNG displayed |
| `focused` | ✅ real user-provided, normalized (512×512, TASK-094) | PNG displayed |
| `happy` | ✅ real user-provided, normalized (512×512, TASK-094) | PNG displayed |
| `proud` | ✅ real user-provided, normalized (512×512, TASK-094) | PNG displayed |
| `annoyed` | ✅ real user-provided, normalized (512×512, TASK-094) | PNG displayed |
| `worried` | ✅ real user-provided, normalized (512×512, TASK-095-RESUME) | PNG displayed |
| `sleepy` | ✅ real user-provided, normalized (512×512, TASK-095-RESUME) | PNG displayed |
| `pending` | ⬜ missing | SVG fallback (TASK-096 BLOCKED) |
| `error` | ⬜ missing | SVG fallback (TASK-096 BLOCKED) |
| `offline` | ⬜ missing | SVG fallback (TASK-096 BLOCKED) |

## Production Rules

- Keep the same character design as `reference/christina_v0_reference.png`.
- Output one PNG per mood, named `christina_<mood>.png`.
- Canvas: 512x512 px.
- Mode: RGBA PNG with transparent alpha.
- Background: transparent only; no white, gray, scenic, or gradient background.
- Crop: match `christina_neutral.png` face/bust framing and character scale.
- Runtime target: must remain readable in the 80x80 Electron pet display.
- Do not use external image URLs.
- Do not add Live2D, Spine, 3D, rigging, animation, or layered runtime assets.
- Do not change renderer behavior to support generation artifacts.
- Do not change `/chat` schema.

## Recommended Production Order

TASK-091 integrated `happy`, `proud`, `annoyed`, and `focused` PNG assets.
TASK-094 normalized all four to 512×512 face/bust crops.
TASK-095-RESUME integrated `worried` and `sleepy`.
TASK-096 is BLOCKED awaiting source images. Next real PNG production:

1. `pending` (system-state: thinking / waiting)
2. `error` (system-state: startled / concerned)
3. `offline` (system-state: quiet / inactive)

To resume: provide source images for these three moods, then run TASK-096-RESUME
using the same normalization pipeline as TASK-095-RESUME. Prompts are below.

The `happy`, `proud`, `annoyed`, and `focused` prompts below remain useful if a
future visual QA pass decides to normalize or redraw those assets to the ideal
512x512 face/bust framing.

## Base Prompt Template

Use this base for every mood, with the mood-specific expression appended.

```text
Create a 512x512 RGBA PNG character expression asset for Christina, matching the
same character design, costume, hair, horns, face shape, and crop scale as the
provided local reference image christina_v0_reference.png. Keep the same
face-and-upper-bust framing as christina_neutral.png. Transparent background.
Clean anime/light-novel style, crisp readable facial features, soft shading,
no full-body pose, no background, no props, no text, no logo. The expression
must remain clear at 80x80 pixels in a desktop pet UI.
```

Optional negative prompt:

```text
Do not change character identity, age impression, outfit, horn placement, hair
color, crop scale, camera angle, or silhouette. No background, no scenery, no
extra characters, no hands covering the face, no text, no watermark, no 3D,
no Live2D rig, no animation frame sheet.
```

## Mood Prompt Drafts

### happy

```text
Mood: happy. Christina has a bright pleased smile, softened eyes, and a tiny
childlike sparkle of delight, as if she just received praise or sweets. Keep her
dragon-pride aura, but make the emotion warm and easy to read at 80x80.
```

### proud

```text
Mood: proud. Christina has a smug confident grin, slightly raised chin, and
half-lidded superior eyes, as if she is declaring that humans should admire her.
Expression should feel arrogant but cute, not angry.
```

### annoyed

```text
Mood: annoyed. Christina has a small frown, furrowed brows, and a puffed-cheek
tsundere irritation. She looks bothered by a foolish human but still cute and
not threatening. Keep the face readable at 80x80.
```

### focused

```text
Mood: focused. Christina is attentive and listening carefully, with slightly
narrowed eyes, calm brows, and a concentrated forward gaze. She should look like
she is processing the user's words seriously, not angry or sleepy.
```

### worried

```text
Mood: worried. Christina has raised inner brows, a small uncertain mouth, and
soft anxious eyes, as if she is concerned about a companion. Keep it protective
and sympathetic rather than terrified.
```

### sleepy

```text
Mood: sleepy. Christina has drowsy half-closed eyes, relaxed brows, and a small
tired mouth, as if she is trying to stay awake while listening. Keep the pose and
crop stable; no bed, pillow, or background props.
```

### pending

```text
Mood: pending. Christina looks like she is thinking or waiting for a local model
response, with a focused neutral mouth, slightly lifted brows, and attentive eyes.
The expression should communicate "processing" without adding symbols, text, or
props.
```

### error

```text
Mood: error. Christina looks startled and concerned, with widened eyes and tense
brows, as if something went wrong safely. Avoid horror, injury, tears, or extreme
distress. Keep it suitable for a small desktop companion UI.
```

### offline

```text
Mood: offline. Christina looks quiet and inactive, with subdued sleepy eyes and
a slightly dim emotional tone. Keep the same colors and alpha transparency; do
not make the whole image gray unless a later visual QA task approves it.
```

## Review Checklist Per Asset

- File is 512x512.
- File is RGBA with transparent alpha.
- Character scale matches `christina_neutral.png`.
- Transparent border is clean; no white fringe.
- Face remains readable at 80x80.
- Mood is visually distinct from neutral.
- Filename matches `christina_<mood>.png`.
- Renderer safety scan still finds no direct Ollama runtime URL.
