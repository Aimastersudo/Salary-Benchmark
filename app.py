import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR | Salary Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER - The Ultimate HR Engine
@st.cache_data
def load_databases():
    try:
        # DB 1: Internal Roles
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        # DB 2: Actuals Payroll
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        # DB 3: External Market Benchmarks (Updated without Pioneer column)
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        # Clean column spaces
        for df in [core_df, payroll_df, market_df]:
            df.columns = df.columns.str.strip()

        # Clean Designations for perfect merging
        core_df['Designation_Clean'] = core_df['Designation'].astype(str).str.strip().str.title()
        payroll_df['Designation_Clean'] = payroll_df['Designation'].astype(str).str.strip().str.title()
        market_df['Designation_Clean'] = market_df['Designation'].astype(str).str.strip().str.title()

        # Step 1: Headcount Calculation
        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')

        # Step 2: Dynamic Market Salary Calculation
        def parse_salary_range(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val == '-' or val == '' or str(val).lower() == 'nan': return np.nan
            if '-' in val:
                parts = [float(p.strip()) for p in val.split('-') if p.strip()]
                return sum(parts) / len(parts) if parts else np.nan
            try: return float(val)
            except: return np.nan

        # Dynamically ignore ID and Designation columns
        ignore_cols = ['#', 'Designation', 'Designation_Clean']
        comp_cols = [c for c in market_df.columns if c not in ignore_cols]
        
        # Parse ranges and calculate average for competitors
        for c in comp_cols:
            market_df[c] = market_df[c].apply(parse_salary_range)
            
        market_df['Calculated Market Salary'] = market_df[comp_cols].mean(axis=1).round(0)
        market_clean = market_df[['Designation_Clean', 'Calculated Market Salary']].dropna(subset=['Calculated Market Salary'])

        # Step 3: Merge Everything Together
        merged_df = pd.merge(core_df, hc_df, on='Designation_Clean', how='left')
        merged_df = pd.merge(merged_df, market_clean, on='Designation_Clean', how='left')

        # Clean Pioneer Salary
        merged_df['Your Salary (AED)'] = merged_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float)

        # Fill NAs
        merged_df['Live_HC'] = merged_df['Live_HC'].fillna(0).astype(int)
        
        # If Market Salary is missing for a role, default it to Pioneer salary to avoid graph errors
        merged_df['Calculated Market Salary'] = merged_df['Calculated Market Salary'].fillna(merged_df['Your Salary (AED)'])
        
        # Variance calculation
        merged_df['Variance %'] = ((merged_df['Your Salary (AED)'] - merged_df['Calculated Market Salary']) / merged_df['Calculated Market Salary'] * 100).round(0).astype(int)

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
        
        all_depts = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("Filter Departments:", all_depts, default=all_depts)
        search_q = st.text_input("Find Designation", placeholder="Search roles...")

    # Filter Logic
    f_df = df[df['Department'].isin(selected_depts)]
    if search_q:
        f_df = f_df[f_df['Designation'].str.contains(search_q, case=False, na=False)]

    # 5. Dashboard View
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.caption("🟢 Live 3-Pillar Architecture: Core Roles + Payroll Headcount + Market Benchmarks")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations Scoped", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        
        avg_variance = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_variance, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))

        display_cols = ['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']
        st.subheader("Interactive Salary Matrix (AED)")
        event = st.dataframe(f_df[display_cols], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

        if len(event.selection.rows) > 0:
            row = f_df.iloc[event.selection.rows[0]]
            st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini HR Analysis:</b> Current pay for {row['Designation']} in the {row['Department']} 
                    department is {abs(row['Variance %'])}% below market levels. With a current live headcount of <b>{row['Live_HC']}</b> (synced from payroll), 
                    talent retention should be closely monitored by Management.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 6. Analysis View
    elif page == "📉 Market Analysis":
        st.title("Market Disparity by Structural Tier")
        tier_avg = f_df.groupby('Employee Type')['Variance %'].mean().reset_index()
        fig = px.bar(tier_avg, x='Employee Type', y='Variance %', color='Employee Type', title="Avg. Market Variance by Employee Type (%)")
        fig.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Avg. Variance by Department (%)")
        dept_avg = f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %')
        fig2 = px.bar(dept_avg, x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn')
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # 7. Groups View
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        display_cols = ['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']
        
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, emp_type in enumerate(emp_types):
                with tabs[i]:
                    st.dataframe(f_df[f_df['Employee Type'] == emp_type][display_cols], use_container_width=True, hide_index=True)
