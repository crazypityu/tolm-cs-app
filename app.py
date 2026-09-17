import streamlit as st
import google.generativeai as genai
import pycountry

# 1. Oldalkonfiguráció
st.set_page_config(
    page_title="Crazyfordító",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Célzott CSS: A Partner teljes felső blokkjának és mikrofonjának 180 fokos forgatása
st.markdown("""
<style>
/* Mobil lehúzás letiltása */
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
}

/* Felső blokkban lévő mikrofon 180 fokos forgatása */
div[data-testid="stVerticalBlock"]:has(.card-p) div[data-testid="stAudioInput"] {
    transform: rotate(180deg) !important;
    transform-origin: center center !important;
}

/* Mikrofon sávok stílusa és mérete */
div[data-testid="stAudioInput"] {
    background-color: #1f2937 !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 16px !important;
    padding: 10px !important;
    margin: 8px 0 !important;
}

div[data-testid="stAudioInput"] button {
    transform: scale(1.35) !important;
}

/* Kártyák stílusa */
.card-p {
    transform: rotate(180deg) !important;
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 12px;
    margin-top: 8px;
    text-align: center;
    color: #93c5fd;
    font-weight: bold;
}

.card-u {
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 12px;
    margin-top: 8px;
    text-align: center;
    color: #6ee7b7;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 3. Gemini konfiguráció
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

def fordit_beszed(audio_bytes, honnan, hova, hang):
    try:
        modell = get_hang_modell(hang)
        prompt = f"Profi tolmács vagy. Fordítsd le a hallott beszédet {honnan} nyelvről {hova} nyelvre. Csak a pontos fordítást add vissza {hova} nyelven, semmi bevezető szöveget!"
        tartalom = [prompt, {"mime_type": "audio/wav", "data": audio_bytes}]
        valasz = modell.generate_content(tartalom)
        szov = ""
        hang_data = None
        for part in valasz.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                szov += part.text
            elif hasattr(part, "inline_data") and part.inline_data:
                hang_data = part.inline_data.data
        return szov, hang_data
    except Exception as e:
        return f"Hiba: {e}", None

# ==============================================================================
# FELSŐ TÉRFÉL (PARTNER)
# ==============================================================================
# 1. Partner mikrofonja legfelülre (a partner kezéhez közelebb)
p_audio = st.audio_input("Partner mikrofon", key="partner_mic", label_visibility="collapsed")

# 2. Partner felirata
st.markdown(f'<div class="card-p">🗣️ BESZÉLGETŐPARTNER ({partner_lang})</div>', unsafe_allow_html=True)

if p_audio is not None:
    p_id = p_audio.file_id if hasattr(p_audio, "file_id") else p_audio.name
    if st.session_state.get("last_p") != p_id:
        st.session_state["last_p"] = p_id
        with st.spinner("Tolmácsolás..."):
            sz, h = fordit_beszed(p_audio.read(), partner_lang, sajat_lang, partner_voice)
            st.session_state["p_txt"] = sz
            st.session_state["p_snd"] = h

if st.session_state.get("p_txt"):
    st.markdown(f'<div style="transform: rotate(180deg); text-align:center; padding:12px; background:#1e3a8a; border-radius:10px; color:white; font-size:17px; margin-top:8px;">{st.session_state["p_txt"]}</div>', unsafe_allow_html=True)
    if st.session_state.get("p_snd"):
        st.audio(st.session_state["p_snd"], format="audio/wav", autoplay=True)

st.markdown("<hr style='border: 1px solid #374151; margin: 20px 0;'>", unsafe_allow_html=True)

# ==============================================================================
# ALSÓ TÉRFÉL (TE)
# ==============================================================================
if st.session_state.get("u_txt"):
    st.markdown(f'<div style="text-align:center; padding:12px; background:#065f46; border-radius:10px; color:white; font-size:17px; margin-bottom:8px;">{st.session_state["u_txt"]}</div>', unsafe_allow_html=True)
    if st.session_state.get("u_snd"):
        st.audio(st.session_state["u_snd"], format="audio/wav", autoplay=True)

# Saját feliratod
st.markdown(f'<div class="card-u">🗣️ ÉN ({sajat_lang})</div>', unsafe_allow_html=True)

# Saját mikrofonod
u_audio = st.audio_input("Saját mikrofon", key="user_mic", label_visibility="collapsed")

if u_audio is not None:
    u_id = u_audio.file_id if hasattr(u_audio, "file_id") else u_audio.name
    if st.session_state.get("last_u") != u_id:
        st.session_state["last_u"] = u_id
        with st.spinner("Tolmácsolás és kimondás..."):
            sz, h = fordit_beszed(u_audio.read(), sajat_lang, partner_lang, sajat_voice)
            st.session_state["u_txt"] = sz
            st.session_state["u_snd"] = h
