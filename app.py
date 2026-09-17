import streamlit as st
import google.generativeai as genai
import pycountry

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Élő Tolmács",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Speciális Face-to-Face stílusok és mobilvédelem
st.markdown("""
<style>
/* Mobil lehúzás letiltása */
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
}

/* Felső fél: 180 fokos elforgatás a szemben ülő partnernek */
.partner-zone {
    transform: rotate(180deg);
    background-color: #f0f4f9;
    padding: 15px;
    border-radius: 16px;
    margin-bottom: 25px;
    border: 2px solid #d3e3fd;
}

/* Alsó fél: a te oldalad */
.user-zone {
    background-color: #fdfdfd;
    padding: 15px;
    border-radius: 16px;
    margin-top: 10px;
    border: 2px solid #c2e7ff;
}

/* Hatalmas mikrofon gombok és kezelők */
div[data-testid="stAudioInput"] {
    transform: scale(1.15);
    margin: 15px auto;
}

/* Címkék kiemelése */
.zone-title {
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 8px;
    color: #1a73e8;
}
</style>
""", unsafe_allow_html=True)

# 3. Gemini API konfiguráció
api_kulcs = st.secrets.get("GEMINI_API_KEY")
if not api_kulcs:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

genai.configure(api_key=api_kulcs)

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

# 4. Oldalsáv beállítások (hogy ne foglalja a helyet a képernyőn)
with st.sidebar:
    st.header("⚙️ Beállítások")
    nyelvek = sorted([lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")])
    
    partner_neme = st.radio(
        "Partner neme (hangkarakter):",
        ("Nő", "Férfi"),
        horizontal=True
    )
    
    p_lang_idx = nyelvek.index("French") if "French" in nyelvek else 1
    partner_lang = st.selectbox("Partner nyelve:", nyelvek, index=p_lang_idx)
    
    u_lang_idx = nyelvek.index("Hungarian") if "Hungarian" in nyelvek else 0
    sajat_lang = st.selectbox("Saját nyelved:", nyelvek, index=u_lang_idx)

# Partner hangjának kiválasztása
partner_voice = "Aoede" if partner_neme == "Nő" else "Puck"
sajat_voice = "Puck"

# Tolmácsoló függvény
def fordit_es_mond(audio_file, honnan, hova, beszelo_hang):
    try:
        modell = get_hang_modell(beszelo_hang)
        prompt = f"Profi tolmács vagy. Fordítsd le a hallott beszédet {honnan} nyelvről {hova} nyelvre. Csak a lefordított mondatot add vissza és mondd ki {hova} nyelven, semmi mást!"
        tartalom = [
            prompt,
            {"mime_type": "audio/wav", "data": audio_file.read()}
        ]
        valasz = modell.generate_content(tartalom)
        
        szoveg = ""
        hang = None
        for part in valasz.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                szoveg += part.text
            elif hasattr(part, "inline_data") and part.inline_data:
                hang = part.inline_data.data
        return szoveg, hang
    except Exception as e:
        return f"Hiba: {e}", None

# ==========================================
# PARTNER ZÓNA (FELÜL - 180°-KAL ELFORGATVA)
# ==========================================
st.markdown('<div class="partner-zone">', unsafe_allow_html=True)
st.markdown(f'<div class="zone-title">🗣️ PARTNER ({partner_lang})</div>', unsafe_allow_html=True)

# Partner mikrofonja
partner_audio = st.audio_input("Partner mikrofon", key="partner_mic", label_visibility="collapsed")

if partner_audio is not None:
    if st.session_state.get("last_p_audio") != partner_audio:
        st.session_state["last_p_audio"] = partner_audio
        with st.spinner("Fordítás..."):
            szov, snd = fordit_es_mond(partner_audio, partner_lang, sajat_lang, partner_voice)
            st.session_state["p_forditas_szoveg"] = szov
            st.session_state["p_forditas_hang"] = snd

if st.session_state.get("p_forditas_szoveg"):
    st.info(st.session_state["p_forditas_szoveg"])
    if st.session_state.get("p_forditas_hang"):
        st.audio(st.session_state["p_forditas_hang"], format="audio/wav", autoplay=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SAJÁT ZÓNA (ALUL - FELÉD NÉZ)
# ==========================================
st.markdown('<div class="user-zone">', unsafe_allow_html=True)
st.markdown(f'<div class="zone-title">🗣️ ÉN ({sajat_lang})</div>', unsafe_allow_html=True)

# Saját mikrofonod
sajat_audio = st.audio_input("Saját mikrofon", key="sajat_mic", label_visibility="collapsed")

if sajat_audio is not None:
    if st.session_state.get("last_u_audio") != sajat_audio:
        st.session_state["last_u_audio"] = sajat_audio
        with st.spinner("Tolmácsolás és kimondás..."):
            szov, snd = fordit_es_mond(sajat_audio, sajat_lang, partner_lang, sajat_voice)
            st.session_state["u_forditas_szoveg"] = szov
            st.session_state["u_forditas_hang"] = snd

if st.session_state.get("u_forditas_szoveg"):
    st.success(st.session_state["u_forditas_szoveg"])
    if st.session_state.get("u_forditas_hang"):
        st.audio(st.session_state["u_forditas_hang"], format="audio/wav", autoplay=True)

st.markdown('</div>', unsafe_allow_html=True)
