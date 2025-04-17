import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
                        usl = 120
                        lsl = 80
                        data.append({
                            "prog": prog,
                            "variable": var,
                            "id_install": inst,
                            "value": value,
                            "usl": usl,
                            "lsl": lsl,
                            "year": year,
                            "week": week
                        })

    return pd.DataFrame(data)

# --- Load Data ---
df = load_dummy_data()

# --- Sidebar Filters ---
st.sidebar.title("Filter Options")
selected_prog = st.sidebar.selectbox("Program", sorted(df["prog"].unique()))
selected_var = st.sidebar.selectbox("Variable", sorted(df["variable"].unique()))
selected_inst = st.sidebar.selectbox("Installation", sorted(df["id_install"].unique()))

# --- Filter Data ---
filtered = df[
    (df["prog"] == selected_prog) &
    (df["variable"] == selected_var) &
    (df["id_install"] == selected_inst)
].copy()

# --- Sort and Prepare X Axis ---
filtered = filtered.sort_values(by=["year", "week"])
filtered["x"] = filtered["year"].astype(str) + "-W" + filtered["week"].astype(str).str.zfill(2)

# --- Apply SPC Rules ---
spc_result = apply_spc_rules(filtered["value"], usl=filtered["usl"], lsl=filtered["lsl"])
filtered["Violation"] = spc_result["violation_flags"]

# Add rule flags as columns
rule_names = ["Rule 1", "Rule 2", "Rule 3", "Rule 4", "Rule 5", "Rule 5b", "Rule 7", "Rule 8"]
if len(spc_result["flags"]) > len(rule_names):
    rule_names.append("Rule 11")
for name, flag_array in zip(rule_names, spc_result["flags"]):
    filtered[name] = flag_array

# --- Plotting ---
fig = go.Figure()

# Plot measured values
fig.add_trace(go.Scatter(
    x=filtered["x"],
    y=filtered["value"],
    mode="lines+markers",
    name="Value"
))

# Highlight violations per rule
for name in rule_names:
    points = filtered[filtered[name]]
    if not points.empty:
        fig.add_trace(go.Scatter(
            x=points["x"],
            y=points["value"],
            mode="markers",
            name=f"⚠ {name}",
            marker=dict(symbol="x", size=10)
        ))

# --- Control Limits ---
mean_line = spc_result["mean"]
ucl_line = spc_result["ucl"]
lcl_line = spc_result["lcl"]

fig.add_hline(y=mean_line, line_dash="dot", line_color="gray",
              annotation_text="Mean", annotation_position="top left")

fig.add_hline(y=ucl_line, line_dash="dash", line_color="red",
              annotation_text="UCL", annotation_position="top left")

fig.add_hline(y=lcl_line, line_dash="dash", line_color="red",
              annotation_text="LCL", annotation_position="bottom left")

# --- Specification Limits (USL/LSL) ---
usl_avg = pd.to_numeric(filtered["usl"], errors="coerce").mean()
lsl_avg = pd.to_numeric(filtered["lsl"], errors="coerce").mean()

if not np.isnan(usl_avg):
    fig.add_hline(y=usl_avg, line_dash="dot", line_color="blue",
                  annotation_text="USL", annotation_position="top right")

if not np.isnan(lsl_avg):
    fig.add_hline(y=lsl_avg, line_dash="dot", line_color="blue",
                  annotation_text="LSL", annotation_position="bottom right")

# Final layout
fig.update_layout(
    title=f"SPC Chart for {selected_var} @ {selected_inst}",
    xaxis_title="Week",
    yaxis_title="Value",
    height=500
)

# Render plot and rule documentation
st.plotly_chart(fig, use_container_width=True)
st.markdown(CONFIG["spc_rules"])


