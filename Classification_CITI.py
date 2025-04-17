import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import os 
st.set_page_config(page_title="Classification CITI", layout="wide")


# Chargement du logo (remplacez par le chemin réel si nécessaire)
logo_path = "Capture.png"  # Placez votre logo dans le même dossier que ce script
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    st.image(image, width=150)

# 🧠 Fonctions de traitement
def extract_citi_levels(code):
    code_str = str(code)
    if len(code_str) < 2:
        return None, None, None
    division = code_str[:2]
    group = code_str[:3] if len(code_str) >= 3 else None
    section = get_section(division)
    return section, division, group

def get_section(division_code):
    try:
        code = int(division_code)
    except:
        return None
    if 1 <= code <= 3:
        return "A"
    elif 5 <= code <= 39:
        return "B"
    elif 41 <= code <= 43:
        return "F"
    elif 45 <= code <= 47:
        return "G"
    elif 49 <= code <= 53:
        return "H"
    elif 55 <= code <= 56:
        return "I"
    elif 58 <= code <= 63:
        return "J"
    elif 64 <= code <= 66:
        return "K"
    elif 68 <= code <= 68:
        return "L"
    elif 69 <= code <= 75:
        return "M"
    elif 77 <= code <= 82:
        return "N"
    elif 84 <= code <= 84:
        return "O"
    elif 85 <= code <= 85:
        return "P"
    elif 86 <= code <= 88:
        return "Q"
    elif 90 <= code <= 93:
        return "R"
    elif 94 <= code <= 96:
        return "S"
    elif 97 <= code <= 98:
        return "T"
    elif 99 <= code <= 99:
        return "U"
    else:
        return None

def process_row(row, a_cols, p_cols):
    data = []
    for a_col, p_col in zip(a_cols, p_cols):
        code = row[a_col]
        try:
            poids = float(row[p_col])
        except:
            poids = 0
        if pd.notna(code) and poids > 0:
            section, division, group = extract_citi_levels(code)
            data.append({
                'code': code,
                'poids': poids,
                'group': group,
                'division': division,
                'section': section
            })
    if not data:
        return None, None

    df = pd.DataFrame(data)
    section_max = df.groupby('section')['poids'].sum().idxmax()
    df_section = df[df['section'] == section_max]
    division_max = df_section.groupby('division')['poids'].sum().idxmax()
    df_div = df_section[df_section['division'] == division_max]
    group_max = df_div.groupby('group')['poids'].sum().idxmax()
    df_group = df_div[df_div['group'] == group_max]
    code_principal = df_group.sort_values('poids', ascending=False)['code'].iloc[0]
    secondaires = df[df['code'] != code_principal]['code'].tolist()
    return code_principal, secondaires

# 🖥️ Interface principale
st.title("📊 Application de Classification CITI des Entreprises")

file_type = st.selectbox("📁 Type de fichier à importer", ["Excel (.xlsx)", "CSV (.csv)"])
uploaded_file = st.file_uploader("Importer le fichier de données", type=["xlsx", "csv"])

if uploaded_file:
    if file_type == "Excel (.xlsx)":
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success("✅ Fichier chargé avec succès")

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📄 Données importées", "🔍 Résultats CITI", "⬇️ Export Excel"])

    with tab1:
        st.subheader("Aperçu des données importées")
        st.dataframe(df.head())

    # Identification des colonnes d’activités et poids
    activity_cols = [col for col in df.columns if col.startswith("A")]
    poids_cols = [col for col in df.columns if col.startswith("P")]

    result = []
    for i, row in df.iterrows():
        principal, secondaires = process_row(row, activity_cols, poids_cols)
        row_result = {
            "Nom entreprise": row["Nom entreprise"],
            "Sigle": row["Sigle"],
            "APE": principal
        }
        for j, sec in enumerate(secondaires):
            row_result[f"AS{j+1}"] = sec
        result.append(row_result)

    df_result = pd.DataFrame(result)

    with tab2:
        st.subheader("Résultats de classification CITI")
        st.dataframe(df_result)

    with tab3:
        st.subheader("Téléchargement des résultats")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Données originales")
            df_result.to_excel(writer, index=False, sheet_name="Résultats CITI")
        output.seek(0)

        st.download_button("📥 Télécharger le fichier Excel complet",
                           data=output,
                           file_name="resultats_CITI.xlsx")
