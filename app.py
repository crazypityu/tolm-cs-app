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
st.write("Valós idejű, folyamatos fordító intelligens szünetfigyeléssel.")

# API kulcs ellenőrzése
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# Nyelvlisták előkészítése
top_languages = [
    "English", "Hungarian", "German", "French", "Spanish", 
    "Italian", "Russian", "Chinese", "Japanese", "Arabic", 
    "Portuguese", "Polish", "Dutch", "Romanian", "Turkish", 
    "Ukrainian", "Czech", "Greek", "Swedish", "Korean"
]
all_languages = sorted([lang.name for lang in pycountry.languages if hasattr(lang, 'name')])
languages = top_languages + [lang for lang in all_languages if lang not in top_languages]

# Session state inicializálás a nyelvek tiszta kezeléséhez
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English" if "English" in languages else languages[0]
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hungarian" if "Hungarian" in languages else languages[1]

# Cserélő függvény
def swap_languages():
    st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang

# Nyelvbeállítások felülete és a csere gomb
st.markdown("### 🌐 Nyelvbeállítások")
col1, col_swap, col2 = st.columns([5, 1.5, 5])

with col1:
    # Biztosítjuk, hogy az index ne lógjon ki
    try:
        src_idx = languages.index(st.session_state.source_lang)
    except ValueError:
        src_idx = 0
    
    selected_source = st.selectbox("Forrás nyelv", languages, index=src_idx, key="src_sb")
    if selected_source != st.session_state.source_lang:
        st.session_state.source_lang = selected_source

with col_swap:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("⇄ Csere", help="Nyelvek megfordítása", on_click=swap_languages):
        pass

with col2:
    try:
        tgt_idx = languages.index(st.session_state.target_lang)
    except ValueError:
        tgt_idx = 1
        
    selected_target = st.selectbox("Cél nyelv", languages, index=tgt_idx, key="tgt_sb")
    if selected_target != st.session_state.target_lang:
        st.session_state.target_lang = selected_target

# Állapotkezelés a szövegek gyűjtéséhez és összefűzéséhez
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
    st.session_state.is_running = True
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
    st.info(f"A hallgatás aktív ({st.session_state.source_lang} ➡️ {st.session_state.target_lang}). Beszélj a mikrofonba...")
    
    audio_value = st.audio_input("Beszéljen most...")

    if audio_value is not None:
        with st.spinner("Fordítás folyamatban..."):
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                audio_bytes = audio_value.read()
                
                prompt = (
                    f"Translate the following speech audio from {st.session_state.source_lang} to {st.session_state.target_lang}. "
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

    # Eredmények megjelenítése
    with transcript_placeholder.container():
        st.markdown(f"**Eredeti ({st.session_state.source_lang}):**\n\n{st.session_state.transcript_buffer or 'Várakozás a beszédre...'}")

    with translation_placeholder.container():
        st.markdown(f"**Fordítás ({st.session_state.target_lang}):**\n\n{st.session_state.translated_buffer or 'A fordítás itt jelenik meg...'}")
        
    time.sleep(0.5)
    if st.session_state.is_running:
        st.rerun()
else:
    st.warning("A fordítás le van állítva. Kattints a **FORDÍTÁS INDÍTÁSA** gombra a kezdéshez.")
