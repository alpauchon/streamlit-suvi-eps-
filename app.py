import streamlit as st
import pandas as pd

# Configuration générale de l'application
st.set_page_config(page_title="Suivi EPS", page_icon="🏆", layout="wide")

# Chargement et sauvegarde des données
def load_data():
    try:
        df = pd.read_csv("students_data.csv")
        if df.empty:
            raise FileNotFoundError
        return df
    except FileNotFoundError:
        return pd.DataFrame({"Nom": [], "Niveau": [], "Points de Compétence": [], "FAVEDS 🤸": [], "Stratégie 🧠": [], "Coopération 🤝": [], "Engagement 🌟": [], "Rôles": [], "Pouvoirs": []})

def save_data(df):
    df.to_csv("students_data.csv", index=False)

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
    """)
    
    if st.button("OK, j'ai compris les règles"):
        st.session_state["accepted_rules"] = True
    st.stop()

# Ajout d'un élève
st.title("➕ Ajouter un élève")
nom = st.text_input("Nom de l'élève")
niveau = st.number_input("Niveau de départ", min_value=0, max_value=10, step=1)
points_comp = niveau * 5
faveds = st.number_input("FAVEDS 🤸", min_value=0, max_value=points_comp, step=1)
strategie = st.number_input("Stratégie 🧠", min_value=0, max_value=points_comp - faveds, step=1)
cooperation = st.number_input("Coopération 🤝", min_value=0, max_value=points_comp - faveds - strategie, step=1)
engagement = points_comp - faveds - strategie - cooperation

if st.button("Ajouter l'élève") and nom:
    new_data = pd.DataFrame({
        "Nom": [nom], "Niveau": [niveau], "Points de Compétence": [points_comp],
        "FAVEDS 🤸": [faveds], "Stratégie 🧠": [strategie], "Coopération 🤝": [cooperation], "Engagement 🌟": [engagement], "Rôles": ["Apprenti(e)"], "Pouvoirs": [""]
    })
    st.session_state["students"] = pd.concat([st.session_state["students"], new_data], ignore_index=True)
    save_data(st.session_state["students"])
    st.success(f"✅ {nom} ajouté avec niveau {niveau} et répartition des points complétée.")

# Affichage du tableau général
st.title("📊 Suivi Général des Élèves")
st.markdown("**Modifiez directement les valeurs dans le tableau ci-dessous.**")
if not st.session_state["students"].empty:
    st.session_state["students"] = st.data_editor(st.session_state["students"], num_rows="dynamic", use_container_width=True)
    save_data(st.session_state["students"])

# Sélection d'un élève pour voir sa fiche détaillée
st.subheader("🔍 Sélectionner un élève")
if not st.session_state["students"].empty:
    selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    if selected_student and not st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].empty:
        student_data = st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student].iloc[0]
        
        st.title(f"📌 Fiche de {selected_student}")
        st.write(f"**Niveau :** {student_data['Niveau']}")
        st.write(f"**Points de Compétence :** {student_data['Points de Compétence']}")
        
        st.write("### 📊 Répartition des compétences")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            faveds = st.number_input("FAVEDS 🤸", value=int(student_data.get('FAVEDS 🤸', 0)), min_value=0, step=1)
        with col2:
            strategie = st.number_input("Stratégie 🧠", value=int(student_data.get('Stratégie 🧠', 0)), min_value=0, step=1)
        with col3:
            cooperation = st.number_input("Coopération 🤝", value=int(student_data.get('Coopération 🤝', 0)), min_value=0, step=1)
        with col4:
            engagement = st.number_input("Engagement 🌟", value=int(student_data.get('Engagement 🌟', 0)), min_value=0, step=1)
        
        if st.button("Mettre à jour les compétences"):
            st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, ["FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]] = [faveds, strategie, cooperation, engagement]
            save_data(st.session_state["students"])
            st.success(f"✅ Compétences mises à jour pour {selected_student}.")
