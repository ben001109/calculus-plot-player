import re
import subprocess
from PIL import Image
import numpy as np


def png_to_np_array(filename):
    img = Image.open(filename)
    data = np.array(img.getdata()).reshape(img.size[0], img.size[1], 3)
    bindata = np.zeros((img.size[0], img.size[1]), np.uint32)
    for i, row in enumerate(data):
        for j, byte in enumerate(row):
            bindata[i, j] = 1 if sum(byte) < 125*3 else 0
    return bindata

def png_to_svg(filename):
    img = Image.open(filename).convert("L")
    width, height = img.size
    pixels = list(img.getdata())
    lines = [f"P2\n{width} {height}\n255\n"]
    threshold = 127
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        row_vals = ["0" if v < threshold else "255" for v in row]
        lines.append(" ".join(row_vals) + "\n")
    pgm = "".join(lines).encode("ascii")
    proc = subprocess.run(
        ["potrace", "-s", "-o", "-"],
        input=pgm,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return proc.stdout.decode("utf-8", errors="replace")

svg_text = png_to_svg('pngs/png500.png')
path_count = len(re.findall(r'<path[^>]*d="([^"]+)"', svg_text))
print("paths:", path_count)
