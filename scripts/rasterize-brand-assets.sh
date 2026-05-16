#!/usr/bin/env bash
# Rasterize the green-branded SVG sources into every PNG the site references.
# Run this once after editing static/favicon.svg or static/assets/og-image.svg.
#
# Install ONE of these rasterizers first (pick whichever you like):
#   brew install librsvg     # fastest, smallest install, recommended
#   brew install imagemagick # also works
#   brew install --cask inkscape   # heaviest, also works
#
# Outputs (all under static/):
#   apple-touch-icon.png        180x180  (Apple home-screen)
#   assets/icon-192.png         192x192  (PWA standard)
#   assets/icon-512.png         512x512  (PWA hi-res / splash)
#   assets/og-image.png         1200x630 (social previews)
#
# favicon.ico is NOT regenerated here — modern browsers prefer the SVG link
# tag already present. If you want a fresh .ico, run:
#   magick assets/icon-192.png -define icon:auto-resize=16,32,48 favicon.ico

set -euo pipefail
cd "$(dirname "$0")/.."
SRC_ICON="static/favicon.svg"
SRC_OG="static/assets/og-image.svg"

# --- detect rasterizer ---
RASTER=""
if command -v rsvg-convert >/dev/null 2>&1; then
  RASTER="rsvg"
elif command -v magick >/dev/null 2>&1; then
  RASTER="magick"
elif command -v convert >/dev/null 2>&1; then
  RASTER="convert"
elif command -v inkscape >/dev/null 2>&1; then
  RASTER="inkscape"
else
  cat >&2 <<'EOF'
No SVG rasterizer found. Install one of:
  brew install librsvg     # recommended
  brew install imagemagick
  brew install --cask inkscape
Then re-run scripts/rasterize-brand-assets.sh
EOF
  exit 1
fi
echo "Using rasterizer: $RASTER"

render() {
  local src="$1" out="$2" w="$3" h="$4"
  case "$RASTER" in
    rsvg)
      rsvg-convert -w "$w" -h "$h" "$src" -o "$out"
      ;;
    magick)
      magick -background none -density 384 "$src" -resize "${w}x${h}" "$out"
      ;;
    convert)
      convert -background none -density 384 "$src" -resize "${w}x${h}" "$out"
      ;;
    inkscape)
      inkscape --export-type=png --export-filename="$out" -w "$w" -h "$h" "$src"
      ;;
  esac
  echo "  wrote $out ($(wc -c < "$out") bytes)"
}

echo "Rendering icon PNGs from $SRC_ICON ..."
render "$SRC_ICON" "static/apple-touch-icon.png"    180 180
render "$SRC_ICON" "static/assets/icon-192.png"     192 192
render "$SRC_ICON" "static/assets/icon-512.png"     512 512

echo "Rendering OG image from $SRC_OG ..."
render "$SRC_OG"   "static/assets/og-image.png"     1200 630

echo
echo "Done. Re-run the build to copy the new PNGs into site/:"
echo "  .venv/bin/python build.py"
