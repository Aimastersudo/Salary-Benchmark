import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR | Salary Intelligence", layout="wide")

# 2. Premium Dark UI Styling
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    </style>
    """, unsafe_allow_html=True)

# 3. DUAL DATABASE LOADER - Auto Fixing Hidden Spaces
@st.cache_data
def load_databases():
    try:
        # DB 1: Load Benchmark Data 
        bench_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        
        # DB 2: Load Actuals Payroll Data (The one you just uploaded)
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        
        # 🚀 FIX 1: Clean hidden spaces from Column Names
        bench_df.columns = bench_df.columns.str.strip()
        payroll_df.columns = payroll_df.columns.str.strip()
        
        # 🚀 FIX 2: Clean hidden spaces from the actual Designation Names
        bench_df['Designation'] = bench_df['Designation'].astype(str).str.strip()
        payroll_df['Designation'] = payroll_df['Designation'].astype(str).str.strip()
            
        # Calculate Dynamic Headcount from Payroll Data 
        hc_df = payroll_df.groupby('Designation').size().reset_index(name='Live_HC')
        
        # Merge the Live Headcount into the Benchmark Data
        merged_df = pd.merge(bench_df, hc_df, on='Designation', how='left')
        
        # Fill missing values with 0 
        merged_df['Live_HC'] = merged_df['Live_HC'].fillna(0).astype(int)
        
        # Calculate Market Variance %
        merged_df['Variance %'] = ((merged_df['Pioneer'] - merged_df['Market']) / merged_df['Market'] * 100).round(0).astype(int)
        
        return merged_df
    except Exception as e:
        st.error(f"System Error: {e}")
        return None

df = load_databases()

if df is not None:
    # 4. Sidebar Filters
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "📁 Structural Groups"])
        st.markdown("---")
        
        # Sorted Department Filter
        all_depts = sorted(df['Dept'].dropna().unique())
        selected_depts = st.multiselect("Filter Departments:", all_depts, default=all_depts)
        search_q = st.text_input("Find Designation", placeholder="Search roles...")

    # Filter Logic
    f_df = df[df['Dept'].isin(selected_depts)]
    if search_q:
        f_df = f_df[f_df['Designation'].str.contains(search_q, case=False, na=False)]

    # 5. Dashboard View
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.caption("🟢 Live Headcount Synced with Actuals Payroll")
        
        # Metrics - Using dynamic 'Live_HC'
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations Scoped", len(f_df))
        c2.metric("Live Headcount", int(f_df['Live_HC'].sum())) 
        
        avg_variance = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_variance, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))

        # Data Table
        display_cols = ['Designation', 'Dept', 'Tier', 'Live_HC', 'Pioneer', 'Market', 'Variance %']
        st.subheader("Interactive Salary Matrix (AED)")
        event = st.dataframe(f_df[display_cols], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

        # AI Insight
        if len(event.selection.rows) > 0:
            row = f_df.iloc[event.selection.rows[0]]
            st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini HR Analysis:</b> Current pay for {row['Designation']} in the {row['Dept']} 
                    department is {abs(row['Variance %'])}% below market levels. With a current live headcount of <b>{row['Live_HC']}</b> (synced from payroll), 
                    talent retention should be closely monitored by Management.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 6. Analysis View
    elif page == "📉 Market Analysis":
        st.title("Market Disparity by Structural Tier")
        tier_avg = f_df.groupby('Tier')['Variance %'].mean().reset_index()
        fig = px.bar(tier_avg, x='Tier', y='Variance %', color='Tier', title="Avg. Market Variance by Tier (%)")
        fig.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Avg. Variance by Department (%)")
        dept_avg = f_df.groupby('Dept')['Variance %'].mean().reset_index().sort_values('Variance %')
        fig2 = px.bar(dept_avg, x='Dept', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn')
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # 7. Groups View
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        display_cols = ['Designation', 'Dept', 'Live_HC', 'Pioneer', 'Market', 'Variance %']
        t1, t2, t3 = st.tabs(["Leadership & Management", "Professional Staff", "Technical Operations"])
        with t1: st.dataframe(f_df[f_df['Tier'] == 'Leadership & Management'][display_cols], use_container_width=True, hide_index=True)
        with t2: st.dataframe(f_df[f_df['Tier'] == 'Professional Staff'][display_cols], use_container_width=True, hide_index=True)
        with t3: st.dataframe(f_df[f_df['Tier'] == 'Technical Operations'][display_cols], use_container_width=True, hide_index=True)
