#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "frames.json" ]; then
  echo "frames.json not found. Run: python3 build_frames.py"
  exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

pyinstaller \
  --onefile \
  --add-data "frames.json:." \
  --add-data "index.html:." \
  --add-data "geogebra.html:." \
  --name "app_desmos" \
  app_desmos.py

pyinstaller \
  --onefile \
  --add-data "frames.json:." \
  --add-data "index.html:." \
  --add-data "geogebra.html:." \
  --name "app_geogebra" \
  app_geogebra.py

echo "Built dist/app_desmos"
echo "Built dist/app_geogebra"
