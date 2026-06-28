"""Tests for lib/parse.py — all run without hardware."""

from lib.parse import parse_sysinfo, parse_lspci

LSCPU = (
    '{"lscpu":['
    '{"field":"Architecture:","data":"x86_64"},'
    '{"field":"Model name:","data":"Intel(R) Core(TM) i5-8500T CPU @ 2.10GHz"},'
    '{"field":"CPU(s):","data":"6"}'
    ']}'
)
LSCPU_NESTED = (
    '{"lscpu":['
    '{"field":"Architecture:","data":"x86_64","children":[{"field":"CPU(s):","data":"4"}]},'
    '{"field":"Model name:","data":"AMD Ryzen 3"}'
    ']}'
)
MEMINFO = "MemTotal:       16264920 kB\nMemFree:        100 kB\n"
LSBLK = (
    '{"blockdevices":['
    '{"name":"sda","size":"238.5G","type":"disk","model":"Samsung SSD 860",'
    '"children":[{"name":"sda1","size":"512M","type":"part"}]},'
    '{"name":"sr0","size":"1024M","type":"rom"}'
    ']}'
)


def test_cpu_basic():
    s = parse_sysinfo(LSCPU, MEMINFO, LSBLK, True)
    assert s["cpu"]["model"] == "Intel(R) Core(TM) i5-8500T CPU @ 2.10GHz"
    assert s["cpu"]["logical"] == "6"
    assert s["cpu"]["arch"] == "x86_64"


def test_cpu_nested_fields():
    s = parse_sysinfo(LSCPU_NESTED, MEMINFO, LSBLK, True)
    assert s["cpu"]["logical"] == "4"
    assert s["cpu"]["model"] == "AMD Ryzen 3"


def test_mem_total_gib():
    s = parse_sysinfo(LSCPU, MEMINFO, LSBLK, True)
    assert s["mem"]["total"] == "15.5G"


def test_disks_whole_only_with_model():
    s = parse_sysinfo(LSCPU, MEMINFO, LSBLK, True)
    assert s["disks"] == [
        {"path": "/dev/sda", "size": "238.5G", "model": "Samsung SSD 860"}
    ]


def test_rom_excluded():
    s = parse_sysinfo(LSCPU, MEMINFO, LSBLK, True)
    paths = [d["path"] for d in s["disks"]]
    assert "/dev/sr0" not in paths


def test_firmware_uefi():
    assert parse_sysinfo(LSCPU, MEMINFO, LSBLK, True)["firmware"] == "UEFI"


def test_firmware_bios():
    assert parse_sysinfo(LSCPU, MEMINFO, LSBLK, False)["firmware"] == "BIOS"


def test_garbage_inputs_dont_raise():
    s = parse_sysinfo("not json", "", "{}", False)
    assert s["cpu"]["model"] == "unknown"
    assert s["mem"]["total"] == ""
    assert s["disks"] == []


def test_missing_model_is_empty_string():
    lsblk = '{"blockdevices":[{"name":"vda","size":"20G","type":"disk"}]}'
    s = parse_sysinfo(LSCPU, MEMINFO, lsblk, False)
    assert s["disks"] == [{"path": "/dev/vda", "size": "20G", "model": ""}]


def test_multiple_disks():
    lsblk = (
        '{"blockdevices":['
        '{"name":"sda","size":"238.5G","type":"disk","model":"SAMSUNG MZ7LN256"},'
        '{"name":"sdb","size":"931.5G","type":"disk","model":"ST1000LM035"}'
        ']}'
    )
    s = parse_sysinfo(LSCPU, MEMINFO, lsblk, True)
    assert len(s["disks"]) == 2
    assert s["disks"][1]["path"] == "/dev/sdb"


# --- parse_lspci ---

LSPCI_DISCRETE = """\
00:02.0 "VGA compatible controller" "Intel Corporation" "UHD Graphics 630" "Lenovo" "" "00"
01:00.0 "3D controller" "NVIDIA Corporation" "GM108M [GeForce 940MX]" "Lenovo" "" "a2"
02:00.0 "Network controller" "Intel Corporation" "Wireless 8265 / 8275" "Intel Corporation" "" "78"
03:00.0 "Ethernet controller" "Realtek Semiconductor" "RTL8111" "" "" "15"
"""

LSPCI_INTEGRATED_ONLY = """\
00:02.0 "VGA compatible controller" "Intel Corporation" "HD Graphics 620" "" "" "07"
01:00.0 "Ethernet controller" "Realtek Semiconductor" "RTL8111" "" "" "15"
"""

LSPCI_NO_WIFI = """\
00:02.0 "VGA compatible controller" "AMD" "Radeon RX 6600" "" "" "00"
01:00.0 "Ethernet controller" "Realtek Semiconductor" "RTL8111" "" "" "15"
"""

LSPCI_MULTI_GPU = """\
00:02.0 "VGA compatible controller" "Intel Corporation" "UHD Graphics 770" "" "" "00"
01:00.0 "Display controller" "AMD" "Radeon RX 7900 XTX" "" "" "00"
"""


def test_lspci_discrete_gpu():
    r = parse_lspci(LSPCI_DISCRETE)
    assert len(r["gpu"]) == 2
    assert "Intel Corporation UHD Graphics 630" in r["gpu"]
    assert "NVIDIA Corporation GM108M [GeForce 940MX]" in r["gpu"]


def test_lspci_integrated_only():
    r = parse_lspci(LSPCI_INTEGRATED_ONLY)
    assert r["gpu"] == ["Intel Corporation HD Graphics 620"]


def test_lspci_wifi_detected():
    r = parse_lspci(LSPCI_DISCRETE)
    assert r["wifi"] == "Intel Corporation Wireless 8265 / 8275"


def test_lspci_no_wifi():
    r = parse_lspci(LSPCI_NO_WIFI)
    assert r["wifi"] is None


def test_lspci_ethernet_excluded_from_wifi():
    r = parse_lspci(LSPCI_INTEGRATED_ONLY)
    assert r["wifi"] is None


def test_lspci_multiple_gpus():
    r = parse_lspci(LSPCI_MULTI_GPU)
    assert len(r["gpu"]) == 2
    assert any("Radeon" in g for g in r["gpu"])


def test_lspci_empty_input():
    r = parse_lspci("")
    assert r["gpu"] == []
    assert r["wifi"] is None


def test_lspci_garbage_input():
    r = parse_lspci("not lspci output\x00\nbinary junk")
    assert r["gpu"] == []
    assert r["wifi"] is None
