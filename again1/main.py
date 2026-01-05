import streamlit as st

from auth import login
from admin_dashboard import admin_dashboard
from employee_dashboard import employee_dashboard

st.set_page_config(
    page_title="Étudiant Nettoyeur",
    layout="wide"
)

# Init session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# SIDEBAR
with st.sidebar:
    st.title("🧼 Étudiant Nettoyeur")

    if st.session_state.get("authenticated"):
        st.write(f"👤 {st.session_state.get('username')}")
        if st.button("🚪 Déconnexion"):
            st.session_state.clear()
            st.rerun()
    else:
        st.info("Veuillez vous connecter")

# MAIN
if not st.session_state["authenticated"]:
    login()
else:
    if st.session_state["role"] == "admin":
        admin_dashboard()
    else:
        employee_dashboard(st.session_state["user_id"])
