import streamlit as st
import google.generativeai as genai
import pycountry
from gtts import gTTS
import io

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Többnyelvű Tolmács",
    page_icon="🌍",
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

# 3. Gemini API konfiguráció
api_kulcs = st.secrets.get("GEMINI_API_KEY")
if not api_kulcs:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

genai.configure(api_key=api_kulcs)
modell = genai.GenerativeModel("gemini-1.5-flash")

# MP3 hang készítése a háttérben
def hang_generalas(szoveg, nyelv_kod):
    fp = io.BytesIO()
    try:
        tts = gTTS(text=szoveg, lang=nyelv_kod)
        tts.write_to_fp(fp)
    except Exception:
        # Ha az adott nyelvkódot nem támogatná a gTTS, visszaáll angolra
        tts = gTTS(text=szoveg, lang="en")
        tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# Fordítás a Geminivel
def fordit(szoveg, forras_nev, cel_nev):
    prompt = f"""
    Profi tolmács vagy. Fordítsd le a következő szöveget {forras_nev} nyelvről {cel_nev} nyelvre.
    Kizárólag a lefordított, természetes szöveget add vissza, mindenféle bevezető vagy magyarázat nélkül:
    "{szoveg}"
    """
    valasz = modell.generate_content(prompt)
    return valasz.text.strip()

# 4. Fejléc és hangszóró teszt
st.title("🌍 Többnyelvű Tolmács")
st.write("Azonnali fordítás és felolvasás.")

if st.button("🔊 Üdvözlet felolvasása (Hangteszt)"):
    audio_fp = hang_generalas("Üdvözöllek! A hangszóró és a tolmács rendszer működik.", "hu")
    st.audio(audio_fp, format="audio/mp3", autoplay=True)

st.markdown("---")

# 5. Nyelvválasztó legördülő menük pycountry alapján
nyelvek = sorted([lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")])

col1, col2 = st.columns(2)
with col1:
    forras_index = nyelvek.index("Hungarian") if "Hungarian" in nyelvek else 0
    forras_valasztott = st.selectbox("Forrásnyelv:", nyelvek, index=forras_index)

with col2:
    cel_index = nyelvek.index("French") if "French" in nyelvek else 1
    cel_valasztott = st.selectbox("Célnyelv:", nyelvek, index=cel_index)

# 2 betűs kódok kinyerése a felolvasáshoz
forras_lang = pycountry.languages.get(name=forras_valasztott)
cel_lang = pycountry.languages.get(name=cel_valasztott)
cel_kod = cel_lang.alpha_2.lower() if cel_lang and hasattr(cel_lang, "alpha_2") else "en"

# 6. Szövegbevitel
forras_szoveg = st.text_area(
    "Írd vagy másold be a szöveget:",
    placeholder="Írj be egy mondatot a fordításhoz...",
    height=100
)

# 7. Fordítás és felolvasás
if st.button("🔄 Fordítás és Felolvasás"):
    if forras_szoveg.strip():
        with st.spinner("Fordítás folyamatban..."):
            eredmeny = fordit(forras_szoveg.strip(), forras_valasztott, cel_valasztott)
            st.session_state["utolso_forditas"] = eredmeny
            st.session_state["cel_kod"] = cel_kod
    else:
        st.warning("Kérlek, írj be szöveget a fordításhoz!")

# 8. Eredmény megjelenítése és lejátszása
if "utolso_forditas" in st.session_state and st.session_state["utolso_forditas"]:
    st.subheader(f"Fordítás eredménye ({cel_valasztott}):")
    szoveg = st.session_state["utolso_forditas"]
    st.success(szoveg)

    audio_fp = hang_generalas(szoveg, st.session_state.get("cel_kod", "fr"))
    st.audio(audio_fp, format="audio/mp3", autoplay=True)
