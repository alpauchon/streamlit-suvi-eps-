import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os

st.set_page_config(page_title="Suivi EPS", layout="wide", page_icon=":rocket:")

# FOND DYNAMIQUE (gradient animé)
st.markdown("""
    <style>
    body {
        background: linear-gradient(120deg, #1d2671, #c33764, #43cea2, #185a9d, #2af598, #009efd);
        background-size: 1600% 1600%;
        animation: gradientBG 30s ease infinite;
    }
    @keyframes gradientBG {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }
    .card {
        background: rgba(30,30,35,0.86);
        border-radius: 1.5em;
        padding: 2.2em 2.7em;
        margin-bottom: 2em;
        box-shadow: 0 8px 40px 0 rgba(33,150,243,0.14), 0 1.5px 3.5px rgba(0,0,0,0.12);
        color: #f8fafc;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'sans-serif';
        backdrop-filter: blur(3.5px);
    }
    .title {
        font-size: 2.7em; letter-spacing: 0.03em; font-weight: bold;
        background: linear-gradient(90deg,#43cea2,#185a9d,#c33764,#009efd,#2af598);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2em;
    }
    .section {
        font-size: 1.5em; font-weight: 700; letter-spacing: 0.02em; margin-bottom: 0.7em;
        color: #80ffe0;
    }
    .footer {font-size: 0.95em; color: #cccccc; opacity: 0.9; margin-top: 2em;}
    </style>
""", unsafe_allow_html=True)

# MongoDB
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["SuiviEPS"]

# DB Functions (simplified)
def load_data():
    collection = db.students
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        df = pd.DataFrame({
            "Nom": [], "Niveau": [], "Points de Compétence": [],
            "Rôles": [], "Pouvoirs": [], "StudentCode": [],
        })
    else:
        df = pd.DataFrame(data)
        df = df.rename(columns={"Points_de_Competence": "Points de Compétence"})
    return df

def save_data(df):
    df_to_save = df.rename(columns={"Points de Compétence": "Points_de_Competence"})
    collection = db.students
    collection.delete_many({})
    records = df_to_save.to_dict(orient="records")
    if records:
        collection.insert_many(records)

def load_hof():
    collection = db.hall_of_fame
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return [{"name": "", "achievement": ""} for _ in range(3)]
    return data

def save_hof(hof_data):
    collection = db.hall_of_fame
    collection.delete_many({})
    if hof_data:
        collection.insert_many(hof_data)

# Session state
if "students" not in st.session_state:
    st.session_state["students"] = load_data()
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# ACCES
if st.session_state["role"] is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🚀 Suivi EPS</div>', unsafe_allow_html=True)
    access_mode = st.radio("Connexion", options=["Enseignant", "Élève"], horizontal=True)
    if access_mode == "Enseignant":
        teacher_password = st.text_input("Code enseignant 🔑", type="password")
        if st.button("Connexion Pro"):
            if teacher_password == st.secrets["ACCESS_CODE"]:
                st.session_state["role"] = "teacher"
                st.session_state["user"] = "Enseignant"
                st.success("Bienvenue, Professeur !")
            else:
                st.error("Code incorrect.")
    else:
        if st.session_state["students"].empty:
            st.warning("Aucun élève enregistré.")
        else:
            student_name = st.selectbox("Ton nom", st.session_state["students"]["Nom"])
            student_row = st.session_state["students"].loc[st.session_state["students"]["Nom"] == student_name].iloc[0]
            if student_row["StudentCode"] == "":
                st.info("Crée ton code d'accès secret.")
                new_code = st.text_input("Nouveau code (min 4 caractères)", type="password")
                new_code_confirm = st.text_input("Confirme ton code", type="password")
                if st.button("Créer mon code & me connecter"):
                    if new_code != new_code_confirm:
                        st.error("Codes différents !")
                    elif len(new_code) < 4:
                        st.error("Code trop court.")
                    else:
                        idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == student_name][0]
                        st.session_state["students"].at[idx, "StudentCode"] = new_code
                        save_data(st.session_state["students"])
                        st.session_state["role"] = "student"
                        st.session_state["user"] = student_name
                        st.success(f"Bienvenue {student_name} !")
            else:
                code_entered = st.text_input("Ton code secret", type="password")
                if st.button("Connexion"):
                    if code_entered != student_row["StudentCode"]:
                        st.error("Code incorrect !")
                    else:
                        st.session_state["role"] = "student"
                        st.session_state["user"] = student_name
                        st.success(f"Bienvenue {student_name} !")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# REGLES
if not st.session_state["accepted_rules"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">📜 Règles du système</div>', unsafe_allow_html=True)
    st.markdown("""
- 🚫 **L'utilisation du site n'est pas obligatoire**.
- 🌟 Chaque séance : **4 niveaux max** (1 niveau = 5 points compétence).
- 🛒 **Achète des rôles et pouvoirs** avec tes points, tout simplement !
- 🧑‍🎓 **Aucun ajout manuel de points**, pas de triche ou d’édition sauvage.
- 🥇 **Le plaisir, le respect et la progression** avant tout.
    """)
    if st.button("✅ J'accepte les règles et l'aventure !"):
        st.session_state["accepted_rules"] = True
        st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# PAGES
pages = ["🏠 Accueil", "👤 Fiche Élève", "📊 Tableau de progression", "🏅 Leaderboard", "🏆 Hall of Fame", "🎬 Vidéo"]
if st.session_state["role"] == "teacher":
    pages.insert(1, "➕ Ajouter Élève")
    pages.insert(4, "🔼 Attribution de niveaux")
choice = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")

# PAGE ACCUEIL
if "Accueil" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">👾 Suivi EPS Futuriste</div>', unsafe_allow_html=True)
    st.markdown("**Bienvenue sur la plateforme EPS gamifiée !**<br><br>"
                "Utilise le menu à gauche pour explorer les <span style='color:#80ffe0'>classements</span>, ta <span style='color:#fff45f'>fiche</span>, ou dépenser tes points dans la boutique.", 
                unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:1em'>👤 <b>Mode d'accès :</b> <span style='color:#77f'>{st.session_state['role'].capitalize()} ({st.session_state['user']})</span></div>", unsafe_allow_html=True)
    if st.session_state["role"] == "teacher":
        st.download_button("⬇️ Exporter tous les élèves (CSV)", data=st.session_state["students"].to_csv(index=False), file_name="students_data.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div class='footer'>Made with 🤍 for teaching innovation</div>", unsafe_allow_html=True)

# PAGE AJOUT ELEVE
elif "Ajouter Élève" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">➕ Ajouter un élève</div>', unsafe_allow_html=True)
    with st.form("ajouter_eleve_form"):
        nom = st.text_input("Nom / Prénom")
        niveau = st.slider("Niveau de départ", 0, 20, 0)
        points_comp = niveau * 5
        st.write(f"Points de compétence attribués : `{points_comp}`")
        submit_eleve = st.form_submit_button("Ajouter 👤")
    if submit_eleve and nom:
        new_data = pd.DataFrame({
            "Nom": [nom],
            "Niveau": [niveau],
            "Points de Compétence": [points_comp],
            "Rôles": ["Apprenti(e)"],
            "Pouvoirs": [""],
            "StudentCode": [""],
        })
        st.session_state["students"] = pd.concat([st.session_state["students"], new_data], ignore_index=True)
        for col in ["Niveau", "Points de Compétence"]:
            st.session_state["students"][col] = pd.to_numeric(st.session_state["students"][col], errors="coerce").fillna(0).astype(int)
        save_data(st.session_state["students"])
        st.success(f"👤 Élève ajouté !")
        st.snow()
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE TABLEAU DE PROGRESSION
elif "Tableau de progression" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📊 Progression de tous les élèves</div>', unsafe_allow_html=True)
    if st.session_state["role"] == "teacher":
        df = st.data_editor(st.session_state["students"], use_container_width=True)
        if st.button("💾 Enregistrer toutes les modifications"):
            st.session_state["students"] = df
            save_data(df)
            st.success("Modifications sauvegardées ✔️")
    else:
        student = st.session_state["user"]
        df = st.session_state["students"][st.session_state["students"]["Nom"] == student]
        st.data_editor(df, use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE ATTRIBUTION DE NIVEAUX
elif "Attribution de niveaux" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🔼 Attribution de niveaux</div>', unsafe_allow_html=True)
    with st.form("assign_form"):
        selected = st.multiselect("Sélectionner des élèves", st.session_state["students"]["Nom"].tolist())
        levels = st.slider("Nombre de niveaux à ajouter", 1, 12, 1)
        submit = st.form_submit_button("Attribuer 🚀")
    if submit:
        for nom in selected:
            idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == nom][0]
            st.session_state["students"].at[idx, "Niveau"] += levels
            st.session_state["students"].at[idx, "Points de Compétence"] += levels * 5
        save_data(st.session_state["students"])
        st.success("Niveaux attribués !")
        st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE LEADERBOARD
elif "Leaderboard" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🏅 Top 10 - Leaderboard</div>', unsafe_allow_html=True)
    leaderboard = st.session_state["students"].sort_values("Points de Compétence", ascending=False)
    top10 = leaderboard.head(10)
    for rank, (_, row) in enumerate(top10.iterrows(), start=1):
        st.markdown(
            f"<div style='display:flex;align-items:center;font-size:1.25em;gap:1em'><span style='font-size:1.4em'>{'🥇' if rank==1 else '🥈' if rank==2 else '🥉' if rank==3 else '🏅'}</span>"
            f"<b>{rank}. {row['Nom']}</b> — Niveaux : <span style='color:#80ffe0'>{row['Niveau']}</span> — Points : <span style='color:#fcb900'>{row['Points de Compétence']}</span></div>"
            f"<div style='margin-bottom:0.8em;font-size:0.95em'>🎭 <b>Rôles :</b> {row['Rôles']}<br>💫 <b>Pouvoirs :</b> {row['Pouvoirs']}</div>",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE HALL OF FAME
elif "Hall of Fame" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🏆 Hall of Fame</div>', unsafe_allow_html=True)
    hof_data = load_hof()
    st.session_state["hall_of_fame"] = hof_data
    if st.session_state["role"] == "teacher":
        st.subheader("⚡ Mettre en avant les élèves")
        nb_entries = st.slider("Nombre d'élèves à mettre en lumière", 1, 5, len(hof_data))
        with st.form("hof_form"):
            new_entries = []
            for i in range(nb_entries):
                st.write(f"### ⭐ Élève {i+1}")
                options = st.session_state["students"]["Nom"].tolist()
                default_name = hof_data[i]["name"] if i < len(hof_data) else ""
                name = st.selectbox(f"Nom {i+1}", options, index=options.index(default_name) if default_name in options else 0, key=f"hof_{i}")
                default_achievement = hof_data[i]["achievement"] if i < len(hof_data) else ""
                achievement = st.text_area(f"Fait d'armes 🎯", value=default_achievement, key=f"hof_txt_{i}")
                new_entries.append({"name": name, "achievement": achievement})
            if st.form_submit_button("Mettre à jour"):
                st.session_state["hall_of_fame"] = new_entries
                save_hof(new_entries)
                st.success("Hall of Fame mis à jour !")
                st.snow()
    st.markdown('<div style="margin-top:2em"></div>', unsafe_allow_html=True)
    for entry in st.session_state["hall_of_fame"]:
        if entry["name"]:
            st.markdown(f"<div style='margin-bottom:1em'><span style='font-size:1.1em;font-weight:bold'>{entry['name']}</span><br>"
                        f"<span style='color:#ffd580;'>{entry['achievement']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("*Entrée vide*")
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE VIDEO
elif "Vidéo" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🎬 Vidéo du cours</div>', unsafe_allow_html=True)
    video_filename = "uploaded_video.mp4"
    if st.session_state["role"] == "teacher":
        st.subheader("Gestion vidéo")
        uploaded_file = st.file_uploader("Upload une vidéo MP4", type=["mp4"])
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_file is not None:
                with open(video_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Vidéo uploadée !")
        with col2:
            if os.path.exists(video_filename):
                if st.button("❌ Supprimer la vidéo"):
                    os.remove(video_filename)
                    st.success("Vidéo supprimée !")
    if os.path.exists(video_filename):
        st.video(video_filename)
    else:
        st.info("Aucune vidéo disponible pour l’instant.")
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE FICHE ELEVE
elif "Fiche Élève" in choice:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">👤 Ta fiche et ta boutique</div>', unsafe_allow_html=True)
    if st.session_state["role"] == "teacher":
        selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    else:
        selected_student = st.session_state["user"]
        st.info(f"Connecté comme <b>{selected_student}</b>", unsafe_allow_html=True)
    if selected_student:
        student_data = st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].iloc[0]
        st.subheader(f"📌 Fiche de {selected_student}")

        st.markdown(f"""
        <div style='padding:1em;background:rgba(22,24,31,0.75);border-radius:1em;margin-bottom:1em'>
            <b>Niveau :</b> {student_data['Niveau']}<br>
            <progress value="{student_data['Niveau']%21}" max="20" style="width:80%"></progress>
            <br>
            <b>Points de Compétence :</b> {student_data['Points de Compétence']}
            <progress value="{student_data['Points de Compétence']%501}" max="500" style="width:80%"></progress>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🥳 Fêter ma progression !"):
            st.balloons()
        onglets = st.tabs(["🛒 Pouvoirs", "🏅 Rôles"])
        with onglets[0]:
            st.markdown('<div class="section">Boutique des Pouvoirs</div>', unsafe_allow_html=True)
            store_items = {
                "Le malin / la maligne": 40,
                "Choix d’un jeu (5 min) ou donner 20 niveaux": 50,
                "Maître des groupes (1h30) ou doubler points de compétence": 100,
                "Maître du thème d’une séance": 150,
                "Roi / Reine de la séquence": 300
            }
            selected_item = st.selectbox("Choisir un pouvoir", list(store_items.keys()), key="pouvoirs")
            cost = store_items[selected_item]
            st.info(f"💰 Coût : <b>{cost}</b> niveaux", unsafe_allow_html=True)
            if st.button("Acheter ce pouvoir"):
                if int(student_data["Niveau"]) >= cost:
                    current_level = int(student_data["Niveau"])
                    new_level = current_level - cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"] = new_level
                    anciens_pouvoirs = str(student_data["Pouvoirs"]) if pd.notna(student_data["Pouvoirs"]) else ""
                    nouveaux_pouvoirs = anciens_pouvoirs + ", " + selected_item if anciens_pouvoirs else selected_item
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] = nouveaux_pouvoirs
                    save_data(st.session_state["students"])
                    st.success(f"🎁 Pouvoir '{selected_item}' acquis !")
                    st.snow()
                else:
                    st.error("Pas assez de niveaux !")
        with onglets[1]:
            st.markdown('<div class="section">Boutique des Rôles</div>', unsafe_allow_html=True)
            roles_store = {
                "Testeur.euse": 200, "Démonstrateur.rice": 150, "Facilitateur.rice": 150,
                "Créateur.rice de règles": 250, "Meneur.euse tactique": 250, "Arbitre / Régulateur.rice": 300,
                "Aide-coach": 250, "Coordinateur.rice de groupe": 300, "Facilitateur.rice (social)": 250,
                "Réducteur.rice des contraintes": 200, "Autonome": 200, "Responsable de séance": 350
            }
            selected_role = st.selectbox("Choisir un rôle", list(roles_store.keys()), key="roles")
            role_cost = roles_store[selected_role]
            st.info(f"💰 Coût : <b>{role_cost}</b> points de compétence", unsafe_allow_html=True)
            if st.button("Acquérir ce rôle"):
                if int(student_data["Points de Compétence"]) >= role_cost:
                    current_points = int(student_data["Points de Compétence"])
                    new_points = current_points - role_cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"] = new_points
                    anciens_roles = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
                    nouveaux_roles = anciens_roles + ", " + selected_role if anciens_roles else selected_role
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Rôles"] = nouveaux_roles
                    save_data(st.session_state["students"])
                    st.success(f"🏅 Rôle '{selected_role}' acquis !")
                    st.snow()
                else:
                    st.error("Pas assez de points !")
    st.markdown('</div>', unsafe_allow_html=True)
