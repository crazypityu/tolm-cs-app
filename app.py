import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Szakmai Tolmács", page_icon="🎙️", layout="centered")

# --- JELSZÓ VÉDELEM BEÁLLÍTÁSA ---
# Itt vannak a jelszavak. Amit az idézőjelek közé írsz, az lesz a kód!
ERVENYES_JELSZAVAK = ["MesterKód74", "Zolder2026", "Teszt01"]

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
    st.stop() # Megállítja az oldalt, nem mutat semmi mást a jelszóig
# ---------------------------------

st.title("🎙️ Élő Szakmai Tolmács")
st.write("Nyomd meg a mikrofont, beszélj bármilyen nyelven, és a Gemini automatikusan fordítja!")

# Ide másold be az AI Studio-ból kapott API kulcsodat az idézőjelek közé!
API_KEY = "AIzaSyDijf4BunkGRbH4ovX91PkIYhrxyvV1uRw"

if API_KEY and API_KEY != "IDE_MÁSOLD_AZ_AI_STUDIO_API_KULCSODAT":
    genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = "Te egy univerzális, professzionális műszaki, ipari és szakmai fordító-asszisztens vagy. A feladatod a kapott hangot azonnal és pontosan lefordítani a környezetnek megfelelő szakmai nyelvezettel."

audio_bytes = audio_recorder(
    text="Kattints a rögzítéshez...",
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
                model_name="gemini-1.5-pro",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            response = model.generate_content([audio_data])
            
            st.success("Fordítás eredménye:")
            st.markdown(f"### {response.text}")
        except Exception as e:
            st.error(f"Hiba történt a fordítás során: {e}")
