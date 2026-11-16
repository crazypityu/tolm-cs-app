# Nyelvlisták előkészítése
top_languages = [
    "English", "Hungarian", "German", "French", "Spanish", 
    "Italian", "Russian", "Chinese", "Japanese", "Arabic", 
    "Portuguese", "Polish", "Dutch", "Romanian", "Turkish", 
    "Ukrainian", "Czech", "Greek", "Swedish", "Korean"
]
all_languages = sorted([lang.name for lang in pycountry.languages if hasattr(lang, 'name')])
languages = top_languages + [lang for lang in all_languages if lang not in top_languages]

# Alapértelmezett értékek beállítása a selectbox kulcsokhoz, ha még nincsenek benne
if "src_lang_selectbox" not in st.session_state:
    st.session_state.src_lang_selectbox = "English" if "English" in languages else languages[0]
if "tgt_lang_selectbox" not in st.session_state:
    st.session_state.tgt_lang_selectbox = "Hungarian" if "Hungarian" in languages else languages[1]

# Cserélő függvény, ami közvetlenül a widgetek kulcsait cseréli fel
def swap_languages():
    st.session_state.src_lang_selectbox, st.session_state.tgt_lang_selectbox = (
        st.session_state.tgt_lang_selectbox,
        st.session_state.src_lang_selectbox,
    )

# Nyelvbeállítások felülete és a csere gomb
st.markdown("### 🌐 Nyelvbeállítások")
col1, col_swap, col2 = st.columns([5, 1.5, 5])

with col1:
    # A selectbox automatikusan szinkronizálódik a st.session_state["src_lang_selectbox"] értékével
    source_lang = st.selectbox("Forrás nyelv", languages, key="src_lang_selectbox")

with col_swap:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("⇄ Csere", help="Nyelvek megfordítása", on_click=swap_languages):
        pass

with col2:
    target_lang = st.selectbox("Cél nyelv", languages, key="tgt_lang_selectbox")
