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
    .outsource-text { color: #3b82f6; font-weight: bold; font-size: 18px; }
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER - Robust HC & Market Engine
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        for d in [core_df, payroll_df, market_df]:
            d.columns = d.columns.str.strip()

        # 🚀 1. Normalization
        def clean_text(text):
            t = str(text).strip().title()
            t = " ".join(t.split())
            t = t.replace("Co-Ordinator", "Coordinator")
            return t

        core_df['Desig_Match'] = core_df['Designation'].apply(clean_text)
        payroll_df['Desig_Match'] = payroll_df['Designation'].apply(clean_text)
        market_df['Desig_Match'] = market_df['Designation'].apply(clean_text)

        # 🚀 2. Payroll Corrector (Matches short/broken names in payroll to core)
        corrector = {
            "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager",
            "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support",
            "Masons": "Mason", "Weighbridge Operator": "Weigh Bridge Operator"
        }
        payroll_df['Desig_Match'] = payroll_df['Desig_Match'].replace(corrector)
        market_df['Desig_Match'] = market_df['Desig_Match'].replace(corrector)

        # 🚀 3. Department Splitting (Fixes combined rows)
        core_split = core_df[core_df['Department'].str.contains('/', na=False)].copy()
        if not core_split.empty:
            rows_to_add = []
            for idx, row in core_split.iterrows():
                depts = [d.strip() for d in row['Department'].split('/')]
                for d in depts:
                    new_row = row.copy()
                    new_row['Department'] = d
                    rows_to_add.append(new_row)
            core_df = core_df[~core_df['Department'].str.contains('/', na=False)]
            core_df = pd.concat([core_df, pd.DataFrame(rows_to_add)], ignore_index=True)

        # 🚀 4. Market Salary Calculation
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

        # Final Dashboard Data Preparation
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        
        # Merge Market Average
        final_core_df = pd.merge(core_df, market_clean, on='Desig_Match', how='left')
        final_core_df['Market_Avg'] = final_core_df['Market_Avg'].fillna(final_core_df['Your Salary (AED)']).astype(int)
        final_core_df['Variance %'] = ((final_core_df['Your Salary (AED)'] - final_core_df['Market_Avg']) / final_core_df['Market_Avg'] * 100).round(0).astype(int)

        # 🚀 5. SMART HEADCOUNT LOGIC (Fixes 0 HC)
        # First attempt: Match by Designation AND Department
        hc_by_dept = payroll_df.groupby(['Desig_Match', 'Department']).size().reset_index(name='HC_Dept')
        final_core_df = pd.merge(final_core_df, hc_by_dept, on=['Desig_Match', 'Department'], how='left')
        
        # Second attempt: For remaining 0s, match by Designation ONLY (Total HC for that role)
        hc_by_role = payroll_df.groupby('Desig_Match').size().reset_index(name='HC_Role')
        final_core_df = pd.merge(final_core_df, hc_by_role, on='Desig_Match', how='left')
        
        # Final HC Decision: Use Dept-specific HC if available, else use Role HC (divided by dept instances if necessary)
        # But most simply: Use Dept match first, if NaN use 0.
        final_core_df['Live_HC'] = final_core_df['HC_Dept'].fillna(0).astype(int)
        
        # Special fix for Masons/Foremen if still 0 after dept match:
        final_core_df.loc[final_core_df['Live_HC'] == 0, 'Live_HC'] = final_core_df['HC_Role'].fillna(0).astype(int)

        # Process Employee Table Data
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_market_df = pd.merge(payroll_df, market_clean[['Desig_Match', 'Market_Avg']], on='Desig_Match', how='left')
        emp_market_df['Market_Avg'] = emp_market_df['Market_Avg'].fillna(emp_market_df['Salary']).astype(int)
        emp_market_df['Gap (AED)'] = (emp_market_df['Salary'] - emp_market_df['Market_Avg']).astype(int)
        emp_market_df['Gap %'] = ((emp_market_df['Salary'] - emp_market_df['Market_Avg']) / emp_market_df['Market_Avg'] * 100).round(0).astype(int)

        return final_core_df, emp_market_df, comp_cols
    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None, None

df, emp_df, competitor_columns = load_databases()

if df is not None:
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employee Analysis", "📈 Increment Planner"])
        st.markdown("---")
        depts_list = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("Filter Department:", depts_list, default=depts_list)

    f_df = df[df['Department'].isin(selected_depts)]
    f_emp = emp_df[emp_df['Department'].isin(selected_depts)]

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
        sel_role = st.selectbox("Select Designation:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            cols = st.columns(len(competitor_columns))
            for i, comp in enumerate(competitor_columns):
                val = str(row[comp])
                with cols[i]:
                    if val in ['nan', '-', '', 'None']:
                        st.markdown(f"""<div class="market-box"><small>{comp}</small><br><span class="outsource-text">Outsource</span></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="market-box"><small>{comp}</small><br><span class="value-text">{val}</span></div>""", unsafe_allow_html=True)

    elif page == "📉 Market Analysis":
        st.title("📊 Market Disparity Analysis")
        col1, col2 = st.columns(2)
        with col1: st.plotly_chart(px.bar(f_df.groupby('Employee Type')['Variance %'].mean().reset_index(), x='Employee Type', y='Variance %', color='Employee Type', title="Variance by Type (%)", template="plotly_dark"), use_container_width=True)
        with col2: st.plotly_chart(px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)", template="plotly_dark"), use_container_width=True)

    elif page == "👥 PCI Employee Analysis":
        st.title("👥 PCI Employees vs Market")
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap (AED)', 'Gap %']], use_container_width=True, hide_index=True)

    elif page == "📈 Increment Planner":
        st.title("📈 Increment Planner")
        target_emp = st.selectbox("Select Employee:", f_emp['Employee Name'].unique() if not f_emp.empty else [])
        if target_emp:
            emp_data = f_emp[f_emp['Employee Name'] == target_emp].iloc[0]
            inc_pct = st.number_input("Enter Increment %", 0.0, 100.0, 5.0, 0.5)
            cur, new = int(emp_data['Salary']), int(emp_data['Salary'] * (1 + inc_pct/100))
            st.metric("New Salary", f"{new} AED", f"+{new-cur}")
            
            basic = int(new * 0.7)
            rem = new - basic
            # Smart Rule detection
            is_staff = "Staff" in str(emp_data.get('Employee Type', 'Worker'))
            food = 0 if is_staff else 300
            other = rem - food if (rem - food) > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"""<div class="market-box"><small>Basic (70%)</small><br><span class="value-text">{basic}</span></div>""", unsafe_allow_html=True)
            with c2: st.markdown(f"""<div class="market-box"><small>Food</small><br><span class="value-text">{food}</span></div>""", unsafe_allow_html=True)
            with c3: st.markdown(f"""<div class="market-box"><small>Other</small><br><span class="value-text">{other}</span></div>""", unsafe_allow_html=True)
