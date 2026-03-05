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

# 3. TRIPLE DATABASE LOADER - Enhanced Multi-Join Engine
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        # Basic Cleanup
        for d in [core_df, payroll_df, market_df]:
            d.columns = d.columns.str.strip()

        # 🚀 1. Normalization Function (Solves spacing and case issues)
        def clean_text(text):
            t = str(text).strip().title()
            t = " ".join(t.split()) # Remove double spaces
            t = t.replace("Co-Ordinator", "Coordinator")
            t = t.replace("–", "-")
            t = t.replace(" (Mech)", " (Mechanical)")
            t = t.replace(" (Pro)", " (Production)")
            return t

        core_df['Desig_Match'] = core_df['Designation'].apply(clean_text)
        payroll_df['Desig_Match'] = payroll_df['Designation'].apply(clean_text)
        market_df['Desig_Match'] = market_df['Designation'].apply(clean_text)

        # 🚀 2. Payroll-to-Core Mapping (Fixes ID specific character cuts)
        payroll_corrector = {
            "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager",
            "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support",
            "Truck Driver - Bulker": "Truck Driver - Bulker",
            "Truck Driver -  Bulker": "Truck Driver - Bulker",
            "Masons": "Mason", "Weighbridge Operator": "Weigh Bridge Operator"
        }
        payroll_df['Desig_Match'] = payroll_df['Desig_Match'].replace(payroll_corrector)
        market_df['Desig_Match'] = market_df['Desig_Match'].replace(payroll_corrector)

        # 🚀 3. Department Mapping (Standardize filters)
        dept_map = {
            "HR Administration": "HR", "Information technology": "IT",
            "Procurement": "Procurment", "Quality Control": "QC",
            "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores"
        }
        payroll_df['Department'] = payroll_df['Department'].replace(dept_map)

        # Market Salary Logic
        def parse_salary(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val in ['-', '', 'nan', 'None']: return np.nan
            if '-' in val:
                p = [float(i.strip()) for i in val.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(val)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Desig_Match']]
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_salary)
        
        market_df['Market_Avg'] = market_calc[comp_cols].mean(axis=1).round(0)
        market_clean = market_df[['Desig_Match', 'Market_Avg'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Desig_Match'])

        # Core Merge
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        final_core_df = pd.merge(core_df, market_clean, on='Desig_Match', how='left')
        final_core_df['Market_Avg'] = final_core_df['Market_Avg'].fillna(final_core_df['Your Salary (AED)']).astype(int)
        final_core_df['Variance %'] = ((final_core_df['Your Salary (AED)'] - final_core_df['Market_Avg']) / final_core_df['Market_Avg'] * 100).round(0).astype(int)

        # Headcount logic (Matches Dept as well to fix duplicate names across depts)
        hc_df = payroll_df.groupby(['Desig_Match', 'Department']).size().reset_index(name='Live_HC')
        final_core_df = pd.merge(final_core_df, hc_df, on=['Desig_Match', 'Department'], how='left')
        final_core_df['Live_HC'] = final_core_df['Live_HC'].fillna(0).astype(int)

        # Employee Detail Merge
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_market_df = pd.merge(payroll_df, market_clean[['Desig_Match', 'Market_Avg']], on='Desig_Match', how='left')
        emp_market_df['Market_Avg'] = emp_market_df['Market_Avg'].fillna(emp_market_df['Desig_Match'].map(dict(zip(core_df['Desig_Match'], core_df['Your Salary (AED)']))))
        emp_market_df['Market_Avg'] = emp_market_df['Market_Avg'].fillna(emp_market_df['Salary']).astype(int)
        
        emp_market_df['Gap (AED)'] = (emp_market_df['Salary'] - emp_market_df['Market_Avg']).astype(int)
        emp_market_df['Gap %'] = ((emp_market_df['Salary'] - emp_market_df['Market_Avg']) / emp_market_df['Market_Avg'] * 100).round(0).astype(int)
        emp_market_df['Employee Type'] = emp_market_df['Desig_Match'].map(dict(zip(core_df['Desig_Match'], core_df['Employee Type']))).fillna("Worker")

        return final_core_df, emp_market_df, comp_cols
    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None, None

df, emp_df, competitor_columns = load_databases()

if df is not None:
    # Sidebar Filters
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employee Analysis", "📈 Increment Planner", "📁 Structural Groups"])
        st.markdown("---")
        depts_list = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("1. Filter Department:", depts_list, default=depts_list)
        roles_list = sorted(df[df['Department'].isin(selected_depts)]['Designation'].unique())
        selected_roles = st.multiselect("2. Filter Designation:", roles_list, default=roles_list)

    f_df = df[(df['Department'].isin(selected_depts)) & (df['Designation'].isin(selected_roles))]
    f_emp = emp_df[(emp_df['Department'].isin(selected_depts)) & (emp_df['Desig_Match'].isin(f_df['Desig_Match']))]

    # DASHBOARD
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total HC", int(f_df['Live_HC'].sum())) 
        avg_v = f"{int(f_df['Variance %'].mean())}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps", len(f_df[f_df['Variance %'] < -30]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Deep-Dive Market Analysis")
        sel_role = st.selectbox("Select Designation for Competitor Breakdown:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            cols = st.columns(len(competitor_columns))
            for i, comp in enumerate(competitor_columns):
                val = str(row[comp])
                if val in ['nan', '-', '', 'None']: val = "Outsource"
                with cols[i]: st.markdown(f"""<div class="market-box"><small>{comp}</small><br><b>{val}</b></div>""", unsafe_allow_html=True)

    # MARKET ANALYSIS
    elif page == "📉 Market Analysis":
        st.title("📊 In-Depth Market Disparity Analysis")
        col1, col2 = st.columns(2)
        with col1: st.plotly_chart(px.bar(f_df.groupby('Employee Type')['Variance %'].mean().reset_index(), x='Employee Type', y='Variance %', color='Employee Type', title="Variance by Type (%)", template="plotly_dark"), use_container_width=True)
        with col2: st.plotly_chart(px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)", template="plotly_dark"), use_container_width=True)
        st.divider()
        st.subheader("⚠️ Top 10 Critical Salary Gaps")
        gap_df = f_df[f_df['Variance %'] < 0].sort_values('Variance %').head(10)
        if not gap_df.empty: st.plotly_chart(px.bar(gap_df.melt(id_vars=['Designation'], value_vars=['Your Salary (AED)', 'Market_Avg']), x='Designation', y='value', color='variable', barmode='group', title="Pioneer vs Market", template="plotly_dark"), use_container_width=True)

    # EMPLOYEE ANALYSIS
    elif page == "👥 PCI Employee Analysis":
        st.title("👥 PCI Employees: Actual Salary vs Market")
        search_emp = st.text_input("Search Employee Name:", "")
        if search_emp: f_emp = f_emp[f_emp['Employee Name'].str.contains(search_emp, case=False, na=False)]
        e1, e2, e3 = st.columns(3)
        e1.metric("Selected Employees", len(f_emp))
        e2.metric("Under Market Avg.", len(f_emp[f_emp['Gap (AED)'] < 0]))
        avg_gap = f_emp['Gap (AED)'].mean()
        e3.metric("Avg. Gap per Employee", f"{int(avg_gap)} AED" if pd.notna(avg_gap) else "N/A")
        st.markdown("---")
        def color_gap(val): return f"color: {'#ef4444' if val < 0 else '#22c55e'}"
        if not f_emp.empty:
            st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap (AED)', 'Gap %']].style.applymap(color_gap, subset=['Gap (AED)', 'Gap %']), use_container_width=True, hide_index=True)

    # INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("📈 Individual Salary Increment Planner")
        emp_list = emp_df.sort_values('Employee Name')['Employee Name'].unique()
        target_emp = st.selectbox("Select Employee:", emp_list)
        if target_emp:
            emp_data = emp_df[emp_df['Employee Name'] == target_emp].iloc[0]
            inc_pct = st.number_input("Enter Increment %", 0.0, 100.0, 5.0, 0.5)
            cur, new = int(emp_data['Salary']), int(emp_data['Salary'] * (1 + inc_pct/100))
            basic = int(new * 0.7)
            rem = new - basic
            food, other = (300, rem-300 if rem>300 else 0) if str(emp_data['Employee Type']).lower() != 'staff' else (0, rem)
            st.markdown("---")
            r1, r2, r3 = st.columns(3)
            r1.metric("Current", f"{cur} AED")
            r2.metric("New Salary", f"{new} AED", f"+{new-cur}")
            r3.metric("Rule", "Staff (70/30)" if food==0 else "Worker (70/30+300)")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"""<div class="market-box"><small>Basic</small><br><b style="color:#22c55e;">{basic}</b></div>""", unsafe_allow_html=True)
            with c2: st.markdown(f"""<div class="market-box"><small>Food</small><br><b style="color:#38bdf8;">{food}</b></div>""", unsafe_allow_html=True)
            with c3: st.markdown(f"""<div class="market-box"><small>Other</small><br><b style="color:#f59e0b;">{other}</b></div>""", unsafe_allow_html=True)

    # STRUCTURAL GROUPS
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, etype in enumerate(emp_types):
                with tabs[i]: st.dataframe(f_df[f_df['Employee Type'] == etype][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
