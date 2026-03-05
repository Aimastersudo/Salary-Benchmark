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
    /* 🚀 Custom Style for Blue Outsource */
    .outsource-text { color: #3b82f6; font-weight: bold; font-size: 18px; }
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        for d in [core_df, payroll_df, market_df]:
            d.columns = d.columns.str.strip()

        # 🚀 1. Normalization & Cleanup
        def clean_text(text):
            t = str(text).strip().title()
            t = " ".join(t.split())
            t = t.replace("Co-Ordinator", "Coordinator")
            return t

        core_df['Desig_Match'] = core_df['Designation'].apply(clean_text)
        payroll_df['Desig_Match'] = payroll_df['Designation'].apply(clean_text)
        market_df['Desig_Match'] = market_df['Designation'].apply(clean_text)

        # 🚀 2. Split "Mechanical / Production" into separate departments
        # We find rows where dept contains "/" and duplicate them
        core_split = core_df[core_df['Department'].str.contains('/', na=False)].copy()
        if not core_split.empty:
            rows_to_add = []
            for idx, row in core_split.iterrows():
                depts = [d.strip() for d in row['Department'].split('/')]
                for d in depts:
                    new_row = row.copy()
                    new_row['Department'] = d
                    # If HC was 2 for combined, we assume 1 each or we will sync with payroll anyway
                    rows_to_add.append(new_row)
            # Remove original combined rows and add split rows
            core_df = core_df[~core_df['Department'].str.contains('/', na=False)]
            core_df = pd.concat([core_df, pd.DataFrame(rows_to_add)], ignore_index=True)

        # Standardize Payroll Depts
        dept_map = {"HR Administration": "HR", "Information technology": "IT", "Procurement": "Procurment", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_map)

        # Name corrections for mapping
        corrector = {"Asst.Public Relation Offi": "Asst. Public Relation Officer", "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator", "Masons": "Mason"}
        payroll_df['Desig_Match'] = payroll_df['Desig_Match'].replace(corrector)
        market_df['Desig_Match'] = market_df['Desig_Match'].replace(corrector)

        # Market Average Parsing
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

        # Final Merges
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        final_core_df = pd.merge(core_df, market_clean, on='Desig_Match', how='left')
        final_core_df['Market_Avg'] = final_core_df['Market_Avg'].fillna(final_core_df['Your Salary (AED)']).astype(int)
        final_core_df['Variance %'] = ((final_core_df['Your Salary (AED)'] - final_core_df['Market_Avg']) / final_core_df['Market_Avg'] * 100).round(0).astype(int)

        hc_df = payroll_df.groupby(['Desig_Match', 'Department']).size().reset_index(name='Live_HC')
        final_core_df = pd.merge(final_core_df, hc_df, on=['Desig_Match', 'Department'], how='left')
        final_core_df['Live_HC'] = final_core_df['Live_HC'].fillna(0).astype(int)

        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_market_df = pd.merge(payroll_df, market_clean[['Desig_Match', 'Market_Avg']], on='Desig_Match', how='left')
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
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employee Analysis", "📈 Increment Planner", "📁 Structural Groups"])
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
        sel_role = st.selectbox("Select Designation for Competitor Breakdown:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"#### Market Breakdown for {row['Designation']}")
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
        search_emp = st.text_input("Search Name:", "")
        if search_emp: f_emp = f_emp[f_emp['Employee Name'].str.contains(search_emp, case=False, na=False)]
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap (AED)', 'Gap %']], use_container_width=True, hide_index=True)

    elif page == "📈 Increment Planner":
        st.title("📈 Increment Planner")
        target_emp = st.selectbox("Select Employee:", f_emp['Employee Name'].unique() if not f_emp.empty else [])
        if target_emp:
            emp_data = f_emp[f_emp['Employee Name'] == target_emp].iloc[0]
            inc_pct = st.number_input("Enter Increment %", 0.0, 100.0, 5.0, 0.5)
            cur, new = int(emp_data['Salary']), int(emp_data['Salary'] * (1 + inc_pct/100))
            st.metric("New Salary", f"{new} AED", f"+{new-cur}")

    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        for etype in df['Employee Type'].unique():
            with st.expander(f"Tier: {etype}"):
                st.dataframe(f_df[f_df['Employee Type'] == etype][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
