from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILE = ROOT / "results" / "stress_test_results.csv"
SUMMARY_FILE = ROOT / "results" / "stress_test_summary.csv"

st.set_page_config(
    page_title="DataResilience | Stress Testing",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --ink:#0E1420; --panel:#161D2E; --panel2:#1B2438; --line:#26304A;
  --amber:#E8A33D; --teal:#4FBDB0; --paper:#EDEFF3; --mute:#8A93A8;
}
html, body, [class*="css"] {font-family:'Inter',sans-serif;}
.stApp {
  color:var(--paper);
  background-color:var(--ink);
  background-image:linear-gradient(rgba(38,48,74,.24) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(38,48,74,.24) 1px,transparent 1px);
  background-size:64px 64px;
}
header[data-testid="stHeader"] {background:rgba(14,20,32,.82);}
.block-container {max-width:1500px;padding-top:2.1rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;color:var(--paper)!important;letter-spacing:-.025em;}
p, label, .stMarkdown {color:var(--paper);}
[data-testid="stSidebar"] {background:#111827;border-right:1px solid var(--line);}
[data-testid="stSidebar"] * {color:var(--paper);}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:var(--mute);}
.hero {
  position:relative; overflow:hidden; padding:34px 38px; margin-bottom:30px;
  border:1px solid var(--line); border-radius:14px;
  background:radial-gradient(ellipse at 88% 0%,rgba(79,189,176,.14),transparent 42%),
             linear-gradient(125deg,#161D2E,#121a2a 72%,#182438);
}
.hero:after {content:"";position:absolute;right:8%;top:-100px;width:250px;height:250px;
  border:1px solid rgba(79,189,176,.18);border-radius:50%;
  box-shadow:0 0 0 30px rgba(79,189,176,.025),0 0 0 60px rgba(79,189,176,.02);}
.eyebrow {font:500 11px 'JetBrains Mono',monospace;letter-spacing:.15em;text-transform:uppercase;color:var(--teal);}
.hero h1 {font-size:clamp(28px,3vw,42px);line-height:1.13;margin:13px 0 12px;max-width:900px;}
.hero p {max-width:760px;color:var(--mute);font-size:14px;line-height:1.8;margin:0;}
.section-kicker {font:500 11px 'JetBrains Mono',monospace;color:var(--teal);letter-spacing:.14em;text-transform:uppercase;margin:26px 0 10px;}
.metric-card {height:100%;min-height:126px;background:linear-gradient(145deg,#1a2438,#151d2e);
  border:1px solid var(--line);border-radius:10px;padding:18px 19px;transition:.2s ease;}
.metric-card:hover {border-color:var(--teal);transform:translateY(-2px);}
.metric-label {font:500 10px 'JetBrains Mono',monospace;letter-spacing:.1em;color:var(--mute);text-transform:uppercase;}
.metric-value {font:600 29px 'Space Grotesk',sans-serif;color:var(--amber);margin-top:13px;}
.metric-help {font-size:11px;color:var(--mute);margin-top:3px;}
.panel {background:rgba(22,29,46,.84);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:8px 0 18px;}
.panel-title {font:600 17px 'Space Grotesk',sans-serif;color:var(--paper);margin-bottom:3px;}
.panel-sub {font-size:12px;color:var(--mute);margin-bottom:10px;}
div[data-baseweb="select"]>div,div[data-testid="stMultiSelect"]>div>div {
  background:#161D2E;border-color:var(--line);border-radius:7px;}
.stTabs [data-baseweb="tab-list"] {gap:20px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {font-weight:600;color:var(--mute);}
.stTabs [aria-selected="true"] {color:var(--teal)!important;border-bottom-color:var(--teal)!important;}
.stButton>button,.stDownloadButton>button {border:1px solid var(--line);border-radius:6px;background:#1B2438;color:var(--paper);font-weight:600;}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:var(--teal);color:var(--teal);}
div[data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:9px;overflow:hidden;}
hr {border-color:var(--line);}
small,.muted {color:var(--mute);}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
# Graph palette matched to the reference chart:
# combined = sky blue, label = deep blue, missing = soft pink, outlier = vivid red.
COLORS = {
    "combined": "#82C8FF",
    "label": "#0874C9",
    "missing": "#FFAAAA",
    "outlier": "#FF2929",
    "baseline": "#8A93A8",
}
PLOT_TEMPLATE = "plotly_dark"

def find_col(frame, candidates):
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None

def summary_col(metric):
    return find_col(summary, [f"{metric}_mean", metric])

def fmt_number(value, currency=False):
    if pd.isna(value):
        return "—"
    value = float(value)
    if currency:
        sign = "−" if value < 0 else ""
        value = abs(value)
        if value >= 10_000_000:
            return f"{sign}₹{value/10_000_000:.2f}Cr"
        if value >= 100_000:
            return f"{sign}₹{value/100_000:.2f}L"
        return f"{sign}₹{value:,.0f}"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.2f}"

def chart_layout(fig, height=390, legend=True):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,29,46,.42)",
        font=dict(family="Inter", color="#EDEFF3", size=12),
        margin=dict(l=18, r=18, t=55, b=22),
        hoverlabel=dict(bgcolor="#1B2438", bordercolor="#4FBDB0",
                        font=dict(color="#EDEFF3", family="Inter")),
        xaxis=dict(gridcolor="#26304A", linecolor="#26304A", zerolinecolor="#26304A"),
        yaxis=dict(gridcolor="#26304A", linecolor="#26304A", zerolinecolor="#26304A"),
        legend=dict(
            title="CORRUPTION TYPE",
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11)
        ) if legend else dict(visible=False),
    )
    return fig

def line_chart(data, y, title, y_title, percent=False, height=390):
    fig = px.line(
        data, x="Noise_Level_Pct", y=y, color="Noise_Type",
        markers=True, color_discrete_map=COLORS,
        category_orders={"Noise_Type": ["missing", "outlier", "label", "combined"]},
        labels={"Noise_Level_Pct":"Noise intensity (%)", y:y_title,
                "Noise_Type":"Corruption type"},
    )
    fig.update_traces(
        line=dict(width=3, shape="spline"),
        marker=dict(size=10, line=dict(width=2, color="#0E1420")),
        hovertemplate="<b>%{fullData.name}</b><br>Noise: %{x}%<br>"+y_title+": %{y:.2f}"+("%" if percent else "")+"<extra></extra>",
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=sorted(data["Noise_Level_Pct"].dropna().unique()),
        ticksuffix="%",
        title="Noise intensity (%)",
    )
    fig.update_yaxes(title=y_title, ticksuffix="%" if percent else "")
    fig.update_layout(title=dict(text=title, x=0.01, xanchor="left",
                                 font=dict(size=17, color="#EDEFF3")))
    return chart_layout(fig, height)

def metric_card(label, value, note):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-help">{note}</div></div>',
        unsafe_allow_html=True,
    )

# ---------- Load outputs ----------
if not RESULTS_FILE.exists() or not SUMMARY_FILE.exists():
    st.markdown('<div class="hero"><div class="eyebrow">DATA QUALITY RESEARCH FRAMEWORK</div>'
                '<h1>Stress-Testing &amp; Noise-Injection Analytics Engine</h1>'
                '<p>The dashboard needs the experiment output files. Run the experiment runner '
                'and plot generator from the project root, then refresh this page.</p></div>',
                unsafe_allow_html=True)
    st.code("python src/experiment_runner.py\npython src/plot_degradation.py", language="powershell")
    st.stop()

results = pd.read_csv(RESULTS_FILE)
summary = pd.read_csv(SUMMARY_FILE)

# Support the current project column names and earlier prototype names.
type_col = find_col(results, ["Noise_Type"])
level_col = find_col(results, ["Noise_Level_Pct", "Noise_Pct"])
summary_level_col = find_col(summary, ["Noise_Level_Pct", "Noise_Pct"])
if not all([type_col, level_col, summary_level_col]):
    st.error("The results files do not contain the expected noise type / noise level columns.")
    st.write("Results columns:", list(results.columns))
    st.write("Summary columns:", list(summary.columns))
    st.stop()

results[level_col] = pd.to_numeric(results[level_col], errors="coerce")
summary[summary_level_col] = pd.to_numeric(summary[summary_level_col], errors="coerce")
results[type_col] = results[type_col].astype(str).str.lower()
summary[type_col] = summary[type_col].astype(str).str.lower()

# Normalize older prototype column names so every chart uses one schema.
if level_col != "Noise_Level_Pct":
    results = results.rename(columns={level_col: "Noise_Level_Pct"})
    level_col = "Noise_Level_Pct"
if summary_level_col != "Noise_Level_Pct":
    summary = summary.rename(columns={summary_level_col: "Noise_Level_Pct"})
    summary_level_col = "Noise_Level_Pct"

noise_results = results[~results[type_col].isin(["baseline", "none", "clean"])].copy()
noise_summary = summary[~summary[type_col].isin(["baseline", "none", "clean"])].copy()
noise_summary = noise_summary[noise_summary[summary_level_col] > 0].copy()

if noise_results.empty or noise_summary.empty:
    st.error("No non-baseline experiment results were found.")
    st.stop()

noise_types = sorted(noise_results[type_col].dropna().unique())
levels = sorted(noise_results[level_col].dropna().unique())

# ---------- Sidebar ----------
st.sidebar.markdown("## ◈ DataResilience")
st.sidebar.markdown('<div class="eyebrow">EXPERIMENT CONTROL PANEL</div>', unsafe_allow_html=True)
st.sidebar.divider()
selected_types = st.sidebar.multiselect("Corruption mechanisms", noise_types, default=noise_types)
selected_levels = st.sidebar.multiselect("Noise intensity (%)", levels, default=levels)
st.sidebar.divider()
st.sidebar.markdown("**Experiment configuration**")
st.sidebar.caption(f"{len(noise_types)} corruption mechanisms · {len(levels)} intensity levels")
st.sidebar.caption("Repeated random-seed experiments")
st.sidebar.markdown("---")
st.sidebar.caption("Python · Pandas · NumPy · SciPy · Plotly · Streamlit")

filtered_results = noise_results[
    noise_results[type_col].isin(selected_types)
    & noise_results[level_col].isin(selected_levels)
].copy()
filtered_summary = noise_summary[
    noise_summary[type_col].isin(selected_types)
    & noise_summary[summary_level_col].isin(selected_levels)
].copy()

if filtered_results.empty or filtered_summary.empty:
    st.warning("No experiments match the selected filters. Choose at least one mechanism and intensity.")
    st.stop()

# ---------- Hero ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">DATA QUALITY RESEARCH FRAMEWORK · EXPERIMENTAL ANALYSIS</div>
  <h1>Stress-Testing &amp; Noise-Injection Analytics Engine</h1>
  <p>Measuring how controlled data corruption changes business KPIs, customer segmentation
  and statistical analysis — across multiple corruption mechanisms and repeated experiments.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Summary cards ----------
st.markdown('<div class="section-kicker">01 / Experiment overview</div>', unsafe_allow_html=True)
seed_col = find_col(noise_results, ["Seed"])
run_count = len(noise_results)
seed_count = noise_results[seed_col].nunique() if seed_col else "—"
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("EXPERIMENTAL RUNS", f"{run_count:,}", "Across all noise scenarios")
with c2: metric_card("CORRUPTION TYPES", str(len(noise_types)), "Missing · Outlier · Label · Combined")
with c3: metric_card("INTENSITY LEVELS", str(len(levels)), "Distinct noise settings")
with c4: metric_card("RANDOM SEEDS", str(seed_count), "Repeated runs per scenario")

# ---------- Tabs ----------
tab_overview, tab_kpis, tab_statistics, tab_records = st.tabs([
    "Overview", "Business KPI impact", "Stability & statistics", "Experiment records"
])

with tab_overview:
    st.markdown('<div class="section-kicker">02 / Revenue response</div>', unsafe_allow_html=True)
    revenue_error = find_col(noise_summary, ["Revenue_Error_Pct_mean", "Revenue_Abs_Error_Pct_mean", "Revenue_Error_mean"])
    if revenue_error:
        st.markdown('<div class="panel"><div class="panel-title">Revenue deviation by corruption mechanism</div>'
                    '<div class="panel-sub">Mean percentage deviation from the clean baseline across repeated runs.</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            line_chart(filtered_summary, revenue_error,
                       "Revenue impact across noise intensity",
                       "Mean revenue deviation (%)", percent=True, height=440),
            use_container_width=True, config={"displayModeBar": False, "responsive": True}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("A revenue error mean column was not found in the summary file.")

    left, right = st.columns(2)
    with left:
        rev_col = summary_col("Total_Revenue")
        if rev_col:
            fig = px.bar(filtered_summary, x=summary_level_col, y=rev_col,
                         color=type_col, barmode="group", color_discrete_map=COLORS,
                         labels={summary_level_col:"Noise intensity (%)", rev_col:"Mean total revenue", type_col:"Corruption type"})
            fig.update_layout(title="Reported revenue", xaxis_title="Noise intensity (%)", yaxis_title="Mean total revenue")
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True, config={"displayModeBar":False})
    with right:
        flip_col = find_col(noise_summary, ["Segment_Flip_Rate_Pct_mean", "Segment_Flip_Pct_mean"])
        if flip_col:
            fig = px.bar(filtered_summary, x=summary_level_col, y=flip_col,
                         color=type_col, barmode="group", color_discrete_map=COLORS,
                         labels={summary_level_col:"Noise intensity (%)", flip_col:"Mean segment flip rate (%)", type_col:"Corruption type"})
            fig.update_layout(title="Customer segment changes", xaxis_title="Noise intensity (%)", yaxis_title="Mean segment flip rate (%)")
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True, config={"displayModeBar":False})

with tab_kpis:
    st.markdown('<div class="section-kicker">03 / Business KPI impact</div>', unsafe_allow_html=True)
    kpi_options = [
        ("Revenue deviation (%)", ["Revenue_Error_Pct_mean", "Revenue_Abs_Error_Pct_mean"]),
        ("Units deviation (%)", ["Units_Error_Pct_mean", "Units_Abs_Error_Pct_mean"]),
        ("Average order value", ["AOV_mean"]),
        ("Revenue per customer", ["Revenue_Per_Customer_mean"]),
        ("Missing cells (%)", ["Missing_Percentage_mean", "Missing_Pct_mean"]),
    ]
    available = [(label, find_col(noise_summary, cols)) for label, cols in kpi_options]
    available = [(label, col) for label, col in available if col]
    if available:
        label_to_col = {label: col for label, col in available}
        chosen_label = st.selectbox("Select a metric to inspect", list(label_to_col))
        chosen_col = label_to_col[chosen_label]
        is_percent = "%" in chosen_label or "deviation" in chosen_label.lower()
        fig = line_chart(filtered_summary, chosen_col, chosen_label,
                         chosen_label, percent=is_percent, height=430)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No compatible KPI summary columns were found.")

    st.markdown("#### Mean experimental outcomes")
    st.dataframe(filtered_summary, use_container_width=True, hide_index=True)

with tab_statistics:
    st.markdown('<div class="section-kicker">04 / Analytical stability</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    anova_col = find_col(noise_summary, ["ANOVA_p_mean", "ANOVA_p_value_mean"])
    with left:
        if anova_col:
            fig = px.line(filtered_summary, x=summary_level_col, y=anova_col,
                          color=type_col, markers=True, color_discrete_map=COLORS,
                          labels={summary_level_col:"Noise intensity (%)", anova_col:"Mean ANOVA p-value", type_col:"Corruption type"})
            fig.add_hline(y=.05, line_dash="dash", line_color="#E8A33D",
                          annotation_text="p = 0.05", annotation_position="top left")
            fig.update_layout(title="ANOVA p-value trend", yaxis_title="Mean p-value", xaxis_title="Noise intensity (%)")
            st.plotly_chart(chart_layout(fig, 370), use_container_width=True, config={"displayModeBar":False})
            st.caption("Mean p-values are descriptive; they do not alone establish false-positive or false-negative rates.")
        else:
            st.info("ANOVA p-value summary is unavailable.")
    with right:
        missing_col = find_col(noise_summary, ["Missing_Percentage_mean", "Missing_Pct_mean"])
        if missing_col:
            fig = px.bar(filtered_summary, x=summary_level_col, y=missing_col,
                         color=type_col, barmode="group", color_discrete_map=COLORS,
                         labels={summary_level_col:"Noise intensity (%)", missing_col:"Mean missing data (%)", type_col:"Corruption type"})
            fig.update_layout(title="Missing-data exposure", yaxis_title="Mean missing data (%)", xaxis_title="Noise intensity (%)")
            st.plotly_chart(chart_layout(fig, 370), use_container_width=True, config={"displayModeBar":False})
    flip_col = find_col(noise_summary, ["Segment_Flip_Rate_Pct_mean", "Segment_Flip_Pct_mean"])
    if flip_col:
        fig = px.line(filtered_summary, x=summary_level_col, y=flip_col,
                      color=type_col, markers=True, color_discrete_map=COLORS,
                      labels={summary_level_col:"Noise intensity (%)", flip_col:"Mean segment flip rate (%)", type_col:"Corruption type"})
        fig.update_layout(title="Customer segmentation stability", yaxis_title="Mean segment flip rate (%)", xaxis_title="Noise intensity (%)")
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True, config={"displayModeBar":False})

with tab_records:
    st.markdown('<div class="section-kicker">05 / Experiment-level records</div>', unsafe_allow_html=True)
    st.markdown("Inspect individual repetitions, compare seeds and export the filtered records.")
    st.dataframe(filtered_results, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered experiment records",
        data=filtered_results.to_csv(index=False).encode("utf-8"),
        file_name="stress_test_filtered_results.csv",
        mime="text/csv",
    )

st.divider()
st.markdown(
    '<div style="text-align:center;color:#8A93A8;font:11px JetBrains Mono,monospace;letter-spacing:.1em;">'
    'DATA RESILIENCE ANALYTICS · CONTROLLED CORRUPTION · REPRODUCIBLE EXPERIMENTS'
    '</div>',
    unsafe_allow_html=True,
)

