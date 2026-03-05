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
    .note-box { background-color: rgba(245, 158, 11, 0.1); border-left: 5px solid #f59e0b; padding: 15px; margin: 10px 0; border-radius: 5px; color: #fbbf24; }
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    .highlight-red { color: #ef4444; font-weight: bold; }
    .highlight-green { color: #22c55e; font-weight: bold; }
    .profile-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. ADVANCED PDF GENERATOR (Visual & Graphical Summary)
def generate_graphical_pdf(f_df, avg_v, worst_d, total_hc, crit_df, loyalty_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(190, 15, "PCI STRATEGIC SALARY INTELLIGENCE REPORT", 0, 1, 'C')
    pdf.set_font("Arial", '', 10); pdf.cell(190, 5, f"Snapshot: {datetime.now().strftime('%d %b %Y')}", 0, 1, 'C')
    pdf.ln(25); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14); pdf.set_fill_color(230, 235, 255)
    pdf.cell(190, 10, " 1. Executive Summary & AI Market Insight", 1, 1, 'L', True)
    pdf.set_font("Arial", '', 11)
    summary = (f"Market Disparity: {avg_v}% | Total Workforce: {total_hc} | Roles: {len(f_df)}\n\n"
               f"AI Insights: The current parity gap is {avg_v}%. The {worst_d} department shows the highest "
               f"competitive risk. We recommend immediate salary alignment for {loyalty_count} loyal personnel (5y+) "
               f"to prevent talent poaching by JK Cement and Emirates Steel.")
    pdf.multi_cell(190, 8, summary, 1); pdf.ln(10)
    pdf.set_font("Arial", 'B', 14); pdf.set_fill_color(255, 230, 230)
    pdf.cell(190, 10, " 2. Critical High-Priority Retention Gaps", 1, 1, 'L', True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(90, 8, "Role", 1); pdf.cell(50, 8, "Dept", 1); pdf.cell(30, 8, "Gap %", 1); pdf.cell(20, 8, "HC", 1, 1)
    pdf.set_font("Arial", '', 9)
    for _, row in crit_df.head(15).iterrows():
        pdf.cell(90, 7, str(row['Designation']), 1); pdf.cell(50, 7, str(row['Department']), 1)
        pdf.cell(30, 7, f"{int(row['Variance %'])}%", 1); pdf.cell(20, 7, str(int(row['Live_HC'])), 1, 1)
    pdf.ln(15); pdf.set_font("Arial", 'I', 8); pdf.cell(190, 5, "CONFIDENTIAL - PIONEER CEMENT AI SYSTEM", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# 3. DATABASE LOADER (Safe Rounded Engine - HC 200 Fix)
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

        payroll_df['DOJ'] = pd.to_datetime(payroll_df['Date of Joining'], errors='coerce')
        today = pd.to_datetime('today')
        payroll_df['Tenure_Y'] = ((today - payroll_df['DOJ']).dt.days / 365.25).fillna(0).astype(int)
        payroll_df['Tenure_M'] = (((today - payroll_df['DOJ']).dt.days % 365.25) / 30.44).fillna(0).astype(int)
        payroll_df['Tenure_Text'] = payroll_df.apply(lambda x: f"{int(x['Tenure_Y'])}y {int(x['Tenure_M'])}m" if pd.notna(x['DOJ']) else "N/A", axis=1)

        rows = []
        for _, row in core_df.iterrows():
            dv = str(row['Department'])
            if '/' in dv:
                for sd in [s.strip() for s in dv.split('/')]:
                    nr = row.copy(); nr['Department'] = sd; rows.append(nr)
            else: rows.append(row)
        core_df = pd.DataFrame(rows)

        def parse_v(v):
            v = str(v).replace(',', '').replace('AED', '').strip()
            if v in ['-', '', 'nan']: return np.nan
            if '-' in v:
                p = [float(i.strip()) for i in v.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(v)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        m_calc = market_df.copy()
        for c in comp_cols: m_calc[c] = m_calc[c].apply(parse_v)
        market_df['Market_Avg'] = m_calc[comp_cols].mean(axis=1).round(0) # Keep NaN here to prevent 0 average
        m_clean = market_df[['Match_Key', 'Market_Avg'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0).fillna(0).astype(int)
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

        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0).fillna(0).astype(int)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        gap_c = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'].replace(0, np.nan) * 100)
        emp_data['Gap %'] = gap_c.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)
        emp_data['Gap (AED)'] = (emp_data['Salary'] - emp_data['Market_Avg']).astype(int)
        t_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(t_map).fillna("Worker")
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Logic Engine Error: {e}"); return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
    with st.sidebar:
        l_path = None
        for ex in ["jpg", "png"]:
            if os.path.exists(f"PCI_Logo.{ex}"): l_path = f"PCI_Logo.{ex}"; break
        if l_path: st.image(l_path, use_container_width=True)
        page = st.radio("MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner"])
        st.markdown("---")
        depts = sorted(df['Department'].unique()); sel_depts = st.multiselect("Filter Dept:", depts, default=depts)
        if st.button("Generate Strategy Report"):
            f_pdf = df[df['Department'].isin(sel_depts)]
            avg_v = int(f_pdf['Variance %'].mean()) if not f_pdf.empty else 0
            worst_d = f_pdf.groupby('Department')['Variance %'].mean().idxmin() if not f_pdf.empty else "N/A"
            crit_df = f_pdf[f_pdf['Variance %'] <= -15].sort_values('Variance %')
            pdf_bytes = generate_graphical_pdf(f_pdf, avg_v, worst_d, int(f_pdf['Live_HC'].sum()), crit_df, len(emp_df[emp_df['Tenure_Y'] >= 5]))
            st.download_button(label="📥 Download Strategy PDF", data=pdf_bytes, file_name="PCI_Strategic_Report.pdf", mime="application/pdf")

    f_df = df[df['Department'].isin(sel_depts)]; f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # 1. EXECUTIVE DASHBOARD
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        mean_v = f_df['Variance %'].mean(); avg_v = f"{int(mean_v) if pd.notna(mean_v) else 0}%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        st.markdown("---")
        st.subheader("🔍 Role Deep-Dive Analysis")
        sel_role = st.selectbox("Select a Role:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini HR Insight:</b> {row['Designation']} is {abs(int(row['Variance %']))}% {'below' if row['Variance %'] < 0 else 'above'} market benchmark. Retention risk: {'High' if row['Variance %'] < -20 else 'Moderate'}.</div></div>""", unsafe_allow_html=True)
            cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = str(row.get(c, "nan"))
                with cols[i]: st.markdown(f"""<div class="market-box"><small>{c}</small><br><b class="value-text">{val if val not in ['nan','-','None'] else 'Outsource'}</b></div>""", unsafe_allow_html=True)

    # 2. MARKET ANALYSIS
    elif page == "📉 Market Analysis":
        st.title("📊 Detailed Market Disparity Analysis")
        if not f_df.empty:
            avg_var = int(f_df['Variance %'].mean()); worst_d = f_df.groupby('Department')['Variance %'].mean().idxmin()
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Strategic Summary:</b> Pioneer is {abs(avg_var)}% behind market. {worst_d} is the highest risk department. Bubble size indicates workforce density.</div></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', title="Positioning Matrix")
                fig.add_shape(type='line', x0=0, y0=0, x1=max(f_df['Market_Avg'] if not f_df.empty else [0]), y1=max(f_df['Market_Avg'] if not f_df.empty else [0]), line=dict(color='white', dash='dash'))
                fig.update_layout(template="plotly_dark"); st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Variance %', y='Department', orientation='h', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)")
                fig2.update_layout(template="plotly_dark"); st.plotly_chart(fig2, use_container_width=True)
            st.subheader("⚠️ High-Priority Adjustment List")
            st.dataframe(f_df[f_df['Variance %'] <= -20][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

    # 3. PCI EMPLOYEES (Interface with AI Payroll Health Check)
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        if not f_emp.empty:
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Selected Employees", len(f_emp))
            e2.metric("Loyal Staff (>5y)", len(f_emp[f_emp['Tenure_Y'] >= 5]))
            e3.metric("Avg. Tenure", f"{round(f_emp['Tenure_Y'].mean(), 1)} Yrs")
            e4.metric("Retention Risk", "High" if len(f_emp[f_emp['Gap %'] < -15]) > 10 else "Stable")

            # 🚀 AI PAYROLL HEALTH CHECK CARD
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>AI Payroll Health Check:</b> {len(f_emp[f_emp['Gap %'] < -10])} employees are significantly underpaid. 
                    Tenure vs Salary Analysis indicates <b>{len(f_emp[(f_emp['Tenure_Y'] >= 3) & (f_emp['Gap %'] < -10)])}</b> loyal personnel (3y+) are at critical risk. 
                    We recommend immediate parity alignment for core technical roles.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Highlight Cards
            h1, h2 = st.columns(2)
            with h1: st.error(f"⚠️ Top Underpaid: {f_emp.sort_values('Gap %').iloc[0]['Employee Name']} ({int(f_emp.sort_values('Gap %').iloc[0]['Gap %'])}%)")
            with h2: st.success(f"⭐ Top Above Market: {f_emp.sort_values('Gap %', ascending=False).iloc[0]['Employee Name']} (+{int(f_emp.sort_values('Gap %', ascending=False).iloc[0]['Gap %'])}%)")

            # Spotlight Profile
            sel_name = st.selectbox("Search Spotlight Profile:", sorted(f_emp['Employee Name'].unique()))
            if sel_name:
                ed = f_emp[f_emp['Employee Name'] == sel_name].iloc[0]
                ca, cb = st.columns([1, 2])
                with ca:
                    st.markdown(f"""<div class="profile-card"><h3>{ed['Employee Name']}</h3><p>ID: {ed['Employee ID']} | Tenure: {ed['Tenure_Text']}</p><p>Joined: {ed['Date of Joining']}</p><hr><p>Salary: {int(ed['Salary']):,} AED | <span class="{'highlight-red' if ed['Gap %'] < 0 else 'highlight-green'}">Gap: {int(ed['Gap %'])}%</span></p></div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown("#### Competitor Comparison for Role")
                    cc = st.columns(len(comp_cols))
                    for i, cn in enumerate(comp_cols):
                        cv = str(ed.get(cn, "nan"))
                        with cc[i]: st.markdown(f"""<div class="market-box"><small>{cn}</small><br><b style="color:#38bdf8;">{cv if cv not in ['nan','-','None'] else 'Outsource'}</b></div>""", unsafe_allow_html=True)
            st.divider()
            def style_status(v): return f'color: {"#ef4444" if v < 0 else "#22c55e"}; font-weight: bold'
            st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Tenure_Text', 'Salary', 'Market_Avg', 'Gap %']].style.applymap(style_status, subset=['Gap %']), use_container_width=True, hide_index=True)

    # 4. INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("📈 Increment Strategy Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            col1, col2 = st.columns([1, 2])
            with col1:
                pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
                new_s = int(data['Salary'] * (1 + pct/100))
                gap_af = int(((new_s - data['Market_Avg']) / data['Market_Avg'] if data['Market_Avg'] != 0 else 1) * 100)
                st.metric("Proposed Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}")
                st.metric("New Market Gap", f"{gap_af}%")
            with col2:
                st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>AI Budget Strategy:</b> Monthly impact: {new_s - int(data['Salary']):,} AED. New status: <b>{'Still Underpaid' if gap_af < -5 else 'Aligned'}</b>.</div></div>""", unsafe_allow_html=True)
                fig = go.Figure(go.Indicator(mode="gauge+number", value=new_s, title={'text': "Market Position Gauge"}, gauge={'axis': {'range': [0, data['Market_Avg']*1.5 if data['Market_Avg'] != 0 else 10000]}, 'bar': {'color': "#3b82f6"}, 'steps': [{'range': [0, data['Market_Avg']*0.9], 'color': "red"}, {'range': [data['Market_Avg']*0.9, data['Market_Avg']*1.1], 'color': "green"}]}))
                fig.update_layout(template="plotly_dark", height=280); st.plotly_chart(fig, use_container_width=True)
            st.subheader("💰 Component Breakdown")
            b = int(new_s * 0.7); rem = new_s - b; f = 0 if "Staff" in str(data['Employee Type']) else 300
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"""<div class="market-box"><small>Basic Salary</small><br><b class="value-text">{b:,}</b></div>""", unsafe_allow_html=True)
            c2.markdown(f"""<div class="market-box"><small>Food Allowance</small><br><b class="value-text">{f}</b></div>""", unsafe_allow_html=True)
            c3.markdown(f"""<div class="market-box"><small>Other Allowances</small><br><b class="value-text">{max(0, rem-f):,}</b></div>""", unsafe_allow_html=True)
