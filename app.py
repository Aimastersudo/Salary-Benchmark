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
    .formula-display { background-color: #0f172a; border: 2px solid #1e293b; padding: 30px; border-radius: 15px; text-align: center; font-size: 22px; color: #38bdf8; font-family: 'Courier New', Courier, monospace; margin: 20px 0; border-left: 8px solid #3b82f6; }
    .audit-card { background-color: #1e293b; padding: 15px; border-radius: 10px; border-top: 4px solid #3b82f6; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOADER (The Core Engine)
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

        def parse_v(v):
            if pd.isna(v): return np.nan
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
        
        # Metadata for Transparency Lab
        def get_audit_logic(idx):
            row = m_calc.loc[idx]
            active_parts = []
            count = 0
            for c in comp_cols:
                val = row[c]
                if pd.notna(val) and val > 0:
                    active_parts.append(f"{c}: {int(val):,}")
                    count += 1
            formula = " + ".join(active_parts) if active_parts else "N/A"
            return formula, count

        audit_data = [get_audit_logic(i) for i in range(len(m_calc))]
        market_df['Audit_Sum'], market_df['Data_Count'] = zip(*audit_data)
        for c in comp_cols: market_df[f"Mean_{c}"] = m_calc[c]

        m_clean = market_df[['Match_Key', 'Market_Avg', 'Audit_Sum', 'Data_Count'] + [f"Mean_{c}" for c in comp_cols]].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])
        
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].apply(parse_v).fillna(0).astype(int)
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        
        var_calc = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'].replace(0, np.nan) * 100)
        final_df['Variance %'] = var_calc.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)

        # 200 HC Fix Logic (simplified)
        hc_d = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='Live_HC')
        final_df = pd.merge(final_df, hc_d, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['Live_HC'].fillna(0).astype(int)

        payroll_df['Salary'] = payroll_df['Salary'].apply(parse_v).fillna(0).astype(int)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Engine Load Error: {e}"); return None, None, None

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

    # 🎯 1. TRANSPARENCY LAB
    if page == "🎯 Transparency Lab":
        st.title("🎯 Transparency Lab: Data Audit & Logic")
        sel_role = st.selectbox("Select a Designation to Audit Calculation:", sorted(f_df['Designation'].unique()))
        
        if sel_role:
            audit = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.subheader("1. Mathematical Formula Breakdown")
            
            st.markdown(f"""<div class="formula-display">Market Average = ( {audit['Audit_Sum']} ) / {audit['Data_Count'] if audit['Data_Count'] > 0 else 1}</div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Market Benchmark", f"{int(audit['Market_Avg']):,} AED")
            with c2: 
                conf = (int(audit['Data_Count'])/4)*100
                st.metric("Confidence Level", f"{int(conf)}%", delta="Verified ✅" if conf >= 75 else "Moderate")
            with c3: st.metric("Pioneer Current Pay", f"{int(audit['Your Salary (AED)']):,} AED")

            st.markdown("### 🔍 Raw Data Audit Trail")
            chips_cols = st.columns(len(comp_cols))
            comp_chart_data = []
            for i, c in enumerate(comp_cols):
                val = audit.get(f"Mean_{c}")
                with chips_cols[i]:
                    if pd.notna(val) and val > 0:
                        st.markdown(f"""<div class="audit-card"><small>{c}</small><br><b style="color: #38bdf8; font-size: 20px;">{int(val):,}</b><br><small style="color: #4ade80;">Validated ✅</small></div>""", unsafe_allow_html=True)
                        comp_chart_data.append({"Company": c, "Salary": val})
                    else:
                        st.markdown(f"""<div class="audit-card" style="opacity:0.5;"><small>{c}</small><br><b style="font-size: 20px;">N/A</b><br><small>No Data</small></div>""", unsafe_allow_html=True)

            if comp_chart_data:
                st.markdown("---")
                st.subheader("📊 Competitor Comparison Chart")
                st.plotly_chart(px.bar(pd.DataFrame(comp_chart_data), x='Company', y='Salary', color='Company', text_auto=',.0f', template="plotly_dark"), use_container_width=True)

    # (Other Pages Standard Logic)
    elif page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.dataframe(f_df[['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

    elif page == "📉 Market Analysis":
        st.title("Market Disparity Analysis")
        fig = px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation')
        fig.add_shape(type='line', x0=0, y0=0, x1=max(f_df['Market_Avg']), y1=max(f_df['Market_Avg']), line=dict(color='white', dash='dash'))
        fig.update_layout(template="plotly_dark"); st.plotly_chart(fig, use_container_width=True)

    elif page == "👥 PCI Employees":
        st.title("PCI Employee Intelligence")
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg']], use_container_width=True, hide_index=True)

    elif page == "📈 Increment Planner":
        st.title("Increment Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
            new_s = int(data['Salary'] * (1 + pct/100))
            st.metric("New Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}")
