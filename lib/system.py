"""Subprocess wrappers for beerfetch.

Collects raw hardware data and returns the parsed overview dict.
Kept separate from parse.py so parsers stay unit-testable without hardware.
"""

import os
import subprocess

from .parse import parse_sysinfo, parse_lspci


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

    lspci = subprocess.run(
        ["lspci", "-mm"], capture_output=True, text=True
    ).stdout

    result = parse_sysinfo(lscpu, meminfo, lsblk, is_uefi())
    result.update(parse_lspci(lspci))
    return result


def read_cpu_sample():
    """Return (total_jiffies, idle_jiffies) from the aggregate /proc/stat line.

    The idle figure includes iowait. Returns None if /proc/stat cannot be
    read or parsed, so callers degrade to a calm reading rather than crash.
    """
    try:
        with open("/proc/stat") as f:
            vals = [int(x) for x in f.readline().split()[1:]]
    except (OSError, ValueError):
        return None
    if len(vals) < 4:
        return None
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    return sum(vals), idle
