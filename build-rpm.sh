#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPDIR="$PROJECT_DIR/rpmbuild"
DISTDIR="$PROJECT_DIR/dist"
SPEC_FILE="$PROJECT_DIR/numberrace.spec"

MODE="ba"
if [[ "${1:-}" == "--srpm-only" || "${1:-}" == "-bs" ]]; then
    MODE="bs"
elif [[ "${1:-}" == "--clean" ]]; then
    rm -rf "$TOPDIR" "$DISTDIR"
    echo "Cleaned $TOPDIR and $DISTDIR"
    exit 0
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat <<EOF
Usage: $(basename "$0") [--srpm-only | --clean | --help]

Builds the Number Race RPM and SRPM inside the project directory:
  (no args)     Build both .noarch.rpm and .src.rpm into ./dist/
  --srpm-only   Build only .src.rpm (for Fedora COPR upload)
  --clean       Remove ./rpmbuild/ and ./dist/
EOF
    exit 0
fi

for cmd in rpmbuild; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is not installed. Run: sudo dnf install rpm-build" >&2
        exit 1
    fi
done

SOURCES=(
    "numberrace-installer-3.1.1-fr.jar"
    "extract-izpack.py"
    "numberrace.desktop"
    "numberrace.sh"
    "org.unicog.numberrace.metainfo.xml"
    "make-icons.py"
)

for src in "${SOURCES[@]}"; do
    if [[ ! -f "$PROJECT_DIR/$src" ]]; then
        echo "Error: missing source file: $PROJECT_DIR/$src" >&2
        exit 1
    fi
done

rm -rf "$TOPDIR" "$DISTDIR"
mkdir -p "$TOPDIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp} "$DISTDIR"

for src in "${SOURCES[@]}"; do
    cp -a "$PROJECT_DIR/$src" "$TOPDIR/SOURCES/"
done
cp -a "$SPEC_FILE" "$TOPDIR/SPECS/"

rpmbuild "-$MODE" \
    --define "_topdir $TOPDIR" \
    --define "_tmppath $TOPDIR/tmp" \
    "$TOPDIR/SPECS/numberrace.spec"

find "$TOPDIR/SRPMS" "$TOPDIR/RPMS" -type f -name '*.rpm' -exec cp -a {} "$DISTDIR/" \;

echo ""
echo "=== Build complete ==="
ls -lh "$DISTDIR"/*.rpm

if command -v rpmlint >/dev/null 2>&1; then
    echo ""
    echo "=== Running rpmlint ==="
    rpmlint "$SPEC_FILE" "$DISTDIR"/*.rpm || true
fi
