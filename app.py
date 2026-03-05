import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pioneer Salary Analytics | Dark Edition", layout="wide")

# 2. Premium Dark UI/UX Custom Styling
st.markdown("""
    <style>
    /* Main Background and Text */
    .main { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    
    /* Metrics and Cards */
    .stMetric { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; color: white !important; }
    .salary-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-top: 20px; }
    
    /* Table Styling */
    .stDataFrame { border: 1px solid #334155; border-radius: 8px; }
    th { background-color: #334155 !important; color: #cbd5e1 !important; font-size: 13px !important; text-transform: uppercase; }
    
    /* Note Box */
    .note-box { background-color: #334155; border: 1px solid #475569; padding: 15px; border-radius: 8px; color: #fbbf24; font-style: italic; margin-top: 10px; }
    
    /* Typography */
    h1, h2, h3 { color: #f8fafc !important; }
    p { color: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data with Rounded Figures
raw_data = [
    {"Designation": "Production Manager (HOD)", "Pioneer": 8300, "Asian_White": 19000, "JK": 24000, "Emirates": 27500, "Union": 17500, "Note": "Critical Gap: Current salary is ~61% below market median. High risk of operational disruption if key talent departs."},
    {"Designation": "Chief Engineer (Mechanical)", "Pioneer": 14685, "Asian_White": 19000, "JK": 23500, "Emirates": 27500, "Union": 25000, "Note": "Strategic Role: Compensation is significantly unaligned with Tier-1 competitors like Emirates Steel."},
    {"Designation": "Dy. Chief Engineer (Electrical) (HOD)", "Pioneer": 8500, "Asian_White": 19000, "JK": 23500, "Emirates": 22500, "Union": 20000, "Note": "Severe Disparity: Despite HOD status, pay is aligned with junior technical levels in the market."},
    {"Designation": "HR Executive (Internal)", "Pioneer": 4000, "Asian_White": 7000, "JK": 7000, "Emirates": 11000, "Union": 7500, "Note": "Internal Inequity: Paid significantly less than the External Relations counterpart (7,000) and far below market baseline."},
    {"Designation": "HR Executive (External)", "Pioneer": 7000, "Asian_White": 7500, "JK": 7000, "Emirates": 11000, "Union": 7500, "Note": "Partial Alignment: Closer to market average but requires adjustment to meet industry standard of 8,500+."},
    {"Designation": "CCR Operator", "Pioneer": 4070, "Asian_White": 6000, "JK": 7750, "Emirates": 9500, "Union": 7000, "Note": "Turnover Risk: Essential for continuous production; current pay scale is ~45% below market average."},
    {"Designation": "Head of Finance", "Pioneer": 25000, "Asian_White": 27500, "JK": 32500, "Emirates": 32500, "Union": 30000, "Note": "Executive Level: Competitive but lags behind the top-quartile pay of cement industry giants."}
]

df = pd.DataFrame(raw_data)
df['Pioneer'] = df['Pioneer'].round(0).astype(int)
df['Market_Avg'] = df[['Asian_White', 'JK', 'Emirates', 'Union']].mean(axis=1).round(0).astype(int)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Search
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1e293b/f8fafc?text=PIONEER+HR", use_column_width=True)
    st.markdown("### 🔍 Search Position")
    search_query = st.text_input("Designation Search", placeholder="Filter by title...", label_visibility="collapsed")
    st.markdown("---")
    st.info("Tip: Select a row in the table to reveal the interactive market comparison card.")

# 5. Dashboard Header
st.title("Competitive Salary Benchmark Dashboard (UAE)")
st.markdown("Detailed Analysis for Pioneer Cement Industries | Date: March 2026")

# Metrics Section
c1, c2, c3 = st.columns(3)
c1.metric("Roles Scoped", len(df))
c2.metric("Avg Market Variance", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
c3.metric("Critical Gaps (<-30%)", len(df[df['Variance %'] < -30]))

# Search Filtering
filtered_df = df[df['Designation'].str.contains(search_query, case=False)] if search_query else df

# Interactive Data Matrix
st.subheader("Salary Matrix (AED) - Click Row to Expand")
event = st.dataframe(
    filtered_df[['Designation', 'Pioneer', 'Market_Avg', 'Variance %']],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 6. Interaction Card
if len(event.selection.rows) > 0:
    sel_idx = event.selection.rows[0]
    row = filtered_df.iloc[sel_idx]
    
    st.markdown("---")
    st.markdown(f"### 📊 Competitive Analysis: {row['Designation']}")
    
    # Benchmarks
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Asian White", f"{row['Asian_White']:,}")
    b2.metric("JK Cement", f"{row['JK']:,}")
    b3.metric("Emirates Steel", f"{row['Emirates']:,}")
    b4.metric("Union Cement", f"{row['Union']:,}")
    
    st.markdown(f"""
    <div class="salary-card">
        <h4 style="margin-top:0; color: #3b82f6;">HR Intelligence & Market Notes:</h4>
        <p style="color: #cbd5e1;">{row['Note']}</p>
        <div class="note-box">
            <b>Verdict:</b> This designation is currently underpaid by <b>{abs(row['Variance %'])}%</b> 
            compared to the industry benchmark of {row['Market_Avg']:,} AED.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="padding: 20px; border: 1px dashed #475569; border-radius: 10px; text-align: center; color: #94a3b8;">
        Select a row above to generate the specialized market analysis note.
    </div>
    """, unsafe_allow_html=True)

# 7. CSV Export
st.sidebar.download_button("📥 Export CSV Data", df.to_csv(index=False), "Pioneer_Salary_Analysis.csv", "text/csv")
