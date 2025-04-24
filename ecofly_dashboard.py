import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config("EcoFly Dashboard", layout="wide")
logo = Image.open("ecofly_logo.png")

# --------------------------
# Investment + Calculation Logic
# --------------------------
investments = {
    "Baseline (No Innovation)": 0,
    "Scenario 1 – Drop-in SAF": 250,
    "Scenario 2 – Green Hydrogen": 400,
    "Scenario 3 – Battery Electric": 350,
    "Scenario 4 – Innovation (TBD)": 300
}

def calculate_emissions(investment, year):
    base = 100
    reduction = (investment / 1000) * ((year - 2026) / (2050 - 2026))
    return round(base * (1 - reduction), 2)

def calculate_waste(investment, year):
    base = 1000
    reduction = (investment / 1000) * ((year - 2026) / (2050 - 2026))
    return round(base * (1 - reduction), 0)

def calculate_trl(investment, year):
    if investment == 0: return 6
    progress = ((year - 2026) / (2050 - 2026)) * (investment / 1000)
    return min(9, round(6 + 3 * progress))

def calculate_financials(investment, year):
    return (
        round(2000 + (year - 2030) * 150),
        round(300 + (year - 2030) * 50),
        round(500 + (year - 2030) * 60)
    )

# --------------------------
# Sidebar Navigation
# --------------------------
menu = st.sidebar.selectbox(
    "Select Section",
    ["Home", "Fleet Information", "Economic Assumptions", "Scenario Configuration", "Scenario Comparison"]
)

# --------------------------
# HOME PAGE
# --------------------------
if menu == "Home":
    st.markdown("""
    # Welcome to the EcoFly Sustainability & Innovation Dashboard """)

    st.info("""
    This dashboard supports strategic decision-making for EcoFly’s environmental and financial goals through:

    - Fleet & baseline context  
    - Economic assumptions for forecasting  
    - Scenario-specific KPI analysis  
    - Side-by-side performance comparison

    Use the sidebar on the left to explore the sections.
    """)

    st.image(logo, use_container_width=True)

    st.info("""
    ## COL 4, Group 3
    - **Sil Jonker**, 500927601  
    - **Lotte den Braver**, 500926192  
    - **Katja Skulj**, 500930355  
    - **Xander Meuris**, 500921909  
    - **Eva Bhagwandien**, 500924545  
    - **Terry Lazonder**, 500834811
    """)



# --------------------------
# SCENARIO CONFIGURATION
# --------------------------
elif menu == "Scenario Configuration":
    st.header("Scenario Configuration & KPIs")
    scenario = st.selectbox("Choose a scenario:", list(investments.keys()))
    year_range = st.slider("Select Snapshot Year Range", 2030, 2050, (2030, 2050), step=10)

    investment = investments[scenario]
    latest_year = year_range[1]

    revenue, profit, cashflow = calculate_financials(investment, latest_year)
    emissions = calculate_emissions(investment, latest_year)
    waste = calculate_waste(investment, latest_year)
    trl = calculate_trl(investment, latest_year)

    cols = st.columns(6)
    cols[0].metric("Revenue ($M)", f"${revenue}")
    cols[1].metric("Profit ($M)", f"${profit}")
    cols[2].metric("Cashflow ($M)", f"${cashflow}")
    cols[3].metric("Emissions (Mt CO₂)", f"{emissions}")
    cols[4].metric("Waste (tons)", f"{waste}")
    cols[5].metric("TRL", f"{trl}/9")

    # Plotly Line Chart
    st.subheader("Emissions Trend")
    years = list(range(year_range[0], year_range[1] + 1, 10))
    trend_data = [calculate_emissions(investment, y) for y in years]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=trend_data, mode='lines+markers', name=scenario))
    fig.update_layout(title="Projected Emissions (Mt CO₂)", xaxis_title="Year", yaxis_title="Emissions")
    st.plotly_chart(fig, use_container_width=True)

# --------------------------
# SCENARIO COMPARISON
# --------------------------
elif menu == "Scenario Comparison":
    st.header("Scenario Comparison – KPIs in 2050")
    data = []
    for scen, inv in investments.items():
        e = calculate_emissions(inv, 2050)
        w = calculate_waste(inv, 2050)
        t = calculate_trl(inv, 2050)
        r, p, _ = calculate_financials(inv, 2050)
        data.append({
            "Scenario": scen,
            "Emissions (Mt CO₂)": e,
            "Waste (tons)": w,
            "TRL": t,
            "Revenue ($M)": r,
            "Profit ($M)": p
        })

    df = pd.DataFrame(data)

    with st.expander("📊 Click to view full KPI comparison table (2050)"):
        st.dataframe(df.set_index("Scenario"))

    fig2 = px.bar(df, x="Emissions (Mt CO₂)", y="Scenario", orientation='h', title="2050 Emissions by Scenario")
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------
# FLEET + ECONOMICS (geen verandering nodig)
# --------------------------
elif menu == "Fleet Information":
    st.header("Fleet Information")
    st.info("""
**EcoFly**, a Dutch leisure airline, began operations in **FY24/25** from Lelystad Airport with:
- **6 Airbus A350-900** (long-haul)
- **15 Boeing 737-800** (short-haul)

By **FY26/27**, the fleet expands to:
- **8 A350s** and **20 B737s**
""")

elif menu == "Economic Assumptions":
    st.header("Economic & Financial Assumptions")

    st.info("""
    ### Key Inputs

    - **Interest Rate (Corporate Loans)**: 3.5% per annum  
    - **Inflation Rate (Industrial Goods)**: 1.5% per annum  
    - **Passenger & Cargo Growth**: Based on IATA/ICAO long-term forecasts
    """)

