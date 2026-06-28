# beerfetch 🍺

A lightweight standalone system information tool for FruitBang and Arch-based systems.
Served locally via a minimal HTTP server and viewed in any browser.

```
CPU       Intel(R) Core(TM) i5-8500T · 6 logical · x86_64
Memory    15.5G
Drives    /dev/sda  238.5G  SAMSUNG MZ7LN256
          /dev/sdb  931.5G  ST1000LM035-1RK172
Firmware  UEFI
```

## Overview

beerfetch probes the local machine (lscpu, /proc/meminfo, lsblk) and serves a
clean browser-based overview on localhost. No external dependencies beyond Python
and the standard library. Icons are inline SVG — no font dependencies.

Inspired by neofetch/fastfetch but browser-based and built around FruitBang's
visual identity.

## Usage

```bash
python main.py
# then open http://localhost:7778
```

## Live view

beerfetch also serves an ambient live view at `http://localhost:7778/live`: a
single CPU bar that warms from cool through gold to hot as load climbs. It polls
`/api/live` (CPU utilisation as a 0..1 value, sampled from `/proc/stat`) once a
second and eases between samples so it glides rather than jumps. This is the
first step toward a fuller ambient display driven by live system state.

## Structure

```
beerfetch/
├── main.py          # entry point — starts the server and opens the browser
├── lib/
│   ├── parse.py     # pure parsers + cpu_load delta (unit-testable, no subprocess)
│   ├── system.py    # subprocess wrappers (lscpu, lsblk, /proc/meminfo, /proc/stat)
│   ├── server.py    # minimal HTTP server + /api/sysinfo, /api/live, /live
│   ├── ui.py        # static HTML/CSS/JS sysinfo panel
│   └── live.py      # ambient CPU-bar view
└── tests/
    ├── test_sysinfo.py
    └── test_live.py
```

## Requirements

- Python 3.8+
- Arch Linux / FruitBang (or any system with lscpu and lsblk)

## License

MIT
