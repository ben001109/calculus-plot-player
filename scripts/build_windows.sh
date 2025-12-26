#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "frames.json" ]; then
  echo "frames.json not found. Run: python3 build_frames.py"
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install pyinstaller

SEP=":"
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) SEP=";" ;;
esac

pyinstaller \
  --onefile \
  --add-data "frames.json${SEP}." \
  --add-data "index.html${SEP}." \
  --add-data "geogebra.html${SEP}." \
  --name "app_desmos" \
  app_desmos.py

pyinstaller \
  --onefile \
  --add-data "frames.json${SEP}." \
  --add-data "index.html${SEP}." \
  --add-data "geogebra.html${SEP}." \
  --name "app_geogebra" \
  app_geogebra.py

echo "Built dist/app_desmos.exe"
echo "Built dist/app_geogebra.exe"
