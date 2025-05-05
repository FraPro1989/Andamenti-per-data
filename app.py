import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Monitoraggio Prenotazioni PMS", layout="wide")
st.title("📊 Trasformazione dati PMS – Albergatore Pro")

st.subheader("1️⃣ Carica il file Excel esportato dal gestionale (PMS)")
uploaded_file = st.file_uploader("Carica file .xls o .xlsx", type=["xls", "xlsx"])

# Sinonimi per colonne da cercare
MAPPINGS = {
    "camere": ["Occupate", "Camere occupate", "Rooms", "Booked rooms"],
    "revenue": ["Room revenue", "Ricavi camere", "Camere ricavo"],
    "presenze": ["Presenze", "Guests", "Occupanti"],
    "occupazione": ["Occupazione %", "OCC%", "Tasso occupazione"],
    "f&b": ["F&B revenue", "Ristorante", "Ricavi F&B"],
    "totale_ricavi": ["Totale", "Rate revenue", "Revenue totale"],
}

def trova_colonna(df, possibili_nomi):
    for nome in possibili_nomi:
        for col in df.columns:
            if str(col).strip().lower() == nome.strip().lower():
                return col
    return None

if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file, sheet_name=0, skiprows=2)
        df_raw = df_raw.rename(columns={df_raw.columns[0]: "Data"})
        df_raw = df_raw[df_raw["Data"].notnull() & df_raw["Data"].astype(str).str.contains("/")]

        df_raw["Data"] = df_raw["Data"].str.extract(r"(\d{2}/\d{2}/\d{4})")
        df_raw["Data"] = pd.to_datetime(df_raw["Data"], format="%d/%m/%Y", errors="coerce")
        df_raw = df_raw.dropna(subset=["Data"])

        # Trova colonne con nomi flessibili
        col_camere = trova_colonna(df_raw, MAPPINGS['camere'])
        col_revenue = trova_colonna(df_raw, MAPPINGS['revenue'])
        col_fb = trova_colonna(df_raw, MAPPINGS['f&b'])
        col_totale = trova_colonna(df_raw, MAPPINGS['totale_ricavi'])
        col_presenze = trova_colonna(df_raw, MAPPINGS['presenze'])
        col_occ = trova_colonna(df_raw, MAPPINGS['occupazione'])

        df_finale = pd.DataFrame()
        df_finale["Data"] = df_raw["Data"]

        if col_camere:
            df_finale["Camere Occupate"] = pd.to_numeric(df_raw[col_camere], errors='coerce')
        else:
            st.warning("⚠️ Colonna 'camere occupate' non trovata.")

        if col_revenue:
            df_finale["Room Revenue"] = pd.to_numeric(df_raw[col_revenue], errors='coerce')
        if col_fb:
            df_finale["F&B Revenue"] = pd.to_numeric(df_raw[col_fb], errors='coerce')
        if col_totale:
            df_finale["Totale Ricavi"] = pd.to_numeric(df_raw[col_totale], errors='coerce')
        if col_presenze:
            df_finale["Presenze"] = pd.to_numeric(df_raw[col_presenze], errors='coerce')
        if col_occ:
            df_finale["Occupazione %"] = pd.to_numeric(df_raw[col_occ], errors='coerce')

        # Calcolo KPI se dati sufficienti
        if "Room Revenue" in df_finale.columns and "Camere Occupate" in df_finale.columns:
            df_finale["RevPAR"] = df_finale["Room Revenue"] / 30
            df_finale["RMC"] = df_finale["Room Revenue"] / df_finale["Camere Occupate"].replace(0, pd.NA)

        st.success("✅ Dati elaborati con successo!")
        st.dataframe(df_finale)

        if "Room Revenue" in df_finale.columns:
            st.subheader("📈 Andamento Room Revenue")
            st.line_chart(df_finale.set_index("Data")["Room Revenue"])

    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
