import streamlit as st
from gtts import gTTS
import io

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Tolmács App",
    page_icon="🗣️",
    layout="centered"
)

# 2. Lehúzásos frissítés letiltása
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
}
.stButton button {
    width: 100%;
    border-radius: 8px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# MP3 hang készítése a háttérben
def hang_generalas(szoveg, nyelv):
    fp = io.BytesIO()
    tts = gTTS(text=szoveg, lang=nyelv)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# 3. Fejléc és biztos hangszóró teszt
st.title("🗣️ Kétnyelvű Tolmács")
st.write("Magyar ⇄ Francia azonnali fordító és hangszóró teszt.")

if st.button("🔊 Üdvözlet felolvasása (Hangteszt)"):
    audio_fp = hang_generalas("Üdvözöllek! A hangszóró és a tolmács rendszer működik.", "hu")
    st.audio(audio_fp, format="audio/mp3", autoplay=True)

st.markdown("---")

# 4. Irányválasztás
irany = st.radio(
    "Válassz fordítási irányt:",
    ("Magyar ➔ Francia", "Francia ➔ Magyar"),
    horizontal=True
)

# 5. Szövegbevitel
forras_szoveg = st.text_area(
    "Írd vagy másold be a szöveget:",
    placeholder="Írj be egy mondatot a teszteléshez...",
    height=100
)

# 6. Minta szótár
minta_forditasok = {
    "Magyar ➔ Francia": {
        "szia": "Bonjour",
        "hogy vagy": "Comment ça va ?",
        "jó napot": "Bonjour, bonne journée",
        "egészségedre": "Santé !"
    },
    "Francia ➔ Magyar": {
        "bonjour": "Jó napot kívánok",
        "merci": "Köszönöm",
        "santé": "Egészségedre !"
    }
}

beszed_nyelv = "fr" if irany == "Magyar ➔ Francia" else "hu"

if st.button("🔄 Fordítás"):
    if forras_szoveg.strip():
        keresett = forras_szoveg.strip().lower()
        forditas_eredmeny = minta_forditasok.get(irany, {}).get(
            keresett,
            f"{forras_szoveg}"
        )
        st.session_state["utolso_forditas"] = forditas_eredmeny
        st.session_state["beszed_nyelv"] = beszed_nyelv
    else:
        st.warning("Kérlek, írj be szöveget a fordításhoz!")

# 7. Eredmény megjelenítése és felolvasása
if "utolso_forditas" in st.session_state and st.session_state["utolso_forditas"]:
    st.subheader("Fordítás eredménye:")
    szoveg = st.session_state["utolso_forditas"]
    st.info(szoveg)

    audio_fp = hang_generalas(szoveg, st.session_state.get("beszed_nyelv", "fr"))
    st.audio(audio_fp, format="audio/mp3", autoplay=True)
