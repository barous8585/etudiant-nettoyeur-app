import streamlit as st
from database import get_connection
from security import verify_password


def login():
    st.subheader("Connexion")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password, role FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()

        if user and verify_password(password, user[1]):
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["role"] = user[2]
            st.session_state["username"] = username
            st.success(f"Bienvenue {username}")
            st.rerun()
        else:
            st.error("Identifiants incorrects")
