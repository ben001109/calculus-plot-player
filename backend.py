import json
import os
import sys
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FRAMES = 5258
def _base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


FRAME_JSON = os.path.join(_base_dir(), "frames.json")

if os.path.exists(FRAME_JSON):
    with open(FRAME_JSON, "r", encoding="utf-8") as f:
        frame_coords = json.load(f)
else:
    frame_coords = None


@app.route('/')
def index():
    if frame_coords is None:
        return json.dumps({"error": "frames.json not found; run build_frames.py"}), 503
    # print(json.dumps(frame_coords))
    return json.dumps(frame_coords)


@app.route('/meta')
def meta():
    ready = 0 if frame_coords is None else len(frame_coords)
    return json.dumps({"total": FRAMES, "ready": ready})


if __name__ == "__main__":
    app.run()
