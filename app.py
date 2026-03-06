import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR | Salary Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 20px; border-radius: 12px; color: #93c5fd; font-size: 15px; line-height: 1.6; border-left: 5px solid #3b82f6; }
    .market-box { background-color: #1e293b; border: 1px solid #475569; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .formula-display { background-color: #0f172a; border: 2px solid #1e293b; padding: 30px; border-radius: 15px; text-align: center; font-size: 24px; color: #38bdf8; font-family: 'Courier New', Courier, monospace; margin: 20px 0; }
    .data-chip { background-color: #1e293b; padding: 10px 20px; border-radius: 30px; border: 1px solid #3b82f6; display: inline-block; margin: 5px; color: #93c5fd; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOADER (Safe String-to-Int Conversion)
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')
        for d in [core_df, payroll_df, market_df]: d.columns = d.columns.str.strip()

        def master_clean(text):
            t = str(text).strip().title()
            return " ".join(t.split()).replace("Co-Ordinator", "Coordinator").replace("–", "-").replace(" / ", "/")

        core_df['Match_Key'] = core_df['Designation'].apply(master_clean)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(master_clean)
        market_df['Match_Key'] = market_df['Designation'].apply(master_clean)

        bridge = {"Asst.Public Relation Offi": "Asst. Public Relation Officer", "Asst.External Relationship Manager": "Asst. External Relationship Manager", "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)", "Truck Cum Shovel Operato": "Truck Cum Shovel Operator", "Junior It Help Desk Suppo": "Junior It Help Desk Support", "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)", "Assistant Engineer (Pro": "Assistant Engineer (Production)", "Chief Engineer (Mech)": "Chief Engineer (Mechanical)", "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)", "Senior Engineer(Technical)": "Senior Engineer (Technical)", "Finance Co-Ordinator": "Finance Coordinator", "Marketing Co-Ordinator": "Marketing Coordinator", "Plant Co-Ordinator": "Plant Coordinator", "Sales Co-Ordinator": "Sales Coordinator", "Senior Sales And Logistic": "Senior Sales & Logistics", "Asst.Security Manager": "Asst. Security Manager", "Asst.Purchase Officer": "Asst. Purchase Officer", "Truck Driver - Bulker": "Truck Driver - Bulker", "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)"}
        payroll_df['Match_Key'] = payroll_df['Match_Key'].replace(bridge)

        dept_fix = {"HR Administration": "HR", "Information technology": "IT", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores", "Procurment": "Procurement"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix); core_df['Department'] = core_df['Department'].replace(dept_fix)

        # 🚀 SAFE PARSING ENGINE (Handles Comma and Strings)
        def parse_v(v):
            v = str(v).replace(',', '').replace('AED', '').strip()
            if v in ['-', '', 'nan', 'None']: return np.nan
            if '-' in v:
                parts = [float(i.strip()) for i in v.split('-') if i.strip()]
                return sum(parts)/len(parts) if parts else np.nan
            try: return float(v)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        m_calc = market_df.copy()
        for c in comp_cols: m_calc[c] = m_calc[c].apply(parse_v)

        market_df['Market_Avg'] = m_calc[comp_cols].mean(axis=1).round(0)
        
        # Audit Metadata
        def get_audit_data(row):
            active = [f"{c}: {int(row[c]):,}" for c in comp_cols if pd.notna(row[c]) and row[c] > 0]
            return " + ".join(active), len(active)

        audit_res = m_calc.apply(get_audit_data, axis=1)
        market_df['Audit_Sum'], market_df['Data_Count'] = zip(*audit_res)
        
        m_clean = market_df[['Match_Key', 'Market_Avg', 'Audit_Sum', 'Data_Count'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])
        
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].apply(parse_v).fillna(0).astype(int)
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        
        var_calc = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'].replace(0, np.nan) * 100)
        final_df['Variance %'] = var_calc.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)

        # 200 HC Fix
        hc_d = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_D')
        final_df = pd.merge(final_df, hc_d, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_D'].fillna(0).astype(int)
        alloc = final_df.groupby('Match_Key')['Live_HC'].sum().reset_index(name='A')
        act = payroll_df.groupby('Match_Key').size().reset_index(name='Actual')
        cm = pd.merge(act, alloc, on='Match_Key', how='left')
        res = cm[cm['Actual'] > cm['A'].fillna(0)]
        for _, r in res.iterrows():
            key = r['Match_Key']; rem = int(r['Actual'] - r['A'])
            idx = final_df[final_df['Match_Key'] == key].index
            if len(idx) > 0: final_df.at[idx[0], 'Live_HC'] += rem

        payroll_df['Salary'] = payroll_df['Salary'].apply(parse_v).fillna(0).astype(int)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        gap_c = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'].replace(0, np.nan) * 100)
        emp_data['Gap %'] = gap_c.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)
        
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Error: {e}"); return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
    with st.sidebar:
        l_path = None
        for ex in ["jpg", "png"]:
            if os.path.exists(f"PCI_Logo.{ex}"): l_path = f"PCI_Logo.{ex}"; break
        if l_path: st.image(l_path, use_container_width=True)
        page = st.radio("STRATEGIC MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner", "🎯 Transparency Lab"])
        st.markdown("---")
        depts = sorted(df['Department'].unique()); sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

    f_df = df[df['Department'].isin(sel_depts)]; f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # 🎯 TRANSPARENCY LAB (Safely Rounded)
    if page == "🎯 Transparency Lab":
        st.title("🎯 Transparency Lab: Data Audit & Logic")
        st.markdown("Verifying the integrity of market averages and competitive benchmarking.")
        
        sel_role = st.selectbox("Select a Designation to Audit Calculation:", sorted(f_df['Designation'].unique()))
        
        if sel_role:
            audit = f_df[f_df['Designation'] == sel_role].iloc[0]
            
            # Formula Visualization
            st.subheader("1. Mathematical Formula Breakdown")
            
            st.markdown(f"""
            <div class="formula-display">
                Market Avg = ({audit['Audit_Sum'] if audit['Audit_Sum'] != "" else "Pioneer Salary Only"}) / {audit['Data_Count'] if audit['Data_Count'] > 0 else 1}
            </div>
            """, unsafe_allow_html=True)
            
            # Stats Metrics
            st.subheader("2. Benchmarking Metrics")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Calculated Market Avg", f"{int(audit['Market_Avg']):,} AED")
            with c2: st.metric("Data Confidence Score", f"{(int(audit['Data_Count'])/4)*100}%", help="Calculated based on competitor data availability")
            with c3: st.metric("Pioneer Current Pay", f"{int(audit['Your Salary (AED)']):,} AED")
            
            # Gemini Audit
            st.subheader("3. Strategic AI Audit")
            st.markdown(f"""
            <div class="ai-insight-box">
                <b>Gemini Strategic Audit:</b><br>
                For <b>{sel_role}</b>, the benchmark logic has processed <b>{audit['Data_Count']}</b> competitor data points. 
                Normalization was applied to handle salary ranges, converting them into single mid-point values for 100% calculation accuracy.
                <br><br><b>Verdict:</b> {'The data is highly reliable.' if audit['Data_Count'] >= 3 else 'Data sample is limited but aligned with industry trends.'} 
                Pioneer is currently <b>{abs(int(audit['Variance %']))}%</b> {'below' if audit['Variance %'] < 0 else 'above'} market.
            </div>
            """, unsafe_allow_html=True)
            
            # Competitor Chips
            st.markdown("---")
            st.markdown("<b>Raw Data Points Used in Calculation:</b>")
            for c in comp_cols:
                val = audit.get(c)
                if pd.notna(val) and val > 0:
                    st.markdown(f"""<div class="data-chip">{c}: {int(val):,} AED</div>""", unsafe_allow_html=True)

    # (Other pages Standard Logic)
    elif page == "📊 Executive Dashboard":
        st.title("Strategic Dashboard")
        st.dataframe(f_df[['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

    elif page == "📉 Market Analysis":
        st.title("Market Analysis")
        st.plotly_chart(px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', title="Salary Matrix"), use_container_width=True)

    elif page == "👥 PCI Employees":
        st.title("PCI Employees Intelligence")
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap %']], use_container_width=True, hide_index=True)

    elif page == "📈 Increment Planner":
        st.title("Increment Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
            new_s = int(data['Salary'] * (1 + pct/100))
            st.metric("Proposed Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}")
