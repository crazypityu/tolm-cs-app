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
# 6 nyelvű azonnali szakmai bemutatkozás
    if st.button(f"📢 Bemutatkozás a kollégának ({cel_nyelv} nyelven)"):
        intros = {
            "French": "Bonjour ! Je m'appelle István Molnár. Je suis serrurier-métallier. Cette application traduit notre conversation en direct, vous pouvez parler naturellement en français !",
            "Dutch": "Hallo! Mijn naam is István Molnár, ik ben metaalbewerker. Deze app vertaalt ons gesprek live, u kunt gewoon in het Nederlands praten!",
            "German": "Guten Tag! Mein Name ist István Molnár, ich bin Metallbauer. Diese App übersetzt unser Gespräch live, sprechen Sie einfach auf Deutsch!",
            "English": "Hello! My name is István Molnár, metal construction technician. This app translates our conversation live, feel free to speak in English!",
            "Italian": "Buongiorno! Mi chiamo István Molnár, sono un carpentiere metallico. Questa applicazione traduce la nostra conversazione dal vivo, parli pure in italiano!",
            "Spanish": "¡Hola! Me llamo István Molnár, soy cerrajero y montador. Esta aplicación traduce nuestra conversación en vivo, ¡hable en español con tranquilidad!"
        }
        bemutatkozas_szoveg = intros.get(
            cel_nyelv, 
            "Üdvözlöm! Ez az alkalmazás élőben fordítja a beszélgetésünket, nyugodtan beszéljen a saját anyanyelvén!"
        )
        st.info(f"👋 **{bemutatkozas_szoveg}**")

st.write("---")  

SYSTEM_INSTRUCTION = (
    "Te egy professzionális, kétirányú ipari és műszaki tolmács vagy. "
    "A feladatod a beérkező hanganyag automata felismerése és lefordítása: "
    "1. Ha a beszélő MAGYARUL beszél, fordítsd azonnal precíz, szakmai FRANCIA nyelvre. "
    "2. Ha a beszélő FRANCIA nyelven beszél, fordítsd azonnal pontos, szakmai MAGYAR nyelvre. "
    "Alkalmazz helytálló műszaki és szerkezeti terminológiát. "
    "Kizárólag a lefordított mondatot add vissza szövegként, mindenféle bevezető vagy magyarázat nélkül!"
)

gomb_szoveg = f"Kattints, majd beszélj ({forras_nyelv} ➔ {cel_nyelv})...."

st.write("---")

API_KEY = "AIzaSyDijf4BunkGRbH4ovX91PkIYhrxyvV1uRw"

if API_KEY:
    genai.configure(api_key=API_KEY)   

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
