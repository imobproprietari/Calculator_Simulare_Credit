import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Simulatoare Credit Imobiliar", page_icon="🏠", layout="wide"
)

st.title("🏠 Simulator Interactiv Credit Imobiliar")
st.write(
    "Introdu datele creditului tău în panoul din stânga pentru a genera scadențarul și graficele de evoluție."
)

# Panou lateral pentru introducerea datelor (Sidebar)
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

# Calcul matematic
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

# Afișare metrici cheie
col1, col2, col3, col4 = st.columns(4)
col1.metric("Prima Rată", f"{df['Rata Totala'].iloc[0]:,.2f} RON")
col2.metric("Total Dobândă", f"{df['Dobanda'].sum():,.2f} RON")
col3.metric("Total de Plată", f"{df['Rata Totala'].sum():,.2f} RON")
col4.metric("Perioadă (Ani)", f"{perioada_luni / 12:.1f} ani")

st.markdown("---")

# Generare Grafic Matplotlib
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax1.plot(
    df["Luna"],
    df["Sold Ramas"],
    color="#1f77b4",
    linewidth=2.5,
    label="Sold Rămas",
)
ax1.fill_between(df["Luna"], df["Sold Ramas"], color="#1f77b4", alpha=0.15)
ax1.set_title("Evoluția Soldului Rămas", fontsize=11, fontweight="bold")
ax1.set_ylabel("RON")
ax1.grid(True, linestyle="--", alpha=0.5)

ax2.bar(
    df["Luna"],
    df["Principal"],
    color="#2ca02c",
    label="Principal (Capital)",
    width=1.0,
)
ax2.bar(
    df["Luna"],
    df["Dobanda"],
    bottom=df["Principal"],
    color="#d62728",
    label="Dobândă",
    width=1.0,
)
ax2.set_title(
    "Componența Lunară a Ratei (Principal vs. Dobândă)",
    fontsize=11,
    fontweight="bold",
)
ax2.set_xlabel("Luna din scadențar")
ax2.set_ylabel("RON / lună")
ax2.legend(loc="upper right")
ax2.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

# Tabel detaliat
with st.expander("📋 Vezi Scadențarul Detaliat Lună cu Lună"):
    st.dataframe(df.style.format("{:,.2f}"))
