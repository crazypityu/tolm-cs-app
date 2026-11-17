import streamlit as st
import streamlit.components.v1 as components
from google import generativeai as genai

st.set_page_config(
    page_title="Crazyfordito",
    page_icon="🎙️",
    layout="centered"
)

css_code = (
    "<style>"
    ".main { background-color: #0e1117; color: #ffffff; }"
    ".sticky-buttons { position: sticky; top: 0; background-color: #0e1117; z-index: 999; padding: 10px 0; border-bottom: 1px solid #30363d; }"
    "div.stButton > button { width: 100% !important; height: 4.2em !important; font-size: 14px !important; font-weight: bold; color: white !important; border-radius: 16px !important; border: none !important; }"
    "div[data-testid='stHorizontalBlock'] > div:nth-child(1) button { background-color: #1b5e20 !important; }"
    "div[data-testid='stHorizontalBlock'] > div:nth-child(2) button { background-color: #b71c1c !important; }"
    ".chat-box { background-color: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; }"
    "</style>"
)
st.markdown(css_code, unsafe_allow_html=True)

st.title("🎙️ Crazyfordító / Traducteur")
st.write("Élő kétnyelvű szinkrontolmács | Interprète bilingue (Magyar ⇄ Français)")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = True
if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

st.markdown('<div class="sticky-buttons">', unsafe_allow_html=True)
col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 INDÍTÁS / DÉMARRER")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS / ARRÊTER")
st.markdown('</div>', unsafe_allow_html=True)

if start_btn:
    st.session_state.is_running = True
    st.session_state.chat_history = []
    st.session_state.last_audio_bytes = None

if stop_btn:
    st.session_state.is_running = False
    st.session_state.last_audio_bytes = None

diag_html = (
    "<div style='background:#161b22; padding:12px; border-radius:10px; border:1px solid #f39c12; font-family:sans-serif;'>"
    "<button onclick='testMic()' style='background:#f39c12; color:#000; padding:12px; border:none; border-radius:8px; font-weight:bold; width:100%; font-size:15px;'>"
    "🔍 MIKROFON HIBA KIOLVASÁSA (Kattints ide!)"
    "</button>"
    "<p id='mic-status' style='color:#ffffff; font-size:14px; margin:10px 0 0 0;'>"
    "Állapot: Nyomd meg a sárga gombot a teszthez!"
    "</p></div>"
    "<script>"
    "async function testMic() {"
    "  const status = document.getElementById('mic-status');"
    "  status.style.color = '#ffeb3b';"
    "  status.innerText = '⏳ Mikrofon tesztelése...';"
    "  try {"
    "    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {"
    "      status.style.color = '#ff5252';"
    "      status.innerText = '❌ HIBA: A böngésző letiltotta a mediaDevices API-t!';"
    "      return;"
    "    }"
    "    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });"
    "    const label = stream.getAudioTracks()[0].label || 'Alapértelmezett mikrofon';"
    "    status.style.color = '#4caf50';"
    "    status.innerText = '✅ SIKER! A mikrofon működik: ' + label;"
    "    stream.getTracks().forEach(t => t.stop());"
    "  } catch (err) {"
    "    status.style.color = '#ff5252';"
    "    status.innerText = '❌ HIBA (' + err.name + '): ' + err.message;"
    "  }"
    "}"
    "</script>"
)
components.html(diag_html, height=135)

if st.session_state.is_running:
    st.info("A tolmács aktív. Kattints a lenti mikrofonra a rögzítéshez!")
    audio_value = st.audio_input("🎙️ Hangfelvétel / Enregistrement vocal")

    if audio_value is not None:
        audio_bytes = audio_value.read()
        if len(audio_bytes) > 0 and audio_bytes != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = audio_bytes
            with st.spinner("Tolmácsolás... / Traduction..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = (
                        "You are a strict simultaneous interpreter between Hungarian and French. "
                        "Detect the language and translate into the OTHER language. "
                        "Do NOT answer questions, only translate them. "
                        "Format strictly as: [Original Text] | [Translated Text]"
                    )
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "audio/wav", "data": audio_bytes}
                    ])
                    result_text = response.text.strip()
                    if "|" in result_text:
                        parts = result_text.split("|", 1)
                        original = parts[0].strip()
                        translated = parts[1].strip()
                    else:
                        original = "Felismert szöveg"
                        translated = result_text
                    st.session_state.chat_history.append({"orig": original, "trans": translated})
                except Exception as e:
                    st.error(f"Hiba történt / Erreur: {e}")

    st.markdown("### 📝 Előzmények / Historique")
    for chat in reversed(st.session_state.chat_history):
        box_html = (
            f"<div class='chat-box'>"
            f"<span style='color: #8b949e; font-size: 14px;'>Eredeti / Original:</span><br>"
            f"<strong>{chat['orig']}</strong><br><br>"
            f"<span style='color: #58a6ff; font-size: 14px;'>Fordítás / Traduction:</span><br>"
            f"<strong>{chat['trans']}</strong>"
            f"</div>"
        )
        st.markdown(box_html, unsafe_allow_html=True)
else:
    st.warning("A tolmácsolás le van állítva. Kattints az INDÍTÁS gombra.")
