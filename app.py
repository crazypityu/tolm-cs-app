import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Crazyfordito", page_icon="🎙️", layout="wide")

st.markdown(
    "<style>"
    ".main, .stApp { background-color: #0e1117; color: #ffffff; }"
    ".block-container { padding: 0.2rem !important; max-width: 100% !important; }"
    "header, footer { visibility: hidden; height: 0px !important; }"
    "iframe { width: 100% !important; border: none !important; }"
    "</style>",
    unsafe_allow_html=True
)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Hiányzik a GEMINI_API_KEY!")
    st.stop()

KEY = st.secrets["GEMINI_API_KEY"]

# Rövid, vágólap-biztos HTML/JS blokk: 1-gombos mikrofon, szünet-érzékelő és azonnali fordítás
HTML_LINES = [
    "<!DOCTYPE html><html><head><meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width,initial-scale=1'>",
    "<style>",
    "*{box-sizing:border-box} body{background:#0e1117;color:#fff;font-family:sans-serif;margin:0;padding:6px}",
    "h2{text-align:center;margin:4px 0 10px 0;font-size:24px}",
    ".row{display:flex;gap:12px;position:sticky;top:0;background:#0e1117;padding:6px 0;z-index:9}",
    ".btn{flex:1;height:110px;border:3px solid #fff4;border-radius:20px;color:#fff;font-size:21px;font-weight:900}",
    ".go{background:#1b5e20} .stop{background:#b71c1c}",
    "#st{background:#161b22;border:2px solid #30363d;border-radius:14px;padding:14px;margin:10px 0;font-size:19px;font-weight:bold;text-align:center;color:#ffeb3b}",
    "#bar{height:12px;width:0%;background:#00e676;border-radius:6px;margin-top:8px;transition:width 0.1s}",
    ".box{background:#161b22;padding:18px;border-radius:16px;border:2px solid #30363d;margin-bottom:14px}",
    ".lbl{color:#8b949e;font-size:15px;font-weight:bold}",
    ".orig{color:#fff;font-size:22px;font-weight:bold;margin:4px 0 14px 0}",
    ".tr{color:#58a6ff;font-size:26px;font-weight:900;margin-top:4px}",
    "</style></head><body>",
    "<h2>🎙️ Crazyfordító (HU ⇄ FR)</h2>",
    "<div class='row'>",
    "<button class='btn go' onclick='startRec()'>🟢 INDÍTÁS<br>DÉMARRER</button>",
    "<button class='btn stop' onclick='stopRec()'>🔴 LEÁLLÍTÁS<br>ARRÊTER</button>",
    "</div>",
    "<div id='st'><span id='txt'>⏹️ Nyomd meg a ZÖLD gombot!</span><div id='bar'></div></div>",
    "<div id='list'><div class='box' id='emp'><div class='orig'>Szövegláda készen áll...</div><div class='tr'>Prêt à traduire...</div></div></div>",
    "<script>",
    f"const KEY='{KEY}';",
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
    "  try{",
    "   const res=await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key='+KEY,{",
    "    method:'POST',headers:{'Content-Type':'application/json'},",
    "    body:JSON.stringify({contents:[{parts:[{text:p},{inline_data:{mime_type:mime,data:b64}}]}]})",
    "   });",
    "   const j=await res.json();",
    "   if(j.error){add('API Hiba',j.error.message);return;}",
    "   const txt=(j.candidates?.[0]?.content?.parts?.[0]?.text||'').trim();",
    "   if(txt&&!txt.startsWith('SKIP')){",
    "    const sp=txt.split('|'); add(sp[0].trim(),(sp[1]||txt).trim());",
    "   }",
    "   msg(run?'🟢 HALLGATLAK! Beszélj!':'🔴 Leállítva / Arrêté',run?'#00e676':'#ff5252');",
    "  }catch(e){add('Hiba',e.message);}",
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

components.html("\n".join(HTML_LINES), height=900, scrolling=True)
