import streamlit as st 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import numpy as np

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config("EcoFly Dashboard", layout="wide")
logo = Image.open("ecofly_logo.png")

# --------------------------
# Number formatting helper
# --------------------------
def format_number(n, unit=""):
    if isinstance(n, str):  # bijvoorbeeld "-"
        return n

    try:
        abs_n = abs(n)
        if abs_n >= 1e9:
            return f"{n / 1e9:.1f} B{unit}"  # miljard
        elif abs_n >= 1e6:
            return f"{n / 1e6:.1f} M{unit}"  # miljoen
        elif abs_n >= 1e3:
            return f"{n / 1e3:.0f} K{unit}"  # duizend
        elif abs_n == int(abs_n):
            return f"{int(n)}{unit}"
        else:
            return f"{n:.2f}{unit}"
    except:
        return str(n)  # fallback als n niet numeriek is



# --------------------------
# Investment + Calculation Logic
# --------------------------
investments = {
    "Baseline (No Innovation)": 0,
    "Scenario 1 – Drop-in SAF": 250,
    "Scenario 2 – Green Hydrogen": 400,
    "Scenario 3 – Battery Electric": 350,
    "Scenario 4 – Train for SH flights": 300,   # Updated scenario
}
train_kpis = {
    2030: {"Revenue": 1003000000, "Profit": 93000000, "Cashflow": -144000000, "Waste": 161987703, "CO2": 815461, "TRL": 9},
    2040: {"Revenue": 1014000000, "Profit": 70000000, "Cashflow": 47000000, "Waste": 168791186, "CO2": 730146, "TRL": 9},
    2050: {"Revenue": 1025000000, "Profit": 238000000, "Cashflow": 41000000, "Waste": 175880416, "CO2": 645831, "TRL": 9}
}

saf_kpis = {
    2030: {"Revenue": 814102792, "Profit": 261921948, "Cashflow": 170760538, "Waste": 161987703, "CO2": 720635, "TRL": 9},
    2040: {"Revenue": 870884190, "Profit": 244412043, "Cashflow": 112405480, "Waste": 168791186, "CO2": 540476, "TRL": 9},
    2050: {"Revenue": 916321626, "Profit": 216304917, "Cashflow": 55093729, "Waste": 175880416, "CO2": 459785, "TRL": 9}
}
eflight_kpis = {
    2030: {
        "Revenue": 1_131_483_298.91,
        "Profit": 249_046_359,
        "Cashflow": 249_046_350,
        "Waste": 163_328_532,
        "CO2": 900_775,
        "TRL": 9
    },
    2040: {
        "Revenue": 379_746_000,
        "Profit": -348_471_324,
        "Cashflow": -348_471_324,
        "Waste": 3_127_320,
        "CO2": 0,
        "TRL": 3
    },
    2050: {
        "Revenue": 462_908_255,
        "Profit": 65_690_931,
        "Cashflow": -173_869_558,
        "Waste": 3_127_320,
        "CO2": 0,
        "TRL": 1
    }
}


best_kpis = {
    2030: {
        "Revenue": 1030904820,
        "Profit": 51509579,
        "Cashflow": -267732230,
        "Waste": 161987703,
        "CO2": 653753,
        "TRL": 9
    },
    2040: {
        "Revenue": 1047903920,
        "Profit": 1457335,
        "Cashflow": -408336284,
        "Waste": 168791186,
        "CO2": 442859,
        "TRL": 9
    },
    2050: {
        "Revenue": 1074234280,
        "Profit": 198831371,
        "Cashflow": 302465099,
        "Waste": 175880416,
        "CO2": 268093,
        "TRL": 9
    }
}

h2_kpis = {
    2025: {
        "Revenue": 993355902,
        "Profit": 147079247,
        "Cashflow": 147079247,
        "Waste": 155458448,  # ← from your new waste list
        "CO2": 900775,
        "TRL": 5
    },
    2030: {
        "Revenue": 930371089,
        "Profit": -339602725,
        "Cashflow": 540429564,
        "Waste": 161987703,  # ← updated
        "CO2": 846583,
        "TRL": 5
    },
    2040: {
        "Revenue": 1022918520,
        "Profit": -216342744,
        "Cashflow": 1700833067,
        "Waste": 168791186,  # ← updated
        "CO2": 720135,
        "TRL": 6
    },
    2050: {
        "Revenue": 1046588625,
        "Profit": 470020020,
        "Cashflow": 5057688490,
        "Waste": 175880416,  # ← updated
        "CO2": 575623,
        "TRL": 6
    }
}

baseline_kpis = {
    2030: {
        "Revenue": 1131483298.91,
        "Profit": 249046359,
        "Cashflow": 249046350,
        "Waste": 163328532,
        "CO2": 900775,
        "TRL": 9
    },
    2040: {
        "Revenue": 1173365667.52,
        "Profit": 259721960.62,
        "Cashflow": 2798225761,
        "Waste": 171932393,
        "CO2": 945814,
        "TRL": 9
    },
    2050: {
        "Revenue": 1247033426.61,
        "Profit": 272730401.73,
        "Cashflow": 5466991792,
        "Waste": 188960715,
        "CO2": 993105,
        "TRL": 9
    }
}



def get_kpi(scenario, year, investment):
    if scenario == "Scenario 4 – Train for SH flights" and year in train_kpis:
        data = train_kpis[year]
    elif scenario == "Scenario 1 – Drop-in SAF" and year in saf_kpis:
        data = saf_kpis[year]
    elif scenario == "Scenario 3 – Battery Electric" and year in eflight_kpis:
        data = eflight_kpis[year]
    elif scenario == "Best Scenario – Hybrid" and year in best_kpis:
        data = best_kpis[year]
    elif scenario == "Scenario 2 – Green Hydrogen" and year in h2_kpis:
        data = h2_kpis[year]
    elif scenario == "Baseline (No Innovation)" and year in baseline_kpis:  # 👈 Add this line
        data = baseline_kpis[year]
    else:
        return "-", "-", "-", "-", "-", "-"

    return (
        data["Revenue"],
        data["Profit"],
        data["Cashflow"],
        data["Waste"],
        data["CO2"],
        data["TRL"]
    )


# --------------------------
# Sidebar Navigation
# --------------------------
menu = st.sidebar.selectbox(
    "Select Section",
    ["Home", "Fleet Information", "Key Assumptions", "Scenario Configuration", "Scenario Comparison", "Best Scenario🏆"]
)

# --------------------------
# HOME PAGE
# --------------------------
if menu == "Home":
    st.markdown("""
    # Welcome to the EcoFly Sustainability & Innovation Dashboard 
    """)

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
    - *Sil Jonker*, 500927601  
    - *Lotte den Braver*, 500926192  
    - *Katja Skulj*, 500930355  
    - *Xander Meuris*, 500921909  
    - *Eva Bhagwandien*, 500924545  
    - *Terry Lazonder*, 500834811
    """)

# --------------------------
# FLEET INFORMATION
# --------------------------
elif menu == "Fleet Information":
    st.header("Fleet Information")
    st.info("""
*EcoFly*, a Dutch leisure airline, began operations in **FY24/25** from Lelystad Airport with:  

- 6 *Airbus A350-900* (long-haul)  
- 15 *Boeing 737-800* (short-haul)  

By **FY26/27**, the fleet expands to:  
- 8 *A350s* and 20 *B737s*  

---

***Future fleet & innovations we will explore***

To prepare for a sustainable aviation future, EcoFly is actively exploring various **technological and operational innovations** that could be integrated into its evolving fleet and route network. These innovations will be assessed for feasibility, impact, and alignment with EcoFly’s business goals.

The innovations we will include in our analysis are:

- **Sustainable Aviation Fuel (SAF)** – drop-in biofuel alternatives for existing engines  
- **Battery-electric aircraft** – for short-range, low-emission operations  
- **Green hydrogen** – a long-term option for clean propulsion  
- **High-speed train substitution** – as an alternative to short-haul (SH) flights

Each option will be evaluated based on key performance indicators (KPIs) such as emissions, profitability, technology readiness (TRL), and operational compatibility.

Through scenario modeling, we aim to determine which innovation—or combination—is the most effective and realistic pathway for EcoFly’s growth and decarbonization.
""")

elif menu == "Best Scenario🏆":
    st.header("SAF + Train Hybrid Strategy")

    selected_year = st.select_slider("Select Snapshot Year", options=[2030, 2040, 2050], value=2030)
    scenario = "Best Scenario – Hybrid"

    revenue, profit, cashflow, waste, emissions, trl = get_kpi(scenario, selected_year, 0)

    cols = st.columns(6)
    cols[0].metric("Revenue", f"€{format_number(revenue)}" if revenue != "-" else "-")
    cols[1].metric("Profit", f"€{format_number(profit)}")
    cols[2].metric("Cashflow", f"€{format_number(cashflow)}")
    cols[3].metric("Emissions (ton)", f"{format_number(emissions)} CO₂")
    cols[4].metric("Waste", f"{format_number(waste, ' ton')}")
    cols[5].metric("TRL", f"{trl}/9")

    st.subheader("Hybrid Emissions Trend")
    years = [2030, 2040, 2050]
    trend = [best_kpis[y]["CO2"] for y in years]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=trend, mode='lines+markers', name="Hybrid Emissions"))
    fig.update_layout(title="Projected CO₂ Emissions", xaxis_title="Year", yaxis_title="ton CO₂")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
### EcoFly’s Hybrid Decarbonization Strategy – Train + SAF Integration

After carefully evaluating all four scenarios, EcoFly has concluded that a **hybrid strategy** is the only realistic and responsible way forward.  
This combined approach integrates **train substitution for short-haul (SH)** flights and **Sustainable Aviation Fuel (SAF)** for long-haul & short-haul flights.

---

### Why a Hybrid Strategy?

Fully replacing SH flights with trains would have required massive infrastructure investments and decades of construction.  
Going fully electric or only using SAF creates either **operational limitations** or **significant long-term fuel costs**.

After comparing all alternatives, only this hybrid strategy:
- Delivers meaningful emission reductions
- Remains financially viable and scalable
- Offers realistic infrastructure timelines

---

### What the Hybrid Model Looks Like by 2050:

- **75% of SH flights** are replaced with a high-speed train network  
- The remaining **25% of SH flights** use **SAF** (blended fuel)  
- **75% of LH flights** also operate on SAF blends  
- The transition is **not yet 100% carbon-free**, but it achieves substantial reductions and is aligned with EcoFly’s growth

---

### Phased Investment Plan 💸

To support this strategy, EcoFly commits to the following investment plan:

- **€1.0 billion in 2025** – secured via a bank loan  
- **€600 million in 2030** – secured via a bank loan
- **€500 million in 2040** – secured via a bank loan

This total is **lower** than the full train only strategy, because:
- We utilize **existing railway infrastructure** more efficiently  
- We avoid overcommitting to **new rail lines** that take decades to build  
- We redirect funding to accelerate **SAF adoption** where it has the most impact

---

### Supporting Sustainability Through Pricing 🎟

To help finance the transition, EcoFly added **small price adjustments** across the network between 2025 and 2050:

- **+€8** on short-haul (SH) flights  
- **+€15** on long-haul (LH) flights  
- **+€6** on train tickets  

These modest increases support sustainability investments without disrupting passenger demand reflecting our belief that customers will support climate-forward aviation.

---

### Strategic Outcome 🚀

EcoFly’s hybrid strategy:
- Balances **climate ambition** with **operational and financial feasibility**
- Achieves major **CO₂ reductions** across both SH and LH  
- Keeps us **profitable, flexible, and scalable** in a changing aviation landscape

This isn’t yet 100% carbon-free but it’s the **smartest and fastest route to realistic decarbonization** for EcoFly and our passengers.
    """)

# --------------------------
# ASSUMPTIONS
# --------------------------
elif menu == "Key Assumptions":
    st.header("Assumptions")
    st.info("""

#### 💰 Financial Assumptions
- **Cost of capital:** 3.5%  
- **Inflation (industrial goods):** 1.5%

#### ✈️ Growth Forecasts (2025–2041)
- **Passenger (PAX) growth forecast:** 4.2%  
- **Cargo growth forecast:** 4.5%

#### 🎟 Ticket Pricing
- **Train ticket price:** €100 (total)  
- **Short-haul (SH) ticket price:** €80/hour  
- **Long-haul (LH) ticket price:** €100/hour

#### 📊 Baseline Pax Volumes (starting FY25/26)
- **PAX SH (Short-Haul):** 180  
- **PAX LH (Long-Haul):** 300  
- **PAX Train:** 350
    """)

# --------------------------
# SCENARIO COMPARISON
# --------------------------
elif menu == "Scenario Comparison":
    st.header("Scenario Comparison – KPIs in 2050")
    data = []
    for scen, inv in investments.items():
        revenue, profit, cashflow, waste, emissions, trl = get_kpi(scen, 2050, inv)
        data.append({
    "Scenario": scen,
    "Emissions CO₂": emissions,  # numeric for plotting
    "Emissions(ton)": f"{format_number(emissions)} CO₂",  # pretty for display
    "Waste": format_number(waste, " ton"),
    "TRL": f"{trl}/9",
    "Revenue": f"€{format_number(revenue)}",
    "Profit": f"€{format_number(profit)}",
    "Cashflow": f"€{format_number(cashflow)}"
})


    df = pd.DataFrame(data)

    with st.expander("📊 Click to view full KPI comparison table (2050)"):
        st.dataframe(df.set_index("Scenario"))

    fig2 = px.bar(df, x="Emissions CO₂", y="Scenario", orientation='h', title="2050 Emissions by Scenario")
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------
# SCENARIO CONFIGURATION
# --------------------------
elif menu == "Scenario Configuration":
    st.header("Scenario Configuration & KPIs")
    scenario = st.selectbox("Choose a scenario:", list(investments.keys()))
    selected_year = st.select_slider("Select Snapshot Year", options=[2030, 2040, 2050], value=2030)
    investment = investments[scenario]

    revenue, profit, cashflow, waste, emissions, trl = get_kpi(scenario, selected_year, investment)

    cols = st.columns(6)
    cols[0].metric("Revenue", f"€{format_number(revenue)}")
    cols[1].metric("Profit", f"€{format_number(profit)}")
    cols[2].metric("Cashflow", f"€{format_number(cashflow)}")
    cols[3].metric("Emissions(ton)", f"{format_number(emissions)} CO₂")
    cols[4].metric("Waste", f"{format_number(waste)} ton")
    cols[5].metric("TRL", f"{trl}/9")
 
    st.subheader("Emissions Trend")
    if scenario != "Scenario 4 – Train for SH flights":
        years = [2030, 2040, 2050]
        trend_data = [get_kpi(scenario, y, investment)[4] for y in years]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=trend_data, mode='lines+markers', name="Emissions ton CO₂"))
    else:
        years_full = np.arange(2030, 2051)
        base_emissions = np.interp(
            years_full,
            [2030, 2040, 2050],
            [train_kpis[2030]["CO2"], train_kpis[2040]["CO2"], train_kpis[2050]["CO2"]]
        )
        summer_spike = 1 + 0.04 * np.sin(2 * np.pi * (years_full - 2030))
        emissions_with_spike = base_emissions * summer_spike
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_full, y=emissions_with_spike, mode='lines', name="Emissions ton CO₂"))
        fig.add_trace(go.Scatter(
            x=[2030, 2040, 2050],
            y=[train_kpis[2030]["CO2"], train_kpis[2040]["CO2"], train_kpis[2050]["CO2"]],
            mode='markers',
            marker=dict(size=10),
            name="KPI Points"
        ))

    fig.update_layout(title="Projected Emissions (ton CO₂)", xaxis_title="Year", yaxis_title="Emissions")
    st.plotly_chart(fig, use_container_width=True)
    # Scenario-specific explanatory texts
    if scenario == "Scenario 1 – Drop-in SAF":
        st.markdown("""
**Scenario Analysis: Drop-in Sustainable Aviation Fuel (SAF)**

Between *2030 and 2050*, EcoFly’s operations remain stable, with:
- **28,718 flights annually**
- A consistent fleet of *6 Airbus A350s* and *20 Boeing 737s*
- Total passenger volume of **4.53 million**

Despite operational stability, higher SAF usage in the *50%* and *70%* adoption scenarios leads to a **noticeable increase in fuel costs**.

**Financial Outlook:**
- **Passenger revenues** remain steady at around **€800-900 Million**.
- However, **operating profit** declines slightly over time as SAF-related expenses rise.

**Environmental Impact:**
- CO₂ emissions **decrease significantly** with greater SAF adoption, making it one of the most impactful sustainability levers available to EcoFly.
- The transition supports long-term climate goals and strengthens EcoFly’s reputation for greener aviation.

**Strategic Conclusion:**

Although SAF introduces **higher fuel costs**, it offers **substantial environmental benefits** with minimal disruption to existing operations or fleet.  
Drop-in SAF is a **promising, scalable, and realistic** solution for a sustainable future in aviation.
        """)
    elif scenario == "Scenario 2 – Green Hydrogen":
          st.markdown("""
**Hydrogen Drop-in & ZEROe Aircraft Transition**

Between *2025 and 2050*, EcoFly transitions toward **hydrogen-based operations** by gradually adopting hydrogen drop-in fuel and expanding its fleet with zero-emission aircraft.  
Throughout this shift, the long-haul fleet of *6 Airbus A350-900s* remains unchanged, continuing to serve intercontinental routes with kerosene and increasing shares of SAF.

- **2030**  
  EcoFly starts using a *15% hydrogen fuel blend* in its **17 Boeing 737-800** aircraft, while also introducing **3 hydrogen-powered Dash 8-300** aircraft for regional operations.

- **2040**  
  The transition accelerates:  
  - The 737 fleet is reduced to **9 aircraft**  
  - EcoFly adds **6 Airbus ZEROe Turboprops**, **3 ZEROe Jets**, and expands to **8 Dash 8-H2**  
  - Hydrogen fuel usage reaches **50%**, cutting CO₂ emissions significantly

- **2050**  
  All **Boeing 737s are retired**.  
  EcoFly’s short- and mid-haul network is now operated by:  
  - **8 Dash 8-H2**  
  - **8 ZEROe Turboprops**  
  - **10 ZEROe Jets**  
  All of which are powered by **hydrogen**.  
  *Long-haul flights continue with A350s running on 100% SAF where available.*

**Operational Scale:**
- EcoFly continues to serve **28 destinations**, with nearly **29,000 flights annually** and **4.5 million passengers**.

**Financial Outlook:**
- Despite increased hydrogen costs, **revenue remains around €930 million**
- **Profit remains positive throughout**, and investment risk is minimized due to phased aircraft replacement

**Environmental Impact:**
- By 2050, CO₂ emissions are reduced by **over 70%** compared to 2025  
- Hydrogen fuel and aircraft technologies evolve from **TRL 6 in 2025** to **TRL 9 by 2040**, reaching full maturity

**Strategic Summary:**
EcoFly’s hydrogen approach leverages a **stepwise rollout**, blending existing and future aircraft. This enables both **risk control** and **long-term climate alignment**, without needing full fleet replacement or unrealistic infrastructure changes by 2030.
    """)


    elif scenario == "Scenario 3 – Battery Electric":
        st.markdown("""
**Phased Evaluation of Battery Electric Flight**

One of the innovations explored by EcoFly is the use of **fully electric aircraft** for short-haul operations. While promising from a sustainability perspective, the approach presents serious **financial and operational limitations** that must be considered.

- *In 2030*, electric flight is not feasible — no viable electric aircraft exist for commercial passenger use.  
- *In 2040*, EcoFly introduces **20 electric aircraft** carrying 90 passengers, with a maximum range of *800 km*.  
- *In 2050*, **10 larger electric aircraft** are added, each with *150 seats* and a range of *1,500 km*.  
- A total investment of **€1.2 billion** is required in *2040* and *2050* to support development, acquisition, and charging infrastructure.

**Financial Impacts:**
- These investments lead to **negative cashflows** due to high capital costs and limited passenger capacity.  
- Revenue remains low compared to conventional aircraft, as fewer passengers can be transported per flight.  
- *Profit is first achieved in 2044*, but another major investment in 2050 pushes profit back into the negative.  
- Sustainable profitability is only reached by *2056*.

**Operational Limitations:**
- The limited range of electric aircraft means **not all destinations** in EcoFly’s short-haul network can be reached.  
- This **restricts route flexibility** and reduces competitive reach compared to existing SH aircraft.

**Strategic Conclusion:**

While battery electric flight supports EcoFly’s long-term sustainability goals, the technology is **not currently realistic** from a financial and operational standpoint.  
Other decarbonization strategies — such as train substitution or SAF integration — offer **faster returns**, **greater network compatibility**, and **lower risk**.

**Note:** These projections reflect expected industry capabilities and EcoFly's operational needs. Technology readiness may improve over time, but current forecasts do not support full-scale electric adoption within the timeframe.
        """)
    elif scenario == "Scenario 4 – Train for SH flights":
        st.markdown("""
**Phased Investment Strategy for SH Train Substitution**

A €1 billion investment is feasible several banks and institutions are open to financing large-scale, sustainable, and innovative aviation projects, provided if there is a solid business plan and strong partners.

- *Three major investments of €1 billion each* are made in 2025, 2030, and 2040. These investments focus on train station development, electric train procurement, and both the use of existing rail infrastructure and the creation of dedicated EcoFly train lines.
- *Transition timeline:*  
    - By *2030*, 25% of short-haul (SH) flights are replaced with electric trains.  
    - Between *2030 and 2040*, this increases to 50%.  
    - Between *2040 and 2050*, we reach 75% replacement.  
- Passenger growth is fully accommodated: expanded train capacity ensures total passenger numbers (pax) keep pace with forecasts.

**Network expansion & infrastructure:**
- We begin with routes up to *600 km*, making use of existing rails.
- As we invest further, dedicated rail lines will be built for EcoFly. When this infrastructure is complete, our network will expand to serve destinations up to *1,200 km*.

**Financially:**
- *Return on investment (ROI)* is achieved by 2040 after the second major investment.
- After the final investment, full profitable operation is expected by *2049*.

**Business Risk & Mitigation Strategy**
                    
Implementing trains instead of short-haul (SH) flights brings significant business risks including the potential loss of customers and revenue, operational complexity, and high upfront infrastructure costs.

To mitigate these risks, EcoFly is taking a phased and customer-centric approach:
- Offer seamless booking, guaranteed connections, and competitive travel times.  
- Launch strong marketing campaigns focused on comfort, reliability, and sustainability.  
- Upsell premium train classes and offer high-quality onboard services.  
- Partner with top-tier rail operators that have proven expertise and infrastructure.

To remain competitive during this transition, EcoFly will retain **25% of SH flights** throughout the transition period. This hybrid model allows customers time to adapt, maintains brand trust, and supports profitability while gradually introducing rail-based alternatives.

**Note:** Long-haul (LH) flights remain part of our operations. Emissions figures therefore reflect all emissions: SH flights, trains, and LH flights. Our own rail infrastructure is a future goal; until then, we use the existing network where possible.
        """)
