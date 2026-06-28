"""Ambient live view for beerfetch.

A single CPU bar that warms cool -> gold -> hot with load, polling
/api/live once a second. Kept in its own module so the static sysinfo
panel (ui.py) stays untouched. Uses the same FruitBang palette.
"""

_LIVE_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>beerfetch \u00b7 cpu</title>
<style>
  html,body{margin:0;height:100%;background:#201b14;color:#c9c0b0;
    font:14px/1.5 ui-monospace,Menlo,Consolas,monospace;
    display:flex;align-items:center;justify-content:center;}
  .wrap{width:min(620px,86vw);}
  .label{display:flex;justify-content:space-between;align-items:baseline;
    letter-spacing:.18em;color:#8c8070;font-size:12px;margin:0 2px 11px;}
  .mark{color:#c9b890;font-weight:700;letter-spacing:.05em;}
  .track{height:26px;border-radius:13px;background:#161109;
    box-shadow:inset 0 1px 3px rgba(0,0,0,.6);overflow:hidden;}
  .fill{height:100%;width:0;border-radius:13px;}
  .foot{display:flex;justify-content:space-between;align-items:baseline;
    margin-top:11px;color:#8c8070;font-size:12px;}
  .foot a{color:#8c8070;text-decoration:none;}
  .foot a:hover{color:#c9b890;}
  #pct{font-variant-numeric:tabular-nums;}
  .off{color:#b5683f;}
</style></head>
<body>
  <div class="wrap">
    <div class="label"><span><span class="mark">^!</span>&nbsp;&nbsp;cpu</span>
      <span id="state"></span></div>
    <div class="track"><div class="fill" id="fill"></div></div>
    <div class="foot"><a href="/">&lsaquo; sysinfo</a><span id="pct">\u2014</span></div>
  </div>
<script>
  const fill=document.getElementById('fill'),
        pct=document.getElementById('pct'),
        state=document.getElementById('state');
  let cur=0, tgt=0, ok=false, last=performance.now();

  // cool -> gold -> hot, driven by load
  const stops=[[0,[92,140,112]],[0.5,[201,184,144]],[0.8,[208,120,66]],[1,[200,70,55]]];
  function ramp(v){
    let a=stops[0], b=stops[stops.length-1];
    for(let i=0;i<stops.length-1;i++){
      if(v>=stops[i][0]&&v<=stops[i+1][0]){a=stops[i];b=stops[i+1];break;}
    }
    const k=(v-a[0])/((b[0]-a[0])||1);
    const c=a[1].map((ch,i)=>Math.round(ch+(b[1][i]-ch)*k));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }
  async function poll(){
    try{
      const d=await (await fetch('/api/live')).json();
      if(!d.ok) throw 0;
      tgt=Math.max(0,Math.min(1,d.cpu)); ok=true;
      state.textContent=''; state.className='';
    }catch(e){ ok=false; state.textContent='offline'; state.className='off'; }
  }
  function frame(now){
    const dt=(now-last)/1000; last=now;
    cur += (tgt-cur)*(1-Math.exp(-dt/0.9));      // glide between 1s polls
    const c=ramp(cur);
    fill.style.width=(cur*100).toFixed(1)+'%';
    fill.style.background=c;
    fill.style.boxShadow=`0 0 ${Math.round(cur*24)}px ${c}`;  // warmer = glowier
    pct.textContent = ok ? Math.round(cur*100)+'%' : '\u2014';
    requestAnimationFrame(frame);
  }
  poll(); setInterval(poll,1000); requestAnimationFrame(frame);
</script>
</body></html>"""


def render_live_page():
    """Return the ambient CPU-bar HTML page."""
    return _LIVE_PAGE
