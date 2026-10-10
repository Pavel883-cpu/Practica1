"""Parsing of input lines: splitting and environment variable expansion."""

import os
import re

ENV_PATTERN = re.compile(r"\$(?:(\w+)|\{(\w+)\})")


def expand_env(text, env=None):
    """Replace $VAR and ${VAR} in text by values of environment variables.

    Unknown variables are replaced by an empty string, like in a real shell.
    """
    source = os.environ if env is None else env

    def replace(match):
        name = match.group(1) or match.group(2)
        return source.get(name, "")

    return ENV_PATTERN.sub(replace, text)


def parse_line(line, env=None):
    """Split a line into a command name and a list of arguments.

    The line is split by whitespace, then every token is expanded.
    Tokens that become empty after expansion are dropped.
    """
    tokens = [expand_env(token, env) for token in line.split()]
    tokens = [token for token in tokens if token]
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]
