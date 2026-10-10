#!/bin/sh
# Stage 3: different VFS variants, motd and load errors.
cd "$(dirname "$0")/../.." || exit 1
EMU="python3 src/main.py --headless"
failed=0

check() {
    expected="$1"; shift
    echo "\$ $*"
    "$@"
    code=$?
    echo "exit code: $code (expected $expected)"
    echo
    [ "$code" -eq "$expected" ] || failed=1
}

echo "== minimal VFS =="
check 0 $EMU --vfs examples/vfs/minimal
echo "== several files, motd is shown =="
check 0 $EMU --vfs examples/vfs/multi
echo "== 4 levels of folders, motd is shown =="
check 0 $EMU --vfs examples/vfs/deep
echo "== default VFS (no --vfs) =="
check 0 $EMU
echo "== stage 3 script on the deep VFS (stops at the error) =="
check 1 $EMU --vfs examples/vfs/deep --script examples/scripts/stage3.emu
echo "== VFS directory does not exist =="
check 1 $EMU --vfs examples/vfs/does-not-exist
echo "== VFS path is a file, not a directory =="
check 1 $EMU --vfs README.md

[ "$failed" -eq 0 ] && echo "ALL OK" || echo "SOME CHECKS FAILED"
exit "$failed"
