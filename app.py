import time
import streamlit as st
from google import generativeai as genai

# Oldal konfiguráció
st.set_page_config(
    page_title="Crazyfordító - Two-Way Interpreter",
    page_icon="🎙️",
    layout="centered"
)

# Egyedi CSS stílusok a nagy gombhoz és a tiszta felülethez
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        height: 4em;
        font-size: 18px !important;
        font-weight: bold;
        color: white;
        background-color: #2b6cb0;
        border-radius: 12px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3182ce;
    }
    .chat-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# Címsor két nyelven
st.title("🎙️ Crazyfordító / Traducteur")
st.write("Élő kétnyelvű szinkrontolmács | Interprète simultané bilingue (Magyar ⇄ Français)")

# API kulcs ellenőrzése
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# Állapotkezelés
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

st.markdown("---")

# Vezérlő gombok kétnyelvű felirattal
col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 INDÍTÁS / DÉMARRER")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS / ARRÊTER")

if start_btn:
    st.session_state.is_running = True
    st.session_state.chat_history = []

if stop_btn:
    st.session_state.is_running = False

# Felület a párbeszédhez
st.markdown("### 📝 Beszélgetési Előzmények / Historique de la conversation")
chat_placeholder = st.empty()

# Fő ciklus a hallgatáshoz
if st.session_state.is_running:
    st.info("A tolmács aktív (Magyar ⇄ Francia). Beszéljen a mikrofonba... | Interprète actif. Parlez dans le micro...")
    
    audio_value = st.audio_input("Beszéljen most / Parlez maintenant...")

    if audio_value is not None:
        with st.spinner("Tolmácsolás folyamatban... / Traduction en cours..."):
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                audio_bytes = audio_value.read()
                
                # Szigorú tolmács prompt
                prompt = (
                    "You are a strict, professional simultaneous interpreter operating strictly between Hungarian and French. "
                    "Listen to the speech audio, automatically detect whether the speaker is using Hungarian or French, "
                    "and translate it into the OTHER language. "
                    "CRITICAL: "
                    "1. Your ONLY job is to translate. If the speech contains a question, you MUST translate the question itself without answering. "
                    "2. Return your response strictly in the following format, separated by a pipe character (|): "
                    "[Detected Original Text] | [Translated Text]"
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
                    original = "Ismeretlen / Inconnu"
                    translated = result_text

                st.session_state.chat_history.append({"orig": original, "trans": translated})
                
            except Exception as e:
                st.error(f"Hiba történt / Erreur: {e}")

    # Eredmények megjelenítése
    with chat_placeholder.container():
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"""
                <div class="chat-box">
                    <span style='color: #8b949e; font-size: 14px;'>Eredeti / Original:</span><br>
                    <strong>{chat['orig']}</strong><br><br>
                    <span style='color: #58a6ff; font-size: 14px;'>Fordítás / Traduction:</span><br>
                    <strong>{chat['trans']}</strong>
                </div>
            """, unsafe_allow_html=True)
        
    time.sleep(0.5)
    if st.session_state.is_running:
        st.rerun()
else:
    st.warning("A tolmácsolás le van állítva. Kattints az INDÍTÁS gombra. | L'interprète est arrêté. Cliquez sur DÉMARRER.")
