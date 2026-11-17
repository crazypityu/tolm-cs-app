import streamlit as st
import streamlit.components.v1 as components
from google import generativeai as genai

# Oldal konfiguráció
st.set_page_config(
    page_title="Crazyfordító - Two-Way Interpreter",
    page_icon="🎙️",
    layout="centered"
)

# Egyedi CSS: Kétnyelvű, kesztyűbarát gombok és sötét módú elrendezés
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sticky-buttons {
        position: sticky;
        top: 0;
        background-color: #0e1117;
        z-index: 999;
        padding-bottom: 10px;
        padding-top: 10px;
        border-bottom: 1px solid #30363d;
    }
    div.stButton > button {
        width: 100% !important;
        height: 4.2em !important;
        font-size: 14px !important;
        font-weight: bold;
        color: white !important;
        border-radius: 16px !important;
        border: none !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #1b5e20 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover {
        background-color: #2e7d32 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #b71c1c !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background-color: #c62828 !important;
    }
    .chat-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# Címsor két nyelven
st.title("🎙️ Crazyfordító / Traducteur")
st.write("Élő kétnyelvű szinkrontolmács | Interprète bilingue (Magyar ⇄ Français)")

# API kulcs ellenőrzése
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hiányzik a GEMINI_API_KEY a Streamlit Secrets-ből!")
    st.stop()

# Állapotkezelés (Alapból bekapcsolva indul, hogy rögtön tudd tesztelni)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = True
if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

st.markdown("---")

# Vezérlő gombok kétnyelvű felirattal
st.markdown('<div class="sticky-buttons">', unsafe_allow_html=True)
col_start, col_stop = st.columns(2)
with col_start:
    start_btn = st.button("🟢 INDÍTÁS / DÉMARRER")
with col_stop:
    stop_btn = st.button("🔴 LEÁLLÍTÁS / ARRÊTER")
st.markdown('</div>', unsafe_allow_html=True)

if start_btn:
    st.session_state.is_running = True
    st.session_state.chat_history = []
    st.session_state.last_audio_bytes = None

if stop_btn:
    st.session_state.is_running = False
    st.session_state.last_audio_bytes = None

# Diagnosztikai panel: kiírja a képernyőre, miért akad el a mikrofon
components.html("""
    <div style="background:#161b22; padding:12px; border-radius:10px; border:1px solid #f39c12; font-family:sans-serif;">
        <button onclick="testMic()" style="background:#f39c12; color:#000;
