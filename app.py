
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(
    page_title="Simulatoare Credit Imobiliar Interactiv",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Simulator Interactiv Credit Imobiliar")
st.write(
    "Mută cursorul peste grafice pentru a vedea detaliile exacte (sold, principal, dobândă) pentru fiecare lună în parte."
)

# Panou lateral pentru parametri
st.sidebar.header("⚙️ Parametri Credit")
suma_credit = st.sidebar.number_input(
    "Suma împrumutată (RON):", min_value=10000, value=797096, step=5000
)
rata_dobanda_anuala = st.sidebar.number_input(
    "Rată dobândă anuală (%):", min_value=0.1, value=4.75, step=0.1, format="%.2f"
)
perioada_luni = st.sidebar.number_input(
    "Perioada creditului (luni):", min_value=12, value=252, step=12
)
tip_rambursare = st.sidebar.selectbox(
    "Tip rambursare:",
    options=["Rate Egale (Anuități)", "Rate Descrescătoare"],
    index=0,
)

# Calcul scadențar
dobanda_lunara = (rata_dobanda_anuala / 100) / 12
sold_ramas = suma_credit
istoric_luni, istoric_sold, istoric_principal, istoric_dobanda, (
    istoric_rata_totala
) = ([], [], [], [], [])

if tip_rambursare == "Rate Egale (Anuități)":
    if dobanda_lunara > 0:
        rata_fixa = suma_credit * (
            (dobanda_lunara * (1 + dobanda_lunara) ** perioada_luni)
            / ((1 + dobanda_lunara) ** perioada_luni - 1)
        )
    else:
        rata_fixa = suma_credit / perioada_luni

for luna in range(1, perioada_luni + 1):
    dobanda_luna = sold_ramas * dobanda_lunara
    if tip_rambursare == "Rate Egale (Anuități)":
        principal_luna = rata_fixa - dobanda_luna
        rata_totala = rata_fixa
    else:
        principal_luna = suma_credit / perioada_luni
        rata_totala = principal_luna + dobanda_luna

    if sold_ramas < principal_luna:
        principal_luna = sold_ramas
        rata_totala = principal_luna + dobanda_luna

    sold_ramas -= principal_luna
    istoric_luni.append(luna)
    istoric_sold.append(max(0, sold_ramas))
    istoric_principal.append(principal_luna)
    istoric_dobanda.append(dobanda_luna)
    istoric_rata_totala.append(rata_totala)

df = pd.DataFrame(
    {
        "Luna": istoric_luni,
        "Rata Totala": istoric_rata_totala,
        "Principal": istoric_principal,
        "Dobanda": istoric_dobanda,
        "Sold Ramas": istoric_sold,
    }
)

# Metrici cheie
col1, col2, col3, col4 = st.columns(4)
col1.metric("Prima Rată", f"{df['Rata Totala'].iloc[0]:,.2f} RON")
col2.metric("Total Dobândă", f"{df['Dobanda'].sum():,.2f} RON")
col3.metric("Total de Plată", f"{df['Rata Totala'].sum():,.2f} RON")
col4.metric("Perioadă (Ani)", f"{perioada_luni / 12:.1f} ani")

st.markdown("---")

# ==========================================
# CREARE GRAFIC INTERACTIV CU PLOTLY
# ==========================================
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    subplot_titles=(
        "Evoluția Soldului Rămas",
        "Componența Lunară a Ratei (Principal vs. Dobândă)",
    ),
)

# Grafic 1: Evoluție Sold Rămas
fig.add_trace(
    go.Scatter(
        x=df["Luna"],
        y=df["Sold Ramas"],
        mode="lines",
        name="Sold Rămas",
        line=dict(color="#1f77b4", width=3),
        hovertemplate="""**Luna %{x}**
