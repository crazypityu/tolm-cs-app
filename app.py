import streamlit as st
import google.generativeai as genai
import pycountry

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Intelligens Élő Tolmács",
    page_icon="🗣️",
    layout="centered"
)

# 2. Lehúzásos frissítés letiltása (CSS + JS) és gombstílus
st.markdown("""
<style>
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
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

<script>
let startY = 0;
window.addEventListener('touchstart', function (e) {
    if (e.touches.length === 1) {
        startY = e.touches[0].clientY;
    }
}, { passive: true });

window.addEventListener('touchmove', function (e) {
    if (e.touches.length === 1) {
        const currentY = e.touches[0].clientY;
        if (window.scrollY === 0 && currentY > startY) {
            e.preventDefault();
        }
    }
}, { passive: false });
</script>
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

# 7. Hang- és szövegbevitel
st.markdown("### 🎙️ Mondd be a mondatot vagy írd le:")
audio_bemenet = st.audio_input("Beszélj a mikrofonba:")

forras_szoveg = st.text_area(
    "Vagy írd be szövegként (ha nem mikrofont használsz):",
    placeholder="Írd be a lefordítandó szöveget...",
    height=80
)

# 8. Fordítás és hanggenerálás a Geminivel
if st.button("🚀 Fordítás és Kimondás"):
    if audio_bemenet is not None or forras_szoveg.strip():
        with st.spinner("Tolmácsolás és beszéd generálása..."):
            try:
                modell = get_hang_modell(hasznalt_hang)
                prompt_szoveg = f"""
                Profi élő tolmács vagy. Fordítsd le az elhangzott/leírt szöveget {forras_nyelv} nyelvről {cel_nyelv} nyelvre.
                Csak a lefordított mondatot mondd ki és írd le ezen a célnyelven ({cel_nyelv}), mindenféle bevezető vagy magyarázat nélkül!
                """
                
                # Tartalom összeállítása: hang vagy szöveg
                tartalom = [prompt_szoveg]
                if audio_bemenet is not None:
                    audio_bytes_input = audio_bemenet.read()
                    tartalom.append({
                        "mime_type": "audio/wav",
                        "data": audio_bytes_input
                    })
                elif forras_szoveg.strip():
                    tartalom.append(f'Szöveg: "{forras_szoveg.strip()}"')

                valasz = modell.generate_content(tartalom)
                
                # Szöveg és audió kinyerése a válaszból
                szoveg_eredmeny = ""
                audio_bytes_output = None
                
                for part in valasz.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        szoveg_eredmeny += part.text
                    elif hasattr(part, "inline_data") and part.inline_data:
                        audio_bytes_output = part.inline_data.data

                st.session_state["eredmeny_szoveg"] = szoveg_eredmeny
                st.session_state["eredmeny_audio"] = audio_bytes_output
            except Exception as e:
                st.error(f"Hiba történt a generálás során: {e}")
    else:
        st.warning("Kérlek, beszélj a mikrofonba vagy írj be szöveget!")

# 9. Eredmény megjelenítése és lejátszása
if "eredmeny_szoveg" in st.session_state and st.session_state["eredmeny_szoveg"]:
    st.markdown("---")
    st.subheader(f"Fordítás ({cel_nyelv}):")
    st.success(st.session_state["eredmeny_szoveg"])

    if st.session_state.get("eredmeny_audio"):
        # A Gemini közvetlen WAV/PCM audiója azonnali lejátszással
        st.audio(st.session_state["eredmeny_audio"], format="audio/wav", autoplay=True)
