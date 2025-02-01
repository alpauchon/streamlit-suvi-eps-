import streamlit as st
import pandas as pd

# Configuration générale de l'application
st.set_page_config(page_title="Suivi EPS", page_icon="🏆", layout="wide")

# Chargement et sauvegarde des données
def load_data():
    try:
        return pd.read_csv("students_data.csv")
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

# Affichage du tableau général
st.title("📊 Suivi Général des Élèves")
st.markdown("**Modifiez directement les valeurs dans le tableau ci-dessous.**")
st.session_state["students"] = st.data_editor(st.session_state["students"], num_rows="dynamic", use_container_width=True)
save_data(st.session_state["students"])

# Sélection d'un élève pour voir sa fiche détaillée
st.subheader("🔍 Sélectionner un élève")
if not st.session_state["students"].empty:
    selected_student = st.selectbox("Choisir un élève", st.session_state["students"]["Nom"])
    if selected_student:
        student_data = st.session_state["students"][st.session_state["students"]["Nom"] == selected_student].iloc[0]
        
        st.title(f"📌 Fiche de {selected_student}")
        st.write(f"**Niveau :** {student_data['Niveau']}")
        st.write(f"**Points de Compétence :** {student_data['Points de Compétence']}")
        
        st.write("### 📊 Répartition des compétences")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            faveds = st.number_input("FAVEDS 🤸", value=int(student_data['FAVEDS 🤸']), min_value=0, step=1)
        with col2:
            strategie = st.number_input("Stratégie 🧠", value=int(student_data['Stratégie 🧠']), min_value=0, step=1)
        with col3:
            cooperation = st.number_input("Coopération 🤝", value=int(student_data['Coopération 🤝']), min_value=0, step=1)
        with col4:
            engagement = st.number_input("Engagement 🌟", value=int(student_data['Engagement 🌟']), min_value=0, step=1)
        
        if st.button("Mettre à jour les compétences"):
            st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, ["FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"]] = [faveds, strategie, cooperation, engagement]
            save_data(st.session_state["students"])
            st.success(f"✅ Compétences mises à jour pour {selected_student}.")
        
        # Boutiques
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
                st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] += f", {selected_item}" if student_data["Pouvoirs"] else selected_item
                save_data(st.session_state["students"])
                st.success(f"🛍️ {selected_student} a acheté '{selected_item}'.")
            else:
                st.error("❌ Niveaux insuffisants !")
