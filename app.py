import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Crazyfordito", page_icon="🎙️", layout="wide")

st.markdown(
    "<style>"
    ".main, .stApp { background-color: #0e1117; color: #ffffff; overflow: hidden; }"
    ".block-container { padding: 0 !important; max-width: 100% !important; }"
    "header, footer { display: none !important; }"
    "iframe { width: 100vw !important; height: 96vh !important; border: none !important; display: block; }"
    "</style>",
    unsafe_allow_html=True
)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Hiányzik a GEMINI_API_KEY!")
    st.stop()

KEY = st.secrets["GEMINI_API_KEY"]

HTML_LINES = [
    "<!DOCTYPE html><html><head><meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'>",
    "<style>",
    "*{box-sizing:border-box}",
    "body{background:#0e1117;color:#fff;font-family:sans-serif;margin:0;padding:10px;height:95vh;display:flex;flex-direction:column;gap:12px}",
    "h2{text-align:center;margin:0;font-size:26px;padding:4px 0}",
    ".row{display:flex;gap:14px;height:22vh;min-height:135px}",
    ".btn{flex:1;height:100%;border:3px solid #fff4;border-radius:24px;color:#fff;font-size:25px;font-weight:900;line-height:1.25}",
    ".go{background:#1b5e20} .stop{background:#b71c1c}",
    "#st{background:#161b22;border:2px solid #30363d;border-radius:18px;padding:18px;font-size:22px;font-weight:bold;text-align:center;color:#ffeb3b}",
    "#bar{height:16px;width:0%;background:#00e676;border-radius:8px;margin-top:12px;transition:width 0.1s}",
    "#list{flex:1;display:flex;flex-direction:column;gap:14px;overflow-y:auto}",
    ".box{background:#161b22;padding:24px;border-radius:22px;border:2px solid #30363d;flex:1;display:flex;flex-direction:column;justify-content:center}",
    ".lbl{color:#8b949e;font-size:18px;font-weight:bold;text-transform:uppercase}",
    ".orig{color:#fff;font-size:26px;font-weight:bold;margin:8px 0 22px 0;line-height:1.3}",
    ".tr{color:#58a6ff;font-size:32px;font-weight:900;margin-top:8px;line-height:1.3}",
    "</style></head><body>",
    "<h2>🎙️ Crazyfordító (HU ⇄ FR)</h2>",
    "<div class='row'>",
    "<button class='btn go' onclick='startRec()'>🟢 INDÍTÁS<br>DÉMARRER</button>",
    "<button class='btn stop' onclick='stopRec()'>🔴 LEÁLLÍTÁS<br>ARRÊTER</button>",
    "</div>",
    "<div id='st'><span id='txt'>⏹️ Nyomd meg a ZÖLD gombot!</span><div id='bar'></div></div>",
    "<div id='list'><div class='box' id='emp'><div class='lbl'>Eredeti / Original:</div><div class='orig'>Várakozás a beszédre...</div><div class='lbl'>Fordítás / Traduction:</div><div class='tr'>En attente de parole...</div></div></div>",
    "<script>",
    f"const KEY='{KEY}';",
    "const MODELS=['gemini-3.8-flash','gemini-3.6-flash','gemini-3.5-flash','gemini-3.5-flash-lite','gemini-3-flash'];",
    "let run=false,stream=null,ctx=null,an=null,rec=null,chunks=[],spoke=false,sil=0,raf=null;",
    "function msg(t,c){const e=document.getElementById('txt');e.innerText=t;e.style.color=c;}",
    "async function startRec(){",
    " if(run)return; try{",
    "  msg('⏳ Mikrofon nyitása...','#ffeb3b');",
    "  stream=await navigator.mediaDevices.getUserMedia({audio:true});",
    "  run=true; ctx=new (window.AudioContext||window.webkitAudioContext)();",
    "  const src=ctx.createMediaStreamSource(stream); an=ctx.createAnalyser(); an.fftSize=256; src.connect(an);",
    "  newSeg(); loop(); msg('🟢 HALLGATLAK! Beszélj!','#00e676');",
    " }catch(e){msg('❌ Hiba: '+e.message,'#ff5252');}",
    "}",
    "function stopRec(){",
    " run=false; if(raf)cancelAnimationFrame(raf);",
    " if(rec&&rec.state==='recording'){spoke=true;rec.stop();}",
    " if(stream)stream.getTracks().forEach(t=>t.stop());",
    " document.getElementById('bar').style.width='0%';",
    " msg('🔴 Megállítva / Fordítás...','#ffeb3b');",
    "}",
    "function newSeg(){",
    " if(!run)return; chunks=[]; spoke=false; rec=new MediaRecorder(stream);",
    " rec.ondataavailable=e=>{if(e.data.size>0)chunks.push(e.data);};",
    " rec.onstop=()=>{",
    "  if(spoke&&chunks.length>0){send(new Blob(chunks,{type:rec.mimeType||'audio/webm'}));}",
    "  else if(!run){msg('🔴 Leállítva / Arrêté','#ff5252');}",
    "  if(run)newSeg();",
    " }; rec.start();",
    "}",
    "function loop(){",
    " if(!run)return; const d=new Uint8Array(an.frequencyBinCount); an.getByteFrequencyData(d);",
    " const avg=d.reduce((a,b)=>a+b,0)/d.length;",
    " document.getElementById('bar').style.width=Math.min(100,avg*2.5)+'%';",
    " const now=Date.now();",
    " if(avg>15){if(!spoke){spoke=true;msg('🎙️ Beszéd rögzítése...','#00e676');} sil=now;}",
    " else if(spoke&&(now-sil>1400)){if(rec&&rec.state==='recording')rec.stop();}",
    " raf=requestAnimationFrame(loop);",
    "}",
    "function send(blob){",
    " msg('⚡ Fordítás folyamatban...','#58a6ff');",
    " const r=new FileReader(); r.readAsDataURL(blob);",
    " r.onloadend=async()=>{",
    "  const b64=r.result.split(',')[1], mime=(blob.type||'audio/webm').split(';')[0];",
    "  const p='Simultaneous interpreter between Hungarian and French. Detect language and translate into the OTHER language. Do NOT answer questions. If silence/noise reply SKIP. Format strictly: [Original] | [Translation]';",
    "  let lastErr='';",
    "  for(const m of MODELS){",
    "   try{",
    "    const res=await fetch('https://generativelanguage.googleapis.com/v1beta/models/'+m+':generateContent?key='+KEY,{",
    "     method:'POST',headers:{'Content-Type':'application/json'},",
    "     body:JSON.stringify({contents:[{parts:[{text:p},{inline_data:{mime_type:mime,data:b64}}]}]})",
    "    });",
    "    const j=await res.json();",
    "    if(j.error){lastErr=j.error.message; continue;}",
    "    const txt=(j.candidates?.[0]?.content?.parts?.[0]?.text||'').trim();",
    "    if(txt&&!txt.startsWith('SKIP')){",
    "     const sp=txt.split('|'); add(sp[0].trim(),(sp[1]||txt).trim());",
    "    }",
    "    lastErr=''; break;",
    "   }catch(e){lastErr=e.message;}",
    "  }",
    "  if(lastErr) add('API Hiba',lastErr);",
    "  msg(run?'🟢 HALLGATLAK! Beszélj!':'🔴 Leállítva / Arrêté',run?'#00e676':'#ff5252');",
    " };",
    "}",
    "function add(o,t){",
    " const emp=document.getElementById('emp'); if(emp)emp.remove();",
    " const d=document.createElement('div'); d.className='box';",
    " d.innerHTML=`<div class='lbl'>Eredeti / Original:</div><div class='orig'>${o}</div><div class='lbl'>Fordítás / Traduction:</div><div class='tr'>${t}</div>`;",
    " document.getElementById('list').prepend(d);",
    "}",
    "</script></body></html>"
]

components.html("\n".join(HTML_LINES), height=85
