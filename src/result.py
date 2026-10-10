"""Result of executing one command."""

from dataclasses import dataclass


@dataclass
class Result:
    """Text output, error flag and requests to the interface."""

    output: str = ""
    error: bool = False
    exit: bool = False
    clear: bool = False


def fail(message):
    """Create an error result with the given message."""
    return Result(message, error=True)
