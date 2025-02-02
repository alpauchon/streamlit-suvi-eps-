import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# Importation de ChatterBot pour le chatbot
# -----------------------------------------------------------------------------
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# -----------------------------------------------------------------------------
# Configuration de la page et injection de CSS pour un design moderne
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Suivi EPS", page_icon="🏆", layout="wide")

st.markdown("""
<style>
/* Fond global */
body {
    background-color: #f0f2f6;
}

/* Style pour les cartes (sections) */
.card {
    background: #ffffff;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
}

/* Couleur des titres */
h1, h2, h3 {
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Fonction utilitaire pour redémarrer l'application
# -----------------------------------------------------------------------------
def rerun_app():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("La fonction de redémarrage automatique n'est pas disponible. Veuillez mettre à jour Streamlit.")

# -----------------------------------------------------------------------------
# Chargement et sauvegarde des données
# -----------------------------------------------------------------------------
def load_data():
    try:
        df = pd.read_csv("students_data.csv")
        if df.empty:
            raise FileNotFoundError
        # Si la colonne "StudentCode" n'existe pas, on la crée avec des valeurs vides,
        # sinon on remplace les valeurs manquantes par ""
        if "StudentCode" not in df.columns:
            df["StudentCode"] = ""
        else:
            df["StudentCode"] = df["StudentCode"].fillna("")
        # Assurer que "Pouvoirs" est de type chaîne
        df["Pouvoirs"] = df["Pouvoirs"].astype(str)
        # Conversion forcée des colonnes numériques
        for col in ["Niveau", "Points de Compétence", "FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        print("[INFO] Données chargées avec succès.")
        return df
    except FileNotFoundError:
        print("[WARNING] Fichier non trouvé, création d'un nouveau DataFrame.")
        return pd.DataFrame({
            "Nom": [], "Niveau": [], "Points de Compétence": [],
            "FAVEDS 🤸": [], "Stratégie 🧠": [], "Coopération 🤝": [], "Engagement 🌟": [],
            "Rôles": [], "Pouvoirs": [], "StudentCode": []
        })

def save_data(df):
    df.to_csv("students_data.csv", index=False)
    print("[INFO] Données sauvegardées.")

if "students" not in st.session_state:
    st.session_state["students"] = load_data()

# -----------------------------------------------------------------------------
# Initialisation des variables de session pour l'accès spécialisé
# -----------------------------------------------------------------------------
if "role" not in st.session_state:
    st.session_state["role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False
if "do_rerun" not in st.session_state:
    st.session_state["do_rerun"] = False

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
                st.session_state["do_rerun"] = True
                st.success("Accès enseignant autorisé.")
            else:
                st.error("Code incorrect.")
    else:  # Mode Élève
        if st.session_state["students"].empty:
            st.warning("Aucun élève n'est enregistré. Veuillez contacter votre enseignant.")
        else:
            student_name = st.selectbox("Choisissez votre nom", st.session_state["students"]["Nom"])
            # Récupérer la ligne correspondant à l'élève sélectionné
            student_row = st.session_state["students"].loc[st.session_state["students"]["Nom"] == student_name].iloc[0]
            if student_row["StudentCode"] == "":
                st.info("Première connexion : veuillez créer un code d'accès.")
                new_code = st.text_input("Créez un code d'accès (au moins 4 caractères)", type="password", key="new_student_code")
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
                        st.session_state["do_rerun"] = True
                        st.success(f"Accès élève autorisé pour {student_name}.")
            else:
                code_entered = st.text_input("Entrez votre code d'accès", type="password", key="existing_student_code")
                if st.button("Se connecter comme élève", key="student_conn"):
                    if code_entered != student_row["StudentCode"]:
                        st.error("Code incorrect.")
                    else:
                        st.session_state["role"] = "student"
                        st.session_state["user"] = student_name
                        st.session_state["do_rerun"] = True
                        st.success(f"Accès élève autorisé pour {student_name}.")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state["do_rerun"]:
        st.session_state["do_rerun"] = False
        rerun_app()
    st.stop()

# -----------------------------------------------------------------------------
# Bloc d'acceptation des règles (commun aux deux modes)
# -----------------------------------------------------------------------------
if not st.session_state["accepted_rules"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📜 Règles du système")
    st.markdown("""
    - L’élève peut gagner **4 niveaux** par séance de 45 minutes.
      - **1 niveau** pour le fair-play.
      - **1 niveau** pour le respect.
      - **1 niveau** pour l’investissement.
      - **1 niveau** pour l’atteinte des objectifs du cours.
    - Tous les élèves commencent avec le rôle **d’Apprenti(e)**.
    - **1 niveau = 5 points de compétences** à répartir librement.
    - Chaque élève peut se spécialiser dans **2 compétences uniquement**.
    - L'élève peut acheter des pouvoirs ou des rôles avec ses niveaux et compétences.
    
       ### 🏪 Boutique des rôles et pouvoirs
    | Rôles | Points nécessaires | Compétences requises | Explication |
    |---|---|---|---|
    | Testeur.euse | 200 | FAVEDS | Peut essayer en premier les nouveaux exercices. |
    | Démonstrateur.rice | 150 | FAVEDS + Engagement | Présente les mouvements au reste du groupe. |
    | Facilitateur.rice | 150 | Coopération + Engagement | Moins de répétitions imposées s’il maîtrise déjà l’exercice. |
    | Créateur.rice de règles | 250 | Stratégie | Peut modifier certaines règles des exercices. |
    | Meneur.euse tactique | 250 | Stratégie + Coopération | Oriente une équipe et propose des stratégies. |
    | Arbitre / Régulateur.rice | 300 | Stratégie + Engagement | Aide à gérer les litiges et les décisions collectives. |
    | Aide-coach | 250 | Coopération + Engagement | Peut accompagner un élève en difficulté. |
    | Coordinateur.rice de groupe | 300 | Coopération | Premier choix des groupes. |
    | Facilitateur.rice (social) | 250 | Coopération + Engagement | Peut proposer des ajustements pour favoriser l’intégration de tous. |
    | Réducteur.rice des contraintes | 200 | FAVEDS + Engagement | Accès à des versions simplifiées ou allégées des consignes. |
    | Autonome | 200 | Stratégie + Engagement | Peut choisir son propre parcours ou défi. |
    | Responsable de séance | 350 | Stratégie + Coopération + Engagement | Peut diriger une partie de la séance. |
    
    ### 🏪 Boutique secrète
    | Coût en niveau | Pouvoirs à choix |
    |---|---|
    | 40 | Le malin / la maligne : doubler ses niveaux gagnés à chaque cours. |
    | 50 | Choix d’un jeu (5 min) ou donner 20 niveaux à quelqu’un. |
    | 100 | Maître.sse des groupes pour une séance de 1h30 ou doubler ses points de compétences. |
    | 150 | Maître.sse du thème d’une prochaine séance. |
    | 300 | Roi / Reine de la séquence (permet de choisir le prochain thème que l’on fera pour 4 à 6 cours). |
    """)
    if st.button("OK, j'ai compris les règles", key="accept_rules"):
        st.session_state["accepted_rules"] = True
        st.session_state["do_rerun"] = True
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state["do_rerun"]:
        st.session_state["do_rerun"] = False
        rerun_app()
    st.stop()

# -----------------------------------------------------------------------------
# Définition des pages disponibles selon le rôle
# -----------------------------------------------------------------------------
if st.session_state["role"] == "teacher":
    pages = ["Accueil", "Ajouter Élève", "Tableau de progression", "Fiche Élève", "Chatbot"]
else:  # Mode Élève
    pages = ["Accueil", "Tableau de progression", "Fiche Élève", "Chatbot"]

choice = st.sidebar.radio("Navigation", pages)

# -----------------------------------------------------------------------------
# Page d'accueil
# -----------------------------------------------------------------------------
if choice == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Bienvenue sur le Suivi EPS 🏆")
    st.write("Utilisez le menu à gauche pour naviguer entre les différentes sections de l'application.")
    st.markdown(f"**Mode d'accès :** {st.session_state['role'].capitalize()} ({st.session_state['user']})")
    
    # Bouton de téléchargement réservé à l'enseignant
    if st.session_state["role"] == "teacher":
        if st.download_button(
            "Télécharger le fichier CSV",
            data=st.session_state["students"].to_csv(index=False),
            file_name="students_data.csv",
            mime="text/csv"
        ):
            st.success("Fichier téléchargé.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page d'ajout d'élève (enseignant uniquement)
# -----------------------------------------------------------------------------
elif choice == "Ajouter Élève":
    if st.session_state["role"] != "teacher":
        st.error("Accès réservé aux enseignants.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("➕ Ajout des participant.es")
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
                "StudentCode": [""]
            })
            st.session_state["students"] = pd.concat(
                [st.session_state["students"], new_data],
                ignore_index=True
            )
            # Reconvertir les colonnes numériques après ajout
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
    st.header("📊 Tableau de progression")
    st.markdown("**Modifiez directement les valeurs dans le tableau ci-dessous.**")
    # Fonction de validation de la somme des points attribués aux compétences
    def validate_competences(df):
        invalid = []
        for idx, row in df.iterrows():
            total_comp = row["FAVEDS 🤸"] + row["Stratégie 🧠"] + row["Coopération 🤝"] + row["Engagement 🌟"]
            if total_comp > row["Points de Compétence"]:
                invalid.append(row["Nom"])
        return invalid

    if st.session_state["role"] == "teacher":
        edited_df = st.data_editor(
            st.session_state["students"],
            num_rows="dynamic",
            use_container_width=True,
            key="editor_teacher"
        )
        if st.button("Enregistrer modifications", key="save_teacher"):
            invalid_rows = validate_competences(edited_df)
            if invalid_rows:
                st.error(f"Erreur : les élèves suivants ont une somme de compétences supérieure aux points disponibles : {', '.join(invalid_rows)}")
            else:
                st.session_state["students"] = edited_df
                save_data(st.session_state["students"])
                st.success("Modifications enregistrées.")
    else:
        my_data = st.session_state["students"][st.session_state["students"]["Nom"] == st.session_state["user"]]
        edited_my_data = st.data_editor(
            my_data,
            use_container_width=True,
            key="editor_student"
        )
        if st.button("Enregistrer modifications", key="save_student"):
            invalid_rows = validate_competences(edited_my_data)
            if invalid_rows:
                st.error("Erreur : la somme de vos points de compétences dépasse vos points disponibles.")
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
# Page de la fiche élève
# -----------------------------------------------------------------------------
elif choice == "Fiche Élève":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🔍 Fiche de l'élève")
    if st.session_state["role"] == "teacher":
        selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    else:
        selected_student = st.session_state["user"]
        st.info(f"Vous êtes connecté(e) en tant que {selected_student}.")
    
    if selected_student:
        student_data = st.session_state["students"].loc[
            st.session_state["students"]["Nom"] == selected_student
        ].iloc[0]
        st.subheader(f"📌 Fiche de {selected_student}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Niveau :** {student_data['Niveau']}")
            st.write(f"**Points de Compétence :** {student_data['Points de Compétence']}")
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
                    st.session_state["students"].loc[
                        st.session_state["students"]["Nom"] == selected_student, "Niveau"
                    ] = new_level
                    pouvoirs_anciens = str(student_data["Pouvoirs"]) if pd.notna(student_data["Pouvoirs"]) else ""
                    nouveaux_pouvoirs = pouvoirs_anciens + ", " + selected_item if pouvoirs_anciens else selected_item
                    st.session_state["students"].loc[
                        st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"
                    ] = nouveaux_pouvoirs
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
                    st.session_state["students"].loc[
                        st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"
                    ] = new_points
                    roles_anciens = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
                    nouveaux_roles = roles_anciens + ", " + selected_role if roles_anciens else selected_role
                    st.session_state["students"].loc[
                        st.session_state["students"]["Nom"] == selected_student, "Rôles"
                    ] = nouveaux_roles
                    save_data(st.session_state["students"])
                    st.success(f"🏅 {selected_student} a acquis le rôle '{selected_role}'.")
                else:
                    st.error("❌ Points de compétence insuffisants ou compétences requises non atteintes !")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Aucun élève n'a encore été ajouté. Veuillez ajouter un élève dans la section 'Ajouter Élève'.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Page Chatbot (accessible à tous)
# -----------------------------------------------------------------------------
elif choice == "Chatbot":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Chatbot interactif")
    # Initialiser le chatbot dans la session s'il n'est pas déjà présent
    if "chatbot" not in st.session_state:
        st.session_state["chatbot"] = ChatBot(
            'Assistant',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='sqlite:///database.sqlite3'
        )
        trainer = ChatterBotCorpusTrainer(st.session_state["chatbot"])
        try:
            # Entraînement avec le corpus français
            trainer.train("chatterbot.corpus.french")
        except Exception as e:
            st.error("Erreur lors de l'entraînement du chatbot : " + str(e))
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    user_question = st.text_input("Posez votre question ici :", key="chat_input")
    if st.button("Envoyer", key="send_chat"):
        if user_question:
            st.session_state["chat_history"].append(("Vous", user_question))
            response = st.session_state["chatbot"].get_response(user_question)
            st.session_state["chat_history"].append(("Chatbot", str(response)))
    for sender, text in st.session_state["chat_history"]:
        st.write(f"**{sender} :** {text}")
    st.markdown('</div>', unsafe_allow_html=True)
