import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os

st.set_page_config(page_title="Suivi EPS", layout="wide", page_icon=":trophy:")

# STYLES SIMPLES, ACCESSIBLES
st.markdown("""
    <style>
    body, html, [class*="st-"]  {
        background: linear-gradient(115deg, #f2f8ff 0%, #ddeeff 100%) !important;
        color: #20232a !important;
        font-family: system-ui, "Roboto", Arial, sans-serif;
    }
    .card {
        background: rgba(255,255,255,0.96);
        border-radius: 1.4em;
        box-shadow: 0 2px 20px 0 rgba(100,140,200,0.07);
        padding: 2em 1.2em 2em 1.2em;
        margin: 1em 0 2em 0;
    }
    .stButton>button, .stDownloadButton>button {
        background: #2776e8 !important;
        color: #fff !important;
        border-radius: 0.7em !important;
        font-size: 1.1em;
        padding: 0.6em 1.5em;
        font-weight: 500;
        border: none !important;
        margin-bottom: 0.8em;
        margin-top: 0.5em;
        transition: background 0.2s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: #1557a5 !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.05em;
        color: #2776e8;
    }
    .stTabs [aria-selected="true"] {
        background: #eaf1fc !important;
        color: #1a345d !important;
    }
    .title {
        font-size: 2.25em;
        font-weight: 700;
        color: #175bc7;
        margin-bottom: 0.2em;
    }
    @media (max-width: 800px) {
        .card { padding: 1.1em 0.6em 1.1em 0.6em; }
        .title { font-size: 1.4em; }
    }
    </style>
""", unsafe_allow_html=True)

# Connexion à MongoDB
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["SuiviEPS"]

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

def load_data():
    collection = db.students
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        df = pd.DataFrame({
            "Nom": [],
            "Niveau": [],
            "Points de Compétence": [],
            "Rôles": [],
            "Pouvoirs": [],
            "StudentCode": [],
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

if "students" not in st.session_state:
    st.session_state["students"] = load_data()
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# PAGE D'ACCÈS
if st.session_state["role"] is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Bienvenue sur Suivi EPS</div>', unsafe_allow_html=True)
    access_mode = st.radio("Qui êtes-vous ?", options=["Enseignant", "Élève"], horizontal=True)
    if access_mode == "Enseignant":
        teacher_password = st.text_input("Code enseignant", type="password")
        if st.button("Connexion"):
            if teacher_password == st.secrets["ACCESS_CODE"]:
                st.session_state["role"] = "teacher"
                st.session_state["user"] = "Enseignant"
                st.success("Bienvenue !")
            else:
                st.error("Code incorrect.")
    else:
        if st.session_state["students"].empty:
            st.warning("Aucun élève n'est encore enregistré.")
        else:
            student_name = st.selectbox("Choisis ton nom", st.session_state["students"]["Nom"])
            student_row = st.session_state["students"].loc[st.session_state["students"]["Nom"] == student_name].iloc[0]
            if student_row["StudentCode"] == "":
                st.info("Première connexion : crée ton code secret.")
                new_code = st.text_input("Nouveau code (min 4 caractères)", type="password")
                new_code_confirm = st.text_input("Confirme ton code", type="password")
                if st.button("Créer le code et me connecter"):
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

# RÈGLES
if not st.session_state["accepted_rules"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">📜 Règles du système</div>', unsafe_allow_html=True)
    st.markdown("""
- **Utilisation du site non obligatoire**
- Maximum **4 niveaux** par séance (1 niveau = 5 points).
- Début = rôle **Apprenti(e)**.
- Tu peux acheter des rôles ou pouvoirs avec tes niveaux ou points.
- **Aucun ajout manuel** non validé par l’enseignant.
    """)
    if st.button("J'ai lu et j'accepte les règles"):
        st.session_state["accepted_rules"] = True
        st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# NAVIGATION
if st.session_state["role"] == "teacher":
    pages = ["Accueil", "Ajouter Élève", "Tableau de progression", "Attribution de niveaux", "Hall of Fame", "Leaderboard", "Vidéo", "Fiche Élève"]
else:
    pages = ["Accueil", "Tableau de progression", "Hall of Fame", "Leaderboard", "Vidéo", "Fiche Élève"]
choice = st.sidebar.radio("Navigation", pages)

# ACCUEIL
if choice == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Bienvenue !</div>', unsafe_allow_html=True)
    st.write("Utilise le menu à gauche pour accéder à toutes les sections.")
    st.markdown(f"**Mode d'accès :** {st.session_state['role'].capitalize()} ({st.session_state['user']})")
    if st.session_state["role"] == "teacher":
        st.download_button("Télécharger le CSV des élèves", data=st.session_state["students"].to_csv(index=False), file_name="students_data.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# AJOUTER ÉLÈVE
elif choice == "Ajouter Élève":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ajouter un élève")
        with st.form("ajouter_eleve_form"):
            nom = st.text_input("Nom")
            niveau = st.number_input("Niveau de départ", min_value=0, max_value=10000, step=1)
            points_comp = niveau * 5
            st.write(f"Points de Compétence : {points_comp}")
            submit_eleve = st.form_submit_button("Ajouter")
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
            st.success(f"{nom} ajouté avec {niveau} niveaux.")
        st.markdown('</div>', unsafe_allow_html=True)

# TABLEAU DE PROGRESSION
elif choice == "Tableau de progression":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Tableau de progression")
    if st.session_state["role"] == "teacher":
        df = st.data_editor(st.session_state["students"], use_container_width=True)
        if st.button("Enregistrer"):
            st.session_state["students"] = df
            save_data(df)
    else:
        student = st.session_state["user"]
        df = st.session_state["students"][st.session_state["students"]["Nom"] == student]
        st.data_editor(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ATTRIBUTION DE NIVEAUX
elif choice == "Attribution de niveaux":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Attribuer des niveaux")
        with st.form("assign_form"):
            selected = st.multiselect("Sélectionner les élèves", st.session_state["students"]["Nom"].tolist())
            levels = st.number_input("Niveaux à ajouter", min_value=1, step=1)
            submit = st.form_submit_button("Attribuer")
        if submit:
            for nom in selected:
                idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == nom][0]
                st.session_state["students"].at[idx, "Niveau"] += levels
                st.session_state["students"].at[idx, "Points de Compétence"] += levels * 5
            save_data(st.session_state["students"])
            st.success("Attributions effectuées.")
        st.markdown('</div>', unsafe_allow_html=True)

# HALL OF FAME
elif choice == "Hall of Fame":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Hall of Fame")
    hof_data = load_hof()
    st.session_state["hall_of_fame"] = hof_data
    if st.session_state["role"] == "teacher":
        st.subheader("Mettre en lumière")
        nb_entries = st.number_input("Nombre d'élèves", min_value=1, max_value=5, value=len(st.session_state["hall_of_fame"]) if st.session_state["hall_of_fame"] else 3, step=1)
        with st.form("hof_form"):
            new_entries = []
            for i in range(nb_entries):
                st.write(f"Élève {i+1}")
                options = st.session_state["students"]["Nom"].tolist()
                default_name = st.session_state["hall_of_fame"][i]["name"] if i < len(st.session_state["hall_of_fame"]) else ""
                name = st.selectbox(f"Nom de l'élève {i+1}", options=options, index=options.index(default_name) if default_name in options else 0, key=f"hof_name_{i}")
                default_achievement = st.session_state["hall_of_fame"][i]["achievement"] if i < len(st.session_state["hall_of_fame"]) else ""
                achievement = st.text_area(f"Exploits de {name}", value=default_achievement, key=f"hof_achievement_{i}")
                new_entries.append({"name": name, "achievement": achievement})
            if st.form_submit_button("Enregistrer"):
                st.session_state["hall_of_fame"] = new_entries
                save_hof(new_entries)
                st.success("Hall of Fame mis à jour.")
    st.subheader("Les exploits")
    for entry in st.session_state["hall_of_fame"]:
        if entry["name"]:
            st.markdown(f"**{entry['name']}** : {entry['achievement']}")
        else:
            st.markdown("*Entrée vide*")
    st.markdown('</div>', unsafe_allow_html=True)

# LEADERBOARD
elif choice == "Leaderboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Leaderboard")
    leaderboard = st.session_state["students"].sort_values("Points de Compétence", ascending=False)
    st.subheader("Top 10")
    top10 = leaderboard.head(10)
    for rank, (_, row) in enumerate(top10.iterrows(), start=1):
        st.markdown(
            f"**{rank}. {row['Nom']}** – Niveau : {row['Niveau']} – Points : {row['Points de Compétence']}<br>"
            f"Rôle : {row['Rôles']} | Pouvoirs : {row['Pouvoirs']}",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# VIDÉO
elif choice == "Vidéo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Vidéo du dernier cours")
    video_filename = "uploaded_video.mp4"
    if st.session_state["role"] == "teacher":
        st.subheader("Gérer la vidéo")
        uploaded_file = st.file_uploader("Uploader une vidéo (MP4)", type=["mp4"])
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_file is not None:
                with open(video_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Vidéo téléchargée !")
        with col2:
            if os.path.exists(video_filename):
                if st.button("Retirer la vidéo"):
                    os.remove(video_filename)
                    st.success("Vidéo retirée.")
    if os.path.exists(video_filename):
        st.video(video_filename)
    else:
        st.info("Aucune vidéo ajoutée pour l'instant.")
    st.markdown('</div>', unsafe_allow_html=True)

# FICHE ELEVE & BOUTIQUE
elif choice == "Fiche Élève":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Ma fiche & Boutique")
    if st.session_state["role"] == "teacher":
        selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    else:
        selected_student = st.session_state["user"]
        st.info(f"Connecté(e) comme {selected_student}")
    if selected_student:
        student_data = st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].iloc[0]
        st.markdown(f"""<div style='background:#f7fafd;border-radius:1em;padding:1em 1.2em;margin-bottom:1.2em'>
            <b>Niveau :</b> {student_data['Niveau']}<br>
            <b>Points de Compétence :</b> {student_data['Points de Compétence']}
        </div>""", unsafe_allow_html=True)
        if st.button("Fêter ma progression"):
            st.balloons()
        onglets = st.tabs(["Boutique des Pouvoirs", "Boutique des Rôles"])
        with onglets[0]:
            store_items = {
                "Le malin / la maligne": 40,
                "Choix d’un jeu (5 min) ou donner 20 niveaux": 50,
                "Maître des groupes (1h30) ou doubler points de compétence": 100,
                "Maître du thème d’une séance": 150,
                "Roi / Reine de la séquence": 300
            }
            selected_item = st.selectbox("Choisir un pouvoir", list(store_items.keys()), key="pouvoirs")
            cost = store_items[selected_item]
            st.info(f"Coût : {cost} niveaux")
            if st.button("Acheter ce pouvoir", key="acheter_pouvoir"):
                if int(student_data["Niveau"]) >= cost:
                    current_level = int(student_data["Niveau"])
                    new_level = current_level - cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"] = new_level
                    anciens_pouvoirs = str(student_data["Pouvoirs"]) if pd.notna(student_data["Pouvoirs"]) else ""
                    nouveaux_pouvoirs = anciens_pouvoirs + ", " + selected_item if anciens_pouvoirs else selected_item
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] = nouveaux_pouvoirs
                    save_data(st.session_state["students"])
                    st.success(f"Pouvoir '{selected_item}' acquis !")
                else:
                    st.error("Pas assez de niveaux.")
        with onglets[1]:
            roles_store = {
                "Testeur.euse": 200,
                "Démonstrateur.rice": 150,
                "Facilitateur.rice": 150,
                "Créateur.rice de règles": 250,
                "Meneur.euse tactique": 250,
                "Arbitre / Régulateur.rice": 300,
                "Aide-coach": 250,
                "Coordinateur.rice de groupe": 300,
                "Facilitateur.rice (social)": 250,
                "Réducteur.rice des contraintes": 200,
                "Autonome": 200,
                "Responsable de séance": 350
            }
            selected_role = st.selectbox("Choisir un rôle", list(roles_store.keys()), key="roles")
            role_cost = roles_store[selected_role]
            st.info(f"Coût : {role_cost} points de compétence")
            if st.button("Acquérir ce rôle", key="acheter_role"):
                if int(student_data["Points de Compétence"]) >= role_cost:
                    current_points = int(student_data["Points de Compétence"])
                    new_points = current_points - role_cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"] = new_points
                    anciens_roles = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
                    nouveaux_roles = anciens_roles + ", " + selected_role if anciens_roles else selected_role
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Rôles"] = nouveaux_roles
                    save_data(st.session_state["students"])
                    st.success(f"Rôle '{selected_role}' acquis !")
                else:
                    st.error("Pas assez de points.")
    st.markdown('</div>', unsafe_allow_html=True)
