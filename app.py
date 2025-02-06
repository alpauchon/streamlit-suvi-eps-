import streamlit as st
import pandas as pd
import json
import os

# -----------------------------------------------------------------------------
# Configuration de la page et injection de CSS pour un design moderne
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Suivi EPS", page_icon="🏆", layout="wide")
st.markdown("""
<style>
/* Fond global */
body {
    background-color: #f0f2f6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Style pour les cartes (sections) */
.card {
    background: #ffffff;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}
.card:hover {
    transform: scale(1.01);
}

/* Personnalisation des boutons */
.stButton>button {
    background-color: #2c3e50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 5px;
    font-size: 16px;
    margin: 5px;
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #34495e;
}

/* Couleur des titres */
h1, h2, h3 {
    color: #2c3e50;
}

/* Footer fixe */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #2c3e50;
    color: white;
    text-align: center;
    padding: 5px;
    font-size: 12px;
    font-weight: bold;
}
</style>

<div class="footer">
    © 2025 - Créé par Al Pauchon
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Suppression de la fonction de redémarrage automatique (non compatible)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Fonctions de gestion du Hall of Fame (sauvegarde en JSON)
# -----------------------------------------------------------------------------
HOF_FILE = "hall_of_fame.json"

def load_hof():
    if os.path.exists(HOF_FILE):
        with open(HOF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Initialisation par défaut avec 3 entrées vides
        return [{"name": "", "achievement": ""} for _ in range(3)]

def save_hof(hof_data):
    with open(HOF_FILE, "w", encoding="utf-8") as f:
        json.dump(hof_data, f, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------
# Fonctions de gestion de la vidéo du dernier cours (sauvegarde en JSON)
# -----------------------------------------------------------------------------
VIDEO_FILE = "video_link.json"

def load_video_link():
    if os.path.exists(VIDEO_FILE):
        with open(VIDEO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("video_url", "")
    else:
        return ""

def save_video_link(video_url):
    with open(VIDEO_FILE, "w", encoding="utf-8") as f:
        json.dump({"video_url": video_url}, f, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------
# Chargement des données des élèves
# -----------------------------------------------------------------------------
def load_data():
    try:
        df = pd.read_csv("students_data.csv")
        if df.empty:
            raise FileNotFoundError
        if "StudentCode" not in df.columns:
            df["StudentCode"] = ""
        else:
            df["StudentCode"] = df["StudentCode"].fillna("")
        df["Pouvoirs"] = df["Pouvoirs"].astype(str)
        for col in ["Niveau", "Points de Compétence", "FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        print("[INFO] Données chargées avec succès.")
        return df
    except FileNotFoundError:
        print("[WARNING] Fichier non trouvé, création d'un nouveau DataFrame.")
        return pd.DataFrame({
            "Nom": [], "Niveau": [], "Points de Compétence": [],
            "FAVEDS 🤸": [], "Stratégie 🧠": [], "Coopération 🤝": [], "Engagement 🌟": [],
            "Rôles": [], "Pouvoirs": [], "StudentCode": [],
        })

def save_data(df):
    df.to_csv("students_data.csv", index=False)
    print("[INFO] Données sauvegardées.")

if "students" not in st.session_state:
    st.session_state["students"] = load_data()

# -----------------------------------------------------------------------------
# Initialisation des variables de session pour l'accès
# -----------------------------------------------------------------------------
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# -----------------------------------------------------------------------------
# Bloc d'accès spécialisé
# -----------------------------------------------------------------------------
if st.session_state["role"] is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
                st.info("Première connexion : veuillez créer un code d'accès.")
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
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# Bloc d'acceptation des règles
# -----------------------------------------------------------------------------
if not st.session_state["accepted_rules"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
| Rôles                         | Points de compétence nécessaires | Compétences requises           | Explication                                               |
|-------------------------------|--------------------|--------------------------------|-----------------------------------------------------------|
| Testeur.euse                  | 200                | FAVEDS                         | Peut essayer en premier les nouveaux exercices.         |
| Démonstrateur.rice            | 150                | FAVEDS + Engagement            | Présente les mouvements au reste du groupe.             |
| Facilitateur.rice             | 150                | Coopération + Engagement       | Moins de répétitions imposées s’il maîtrise déjà l’exercice.|
| Créateur.rice de règles       | 250                | Stratégie                      | Peut modifier certaines règles des exercices.           |
| Meneur.euse tactique          | 250                | Stratégie + Coopération        | Oriente une équipe et propose des stratégies.           |
| Arbitre / Régulateur.rice     | 300                | Stratégie + Engagement         | Aide à gérer les litiges et décisions collectives.        |
| Aide-coach                    | 250                | Coopération + Engagement       | Peut accompagner un élève en difficulté.                |
| Coordinateur.rice de groupe   | 300                | Coopération                    | Premier choix des groupes.                                |
| Facilitateur.rice (social)     | 250                | Coopération + Engagement       | Favorise l’intégration de tous.                           |
| Réducteur.rice des contraintes| 200                | FAVEDS + Engagement            | Accès à des versions simplifiées des consignes.           |
| Autonome                      | 200                | Stratégie + Engagement         | Peut choisir son propre parcours ou défi.               |
| Responsable de séance         | 350                | Stratégie + Coopération + Engagement | Peut diriger une partie de la séance.              |

### Boutique secrète
| Coût en niveau | Pouvoirs à choix                                                                                   |
|---------------|----------------------------------------------------------------------------------------------------|
| 40            | Le malin / la maligne : doubler ses niveaux gagnés à chaque cours.                                 |
| 50            | Choix d’un jeu (5 min) ou donner 20 niveaux à quelqu’un.                                            |
| 100           | Maître.sse des groupes pour une séance de 1h30 ou doubler ses points de compétences.                 |
| 150           | Maître.sse du thème d’une prochaine séance.                                                        |
| 300           | Roi / Reine de la séquence : permet de choisir le prochain thème pour 4 à 6 cours.                   |
    """)
    if st.button("OK, j'ai compris les règles", key="accept_rules"):
        st.session_state["accepted_rules"] = True
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# -----------------------------------------------------------------------------
# Leaderboard : classement automatique des élèves par Points de Compétence
# -----------------------------------------------------------------------------
def get_leaderboard(df):
    leaderboard = df.sort_values("Points de Compétence", ascending=False)
    return leaderboard[["Nom", "Niveau", "Points de Compétence"]]

# -----------------------------------------------------------------------------
# Définition des pages disponibles selon le rôle
# -----------------------------------------------------------------------------
if st.session_state["role"] == "teacher":
    pages = ["Accueil", "Ajouter Élève", "Tableau de progression", "Attribution de niveaux", "Hall of Fame", "Leaderboard", "Vidéo du dernier cours", "Fiche Élève"]
else:
    pages = ["Accueil", "Tableau de progression", "Hall of Fame", "Leaderboard", "Vidéo du dernier cours", "Fiche Élève"]

choice = st.sidebar.radio("Navigation", pages)

# -----------------------------------------------------------------------------
# Images SVG pour chaque section
# -----------------------------------------------------------------------------
images = {
    "Accueil": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#2c3e50" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Bienvenue sur Suivi EPS
      </text>
    </svg>
    """,
    "Ajouter Élève": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#27ae60" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Ajout des participant.e.s
      </text>
    </svg>
    """,
    "Tableau de progression": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#8e44ad" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Tableau de progression
      </text>
    </svg>
    """,
    "Fiche Élève": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#e67e22" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Fiche de l'élève
      </text>
    </svg>
    """,
    "Attribution de niveaux": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#c0392b" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Attribution de niveaux
      </text>
    </svg>
    """,
    "Hall of Fame": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#f1c40f" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Hall of Fame
      </text>
    </svg>
    """,
    "Leaderboard": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#16a085" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Leaderboard
      </text>
    </svg>
    """,
    "Vidéo du dernier cours": """
    <svg width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="150" fill="#9b59b6" />
      <text x="50%" y="50%" fill="#ffffff" font-size="36" text-anchor="middle" dy=".3em">
        Vidéo du dernier cours
      </text>
    </svg>
    """
}

# -----------------------------------------------------------------------------
# Page d'accueil
# -----------------------------------------------------------------------------
if choice == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Accueil"], unsafe_allow_html=True)
    st.header("Bienvenue sur Suivi EPS 🏆")
    st.write("Utilisez le menu à gauche pour naviguer entre les sections.")
    st.markdown(f"**Mode d'accès :** {st.session_state['role'].capitalize()} ({st.session_state['user']})")
    if st.session_state["role"] == "teacher":
        if st.download_button("Télécharger le fichier CSV", data=st.session_state["students"].to_csv(index=False), file_name="students_data.csv", mime="text/csv"):
            st.success("Fichier téléchargé.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.balloons()

# -----------------------------------------------------------------------------
# Page d'ajout d'élève (enseignant uniquement)
# -----------------------------------------------------------------------------
elif choice == "Ajouter Élève":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(images["Ajouter Élève"], unsafe_allow_html=True)
        st.header("➕ Ajout des participant.e.s")
        with st.form("ajouter_eleve_form"):
            nom = st.text_input("Nom")
            niveau = st.number_input("Niveau de départ", min_value=0, max_value=10000, step=1)
            points_comp = niveau * 5
            st.write(f"**Points de Compétence disponibles :** {points_comp}")
            st.markdown("### Allocation des points entre les compétences")
            remaining_points = points_comp
            faveds = st.number_input("FAVEDS 🤸", min_value=0, max_value=remaining_points, step=1, value=0)
            remaining_points -= faveds
            strategie = st.number_input("Stratégie 🧠", min_value=0, max_value=remaining_points, step=1, value=0)
            remaining_points -= strategie
            cooperation = st.number_input("Coopération 🤝", min_value=0, max_value=remaining_points, step=1, value=0)
            remaining_points -= cooperation
            engagement = st.number_input("Engagement 🌟", min_value=0, max_value=remaining_points, step=1, value=remaining_points)
            submit_eleve = st.form_submit_button("Ajouter l'élève")
        if submit_eleve and nom:
            new_data = pd.DataFrame({
                "Nom": [nom],
                "Niveau": [niveau],
                "Points de Compétence": [points_comp],
                "FAVEDS 🤸": [faveds],
                "Stratégie 🧠": [strategie],
                "Coopération 🤝": [cooperation],
                "Engagement 🌟": [engagement],
                "Rôles": ["Apprenti(e)"],
                "Pouvoirs": [""],
                "StudentCode": [""],
            })
            st.session_state["students"] = pd.concat([st.session_state["students"], new_data], ignore_index=True)
            for col in ["Niveau", "Points de Compétence", "FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]:
                st.session_state["students"][col] = pd.to_numeric(st.session_state["students"][col], errors="coerce").fillna(0).astype(int)
            save_data(st.session_state["students"])
            st.success(f"✅ {nom} ajouté avec niveau {niveau} et répartition des points complétée.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page du tableau de progression
# -----------------------------------------------------------------------------
elif choice == "Tableau de progression":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Tableau de progression"], unsafe_allow_html=True)
    st.header("📊 Tableau de progression")
    st.markdown("**Modifiez directement les valeurs dans le tableau ci-dessous.**")
    def validate_competences(df):
        invalid = []
        for idx, row in df.iterrows():
            total_comp = row["FAVEDS 🤸"] + row["Stratégie 🧠"] + row["Coopération 🤝"] + row["Engagement 🌟"]
            if total_comp > row["Points de Compétence"]:
                invalid.append(row["Nom"])
        return invalid
    if st.session_state["role"] == "teacher":
        edited_df = st.data_editor(st.session_state["students"], num_rows="dynamic", use_container_width=True, key="editor_teacher")
        if st.button("Enregistrer modifications", key="save_teacher"):
            invalid_rows = validate_competences(edited_df)
            if invalid_rows:
                st.error(f"Erreur : {', '.join(invalid_rows)} ont une répartition incorrecte.")
            else:
                st.session_state["students"] = edited_df
                save_data(st.session_state["students"])
                st.success("Modifications enregistrées.")
    else:
        my_data = st.session_state["students"][st.session_state["students"]["Nom"] == st.session_state["user"]]
        edited_my_data = st.data_editor(my_data, use_container_width=True, key="editor_student")
        if st.button("Enregistrer modifications", key="save_student"):
            invalid_rows = validate_competences(edited_my_data)
            if invalid_rows:
                st.error("Erreur : répartition des points incorrecte.")
            else:
                df = st.session_state["students"].copy()
                idx = df.index[df["Nom"] == st.session_state["user"]]
                if len(idx) > 0:
                    df.loc[idx[0]] = edited_my_data.iloc[0]
                st.session_state["students"] = df
                save_data(st.session_state["students"])
                st.success("Vos modifications ont été enregistrées.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page d'attribution de niveaux (enseignant uniquement)
# -----------------------------------------------------------------------------
elif choice == "Attribution de niveaux":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(images["Attribution de niveaux"], unsafe_allow_html=True)
        st.write("Sélectionnez les élèves et le nombre de niveaux à ajouter (chaque niveau donne 5 points de compétence).")
        if "level_assignments" not in st.session_state:
            st.session_state["level_assignments"] = []
        with st.form("form_attribution"):
            selected_students = st.multiselect("Sélectionnez les élèves", options=st.session_state["students"]["Nom"].tolist())
            level_to_add = st.selectbox("Nombre de niveaux à ajouter", options=[1, 2, 3, 4, 6, 8])
            submit_assignment = st.form_submit_button("Ajouter à la liste")
        if submit_assignment:
            if not selected_students:
                st.error("Veuillez sélectionner au moins un élève.")
            else:
                st.session_state["level_assignments"].append({"students": selected_students, "levels": level_to_add})
                st.success(f"Attribution ajoutée : {', '.join(selected_students)} +{level_to_add} niveaux.")
        if st.session_state["level_assignments"]:
            st.write("### Attributions en attente")
            for i, assignment in enumerate(st.session_state["level_assignments"]):
                st.write(f"{i+1}. {', '.join(assignment['students'])} : +{assignment['levels']} niveaux")
            if st.button("Valider toutes les attributions"):
                for assignment in st.session_state["level_assignments"]:
                    for student in assignment["students"]:
                        idx = st.session_state["students"].index[st.session_state["students"]["Nom"] == student]
                        if len(idx) > 0:
                            idx = idx[0]
                            st.session_state["students"].at[idx, "Niveau"] += assignment["levels"]
                            st.session_state["students"].at[idx, "Points de Compétence"] += assignment["levels"] * 5
                save_data(st.session_state["students"])
                st.success("Les attributions ont été appliquées.")
                st.session_state["level_assignments"] = []
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page Hall of Fame (accessible à tous, modifiable uniquement par l'enseignant)
# -----------------------------------------------------------------------------
elif choice == "Hall of Fame":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Hall of Fame"], unsafe_allow_html=True)
    st.header("🏆 Hall of Fame")
    # Recharger le Hall of Fame depuis le fichier
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
            # Recherche dans la DataFrame pour obtenir l'URL de l'avatar
            student_info = st.session_state["students"].loc[st.session_state["students"]["Nom"] == entry["name"]]
            if not student_info.empty:
                avatar_url = student_info.iloc[0].get("Avatar", "")
                if avatar_url:
                    st.image(avatar_url, width=100)
            st.markdown(f"**{entry['name']}** : {entry['achievement']}")
        else:
            st.markdown("*Entrée vide*")
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Page Leaderboard (classement automatique par Points de Compétence)
# -----------------------------------------------------------------------------
elif choice == "Leaderboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Leaderboard"], unsafe_allow_html=True)
    st.header("🏆 Leaderboard")
    # Tri automatique des élèves par points décroissants
    leaderboard = st.session_state["students"].sort_values("Points de Compétence", ascending=False)
    st.subheader("Le top ten")
    top3 = leaderboard.head(10)
    for rank, (_, row) in enumerate(top3.iterrows(), start=1):
        st.markdown(
            f"**{rank}. {row['Nom']}** - Niveau: {row['Niveau']} - Points: {row['Points de Compétence']}<br>"
            f"**Rôle:** {row['Rôles']} | **Pouvoirs:** {row['Pouvoirs']} :trophy:",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page Vidéo du dernier cours (accessible à tous, modifiable uniquement par l'enseignant)
# -----------------------------------------------------------------------------
elif choice == "Vidéo du dernier cours":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Vidéo du dernier cours"], unsafe_allow_html=True)
    st.header("📹 Vidéo du dernier cours")
    
    video_filename = "uploaded_video.mp4"
    
    # Pour l'enseignant : possibilité d'uploader ou de retirer la vidéo
    if st.session_state["role"] == "teacher":
        st.subheader("Gérer la vidéo")
        uploaded_file = st.file_uploader("Uploader une vidéo (format MP4)", type=["mp4"])
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_file is not None:
                # Sauvegarde du fichier uploadé sur le disque
                with open(video_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Vidéo téléchargée avec succès!")
        with col2:
            if os.path.exists(video_filename):
                if st.button("Retirer la vidéo"):
                    os.remove(video_filename)
                    st.success("Vidéo retirée avec succès!")
    
    # Affichage de la vidéo pour tous
    if os.path.exists(video_filename):
        st.video(video_filename)
    else:
        st.info("Aucune vidéo n'a encore été téléchargée pour le dernier cours.")
    
    st.markdown('</div>', unsafe_allow_html=True)



# -----------------------------------------------------------------------------
# Page de la fiche élève
# -----------------------------------------------------------------------------
elif choice == "Fiche Élève":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(images["Fiche Élève"], unsafe_allow_html=True)
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
        with col2:
            st.write(f"**FAVEDS 🤸 :** {student_data['FAVEDS 🤸']}")
            st.write(f"**Stratégie 🧠 :** {student_data['Stratégie 🧠']}")
            st.write(f"**Coopération 🤝 :** {student_data['Coopération 🤝']}")
            st.write(f"**Engagement 🌟 :** {student_data['Engagement 🌟']}")
        onglets = st.tabs(["🛒 Boutique des Pouvoirs", "🏅 Boutique des Rôles"])
        with onglets[0]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
        with onglets[1]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            roles_store = {
                "🧪 Testeur.euse": {"Coût": 200, "Compétences Requises": ["FAVEDS 🤸"]},
                "🎭 Démonstrateur.rice": {"Coût": 150, "Compétences Requises": ["FAVEDS 🤸", "Engagement 🌟"]},
                "🔧 Facilitateur.rice": {"Coût": 150, "Compétences Requises": ["Coopération 🤝", "Engagement 🌟"]},
                "⚖️ Créateur.rice de règles": {"Coût": 250, "Compétences Requises": ["Stratégie 🧠"]},
                "🎯 Meneur.euse tactique": {"Coût": 250, "Compétences Requises": ["Stratégie 🧠", "Coopération 🤝"]},
                "⚖️ Arbitre / Régulateur.rice": {"Coût": 300, "Compétences Requises": ["Stratégie 🧠", "Engagement 🌟"]},
                "🤝 Aide-Coach": {"Coût": 250, "Compétences Requises": ["Coopération 🤝", "Engagement 🌟"]},
                "📋 Coordinateur.rice de groupe": {"Coût": 300, "Compétences Requises": ["Coopération 🤝"]},
                "🌍 Facilitateur.rice (social)": {"Coût": 250, "Compétences Requises": ["Coopération 🤝", "Engagement 🌟"]},
                "⚡ Réducteur.rice des contraintes": {"Coût": 200, "Compétences Requises": ["FAVEDS 🤸", "Engagement 🌟"]},
                "🛤️ Autonome": {"Coût": 200, "Compétences Requises": ["Stratégie 🧠", "Engagement 🌟"]},
                "🏆 Responsable de séance": {"Coût": 350, "Compétences Requises": ["Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]}
            }
            selected_role = st.selectbox("🎭 Choisir un rôle", list(roles_store.keys()), key="roles")
            role_cost = roles_store[selected_role]["Coût"]
            required_compétences = roles_store[selected_role]["Compétences Requises"]
            st.info(f"💰 Coût: {role_cost} points de compétence\n\n🔹 Compétences requises: {', '.join(required_compétences)}")
            if st.button("Acquérir ce rôle", key="acheter_role"):
                student_compétences = {
                    "FAVEDS 🤸": int(student_data["FAVEDS 🤸"]),
                    "Stratégie 🧠": int(student_data["Stratégie 🧠"]),
                    "Coopération 🤝": int(student_data["Coopération 🤝"]),
                    "Engagement 🌟": int(student_data["Engagement 🌟"])
                }
                if int(student_data["Points de Compétence"]) >= role_cost and all(student_compétences[comp] > 0 for comp in required_compétences):
                    current_points = int(student_data["Points de Compétence"])
                    new_points = current_points - role_cost
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"] = new_points
                    anciens_roles = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
                    nouveaux_roles = anciens_roles + ", " + selected_role if anciens_roles else selected_role
                    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Rôles"] = nouveaux_roles
                    save_data(st.session_state["students"])
                    st.success(f"🏅 {selected_student} a acquis le rôle '{selected_role}'.")
                else:
                    st.error("❌ Points de compétence insuffisants ou compétences requises non atteintes !")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
