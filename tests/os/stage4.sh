#!/bin/sh
# Stage 4: all modes of ls, cd, clear, echo, who and their errors.
cd "$(dirname "$0")/../.." || exit 1
EMU="python3 src/main.py --headless --vfs examples/vfs/deep"
failed=0
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

echo "== full script with all command modes =="
$EMU --script examples/scripts/stage4.emu || failed=1
echo

# Every wrong command must stop the script with a non-zero exit code.
for line in "ls /nope" "ls -z" "ls a b" "cd /nope" "cd motd" "cd a b" \
            "clear x" "who x"; do
    echo "== error case: $line =="
    echo "$line" > "$TMP"
    $EMU --script "$TMP"
    code=$?
    echo "exit code: $code (expected 1)"
    echo
    [ "$code" -eq 1 ] || failed=1
done

[ "$failed" -eq 0 ] && echo "ALL OK" || echo "SOME CHECKS FAILED"
exit "$failed"
