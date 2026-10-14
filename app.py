import streamlit as st
import streamlit.components.v1 as components
import pycountry

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Crazyfordító Live",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Jelszavas védelem (Ha be van állítva az APP_PASSWORD a Secrets-ben, kéri, különben továbbenged)
def check_password():
    expected_pw = st.secrets.get("APP_PASSWORD")
    if not expected_pw:
        return True
    if st.session_state.get("authenticated", False):
        return True

    st.markdown("<h3 style='text-align: center; color: white;'>🔒 Crazyfordító Belépés</h3>", unsafe_allow_html=True)
    beirt_jelszo = st.text_input("Add meg a jelszót:", type="password")
    if st.button("Belépés", use_container_width=True):
        if beirt_jelszo == expected_pw:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hibás jelszó!")
    return False

if not check_password():
    st.stop()

# 3. API kulcs kiolvasása a Streamlit Secrets-ből
api_kulcs = st.secrets.get("GEMINI_API_KEY")
if not api_kulcs:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# 4. Oldalsáv beállítások (Automatikus nyelvfelismeréssel + pycountry listával)
with st.sidebar:
    st.header("⚙️ Live Beállítások")
    osszes_nyelv = sorted([lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")])
    partner_nyelvek = ["🌍 Automatikus (Bármilyen nyelv)"] + osszes_nyelv
    
    hang_nem = st.radio("Tolmács hangja:", ("Nő (Aoede)", "Férfi (Puck)"), horizontal=True)
    partner_lang = st.selectbox("Partner nyelve:", partner_nyelvek, index=0)
    
    u_lang_idx = osszes_nyelv.index("Hungarian") if "Hungarian" in osszes_nyelv else 0
    sajat_lang = st.selectbox("Saját nyelved:", osszes_nyelv, index=u_lang_idx)
    
    alap_celnyelv = st.selectbox(
        "Alapértelmezett nyelv (ha te kezdesz beszélni Auto módban):",
        osszes_nyelv,
        index=osszes_nyelv.index("French") if "French" in osszes_nyelv else 0
    )

voice_name = "Aoede" if "Aoede" in hang_nem else "Puck"

# 5. Szinkrontolmács rendszer-utasítás (System Prompt) összeállítása
if partner_lang.startswith("🌍"):
    partner_leiras = f"bármilyen idegen nyelvet (automatikusan ismerd fel a nyelvet; ha a beszélgetés legelején {sajat_lang} beszédet hallasz, fordítsd {alap_celnyelv} nyelvre, utána pedig mindig arra a nyelvre, amin a partner utoljára megszólalt)"
    partner_cimke = f"AUTO ({alap_celnyelv} / Bármely nyelv)"
else:
    partner_leiras = f"{partner_lang} nyelvet"
    partner_cimke = partner_lang.upper()

system_instruction = (
    f"Te egy valós idejű, kétirányú szinkrontolmács vagy (szakmai és műszaki szövegekben is profi). "
    f"Két ember beszélget egymással. Az egyik beszélő nyelve: {sajat_lang}. "
    f"A másik beszélő (Partner) nyelve: {partner_leiras}. "
    f"SZIGORÚ SZABÁLYOK: "
    f"1. Soha ne válaszolj a kérdésekre, ne beszélgess, KIZÁRÓLAG fordítsd le a hallott mondatot! "
    f"2. Ha {sajat_lang} nyelvű beszédet hallasz, azonnal fordítsd le a Partner nyelvére, és a szöveges kimeneted elejére írd oda pontosan ezt a címkét: [PARTNER] "
    f"3. Ha a Partner nyelvén (bármilyen nem {sajat_lang} nyelven) hallasz beszédet, azonnal fordítsd le {sajat_lang} nyelvre, és a szöveges kimeneted elejére írd oda pontosan ezt a címkét: [ÉN] "
    f"4. A [PARTNER] vagy [ÉN] címkét soha ne olvasd fel hangosan, csak a lefordított mondatot mondd ki természetesen!"
)

# Streamlit keret margóinak eltüntetése mobilos teljes képernyőhöz
st.markdown("""
<style>
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
    background-color: #0b0f19 !important;
}
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    max-width: 600px !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# 6. Beágyazott Gemini Live WebSocket Komponens (180°-os Partner nézettel)
live_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ background: #0b0f19; color: #f9fafb; display: flex; flex-direction: column; height: 86vh; justify-content: space-between; overflow: hidden; user-select: none; padding: 4px; }}
  
  /* FELSŐ ZÓNA: 180 FOKBAN ELFORGATOTT PARTNER NÉZET */
  .zone-partner {{
    transform: rotate(180deg);
    background: #111827;
    border: 2px solid #1d4ed8;
    border-radius: 18px;
    padding: 14px;
    height: 37%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(29, 78, 216, 0.25);
  }}

  /* ALSÓ ZÓNA: NORMÁL SAJÁT NÉZET */
  .zone-user {{
    background: #111827;
    border: 2px solid #047857;
    border-radius: 18px;
    padding: 14px;
    height: 37%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(4, 120, 87, 0.25);
  }}

  .header-p {{
    background: #1e3a8a;
    color: #93c5fd;
    padding: 8px 12px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    text-align: center;
    letter-spacing: 0.5px;
  }}

  .header-u {{
    background: #064e3b;
    color: #6ee7b7;
    padding: 8px 12px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    text-align: center;
    letter-spacing: 0.5px;
  }}

  .text-box {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 19px;
    line-height: 1.4;
    padding: 10px;
    overflow-y: auto;
    color: #ffffff;
    font-weight: 500;
  }}

  /* KÖZÉPSŐ VEZÉRLŐ SÁV */
  .center-bar {{
    height: 22%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }}

  .live-btn {{
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 14px 28px;
    font-size: 17px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 10px;
    width: 92%;
    justify-content: center;
  }}

  .live-btn.active {{
    background: linear-gradient(135deg, #dc2626, #991b1b);
    box-shadow: 0 0 22px rgba(220, 38, 38, 0.75);
    animation: pulse 1.6s infinite;
  }}

  .status {{
    font-size: 13px;
    color: #9ca3af;
    text-align: center;
    font-weight: 500;
  }}

  @keyframes pulse {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.03); }}
    100% {{ transform: scale(1); }}
  }}
</style>
</head>
<body>

  <!-- FELSŐ (180 FOKBAN FORGATOTT) PARTNER ZÓNA -->
  <div class="zone-partner">
    <div class="header-p">🗣️ PARTNER ({partner_cimke})</div>
    <div class="text-box" id="partner-text">A fordítás itt jelenik meg...</div>
  </div>

  <!-- KÖZÉPSŐ LIVE KAPCSOLÓ -->
  <div class="center-bar">
    <button id="toggleBtn" class="live-btn" onclick="toggleLive()">
      🟢 ÉLŐ TOLMÁCSOLÁS INDÍTÁSA
    </button>
    <div id="statusText" class="status">Koppints a gombra a folyamatos szinkrontolmácsoláshoz</div>
  </div>

  <!-- ALSÓ SAJÁT ZÓNA -->
  <div class="zone-user">
    <div class="text-box" id="user-text">A magyar fordítás itt jelenik meg...</div>
    <div class="header-u">🗣️ ÉN ({sajat_lang.upper()})</div>
  </div>

<script>
const API_KEY = {repr(api_kulcs)};
const VOICE_NAME = {repr(voice_name)};
const SYSTEM_INSTRUCTION = {repr(system_instruction)};

// Kipróbáljuk sorban a Live-kompatibilis modelleket, ha az első nem lenne elérhető a kulcsoddal
const LIVE_MODELS = [
  "models/gemini-2.0-flash-exp",
  "models/gemini-2.0-flash-live-001",
  "models/gemini-2.5-flash"
];
let currentModelIndex = 0;

let ws = null;
let audioCtx = null;
let mediaStream = null;
let processor = null;
let isRunning = false;
let isModelSpeaking = false;
let nextPlayTime = 0;
let currentTurnText = "";
let activeTargetBox = "both";

const btn = document.getElementById("toggleBtn");
const statusEl = document.getElementById("statusText");
const pBox = document.getElementById("partner-text");
const uBox = document.getElementById("user-text");

function setStatus(msg, color="#9ca3af") {{
  statusEl.innerText = msg;
  statusEl.style.color = color;
}}

async function toggleLive() {{
  if (isRunning) {{
    stopLive("Leállítva. Koppints az újraindításhoz.");
  }} else {{
    currentModelIndex = 0;
    await startLive();
  }}
}}

async function startLive() {{
  try {{
    setStatus("Mikrofon és Gemini Live csatlakozás...", "#fbbf24");
    
    if (!audioCtx) {{
      audioCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 24000 }});
    }}
    if (audioCtx.state === "suspended") {{
      await audioCtx.resume();
    }}

    if (!mediaStream) {{
      mediaStream = await navigator.mediaDevices.getUserMedia({{
        audio: {{
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }}
      }});
    }}

    connectWebSocket(LIVE_MODELS[currentModelIndex]);

  }} catch (err) {{
    setStatus("Mikrofon hiba: Engedélyezd a mikrofont a böngészőben! (" + err.message + ")", "#f87171");
    stopLive();
  }}
}}

function connectWebSocket(modelName) {{
  const host = "generativelanguage.googleapis.com";
  const path = "/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent";
  const url = "wss://" + host + path + "?key=" + API_KEY;

  ws = new WebSocket(url);

  ws.onopen = () => {{
    const setupMsg = {{
      setup: {{
        model: modelName,
        generationConfig: {{
          responseModalities: ["AUDIO"],
          speechConfig: {{
            voiceConfig: {{
              prebuiltVoiceConfig: {{
                voiceName: VOICE_NAME
              }}
            }}
          }}
        }},
        systemInstruction: {{
          parts: [{{ text: SYSTEM_INSTRUCTION }}]
        }}
      }}
    }};
    ws.send(JSON.stringify(setupMsg));
  }};

  ws.onmessage = async (event) => {{
    let raw = event.data;
    if (raw instanceof Blob) {{
      raw = await raw.text();
    }}
    const data = JSON.parse(raw);

    if (data.setupComplete) {{
      isRunning = true;
      btn.classList.add("active");
      btn.innerText = "🛑 ÉLŐ TOLMÁCSOLÁS LEÁLLÍTÁSA";
      setStatus("🎙️ ÉLŐBEN: Beszéljetek nyugodtan, automatikusan fordítok!", "#34d399");
      startMicStreaming();
      return;
    }}

    if (data.serverContent) {{
      const sc = data.serverContent;
      if (sc.modelTurn && sc.modelTurn.parts) {{
        for (const part of sc.modelTurn.parts) {{
          if (part.text) {{
            handleIncomingText(part.text);
          }}
          if (part.inlineData && part.inlineData.data) {{
            playPcm24k(part.inlineData.data);
          }}
        }}
      }}
      if (sc.turnComplete) {{
        currentTurnText = "";
        activeTargetBox = "both";
      }}
    }}
  }};

  ws.onerror = () => {{
    setStatus("Kapcsolódási hiba a szerverhez.", "#f87171");
  }};

  ws.onclose = (ev) => {{
    if (!isRunning && currentModelIndex < LIVE_MODELS.length - 1) {{
      currentModelIndex++;
      connectWebSocket(LIVE_MODELS[currentModelIndex]);
      return;
    }}
    if (isRunning) {{
      stopLive("A kapcsolat megszakadt (" + ev.code + "). Koppints az újraindításhoz.");
    }}
  }};
}}

function handleIncomingText(chunk) {{
  currentTurnText += chunk;
  let clean = currentTurnText;

  if (clean.includes("[PARTNER]")) {{
    activeTargetBox = "partner";
    clean = clean.replace(/\\[PARTNER\\]/g, "").trim();
  }} else if (clean.includes("[ÉN]") || clean.includes("[EN]")) {{
    activeTargetBox = "user";
    clean = clean.replace(/\\[ÉN\\]/g, "").replace(/\\[EN\\]/g, "").trim();
  }}

  if (!clean) return;

  if (activeTargetBox === "partner") {{
    pBox.innerText = clean;
  }} else if (activeTargetBox === "user") {{
    uBox.innerText = clean;
  }} else {{
    pBox.innerText = clean;
    uBox.innerText = clean;
  }}
}}

function startMicStreaming() {{
  if (processor) return;
  const source = audioCtx.createMediaStreamSource(mediaStream);
  processor = audioCtx.createScriptProcessor(4096, 1, 1);

  source.connect(processor);
  processor.connect(audioCtx.destination);

  processor.onaudioprocess = (e) => {{
    if (!isRunning || !ws || ws.readyState !== WebSocket.OPEN) return;
    // Amíg a tolmács hangosan beszél, nem küldjük vissza a saját hangját
    if (audioCtx.currentTime < nextPlayTime) return;

    const inputData = e.inputBuffer.getChannelData(0);
    const pcm16 = downsampleTo16k(inputData, audioCtx.sampleRate);
    const b64 = arrayBufferToBase64(pcm16.buffer);

    const msg = {{
      realtimeInput: {{
        mediaChunks: [{{
          mimeType: "audio/pcm;rate=16000",
          data: b64
        }}]
      }}
    }};
    ws.send(JSON.stringify(msg));
  }};
}}

function downsampleTo16k(buffer, inputRate) {{
  if (inputRate === 16000) {{
    const out = new Int16Array(buffer.length);
    for (let i = 0; i < buffer.length; i++) {{
      let s = Math.max(-1, Math.min(1, buffer[i]));
      out[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }}
    return out;
  }}
  const ratio = inputRate / 16000;
  const newLength = Math.round(buffer.length / ratio);
  const result = new Int16Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;
  while (offsetResult < result.length) {{
    const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
    let accum = 0, count = 0;
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {{
      accum += buffer[i];
      count++;
    }}
    const sample = Math.max(-1, Math.min(1, accum / count));
    result[offsetResult] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    offsetResult++;
    offsetBuffer = nextOffsetBuffer;
  }}
  return result;
}}

function arrayBufferToBase64(buffer) {{
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {{
    binary += String.fromCharCode(bytes[i]);
  }}
  return window.btoa(binary);
}}

function playPcm24k(base64Data) {{
  const binaryStr = window.atob(base64Data);
  const len = binaryStr.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {{
    bytes[i] = binaryStr.charCodeAt(i);
  }}
  const int16 = new Int16Array(bytes.buffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {{
    float32[i] = int16[i] / 32768.0;
  }}

  const audioBuffer = audioCtx.createBuffer(1, float32.length, 24000);
  audioBuffer.getChannelData(0).set(float32);

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);

  const now = audioCtx.currentTime;
  if (nextPlayTime < now) {{
    nextPlayTime = now + 0.05;
  }}
  source.start(nextPlayTime);
  nextPlayTime += audioBuffer.duration;
}}

function stopLive(statusMsg = "Leállítva. Koppints a gombra az indításhoz.") {{
  isRunning = false;
  btn.classList.remove("active");
  btn.innerText = "🟢 ÉLŐ TOLMÁCSOLÁS INDÍTÁSA";
  setStatus(statusMsg, "#9ca3af");

  if (processor) {{
    processor.disconnect();
    processor = null;
  }}
  if ( mediaStream ) {{
    mediaStream.getTracks().forEach(t => t.stop());
    mediaStream = null;
  }}
  if (ws) {{
    ws.close();
    ws = null;
  }}
}}
</script>
</body>
</html>
"""

components.html(live_html, height=680, scrolling=False)
