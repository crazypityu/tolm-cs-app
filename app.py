# Nyelvlisták előkészítése
top_languages = [
    "English", "Hungarian", "German", "French", "Spanish", 
    "Italian", "Russian", "Chinese", "Japanese", "Arabic", 
    "Portuguese", "Polish", "Dutch", "Romanian", "Turkish", 
    "Ukrainian", "Czech", "Greek", "Swedish", "Korean"
]
all_languages = sorted([lang.name for lang in pycountry.languages if hasattr(lang, 'name')])
languages = top_languages + [lang for lang in all_languages if lang not in top_languages]

# 1. Inicializáljuk a widgetek kulcsait a session_state-ben, ha még nincsenek benne
if "source_select" not in st.session_state:
    st.session_state.source_select = "English" if "English" in languages else languages[0]
if "target_select" not in st.session_state:
    st.session_state.target_select = "Hungarian" if "Hungarian" in languages else languages[1]

# 2. A cserélő függvény, ami közvetlenül a state kulcsokat fordítja meg
def swap_languages():
    st.session_state.source_select, st.session_state.target_select = (
        st.session_state.target_select,
        st.session_state.source_select,
    )

# 3. Felület
st.markdown("### 🌐 Nyelvbeállítások")
col1, col_swap, col2 = st.columns([5, 1.5, 5])

with col1:
    # A selectbox közvetlenül a "source_select" kulcsot használja
    source_lang = st.selectbox("Forrás nyelv", languages, key="source_select")

with col_swap:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    # Az on_click azonnal lefut kattintásra, még a képernyő újrarajzolása előtt
    st.button("⇄ Csere", help="Nyelvek megfordítása", on_click=swap_languages)

with col2:
    # A selectbox közvetlenül a "target_select" kulcsot használja
    target_lang = st.selectbox("Cél nyelv", languages, key="target_select")
