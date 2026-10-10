"""Command line configuration of the emulator."""

import argparse
from dataclasses import dataclass
from typing import Optional

NOT_SET = "(not set)"


@dataclass
class Config:
    """Parameters given by the user at startup."""

    vfs: Optional[str] = None
    script: Optional[str] = None
    headless: bool = False

    def as_dict(self):
        """Return all parameters as an ordered key-value mapping."""
        return {
            "vfs": self.vfs or NOT_SET,
            "script": self.script or NOT_SET,
            "headless": str(self.headless).lower(),
        }


def build_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="main.py", description="UNIX shell emulator (variant 30)")
    parser.add_argument("--vfs", help="path to the physical VFS location")
    parser.add_argument("--script", help="path to the startup script")
    parser.add_argument(
        "--headless", action="store_true",
        help="run without a window: print everything to stdout")
    return parser


def parse_args(argv=None):
    """Parse command line arguments into a Config."""
    namespace = build_parser().parse_args(argv)
    return Config(namespace.vfs, namespace.script, namespace.headless)


def format_debug(config):
    """Return debug lines listing all parameters of the emulator."""
    return [f"[debug] {key} = {value}"
            for key, value in config.as_dict().items()]
