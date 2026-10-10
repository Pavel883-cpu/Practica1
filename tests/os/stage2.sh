#!/bin/sh
# Stage 2: every command line parameter of the emulator.
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

echo "== no parameters =="
check 0 $EMU
echo "== --vfs only =="
check 0 $EMU --vfs examples/vfs/minimal
echo "== --script only =="
check 0 $EMU --script examples/scripts/stage2_ok.emu
echo "== --vfs and --script =="
check 0 $EMU --vfs examples/vfs/minimal --script examples/scripts/stage2_ok.emu
echo "== script stops at the first error =="
check 1 $EMU --script examples/scripts/stage2_error.emu
echo "== script file does not exist =="
check 1 $EMU --script examples/scripts/missing.emu

[ "$failed" -eq 0 ] && echo "ALL OK" || echo "SOME CHECKS FAILED"
exit "$failed"
