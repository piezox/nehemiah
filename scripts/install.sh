#!/usr/bin/env bash
# Copy the core and case files into a project and point its AGENTS.md at them (#4).
# Usage: scripts/install.sh <project-dir>
# Refuses to overwrite an existing <project-dir>/nehemiah/; remove it to reinstall.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:?usage: install.sh <project-dir>}"
dest="$target/nehemiah"
pointer='Read `nehemiah/core/core.md` now. It is the always-on core of this project'"'"'s steering, and it applies to you while you work here. Its router table names files in `cases/`; they are in `nehemiah/cases/`.'

if [ -e "$dest" ]; then
  echo "$dest already exists (installed at $(cat "$dest/VERSION" 2>/dev/null || echo 'unknown')). Remove it to reinstall." >&2
  exit 1
fi

sha="$(git -C "$root" rev-parse HEAD)"
changes="none"
git -C "$root" diff --quiet HEAD -- core cases || changes="uncommitted changes to core/ or cases/"

mkdir -p "$dest"
cp -R "$root/core" "$root/cases" "$dest/"
echo "$sha" > "$dest/VERSION"

if ! grep -qsF 'nehemiah/core/core.md' "$target/AGENTS.md"; then
  [ -s "$target/AGENTS.md" ] && echo >> "$target/AGENTS.md"
  echo "$pointer" >> "$target/AGENTS.md"
fi

echo "Installed nehemiah $sha into $dest and pointed $target/AGENTS.md at it."
echo "Publish this line where users of the system can see it (CONTESTING.md):"
echo "  This system is steered by nehemiah (https://github.com/piezox/nehemiah) at commit \`$sha\`, with the following local changes: $changes."
