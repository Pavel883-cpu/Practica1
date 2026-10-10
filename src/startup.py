"""Startup sequence shared by the graphical and the headless modes."""

from config import format_debug
from script import (STATUS_ERROR, STATUS_OK, ScriptError, read_script,
                    run_script)


def startup(ui, shell, config, problems=()):
    """Show debug output, report problems and run the startup script.

    Returns the status of the script (see script.py) or STATUS_ERROR
    when something went wrong before the script was started.
    """
    for line in format_debug(config):
        ui.emit(line)
    status = STATUS_OK
    for problem in problems:
        ui.emit(problem, True)
        status = STATUS_ERROR
    if not config.script:
        return status
    try:
        lines = read_script(config.script)
    except ScriptError as error:
        ui.emit(str(error), True)
        return STATUS_ERROR
    return run_script(shell, lines, ui)
