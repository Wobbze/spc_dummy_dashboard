
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from urllib.parse import quote, unquote

from functions import CONFIG
from utils import apply_spc_rules, get_rule_names_for_index

# --- Page Setup ---
st.set_page_config(page_title="Route Dashboard (Demo)", layout="wide")

# --- Dummy Data Generation ---
@st.cache_data(ttl=600)
def load_dummy_data():
    np.random.seed(42)
    programs = ["Program A", "Program B", "Program C"]
    variables = ["Temperature", "Pressure", "Speed"]
    installations = ["Plant X", "Plant Y", "Plant Z"]
    years = [2023, 2024]
    weeks = list(range(1, 53))

    data = []
    for prog in programs:
        for var in variables:
            for inst in installations:
                for year in years:
                    for week in weeks:
                        value = np.random.normal(loc=100, scale=10)
                        data.append({
                            "prog": prog,
                            "variable": var,
                            "id_install": inst,
                            "value": value,
                            "year": year,
                            "week": week
                        })

    return pd.DataFrame(data)

def wrap_text(text, width=30):
    return '<br>'.join([text[i:i+width] for i in range(0, len(text), width)])

# --- Load and Validate Data ---
data = load_dummy_data()
required_columns = ['prog', 'variable', 'id_install', 'value', 'year', 'week']
for col in required_columns:
    if col not in data.columns:
        st.error(f"Data is missing the required column: {col}")
        st.stop()

# --- Sidebar Program Selection ---
data['prog'] = data['prog'].astype(str).str.strip()
desired_prog_order = sorted(data['prog'].unique().tolist())
query_params = st.query_params
default_prog = query_params.get("prog", desired_prog_order[0])
selected_prog = st.sidebar.selectbox("Select Program", desired_prog_order, index=desired_prog_order.index(default_prog))

# --- Sidebar Variable & Installation Selection ---
filtered_data = data[data['prog'] == selected_prog]
available_vars = sorted(filtered_data['variable'].unique())
selected_var = st.sidebar.selectbox("Select Variable", available_vars)

available_inst = sorted(filtered_data['id_install'].unique())
selected_inst = st.sidebar.selectbox("Select Installation", available_inst)

# --- Filter Final Dataset ---
plot_data = filtered_data[
    (filtered_data["variable"] == selected_var) & 
    (filtered_data["id_install"] == selected_inst)
]

# --- Group and Plot ---
plot_data = plot_data.sort_values(by=["year", "week"])
plot_data["x"] = plot_data["year"].astype(str) + "-W" + plot_data["week"].astype(str).str.zfill(2)

# Apply SPC rules
plot_data = apply_spc_rules(plot_data, col="value", config=CONFIG.get(selected_var, {}))

# SPC Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=plot_data["x"], y=plot_data["value"], mode="lines+markers", name="Value"))
fig.update_layout(title=f"SPC Chart for {selected_var} @ {selected_inst}", xaxis_title="Week", yaxis_title="Value")

st.plotly_chart(fig, use_container_width=True)
