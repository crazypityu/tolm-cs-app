import time
import streamlit as st
from google import generativeai as genai

st.set_page_config(
    page_title="Crazyfordító (HU ⇄ FR)",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .app-header {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #e6edf3;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        width: 100% !important;
    }
    div[data-testid="column"] {
        flex: 1 1 50% !important;
        width: 50% !important;
        min-width: 0 !important;
    }
    div.stButton > button {
        width: 100% !important;
        height: 150px !important;
        font-size: 15px !important;
        font-weight: bold !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #1b5e20 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:active {
        background-color: #2e7d32 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #b71c1c !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:active {
        background-color: #c62828 !important;
    }
    .status-bar {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        margin-top: 8px;
        margin-bottom: 10px;
    }
    .chat-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        min-height: 280px;
        margin-top: 8px;
    }
    .chat-item {
        border-bottom: 1px solid #30363d;
        padding-bottom: 12px;
        margin-bottom: 12px;
    }
    .chat-item:last-child {
        border-bottom: none;
    }
    .label-text {
        color: #8b949e;
        font-size: 12px;
        margin-bottom: 2px;
    }
    .orig-text {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .trans-text {
        color: #58a6ff;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-header">🎙️ Crazyfordító (HU ⇄ FR)</div>', unsafe_allow_html=True)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 INDÍTÁS\nDÉMARRER")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS\nARRÊTER")

if start_btn:
    st.session_state.is_running = True

if stop_btn:
    st.session_state.is_running = False

if st.session_state.is_running:
    st.markdown('<div class="status-bar" style="color: #4caf50;">🟢 Aktív / Actif</div>', unsafe_allow_html=True)
    
    audio_value = st.audio_input("Beszéljen most / Parlez maintenant...")

    if audio_value is not None:
        audio_bytes = audio_value.read()
        if audio_bytes and audio_bytes != st.session_state.last_audio:
            st.session_state.last_audio = audio_bytes
            with st.spinner("Tolmácsolás... / Traduction..."):
                prompt = (
                    "You are a strict, professional simultaneous interpreter operating strictly between Hungarian and French. "
                    "Listen to the speech audio, automatically detect whether the speaker is using Hungarian or French, "
                    "and translate it into the OTHER language. "
                    "CRITICAL: "
                    "1. Your ONLY job is to translate. If the speech contains a question, you MUST translate the question itself without answering. "
                    "2. Return your response strictly in the following format, separated by a pipe character (|): "
                    "[Detected Original Text] | [Translated Text]"
                )
                
                models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
                response = None
                last_error = ""

                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([
                            prompt,
                            {"mime_type": "audio/wav", "data": audio_bytes}
                        ])
                        if response and response.text:
                            break
                    except Exception as err:
                        last_error = str(err)
                        time.sleep(0.8)

                if response and response.text:
                    result_text = response.text.strip()
                    if "|" in result_text:
                        parts = result_text.split("|", 1)
                        original = parts[0].strip()
                        translated = parts[1].strip()
                    else:
                        original = "Felismert szöveg / Texte"
                        translated = result_text

                    st.session_state.chat_history.append({"orig": original, "trans": translated})
                else:
                    st.session_state.chat_history.append({"orig": "Hiba", "trans": last_error})
else:
    st.markdown('<div class="status-bar" style="color: #e53935;">🔴 Leállítva</div>', unsafe_allow_html=True)

if st.session_state.chat_history:
    history_html = '<div class="chat-container">'
    for chat in reversed(st.session_state.chat_history):
        history_html += f"""
            <div class="chat-item">
                <div class="label-text">Eredeti / Original:</div>
                <div class="orig-text">{chat['orig']}</div>
                <div class="label-text">Fordítás / Traduction:</div>
                <div class="trans-text">{chat['trans']}</div>
            </div>
        """
    history_html += '</div>'
    st.markdown(history_html, unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-container"></div>', unsafe_allow_html=True)
