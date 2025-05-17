import streamlit as st
import pandas as pd
from pymongo import MongoClient

# -----------------------------------------------------------------------------
# Connexion à MongoDB Atlas via st.secrets
# -----------------------------------------------------------------------------
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["SuiviEPS"]

# -----------------------------------------------------------------------------
# Fonctions de gestion du Hall of Fame
# -----------------------------------------------------------------------------
def load_hof():
    data = list(db.hall_of_fame.find({}, {"_id": 0}))
    if not data:
        return [{"name": "", "achievement": ""} for _ in range(3)]
    return data

def save_hof(hof_data):
    db.hall_of_fame.delete_many({})
    if hof_data:
        db.hall_of_fame.insert_many(hof_data)

# -----------------------------------------------------------------------------
# Fonctions de gestion des élèves
# -----------------------------------------------------------------------------
def load_data():
    data = list(db.students.find({}, {"_id": 0}))
    if not data:
        df = pd.DataFrame({
            "Nom": [],
            "Niveau": [],
            "Points de Compétence": [],
            "Pouvoirs": [],
            "Rôles": [],
            "StudentCode": [],
        })
    else:
        df = pd.DataFrame(data)
    return df

def save_data(df):
    df_to_save = df.rename(columns={
        "Points de Compétence": "Points_de_Competence"
    })
    db.students.delete_many({})
    records = df_to_save.to_dict(orient="records")
    if records:
        db.students.insert_many(records)
    st.success("Données élèves sauvegardées.")

# Initialisation
if "students" not in st.session_state:
    st.session_state["students"] = load_data()
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# Authentification (enseignant / élève) unifiée
# ... (identique à votre version actuelle, sans logique de compétences)

# Acceptation des règles simplifiées
# ... (gardez seulement règles générales et utilisation)

# Navigation pour rôle enseignant et élève
pages_teacher = ["Accueil", "Ajouter Élève", "Tableau de progression", "Attribution de niveaux", "Hall of Fame", "Leaderboard"]
pages_student = ["Accueil", "Tableau de progression", "Hall of Fame", "Leaderboard"]
choice = st.sidebar.radio("Navigation", pages_teacher if st.session_state["role"] == "teacher" else pages_student)

# Pages principales
if choice == "Accueil":
    st.title("Suivi EPS Simplifié")
    st.write(f"Mode : {st.session_state['role']} - Utilisateur : {st.session_state['user']}")
    if st.session_state["role"] == "teacher":
        if st.download_button("Télécharger CSV", data=st.session_state["students"].to_csv(index=False), file_name="students_data.csv"):
            st.success("Fichier téléchargé.")

elif choice == "Ajouter Élève":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.header("➕ Ajout Élève")
        with st.form("ajout_form"):
            nom = st.text_input("Nom")
            niveau = st.number_input("Niveau de départ", min_value=0, step=1)
            points = niveau * 5
            st.write(f"Points de Compétence initiaux : {points}")
            submit = st.form_submit_button("Ajouter")
        if submit and nom:
            new = pd.DataFrame([{"Nom": nom, "Niveau": niveau, "Points de Compétence": points, "Pouvoirs": "", "Rôles": "", "StudentCode": ""}])
            st.session_state["students"] = pd.concat([st.session_state["students"], new], ignore_index=True)
            save_data(st.session_state["students"])
            st.success(f"Élève {nom} ajouté.")

elif choice == "Tableau de progression":
    st.header("📊 Tableau de progression")
    if st.session_state["role"] == "teacher":
        df = st.data_editor(st.session_state["students"], use_container_width=True)
        if st.button("Enregistrer modifications"):
            st.session_state["students"] = df
            save_data(df)
    else:
        student = st.session_state["user"]
        df = st.session_state["students"][st.session_state["students"]["Nom"] == student]
        st.data_editor(df, use_container_width=True)

elif choice == "Attribution de niveaux":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.header("🏷️ Attribution de niveaux")
        with st.form("assign_form"):
            selected = st.multiselect("Sélectionnez élèves", st.session_state["students"]["Nom"].tolist())
            levels = st.number_input("Niveaux à ajouter", min_value=1, step=1)
            submit = st.form_submit_button("Ajouter")
        if submit:
            for nom in selected:
                idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == nom][0]
                st.session_state["students"].at[idx, "Niveau"] += levels
                st.session_state["students"].at[idx, "Points de Compétence"] += levels * 5
            save_data(st.session_state["students"])
            st.success("Attributions appliquées.")

elif choice == "Hall of Fame":
    st.header("🏆 Hall of Fame")
    hof = load_hof()
    if st.session_state["role"] == "teacher":
        with st.form("hof_form"):
            entries = []
            for i in range(len(hof)):
                name = st.selectbox(f"Élève {i+1}", options=st.session_state["students"]["Nom"], index=0, key=f"hof_name_{i}")
                ach = st.text_area(f"Exploit de {name}", value=hof[i]["achievement"], key=f"hof_ach_{i}")
                entries.append({"name": name, "achievement": ach})
            submit = st.form_submit_button("Enregistrer Hall of Fame")
        if submit:
            save_hof(entries)
            st.success("Hall of Fame mis à jour.")
    for entry in load_hof():
        if entry["name"]:
            st.write(f"**{entry['name']}** : {entry['achievement']}")

elif choice == "Leaderboard":
    st.header("🏅 Leaderboard")
    lb = st.session_state["students"].sort_values("Points de Compétence", ascending=False)
    for i, row in lb.head(10).iterrows():
        st.write(f"{i+1}. {row['Nom']} - Niv: {row['Niveau']} - Points: {row['Points de Compétence']}")
