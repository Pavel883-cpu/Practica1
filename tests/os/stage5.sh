#!/bin/sh
# Stage 5: rm and mv, their modes, errors and "memory only" guarantee.
cd "$(dirname "$0")/../.." || exit 1
EMU="python3 src/main.py --headless"
failed=0
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

echo "== mv and rm on the multi-file VFS =="
$EMU --vfs examples/vfs/multi --script examples/scripts/stage5.emu || failed=1
echo
echo "== directories on the deep VFS =="
$EMU --vfs examples/vfs/deep --script examples/scripts/stage5_deep.emu \
    || failed=1
echo

echo "== the files on the disk are still in place =="
for f in examples/vfs/multi/words.txt examples/vfs/multi/notes.txt \
         examples/vfs/multi/motd examples/vfs/deep/projects/lib/readme.txt; do
    [ -f "$f" ] && echo "ok: $f" || { echo "MISSING: $f"; failed=1; }
done
echo

for line in "rm" "rm nope" "rm dir" "rm -r /" "mv" "mv notes.txt" \
            "mv a b c" "mv nope x" "mv notes.txt nope/x"; do
    echo "== error case: $line =="
    echo "$line" > "$TMP"
    $EMU --vfs examples/vfs/multi --script "$TMP"
    code=$?
    echo "exit code: $code (expected 1)"
    echo
    [ "$code" -eq 1 ] || failed=1
done

[ "$failed" -eq 0 ] && echo "ALL OK" || echo "SOME CHECKS FAILED"
exit "$failed"
