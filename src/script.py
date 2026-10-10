"""Execution of startup scripts with simulated dialog."""

STATUS_OK = "ok"
STATUS_ERROR = "error"
STATUS_EXIT = "exit"
COMMENT_MARK = "#"


class ScriptError(Exception):
    """The script file cannot be read."""


def read_script(path):
    """Return lines of the script file or raise ScriptError."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ScriptError(f"cannot read script '{path}': {error}") from error


def is_skipped(line):
    """Return True for blank lines and full-line comments."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_script(shell, lines, ui):
    """Execute script lines showing both input and output.

    Stops at the first failed command and reports its line number.
    Returns STATUS_OK, STATUS_ERROR or STATUS_EXIT.
    """
    for number, line in enumerate(lines, start=1):
        if is_skipped(line):
            continue
        ui.emit(shell.prompt() + line.strip())
        result = shell.execute(line)
        if result.clear:
            ui.clear()
        ui.emit(result.output, result.error)
        if result.error:
            ui.emit(f"script stopped: error in line {number}", True)
            return STATUS_ERROR
        if result.exit:
            return STATUS_EXIT
    return STATUS_OK
