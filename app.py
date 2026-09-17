import streamlit as st
import google.generativeai as genai
import pycountry

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Intelligens Élő Tolmács",
    page_icon="🗣️",
    layout="centered"
)

# 2. Lehúzásos frissítés letiltása mobilon és gombstílus
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
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

# Hangprofilok beállítása a Gemini-ben
# Férfi hang: Puck, Női hang: Aoede
def get_hang_modell(hang_nev="Puck"):
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "response_modalities": ["AUDIO", "TEXT"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": hang_nev
                    }
                }
            }
        }
    )

# 4. Fejléc
st.title("🗣️ Intelligens Élő Tolmács")

# 5. Partner neme választó
st.markdown("### 👤 Kivel beszélgetsz?")
partner_neme = st.radio(
    "Válaszd ki a beszélgetőpartnered nemét:",
    ("Nővel beszélek", "Férfival beszélek"),
    horizontal=True
)

st.markdown("---")

# 6. Nyelvválasztás pycountry alapján
nyelvek = sorted([lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")])

col1, col2 = st.columns(2)
with col1:
    forras_index = nyelvek.index("Hungarian") if "Hungarian" in nyelvek else 0
    forras_nyelv = st.selectbox("Forrásnyelv (aki beszél):", nyelvek, index=forras_index)

with col2:
    cel_index = nyelvek.index("French") if "French" in nyelvek else 1
    cel_nyelv = st.selectbox("Célnyelv (amire fordít):", nyelvek, index=cel_index)

# Hangkarakter meghatározása a tolmácsoláshoz:
# Ha te beszélsz magyarul -> a kimenő hang a te hangod képviseletében mindig Férfi (Puck)
# Ha a partner beszél hozzád -> a felolvasó hang a kiválasztott partner neme (Aoede vagy Puck)
if forras_nyelv == "Hungarian":
    hasznalt_hang = "Puck"       # Te beszélsz -> Férfi hang tolmácsol
else:
    hasznalt_hang = "Aoede" if partner_neme == "Nővel beszélek" else "Puck"

# 7. Szövegbevitel
forras_szoveg = st.text_area(
    "Írd be a mondatot:",
    placeholder="Írd be a lefordítandó szöveget...",
    height=100
)

# 8. Fordítás és hanggenerálás a Geminivel
if st.button("🚀 Fordítás és Kimondás"):
    if forras_szoveg.strip():
        with st.spinner("Tolmácsolás és beszéd generálása..."):
            try:
                modell = get_hang_modell(hasznalt_hang)
                prompt = f"""
                Profi élő tolmács vagy. Fordítsd le az alábbi szöveget {forras_nyelv} nyelvről {cel_nyelv} nyelvre.
                Csak a lefordított mondatot mondd ki és írd le, mindenféle bevezető vagy magyarázat nélkül:
                "{forras_szoveg.strip()}"
                """
                valasz = modell.generate_content(prompt)
                
                # Szöveg és audió kinyerése a válaszból
                szoveg_eredmeny = ""
                audio_bytes = None
                
                for part in valasz.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        szoveg_eredmeny += part.text
                    elif hasattr(part, "inline_data") and part.inline_data:
                        audio_bytes = part.inline_data.data

                st.session_state["eredmeny_szoveg"] = szoveg_eredmeny
                st.session_state["eredmeny_audio"] = audio_bytes
            except Exception as e:
                st.error(f"Hiba történt a generálás során: {e}")
    else:
        st.warning("Kérlek, írj be szöveget a fordításhoz!")

# 9. Eredmény megjelenítése és lejátszása
if "eredmeny_szoveg" in st.session_state and st.session_state["eredmeny_szoveg"]:
    st.subheader(f"Fordítás ({cel_nyelv}):")
    st.success(st.session_state["eredmeny_szoveg"])

    if st.session_state.get("eredmeny_audio"):
        st.audio(st.session_state["eredmeny_audio"], format="audio/wav", autoplay=True)
