import time
import streamlit as st
import pycountry
from google import generativeai as genai

# Oldal konfiguráció
st.set_page_config(
    page_title="Crazyfordító",
    page_icon="🎙️",
    layout="centered"
)

# Egyedi CSS stílusok a nagy gombhoz és a tiszta, modern mobilbarát felülethez
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .big-button {
        display: flex;
        justify-content: center;
        margin: 20px 0;
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
    .chat-box {
        background-color: #1a202c;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# Címsor
st.title("🎙️ Crazyfordító")
st.write("Valós idejű, folyamatos fordító intelligens szünetfigyeléssel.")

# API kulcs ellenőrzése
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# Nyelvek lekérése pycountry-val
languages = sorted([lang.name for lang in pycountry.languages if hasattr(lang, 'name')])
default_source_idx = languages.index("English") if "English" in languages else 0
default_target_idx = languages.index("Hungarian") if "Hungarian" in languages else 0

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Forrás nyelv (Beszélő)", languages, index=default_source_idx)
with col2:
    target_lang = st.selectbox("Cél nyelv (Fordítás)", languages, index=default_target_idx)

# Állapotkezelés (Session State) a szövegek gyűjtéséhez és összefűzéséhez
if "transcript_buffer" not in st.session_state:
    st.session_state.transcript_buffer = ""
if "translated_buffer" not in st.session_state:
    st.session_state.translated_buffer = ""
if "is_running" not in st.session_state:
    st.session_state.is_running = False

st.markdown("---")

# Vezérlő gombok
col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 FORDÍTÁS INDÍTÁSA")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS")

if start_btn:
    st.session_state.is_running = true
    st.session_state.transcript_buffer = ""
    st.session_state.translated_buffer = ""

if stop_btn:
    st.session_state.is_running = False

# Felület a szövegeknek
st.markdown("### 📝 Élő szöveg és fordítás")
transcript_placeholder = st.empty()
translation_placeholder = st.empty()

# Fő ciklus a folyamatos hallgatáshoz / szünetfigyeléshez
if st.session_state.is_running:
    st.info(f"A hallgatás aktív ({source_lang} ➡️ {target_lang}). Beszélj a mikrofonba...")
    
    # Itt kötjük be a Streamlit hangrögzítőt vagy a folyamatos feldolgozási logikát
    audio_value = st.audio_input("Beszéljen most...")

    if audio_value is not None:
        with st.spinner("Fordítás folyamatban..."):
            try:
                # Gemini modell hívás a fordításhoz és összefűzéshez
                model = genai.GenerativeModel("gemini-2.0-flash")
                
                audio_bytes = audio_value.read()
                
                prompt = (
                    f"Translate the following speech audio from {source_lang} to {target_lang}. "
                    "If there is an existing context/buffer, intelligently append or continue the thought "
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

    # Eredmények megjelenítése a dobozokban
    with transcript_placeholder.container():
        st.markdown(f"**Eredeti ({source_lang}):**\n\n{st.session_state.transcript_buffer or 'Várakozás a beszédre...'}")

    with translation_placeholder.container():
        st.markdown(f"**Fordítás ({target_lang}):**\n\n{st.session_state.translated_buffer or 'A fordítás itt jelenik meg...'}")
        
    # Kis várakozás a 2 másodperces szünet / ciklus finomhangolásához
    time.sleep(0.5)
    if st.session_state.is_running:
        st.rerun()
else:
    st.warning("A fordítás le van állítva. Kattints a **FORDÍTÁS INDÍTÁSA** gombra a kezdéshez.")
