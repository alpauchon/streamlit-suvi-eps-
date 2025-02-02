import streamlit as st
import pandas as pd

# 🔐 Vérification du code d'accès et gestion des règles du jeu
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

def check_password():
    """Vérifie si le mot de passe entré est correct et passe aux règles du jeu"""
    user_password = st.text_input("🔑 Entrez le code d'accès :", type="password")
    if st.button("Valider"):
        if user_password == st.secrets["ACCESS_CODE"]:
            st.session_state["authenticated"] = True
            st.success("✅ Accès autorisé !")
            st.rerun()  # Redémarre l'app proprement sans erreurs
        else:
            st.error("❌ Code incorrect, essayez encore.")

if not st.session_state["authenticated"]:
    st.title("🔒 Espace sécurisé")
    check_password()
    st.stop()

# 🔄 Affichage des règles après authentification
if not st.session_state["accepted_rules"]:
    st.title("📜 Système")
    st.markdown("""
    - L’élève peut gagner **4 niveaux** par séance de 45 minutes.
      - **1 niveau** pour le fair-play.
      - **1 niveau** pour le respect.
      - **1 niveau** pour l’investissement.
      - **1 niveau** pour l’atteinte des objectifs du cours.
    - Tous les élèves commencent avec le rôle **d’Apprenti(e)**.
    - **1 niveau = 5 points de compétences** à répartir librement.
    - Chaque élève peut se spécialiser dans **2 compétences uniquement**.

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
    
    if st.button("OK, j'ai compris les règles"):
        st.session_state["accepted_rules"] = True
        st.rerun()  # Recharge l'application pour afficher la suite
    st.stop()



# Configuration générale de l'application
st.set_page_config(page_title="Suivi EPS", page_icon="🏆", layout="wide")

# Chargement et sauvegarde des données
def load_data():
    try:
        df = pd.read_csv("students_data.csv")
        if df.empty:
            raise FileNotFoundError
        df["Pouvoirs"] = df["Pouvoirs"].astype(str)  # Assurer que la colonne Pouvoirs est bien une chaîne de caractères
        print("[INFO] Données chargées avec succès.")
        return df.fillna(0)  # Remplissage des valeurs NaN avec 0
    except FileNotFoundError:
        print("[WARNING] Fichier non trouvé, création d'un nouveau DataFrame.")
        return pd.DataFrame({
            "Nom": [], "Niveau": [], "Points de Compétence": [],
            "FAVEDS 🤸": [], "Stratégie 🧠": [], "Coopération 🤝": [], "Engagement 🌟": [],
            "Rôles": [], "Pouvoirs": []
        })

def save_data(df):
    df.to_csv("students_data.csv", index=False)
    print("[INFO] Données sauvegardées.")

if "students" not in st.session_state:
    st.session_state["students"] = load_data()
if "accepted_rules" not in st.session_state:
    st.session_state["accepted_rules"] = False

# Affichage de la première page avec les règles du jeu
if not st.session_state["accepted_rules"]:
    st.title("📜 Règles du Jeu")
    st.markdown("""
    - L’élève peut gagner **4 niveaux** par séance de 45 minutes.
      - **1 niveau** pour le fair-play.
      - **1 niveau** pour le respect.
      - **1 niveau** pour l’investissement.
      - **1 niveau** pour l’atteinte des objectifs du cours.
    - Tous les élèves commencent avec le rôle **d’Apprenti(e)**.
    - **1 niveau = 5 points de compétences** à répartir librement.
    - Chaque élève peut se spécialiser dans **2 compétences uniquement**.
    
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
    
    if st.button("OK, j'ai compris les règles"):
        st.session_state["accepted_rules"] = True
    st.stop()

# Ajout d'un élève
st.title("➕ Ajout des participant.es")
nom = st.text_input("Nom")
niveau = st.number_input("Niveau de départ", min_value=0, max_value=10000, step=1)
points_comp = niveau * 5

# Allocation de points librement entre les compétences
remaining_points = points_comp
faveds = st.number_input("FAVEDS 🤸", min_value=0, max_value=remaining_points, step=1, value=0)
remaining_points -= faveds
strategie = st.number_input("Stratégie 🧠", min_value=0, max_value=remaining_points, step=1, value=0)
remaining_points -= strategie
cooperation = st.number_input("Coopération 🤝", min_value=0, max_value=remaining_points, step=1, value=0)
remaining_points -= cooperation
engagement = st.number_input("Engagement 🌟", min_value=0, max_value=remaining_points, step=1, value=remaining_points)

if st.button("Ajouter l'élève") and nom:
    new_data = pd.DataFrame({
        "Nom": [nom], "Niveau": [niveau], "Points de Compétence": [points_comp],
        "FAVEDS 🤸": [faveds], "Stratégie 🧠": [strategie], "Coopération 🤝": [cooperation], "Engagement 🌟": [engagement],
        "Rôles": ["Apprenti(e)"], "Pouvoirs": [""]
    })
    st.session_state["students"] = pd.concat([st.session_state["students"], new_data], ignore_index=True).fillna("")
    save_data(st.session_state["students"])
    print(f"[INFO] Élève ajouté: {nom}, Niveau: {niveau}, Points: {points_comp}")
    st.success(f"✅ {nom} ajouté avec niveau {niveau} et répartition des points complétée.")

# Affichage du tableau général
st.title("📊 Tableau de progression")
st.markdown("**Modifiez directement les valeurs dans le tableau ci-dessous.**")
if not st.session_state["students"].empty:
    st.session_state["students"] = st.data_editor(st.session_state["students"], num_rows="dynamic", use_container_width=True).fillna("")
    save_data(st.session_state["students"])
    print("[INFO] Tableau des élèves mis à jour.")

# Sélection d'un élève pour voir sa fiche détaillée
st.subheader("🔍 Sélectionner un élève")
if not st.session_state["students"].empty:
    selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    if selected_student and not st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].empty:
        student_data = st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].iloc[0]
        
        st.title(f"📌 Fiche de {selected_student}")
        st.write(f"**Niveau :** {student_data['Niveau']}")
        st.write(f"**Points de Compétence :** {student_data['Points de Compétence']}")
        print(f"[INFO] Chargement de la fiche de {selected_student}")
        
              st.write("### 🛒 Boutique des Pouvoirs")
        store_items = {
            "Le malin / la maligne": 40,
            "Choix d’un jeu (5 min) ou donner 20 niveaux": 50,
            "Maître des groupes (1h30) ou doubler points de compétence": 100,
            "Maître du thème d’une séance": 150,
            "Roi / Reine de la séquence": 300
        }
      
        selected_item = st.selectbox("🛍️ Choisir un pouvoir", list(store_items.keys()))
        if st.button("Acheter"):
            cost = store_items[selected_item]
            if student_data["Niveau"] >= cost:
                st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"] -= cost
                pouvoirs_anciens = str(student_data["Pouvoirs"]) if pd.notna(student_data["Pouvoirs"]) else ""
                nouveaux_pouvoirs = pouvoirs_anciens + ", " + selected_item if pouvoirs_anciens else selected_item
                st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] = nouveaux_pouvoirs
                save_data(st.session_state["students"])
                print(f"[INFO] {selected_student} a acheté {selected_item} pour {cost} niveaux.")
                st.success(f"🛍️ {selected_student} a acheté '{selected_item}'.")
            else:
                print(f"[WARNING] {selected_student} n'a pas assez de niveaux pour acheter {selected_item}.")
                st.error("❌ Niveaux insuffisants !")
              
# 🏅 Boutique des Rôles
st.write("### 🏅 Boutique des Rôles")

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
    
selected_role = st.selectbox("🎭 Choisir un rôle", list(roles_store.keys()))
role_cost = roles_store[selected_role]["Coût"]
required_competences = roles_store[selected_role]["Compétences Requises"]

# Affichage des coûts et compétences requises
st.info(f"💰 Coût: {role_cost} points de compétence\n\n🔹 Compétences requises: {', '.join(required_competences)}")

if st.button("Acquérir ce rôle"):
    student_competences = {
        "FAVEDS 🤸": student_data["FAVEDS 🤸"],
        "Stratégie 🧠": student_data["Stratégie 🧠"],
        "Coopération 🤝": student_data["Coopération 🤝"],
        "Engagement 🌟": student_data["Engagement 🌟"]
    }

    if student_data["Points de Compétence"] >= role_cost and all(student_competences[comp] > 0 for comp in required_competences):
        st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Points de Compétence"] -= role_cost
        roles_anciens = str(student_data["Rôles"]) if pd.notna(student_data["Rôles"]) else ""
        nouveaux_roles = roles_anciens + ", " + selected_role if roles_anciens else selected_role
        st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Rôles"] = nouveaux_roles
        save_data(st.session_state["students"])
        st.success(f"🏅 {selected_student} a acquis le rôle '{selected_role}'.")
    else:
        st.error("❌ Points de compétence insuffisants ou compétences requises non atteintes !")
