import streamlit as st
import streamlit.components.v1 as components
from google import generativeai as genai

st.set_page_config(page_title="Crazyfordito", page_icon="🎙️", layout="wide")

# Óriási, kesztyűbarát méretezés (zoom + hatalmas gombok és betűk)
st.markdown(
    "<style>"
    ".main, .stApp { background-color: #0e1117; color: #ffffff; }"
    ".block-container { padding: 0.5rem !important; max-width: 100% !important; zoom: 1.35; }"
    "header, footer { visibility: hidden; height: 0px !important; }"
    "div.stButton > button { width: 100% !important; height: 95px !important; font-size: 22px !important; font-weight: 900 !important; color: white !important; border-radius: 18px !important; border: 2px solid rgba(255,255,255,0.2) !important; }"
    "div[data-testid='stHorizontalBlock'] > div:nth-child(1) button { background-color: #1b5e20 !important; }"
    "div[data-testid='stHorizontalBlock'] > div:nth-child(2) button { background-color: #b71c1c !important; }"
    "div[data-testid='stAudioInput'] { transform: scale(1.15); transform-origin: top left; width: 87% !important; margin: 15px 0 25px 0 !important; }"
    ".chat-box { background-color: #161b22; padding: 18px; border-radius: 16px; margin-bottom: 14px; border: 2px solid #30363d; }"
    ".orig-txt { color: #ffffff; font-size: 22px; font-weight: bold; margin: 6px 0 14px 0; }"
    ".trans-txt { color: #58a6ff; font-size: 26px; font-weight: 900; margin-top: 6px; }"
    "</style>",
    unsafe_allow_html=True
)

st.markdown("<h2 style='text-align:center; margin:0;'>🎙️ Crazyfordító (HU ⇄ FR)</h2>", unsafe_allow_html=True)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Hiányzik a GEMINI_API_KEY!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = True
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 INDÍTÁS\nDÉMARRER"):
        st.session_state.is_running = True
        st.session_state.last_audio = None
with col2:
    if st.button("🔴 LEÁLLÍTÁS\nARRÊTER"):
        st.session_state.is_running = False

if st.session_state.is_running:
    audio_val = st.audio_input("🎙️ NYOMD MEG A MIKROFONT A BESZÉDHEZ:")

    # Automatikusan rákattint a mikrofonra, amikor megnyomod az INDÍTÁS-t
    components.html(
        "<script>"
        "const btn = window.parent.document.querySelector('[data-testid=\"stAudioInput\"] button');"
        "if (btn && btn.getAttribute('aria-label') && btn.getAttribute('aria-label').includes('Record')) { btn.click(); }"
        "</script>",
        height=0
    )

    if audio_val is not None:
        raw = audio_val.read()
        if len(raw) > 0 and raw != st.session_state.last_audio:
            st.session_state.last_audio = raw
            with st.spinner("⚡ Fordítás... / Traduction..."):
                try:
                    model = genai.GenerativeModel("gemini-3.8-flash")
                    prompt = (
                        "Simultaneous interpreter between Hungarian and French. "
                        "Detect language and translate into the OTHER language. "
                        "Do NOT answer questions, only translate. "
                        "Format strictly: [Original] | [Translation]"
                    )
                    res = model.generate_content([prompt, {"mime_type": "audio/wav", "data": raw}])
                    txt = res.text.strip()
                    orig, trans = txt.split("|", 1) if "|" in txt else ("Felismert szöveg", txt)
                    st.session_state.chat_history.append({"orig": orig.strip(), "trans": trans.strip()})
                except Exception as e:
                    st.error(f"Hiba: {e}")
else:
    st.warning("⏹️ Leállítva / Arrêté. Nyomj a zöld INDÍTÁS gombra!")

st.markdown("### 📝 Szövegláda / Historique")
if not st.session_state.chat_history:
    st.markdown(
        "<div class='chat-box'>"
        "<div style='color:#8b949e; font-size:15px;'>Eredeti / Original:</div>"
        "<div class='orig-txt'>Várakozás a beszédre...</div>"
        "<div style='color:#58a6ff; font-size:15px;'>Fordítás / Traduction:</div>"
        "<div class='trans-txt'>En attente de parole...</div>"
        "</div>",
        unsafe_allow_html=True
    )

for c in reversed(st.session_state.chat_history):
    st.markdown(
        f"<div class='chat-box'>"
        f"<div style='color:#8b949e; font-size:15px;'>Eredeti / Original:</div>"
        f"<div class='orig-txt'>{c['orig']}</div>"
        f"<div style='color:#58a6ff; font-size:15px;'>Fordítás / Traduction:</div>"
        f"<div class='trans-txt'>{c['trans']}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
