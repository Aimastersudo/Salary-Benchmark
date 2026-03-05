import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    .market-box { background-color: #1e293b; border: 1px solid #475569; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .note-box { background-color: rgba(245, 158, 11, 0.1); border-left: 5px solid #f59e0b; padding: 15px; margin: 10px 0; border-radius: 5px; color: #fbbf24; }
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    .highlight-red { color: #ef4444; font-weight: bold; }
    .highlight-green { color: #22c55e; font-weight: bold; }
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

        # Normalization
        def master_clean(text):
            t = str(text).strip().title()
            t = " ".join(t.split())
            t = t.replace("Co-Ordinator", "Coordinator")
            t = t.replace("–", "-").replace(" / ", "/")
            return t

        core_df['Match_Key'] = core_df['Designation'].apply(master_clean)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(master_clean)
        market_df['Match_Key'] = market_df['Designation'].apply(master_clean)

        # Bridge
        bridge = {
            "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager",
            "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support",
            "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)",
            "Assistant Engineer (Pro": "Assistant Engineer (Production)",
            "Chief Engineer (Mech)": "Chief Engineer (Mechanical)",
            "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)",
            "Senior Engineer(Technical)": "Senior Engineer (Technical)",
            "Finance Co-Ordinator": "Finance Coordinator",
            "Marketing Co-Ordinator": "Marketing Coordinator",
            "Plant Co-Ordinator": "Plant Coordinator",
            "Sales Co-Ordinator": "Sales Coordinator",
            "Senior Sales And Logistic": "Senior Sales & Logistics",
            "Asst.Security Manager": "Asst. Security Manager",
            "Asst.Purchase Officer": "Asst. Purchase Officer",
            "Truck Driver - Bulker": "Truck Driver - Bulker",
            "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)"
        }
        payroll_df['Match_Key'] = payroll_df['Match_Key'].replace(bridge)

        # Dept standardization
        dept_fix = {"HR Administration": "HR", "Information technology": "IT", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores", "Procurment": "Procurement"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix)
        core_df['Department'] = core_df['Department'].replace(dept_fix)

        # Tenure Calculation
        payroll_df['DOJ'] = pd.to_datetime(payroll_df['Date of Joining'], errors='coerce')
        today = pd.to_datetime('today')
        payroll_df['Tenure_Days'] = (today - payroll_df['DOJ']).dt.days
        payroll_df['Tenure_Y'] = (payroll_df['Tenure_Days'] / 365.25).fillna(0).astype(int)
        payroll_df['Tenure_M'] = ((payroll_df['Tenure_Days'] % 365.25) / 30.44).fillna(0).astype(int)
        payroll_df['Tenure_Text'] = payroll_df.apply(lambda x: f"{x['Tenure_Y']}y {x['Tenure_M']}m" if pd.notna(x['DOJ']) else "N/A", axis=1)

        # Split Depts
        rows = []
        for _, row in core_df.iterrows():
            dv = str(row['Department'])
            if '/' in dv:
                for sd in [s.strip() for s in dv.split('/')]:
                    nr = row.copy(); nr['Department'] = sd; rows.append(nr)
            else: rows.append(row)
        core_df = pd.DataFrame(rows)

        # Market Parsing
        def parse_v(v):
            v = str(v).replace(',', '').replace('AED', '').strip()
            if v in ['-', '', 'nan']: return np.nan
            if '-' in v:
                p = [float(i.strip()) for i in v.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(v)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_v)
        market_df['Market_Avg'] = market_calc[comp_cols].mean(axis=1).round(0)
        m_clean = market_df[['Match_Key', 'Market_Avg'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        # Core Merge
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        final_df['Variance %'] = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'] * 100).round(0).astype(int)

        # 200 HC Fix
        hc_d = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_D')
        final_df = pd.merge(final_df, hc_d, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_D'].fillna(0).astype(int)
        alloc = final_df.groupby('Match_Key')['Live_HC'].sum().reset_index(name='A')
        act = payroll_df.groupby('Match_Key').size().reset_index(name='Actual')
        comp = pd.merge(act, alloc, on='Match_Key', how='left')
        res = comp[comp['Actual'] > comp['A'].fillna(0)]
        for _, r in res.iterrows():
            key = r['Match_Key']; rem = int(r['Actual'] - r['A'])
            idx = final_df[final_df['Match_Key'] == key].index
            if len(idx) > 0: final_df.at[idx[0], 'Live_HC'] += rem

        # Emp Merge
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        emp_data['Gap (AED)'] = (emp_data['Salary'] - emp_data['Market_Avg']).astype(int)
        emp_data['Gap %'] = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'] * 100).fillna(0).round(0).astype(int)
        type_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(type_map).fillna("Worker")

        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
    # Sidebar
    with st.sidebar:
        l_path = None
        for ex in ["jpg", "png", "jpeg"]:
            if os.path.exists(f"PCI_Logo.{ex}"): l_path = f"PCI_Logo.{ex}"; break
        if l_path: st.image(l_path, use_container_width=True)
        else: st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PCI+HR", use_container_width=True)
        page = st.radio("MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner"])
        st.markdown("---")
        depts = sorted(df['Department'].dropna().unique())
        sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

    f_df = df[df['Department'].isin(sel_depts)]
    f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # (Executive Dashboard & Market Analysis stay as before)
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        c3.metric("Avg. Market Gap", f"{int(f_df['Variance %'].mean()) if not f_df.empty else 0}%", delta_color="inverse")
        c4.metric("Critical Gaps", len(f_df[f_df['Variance %'] < -30]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        st.markdown("---")
        st.subheader("🔍 Role Deep-Dive")
        sel_role = st.selectbox("Select Role:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>AI Insight:</b> {row['Designation']} is {abs(row['Variance %'])}% {'below' if row['Variance %'] < 0 else 'above'} market.</div></div>""", unsafe_allow_html=True)
            cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = str(row.get(c, "nan"))
                with cols[i]:
                    if val in ['nan', '-', 'None']: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span class="outsource-text">Outsource</span></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span class="value-text">{val}</span></div>""", unsafe_allow_html=True)

    elif page == "📉 Market Analysis":
        st.title("📊 Detailed Market Disparity Analysis")
        if not f_df.empty:
            avg_v = int(f_df['Variance %'].mean())
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Market Summary:</b> Average disparity is {avg_v}%. Critical talent risk identified in {f_df.groupby('Department')['Variance %'].mean().idxmin()} department.</div></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', title="Positioning Matrix", template="plotly_dark"), use_container_width=True)
            with c2: st.plotly_chart(px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Variance %', y='Department', orientation='h', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)", template="plotly_dark"), use_container_width=True)

    # 👥 PCI EMPLOYEES (WITH TENURE)
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        
        if not f_emp.empty:
            # 1. AI Metrics
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Selected Employees", len(f_emp))
            e2.metric("Loyal Staff (>5y)", len(f_emp[f_emp['Tenure_Y'] >= 5]))
            e3.metric("Avg. Tenure", f"{round(f_emp['Tenure_Y'].mean(), 1)} Years")
            e4.metric("Retention Risk", "High" if len(f_emp[f_emp['Gap %'] < -15]) > 10 else "Moderate")

            # 2. Gemini AI Insight with Tenure
            loyal_underpaid = f_emp[(f_emp['Tenure_Y'] >= 3) & (f_emp['Gap %'] < -10)]
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini Payroll Health Check:</b> There are <b>{len(loyal_underpaid)}</b> loyal employees (3+ years) who are paid 10%+ below market average. 
                    Retention risk for long-term staff is <b>{'Critical' if len(loyal_underpaid) > 5 else 'Significant'}</b>. 
                    Prioritize tenure-based adjustments for these key personnel.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 3. Employee Profile Quick-View
            st.subheader("🔍 Employee Spotlight")
            selected_name = st.selectbox("Search Employee:", sorted(f_emp['Employee Name'].unique()))
            if selected_name:
                edata = f_emp[f_emp['Employee Name'] == selected_name].iloc[0]
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown(f"""
                    <div style="background-color:#1f2937; padding:20px; border-radius:15px; border: 1px solid #3b82f6;">
                        <h3 style="margin:0;">{edata['Employee Name']}</h3>
                        <p style="color:#94a3b8; margin-bottom:10px;">ID: {edata['Employee ID']} | {edata['Designation']}</p>
                        <hr style="border:0.5px solid #374151;">
                        <p><b>Salary:</b> {int(edata['Salary'])} AED</p>
                        <p><b>Tenure:</b> {edata['Tenure_Text']}</p>
                        <p><b>Status:</b> <span class="{'highlight-red' if edata['Gap %'] < 0 else 'highlight-green'}">{'Underpaid' if edata['Gap %'] < 0 else 'Above Market'} ({abs(edata['Gap %'])}%)</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown("#### Competitor Breakdown for this Role")
                    c_cols = st.columns(len(comp_cols))
                    for i, cname in enumerate(comp_cols):
                        c_val = str(edata.get(cname, "nan"))
                        with c_cols[i]:
                            if c_val in ['nan', '-', 'None']: st.markdown(f"""<div class="market-box"><small>{cname}</small><br><span style="color:#3b82f6;">Outsource</span></div>""", unsafe_allow_html=True)
                            else: st.markdown(f"""<div class="market-box"><small>{cname}</small><br><b style="color:#38bdf8;">{c_val}</b></div>""", unsafe_allow_html=True)

            st.divider()

            # 4. Table
            st.subheader("📊 Full Employee Database")
            search_box = st.text_input("Filter by Name or ID:", "")
            display_df = f_emp.copy()
            if search_box: display_df = display_df[display_df['Employee Name'].str.contains(search_box, case=False) | display_df['Employee ID'].astype(str).str.contains(search_box)]
            
            def style_gap(val): return f'color: {"#ef4444" if val < 0 else "#22c55e"}; font-weight: bold'
            st.dataframe(display_df[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Tenure_Text', 'Salary', 'Market_Avg', 'Gap %']].style.applymap(style_gap, subset=['Gap %']), use_container_width=True, hide_index=True)

    elif page == "📈 Increment Planner":
        st.title("📈 Salary Increment Simulator")
        target = st.selectbox("Select Employee:", f_emp['Employee Name'].unique() if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Enter Increment %", 0.0, 100.0, 5.0, 0.5)
            curr = int(data['Salary']); new_s = int(curr * (1 + pct/100))
            st.metric("New Salary", f"{new_s} AED", f"+{new_s - curr}")
            basic = int(new_s * 0.7); rem = new_s - basic
            food = 0 if "Staff" in str(data['Employee Type']) else 300
            st.markdown(f"""<div class="market-box">Basic: {basic} | Food: {food} | Other: {max(0, rem-food)}</div>""", unsafe_allow_html=True)
