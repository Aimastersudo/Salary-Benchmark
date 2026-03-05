import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pioneer Salary Analytics", layout="wide")

# 2. Modern UI/UX Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .salary-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .note-box { background-color: #fff7ed; border: 1px solid #ffedd5; padding: 15px; border-radius: 8px; color: #9a3412; font-style: italic; }
    th { background-color: #f1f5f9 !important; font-size: 13px !important; text-transform: uppercase; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data with Rounded Figures
raw_data = [
    {"Designation": "Production Manager (HOD)", "Pioneer": 8300, "Asian_White": 19000, "JK": 24000, "Emirates": 27500, "Union": 17500, "Note": "Critical Gap: The current salary is approximately 61% below the market median. Immediate review recommended for operational stability."},
    {"Designation": "Chief Engineer (Mechanical)", "Pioneer": 14685, "Asian_White": 19000, "JK": 23500, "Emirates": 27500, "Union": 25000, "Note": "High Responsibility Role: Current pay lags significantly behind Emirates Steel and JK Cement benchmarks."},
    {"Designation": "HR Executive (Internal)", "Pioneer": 4000, "Asian_White": 7000, "JK": 7000, "Emirates": 11000, "Union": 7500, "Note": "Equity Issue: Significantly lower than the External Relations role (7,000) and market minimums."},
    {"Designation": "HR Executive (External)", "Pioneer": 7000, "Asian_White": 7500, "JK": 7000, "Emirates": 11000, "Union": 7500, "Note": "Market Alignment: Closer to market average but still below premium competitors like Emirates Steel."},
    {"Designation": "CCR Operator", "Pioneer": 4070, "Asian_White": 6000, "JK": 7750, "Emirates": 9500, "Union": 7000, "Note": "Technical Skill Gap: Operators are essential for 24/7 production; current pay risks high turnover."},
    {"Designation": "Head of Finance", "Pioneer": 25000, "Asian_White": 27500, "JK": 32500, "Emirates": 32500, "Union": 30000, "Note": "Executive Level: Position is relatively competitive but remains below the 75th percentile of the market."},
    {"Designation": "Quality Control Manager", "Pioneer": 28000, "Asian_White": 19000, "JK": 27500, "Emirates": 27500, "Union": 21000, "Note": "Strong Alignment: One of the few roles currently meeting or exceeding market averages."},
]

df = pd.DataFrame(raw_data)
# Rounding all Pioneer salaries for clean display
df['Pioneer'] = df['Pioneer'].round(0).astype(int)
df['Market_Avg'] = df[['Asian_White', 'JK', 'Emirates', 'Union']].mean(axis=1).round(0).astype(int)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Search
with st.sidebar:
    st.markdown("### 🔍 Search Position")
    search_query = st.text_input("Designation Search", placeholder="Type title...", label_visibility="collapsed")
    st.markdown("---")
    st.info("Tip: Click a row in the table to see detailed market breakdown and notes.")

# 5. Main Content
st.title("Pioneer Cement: Salary Intelligence Portal")

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Roles Analyzed", len(df))
col2.metric("Avg Market Gap", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
col3.metric("Critical Gaps", len(df[df['Variance %'] < -30]))

# Search Logic
filtered_df = df[df['Designation'].str.contains(search_query, case=False)] if search_query else df

# Interactive Table (Selection Enabled)
st.subheader("Select a Designation to view Market Details")
event = st.dataframe(
    filtered_df[['Designation', 'Pioneer', 'Market_Avg', 'Variance %']],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 6. Detailed Note Section (Appears when a row is clicked)
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    selected_row = filtered_df.iloc[selected_index]
    
    st.markdown("---")
    st.markdown(f"### 📋 Market Breakdown: {selected_row['Designation']}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Asian White", f"{selected_row['Asian_White']:,}")
    c2.metric("JK Cement", f"{selected_row['JK']:,}")
    c3.metric("Emirates Steel", f"{selected_row['Emirates']:,}")
    c4.metric("Union Cement", f"{selected_row['Union']:,}")
    
    st.markdown(f"""
    <div class="salary-card">
        <h4 style="margin-top:0;">Management Note:</h4>
        <p>{selected_row['Note']}</p>
        <div class="note-box">
            <b>Market Verdict:</b> This role is currently positioned at <b>{selected_row['Variance %']}%</b> 
            relative to the market average of {selected_row['Market_Avg']:,} AED.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("👆 Click on a row in the table above to see the full market comparison and HR notes.")
