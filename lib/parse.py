"""Pure parsers for beerfetch.

No subprocess calls here — all functions take raw string input so they
are fully unit-testable without hardware.
"""

import json
import shlex


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


def _split_lspci_mm(line):
    """Split an ``lspci -mm`` line respecting ITS quoting convention.

    lspci -mm quotes fields with double quotes only; it never uses single
    quotes as a quote character. shlex.split's default POSIX mode treats a
    bare apostrophe (e.g. inside a vendor name) as starting an unterminated
    quoted string and raises — restricting the lexer to '"' avoids that.
    """
    lex = shlex.shlex(line, posix=True)
    lex.whitespace_split = True
    lex.quotes = '"'
    return list(lex)


def parse_lspci(lspci_mm):
    """Parse ``lspci -mm`` output into GPU and Wi-Fi entries.

    Args:
        lspci_mm: stdout of ``lspci -mm``

    Returns:
        {
            "gpu":  [str, ...],   # vendor + device strings, one per GPU found
            "wifi": str | None,   # first Network controller found, or None
        }
    """
    gpus = []
    wifi = None
    for line in lspci_mm.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parts = _split_lspci_mm(line)
        except ValueError:
            continue
        if len(parts) < 4:
            continue
        cls, vendor, device = parts[1], parts[2], parts[3]
        label = f"{vendor} {device}".strip()
        if any(k in cls for k in ("VGA", "3D", "Display")):
            gpus.append(label)
        elif "Network controller" in cls and wifi is None:
            wifi = label
    return {"gpu": gpus, "wifi": wifi}
