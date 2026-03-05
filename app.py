import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Pioneer HR Intelligence", layout="wide")

# 2. Premium Dark Styling
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data from local CSV
@st.cache_data
def load_data():
    data = pd.read_csv("salary_data.csv")
    data['Variance %'] = ((data['Pioneer'] - data['Market']) / data['Market'] * 100).round(0).astype(int)
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Error: Database file not found. Ensure 'salary_data.csv' is in your GitHub. Error details: {e}")
    st.stop()

# 4. Sidebar Filters
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
    page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "📁 Structural Groups"])
    st.markdown("---")
    selected_depts = st.multiselect("Filter by Department:", df['Dept'].unique(), default=df['Dept'].unique())
    search_q = st.text_input("Find Designation", placeholder="Search all 84 roles...")

# Filtering Logic
f_df = df[df['Dept'].isin(selected_depts)]
if search_q:
    f_df = f_df[f_df['Designation'].str.contains(search_q, case=False)]

# 5. Executive Dashboard
if page == "📊 Executive Dashboard":
    st.title("Strategic Salary Benchmark Dashboard")
    st.caption(f"Connected to Central Database | {len(f_df)} Designations Analysed")
    
    # Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Designations", len(f_df))
    c2.metric("Total Headcount", int(f_df['HC'].sum()))
    c3.metric("Avg. Market Gap", f"{f_df['Variance %'].mean():.0f}%", delta_color="inverse")
    c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))

    # Data Matrix
    st.subheader("Interactive Salary Matrix (AED)")
    event = st.dataframe(f_df, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight
    if len(event.selection.rows) > 0:
        row = f_df.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
        v = row['Variance %']
        st.markdown(f"""
        <div class="salary-card">
            <div class="ai-insight-box">
                <b>Gemini HR Analysis:</b> The role of <b>{row['Designation']}</b> in <b>{row['Dept']}</b> 
                is underpaid by <b>{abs(v)}%</b>. With <b>{row['HC']}</b> employees, this represents a significant risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

# 6. Analysis View
elif page == "📉 Market Analysis":
    st.title("Market Disparity Analysis")
    
    dept_v = f_df.groupby('Dept')['Variance %'].mean().reset_index().sort_values('Variance %')
    fig = px.bar(dept_v, x='Dept', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn', title="Avg. Variance by Department (%)")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    tier_v = f_df.groupby('Tier')['Variance %'].mean().reset_index()
    fig2 = px.bar(tier_v, x='Tier', y='Variance %', color='Tier', title="Variance by Structural Tier (%)")
    fig2.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# 7. Structural Groups
elif page == "📁 Structural Groups":
    st.title("Organizational Tier Breakdown")
    t1, t2, t3 = st.tabs(["Leadership & Management", "Professional Staff", "Technical Operations"])
    with t1: st.dataframe(f_df[f_df['Tier'] == 'Leadership & Management'], use_container_width=True, hide_index=True)
    with t2: st.dataframe(f_df[f_df['Tier'] == 'Professional Staff'], use_container_width=True, hide_index=True)
    with t3: st.dataframe(f_df[f_df['Tier'] == 'Technical Operations'], use_container_width=True, hide_index=True)
