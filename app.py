import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os

# Connexion à MongoDB Atlas via st.secrets
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["SuiviEPS"]

# Fonctions Hall of Fame
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

# Fonctions gestion des élèves (stocké MongoDB)
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
    st.write("[INFO] Données sauvegardées.")

# Chargement initial des données
if "students" not in st.session_state:
    st.session_state["students"] = load_data()
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# Page d'accès
if st.session_state["role"] is None:
    st.title("Page d'accès")
    access_mode = st.radio("Choisissez votre rôle", options=["Enseignant", "Élève"])
    if access_mode == "Enseignant":
        teacher_password = st.text_input("Entrez le code d'accès enseignant :", type="password")
        if st.button("Se connecter comme enseignant", key="teacher_conn"):
            if teacher_password == st.secrets["ACCESS_CODE"]:
                st.session_state["role"] = "teacher"
                st.session_state["user"] = "Enseignant"
                st.success("Accès enseignant autorisé.")
            else:
                st.error("Code incorrect.")
    else:
        if st.session_state["students"].empty:
            st.warning("Aucun élève n'est enregistré. Veuillez contacter votre enseignant.")
        else:
            student_name = st.selectbox("Choisissez votre nom", st.session_state["students"]["Nom"])
            student_row = st.session_state["students"].loc[st.session_state["students"]["Nom"] == student_name].iloc[0]
            if student_row["StudentCode"] == "":
                st.info("Première connexion : veuillez créer un code d'accès.")
                new_code = st.text_input("Créez un code d'accès (min. 4 caractères)", type="password", key="new_student_code")
                new_code_confirm = st.text_input("Confirmez votre code", type="password", key="new_student_code_confirm")
                if st.button("Enregistrer et se connecter", key="student_first_conn"):
                    if new_code != new_code_confirm:
                        st.error("Les codes ne correspondent pas.")
                    elif len(new_code) < 4:
                        st.error("Le code doit contenir au moins 4 caractères.")
                    else:
                        idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == student_name][0]
                        st.session_state["students"].at[idx, "StudentCode"] = new_code
                        save_data(st.session_state["students"])
                        st.session_state["role"] = "student"
                        st.session_state["user"] = student_name
                        st.success(f"Accès élève autorisé pour {student_name}.")
            else:
                code_entered = st.text_input("Entrez votre code d'accès", type="password", key="existing_student_code")
                if st.button("Se connecter comme élève", key="student_conn"):
                    if code_entered != student_row["StudentCode"]:
                        st.error("Code incorrect.")
                    else:
                        st.session_state["role"] = "student"
                        st.session_state["user"] = student_name
                        st.success(f"Accès élève autorisé pour {student_name}.")
    st.stop()

# Bloc d'acceptation des règles
if not st.session_state["accepted_rules"]:
    st.title("📜 Règles du système")
    st.markdown("""
### 🔹 Eléments généraux
- **L'utilisation du site n'est en aucun cas obligatoire, l'expérience durant les cours d'éducation physique sportive et artistique restera la même si l'élève décide de ne pas l'utiliser.**
- L’élève peut gagner **4 niveaux** par séance de 45 minutes.
- 1 niveau pour le fair-play, le respect, l’investissement et l’atteinte des objectifs.
- Tous les élèves commencent avec le rôle **d’Apprenti(e)**.
- 1 niveau = **5 points de compétences**.
- Chaque élève peut se spécialiser dans **3 compétences** uniquement.
- L'élève peut acheter des pouvoirs ou des rôles avec ses niveaux et compétences.
- **L'élève n'a pas le droit de se rajouter des niveaux ou points de compétence sous peine d'exclusion immédiate**.
- L'utilisation du site peut prendre fin à tout moment si l'enseignant le juge nécessaire, mais au plus tard durant la fin de l'année scolaire.

### 🔹 Accès et utilisation
- **Le site est un outil pédagogique** et ne doit pas être utilisé pour nuire aux autres ou perturber le déroulement des séances.
- **L’accès à son compte est personnel** et ne doit pas être partagé avec d’autres élèves.

### 🔹 Attribution et gestion des niveaux
- Un élève peut **proposer une auto-évaluation** de ses niveaux, mais la validation finale revient à l’enseignant.
- **Le gain de niveaux dépend de critères précis** (fair-play, investissement,…). **Aucun niveau n'est automatique.**

### 🔹 Sécurité et fair-play
- **Le harcèlement** via le classement ou les points de compétence est **strictement interdit**.
- **L'enseignant peut modifier, retirer ou ajuster des niveaux en cas de comportement inapproprié**.
- **Aucun élève ne peut voir les statistiques individuelles des autres** mise à part le top ten.

### 🔹 Boutique des pouvoirs et rôles
- **Les pouvoirs et rôles ne doivent pas être utilisés pour désavantager les autres élèves**.

### 🔹 Questions 
- L'élève contacte directement l'enseignant pour toutes questions en lien avec le site ou les cours de sport.

### Boutique des rôles et pouvoirs

| Rôle                          | Points de compétence nécessaires | Explication                                                    |
|-------------------------------|--------------------|----------------------------------------------------------------|
| Testeur.euse                  | 200                | Peut essayer en premier les nouveaux exercices.                |
| Démonstrateur.rice            | 150                | Présente les mouvements au reste du groupe.                    |
| Facilitateur.rice             | 150                | Moins de répétitions imposées s’il maîtrise déjà l’exercice.   |
| Créateur.rice de règles       | 250                | Peut modifier certaines règles des exercices.                  |
| Meneur.euse tactique          | 250                | Oriente une équipe et propose des stratégies.                  |
| Arbitre / Régulateur.rice     | 300                | Aide à gérer les litiges et décisions collectives.             |
| Aide-coach                    | 250                | Peut accompagner un élève en difficulté.                       |
| Coordinateur.rice de groupe   | 300                | Premier choix des groupes.                                     |
| Facilitateur.rice (social)    | 250                | Favorise l’intégration de tous.                                |
| Réducteur.rice des contraintes| 200                | Accès à des versions simplifiées des consignes.                |
| Autonome                      | 200                | Peut choisir son propre parcours ou défi.                      |
| Responsable de séance         | 350                | Peut diriger une partie de la séance.                          |


### Boutique secrète
| Coût en niveau | Pouvoirs à choix                                                                                   |
|---------------|----------------------------------------------------------------------------------------------------|
| 40            | Le malin / la maligne : doubler ses niveaux gagnés à chaque cours.                                 |
| 50            | Choix d’un jeu (5 min) ou donner 20 niveaux à quelqu’un.                                            |
| 100           | Maître.sse des groupes pour une séance de 1h30 ou doubler ses points de compétences.                 |
| 150           | Maître.sse du thème d’une prochaine séance.                                                        |
| 300           | Roi / Reine de la séquence : permet de choisir le prochain thème pour 4 à 6 cours.                   |
    """)
    if st.button("Je confirme avoir lu les règles et m'engager à les respecter", key="accept_rules"):
        st.session_state["accepted_rules"] = True
    st.stop()



# Pages disponibles
if st.session_state["role"] == "teacher":
    pages = ["Accueil", "Ajouter Élève", "Tableau de progression", "Attribution de niveaux", "Hall of Fame", "Leaderboard", "Vidéo", "Fiche Élève"]
else:
    pages = ["Accueil", "Tableau de progression", "Hall of Fame", "Leaderboard", "Vidéo", "Fiche Élève"]

choice = st.sidebar.radio("Navigation", pages)

# PAGE ACCUEIL
if choice == "Accueil":
    st.header("Bienvenue sur Suivi EPS 🏆")
    st.write("Utilisez le menu à gauche pour naviguer entre les sections.")
    st.markdown(f"**Mode d'accès :** {st.session_state['role'].capitalize()} ({st.session_state['user']})")
    if st.session_state["role"] == "teacher":
        st.download_button("Télécharger le fichier CSV", data=st.session_state["students"].to_csv(index=False), file_name="students_data.csv", mime="text/csv")

# AJOUTER ELEVE
elif choice == "Ajouter Élève":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.header("➕ Ajout des participant.e.s")
        with st.form("ajouter_eleve_form"):
            nom = st.text_input("Nom")
            niveau = st.number_input("Niveau de départ", min_value=0, max_value=10000, step=1)
            points_comp = niveau * 5
            st.write(f"**Points de Compétence disponibles :** {points_comp}")
            submit_eleve = st.form_submit_button("Ajouter l'élève")
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
            st.success(f"✅ {nom} ajouté avec niveau {niveau}.")

# TABLEAU DE PROGRESSION
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

# ATTRIBUTION DE NIVEAUX
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

# HALL OF FAME
elif choice == "Hall of Fame":
    st.header("🏆 Hall of Fame")
    hof_data = load_hof()
    st.session_state["hall_of_fame"] = hof_data
    if st.session_state["role"] == "teacher":
        st.subheader("Modifier le Hall of Fame")
        nb_entries = st.number_input("Nombre d'élèves à mettre en lumière", min_value=1, max_value=5, 
                                     value=len(st.session_state["hall_of_fame"]) if st.session_state["hall_of_fame"] else 3, 
                                     step=1)
        with st.form("hall_of_fame_form"):
            new_entries = []
            for i in range(nb_entries):
                st.write(f"### Élève {i+1}")
                options = st.session_state["students"]["Nom"].tolist()
                default_name = st.session_state["hall_of_fame"][i]["name"] if i < len(st.session_state["hall_of_fame"]) else ""
                name = st.selectbox(f"Nom de l'élève {i+1}", options=options, index=options.index(default_name) if default_name in options else 0, key=f"hof_name_{i}")
                default_achievement = st.session_state["hall_of_fame"][i]["achievement"] if i < len(st.session_state["hall_of_fame"]) else ""
                achievement = st.text_area(f"Exploits de {name}", value=default_achievement, key=f"hof_achievement_{i}")
                new_entries.append({"name": name, "achievement": achievement})
            if st.form_submit_button("Enregistrer le Hall of Fame"):
                st.session_state["hall_of_fame"] = new_entries
                save_hof(new_entries)
                st.success("Hall of Fame mis à jour.")
    st.subheader("Les Exploits")
    for entry in st.session_state["hall_of_fame"]:
        if entry["name"]:
            st.markdown(f"**{entry['name']}** : {entry['achievement']}")
        else:
            st.markdown("*Entrée vide*")

# LEADERBOARD
elif choice == "Leaderboard":
    st.header("🏆 Leaderboard")
    leaderboard = st.session_state["students"].sort_values("Points de Compétence", ascending=False)
    st.subheader("Le top ten")
    top10 = leaderboard.head(10)
    for rank, (_, row) in enumerate(top10.iterrows(), start=1):
        st.markdown(
            f"**{rank}. {row['Nom']}** - Niveau: {row['Niveau']} - Points: {row['Points de Compétence']}<br>"
            f"**Rôle:** {row['Rôles']} | **Pouvoirs:** {row['Pouvoirs']} :trophy:",
            unsafe_allow_html=True
        )

# VIDEO
elif choice == "Vidéo":
    st.header("📹 Vidéo")
    video_filename = "uploaded_video.mp4"
    if st.session_state["role"] == "teacher":
        st.subheader("Gérer la vidéo")
        uploaded_file = st.file_uploader("Uploader une vidéo (MP4)", type=["mp4"])
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_file is not None:
                with open(video_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Vidéo téléchargée avec succès!")
        with col2:
            if os.path.exists(video_filename):
                if st.button("Retirer la vidéo"):
                    os.remove(video_filename)
                    st.success("Vidéo retirée avec succès!")
    if os.path.exists(video_filename):
        st.video(video_filename)
    else:
        st.info("Aucune vidéo n'a encore été téléchargée.")

# FICHE ELEVE
elif choice == "Fiche Élève":
    st.header("🔍 Fiche de l'élève")
    if st.session_state["role"] == "teacher":
        selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    else:
        selected_student = st.session_state["user"]
        st.info(f"Vous êtes connecté(e) en tant que {selected_student}.")
    if selected_student:
        student_data = st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].iloc[0]
        st.subheader(f"📌 Fiche de {selected_student}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Niveau :** {student_data['Niveau']}")
            st.write(f"**Points de Compétence :** {student_data['Points de Compétence']}")
            if st.button("Fêter ma progression"):
                st.balloons()
        onglets = st.tabs(["🛒 Boutique des Pouvoirs", "🏅 Boutique des Rôles"])
        with onglets[0]:
            store_items = {
                "Le malin / la maligne": 40,
                "Choix d’un jeu (5 min) ou donner 20 niveaux": 50,
                "Maître des groupes (1h30) ou doubler points de compétence": 100,
                "Maître du thème d’une séance": 150,
                "Roi / Reine de la séquence": 300
            }
            selected_item = st.selectbox("🛍️ Choisir un pouvoir", list(store_items.keys()), key="pouvoirs")
            cost = store_items[selected_item]
            st.info(f"💰 Coût: {cost} niveaux")
            if st.button("Acheter ce pouvoir", key="acheter_pouvoir"):
                if int(student_data["Niveau"]) >= cost:
                    current_level = int(student_data["Niveau"])
                    new_level = current_level - cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"] = new_level
                    anciens_pouvoirs = str(student_data["Pouvoirs"]) if pd.notna(student_data["Pouvoirs"]) else ""
                    nouveaux_pouvoirs = anciens_pouvoirs + ", " + selected_item if anciens_pouvoirs else selected_item
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] = nouveaux_pouvoirs
                    save_data(st.session_state["students"])
                    st.success(f"🛍️ {selected_student} a acheté '{selected_item}'.")
                else:
                    st.error("❌ Niveaux insuffisants !")
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
            selected_role = st.selectbox("🎭 Choisir un rôle", list(roles_store.keys()), key="roles")
            role_cost = roles_store[selected_role]
            st.info(f"💰 Coût: {role_cost} points de compétence")
            if st.button("Acquérir ce rôle", key="acheter_role"):
                if int(student_data["Points de Compétence"]) >= role_cost:
                    current_points = int(student_data["Points de Compétence"])
                    new_points = current_points - role_cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"] = new_points
                    anciens_roles = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
                    nouveaux_roles = anciens_roles + ", " + selected_role if anciens_roles else selected_role
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Rôles"] = nouveaux_roles
                    save_data(st.session_state["students"])
                    st.success(f"🏅 {selected_student} a acquis le rôle '{selected_role}'.")
                else:
                    st.error("❌ Points de compétence insuffisants !")
