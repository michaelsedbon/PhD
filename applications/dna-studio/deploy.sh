#!/bin/bash
# Build → self-contained bundle → install to /Applications.
# Handles the pieces macdeployqt gets wrong for this app: a few helper dylibs it
# fails to resolve, and the QtWebEngineProcess helper's Qt deps. Signs ad-hoc and
# signs the /Applications copy LAST (so the copy doesn't invalidate the seal).
#
# Usage:  ./deploy.sh
set -e
cd "$(dirname "$0")"
QT=/opt/homebrew/opt/qt
APP="build/DNA Studio.app"
DEST="/Applications/DNA Studio.app"

echo "▶ building…"
cmake -S . -B build -DCMAKE_PREFIX_PATH="$QT" >/dev/null
cmake --build build >/dev/null
echo "▶ bundling Qt (macdeployqt)…"
"$QT/bin/macdeployqt" "$APP" >/dev/null 2>&1 || true   # may error on the libs we fix below

FW="$APP/Contents/Frameworks"

echo "▶ copying helper dylibs macdeployqt misses…"
for lib in libwebp.7.dylib libsharpyuv.0.dylib libbrotlicommon.1.dylib \
           libbrotlidec.1.dylib libbrotlienc.1.dylib; do
  if [ ! -f "$FW/$lib" ]; then
    src=$(find /opt/homebrew/opt -name "$lib" 2>/dev/null | head -1)
    [ -n "$src" ] && cp -f "$src" "$FW/"
  fi
  chmod u+w "$FW/$lib" 2>/dev/null || true
  install_name_tool -id "@rpath/$lib" "$FW/$lib" 2>/dev/null || true
  otool -L "$FW/$lib" 2>/dev/null | awk 'NR>1{print $1}' | grep '/opt/homebrew' | while read dep; do
    install_name_tool -change "$dep" "@rpath/$(basename "$dep")" "$FW/$lib" 2>/dev/null || true
  done
done

echo "▶ fixing QtWebEngineProcess helper deps…"
HELPER_APP="$FW/QtWebEngineCore.framework/Versions/A/Helpers/QtWebEngineProcess.app"
HELPER="$HELPER_APP/Contents/MacOS/QtWebEngineProcess"
if [ -f "$HELPER" ]; then
  chmod u+w "$HELPER"
  install_name_tool -add_rpath "@executable_path/../../../../../../.." "$HELPER" 2>/dev/null || true
  otool -L "$HELPER" | awk 'NR>1{print $1}' | grep '/opt/homebrew' | while read dep; do
    install_name_tool -change "$dep" "@rpath/${dep##*/lib/}" "$HELPER" 2>/dev/null || true
  done
  # CRITICAL: the bundled Qt frameworks reference @executable_path/../Frameworks/… .
  # From the helper's own MacOS dir that path is wrong (ICU etc. live in the MAIN
  # app's Frameworks), so the renderer process crashes on launch → blank web views.
  # A Frameworks symlink in the helper bundle pointing at the main Frameworks fixes it.
  ln -sfn "../../../../../.." "$HELPER_APP/Contents/Frameworks"
fi

echo "▶ verifying self-contained…"
LEFT=$(find "$APP" -type f \( -name "*.dylib" -o -perm -u+x \) 2>/dev/null \
       | while read f; do otool -L "$f" 2>/dev/null | grep -q /opt/homebrew && echo x; done | wc -l | tr -d ' ')
echo "   external Homebrew refs: $LEFT"

echo "▶ installing to /Applications…"
ditto "$APP" "$DEST"

echo "▶ signing installed copy (ad-hoc)…"
codesign --force --deep --sign - "$DEST" >/dev/null 2>&1
codesign --verify --deep "$DEST" && echo "   signature OK"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DEST" 2>/dev/null || true

echo "✔ done → $DEST"
