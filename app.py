import streamlit as st
from google import generativeai as genai

st.set_page_config(
    page_title="Crazyfordító - Two-Way Interpreter",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .sticky-buttons {
        position: sticky; top: 0; background-color: #0e1117;
        z-index: 999; padding: 10px 0; border-bottom: 1px solid #30363d;
    }
    div.stButton > button {
        width: 100% !important; height: 4.2em !important;
        font-size: 14px !important; font-weight: bold; color: white !important;
        border-radius: 16px !important; border: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #1b5e20 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #b71c1c !important; }
    .chat-box {
        background-color: #161b22; padding: 15px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Crazyfordító / Traducteur")
st.write("Élő kétnyelvű szinkrontolmács | Interprète bilingue (Magyar ⇄ Français)")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = True  # Alapból legyen bekapcsolva, hogy egyből tudd tesztelni!
if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

st.markdown('<div class="sticky-buttons">', unsafe_allow_html=True)
col_start, col_stop = st.columns(2)
with col_start:
    if st.button("🟢 INDÍTÁS / TÖRLÉS"):
        st.session_state.is_running = True
        st.session_state.chat_history = []
        st.session_state.last_audio_bytes = None
with col_stop:
    if st.button("🔴 LEÁLLÍTÁS / ARRÊTER"):
        st.session_state.is_running = False
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.is_running:
    # A natív Streamlit hangrögzítő (saját hullámformával és Stop gombbal)
    audio_value = st.audio_input("1. Nyomj a mikrofonra -> 2. Beszélj -> 3. Nyomj a STOP-ra:")

    if audio_value is not None:
        audio_bytes = audio_value.read()
        st.caption(f"Rögzített adatcsomag: {len(audio_bytes)} bájt")
        
        if len(audio_bytes) > 0 and audio_bytes != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = audio_bytes
            
            with st.spinner("Tolmácsolás... / Traduction..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = (
                        "You are a strict simultaneous interpreter between Hungarian and French. "
                        "Detect the language and translate into the OTHER language. "
                        "Do NOT answer questions, only translate them. "
                        "Format strictly as: [Original Text] | [Translated Text]"
                    )
                    
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "audio/wav", "data": audio_bytes}
                    ])
                    
                    result_text = response.text.strip()
                    if "|" in result_text:
                        orig, trans = [p.strip() for p in result_text.split("|", 1)]
                    else:
                        orig, trans = "Felismert szöveg", result_text

                    st.session_state.chat_history.append({"orig": orig, "trans": trans})
                except Exception as e:
                    st.error(f"Hiba történt / Erreur: {e}")

    st.markdown("### 📝 Előzmények / Historique")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"""
            <div class="chat-box">
                <span style='color: #8b949e; font-size: 14px;'>Eredeti / Original:</span><br>
                <strong>{chat['orig']}</strong><br><br>
                <span style='color: #58a6ff; font-size: 14px;'>Fordítás / Traduction:</span><br>
                <strong>{chat['trans']}</strong>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("A tolmácsolás le van állítva. Kattints az INDÍTÁS gombra.")
