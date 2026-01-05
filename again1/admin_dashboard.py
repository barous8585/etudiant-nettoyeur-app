import streamlit as st
import pandas as pd
from io import BytesIO
from database import get_connection
from datetime import date
from security import hash_password
from datetime import date


def admin_dashboard():
    st.title("Dashboard Admin")

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # CRÉATION EMPLOYÉ
    # =========================
    st.subheader("👷 Créer un employé")

    emp_username = st.text_input("Nom d'utilisateur employé")
    emp_password = st.text_input("Mot de passe", type="password")

    if st.button("Créer l'employé"):
        if emp_username and emp_password:
            try:
                hashed_pw = hash_password(emp_password)
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'employee')",
                    (emp_username, hashed_pw)
                )

                conn.commit()
                st.success("✅ Employé créé avec succès")
            except:
                st.error("❌ Ce nom d'utilisateur existe déjà")
        else:
            st.warning("⚠️ Remplis tous les champs")

    st.divider()

    # =========================
    # AJOUT SERVICE
    # =========================
    st.subheader("🧼 Ajouter un service")

    service_name = st.text_input("Nom du service")
    service_price = st.number_input("Prix", min_value=0)

    if st.button("Ajouter le service"):
        cursor.execute(
            "INSERT INTO services (name, price) VALUES (?, ?)",
            (service_name, service_price)
        )
        conn.commit()
        st.success("Service ajouté")

    st.divider()

    # =========================
    # CRÉATION MISSION
    # =========================
    st.subheader("📋 Créer une mission")

    # Clients
    client_name = st.text_input("Nom du client")

    # Services
    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()
    service_dict = {s[1]: s[0] for s in services}
    selected_service = st.selectbox("Service", list(service_dict.keys()))

    # Employés
    cursor.execute("SELECT id, username FROM users WHERE role='employee'")
    employees = cursor.fetchall()
    employee_dict = {e[1]: e[0] for e in employees}
    selected_employee = st.selectbox("Employé", list(employee_dict.keys()))

    mission_date = st.date_input("Date de la mission", value=date.today())
    status = st.selectbox("Statut", ["Prévu", "Fait"])

    if st.button("Créer la mission"):
        if client_name:
            cursor.execute("""
                INSERT INTO jobs (client_name, service_id, employee_id, date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                client_name,
                service_dict[selected_service],
                employee_dict[selected_employee],
                mission_date.strftime("%Y-%m-%d"),
                status
            ))
            conn.commit()
            st.success("✅ Mission créée avec succès")
        else:
            st.warning("⚠️ Nom du client obligatoire")

    st.divider()
    st.subheader("📊 Statistiques")

    # -------------------------
    # CHIFFRE D'AFFAIRES TOTAL
    # -------------------------
    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.status = 'Fait'
    """)
    total_ca = cursor.fetchone()[0]
    total_ca = total_ca if total_ca else 0

    st.metric("💰 Chiffre d'affaires total", f"{total_ca} FCFA")

    # -------------------------
    # NOMBRE DE MISSIONS
    # -------------------------
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    st.metric("📋 Nombre total de missions", total_jobs)

    # -------------------------
    # MISSIONS PAR EMPLOYÉ
    # -------------------------
    st.subheader("👷 Missions par employé")

    cursor.execute("""
        SELECT users.username, COUNT(jobs.id)
        FROM jobs
        JOIN users ON jobs.employee_id = users.id
        GROUP BY users.username
    """)
    stats_employees = cursor.fetchall()

    for emp in stats_employees:
        st.write(f"• {emp[0]} : {emp[1]} mission(s)")

    # -------------------------
    # SERVICES LES PLUS UTILISÉS
    # -------------------------
    st.subheader("🧼 Services les plus demandés")

    cursor.execute("""
        SELECT services.name, COUNT(jobs.id)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        GROUP BY services.name
        ORDER BY COUNT(jobs.id) DESC
    """)
    stats_services = cursor.fetchall()

    for s in stats_services:
        st.write(f"• {s[0]} : {s[1]} fois")

    st.divider()
    st.subheader("📤 Export des données")

    cursor.execute("""
        SELECT
            jobs.client_name AS Client,
            users.username AS Employé,
            services.name AS Service,
            services.price AS Prix,
            jobs.date AS Date,
            jobs.status AS Statut
        FROM jobs
        JOIN users ON jobs.employee_id = users.id
        JOIN services ON jobs.service_id = services.id
        ORDER BY jobs.date DESC
    """)

    rows = cursor.fetchall()
    columns = ["Client", "Employé", "Service", "Prix", "Date", "Statut"]

    if rows:
        df = pd.DataFrame(rows, columns=columns)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Missions")

        st.download_button(
            label="📥 Télécharger le rapport Excel",
            data=buffer.getvalue(),
            file_name="rapport_missions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Aucune donnée à exporter")

    st.divider()
    st.header("🕘 Suivi des présences des employés")

    # 🔍 Filtres
    selected_date = st.date_input(
        "Filtrer par date",
        value=date.today()
    )

    cursor.execute("""
        SELECT
            attendance.date,
            users.username,
            services.name,
            attendance.status,
            attendance.comment
        FROM attendance
        JOIN users ON attendance.employee_id = users.id
        JOIN services ON attendance.service_id = services.id
        WHERE attendance.date = ?
        ORDER BY users.username
    """, (selected_date.strftime("%Y-%m-%d"),))

    records = cursor.fetchall()

    if records:
        for r in records:
            st.write(
                f"📅 {r[0]} | 👷 {r[1]} | 🧼 {r[2]} | ⏱️ {r[3]} | 📝 {r[4] if r[4] else ''}"
            )
    else:
        st.info("Aucune présence enregistrée pour cette date.")

    st.divider()
    st.header("📊 Statistiques RH (Présence / Retard / Absence)")

    # Sélection du mois
    selected_month = st.date_input(
        "Sélectionner un mois",
        value=date.today()
    )

    month_str = selected_month.strftime("%Y-%m")

    # =========================
    # STATS GLOBALES DU MOIS
    # =========================
    cursor.execute("""
        SELECT status, COUNT(*)
        FROM attendance
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY status
    """, (month_str,))

    stats = dict(cursor.fetchall())

    present = stats.get("Présent", 0)
    late = stats.get("En retard", 0)
    absent = stats.get("Absent", 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Présences", present)
    col2.metric("🟠 Retards", late)
    col3.metric("🔴 Absences", absent)

    # =========================
    # STATS PAR EMPLOYÉ
    # =========================
    st.subheader("👷 Détail par employé")

    cursor.execute("""
        SELECT
            users.username,
            SUM(CASE WHEN attendance.status = 'Présent' THEN 1 ELSE 0 END),
            SUM(CASE WHEN attendance.status = 'En retard' THEN 1 ELSE 0 END),
            SUM(CASE WHEN attendance.status = 'Absent' THEN 1 ELSE 0 END)
        FROM attendance
        JOIN users ON attendance.employee_id = users.id
        WHERE strftime('%Y-%m', attendance.date) = ?
        GROUP BY users.username
        ORDER BY users.username
    """, (month_str,))

    rows = cursor.fetchall()

    if rows:
        for r in rows:
            st.write(
                f"👤 {r[0]} | 🟢 {r[1]} | 🟠 {r[2]} | 🔴 {r[3]}"
            )
    else:
        st.info("Aucune donnée pour ce mois.")

    st.divider()
    st.header("🛂 Validation des missions (employés)")

    cursor.execute("""
        SELECT jobs.id, jobs.client_name, users.username, services.name, jobs.date
        FROM jobs
        JOIN users ON jobs.employee_id = users.id
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.status = 'En attente'
        ORDER BY jobs.date
    """)

    pending_jobs = cursor.fetchall()

    if not pending_jobs:
        st.info("Aucune mission en attente.")
    else:
        for j in pending_jobs:
            st.markdown(
                f"📋 **{j[1]}** | 👷 {j[2]} | 🧼 {j[3]} | 📅 {j[4]}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Valider", key=f"validate_{j[0]}"):
                    cursor.execute(
                        "UPDATE jobs SET status = 'Prévu' WHERE id = ?",
                        (j[0],)
                    )
                    conn.commit()
                    st.success("Mission validée")

            with col2:
                if st.button("❌ Refuser", key=f"رفض_{j[0]}"):
                    cursor.execute(
                        "UPDATE jobs SET status = 'Refusé' WHERE id = ?",
                        (j[0],)
                    )
                    conn.commit()
                    st.warning("Mission refusée")
    st.divider()
    st.header("🧾 Validation des preuves terrain")

    cursor.execute("""
        SELECT
            jobs.id,
            jobs.client_name,
            users.username,
            services.name,
            jobs.photo_before,
            jobs.photo_after,
            jobs.employee_note
        FROM jobs
        JOIN users ON jobs.employee_id = users.id
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.status = 'À valider'
        ORDER BY jobs.date
    """)

    to_validate = cursor.fetchall()

    if not to_validate:
        st.info("Aucune preuve à valider.")
    else:
        for j in to_validate:
            st.markdown(
                f"📋 **{j[1]}** | 👷 {j[2]} | 🧼 {j[3]}"
            )

            if j[4]:
                st.image(j[4], caption="Avant", width=200)
            if j[5]:
                st.image(j[5], caption="Après", width=200)

            st.write(f"📝 Commentaire employé : {j[6] if j[6] else '—'}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Valider définitivement", key=f"proof_ok_{j[0]}"):
                    cursor.execute(
                        "UPDATE jobs SET status = 'Validée' WHERE id = ?",
                        (j[0],)
                    )
                    conn.commit()
                    st.success("Mission validée et verrouillée")

            with col2:
                if st.button("❌ Refuser (corriger)", key=f"proof_no_{j[0]}"):
                    cursor.execute(
                        "UPDATE jobs SET status = 'Prévu' WHERE id = ?",
                        (j[0],)
                    )
                    conn.commit()
                    st.warning("Preuve refusée — retour à l’employé")
                else:
                    photo_before = st.file_uploader(...)
                    photo_after = st.file_uploader(...)
                    note = st.text_area(...)

                    if st.button("📤 Envoyer les preuves"):
                        ...

    conn.close()
