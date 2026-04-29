import os
import pandas as pd
import streamlit as st
import plotly.express as px
from io import StringIO

st.set_page_config(
    page_title="UYI Data Analysis",
    page_icon="hat.png",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .hero-section {
        background: linear-gradient(rgba(31, 59, 115, 0.9), rgba(31, 59, 115, 0.6)), 
                    url('https://uy1.passresto.com/wp-content/uploads/2026/03/Image11-1024x676.png');
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
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data_uy1.csv"
EXPECTED_COLUMNS = [
    "age", "filiere", "niveau", "heures_etude", "connexion", 
    "pc", "transport", "sommeil", "mgp", "stress", "presence", "sexe"
]

FILIERES = [
    "Informatique", "Mathématiques", "Physique", "ICT4D", "Biologie", 
    "Chimie", "Ingenierie (ENSPY)", "Energies Renouvelables", "Histoire", 
    "Langues (Anglais/Allemand etc.)", "Geographie", "Philosophie", 
    "Psychologie", "Sociologie", "Biochimie"
]

MGP_LIST = ["1-1.49", "1.5-1.99", "2-2.24", "2.25-2.49", "2.5-2.74", "2.75-2.99", "3-3.24", "3.25-3.74", "3.75-4"]

def initialise_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        pd.DataFrame(columns=EXPECTED_COLUMNS).to_csv(DATA_FILE, index=False)

def load_data():
    initialise_data()
    return pd.read_csv(DATA_FILE)

def save_row(row):
    df = pd.DataFrame([row])
    df.to_csv(DATA_FILE, mode="a", header=False, index=False)

if 'user_df' not in st.session_state:
    st.session_state.user_df = None

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
    
    /* Your input styles here */
</style>
""", unsafe_allow_html=True)

if choice == "Questionnaire":
    st.subheader("Formulaire Academique")
    
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
            stress = st.slider("Niveau de stress (1-10)", 1, 10, 3)
            presence = st.slider("Taux de presence en cours (%)", 0, 100, 50)

        submit = st.form_submit_button("Enregistrer")

        if submit:
            save_row({
                "age": age, "filiere": filiere, "niveau": niveau, "heures_etude": heures_etude,
                "connexion": connexion, "pc": pc, "transport": transport, "sommeil": sommeil,
                "mgp": mgp, "stress": stress, "presence": presence, "sexe": sexe
            })
            st.success("Donnees enregistrees avec succes !")
            st.session_state.user_df = None
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
        
        st.info("Interpretation: rouge = forte correlation positive,  bleu = forte correlation negative")
        
        st.subheader("Correlations Fortes")
        col1, col2 = st.columns(2)
        
        corr_unstacked = corr_matrix.unstack()
        corr_unstacked = corr_unstacked[corr_unstacked < 1]
        strongest_pos = corr_unstacked.nlargest(3)
        strongest_neg = corr_unstacked.nsmallest(3)
        
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
    st.info("Aucune donnee disponible. Veuillez remplir le questionnaire ou importer des donnees.")