import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pycountry
import base64

# 1. Oldalbeállítás
st.set_page_config(
    page_title="Crazyfordító",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Letiltjuk a mobil felhúzós frissítést és a felesleges margókat
st.markdown("""
<style>
html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    overscroll-behavior-y: contain !important;
    overscroll-behavior: contain !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
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

# 4. Beállítások oldalsávban
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

# Tolmácsoló függvény
def tolmcsol(audio_base64, honnan, hova, beszelo_hang):
    try:
        raw_bytes = base64.b64decode(audio_base64)
        modell = get_hang_modell(beszelo_hang)
        prompt = f"Profi tolmács vagy. Fordítsd le a hallott beszédet {honnan} nyelvről {hova} nyelvre. Csak a pontos lefordított mondatot mondd ki és írd le {hova} nyelven!"
        tartalom = [prompt, {"mime_type": "audio/webm", "data": raw_bytes}]
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

# Query paraméterek kezelése a komponensből érkező hangadatokhoz
params = st.query_params
if "audio_data" in params and "speaker" in params:
    speaker = params["speaker"]
    b64_data = params["audio_data"]
    st.query_params.clear()
    
    if speaker == "partner":
        szov, snd = tolmcsol(b64_data, partner_lang, sajat_lang, partner_voice)
        st.session_state["partner_text"] = szov
        st.session_state["partner_audio"] = snd
    else:
        szov, snd = tolmcsol(b64_data, sajat_lang, partner_lang, sajat_voice)
        st.session_state["user_text"] = szov
        st.session_state["user_audio"] = snd

# 5. Teljes Képernyős Kétoldalas UI (HTML + JS)
p_text = st.session_state.get("partner_text", "Itt jelenik meg a magyar tolmácsolás...")
u_text = st.session_state.get("user_text", f"Itt jelenik meg a ({partner_lang}) tolmácsolás...")

p_audio_html = ""
if st.session_state.get("partner_audio"):
    b64_snd = base64.b64encode(st.session_state["partner_audio"]).decode()
    p_audio_html = f'<audio autoplay src="data:audio/wav;base64,{b64_snd}"></audio>'

u_audio_html = ""
if st.session_state.get("user_audio"):
    b64_snd = base64.b64encode(st.session_state["user_audio"]).decode()
    u_audio_html = f'<audio autoplay src="data:audio/wav;base64,{b64_snd}"></audio>'

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
    body {{ background-color: #0e1117; color: white; display: flex; flex-direction: column; height: 92vh; justify-content: space-between; overflow: hidden; }}
    
    /* Felső fél: 180 fokkal megfordítva a szemben ülőnek */
    .half-partner {{
        transform: rotate(180deg);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #1e222d;
        border-radius: 20px;
        padding: 15px;
        flex: 1;
        margin-bottom: 8px;
        border: 2px solid #2d3748;
    }}

    /* Alsó fél: Neked néz */
    .half-user {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #1a2332;
        border-radius: 20px;
        padding: 15px;
        flex: 1;
        margin-top: 8px;
        border: 2px solid #2b4365;
    }}

    .title {{ font-size: 14px; font-weight: bold; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; color: #90cdf4; }}
    .textbox {{ width: 95%; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; font-size: 15px; min-height: 45px; text-align: center; margin-bottom: 12px; }}

    /* Hatalmas mikrofon gombok */
    .mic-btn {{
        width: 72px;
        height: 72px;
        border-radius: 50%;
        border: none;
        background: #3182ce;
        color: white;
        font-size: 30px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
    }}

    .recording {{
        background: #e53e3e !important;
        animation: pulse 1.2s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.12); }}
        100% {{ transform: scale(1); }}
    }}
</style>
</head>
<body>

{p_audio_html}
{u_audio_html}

<!-- Felső térfél (Partner) -->
<div class="half-partner">
    <div class="title">🗣️ PARTNER ({partner_lang})</div>
    <div class="textbox">{p_text}</div>
    <button id="pBtn" class="mic-btn" onclick="toggleRecord('partner')">🎤</button>
</div>

<!-- Alsó térfél (Te) -->
<div class="half-user">
    <button id="uBtn" class="mic-btn" onclick="toggleRecord('user')">🎤</button>
    <div class="textbox" style="margin-top: 12px; margin-bottom: 6px;">{u_text}</div>
    <div class="title">🗣️ ÉN ({sajat_lang})</div>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let activeSpeaker = null;

async function toggleRecord(speaker) {
    const pBtn = document.getElementById('pBtn');
    const uBtn = document.getElementById('uBtn');

    if (activeSpeaker === speaker) {
        // Második koppintás: LEÁLLÍTÁS
        mediaRecorder.stop();
        pBtn.classList.remove('recording');
        uBtn.classList.remove('recording');
        activeSpeaker = null;
    } else {
        // Első koppintás: INDÍTÁS
        if (activeSpeaker) return; // ha a másik megy, várjon
        activeSpeaker = speaker;

        const currentBtn = (speaker === 'partner') ? pBtn : uBtn;
        currentBtn.classList.add('recording');

        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {{
                if (event.data.size > 0) audioChunks.push(event.data);
            }};

            mediaRecorder.onstop = () => {{
                const audioBlob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {{
                    const base64Audio = reader.result.split(',')[1];
                    // Visszaküldés a Streamlitnek
                    window.parent.postMessage({{
                        type: "streamlit:setComponentValue",
                        value: null
                    }}, "*");
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("speaker", speaker);
                    url.searchParams.set("audio_data", base64Audio);
                    window.parent.location.href = url.href;
                }};
                stream.getTracks().forEach(track => track.stop());
            }};

            mediaRecorder.start();
        }} catch(err) {{
            alert("Mikrofon hozzáférés szükséges!");
            currentBtn.classList.remove('recording');
            activeSpeaker = null;
        }}
    }
}
</script>
</body>
</html>
""", height=580)
