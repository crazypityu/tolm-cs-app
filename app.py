import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
import pycountry
from google.api_core import client_options

st.set_page_config(page_title="Szakmai Tolmács", page_icon="🎙️", layout="centered")

# --- JELSZÓ VÉDELEM BEÁLLÍTÁSA ---
ERVENYES_JELSZAVAK = ["Pitta62746274"]

if "bejelentkezve" not in st.session_state:
    st.session_state["bejelentkezve"] = False

if not st.session_state["bejelentkezve"]:
    st.title("🔒 Védett Alkalmazás")
    st.write("Kérjük, adja meg a belépési kódot a tolmács használatához.")
    
    beirt_jelszo = st.text_input("Belépési kód:", type="password")
    
    if st.button("Belépés"):
        if beirt_jelszo in ERVENYES_JELSZAVAK:
            st.session_state["bejelentkezve"] = True
            st.rerun()
        else:
            st.error("Hibás belépési kód! Kérjük, próbálja újra.")
    st.stop()
# ---------------------------------

st.title("🎙️ Élő Globális Szakmai Tolmács")
st.write("Válaszd ki a világ bármelyik nyelvét, nyomd meg a mikrofont, és beszélj!")

# --- VILÁG ÖSSZES NYELVE LISTA GENERÁLÁSA ---
st.write("### 🌐 Nyelvi beállítások:")

col1, col2 = st.columns(2)

@st.cache_data
def get_all_languages():
    kiemelt_nyelvek = {
        "Hungarian": "🇭🇺 Magyar (Hungarian)",
        "French": "🇫🇷 Francia (French)",
        "English": "🇬🇧 Angol (English)",
        "German": "🇩🇪 Német (German)",
        "Dutch": "🇳🇱 Holland (Dutch)",
        "Romanian": "🇷🇴 Román (Romanian)",
        "Bulgarian": "🇧🇬 Bolgár (Bulgarian)",
        "Polish": "🇵🇱 Lengyel (Polish)",
        "Spanish": "🇪🇸 Spanyol (Spanish)",
        "Italian": "🇮🇹 Olasz (Italian)",
        "Russian": "🇷🇺 Orosz (Russian)",
        "Turkish": "🇹🇷 Török (Turkish)"
    }
    
    teljes_lista = {}
    for k, v in kiemelt_nyelvek.items():
        teljes_lista[k] = v
        
    maradek = []
    for lang in pycountry.languages:
        if hasattr(lang, 'name') and lang.name not in teljes_lista:
            maradek.append(lang.name)
            
    for l_name in sorted(maradek):
        teljes_lista[l_name] = l_name
        
    return teljes_lista

vilag_nyelvei = get_all_languages()
nyelv_kulcsok = list(vilag_nyelvei.keys())

with col1:
    alap_forras = nyelv_kulcsok.index("Hungarian") if "Hungarian" in nyelv_kulcsok else 0
    forras_nyelv = st.selectbox("Erről a nyelvről:", options=nyelv_kulcsok, format_func=lambda x: vilag_nyelvei[x], index=alap_forras)

with col2:
    alap_cel = nyelv_kulcsok.index("French") if "French" in nyelv_kulcsok else 0
    cel_nyelv = st.selectbox("Erre a nyelvre:", options=nyelv_kulcsok, format_func=lambda x: vilag_nyelvei[x], index=alap_cel)

SYSTEM_INSTRUCTION = (
    f"Te egy univerzális, professzionális műszaki, ipari és szakmai szakfordító és tolmács vagy. "
    f"A feladatod a kapott {forras_nyelv} nyelvű hangot azonnal, folyékonyan és hajszálpontosan lefordítani {cel_nyelv} nyelvre. "
    f"Alkalmazz a környezetnek megfelelő, precíz ipari és szakmai szakkifejezéseket. "
    f"Kizárólag a tiszta fordítást add vissza szövegesen, mindenféle extra kommentár, bevezetés vagy magyarázat nélkül."
)

gomb_szoveg = f"Kattints, majd beszélj ({forras_nyelv} ➔ {cel_nyelv})...."

st.write("---")

API_KEY = "AIzaSyDijf4BunkGRbH4ovX91PkIYhrxyvV1uRw"

if API_KEY:
    # Itt kényszerítjük a stabil v1-es Google API-t, így nem lesz 404-es hiba
    genai.configure(api_key=API_KEY, client_options=client_options.ClientOptions(api_version="v1"))

audio_bytes = audio_recorder(
    text=gomb_szoveg,
    recording_color="#e74c3c",
    neutral_color="#3498db",
    icon_size="3x"
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Fordítás folyamatban..."):
        try:
            audio_data = {
                "mime_type": "audio/wav",
                "data": audio_bytes
            }
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            response = model.generate_content([audio_data])
            
            st.success("Fordítás eredménye:")
            st.markdown(f"### {response.text}")
        except Exception as e:
            st.error(f"Hiba történt a fordítás során: {e}")
