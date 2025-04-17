import numpy as np
import pandas as pd
from functions import (
    rule1, rule2, rule3, rule4, rule5, rule5b, rule5c,
    rule6, rule7, rule8, rule9, rule10, rule11
)

def limit_provided(limit):
    if limit is None:
        return False
    if isinstance(limit, str):
        return limit.strip() != "-"
    if isinstance(limit, pd.Series):
        converted = pd.to_numeric(limit, errors='coerce')
        return not converted.isna().all()
    return True

def apply_spc_rules(series, usl=None, lsl=None):
    mean = series.mean()
    std = series.std()
    flags = [
        rule1(series, mean, std),   # Rule 1
        rule2(series, mean, std),   # Rule 2
        rule3(series, mean, std),   # Rule 3
        rule4(series, mean),        # Rule 4
        rule5(series),              # Rule 5
        rule5b(series),             # Rule 5b
        #rule6(series),              # Rule 6
        rule7(series, mean, std),   # Rule 7
        rule8(series, mean, std),   # Rule 8
    ]
    
    if limit_provided(usl) or limit_provided(lsl):
        flags.append(rule11(series, usl, lsl))  # Rule 11
    
    violation_flags = np.logical_or.reduce(flags)
    return {
        "mean": mean,
        "std": std,
        "ucl": mean + 3 * std,
        "lcl": mean - 3 * std,
        "flags": flags,
        "violation_flags": violation_flags,
    }

def get_rule_names_for_index(flags, index):
    """
    Returns a list of rule names for which the flag at the given index is True.
    """
    base_rule_names = [
        "Rule 1", "Rule 2", "Rule 3", "Rule 4", "Rule 5",
        "Rule 5b", "Rule 7", "Rule 8"
    ]
    if len(flags) > len(base_rule_names):
        base_rule_names.append("Rule 11")
    return [base_rule_names[i] for i, flag in enumerate(flags) if flag[index]]

def count_rule_hits(flags):
    """Returns a list with the count of violations for each SPC rule."""
    return [int(np.sum(flag)) for flag in flags]

def get_violation_summary(flags):
    """
    Returns a list of tuples where each tuple contains the rule name and the number of violations.
    """
    base_rule_names = [
        "Rule 1", "Rule 2", "Rule 3", "Rule 4", "Rule 5",
        "Rule 5b", "Rule 7", "Rule 8"
    ]
    if len(flags) > len(base_rule_names):
        base_rule_names.append("Rule 11")
    summary = []
    for i, flag in enumerate(flags):
        summary.append((base_rule_names[i], int(np.sum(flag))))
    return summary

def create_export_df(df, violation_flags, rule_flags):
    """
    Create and return an exportable DataFrame that includes the original data,
    an overall violation flag, and columns for each SPC rule's individual flag.
    """
    df_export = df.copy().reset_index(drop=True)
    df_export["Violation"] = violation_flags[:len(df_export)]
    base_rule_names = [
        "Rule 1", "Rule 2", "Rule 3", "Rule 4", "Rule 5",
        "Rule 5b", "Rule 7", "Rule 8"
    ]
    if len(rule_flags) > len(base_rule_names):
        base_rule_names.append("Rule 11")
    for i, flag in enumerate(rule_flags):
        df_export[base_rule_names[i]] = flag[:len(df_export)]
    return df_export

# --- Centralized dictionary for config/text ---
CONFIG = {
    "title_main": "KPI Dashboard - Main Page",
    "title_chart": "Control Chart for {var} - Installation {inst}",
    "no_data": "No data available for this combination.",
    "select_text": "Select a Variable and Installation to view the control chart:",
    "spc_rules": """
    **SPC Rules Applied:**
    - **Rule 1:** 1 point > 3σ from the mean.
    - **Rule 2:** 2 out of 3 consecutive points > 2σ from the mean (same side).
    - **Rule 3:** 4 out of 5 consecutive points > 1σ from the mean (same side).
    - **Rule 4:** 8 consecutive points on one side of the mean.
    - **Rule 5:** 6 consecutive points trending up or down.
    - **Rule 5b:** 5 consecutive points trending up or down (faster detection).
    - **Rule 7:** 15 consecutive points within 1σ of the mean.
    - **Rule 8:** 8 consecutive points outside 1σ (both sides).
    - **Rule :** point outside of LSL/USL.

    """
}
