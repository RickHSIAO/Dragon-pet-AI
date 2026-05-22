"""Normalize Christina full-body expression PNGs into 512x512 candidates.

TASK-093 produces QA candidates only. It does not overwrite runtime expression
PNGs. The script intentionally uses only the Python standard library because the
desktop QA environment does not require Pillow.

Usage from repo root:
  python apps/desktop/scripts/normalize-christina-expression-assets.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
import zlib


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPRESSIONS = REPO_ROOT / "apps/desktop/src/renderer/assets/pet/christina/expressions"
CANDIDATES = EXPRESSIONS / "candidates"
TARGET = 512


@dataclass(frozen=True)
class CropSpec:
    mood: str
    source: str
    output: str
    box: tuple[int, int, int, int]
    note: str


# Crop strategy:
# - Match the neutral asset pipeline: top face/bust area, padded to square, then
#   resized to 512x512.
# - Keep horns in frame by starting at y=0.
# - Use 924px-wide crops for the 1024/1030px-wide source images to match the
#   neutral crop scale.
CROPS: tuple[CropSpec, ...] = (
    CropSpec(
        mood="focused",
        source="christina_focused.png",
        output="christina_focused_512_candidate.png",
        box=(50, 0, 974, 844),
        note="top 55% face/bust crop; preserves horns and reaching hand",
    ),
    CropSpec(
        mood="happy",
        source="christina_happy.png",
        output="christina_happy_512_candidate.png",
        box=(53, 0, 977, 844),
        note="top face/bust crop centered to match neutral scale",
    ),
    CropSpec(
        mood="proud",
        source="christina_proud.png",
        output="christina_proud_512_candidate.png",
        box=(50, 0, 974, 844),
        note="top face/bust crop; preserves horns and smug face",
    ),
    CropSpec(
        mood="annoyed",
        source="christina_annoyed.png",
        output="christina_annoyed_512_candidate.png",
        box=(52, 0, 976, 844),
        note="top face/bust crop; preserves horns and annoyed face",
    ),
)


def read_png_rgba(path: Path) -> tuple[int, int, list[bytearray]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")

    pos = 8
    width = height = bit_depth = color_type = interlace = None
    idat: list[bytes] = []

    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if kind == b"IHDR":
            width, height, bit_depth, color_type, _comp, _filter, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif kind == b"IDAT":
            idat.append(payload)
        elif kind == b"IEND":
            break

    if width is None or height is None:
        raise ValueError(f"{path} is missing IHDR")
    if bit_depth != 8 or color_type != 6 or interlace != 0:
        raise ValueError(
            f"{path} must be non-interlaced 8-bit RGBA PNG; "
            f"got bit_depth={bit_depth}, color_type={color_type}, interlace={interlace}"
        )

    raw = zlib.decompress(b"".join(idat))
    bpp = 4
    stride = width * bpp
    rows: list[bytearray] = []
    prev = bytearray(stride)
    i = 0

    for _y in range(height):
        filter_type = raw[i]
        i += 1
        encoded = bytearray(raw[i : i + stride])
        i += stride
        row = bytearray(stride)

        for x in range(stride):
            left = row[x - bpp] if x >= bpp else 0
            up = prev[x]
            up_left = prev[x - bpp] if x >= bpp else 0
            value = encoded[x]

            if filter_type == 0:
                out = value
            elif filter_type == 1:
                out = (value + left) & 255
            elif filter_type == 2:
                out = (value + up) & 255
            elif filter_type == 3:
                out = (value + ((left + up) >> 1)) & 255
            elif filter_type == 4:
                p = left + up - up_left
                pa = abs(p - left)
                pb = abs(p - up)
                pc = abs(p - up_left)
                predictor = left if pa <= pb and pa <= pc else up if pb <= pc else up_left
                out = (value + predictor) & 255
            else:
                raise ValueError(f"{path} has unsupported PNG filter {filter_type}")

            row[x] = out

        rows.append(row)
        prev = row

    return width, height, rows


def write_png_rgba(path: Path, width: int, height: int, rows: list[bytearray]) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(kind)
        crc = zlib.crc32(payload, crc)
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc & 0xFFFFFFFF)

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter type 0
        raw.extend(row)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    encoded = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def crop_rows(rows: list[bytearray], box: tuple[int, int, int, int]) -> tuple[int, int, list[bytearray]]:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    cropped: list[bytearray] = []
    for y in range(top, bottom):
        row = rows[y]
        cropped.append(bytearray(row[left * 4 : right * 4]))
    return width, height, cropped


def is_edge_background_pixel(row: bytearray, x: int) -> bool:
    i = x * 4
    r, g, b, a = row[i], row[i + 1], row[i + 2], row[i + 3]
    if a <= 16:
        return True
    # Some user-provided PNGs contain baked checkerboard remnants. Remove only
    # low-saturation white/gray regions that are connected to the crop edge, so
    # interior eye whites and highlights are preserved.
    if min(r, g, b) >= 180 and (max(r, g, b) - min(r, g, b)) <= 35:
        return True
    return False


def remove_edge_connected_light_background(width: int, height: int, rows: list[bytearray]) -> None:
    queue: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.pop()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        key = (x, y)
        if key in seen:
            continue
        seen.add(key)

        if not is_edge_background_pixel(rows[y], x):
            continue

        i = x * 4
        rows[y][i : i + 4] = b"\x00\x00\x00\x00"
        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))


def pad_to_square(width: int, height: int, rows: list[bytearray]) -> tuple[int, list[bytearray]]:
    size = max(width, height)
    x_offset = (size - width) // 2
    y_offset = (size - height) // 2
    square = [bytearray(size * 4) for _ in range(size)]

    for y, row in enumerate(rows):
        dest = square[y + y_offset]
        start = x_offset * 4
        dest[start : start + width * 4] = row

    return size, square


def sample(rows: list[bytearray], size: int, x: int, y: int) -> tuple[int, int, int, int]:
    x = max(0, min(size - 1, x))
    y = max(0, min(size - 1, y))
    row = rows[y]
    i = x * 4
    return row[i], row[i + 1], row[i + 2], row[i + 3]


def resize_rgba_premultiplied(rows: list[bytearray], source_size: int, target_size: int) -> list[bytearray]:
    out_rows: list[bytearray] = []
    scale = source_size / target_size

    for y_out in range(target_size):
        src_y = (y_out + 0.5) * scale - 0.5
        y0 = int(src_y)
        y1 = y0 + 1
        wy = src_y - y0
        row = bytearray(target_size * 4)

        for x_out in range(target_size):
            src_x = (x_out + 0.5) * scale - 0.5
            x0 = int(src_x)
            x1 = x0 + 1
            wx = src_x - x0

            weights = (
                ((1 - wx) * (1 - wy), x0, y0),
                (wx * (1 - wy), x1, y0),
                ((1 - wx) * wy, x0, y1),
                (wx * wy, x1, y1),
            )

            alpha = 0.0
            red = green = blue = 0.0

            for weight, sx, sy in weights:
                r, g, b, a = sample(rows, source_size, sx, sy)
                af = a / 255.0
                alpha += weight * a
                red += weight * r * af
                green += weight * g * af
                blue += weight * b * af

            i = x_out * 4
            if alpha <= 0:
                row[i : i + 4] = b"\x00\x00\x00\x00"
            else:
                af = alpha / 255.0
                row[i] = max(0, min(255, round(red / af)))
                row[i + 1] = max(0, min(255, round(green / af)))
                row[i + 2] = max(0, min(255, round(blue / af)))
                row[i + 3] = max(0, min(255, round(alpha)))

        out_rows.append(row)

    return out_rows


def alpha_bbox(rows: list[bytearray], width: int, height: int) -> tuple[int, int, int, int] | None:
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1
    for y, row in enumerate(rows):
        for x in range(width):
            if row[x * 4 + 3] > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < 0:
        return None
    return min_x, min_y, max_x, max_y


def alpha_extrema(rows: list[bytearray]) -> tuple[int, int]:
    values = [row[i + 3] for row in rows for i in range(0, len(row), 4)]
    return min(values), max(values)


def transparent_corners(rows: list[bytearray], width: int, height: int) -> bool:
    coords = ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))
    return all(rows[y][x * 4 + 3] == 0 for x, y in coords)


def edge_risk(rows: list[bytearray], width: int, height: int) -> tuple[int, int, int]:
    opaque = near_white = near_black = 0
    coords = []
    coords.extend((x, 0) for x in range(width))
    coords.extend((x, height - 1) for x in range(width))
    coords.extend((0, y) for y in range(height))
    coords.extend((width - 1, y) for y in range(height))

    for x, y in coords:
        row = rows[y]
        i = x * 4
        r, g, b, a = row[i], row[i + 1], row[i + 2], row[i + 3]
        if a > 16:
            opaque += 1
            if r > 240 and g > 240 and b > 240:
                near_white += 1
            if r < 16 and g < 16 and b < 16:
                near_black += 1
    return opaque, near_white, near_black


def render_size_80(width: int, height: int) -> tuple[float, float]:
    scale = min(80 / width, 80 / height)
    return width * scale, height * scale


def normalize(spec: CropSpec) -> dict[str, object]:
    source_path = EXPRESSIONS / spec.source
    out_path = CANDIDATES / spec.output
    source_w, source_h, rows = read_png_rgba(source_path)
    left, top, right, bottom = spec.box
    if left < 0 or top < 0 or right > source_w or bottom > source_h:
        raise ValueError(f"{spec.source} crop {spec.box} outside source {source_w}x{source_h}")

    crop_w, crop_h, cropped = crop_rows(rows, spec.box)
    remove_edge_connected_light_background(crop_w, crop_h, cropped)
    square_size, square = pad_to_square(crop_w, crop_h, cropped)
    resized = resize_rgba_premultiplied(square, square_size, TARGET)
    write_png_rgba(out_path, TARGET, TARGET, resized)

    bbox = alpha_bbox(resized, TARGET, TARGET)
    alpha_min, alpha_max = alpha_extrema(resized)
    opaque_edge, near_white_edge, near_black_edge = edge_risk(resized, TARGET, TARGET)
    render_w, render_h = render_size_80(TARGET, TARGET)

    return {
        "mood": spec.mood,
        "source": spec.source,
        "output": spec.output,
        "source_size": f"{source_w}x{source_h}",
        "crop": f"x{left}-y{top} to x{right - 1}-y{bottom - 1}",
        "candidate_size": f"{TARGET}x{TARGET}",
        "alpha": f"min {alpha_min} / max {alpha_max}",
        "bbox": None if bbox is None else f"x{bbox[0]}-y{bbox[1]} to x{bbox[2]}-y{bbox[3]}",
        "transparent_corners": transparent_corners(resized, TARGET, TARGET),
        "edge": (
            f"opaque edge {opaque_edge}, near-white {near_white_edge}, "
            f"near-black {near_black_edge}"
        ),
        "render_80": f"{render_w:.1f}x{render_h:.1f}",
        "bytes": out_path.stat().st_size,
        "note": spec.note,
    }


def main() -> None:
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    rows = [normalize(spec) for spec in CROPS]

    print("TASK-093 Christina expression normalization candidates")
    for row in rows:
        print(
            f"- {row['mood']}: {row['output']} | {row['candidate_size']} | "
            f"{row['alpha']} | {row['bbox']} | {row['render_80']} | "
            f"{row['bytes']} bytes"
        )


if __name__ == "__main__":
    main()
