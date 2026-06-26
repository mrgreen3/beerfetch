"""Subprocess wrappers for beerfetch.

Collects raw hardware data and returns the parsed overview dict.
Kept separate from parse.py so parsers stay unit-testable without hardware.
"""

import os
import subprocess

from .parse import parse_sysinfo


def is_uefi():
    """True if the system booted via UEFI."""
    return os.path.isdir("/sys/firmware/efi")


def collect_sysinfo():
    """Probe local hardware and return the parsed sysinfo dict."""
    lscpu = subprocess.run(
        ["lscpu", "-J"], capture_output=True, text=True
    ).stdout

    try:
        with open("/proc/meminfo") as f:
            meminfo = f.read()
    except OSError:
        meminfo = ""

    lsblk = subprocess.run(
        ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MODEL"],
        capture_output=True, text=True
    ).stdout

    return parse_sysinfo(lscpu, meminfo, lsblk, is_uefi())
