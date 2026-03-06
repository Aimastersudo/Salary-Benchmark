import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ==========================================
# 1. GLOBAL STYLES & CONFIG
# ==========================================
st.set_page_config(page_title="Pioneer HR | Salary Intelligence", layout="wide")

def apply_custom_css():
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
        .meth-card { background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; height: 100%; border-top: 3px solid #38bdf8; }
        .meth-header { color: #38bdf8; font-weight: bold; font-size: 16px; margin-bottom: 8px; display: block; }
        .profile-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 2. CORE DATA ENGINE
# ==========================================
@st.cache_data
def load_all_data():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')
        meth_db = pd.read_csv("methodology_db.csv", encoding='utf-8-sig') if os.path.exists("methodology_db.csv") else pd.DataFrame()

        for d in [core_df, payroll_df, market_df]: d.columns = d.columns.str.strip()

        def clean_t(t):
            res = str(t).strip().title()
            return " ".join(res.split()).replace("Co-Ordinator", "Coordinator").replace("–", "-").replace(" / ", "/")

        core_df['Match_Key'] = core_df['Designation'].apply(clean_t)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(clean_t)
        market_df['Match_Key'] = market_df['Designation'].apply(clean_t)

        def parse_s(s):
            if pd.isna(s): return np.nan
            s = str(s).replace(',', '').replace('AED', '').strip()
            if s in ['-', '', 'nan', 'None']: return np.nan
            if '-' in s:
                p = [float(i.strip()) for i in s.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(s)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        m_calc = market_df.copy()
        for c in comp_cols: m_calc[c] = m_calc[c].apply(parse_s)
        
        market_df['Market_Avg'] = m_calc[comp_cols].mean(axis=1).round(0)
        
        def get_logic(idx):
            row = m_calc.loc[idx]
            parts = [f"{c}: {int(row[c]):,}" for c in comp_cols if pd.notna(row[c]) and row[c] > 0]
            return " + ".join(parts), len(parts)

        logics = [get_logic(i) for i in range(len(m_calc))]
        market_df['Audit_Sum'], market_df['Data_Count'] = zip(*logics)
        for c in comp_cols: market_df[f"Mean_{c}"] = m_calc[c]

        m_clean = market_df[['Match_Key', 'Market_Avg', 'Audit_Sum', 'Data_Count'] + [f"Mean_{c}" for c in comp_cols]].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].apply(parse_s).fillna(0).astype(int)
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        
        v_calc = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'].replace(0, np.nan) * 100)
        final_df['Variance %'] = v_calc.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)

        hc_dept = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_D')
        final_df = pd.merge(final_df, hc_dept, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_D'].fillna(0).astype(int)

        payroll_df['Salary'] = payroll_df['Salary'].apply(parse_s).fillna(0).astype(int)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        g_calc = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'].replace(0, np.nan) * 100)
        emp_data['Gap %'] = g_calc.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)
        
        return final_df, emp_data, comp_cols, meth_db
    except Exception as e:
        st.error(f"Critical Data Error: {e}")
        return None, None, None, None

# ==========================================
# 3. PAGE FUNCTIONS (Isolated Modules)
# ==========================================

def show_dashboard(df, comp_cols):
    st.title("📊 Strategic Executive Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Roles", len(df))
    c2.metric("Headcount", int(df['Live_HC'].sum()))
    avg_v = int(df['Variance %'].mean())
    c3.metric("Market Gap", f"{avg_v}%", delta_color="inverse")
    c4.metric("Retention Risk", len(df[df['Variance %'] < -25]))
    
    st.dataframe(df[['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🔍 Quick Role Analysis")
    sel = st.selectbox("Select Role:", sorted(df['Designation'].unique()))
    row = df[df['Designation'] == sel].iloc[0]
    st.markdown(f"""<div class="salary-card"><b>Gemini Insight:</b> {sel} is {abs(int(row['Variance %']))}% {'below' if row['Variance %'] < 0 else 'above'} market.</div>""", unsafe_allow_html=True)
    cols = st.columns(len(comp_cols))
    for i, c in enumerate(comp_cols):
        v = row.get(f"Mean_{c}")
        with cols[i]:
            st.markdown(f"""<div class="market-box"><small>{c}</small><br><b style="color:#38bdf8;">{int(v) if pd.notna(v) else 'N/A'}</b></div>""", unsafe_allow_html=True)

def show_market_analysis(df):
    st.title("📉 Market Disparity Analysis")
    fig = px.scatter(df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation')
    fig.add_shape(type='line', x0=0, y0=0, x1=max(df['Market_Avg']), y1=max(df['Market_Avg']), line=dict(color='white', dash='dash'))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = px.bar(df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Variance %', y='Department', orientation='h', color='Variance %', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

def show_employees(emp_df, comp_cols):
    st.title("👥 PCI Employee Intelligence")
    sel_name = st.selectbox("Search Employee:", sorted(emp_df['Employee Name'].unique()))
    ed = emp_df[emp_df['Employee Name'] == sel_name].iloc[0]
    
    ca, cb = st.columns([1, 2])
    with ca:
        st.markdown(f"""<div class="profile-card"><h3>{ed['Employee Name']}</h3><hr><p>Salary: {int(ed['Salary']):,} AED</p><p>Gap: {int(ed['Gap %'])}%</p></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("#### Market Breakdown")
        cc = st.columns(len(comp_cols))
        for i, cn in enumerate(comp_cols):
            cv = ed.get(f"Mean_{cn}")
            with cc[i]:
                st.markdown(f"""<div class="market-box"><small>{cn}</small><br><b>{int(cv) if pd.notna(cv) else 'N/A'}</b></div>""", unsafe_allow_html=True)
    st.divider()
    st.dataframe(emp_df[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap %']], use_container_width=True, hide_index=True)

def show_transparency_lab(df, meth_db, comp_cols):
    st.title("🎯 Transparency Lab: Audit & Logic")
    roles = ["-- Methodology Overview --"] + sorted(df['Designation'].unique().tolist())
    sel = st.selectbox("Audit Selection:", roles)
    
    if sel == "-- Methodology Overview --":
        if not meth_db.empty:
            cols = st.columns(2)
            for i, r in meth_db.iterrows():
                with cols[i % 2]:
                    st.markdown(f"""<div class="meth-card"><span class="meth-header">{r['Step']}. {r['Header']}</span><p>{r['Description']}</p></div><br>""", unsafe_allow_html=True)
    else:
        audit = df[df['Designation'] == sel].iloc[0]
        st.markdown(f"""<div class="formula-display">Market Average = ( {audit['Audit_Sum']} ) / {audit['Data_Count'] if audit['Data_Count'] > 0 else 1}</div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Benchmark", f"{int(audit['Market_Avg']):,} AED")
        c2.metric("Confidence", f"{int((int(audit['Data_Count'])/4)*100)}%")
        c3.metric("Pioneer Pay", f"{int(audit['Your Salary (AED)']):,}")
        
        st.markdown("### 🔍 Verified Competitor Points")
        chips = st.columns(len(comp_cols))
        for i, c in enumerate(comp_cols):
            v = audit.get(f"Mean_{c}")
            with chips[i]:
                if pd.notna(v) and v > 0:
                    st.markdown(f"""<div class="audit-card"><small>{c}</small><br><b>{int(v):,}</b><br><small>Validated ✅</small></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="audit-card" style="opacity:0.5;"><small>{c}</small><br><b>N/A</b></div>""", unsafe_allow_html=True)

def show_planner(emp_df):
    st.title("📈 Increment Simulator")
    target = st.selectbox("Select Staff:", sorted(emp_df['Employee Name'].unique()))
    data = emp_df[emp_df['Employee Name'] == target].iloc[0]
    pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
    new_s = int(data['Salary'] * (1 + pct/100))
    st.metric("New Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}")
    fig = go.Figure(go.Indicator(mode="gauge+number", value=new_s, title={'text': "Market Position"}, gauge={'axis': {'range': [0, data['Market_Avg']*1.5]}, 'bar': {'color': "#3b82f6"}}))
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 4. MAIN NAVIGATION CONTROL
# ==========================================
def main():
    apply_custom_css()
    df, emp_df, comp_cols, meth_db = load_all_data()
    
    if df is not None:
        with st.sidebar:
            if os.path.exists("PCI_Logo.png"): st.image("PCI_Logo.png", use_container_width=True)
            page = st.radio("STRATEGIC MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner", "🎯 Transparency Lab"])
            st.markdown("---")
            all_depts = sorted(df['Department'].unique())
            sel_depts = st.multiselect("Filter Departments:", all_depts, default=all_depts)
        
        f_df = df[df['Department'].isin(sel_depts)]
        f_emp = emp_df[emp_df['Department'].isin(sel_depts)]
        
        if page == "📊 Executive Dashboard": show_dashboard(f_df, comp_cols)
        elif page == "📉 Market Analysis": show_market_analysis(f_df)
        elif page == "👥 PCI Employees": show_employees(f_emp, comp_cols)
        elif page == "📈 Increment Planner": show_planner(f_emp)
        elif page == "🎯 Transparency Lab": show_transparency_lab(f_df, meth_db, comp_cols)

if __name__ == "__main__":
    main()
