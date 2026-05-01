import os
import pandas as pd
import streamlit as st
import plotly.express as px
from io import StringIO
import re

st.set_page_config(
    page_title="UYI Data Analysis",
    page_icon=":material/school:",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .hero-section {
        background: linear-gradient(rgba(31, 59, 115, 0.8), rgba(31, 59, 115, 0.5)), 
                    url('https://res.cloudinary.com/db2aanter/image/upload/v1777477400/Image11-1024x676_sxxnnb.png');
        background-size: cover;
        background-position: center;
        padding: 60px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .big-title {
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 10px;
    }
    .sub {
        text-align:center;
        color:#5a6b8a;
        margin-bottom:30px;
    }
    @media (max-width: 768px) {
        .big-title {
            font-size: 24px;
        }
    }
    
    /* Remove sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Adjust main content to full width */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data_uy1.csv"
MATRICULES_FILE = "matricules.csv"
EXPECTED_COLUMNS = [
    "age", "filiere", "niveau", "heures_etude", "connexion", 
    "pc", "transport", "sommeil", "mgp", "stress", "presence", "sexe"
]

FILIERES = [
    "Informatique", "Mathematiques", "Physique", "ICT4D", "Biologie", 
    "Chimie", "Ingenierie (ENSPY)", "Energies Renouvelables", "Histoire", 
    "Langues (Anglais/Allemand etc.)", "Geographie", "Philosophie", 
    "Psychologie", "Sociologie", "Biochimie"
]

MGP_LIST = ["1-1.49", "1.5-1.99", "2-2.24", "2.25-2.49", "2.5-2.74", "2.75-2.99", "3-3.24", "3.25-3.74", "3.75-4"]

def initialise_data():
    default_data = [
        [22,"Ingenierie (ENSPY)","Master 1",35,"Wi-Fi Campus","Oui",15,5,"3.25-3.5",9,75,"Masculin"],
        [21,"Ingenierie (ENSPY)","Licence 3",30,"Wi-Fi Campus","Oui",20,5,"3-3.24",9,70,"Feminin"],
        [23,"Ingenierie (ENSPY)","Master 2",40,"Wi-Fi Campus","Oui",10,4,"3.25-3.5",10,80,"Masculin"],
        [20,"Ingenierie (ENSPY)","Licence 2",28,"Modem","Oui",25,5,"2.75-2.99",8,65,"Feminin"],
        [22,"Informatique","Master 1",32,"Modem","Oui",20,5,"3-3.24",8,72,"Masculin"],
        [21,"Informatique","Licence 3",28,"Wi-Fi Campus","Oui",25,5,"2.75-2.99",8,68,"Feminin"],
        [20,"Informatique","Licence 2",25,"Donnees Mobiles","Oui",30,5,"2.5-2.74",7,65,"Masculin"],
        [22,"Informatique","Licence 3",30,"Satellite","Oui",20,4,"3-3.24",9,70,"Feminin"],
        [21,"Mathematiques","Master 1",25,"Modem","Oui",30,6,"2.75-2.99",7,65,"Masculin"],
        [20,"Mathematiques","Licence 3",22,"Donnees Mobiles","Oui",35,6,"2.5-2.74",7,60,"Feminin"],
        [22,"Mathematiques","Licence 2",20,"Wi-Fi Campus","Non",40,6,"2.25-2.49",6,55,"Masculin"],
        [20,"Mathematiques","Licence 1",18,"Donnees Mobiles","Non",45,6,"2-2.24",6,50,"Feminin"],
        [21,"Physique","Master 1",20,"Modem","Oui",40,7,"2.5-2.74",6,58,"Masculin"],
        [20,"Physique","Licence 3",18,"Donnees Mobiles","Non",45,7,"2.25-2.49",5,55,"Feminin"],
        [22,"Physique","Licence 2",15,"Donnees Mobiles","Non",50,7,"2-2.24",5,50,"Masculin"],
        [21,"Chimie","Licence 3",18,"Donnees Mobiles","Oui",45,7,"2.25-2.49",5,55,"Feminin"],
        [20,"Chimie","Licence 2",15,"Donnees Mobiles","Non",50,7,"2-2.24",5,50,"Masculin"],
        [22,"Biologie","Master 1",15,"Donnees Mobiles","Non",55,8,"2-2.24",4,48,"Feminin"],
        [21,"Biologie","Licence 3",12,"Wifi Campus","Non",60,8,"1.75-1.99",4,45,"Masculin"],
        [20,"Biologie","Licence 2",10,"Donnees Mobiles","Non",65,8,"1.5-1.74",4,42,"Feminin"]
    ]
    
    # Initialiser le fichier principal
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        df_default = pd.DataFrame(default_data, columns=EXPECTED_COLUMNS)
        df_default.to_csv(DATA_FILE, index=False)
    
    
    if not os.path.exists(MATRICULES_FILE) or os.stat(MATRICULES_FILE).st_size == 0:
        pd.DataFrame(columns=["matricule", "date_soumission"]).to_csv(MATRICULES_FILE, index=False)

def load_data():
    initialise_data()
    return pd.read_csv(DATA_FILE)

def save_row(row):
    df = pd.DataFrame([row])
    df.to_csv(DATA_FILE, mode="a", header=False, index=False)

def check_matricule_exists(matricule):
    if not os.path.exists(MATRICULES_FILE) or os.stat(MATRICULES_FILE).st_size == 0:
        return False
    
    df = pd.read_csv(MATRICULES_FILE)
    return matricule in df["matricule"].values

def save_matricule(matricule):
    from datetime import datetime
    df = pd.DataFrame([[matricule, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], 
                      columns=["matricule", "date_soumission"])
    df.to_csv(MATRICULES_FILE, mode="a", header=False, index=False)

def validate_matricule_format(matricule):
    pattern = r'^\d{2}[A-Z]\d{4}$'
    return bool(re.match(pattern, matricule))

if 'user_df' not in st.session_state:
    st.session_state.user_df = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_matricule' not in st.session_state:
    st.session_state.user_matricule = ""

st.markdown(f"""
<div class="hero-section">
    <div class="logo-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/9/96/University_of_Yaound%C3%A9_I_Logo.png" width="100">
    </div>
    <div class="big-title">Analyses de la Performance et du Bien-Etre des Etudiants - UYI</div>
    <p>Contribuez aux donnees ou importez votre propre dataset pour l'analyser</p>
</div>
""", unsafe_allow_html=True)

choice = st.radio(
    "Choisissez un mode",
    ["Questionnaire", "Analyser vos propres donnees"],
    horizontal=True
)

st.markdown("""
<style>
    .custom-form {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .stSlider .stSlider > div > div {
        background-color: #4facfe !important;
    }
    
    .stSlider .stSlider > div > div > div {
        background-color: #1f3b73 !important;
    }
</style>
""", unsafe_allow_html=True)

if choice == "Questionnaire":
    
    if not st.session_state.authenticated:
        st.subheader("Authentification requise")
        st.markdown("Veuillez entrer votre matricule pour acceder au questionnaire")
        
        with st.form("auth_form"):
            matricule_input = st.text_input(
                "Matricule", 
                placeholder="Exemple: 24H2589", 
                max_chars=20,
                help="Format: 2 chiffres + 1 lettre + 4 chiffres (ex: 00A0000)"
            )
            submit_auth = st.form_submit_button("Verifier mon matricule", use_container_width=True)
            
            if submit_auth:
                if not matricule_input:
                    st.error("Veuillez entrer votre matricule")
                elif not validate_matricule_format(matricule_input):
                    st.error("Matricule invalide. Utilisez le format: 2 chiffres + 1 lettre + 4 chiffres")
                elif check_matricule_exists(matricule_input):
                    st.error(f"Le matricule {matricule_input} a deja rempli le formulaire. Chaque etudiant ne peut participer qu'une seule fois.")
                else:
                    st.session_state.user_matricule = matricule_input
                    st.session_state.authenticated = True
                    st.success(f"Matricule {matricule_input} verifie. Vous pouvez maintenant remplir le formulaire.")
                    st.rerun()
    
    elif st.session_state.authenticated:
        
        st.subheader("Formulaire Academique")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Se deconnecter", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_matricule = ""
                st.rerun()
        
        with st.form("survey_form"):
            c1, c2, c3 = st.columns(3)
            
            with c1:
                age = st.number_input("Age", 15, 60, 20)
                sexe = st.selectbox("Sexe", ["Masculin", "Feminin"])
                filiere = st.selectbox("Filiere", FILIERES)
                niveau = st.selectbox("Niveau", ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"])

            with c2:
                heures_etude = st.slider("Heures d'etude / semaine", 0, 50, 5)
                connexion = st.selectbox("Connexion principale", ["Donnees Mobiles", "Modem (Orange/MTN/...)", "Satellite (Starlink/...)", "Wi-Fi Campus"])
                pc = st.radio("Avez-vous un ordinateur ?", ["Oui", "Non"])
                transport = st.slider("Temps de transport (min/jour)", 0, 90, 20)

            with c3:
                sommeil = st.slider("Heures de sommeil / nuit", 3, 10, 6)
                mgp = st.selectbox("MGP", MGP_LIST)
                stress = st.slider("Niveau de stress (1-10)", 1, 10, 5)
                presence = st.slider("Taux de presence en cours (%)", 0, 100, 65)

            submit = st.form_submit_button("Enregistrer")

            if submit:
                save_row({
                    "age": age, "filiere": filiere, "niveau": niveau, "heures_etude": heures_etude,
                    "connexion": connexion, "pc": pc, "transport": transport, "sommeil": sommeil,
                    "mgp": mgp, "stress": stress, "presence": presence, "sexe": sexe
                })
                save_matricule(st.session_state.user_matricule)
                st.success("Donnees enregistrees avec succes !")
                st.session_state.user_df = None
                st.session_state.authenticated = False
                st.session_state.user_matricule = ""
                st.rerun()

else:
    st.subheader("Ajoutez votre propre dataset")

    tab1, tab2, tab3 = st.tabs([
        "Upload CSV",
        "Coller les Donnees",
        "Saisie Manuelle"
    ])

    with tab1:
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            user_df = pd.read_csv(uploaded)
            st.success("Dataset uploade avec succes")
            st.dataframe(user_df.head())
            st.session_state.user_df = user_df
            if st.button("Analyser ce fichier"):
                st.rerun()

    with tab2:
        pasted = st.text_area(
            "Collez vos donnees CSV ici",
            height=250,
            placeholder="age,filiere,mgp\n20,Informatique,3-3.24\n22,Mathematiques,2.5-2.74"
        )
        if st.button("Charger les donnees collees"):
            if pasted.strip():
                user_df = pd.read_csv(StringIO(pasted), on_bad_lines='skip', quotechar='"')
                st.success("Dataset charge")
                st.dataframe(user_df.head())
                st.session_state.user_df = user_df
                st.rerun()

    with tab3:
        user_df = st.data_editor(
            pd.DataFrame(columns=EXPECTED_COLUMNS),
            num_rows="dynamic"
        )
        if st.button("Utiliser ces donnees"):
            if len(user_df) > 0:
                st.success("Dataset pret")
                st.session_state.user_df = user_df
                st.rerun()

st.markdown("---")
st.header("Analyses des Donnees")

df_to_show = st.session_state.user_df if st.session_state.user_df is not None else load_data()

if len(df_to_show) > 0:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    
    if st.session_state.user_df is not None:
        st.subheader("Analyses de vos donnees")
        if st.button("Retour aux donnees globales"):
            st.session_state.user_df = None
            st.rerun()
    else:
        st.subheader("Analyses des donnees des etudiants")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Participants", len(df_to_show))
    if "stress" in df_to_show.columns:
        m2.metric("Stress Moyen", round(pd.to_numeric(df_to_show["stress"], errors='coerce').mean(), 1))
    if "presence" in df_to_show.columns:
        m3.metric("Presence Moyenne", f"{round(pd.to_numeric(df_to_show['presence'], errors='coerce').mean(), 1)}%")
    if "heures_etude" in df_to_show.columns:
        m4.metric("Etude (h/sem)", round(pd.to_numeric(df_to_show["heures_etude"], errors='coerce').mean(), 1))
    
    if "stress" in df_to_show.columns:
        df_to_show["stress"] = pd.to_numeric(df_to_show["stress"], errors='coerce')
        mean_filiere = df_to_show.groupby("filiere")["stress"].mean()
        if not mean_filiere.empty:
            st.error(f"Filiere la plus stressante : {mean_filiere.idxmax()}")
    
    g1, g2 = st.columns(2)
    
    with g1:
        if "mgp" in df_to_show.columns and "sexe" in df_to_show.columns:
            fig1 = px.histogram(df_to_show, x="mgp", color="sexe", barmode="group", title="Repartition de la MGP par Sexe", category_orders={"mgp": MGP_LIST})
            st.plotly_chart(fig1, use_container_width=True)

        if "mgp" in df_to_show.columns and "sommeil" in df_to_show.columns:
            fig2 = px.box(df_to_show, x="mgp", y="sommeil", title="Impact du Sommeil sur la MGP", category_orders={"mgp": MGP_LIST})
            st.plotly_chart(fig2, use_container_width=True)
        
        if "pc" in df_to_show.columns and "mgp" in df_to_show.columns:
            fig3 = px.violin(df_to_show, x="pc", y="mgp", color="pc", title="Impact de la possession d'un PC sur la MGP", category_orders={"mgp": MGP_LIST})
            st.plotly_chart(fig3, use_container_width=True)

    with g2:
        if "connexion" in df_to_show.columns and "mgp" in df_to_show.columns:
            fig4 = px.sunburst(df_to_show.dropna(subset=['connexion', 'mgp']), path=['connexion', 'mgp'], title="Lien entre Connexion Internet et MGP")
            st.plotly_chart(fig4, use_container_width=True)

        if "filiere" in df_to_show.columns and "stress" in df_to_show.columns:
            avg_stress = df_to_show.dropna(subset=["stress"]).groupby("filiere")["stress"].mean().reset_index()
            fig5 = px.bar(avg_stress, x="filiere", y="stress", title="Niveau de Stress Moyen par Filiere", color="stress")
            st.plotly_chart(fig5, use_container_width=True)

        if "transport" in df_to_show.columns and "presence" in df_to_show.columns and "mgp" in df_to_show.columns:
            fig6 = px.scatter(df_to_show, x="transport", y="presence", color="mgp", size="heures_etude" if "heures_etude" in df_to_show.columns else None, title="Transport, Presence et Performance")
            st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Matrice de Correlation des Facteurs Academiques")
    
    numeric_columns = []
    correlation_data = df_to_show.copy()
    
    if "mgp" in correlation_data.columns:
        mgp_mapping = {
            "1-1.49": 1.25, "1.5-1.99": 1.75, "2-2.24": 2.12, 
            "2.25-2.49": 2.37, "2.5-2.74": 2.62, "2.75-2.99": 2.87,
            "3-3.24": 3.12, "3.25-3.74": 3.50, "3.75-4": 3.88
        }
        correlation_data["mgp_numeric"] = correlation_data["mgp"].map(mgp_mapping)
        numeric_columns.append("mgp_numeric")
    
    numeric_mapping = {
        "heures_etude": "heures_etude",
        "sommeil": "sommeil", 
        "stress": "stress",
        "presence": "presence",
        "transport": "transport",
        "age": "age"
    }
    
    for col, new_name in numeric_mapping.items():
        if col in correlation_data.columns:
            correlation_data[new_name] = pd.to_numeric(correlation_data[col], errors='coerce')
            if new_name not in numeric_columns:
                numeric_columns.append(new_name)
    
    if len(numeric_columns) >= 2:
        corr_matrix = correlation_data[numeric_columns].corr()
        
        fig_heatmap = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlation entre les Facteurs Academiques",
            labels=dict(color="Correlation")
        )
        
        fig_heatmap.update_layout(height=500, font=dict(size=12))
        fig_heatmap.update_traces(texttemplate='%{z:.2f}', textfont=dict(size=10))
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.info("Interpretation: rouge = forte correlation positive, bleu = forte correlation negative")
        
        st.subheader("Correlations Fortes")
        col1, col2 = st.columns(2)
        
        corr_unstacked = corr_matrix.unstack()
        corr_unstacked = corr_unstacked[corr_unstacked < 1]
        strongest_pos = corr_unstacked.nlargest(5)
        strongest_neg = corr_unstacked.nsmallest(5)
        
        with col1:
            st.markdown("Fortes correlations positives:")
            for idx, val in strongest_pos.items():
                if val > 0.3:
                    st.write(f"- {idx[0]} / {idx[1]}: {val:.2f}")
        
        with col2:
            st.markdown("Fortes correlations negatives:")
            for idx, val in strongest_neg.items():
                if val < -0.3:
                    st.write(f"- {idx[0]} / {idx[1]}: {val:.2f}")
    else:
        st.warning("Pas assez de donnees numeriques pour creer la matrice de correlation")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Aucune donnee disponible. Les premieres donnees apparaitront ici apres le premier questionnaire.")