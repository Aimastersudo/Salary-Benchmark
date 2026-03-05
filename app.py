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
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    .market-box { background-color: #1e293b; border: 1px solid #475569; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        # Clean column spaces
        core_df.columns = core_df.columns.str.strip()
        payroll_df.columns = payroll_df.columns.str.strip()
        market_df.columns = market_df.columns.str.strip()

        # Designations Cleaning
        core_df['Designation_Clean'] = core_df['Designation'].astype(str).str.strip().str.title()
        payroll_df['Designation_Clean'] = payroll_df['Designation'].astype(str).str.strip().str.title()
        market_df['Designation_Clean'] = market_df['Designation'].astype(str).str.strip().str.title()

        # Name Corrector for Payroll/Market matching
        name_corrector = {
            "Marketing Co-Ordinator": "Marketing Coordinator", "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Asst.Security Manager": "Asst. Security Manager", "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager", "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)",
            "Finance Co-Ordinator": "Finance Coordinator", "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support", "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator", "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)",
            "Sales Co-Ordinator": "Sales Coordinator", "Assistant Engineer (Pro": "Assistant Engineer (Production)",
            "Chief Engineer (Mech)": "Chief Engineer (Mechanical)", "Senior Engineer(Technical)": "Senior Engineer (Technical)",
            "Senior Engineer (Technical – Sales)": "Senior Engineer (Technical)", "Plant Co-Ordinator": "Plant Coordinator",
            "Asst.Purchase Officer": "Asst. Purchase Officer", "Senior Sales And Logistic": "Senior Sales & Logistics",
            "Truck Driver - Bulker": "Truck Driver – Bulker", "Truck Driver -  Bulker": "Truck Driver – Bulker", "Masons": "Mason"
        }
        payroll_df['Designation_Clean'] = payroll_df['Designation_Clean'].replace(name_corrector)
        market_df['Designation_Clean'] = market_df['Designation_Clean'].replace(name_corrector)

        # Mason/HR separation based on Department
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'
        
        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'

        # Market Salary Parsing
        def parse_salary(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val in ['-', '', 'nan', 'None']: return np.nan
            if '-' in val:
                p = [float(i.strip()) for i in val.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(val)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Designation_Clean']]
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_salary)
        market_df['Calculated Market Salary'] = market_calc[comp_cols].mean(axis=1).round(0)
        market_clean = market_df[['Designation_Clean', 'Calculated Market Salary'] + comp_cols].dropna(subset=['Calculated Market Salary']).drop_duplicates(subset=['Designation_Clean'])

        # Prepare Core Data
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float)
        
        # Prepare Payroll Data (Standardize Actual Salary)
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').str.strip().astype(float)

        # Merge for Headcount (Core Level)
        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')
        final_core_df = pd.merge(core_df, hc_df, on='Designation_Clean', how='left')
        final_core_df = pd.merge(final_core_df, market_clean, on='Designation_Clean', how='left')
        final_core_df['Live_HC'] = final_core_df['Live_HC'].fillna(0).astype(int)
        final_core_df['Calculated Market Salary'] = final_core_df['Calculated Market Salary'].fillna(final_core_df['Your Salary (AED)'])
        final_core_df['Variance %'] = ((final_core_df['Your Salary (AED)'] - final_core_df['Calculated Market Salary']) / final_core_df['Calculated Market Salary'] * 100).round(0).astype(int)

        # Merge for Employee Page
        emp_market_df = pd.merge(payroll_df, market_clean[['Designation_Clean', 'Calculated Market Salary']], on='Designation_Clean', how='left')
        emp_market_df['Calculated Market Salary'] = emp_market_df['Calculated Market Salary'].fillna(emp_market_df['Salary']) # Fallback
        emp_market_df['Gap (AED)'] = (emp_market_df['Salary'] - emp_market_df['Calculated Market Salary']).astype(int)
        emp_market_df['Gap %'] = ((emp_market_df['Salary'] - emp_market_df['Calculated Market Salary']) / emp_market_df['Calculated Market Salary'] * 100).round(1)

        return final_core_df, emp_market_df, comp_cols
    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None, None

df, emp_df, competitor_columns = load_databases()

if df is not None:
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employee Analysis", "📁 Structural Groups"])
        st.markdown("---")
        depts = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("Filter Departments:", depts, default=depts)

    # -------------------------------------------------------------
    # 📊 EXECUTIVE DASHBOARD
    # -------------------------------------------------------------
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        f_df = df[df['Department'].isin(selected_depts)]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total HC", int(f_df['Live_HC'].sum())) 
        avg_v = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps", len(f_df[f_df['Variance %'] < -30]))

        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Deep-Dive Market Analysis")
        sel_role = st.selectbox("Select Designation for Competitor Breakdown:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"#### Market Breakdown for {row['Designation']}")
            cols = st.columns(len(competitor_columns))
            for i, comp in enumerate(competitor_columns):
                val = str(row[comp])
                if val in ['nan', '-', '', 'None']: val = "Outsource"
                with cols[i]: st.markdown(f"""<div class="market-box"><small>{comp}</small><br><b>{val}</b></div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 📉 MARKET ANALYSIS
    # -------------------------------------------------------------
    elif page == "📉 Market Analysis":
        st.title("📊 In-Depth Market Disparity Analysis")
        f_df = df[df['Department'].isin(selected_depts)]
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(f_df.groupby('Employee Type')['Variance %'].mean().reset_index(), x='Employee Type', y='Variance %', color='Employee Type', title="Variance by Type (%)", template="plotly_dark"), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)", template="plotly_dark"), use_container_width=True)

        st.divider()
        st.subheader("⚠️ Top 10 Critical Salary Gaps")
        gap_df = f_df[f_df['Variance %'] < 0].sort_values('Variance %').head(10)
        if not gap_df.empty:
            st.plotly_chart(px.bar(gap_df.melt(id_vars=['Designation'], value_vars=['Your Salary (AED)', 'Calculated Market Salary']), x='Designation', y='value', color='variable', barmode='group', title="Pioneer vs Market", template="plotly_dark"), use_container_width=True)

    # -------------------------------------------------------------
    # 👥 PCI EMPLOYEE ANALYSIS (NEW PAGE)
    # -------------------------------------------------------------
    elif page == "👥 PCI Employee Analysis":
        st.title("👥 PCI Employees: Actual Salary vs Market")
        st.caption("Detailed breakdown of individual employee salaries compared to calculated market benchmarks.")
        
        # Filtering
        f_emp = emp_df[emp_df['Department'].isin(selected_depts)]
        search_emp = st.text_input("Search Employee Name or Designation:", "")
        if search_emp:
            f_emp = f_emp[f_emp['Employee Name'].str.contains(search_emp, case=False) | f_emp['Designation'].str.contains(search_emp, case=False)]

        # Summary Metrics for Employees
        e1, e2, e3 = st.columns(3)
        e1.metric("Selected Employees", len(f_emp))
        e2.metric("Under Market Avg.", len(f_emp[f_emp['Gap (AED)'] < 0]))
        e3.metric("Avg. Gap per Employee", f"{int(f_emp['Gap (AED)'].mean())} AED")

        # Employee Table
        st.markdown("---")
        display_emp_cols = ['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Calculated Market Salary', 'Gap (AED)', 'Gap %']
        
        # Color formatting for the table
        def color_gap(val):
            color = '#ef4444' if val < 0 else '#22c55e'
            return f'color: {color}'

        st.dataframe(f_emp[display_emp_cols].style.applymap(color_gap, subset=['Gap (AED)', 'Gap %']), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # 📁 STRUCTURAL GROUPS
    # -------------------------------------------------------------
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        f_df = df[df['Department'].isin(selected_depts)]
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, etype in enumerate(emp_types):
                with tabs[i]: st.dataframe(f_df[f_df['Employee Type'] == etype][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)
