import json
import re
import subprocess
import time
from PIL import Image

FRAME_DIR = "frames"
FRAME_COUNT = 5258
OUTPUT = "frames.json"
SOURCE_WIDTH = 480
SOURCE_HEIGHT = 360
TARGET_WIDTH = 480
TARGET_HEIGHT = 360

_PATH_RE = re.compile(r'<path[^>]*d="([^"]+)"')
_TOKEN_RE = re.compile(r'[MmLlCcZz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')


def png_to_pgm_bytes(filename):
    img = Image.open(filename).convert("L")
    width, height = img.size
    pixels = list(img.getdata())

    lines = [f"P2\n{width} {height}\n255\n"]
    threshold = 127
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        row_vals = ["0" if v < threshold else "255" for v in row]
        lines.append(" ".join(row_vals) + "\n")
    return "".join(lines).encode("ascii")


def run_potrace_svg(pgm_bytes):
    proc = subprocess.run(
        ["potrace", "-s", "-o", "-"],
        input=pgm_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return proc.stdout.decode("utf-8", errors="replace")


def parse_svg_segments(svg_text):
    segments = []
    for match in _PATH_RE.finditer(svg_text):
        d = match.group(1)
        tokens = _TOKEN_RE.findall(d)
        idx = 0
        cmd = None
        current = None
        start_point = None
        while idx < len(tokens):
            token = tokens[idx]
            if re.match(r"[MmLlCcZz]", token):
                cmd = token
                idx += 1
                if cmd in ("Z", "z"):
                    if start_point and current and current != start_point:
                        segments.append(("L", current, start_point))
                        current = start_point
                    start_point = None
                    cmd = None
                    continue
            if cmd in ("M", "m"):
                x = float(tokens[idx])
                y = float(tokens[idx + 1])
                idx += 2
                if cmd == "m" and current:
                    x += current[0]
                    y += current[1]
                current = (x, y)
                start_point = current
                cmd = "L" if cmd == "M" else "l"
            elif cmd in ("L", "l"):
                x = float(tokens[idx])
                y = float(tokens[idx + 1])
                idx += 2
                if cmd == "l" and current:
                    x += current[0]
                    y += current[1]
                segments.append(("L", current, (x, y)))
                current = (x, y)
            elif cmd in ("C", "c"):
                x1 = float(tokens[idx])
                y1 = float(tokens[idx + 1])
                x2 = float(tokens[idx + 2])
                y2 = float(tokens[idx + 3])
                x3 = float(tokens[idx + 4])
                y3 = float(tokens[idx + 5])
                idx += 6
                if cmd == "c" and current:
                    x1 += current[0]
                    y1 += current[1]
                    x2 += current[0]
                    y2 += current[1]
                    x3 += current[0]
                    y3 += current[1]
                segments.append(("C", current, (x1, y1), (x2, y2), (x3, y3)))
                current = (x3, y3)
    return segments


def parse_svg_transform(svg_text):
    match = re.search(
        r'translate\(([^,]+),([^\)]+)\)\s*scale\(([^,]+),([^\)]+)\)',
        svg_text,
    )
    if not match:
        return 0.0, 0.0, 1.0, 1.0
    tx, ty, sx, sy = (float(match.group(i)) for i in range(1, 5))
    return tx, ty, sx, sy


def apply_transform(point, transform):
    x, y = point
    tx, ty, sx, sy = transform
    x = x * sx + tx
    y = y * sy + ty
    scale_x = TARGET_WIDTH / SOURCE_WIDTH
    scale_y = TARGET_HEIGHT / SOURCE_HEIGHT
    x *= scale_x
    y *= scale_y
    s = 1.0
    x = (x - TARGET_WIDTH / 2) * s + TARGET_WIDTH / 2
    y = (y - TARGET_HEIGHT / 2) * s + TARGET_HEIGHT / 2
    y = TARGET_HEIGHT - y
    return (x, y)


def segment_to_latex(segment, transform):
    if segment[0] == "L":
        (x0, y0) = apply_transform(segment[1], transform)
        (x1, y1) = apply_transform(segment[2], transform)
        return "((1-t)%f+t%f,(1-t)%f+t%f)" % (x0, x1, y0, y1)
    (x0, y0) = apply_transform(segment[1], transform)
    (x1, y1) = apply_transform(segment[2], transform)
    (x2, y2) = apply_transform(segment[3], transform)
    (x3, y3) = apply_transform(segment[4], transform)
    return (
        "((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),"
        "(1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))"
        % (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3)
    )


def main():
    all_frames = []
    start_time = time.time()
    for i in range(1, FRAME_COUNT + 1):
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = FRAME_COUNT - i
            eta = remaining / rate if rate > 0 else 0
            current_file = f"{FRAME_DIR}/frame{i}.png"
            print(
                f"progress {i}/{FRAME_COUNT} | {rate:.2f} frames/s | eta {eta:.0f}s | {current_file}",
                flush=True,
            )
        pgm = png_to_pgm_bytes(f"{FRAME_DIR}/frame{i}.png")
        svg_text = run_potrace_svg(pgm)
        transform = parse_svg_transform(svg_text)
        segments = parse_svg_segments(svg_text)
        latex = [segment_to_latex(seg, transform) for seg in segments]
        all_frames.append(latex)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_frames, f)


if __name__ == "__main__":
    main()
