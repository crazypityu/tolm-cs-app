import time
import streamlit as st
from google import generativeai as genai

# Oldal konfiguráció
st.set_page_config(
    page_title="Crazyfordító - Szinkrontolmács",
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
        font-size: 20px !important;
        font-weight: bold;
        color: white;
        background-color: #2b6cb0;
        border-radius: 12px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3182ce;
    }
    </style>
""", unsafe_allow_html=True)

# Címsor
st.title("🎙️ Crazyfordító")
st.write("Élő, szigorú szinkrontolmács (Magyar ⇄ Francia)")

# API kulcs ellenőrzése
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# Állapotkezelés a szövegek gyűjtéséhez és összefűzéséhez
if "translated_buffer" not in st.session_state:
    st.session_state.translated_buffer = ""
if "is_running" not in st.session_state:
    st.session_state.is_running = False

st.markdown("---")

# Vezérlő gombok
col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 TOLMÁCSOLÁS INDÍTÁSA")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS")

if start_btn:
    st.session_state.is_running = True
    st.session_state.translated_buffer = ""

if stop_btn:
    st.session_state.is_running = False

# Felület a fordításnak
st.markdown("### 📝 Élő Szinkrontolmácsolás")
translation_placeholder = st.empty()

# Fő ciklus a folyamatos hallgatáshoz / szünetfigyeléshez
if st.session_state.is_running:
    st.info("A tolmács aktív (Magyar ⇄ Francia automata felismerés). Beszélj a mikrofonba...")
    
    audio_value = st.audio_input("Beszéljen most...")

    if audio_value is not None:
        with st.spinner("Tolmácsolás..."):
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                audio_bytes = audio_value.read()
                
                # Szigorú szinkrontolmács prompt
                prompt = (
                    "You are a strict, professional simultaneous interpreter (szinkrontolmács) operating strictly between Hungarian and French. "
                    "Listen to the speech audio, automatically detect whether the speaker is using Hungarian or French, "
                    "and instantly translate it into the OTHER language (Hungarian to French, or French to Hungarian). "
                    "CRITICAL RULES: "
                    "1. Your ONLY job is to translate. If the speech contains a question, you MUST translate the question itself. "
                    "DO NOT answer the question, DO NOT act as an assistant, and DO NOT add any commentary or conversational filler. "
                    "2. If there is an existing translation context/buffer, intelligently append or continue the thought "
                    "if it belongs to the same sentence structure, maintaining smooth flow."
                )
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
                new_text = response.text.strip()
                
                # Intelligens összefűzés (akkumuláció)
                if st.session_state.translated_buffer:
                    st.session_state.translated_buffer += " " + new_text
                else:
                    st.session_state.translated_buffer = new_text
                
            except Exception as e:
                st.error(f"Hiba történt a feldolgozás során: {e}")

    # Eredmény megjelenítése
    with translation_placeholder.container():
        st.markdown(f"**Fordítás:**\n\n{st.session_state.translated_buffer or 'A tolmácsolás itt jelenik meg...'}")
        
    time.sleep(0.5)
    if st.session_state.is_running:
        st.rerun()
else:
    st.warning("A tolmácsolás le van állítva. Kattints a **TOLMÁCSOLÁS INDÍTÁSA** gombra a kezdéshez.")
