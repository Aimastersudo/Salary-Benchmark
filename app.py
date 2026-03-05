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
    .increment-card { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; }
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

        # Name Corrector logic
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

        # Mason/HR separation logic
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

        # Prepare Core and Payroll Salaries
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').str.strip().astype(float)
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').str.strip().astype(float)

        # Merge for Dashboard
        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')
        final_core_df = pd.merge(core_df, hc_df, on='Designation_Clean', how='left')
        final_core_df = pd.merge(final_core_df, market_clean, on='Designation_Clean', how='left')
        final_core_df['Live_HC'] = final_core_df['Live_HC'].fillna(0).astype(int)
        final_core_df['Calculated Market Salary'] = final_core_df['Calculated Market Salary'].fillna(final_core_df['Your Salary (AED)'])
        final_core_df['Variance %'] = ((final_core_df['Your Salary (AED)'] - final_core_df['Calculated Market Salary']) / final_core_df['Calculated Market Salary'] * 100).round(0).astype(int)

        # Merge for Employee Page
        emp_market_df = pd.merge(payroll_df, market_clean[['Designation_Clean', 'Calculated Market Salary']], on='Designation_Clean', how='left')
        emp_market_df = pd.merge(emp_market_df, core_df[['Designation_Clean', 'Employee Type']], on='Designation_Clean', how='left') # Get Staff/Worker type
        emp_market_df['Calculated Market Salary'] = emp_market_df['Calculated Market Salary'].fillna(emp_market_df['Salary'])
        emp_market_df['Gap (AED)'] = (emp_market_df['Salary'] - emp_market_df['Calculated Market Salary']).fillna(0).astype(int)
        emp_market_df['Gap %'] = ((emp_market_df['Salary'] - emp_market_df['Calculated Market Salary']) / emp_market_df['Calculated Market Salary'] * 100).fillna(0).round(1)

        return final_core_df, emp_market_df, comp_cols
    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None, None

df, emp_df, competitor_columns = load_databases()

if df is not None:
    # 4. SIDEBAR - CHAINED FILTERS
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employee Analysis", "📈 Increment Planner", "📁 Structural Groups"])
        st.markdown("---")
        
        # 🚀 Chained Filtering Logic
        depts = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("1. Select Departments:", depts, default=depts)
        
        filtered_roles = df[df['Department'].isin(selected_depts)]['Designation'].unique()
        selected_roles = st.multiselect("2. Select Designations:", sorted(filtered_roles), default=sorted(filtered_roles))

    # Apply Filter
    f_df = df[(df['Department'].isin(selected_depts)) & (df['Designation'].isin(selected_roles))]
    f_emp = emp_df[(emp_df['Department'].isin(selected_depts)) & (emp_df['Designation'].isin(selected_roles))]

    # -------------------------------------------------------------
    # 📊 EXECUTIVE DASHBOARD
    # -------------------------------------------------------------
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.caption("🟢 Live 3-Pillar Architecture Sync")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total HC", int(f_df['Live_HC'].sum())) 
        avg_v = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty and pd.notna(f_df['Variance %'].mean()) else "0%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps", len(f_df[f_df['Variance %'] < -30]))

        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Deep-Dive Market Analysis")
        sel_role_deep = st.selectbox("Select Designation for Competitor Breakdown:", f_df['Designation'].unique())
        if sel_role_deep:
            row = f_df[f_df['Designation'] == sel_role_deep].iloc[0]
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
    # 👥 PCI EMPLOYEE ANALYSIS
    # -------------------------------------------------------------
    elif page == "👥 PCI Employee Analysis":
        st.title("👥 PCI Employees: Actual Salary vs Market")
        search_emp = st.text_input("Search Employee Name:", "")
        if search_emp:
            f_emp = f_emp[f_emp['Employee Name'].str.contains(search_emp, case=False, na=False)]

        e1, e2, e3 = st.columns(3)
        e1.metric("Selected Employees", len(f_emp))
        e2.metric("Under Market Avg.", len(f_emp[f_emp['Gap (AED)'] < 0]))
        avg_gap = f_emp['Gap (AED)'].mean()
        avg_gap_display = f"{int(avg_gap)} AED" if pd.notna(avg_gap) else "N/A"
        e3.metric("Avg. Gap per Employee", avg_gap_display)

        st.markdown("---")
        display_emp_cols = ['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Calculated Market Salary', 'Gap (AED)', 'Gap %']
        
        def color_gap(val):
            color = '#ef4444' if val < 0 else '#22c55e'
            return f'color: {color}'

        if not f_emp.empty:
            st.dataframe(f_emp[display_emp_cols].style.applymap(color_gap, subset=['Gap (AED)', 'Gap %']), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # 📈 INCREMENT PLANNER (NEW PAGE)
    # -------------------------------------------------------------
    elif page == "📈 Increment Planner":
        st.title("📈 Individual Salary Increment Planner")
        st.caption("Calculate new salary breakdowns based on PCI Staff/Worker rules.")
        
        # 1. Select Employee
        emp_list = emp_df.sort_values('Employee Name')['Employee Name'].unique()
        target_emp_name = st.selectbox("Select Employee to Plan Increment:", emp_list)
        
        if target_emp_name:
            emp_data = emp_df[emp_df['Employee Name'] == target_emp_name].iloc[0]
            
            # 2. Input Increment %
            c1, c2 = st.columns([1, 2])
            with c1:
                inc_pct = st.number_input("Enter Increment Percentage (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
            
            # 3. Calculations
            current_sal = emp_data['Salary']
            new_sal = current_sal * (1 + inc_pct/100)
            diff = new_sal - current_sal
            is_staff = str(emp_data['Employee Type']).lower() == 'staff'
            
            # Breakdown Rules
            basic = new_sal * 0.70
            remaining = new_sal * 0.30
            
            if is_staff:
                food = 0
                other = remaining
                rule_type = "Staff Rule (70/30)"
            else:
                food = 300
                other = remaining - 300 if (remaining - 300) > 0 else 0
                rule_type = "Worker Rule (70/30 + 300 Food)"

            # 4. Display Results
            st.markdown("---")
            res1, res2, res3 = st.columns(3)
            res1.metric("Current Salary", f"{int(current_sal)} AED")
            res2.metric("New Salary", f"{int(new_sal)} AED", delta=f"+{int(diff)}")
            res3.metric("Applied Rule", rule_type)

            st.markdown("#### 📋 New Salary Component Breakdown")
            comp1, comp2, comp3 = st.columns(3)
            with comp1:
                st.markdown(f"""<div class="market-box"><small>Basic Salary (70%)</small><br><b style="font-size:24px; color:#22c55e;">{int(basic)} AED</b></div>""", unsafe_allow_html=True)
            with comp2:
                st.markdown(f"""<div class="market-box"><small>Food Allowance</small><br><b style="font-size:24px; color:#38bdf8;">{int(food)} AED</b></div>""", unsafe_allow_html=True)
            with comp3:
                st.markdown(f"""<div class="market-box"><small>Other Allowance</small><br><b style="font-size:24px; color:#f59e0b;">{int(other)} AED</b></div>""", unsafe_allow_html=True)

            st.info(f"Insight: Increasing {target_emp_name}'s salary by {inc_pct}% will cost the company an additional {int(diff)} AED per month.")

    # -------------------------------------------------------------
    # 📁 STRUCTURAL GROUPS
    # -------------------------------------------------------------
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, etype in enumerate(emp_types):
                with tabs[i]: st.dataframe(f_df[f_df['Employee Type'] == etype][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)
