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
    .note-box { background-color: rgba(245, 158, 11, 0.1); border-left: 5px solid #f59e0b; padding: 15px; margin: 10px 0; border-radius: 5px; color: #fbbf24; }
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    .highlight-red { color: #ef4444; font-weight: bold; }
    .highlight-green { color: #22c55e; font-weight: bold; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-red { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .badge-green { background-color: rgba(34, 197, 94, 0.2); color: #22c55e; }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER (200 HC & Tenure Engine)
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')
        for d in [core_df, payroll_df, market_df]: d.columns = d.columns.str.strip()

        def master_clean(text):
            t = str(text).strip().title()
            t = " ".join(t.split())
            return t.replace("Co-Ordinator", "Coordinator").replace("–", "-").replace(" / ", "/")

        core_df['Match_Key'] = core_df['Designation'].apply(master_clean)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(master_clean)
        market_df['Match_Key'] = market_df['Designation'].apply(master_clean)

        bridge = {"Asst.Public Relation Offi": "Asst. Public Relation Officer", "Asst.External Relationship Manager": "Asst. External Relationship Manager", "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)", "Truck Cum Shovel Operato": "Truck Cum Shovel Operator", "Junior It Help Desk Suppo": "Junior It Help Desk Support", "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)", "Assistant Engineer (Pro": "Assistant Engineer (Production)", "Chief Engineer (Mech)": "Chief Engineer (Mechanical)", "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)", "Senior Engineer(Technical)": "Senior Engineer (Technical)", "Finance Co-Ordinator": "Finance Coordinator", "Marketing Co-Ordinator": "Marketing Coordinator", "Plant Co-Ordinator": "Plant Coordinator", "Sales Co-Ordinator": "Sales Coordinator", "Senior Sales And Logistic": "Senior Sales & Logistics", "Asst.Security Manager": "Asst. Security Manager", "Asst.Purchase Officer": "Asst. Purchase Officer", "Truck Driver - Bulker": "Truck Driver - Bulker", "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)"}
        payroll_df['Match_Key'] = payroll_df['Match_Key'].replace(bridge)

        dept_fix = {"HR Administration": "HR", "Information technology": "IT", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores", "Procurment": "Procurement", "Procurement": "Procurement"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix)
        core_df['Department'] = core_df['Department'].replace(dept_fix)

        # Tenure Logic
        payroll_df['DOJ'] = pd.to_datetime(payroll_df['Date of Joining'], errors='coerce')
        today = pd.to_datetime('today')
        payroll_df['Tenure_Days'] = (today - payroll_df['DOJ']).dt.days
        payroll_df['Tenure_Y'] = (payroll_df['Tenure_Days'] / 365.25).fillna(0).astype(int)
        payroll_df['Tenure_M'] = ((payroll_df['Tenure_Days'] % 365.25) / 30.44).fillna(0).astype(int)
        payroll_df['Tenure_Text'] = payroll_df.apply(lambda x: f"{x['Tenure_Y']}y {x['Tenure_M']}m" if pd.notna(x['DOJ']) else "N/A", axis=1)

        # Split Slash Depts
        rows = []
        for _, row in core_df.iterrows():
            dv = str(row['Department'])
            if '/' in dv:
                for sd in [s.strip() for s in dv.split('/')]:
                    nr = row.copy(); nr['Department'] = sd; rows.append(nr)
            else: rows.append(row)
        core_df = pd.DataFrame(rows)

        # Market Calcs
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
        cm = pd.merge(act, alloc, on='Match_Key', how='left')
        res = cm[cm['Actual'] > cm['A'].fillna(0)]
        for _, r in res.iterrows():
            key = r['Match_Key']; rem = int(r['Actual'] - r['A'])
            idx = final_df[final_df['Match_Key'] == key].index
            if len(idx) > 0: final_df.at[idx[0], 'Live_HC'] += rem

        # Emp Data
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        emp_data['Gap %'] = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'] * 100).fillna(0).round(0).astype(int)
        emp_data['Gap (AED)'] = (emp_data['Salary'] - emp_data['Market_Avg']).astype(int)
        t_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(t_map).fillna("Worker")
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Error: {e}"); return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
    # Sidebar
    with st.sidebar:
        l_path = None
        for ex in ["jpg", "png", "jpeg"]:
            if os.path.exists(f"PCI_Logo.{ex}"): l_path = f"PCI_Logo.{ex}"; break
        if l_path: st.image(l_path, use_container_width=True)
        page = st.radio("MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner"])
        depts = sorted(df['Department'].dropna().unique())
        sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

    f_df = df[df['Department'].isin(sel_depts)]
    f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # 1. EXECUTIVE DASHBOARD
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        if "Truck Driver - Bulker" in f_df['Designation'].values:
            st.markdown("""<div class="note-box"><b>📌 Note:</b> Bulker Driver salaries are trip-driven; basic pay differences are minimal.</div>""", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        c3.metric("Avg. Market Gap", f"{int(f_df['Variance %'].mean()) if not f_df.empty else 0}%", delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Deep-Dive Role Analysis")
        sel_role = st.selectbox("Select a Role:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini HR Analysis:</b> Current pay for {row['Designation']} in the {row['Department']} department is {abs(row['Variance %'])}% {'below' if row['Variance %'] < 0 else 'above'} market avg. Risk: {'High' if row['Variance %'] < -20 else 'Moderate'}.</div></div>""", unsafe_allow_html=True)
            cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = str(row.get(c, "nan"))
                with cols[i]:
                    if val in ['nan', '-', 'None']: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span class="outsource-text">Outsource</span></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span class="value-text">{val}</span></div>""", unsafe_allow_html=True)

    # 2. MARKET ANALYSIS
    elif page == "📉 Market Analysis":
        st.title("📊 Detailed Market Disparity Analysis")
        if not f_df.empty:
            avg_v = int(f_df['Variance %'].mean()); worst_d = f_df.groupby('Department')['Variance %'].mean().idxmin()
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Market Intelligence:</b> Pioneer is {abs(avg_v)}% behind market. The {worst_d} department shows the highest disparity. Bubble chart size indicates headcount concentration.</div></div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                # Positioning Matrix (Bubble Chart)
                fig = px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', title="Positioning Matrix (Bubble = HC)")
                fig.add_shape(type='line', x0=0, y0=0, x1=max(f_df['Market_Avg']), y1=max(f_df['Market_Avg']), line=dict(color='white', dash='dash'))
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                # H-Bar Chart
                dept_v = f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %')
                fig2 = px.bar(dept_v, x='Variance %', y='Department', orientation='h', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)")
                fig2.update_layout(template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader("⚠️ Critical Gap Table (Gap > 20%)")
            st.dataframe(f_df[f_df['Variance %'] <= -20][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

    # 3. PCI EMPLOYEES
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        if not f_emp.empty:
            # Loyalty Metrics
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Selected Employees", len(f_emp))
            e2.metric("Loyal Staff (>5y)", len(f_emp[f_emp['Tenure_Y'] >= 5]))
            e3.metric("Avg. Tenure", f"{round(f_emp['Tenure_Y'].mean(), 1)} Yrs")
            e4.metric("Retention Risk", "High" if len(f_emp[f_emp['Gap %'] < -15]) > 10 else "Stable")

            # AI Health Check & Tenure Insight
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Payroll Health Check:</b> {len(f_emp[f_emp['Gap %'] < -10])} employees are significantly underpaid. Tenure vs Salary Analysis suggests attention needed for staff with 3+ years experience but high market gaps.</div></div>""", unsafe_allow_html=True)

            # Highlight Cards
            h1, h2 = st.columns(2)
            with h1: st.error(f"Top Underpaid: {f_emp.sort_values('Gap %').iloc[0]['Employee Name']} ({f_emp.sort_values('Gap %').iloc[0]['Gap %']}%)")
            with h2: st.success(f"Top Above Market: {f_emp.sort_values('Gap %', ascending=False).iloc[0]['Employee Name']} (+{f_emp.sort_values('Gap %', ascending=False).iloc[0]['Gap %']}%)")

            sel_name = st.selectbox("Search Employee spotlight:", sorted(f_emp['Employee Name'].unique()))
            if sel_name:
                ed = f_emp[f_emp['Employee Name'] == sel_name].iloc[0]
                ca, cb = st.columns([1, 2])
                with ca:
                    # Spotlight Card with Tenure
                    st.markdown(f"""<div style="background-color:#1f2937; padding:20px; border-radius:15px; border: 1px solid #3b82f6;"><h3>{ed['Employee Name']}</h3><p>ID: {ed['Employee ID']} | Tenure: {ed['Tenure_Text']}</p><p>Joined: {ed['Date of Joining']}</p><hr><p>Salary: {int(ed['Salary'])} | <span class="{'highlight-red' if ed['Gap %'] < 0 else 'highlight-green'}">{'Underpaid' if ed['Gap %'] < 0 else 'Above Market'} ({ed['Gap %']}%)</span></p></div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown("#### Competitor Breakdown for this Role")
                    cc = st.columns(len(comp_cols))
                    for i, cn in enumerate(comp_cols):
                        cv = str(ed.get(cn, "nan"))
                        with cc[i]: st.markdown(f"""<div class="market-box"><small>{cn}</small><br><b style="color:#38bdf8;">{cv if cv not in ['nan','-'] else 'Outsource'}</b></div>""", unsafe_allow_html=True)

            st.divider()
            # Full table with Status Badges (styled text)
            def style_status(v): return f'color: {"#ef4444" if v < 0 else "#22c55e"}; font-weight: bold'
            st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Tenure_Text', 'Salary', 'Market_Avg', 'Gap %']].style.applymap(style_status, subset=['Gap %']), use_container_width=True, hide_index=True)

    # 4. INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("📈 Salary Increment Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            col1, col2 = st.columns([1, 2])
            with col1:
                pct = st.number_input("Enter Increment %", 0.0, 50.0, 5.0, 0.5)
                new_s = int(data['Salary'] * (1 + pct/100))
                gap_after = int(((new_s - data['Market_Avg']) / data['Market_Avg']) * 100)
                st.metric("New Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary'])}")
                st.metric("Post-Increment Status", f"{gap_after}% Gap", delta=gap_after - data['Gap %'])
            with col2:
                # AI Budget Strategy & Advice
                st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Budget Strategy:</b> Incrementing {data['Employee Name']} by {pct}% will result in a monthly budget increase of {(new_s - int(data['Salary'])):,} AED. Status after: <b>{'Still Underpaid' if gap_after < -5 else 'Market Aligned'}</b>.</div></div>""", unsafe_allow_html=True)
                # Visual Gauge
                fig = go.Figure(go.Indicator(mode="gauge+number", value=new_s, title={'text': "Market Position"}, gauge={'axis': {'range': [None, data['Market_Avg']*1.5]}, 'bar': {'color': "#3b82f6"}, 'steps': [{'range': [0, data['Market_Avg']*0.9], 'color': "#ef4444"}, {'range': [data['Market_Avg']*0.9, data['Market_Avg']*1.1], 'color': "#22c55e"}], 'threshold': {'line': {'color': "white", 'width': 4}, 'value': data['Market_Avg']}}))
                fig.update_layout(template="plotly_dark", height=280, margin=dict(t=50, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("💰 Component Breakdown")
            b = int(new_s * 0.7); rem = new_s - b; f = 0 if "Staff" in str(data['Employee Type']) else 300
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"""<div class="market-box"><small>Basic (70%)</small><br><b class="value-text">{b:,}</b></div>""", unsafe_allow_html=True)
            c2.markdown(f"""<div class="market-box"><small>Food</small><br><b class="value-text">{f}</b></div>""", unsafe_allow_html=True)
            c3.markdown(f"""<div class="market-box"><small>Other</small><br><b class="value-text">{max(0, rem-f):,}</b></div>""", unsafe_allow_html=True)
