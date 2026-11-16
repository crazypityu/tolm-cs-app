# Nyelvlisták előkészítése
top_languages = [
    "English", "Hungarian", "German", "French", "Spanish", 
    "Italian", "Russian", "Chinese", "Japanese", "Arabic", 
    "Portuguese", "Polish", "Dutch", "Romanian", "Turkish", 
    "Ukrainian", "Czech", "Greek", "Swedish", "Korean"
]
all_languages = sorted([lang.name for lang in pycountry.languages if hasattr(lang, 'name')])
languages = top_languages + [lang for lang in all_languages if lang not in top_languages]

# Session state inicializálás
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English" if "English" in languages else languages[0]
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hungarian" if "Hungarian" in languages else languages[1]

# Cserélő függvény mobilos kattintáshoz
def swap_languages():
    st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang

# Elrendezés: Forrás selectbox -> Cserélő gomb -> Cél selectbox egymás alatt mobilosan is stabilan
st.markdown("### 🌐 Nyelvbeállítások")

col1, col_swap, col2 = st.columns([5, 1.5, 5])

with col1:
    st.session_state.source_lang = st.selectbox(
        "Forrás nyelv", 
        languages, 
        index=languages.index(st.session_state.source_lang) if st.session_state.source_lang in languages else 0,
        key="src_lang_selectbox"
    )

with col_swap:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    # Mobilon is stabil gomb, ami azonnal meghívja a cserét
    if st.button("⇄ Csere", help="Nyelvek megfordítása", on_click=swap_languages):
        pass

with col2:
    st.session_state.target_lang = st.selectbox(
        "Cél nyelv", 
        languages, 
        index=languages.index(st.session_state.target_lang) if st.session_state.target_lang in languages else 1,
        key="tgt_lang_selectbox"
    )
