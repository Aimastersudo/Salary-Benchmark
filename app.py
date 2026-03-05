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

# 3. TRIPLE DATABASE LOADER - With Duplicate Name Corrector & Market Calculator
@st.cache_data
def load_databases():
    try:
        # Load DBs
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        # Clean spaces
        for df in [core_df, payroll_df, market_df]:
            df.columns = df.columns.str.strip()

        core_df['Designation_Clean'] = core_df['Designation'].astype(str).str.strip().str.title()
        payroll_df['Designation_Clean'] = payroll_df['Designation'].astype(str).str.strip().str.title()
        market_df['Designation_Clean'] = market_df['Designation'].astype(str).str.strip().str.title()

        # 🚀 Fix Typographical Errors in Payroll & Market Data
        name_corrector = {
            "Marketing Co-Ordinator": "Marketing Coordinator",
            "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Asst.Security Manager": "Asst. Security Manager",
            "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager",
            "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)",
            "Finance Co-Ordinator": "Finance Coordinator",
            "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support",
            "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator", # 2 spaces fix
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)",
            "Sales Co-Ordinator": "Sales Coordinator",
            "Assistant Engineer (Pro": "Assistant Engineer (Production)",
            "Chief Engineer (Mech)": "Chief Engineer (Mechanical)",
            "Senior Engineer(Technical)": "Senior Engineer (Technical)",
            "Senior Engineer (Technical – Sales)": "Senior Engineer (Technical)",
            "Plant Co-Ordinator": "Plant Coordinator",
            "Asst.Purchase Officer": "Asst. Purchase Officer",
            "Senior Sales And Logistic": "Senior Sales & Logistics",
            "Truck Driver - Bulker": "Truck Driver – Bulker",
            "Truck Driver -  Bulker": "Truck Driver – Bulker",
            "Masons": "Mason"
        }
        payroll_df['Designation_Clean'] = payroll_df['Designation_Clean'].replace(name_corrector)
        market_df['Designation_Clean'] = market_df['Designation_Clean'].replace(name_corrector)

        # 🚀 Duplicate Market Rows for split roles (Mason & HR) so they match the Core Data
        mason_market = market_df[market_df['Designation_Clean'] == 'Mason'].copy()
        if not mason_market.empty:
            mason_prod, mason_mech = mason_market.copy(), mason_market.copy()
            mason_prod['Designation_Clean'], mason_mech['Designation_Clean'] = 'Mason (Production)', 'Mason (Mechanical)'
            market_df = pd.concat([market_df, mason_prod, mason_mech], ignore_index=True)

        hr_market = market_df[market_df['Designation_Clean'] == 'Hr Executive'].copy()
        if not hr_market.empty:
            hr_ext, hr_int = hr_market.copy(), hr_market.copy()
            hr_ext['Designation_Clean'], hr_int['Designation_Clean'] = 'HR Executive (External)', 'HR Executive (Internal)'
            market_df = pd.concat([market_df, hr_ext, hr_int], ignore_index=True)

        # 🚀 Fix Duplicate Designations by separating them based on Department
        # For Masons
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'

        # For HR Executives
        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'

        # Step 1: Headcount Calculation
        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')

        # Step 2: Dynamic Market Salary (Calculating Averages)
        def parse_salary_range(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val == '-' or val == '' or str(val).lower() == 'nan': return np.nan
            if '-' in val:
                parts = [float(p.strip()) for p in val.split('-') if p.strip()]
                return sum(parts) / len(parts) if parts else np.nan
            try: return float(val)
            except: return np.nan

        ignore_cols = ['#', 'Designation', 'Designation_Clean']
        comp_cols = [c for c in market_df.columns if c not in ignore_cols]
        for c in comp_cols:
            market_df[c] = market_df[c].apply(parse_salary_range)
            
        market_df['Calculated Market Salary'] = market_df[comp_cols].mean(axis=1).round(0)
        
        # Drop duplicates to prevent any row multiplying during merge
        market_clean = market_df[['Designation_Clean', 'Calculated Market Salary']].dropna(subset=['Calculated Market Salary']).drop_duplicates(subset=['Designation_Clean'])

        # Step 3: Merge
        merged_df = pd.merge(core_df, hc_df, on='Designation_Clean', how='left')
        merged_df = pd.merge(merged_df, market_clean, on='Designation_Clean', how='left')

        # Data Cleaning & Fallbacks
        merged_df['Your Salary (AED)'] = merged_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float)
        merged_df['Live_HC'] = merged_df['Live_HC'].fillna(0).astype(int)
        
        # If Market Salary is not found in Market_salary.csv, fallback to internal Pioneer salary to avoid graph crash
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
