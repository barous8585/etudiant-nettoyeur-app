import streamlit as st
from database import get_connection
from datetime import date


def employee_dashboard(user_id):
    st.title(f"👷 Espace Employé – {st.session_state.get('username')}")

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # STATISTIQUES PERSONNELLES
    # =========================
    st.subheader("📊 Mes performances")

    # Total missions
    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE employee_id = ?",
        (user_id,)
    )
    total_jobs = cursor.fetchone()[0]

    # Missions faites
    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE employee_id = ? AND status = 'À valider'",
        (user_id,)
    )
    done_jobs = cursor.fetchone()[0]


    # Chiffre d'affaires généré
    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.employee_id = ? AND jobs.status = 'Fait'
    """, (user_id,))
    ca = cursor.fetchone()[0]
    ca = ca if ca else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Missions", total_jobs)
    col2.metric("✅ Missions faites", done_jobs)
    col3.metric("💰 CA généré", f"{ca} FCFA")

    st.divider()

    st.divider()
    st.subheader("📝 Créer une mission")

    client_name = st.text_input("Nom du client")

    # Récupérer les services
    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()

    if not services:
        st.warning("Aucun service disponible. Contactez l'administrateur.")
    else:
        service_dict = {s[1]: s[0] for s in services}
        selected_service = st.selectbox(
            "Service à exécuter",
            list(service_dict.keys())
        )

        mission_date = st.date_input(
            "Date de la mission",
            value=date.today()
        )

        if st.button("Créer ma mission"):
            if not client_name:
                st.warning("⚠️ Le nom du client est obligatoire.")
            else:
                cursor.execute("""
                    INSERT INTO jobs (client_name, service_id, employee_id, date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    client_name,
                    service_dict[selected_service],
                    user_id,  # 👈 assigné automatiquement à l'employé connecté
                    mission_date.strftime("%Y-%m-%d"),
                    "En attente"
                ))
                conn.commit()
                st.success("✅ Mission créée avec succès")

    # =========================
    # HISTORIQUE DES MISSIONS
    # =========================
    st.subheader("🗂️ Mon historique")

    cursor.execute("""
        SELECT jobs.client_name, services.name, services.price, jobs.date, jobs.status
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.employee_id = ?
        ORDER BY jobs.date DESC
    """, (user_id,))

    missions = cursor.fetchall()

    if missions:
        for m in missions:
            st.write(
                f"👤 {m[0]} | 🧼 {m[1]} | 💰 {m[2]} FCFA | 📅 {m[3]} | ✅ {m[4]}"
            )
            job_status = m[4]  # statut de la mission
            job_id = m[0]  # ou l'id si tu l’as dans la requête
            if job_status in ["À valider", "Validée"]:
                st.info("🔒 Preuves déjà envoyées. En attente de validation admin.")


    else:
        st.info("Aucune mission pour le moment")
    st.subheader("🕘 Enregistrement de présence")

    # Récupérer les services
    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()

    service_dict = {s[1]: s[0] for s in services}
    service_selected = st.selectbox("Service exécuté", list(service_dict.keys()))

    status = st.radio(
        "Statut du jour",
        ["Présent", "En retard", "Absent"]
    )

    comment = st.text_area("Commentaire (optionnel)")

    if st.button("Enregistrer ma présence"):
        today = date.today().strftime("%Y-%m-%d")

        # Vérifier s'il existe déjà une présence aujourd'hui
        cursor.execute("""
            SELECT id FROM attendance
            WHERE employee_id = ? AND date = ?
        """, (user_id, today))

        already_exists = cursor.fetchone()

        if already_exists:
            st.warning("⚠️ Vous avez déjà enregistré votre présence aujourd’hui.")
        else:
            cursor.execute("""
                INSERT INTO attendance (employee_id, service_id, status, date, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                service_dict[service_selected],
                status,
                today,
                comment
            ))
            conn.commit()
            st.success("✅ Présence enregistrée avec succès")

        cursor.execute("""
            INSERT INTO attendance (employee_id, service_id, status, date, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            service_dict[service_selected],
            status,
            date.today().strftime("%Y-%m-%d"),
            comment
        ))
        conn.commit()
        st.success("✅ Présence enregistrée avec succès")
    st.divider()
    st.subheader("📅 Mon historique de présence")

    cursor.execute("""
        SELECT attendance.date, services.name, attendance.status, attendance.comment
        FROM attendance
        JOIN services ON attendance.service_id = services.id
        WHERE attendance.employee_id = ?
        ORDER BY attendance.date DESC
    """, (user_id,))

    records = cursor.fetchall()

    if records:
        for r in records:
            st.write(
                f"📅 {r[0]} | 🧼 {r[1]} | ⏱️ {r[2]} | 📝 {r[3] if r[3] else ''}"
            )
    else:
        st.info("Aucun enregistrement pour le moment")


    conn.close()
