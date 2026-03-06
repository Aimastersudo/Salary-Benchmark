import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

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
    .meth-card { background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; height: 100%; border-top: 3px solid #38bdf8; }
    .profile-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; }
    .highlight-red { color: #ef4444; font-weight: bold; }
    .highlight-green { color: #22c55e; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOADER (Safe Rounded Engine)
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')
        meth_db = pd.read_csv("methodology_db.csv", encoding='utf-8-sig') if os.path.exists("methodology_db.csv") else pd.DataFrame()

        for d in [core_df, payroll_df, market_df]: d.columns = d.columns.str.strip()

        def master_clean(text):
            t = str(text).strip().title()
            return " ".join(t.split()).replace("Co-Ordinator", "Coordinator").replace("–", "-").replace(" / ", "/")

        core_df['Match_Key'] = core_df['Designation'].apply(master_clean)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(master_clean)
        market_df['Match_Key'] = market_df['Designation'].apply(master_clean)

        # Salary Parsing
        def parse_v(v):
            if pd.isna(v): return np.nan
            v = str(v).replace(',', '').replace('AED', '').strip()
            if v in ['-', '', 'nan', 'None']: return np.nan
            if '-' in v:
                p = [float(i.strip()) for i in v.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(v)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        m_calc = market_df.copy()
        for c in comp_cols: m_calc[c] = m_calc[c].apply(parse_v)

        market_df['Market_Avg'] = m_calc[comp_cols].mean(axis=1).round(0)
        
        # Tenure Calculation
        payroll_df['DOJ'] = pd.to_datetime(payroll_df['Date of Joining'], errors='coerce')
        today = pd.to_datetime('today')
        payroll_df['Tenure_Y'] = ((today - payroll_df['DOJ']).dt.days / 365.25).fillna(0).astype(int)
        payroll_df['Tenure_M'] = (((today - payroll_df['DOJ']).dt.days % 365.25) / 30.44).fillna(0).astype(int)
        payroll_df['Tenure_Text'] = payroll_df.apply(lambda x: f"{int(x['Tenure_Y'])}y {int(x['Tenure_M'])}m" if pd.notna(x['DOJ']) else "N/A", axis=1)

        # Transparency Metadata
        def get_audit_logic(idx):
            row = m_calc.loc[idx]
            active = [f"{c}: {int(row[c]):,}" for c in comp_cols if pd.notna(row[c]) and row[c] > 0]
            return " + ".join(active), len(active)

        audit_data = [get_audit_logic(i) for i in range(len(m_calc))]
        market_df['Audit_Sum'], market_df['Data_Count'] = zip(*audit_data)
        for c in comp_cols: market_df[f"Mean_{c}"] = m_calc[c]

        m_clean = market_df[['Match_Key', 'Market_Avg', 'Audit_Sum', 'Data_Count'] + [f"Mean_{c}" for c in comp_cols]].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].apply(parse_v).fillna(0).astype(int)
        
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        var_calc = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'].replace(0, np.nan) * 100)
        final_df['Variance %'] = var_calc.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)

        # 200 HC Fix
        hc_d = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_D')
        final_df = pd.merge(final_df, hc_d, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_D'].fillna(0).astype(int)

        payroll_df['Salary'] = payroll_df['Salary'].apply(parse_v).fillna(0).astype(int)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        gap_c = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'].replace(0, np.nan) * 100)
        emp_data['Gap %'] = gap_c.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)
        t_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(t_map).fillna("Worker")
        
        return final_df, emp_data, comp_cols, meth_db
    except Exception as e:
        st.error(f"Error: {e}"); return None, None, None, None

df, emp_df, comp_cols, meth_db = load_databases()

if df is not None:
    with st.sidebar:
        if os.path.exists("PCI_Logo.png"): st.image("PCI_Logo.png", use_container_width=True)
        page = st.radio("STRATEGIC MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner", "🎯 Transparency Lab"])
        st.markdown("---")
        depts = sorted(df['Department'].unique()); sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

    f_df = df[df['Department'].isin(sel_depts)]; f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # 📊 1. EXECUTIVE DASHBOARD
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        mean_v = f_df['Variance %'].mean(); avg_v = f"{int(mean_v) if pd.notna(mean_v) else 0}%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Retention Risks", len(f_df[f_df['Variance %'] < -25]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Role Deep-Dive Analysis")
        sel_role = st.selectbox("Select Role:", sorted(f_df['Designation'].unique()))
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>AI Insight:</b> {row['Designation']} is {abs(int(row['Variance %']))}% {'below' if row['Variance %'] < 0 else 'above'} market benchmark.</div></div>""", unsafe_allow_html=True)
            cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = row.get(f"Mean_{c}")
                with cols[i]:
                    if pd.notna(val): st.markdown(f"""<div class="market-box"><small>{c}</small><br><b style="color:#38bdf8;">{int(val):,}</b></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span style="color:#4b5563;">N/A</span></div>""", unsafe_allow_html=True)

    # 📉 2. MARKET ANALYSIS
    elif page == "📉 Market Analysis":
        st.title("Market Disparity Analysis")
        if not f_df.empty:
            avg_var = int(f_df['Variance %'].mean()); worst_d = f_df.groupby('Department')['Variance %'].mean().idxmin()
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Strategic Summary:</b> Average gap is {abs(avg_var)}%. {worst_d} is the highest risk department.</div></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation')
                fig.add_shape(type='line', x0=0, y0=0, x1=max(f_df['Market_Avg']), y1=max(f_df['Market_Avg']), line=dict(color='white', dash='dash'))
                fig.update_layout(template="plotly_dark"); st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Variance %', y='Department', orientation='h', color='Variance %', template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

    # 👥 3. PCI EMPLOYEES
    elif page == "👥 PCI Employees":
        st.title("PCI Employee Intelligence")
        if not f_emp.empty:
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Staff", len(f_emp)); e2.metric("Loyal (>5y)", len(f_emp[f_emp['Tenure_Y'] >= 5])); e3.metric("Avg Tenure", f"{round(f_emp['Tenure_Y'].mean(),1)}y"); e4.metric("Risk", "High" if len(f_emp[f_emp['Gap %'] < -15]) > 10 else "Stable")
            
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>AI Payroll Health Check:</b> {len(f_emp[f_emp['Gap %'] < -10])} employees are significantly underpaid. Tenure vs Salary Analysis identifies <b>{len(f_emp[(f_emp['Tenure_Y'] >= 3) & (f_emp['Gap %'] < -10)])}</b> loyal personnel (3y+) at risk.</div></div>""", unsafe_allow_html=True)
            
            sel_name = st.selectbox("Search Employee:", sorted(f_emp['Employee Name'].unique()))
            if sel_name:
                ed = f_emp[f_emp['Employee Name'] == sel_name].iloc[0]
                ca, cb = st.columns([1, 2])
                with ca: st.markdown(f"""<div class="profile-card"><h3>{ed['Employee Name']}</h3><p>{ed['Designation']} | {ed['Tenure_Text']}</p><hr><p>Salary: {int(ed['Salary']):,} AED | <span class="highlight-red">Gap: {int(ed['Gap %'])}%</span></p></div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown("#### Market Breakdown")
                    cc = st.columns(len(comp_cols))
                    for i, cn in enumerate(comp_cols):
                        cv = ed.get(f"Mean_{cn}")
                        with cc[i]:
                            if pd.notna(cv): st.markdown(f"""<div class="market-box"><small>{cn}</small><br><b style="color:#38bdf8;">{int(cv):,}</b></div>""", unsafe_allow_html=True)
                            else: st.markdown(f"""<div class="market-box"><small>{cn}</small><br><span style="color:#4b5563;">N/A</span></div>""", unsafe_allow_html=True)
            st.divider(); st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Tenure_Text', 'Salary', 'Market_Avg', 'Gap %']], use_container_width=True, hide_index=True)

    # 🎯 4. TRANSPARENCY LAB
    elif page == "🎯 Transparency Lab":
        st.title("🎯 Transparency Lab: Data Integrity & Methodology")
        roles_list = ["-- Select Designation --"] + sorted(f_df['Designation'].unique().tolist())
        sel_role = st.selectbox("Audit specific calculation:", roles_list)
        
        if sel_role == "-- Select Designation --":
            st.markdown("""<div class="ai-insight-box"><b>Strategic Methodology:</b> documentation of the computational logic used for market benchmarking.</div>""", unsafe_allow_html=True)
            if not meth_db.empty:
                cols_meth = st.columns(2)
                for i, row_meth in meth_db.iterrows():
                    with cols_meth[i % 2]: st.markdown(f"""<div class="meth-card"><span class="meth-header">{row_meth['Step']}. {row_meth['Header']}</span><p>{row_meth['Description']}</p></div><br>""", unsafe_allow_html=True)
        else:
            audit = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="formula-display">Market Average = ( {audit['Audit_Sum']} ) / {audit['Data_Count'] if audit['Data_Count'] > 0 else 1}</div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3); c1.metric("Benchmark", f"{int(audit['Market_Avg']):,} AED"); c2.metric("Confidence", f"{int((int(audit['Data_Count'])/4)*100)}%"); c3.metric("Pioneer Pay", f"{int(audit['Your Salary (AED)']):,} AED")
            st.markdown("### 🔍 Raw Competitor Points")
            chips_cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = audit.get(f"Mean_{c}")
                with chips_cols[i]:
                    if pd.notna(val) and val > 0: st.markdown(f"""<div class="audit-card"><small>{c}</small><br><b style="color: #38bdf8; font-size: 20px;">{int(val):,}</b><br><small style="color: #4ade80;">Validated ✅</small></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="audit-card" style="opacity:0.5;"><small>{c}</small><br><b style="font-size: 20px;">N/A</b><br><small>No Data</small></div>""", unsafe_allow_html=True)
            if len(comp_cols) > 0: st.plotly_chart(px.bar(pd.DataFrame([{"Comp": c, "Salary": audit.get(f"Mean_{c}")} for c in comp_cols if pd.notna(audit.get(f"Mean_{c}"))]), x='Comp', y='Salary', color='Comp', template="plotly_dark"), use_container_width=True)

    # 📈 5. INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("Increment Strategy Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            col1, col2 = st.columns([1, 2])
            with col1:
                pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
                new_s = int(data['Salary'] * (1 + pct/100)); gap_af = int(((new_s - data['Market_Avg']) / data['Market_Avg']) * 100)
                st.metric("New Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}"); st.metric("New Gap", f"{gap_af}%")
            with col2:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=new_s, title={'text': "Market Position"}, gauge={'axis': {'range': [0, data['Market_Avg']*1.5]}, 'bar': {'color': "#3b82f6"}}))
                st.plotly_chart(fig, use_container_width=True)
