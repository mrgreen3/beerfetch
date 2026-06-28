"""HTML/CSS/JS panel for beerfetch.

render_page() returns the full page as a string.
Icons are inline SVG — no external font dependencies.
"""

_ICON_CPU = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <rect x="7" y="7" width="10" height="10" rx="1"/>
  <path d="M10 2v3M14 2v3M10 19v3M14 19v3M2 10h3M2 14h3M19 10h3M19 14h3"/>
</svg>"""

_ICON_MEM = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="7" width="20" height="10" rx="1"/>
  <path d="M6 17v2.5M10 17v2.5M14 17v2.5M18 17v2.5"/>
  <path d="M6 7v3M18 7v3"/>
</svg>"""

_ICON_DISK = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="12" cy="6" rx="8" ry="3"/>
  <path d="M4 6v12c0 1.6 3.6 3 8 3s8-1.4 8-3V6"/>
  <path d="M4 12c0 1.6 3.6 3 8 3s8-1.4 8-3"/>
</svg>"""

_ICON_GPU = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="4" width="20" height="13" rx="2"/>
  <path d="M8 21h8M12 17v4"/>
</svg>"""

_ICON_WIFI = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <path d="M2 8.5C5.8 4.8 9.6 3 12 3s6.2 1.8 10 5.5"/>
  <path d="M5.5 12c1.8-1.8 4-2.8 6.5-2.8s4.7 1 6.5 2.8"/>
  <path d="M9 15.5c.8-.8 1.9-1.3 3-1.3s2.2.5 3 1.3"/>
  <circle cx="12" cy="19" r="1.2" fill="#5bc4d4" stroke="none"/>
</svg>"""

_ICON_FW = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5bc4d4"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <rect x="5" y="5" width="14" height="14" rx="1.5"/>
  <circle cx="8.5" cy="8.5" r="1" fill="#5bc4d4" stroke="none"/>
  <path d="M2 9.5h3M2 14.5h3M19 9.5h3M19 14.5h3"/>
</svg>"""

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0f1923;
  color: #b8cfe0;
  font-family: monospace;
  max-width: 640px;
  margin: 40px auto;
  padding: 0 16px;
  line-height: 1.5;
}
h2 { color: #5bc4d4; margin-bottom: 12px; }
button {
  background: #5bc4d4;
  color: #0f1923;
  border: none;
  border-radius: 6px;
  padding: 10px 18px;
  font-family: monospace;
  font-size: 1em;
  cursor: pointer;
}
button:hover { background: #7ad4e4; }
.logo { text-align: center; margin-bottom: 24px; }
.section-lbl {
  color: #5bc4d4;
  font-size: .85em;
  margin: 14px 0 4px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.section-lbl svg { flex: none; }
.val { margin: 0 0 4px; }
.rule { border: none; border-top: 1px solid #253545; margin: 16px 0 12px; }
.muted { color: #4a6878; }
#status { color: #c05050; margin: 8px 0; min-height: 1.4em; }
"""

_JS = """
const esc = t => String(t == null ? '' : t)
  .replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

async function load() {
  const body = document.getElementById('sysinfo-body');
  const status = document.getElementById('status');
  body.textContent = 'Probing hardware\u2026';
  status.textContent = '';
  let d;
  try {
    const r = await fetch('/api/sysinfo');
    d = await r.json();
  } catch (e) {
    body.textContent = '';
    status.textContent = 'Could not reach /api/sysinfo: ' + e;
    return;
  }
  if (!d || !d.ok) {
    body.textContent = '';
    status.textContent = d?.error || 'Unknown error';
    return;
  }
  const s = d.sysinfo;
  const cpuLine = [s.cpu.model, s.cpu.logical && s.cpu.logical + ' logical', s.cpu.arch]
    .filter(Boolean).map(esc).join(' \xb7 ');
  const diskLines = s.disks.length
    ? s.disks.map(x => esc([x.path, x.size, x.model].filter(Boolean).join('  '))).join('<br>')
    : '<span class="muted">none detected</span>';
  const gpuLines = s.gpu && s.gpu.length
    ? s.gpu.map(esc).join('<br>')
    : '<span class="muted">none detected</span>';
  const wifiLine = s.wifi ? esc(s.wifi) : '<span class="muted">none detected</span>';
  body.innerHTML =
    LBCPU  + '<p class="val">' + (cpuLine || 'unknown') + '</p>' +
    LBMEM  + '<p class="val">' + (esc(s.mem.total) || 'unknown') + '</p>' +
    LBGPU  + '<p class="val">' + gpuLines + '</p>' +
    LBWIFI + '<p class="val">' + wifiLine + '</p>' +
    LBDISK + '<p class="val">' + diskLines + '</p>' +
    LBFW   + '<p class="val">' + esc(s.firmware) + '</p>';
}

window.addEventListener('DOMContentLoaded', load);
"""


def render_page():
    icon_labels = {
        "LBCPU":  f'<p class="section-lbl">{_ICON_CPU}CPU</p>',
        "LBMEM":  f'<p class="section-lbl">{_ICON_MEM}Memory</p>',
        "LBGPU":  f'<p class="section-lbl">{_ICON_GPU}GPU</p>',
        "LBWIFI": f'<p class="section-lbl">{_ICON_WIFI}Wi-Fi</p>',
        "LBDISK": f'<p class="section-lbl">{_ICON_DISK}Drives</p>',
        "LBFW":   f'<p class="section-lbl">{_ICON_FW}Firmware</p>',
    }
    # Inject icon label HTML as JS string constants so the fetch handler
    # can build the page without a template engine.
    js_consts = "\n".join(
        f'const {k} = {repr(v)};' for k, v in icon_labels.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>beerfetch</title>
<style>{_CSS}</style>
</head>
<body>
<div class="logo">
  <svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" viewBox="0 0 300 120">
    <rect width="300" height="120" rx="12" fill="#1a2d3d"/>
    <text x="150" y="70" text-anchor="middle" font-family="monospace" font-size="56"
          font-weight="bold" fill="#5bc4d4">^!</text>
    <text x="150" y="98" text-anchor="middle" font-family="monospace" font-size="15"
          fill="#b8cfe0" letter-spacing="5">System Information</text>
  </svg>
</div>
<div id="status"></div>
<div id="sysinfo-body">Loading\u2026</div>
<hr class="rule">
<button onclick="load()">Refresh</button>
</div>
<script>
{js_consts}
{_JS}
</script>
</body>
</html>"""
