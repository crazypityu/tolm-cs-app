import streamlit as st
import streamlit.components.v1 as components

# 1. Lap konfiguráció
st.set_page_config(
    page_title="Tolmács App",
    page_icon="🗣️",
    layout="centered"
)

# 2. Pull-to-refresh (véletlen lehúzásos frissítés) letiltása
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
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

# 3. Fejléc és tesztfelület
st.title("🗣️ Kétnyelvű Tolmács")
st.write("Magyar ⇄ Francia azonnali fordító és hangszóró teszt.")

# --- HANGSZÓRÓ TESZT GOMB ---
if st.button("🔊 Üdvözlet felolvasása (Hangteszt)"):
    components.html("""
    <script>
        const uzenet = new SpeechSynthesisUtterance("Üdvözöllek! A hangszóró és a tolmács rendszer működik.");
        uzenet.lang = 'hu-HU';
        uzenet.rate = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(uzenet);
    </script>
    """, height=0)

st.markdown("---")

# 4. Irányválasztás
irany = st.radio(
    "Válassz fordítási irányt:",
    ("Magyar ➔ Francia", "Francia ➔ Magyar"),
    horizontal=True
)

# 5. Szövegbevitel
forras_szoveg = st.text_area(
    "Írd vagy másold be a szöveget:",
    placeholder="Írj be egy mondatot a teszteléshez...",
    height=100
)

# 6. Minta szótár az azonnali kipróbáláshoz (API kulcs nélkül is tesztelhető)
minta_forditasok = {
    "Magyar ➔ Francia": {
        "szia": "Bonjour",
        "hogy vagy": "Comment ça va ?",
        "jó napot": "Bonjour, bonne journée",
        "egészségedre": "Santé !"
    },
    "Francia ➔ Magyar": {
        "bonjour": "Jó napot kívánok",
        "merci": "Köszönöm",
        "santé": "Egészségedre !"
    }
}

forditas_eredmeny = ""
beszed_nyelv = "fr-FR" if irany == "Magyar ➔ Francia" else "hu-HU"

if st.button("🔄 Fordítás"):
    if forras_szoveg.strip():
        keresett = forras_szoveg.strip().lower()
        forditas_eredmeny = minta_forditasok.get(irany, {}).get(
            keresett,
            f"[{'FR' if irany == 'Magyar ➔ Francia' else 'HU'}] {forras_szoveg}"
        )
        st.session_state["utolso_forditas"] = forditas_eredmeny
        st.session_state["beszed_nyelv"] = beszed_nyelv
    else:
        st.warning("Kérlek, írj be szöveget a fordításhoz!")

# 7. Eredmény megjelenítése és felolvasása
if "utolso_forditas" in st.session_state and st.session_state["utolso_forditas"]:
    st.subheader("Fordítás eredménye:")
    st.info(st.session_state["utolso_forditas"])

    if st.button("🔊 Fordítás felolvasása"):
        szoveg_js = st.session_state["utolso_forditas"].replace("'", "\\'").replace('"', '\\"')
        lang_js = st.session_state.get("beszed_nyelv", "fr-FR")
        components.html(f"""
        <script>
            const uzenet = new SpeechSynthesisUtterance('{szoveg_js}');
            uzenet.lang = '{lang_js}';
            uzenet.rate = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(uzenet);
        </script>
        """, height=0)
