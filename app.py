import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Dashboard Prenotazioni", layout="wide")
st.title("📊 Dashboard Prenotazioni – Albergatore Pro")

st.subheader("1️⃣ Incolla qui i dati (copiati da Excel come tabella):")
text_data = st.text_area("Incolla i dati qui", height=300)

if text_data:
    try:
        df = pd.read_csv(StringIO(text_data), sep='\t')  # usa '\t' per dati copiati da Excel
        st.success("✅ Dati caricati correttamente!")
        st.dataframe(df)

        st.subheader("📈 Esempio: andamento camere vendute (2025)")
        if "2025" in df.columns:
            df["Data"] = pd.to_datetime(df[df.columns[0]], errors='coerce')
            df = df.dropna(subset=["Data"])
            df_sorted = df.sort_values("Data")
            st.line_chart(df_sorted.set_index("Data")["2025"])
        else:
            st.warning("Colonna '2025' non trovata nei dati.")
    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
