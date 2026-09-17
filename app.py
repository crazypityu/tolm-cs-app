import streamlit as st
import google.generativeai as genai
import pycountry

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Crazyfordító",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Letiltjuk a felhúzós frissítést és megformázzuk a két térfelet
st.markdown("""
<style>
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
}

/* Felső fél: 180 fokkal fejjel lefelé a partnernek */
.partner-container {
    transform: rotate(180deg);
    background-color: #1a202c;
    border: 2px solid #4a5568;
    border-radius: 20px;
    padding: 16px;
    margin-bottom: 20px;
    text-align: center;
}

/* Alsó fél: Neked néz */
.user-container {
    background-color: #171923;
    border: 2px solid #2b6cb0;
    border-radius: 20px;
    padding: 16px;
    margin-top: 20px;
    text-align: center;
}

.title-partner {
    color: #63b3ed;
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 10px;
}

.title-user {
    color: #4fd1c5;
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Mikrofon méretének megnövelése */
div[data-testid="stAudioInput"] {
    transform: scale(1.15);
    margin: 10px auto;
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

# 4. Oldalsáv beállítások
with st.sidebar:
    st.header("⚙️ Beállítások")
    nyelvek = sorted([lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")])
    partner_neme = st.radio("Partner neme:", ("Nő", "Férfi"), horizontal=True)
    p_lang_idx = nyelvek.index("French") if "French" in nyelvek else 1
    partner_lang = st.selectbox("Partner nyelve:", nyelvek, index=p_lang_idx)
    u_lang_idx = nyelvek.index("Hungarian") if "Hungarian" in nyelvek else 0
    sajat_lang = st.selectbox("Saját nyelved:", nyelvek, index=u_lang_idx)

partner_voice = "Aoede" if partner_neme == "Nő" else "Puck"
sajat_voice = "Puck"

def fordit_beszed(audio_data, honnan, hova, beszelo_hang):
    try:
        modell = get_hang_modell(beszelo_hang)
        prompt = f"Profi tolmács vagy. Fordítsd le a hallott szöveget {honnan} nyelvről {hova} nyelvre. Csak a lefordított mondatot mondd ki és írd le ezen a célnyelven ({hova}), mindenféle magyarázat nélkül!"
        tartalom = [
            prompt,
            {"mime_type": "audio/wav", "data": audio_data}
        ]
        valasz = modell.generate_content(tartalom)
        
        szov = ""
        hang = None
        for part in valasz.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                szov += part.text
            elif hasattr(part, "inline_data") and part.inline_data:
                hang = part.inline_data.data
        return szov, hang
    except Exception as e:
        return f"Hiba: {e}", None

# ===================================================
# FELSŐ TÉRFÉL (PARTNER - 180 FOKKAL ELFORGATVA)
# ===================================================
st.markdown('<div class="partner-container">', unsafe_allow_html=True)
st.markdown(f'<div class="title-partner">🗣️ PARTNER ({partner_lang})</div>', unsafe_allow_html=True)

partner_mic = st.audio_input("Partner felvétel", key="p_mic_input", label_visibility="collapsed")

if partner_mic is not None:
    mic_id = partner_mic.file_id if hasattr(partner_mic, "file_id") else partner_mic.name
    if st.session_state.get("last_p_id") != mic_id:
        st.session_state["last_p_id"] = mic_id
        with st.spinner("Fordítás..."):
            audio_bytes = partner_mic.read()
            sz, hg = fordit_beszed(audio_bytes, partner_lang, sajat_lang, partner_voice)
            st.session_state["p_forditas"] = sz
            st.session_state["p_hang"] = hg

if st.session_state.get("p_forditas"):
    st.info(st.session_state["p_forditas"])
    if st.session_state.get("p_hang"):
        st.audio(st.session_state["p_hang"], format="audio/wav", autoplay=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ===================================================
# ALSÓ TÉRFÉL (TE - NORMÁL ÁLLÁS)
# ===================================================
st.markdown('<div class="user-container">', unsafe_allow_html=True)
st.markdown(f'<div class="title-user">🗣️ ÉN ({sajat_lang})</div>', unsafe_allow_html=True)

sajat_mic = st.audio_input("Saját felvétel", key="u_mic_input", label_visibility="collapsed")

if sajat_mic is not None:
    mic_id = sajat_mic.file_id if hasattr(sajat_mic, "file_id") else sajat_mic.name
    if st.session_state.get("last_u_id") != mic_id:
        st.session_state["last_u_id"] = mic_id
        with st.spinner("Tolmácsolás és beszéd..."):
            audio_bytes = sajat_mic.read()
            sz, hg = fordit_beszed(audio_bytes, sajat_lang, partner_lang, sajat_voice)
            st.session_state["u_forditas"] = sz
            st.session_state["u_hang"] = hg

if st.session_state.get("u_forditas"):
    st.success(st.session_state["u_forditas"])
    if st.session_state.get("u_hang"):
        st.audio(st.session_state["u_hang"], format="audio/wav", autoplay=True)

st.markdown('</div>', unsafe_allow_html=True)
