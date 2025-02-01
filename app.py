import streamlit as st
import pandas as pd

# Fonction pour charger les données sauvegardées
def load_data():
    try:
        return pd.read_csv("students_data.csv")
    except FileNotFoundError:
        return pd.DataFrame({"Nom": [], "Niveau": [], "Points de Compétence": [], "Compétences": []})

# Fonction pour sauvegarder les données
def save_data(df):
    df.to_csv("students_data.csv", index=False)

# Chargement des données
if "students" not in st.session_state:
    st.session_state["students"] = load_data()

# Données des rôles
roles_data = {
    "Rôle": ["🧪 Testeur.euse", "🎭 Démonstrateur.rice", "🔧 Facilitateur.rice", "⚖️ Créateur.rice de règles",
              "🎯 Meneur.euse tactique", "⚖️ Arbitre / Régulateur.rice", "🤝 Aide-Coach", "📋 Coordinateur.rice de groupe",
              "🌍 Facilitateur.rice (social)", "⚡ Réducteur.rice des contraintes", "🛤️ Autonome", "🏆 Responsable de séance"],
    "Points nécessaires": [200, 150, 150, 250, 250, 300, 250, 300, 250, 200, 200, 350],
    "Compétences requises": ["FAVEDS 🤸", "FAVEDS 🤸 + Engagement 🌟", "Coopération 🤝 + Engagement 🌟", "Stratégie 🧠",
                              "Stratégie 🧠 + Coopération 🤝", "Stratégie 🧠 + Engagement 🌟", "Coopération 🤝 + Engagement 🌟",
                              "Coopération 🤝", "Coopération 🤝 + Engagement 🌟", "FAVEDS 🤸 + Engagement 🌟",
                              "Stratégie 🧠 + Engagement 🌟", "Stratégie 🧠 + Coopération 🤝 + Engagement 🌟"]
}
roles_df = pd.DataFrame(roles_data)

st.title("📊 Suivi de Progression en EPS")

# Mise en page avec colonnes
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Ajouter un élève")
    nom = st.text_input("Nom de l'élève")
    niveau = st.number_input("Niveau", min_value=0, max_value=1000, step=1)
    points_comp = st.number_input("Points de compétence", min_value=0, max_value=5000, step=5)
    competences = st.multiselect("Compétences principales", ["FAVEDS 🤸", "Stratégie 🧠", "Coopération 🤝", "Engagement 🌟"])
    
    if st.button("Ajouter l'élève") and nom:
        new_data = pd.DataFrame({"Nom": [nom], "Niveau": [niveau], "Points de Compétence": [points_comp], "Compétences": [", ".join(competences)]})
        st.session_state["students"] = pd.concat([st.session_state["students"], new_data], ignore_index=True)
        save_data(st.session_state["students"])
        st.success(f"✅ {nom} ajouté avec niveau {niveau} et {points_comp} points de compétence.")

with col2:
    st.header("📋 Liste des élèves")
    st.dataframe(st.session_state["students"], height=250)
    
    # Modifier le niveau d'un élève
    st.header("🛠 Modifier un élève")
    if not st.session_state["students"].empty:
        selected_student = st.selectbox("🎓 Sélectionner un élève à modifier", st.session_state["students"]["Nom"])
        if selected_student:
            new_level = st.number_input("Modifier le niveau", min_value=0, max_value=10, step=1, value=int(st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"].values[0]))
            if st.button("Mettre à jour le niveau"):
                st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Niveau"] = new_level
                save_data(st.session_state["students"])
                st.success(f"✅ Niveau de {selected_student} mis à jour à {new_level}.")
    
    # Supprimer un élève
    st.header("🗑 Supprimer un élève")
    if not st.session_state["students"].empty:
        student_to_delete = st.selectbox("❌ Sélectionner un élève à supprimer", st.session_state["students"]["Nom"])
        if st.button("Supprimer"):
            st.session_state["students"] = st.session_state["students"][st.session_state["students"]["Nom"] != student_to_delete]
            save_data(st.session_state["students"])
            st.success(f"🗑 {student_to_delete} a été supprimé.")

# Attribution automatique des rôles
st.header("🎭 Attribution des Rôles")
if not st.session_state["students"].empty:
    selected_student = st.selectbox("🎓 Choisir un élève", st.session_state["students"]["Nom"])
    
    def assign_roles(points, competences):
        assigned_roles = roles_df[(roles_df["Points nécessaires"] <= points) & roles_df["Compétences requises"].apply(lambda x: any(comp in x for comp in competences))]
        return assigned_roles["Rôle"].tolist()
    
    if selected_student:
        student_data = st.session_state["students"][st.session_state["students"]["Nom"] == selected_student].iloc[0]
        roles = assign_roles(student_data["Points de Compétence"], student_data["Compétences"].split(", "))
        st.write(f"🎖️ Rôles attribués à **{selected_student}**:")
        st.success(roles)
