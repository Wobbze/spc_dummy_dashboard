import numpy as np
import pandas as pd

# --- SPC Rules ---
def rule1(series, mean, std):
    return (series > mean + 3 * std) | (series < mean - 3 * std)

def rule2(series, mean, std):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 2):
        window = series.iloc[i:i + 3]
        if np.sum(window > mean + 2 * std) >= 2 or np.sum(window < mean - 2 * std) >= 2:
            flags[i:i + 3] = True
    return flags

def rule3(series, mean, std):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 4):
        window = series.iloc[i:i + 5]
        if np.sum(window > mean + std) >= 4 or np.sum(window < mean - std) >= 4:
            flags[i:i + 5] = True
    return flags

def rule4(series, mean):
    flags = np.zeros(len(series), dtype=bool)
    for direction in [lambda x: x > mean, lambda x: x < mean]:
        count = 0
        start = 0
        for i in range(len(series)):
            if direction(series.iloc[i]):
                if count == 0:
                    start = i
                count += 1
            else:
                if count >= 8:
                    flags[start:i] = True
                count = 0
        if count >= 8:
            flags[len(series) - count:] = True
    return flags

def rule5(series):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 5):
        window = series.iloc[i:i + 6]
        if np.all(np.diff(window) > 0) or np.all(np.diff(window) < 0):
            flags[i:i + 6] = True
    return flags

def rule5b(series):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 4):
        window = series.iloc[i:i + 5]
        if np.all(np.diff(window) > 0) or np.all(np.diff(window) < 0):
            flags[i:i + 5] = True
    return flags

def rule5c(series):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 5):
        window = series.iloc[i:i + 6]
        diffs = np.diff(window)
        if np.all(diffs >= 0) and np.any(diffs > 0):
            flags[i:i + 6] = True
        elif np.all(diffs <= 0) and np.any(diffs < 0):
            flags[i:i + 6] = True
    return flags

def rule6(series):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 13):
        window = series.iloc[i:i + 14]
        diffs = np.diff(window)
        if np.all(diffs != 0) and all(np.sign(diffs[j]) != np.sign(diffs[j + 1]) for j in range(len(diffs) - 1)):
            flags[i:i + 14] = True
    return flags

def rule7(series, mean, std):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 14):
        window = series.iloc[i:i + 15]
        if np.all((window < mean + std) & (window > mean - std)):
            flags[i:i + 15] = True
    return flags

def rule8(series, mean, std):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 7):
        window = series.iloc[i:i + 8]
        if np.all((window > mean + std) | (window < mean - std)):
            flags[i:i + 8] = True
    return flags

def rule9(series, mean):
    flags = np.zeros(len(series), dtype=bool)
    count = 0
    start = 0
    for i in range(len(series)):
        if series.iloc[i] > mean:
            if count == 0:
                start = i
            count += 1
        else:
            if count >= 9:
                flags[start:i] = True
            count = 0
    if count >= 9:
        flags[len(series) - count:] = True
    return flags

def rule10(series, mean, std):
    flags = np.zeros(len(series), dtype=bool)
    for i in range(len(series) - 24):
        window = series.iloc[i:i + 25]
        if np.sum((window < mean + std) & (window > mean - std)) >= 24:
            flags[i:i + 25] = True
    return flags

# --- Extra Rule: Check if a point is out of control limits ---
def rule11(series, usl, lsl):
    usl_numeric = pd.to_numeric(usl, errors='coerce') if usl is not None else None
    lsl_numeric = pd.to_numeric(lsl, errors='coerce') if lsl is not None else None

    flags = np.zeros(len(series), dtype=bool)
    if usl_numeric is not None:
        flags |= (series > usl_numeric)
    if lsl_numeric is not None:
        flags |= (series < lsl_numeric)
    return flags

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
    - **Rule 5c:** 6 points with non-strict monotonic trend.
    - **Rule 6:** 14 consecutive points alternating up and down.
    - **Rule 7:** 15 consecutive points within 1σ of the mean.
    - **Rule 8:** 8 consecutive points outside 1σ (both sides).
    - **Rule 9:** 9 consecutive points on the same side of the mean.
    - **Rule 10:** 24 out of 25 points within 1σ of the mean.
    - **Rule 11:** Data point is flagged if it is above USL or below LSL.
    """
}
