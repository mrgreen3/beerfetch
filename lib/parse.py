"""Pure parsers for beerfetch.

No subprocess calls here — all functions take raw string input so they
are fully unit-testable without hardware.
"""

import json


def parse_sysinfo(lscpu_json, meminfo, lsblk_json, uefi):
    """Build a system-overview dict from raw command output.

    Args:
        lscpu_json: stdout of ``lscpu -J``
        meminfo:    contents of ``/proc/meminfo``
        lsblk_json: stdout of ``lsblk -J -o NAME,SIZE,TYPE,MODEL``
        uefi:       bool — True if /sys/firmware/efi is present

    Returns:
        {
            "cpu":      {"model": str, "logical": str, "arch": str},
            "mem":      {"total": str},   # e.g. "15.5G"
            "disks":    [{"path": str, "size": str, "model": str}],
            "firmware": "UEFI" | "BIOS",
        }
    """
    # --- CPU ---
    fields = {}

    def walk_cpu(node):
        f = node.get("field", "").rstrip(":")
        if f:
            fields[f] = node.get("data", "")
        for child in node.get("children", []):
            walk_cpu(child)

    try:
        for node in json.loads(lscpu_json).get("lscpu", []):
            walk_cpu(node)
    except (ValueError, AttributeError):
        pass

    cpu = {
        "model":   fields.get("Model name", "unknown"),
        "logical": fields.get("CPU(s)", ""),
        "arch":    fields.get("Architecture", ""),
    }

    # --- Memory ---
    total = ""
    for line in meminfo.splitlines():
        if line.startswith("MemTotal:"):
            try:
                total = f"{int(line.split()[1]) / (1024 * 1024):.1f}G"
            except (IndexError, ValueError):
                pass
            break

    # --- Drives (whole disks only) ---
    disks = []
    try:
        for dev in json.loads(lsblk_json).get("blockdevices", []):
            if dev.get("type") == "disk":
                disks.append({
                    "path":  "/dev/" + dev["name"],
                    "size":  dev.get("size", ""),
                    "model": (dev.get("model") or "").strip(),
                })
    except (ValueError, AttributeError):
        pass

    return {
        "cpu":      cpu,
        "mem":      {"total": total},
        "disks":    disks,
        "firmware": "UEFI" if uefi else "BIOS",
    }
