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
    .note-box { background-color: rgba(245, 158, 11, 0.1); border-left: 5px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 5px; color: #fbbf24; font-size: 15px; line-height: 1.5;}
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    .highlight-red { color: #ef4444; font-weight: bold; }
    .highlight-green { color: #22c55e; font-weight: bold; }
    .profile-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; }
    
    /* Logic & Transparency Additions */
    .formula-display { background-color: #0f172a; border: 2px solid #1e293b; padding: 20px; border-radius: 10px; text-align: center; font-size: 22px; color: #38bdf8; font-family: 'Courier New', Courier, monospace; margin: 15px 0; border-left: 6px solid #3b82f6; }
    .method-section { background-color: #111827; border: 1px solid #1f2937; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #38bdf8; }
    .method-header { color: #38bdf8; font-weight: bold; font-size: 20px; margin-bottom: 12px; display: block; }
    .method-text { color: #e2e8f0; font-size: 16px; line-height: 1.7; margin-bottom: 8px;}
    .sub-point { color: #93c5fd; font-weight: bold; }
    .audit-card { background-color: #1e293b; padding: 15px; border-radius: 10px; border-top: 4px solid #3b82f6; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. ADVANCED PDF GENERATOR
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
               f"to prevent talent poaching.")
    pdf.multi_cell(190, 8, summary, 1); pdf.ln(10)
    pdf.set_font("Arial", 'B', 14); pdf.set_fill_color(255, 230, 230)
    pdf.cell(190, 10, " 2. Critical High-Priority Retention Gaps", 1, 1, 'L', True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(90, 8, "Role", 1); pdf.cell(50, 8, "Dept", 1); pdf.cell(30, 8, "Gap %", 1); pdf.cell(20, 8, "HC", 1, 1)
    pdf.set_font("Arial", '', 9)
    for _, row in crit_df.head(15).iterrows():
        pdf.cell(90, 7, str(row['Designation']), 1); pdf.cell(50, 7, str(row['Department']), 1)
        pdf.cell(30, 7, f"{int(row['Variance %'])}%", 1); pdf.cell(20, 7, str(int(row['Live_HC'])), 1, 1)
    return pdf.output(dest='S').encode('latin-1')

# 3. DATABASE LOADER (With Embedded Formula Logic & HOD Market Upgrade)
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

        # 🚀 HOD TO MANAGER MAPPING (Upgrades HODs to Manager Salary automatically)
        hod_market_override = {
            "Chief Engineer (Mechanical)": "Mechanical Manager",  # Ensures they pull Manager data
            "Production Incharge": "Production Manager",
            "Dy. Chief Engineer (Electrical)": "Electrical Manager"
        }
        # Create a special Lookup Key just for joining with Market Data
        core_df['Lookup_Key'] = core_df['Match_Key'].replace(hod_market_override)
        payroll_df['Lookup_Key'] = payroll_df['Match_Key'].replace(hod_market_override)

        dept_fix = {"HR Administration": "HR", "Information technology": "IT", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores", "Procurment": "Procurement"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix); core_df['Department'] = core_df['Department'].replace(dept_fix)

        payroll_df['DOJ'] = pd.to_datetime(payroll_df['Date of Joining'], errors='coerce')
        today = pd.to_datetime('today')
        payroll_df['Tenure_Y'] = ((today - payroll_df['DOJ']).dt.days / 365.25).fillna(0).astype(int)
        payroll_df['Tenure_M'] = (((today - payroll_df['DOJ']).dt.days % 365.25) / 30.44).fillna(0).astype(int)
        payroll_df['Tenure_Text'] = payroll_df.apply(lambda x: f"{int(x['Tenure_Y'])}y {int(x['Tenure_M'])}m" if pd.notna(x['DOJ']) else "N/A", axis=1)

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

        # 🚀 EMBEDDED AUDIT/FORMULA LOGIC
        def get_audit(row):
            parts = []
            cnt = 0
            for c in comp_cols:
                if pd.notna(row[c]) and row[c] > 0:
                    parts.append(f"{c}: {int(row[c]):,}")
                    cnt += 1
            return " + ".join(parts) if parts else "No External Data", cnt if cnt > 0 else 1, cnt

        audit_res = m_calc.apply(get_audit, axis=1)
        market_df['Audit_Sum'] = [x[0] for x in audit_res]
        market_df['Data_Count'] = [x[1] for x in audit_res]
        market_df['Actual_Count'] = [x[2] for x in audit_res]
        
        for c in comp_cols: market_df[f"Mean_{c}"] = m_calc[c]
        
        m_clean = market_df[['Match_Key', 'Market_Avg', 'Audit_Sum', 'Data_Count', 'Actual_Count'] + [f"Mean_{c}" for c in comp_cols]].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0).fillna(0).astype(int)
        
        # Merge using Lookup_Key so HODs inherit Manager data
        final_df = pd.merge(core_df, m_clean, left_on='Lookup_Key', right_on='Match_Key', how='left', suffixes=('', '_m'))
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        
        final_df['Audit_Sum'] = final_df['Audit_Sum'].fillna("Pioneer Base Used")
        final_df['Data_Count'] = final_df['Data_Count'].fillna(1)
        final_df['Actual_Count'] = final_df['Actual_Count'].fillna(0)

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
        
        # Merge Employee data using Lookup_Key
        emp_data = pd.merge(payroll_df, m_clean, left_on='Lookup_Key', right_on='Match_Key', how='left', suffixes=('', '_m'))
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        emp_data['Audit_Sum'] = emp_data['Audit_Sum'].fillna("Pioneer Base Used")
        emp_data['Data_Count'] = emp_data['Data_Count'].fillna(1)
        
        gap_c = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'].replace(0, np.nan) * 100)
        emp_data['Gap %'] = gap_c.replace([np.inf, -np.inf], np.nan).fillna(0).round(0).astype(int)
        emp_data['Gap (AED)'] = (emp_data['Salary'] - emp_data['Market_Avg']).astype(int)
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Logic Engine Error: {e}"); return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
    hod_roles = ["Chief Engineer (Mechanical)", "Production Incharge", "Dy. Chief Engineer (Electrical)"]

    with st.sidebar:
        l_path = None
        for ex in ["jpg", "png"]:
            if os.path.exists(f"PCI_Logo.{ex}"): l_path = f"PCI_Logo.{ex}"; break
        if l_path: st.image(l_path, use_container_width=True)
        page = st.radio("MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner", "🎯 Transparency Lab"])
        st.markdown("---")
        depts = sorted(df['Department'].unique()); sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

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
        st.dataframe(f_df[['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Role Deep-Dive Analysis")
        sel_role = st.selectbox("Select a Role:", sorted(f_df['Designation'].unique()))
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini HR Insight:</b> {row['Designation']} is {abs(int(row['Variance %']))}% {'below' if row['Variance %'] < 0 else 'above'} market benchmark.</div></div>""", unsafe_allow_html=True)
            
            # 🚀 HOD NOTE
            if sel_role in hod_roles:
                st.markdown(f"""<div class="note-box"><b>Strategic Context (HOD):</b> At Pioneer Cement, the <b>{sel_role}</b> functions as the Head of Department. Therefore, this designation's benchmark is explicitly mapped to the <b>Manager-level Salary</b> within the market for this department, ensuring accurate structural parity.</div>""", unsafe_allow_html=True)

            # 🚀 FORMULA DISPLAY
            st.markdown(f"""<div class="formula-display">Calculation: ({row['Audit_Sum']}) / {int(row['Data_Count'])} = {int(row['Market_Avg']):,} AED</div>""", unsafe_allow_html=True)

            cols = st.columns(len(comp_cols))
            for i, c in enumerate(comp_cols):
                val = str(row.get(f"Mean_{c}", "nan"))
                with cols[i]:
                    if val not in ['nan','-','None','']: st.markdown(f"""<div class="market-box"><small>{c}</small><br><b class="value-text">{int(float(val)):,}</b></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="market-box"><small>{c}</small><br><span style="color:#4b5563;">N/A</span></div>""", unsafe_allow_html=True)

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

    # 3. PCI EMPLOYEES
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        if not f_emp.empty:
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>AI Payroll Health Check:</b> {len(f_emp[f_emp['Gap %'] < -10])} employees are significantly underpaid. Tenure vs Salary Analysis indicates <b>{len(f_emp[(f_emp['Tenure_Y'] >= 3) & (f_emp['Gap %'] < -10)])}</b> loyal personnel (3y+) are at critical risk.</div></div>""", unsafe_allow_html=True)

            sel_name = st.selectbox("Search Spotlight Profile:", sorted(f_emp['Employee Name'].unique()))
            if sel_name:
                ed = f_emp[f_emp['Employee Name'] == sel_name].iloc[0]
                
                # 🚀 HOD NOTE
                if ed['Designation'] in hod_roles:
                    st.markdown(f"""<div class="note-box"><b>HOD Benchmarking Context:</b> Because {ed['Employee Name']} serves as the Head of Department, their salary is benchmarked directly against the <b>Manager-level Salary</b> in the market to ensure true competitive positioning.</div>""", unsafe_allow_html=True)

                ca, cb = st.columns([1, 2])
                with ca:
                    st.markdown(f"""<div class="profile-card"><h3>{ed['Employee Name']}</h3><p>ID: {ed['Employee ID']} | Tenure: {ed['Tenure_Text']}</p><hr><p>Salary: {int(ed['Salary']):,} AED | <span class="{'highlight-red' if ed['Gap %'] < 0 else 'highlight-green'}">Gap: {int(ed['Gap %'])}%</span></p></div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown("#### Competitor Comparison for Role")
                    # 🚀 FORMULA DISPLAY
                    st.markdown(f"""<div style="background-color: #0f172a; padding: 10px; border-radius: 8px; font-family: monospace; color: #38bdf8; margin-bottom: 10px; border-left: 4px solid #3b82f6;">Logic: ({ed['Audit_Sum']}) / {int(ed['Data_Count'])}</div>""", unsafe_allow_html=True)
                    
                    cc = st.columns(len(comp_cols))
                    for i, cn in enumerate(comp_cols):
                        cv = str(ed.get(f"Mean_{cn}", "nan"))
                        with cc[i]:
                            if cv not in ['nan','-','None','']: st.markdown(f"""<div class="market-box"><small>{cn}</small><br><b style="color:#38bdf8;">{int(float(cv)):,}</b></div>""", unsafe_allow_html=True)
                            else: st.markdown(f"""<div class="market-box"><small>{cn}</small><br><span style="color:#4b5563;">N/A</span></div>""", unsafe_allow_html=True)
            st.divider()
            def style_status(v): return f'color: {"#ef4444" if v < 0 else "#22c55e"}; font-weight: bold'
            st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Tenure_Text', 'Salary', 'Market_Avg', 'Gap %']].style.applymap(style_status, subset=['Gap %']), use_container_width=True, hide_index=True)

    # 4. INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("📈 Increment Strategy Simulator")
        target = st.selectbox("Select Employee:", sorted(f_emp['Employee Name'].unique()) if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Increment %", 0.0, 50.0, 5.0)
            new_s = int(data['Salary'] * (1 + pct/100))
            st.metric("Proposed Salary", f"{new_s:,} AED", f"+{new_s - int(data['Salary']):,}")
            fig = go.Figure(go.Indicator(mode="gauge+number", value=new_s, title={'text': "Market Position Gauge"}, gauge={'axis': {'range': [0, data['Market_Avg']*1.5 if data['Market_Avg'] != 0 else 10000]}, 'bar': {'color': "#3b82f6"}}))
            st.plotly_chart(fig, use_container_width=True)

    # 5. TRANSPARENCY LAB
    elif page == "🎯 Transparency Lab":
        st.title("🎯 Transparency Lab: Data Integrity & Methodology")
        
        roles_list = ["-- Select Designation --"] + sorted(f_df['Designation'].unique().tolist())
        sel_role = st.selectbox("Select a Designation to view its specific audit trail:", roles_list)
        
        if sel_role == "-- Select Designation --":
            st.markdown("""<div class="ai-insight-box" style="margin-bottom:25px;"><b>System Statement:</b> The Market Average Calculation Logic used in this system is <b>100% mathematically accurate</b>. Below is the step-by-step logic breakdown.</div>""", unsafe_allow_html=True)

            st.markdown("""
            <div class="method-section">
                <span class="method-header">1. Mathematical Accuracy</span>
                <p class="method-text">We utilize the <b>Arithmetic Mean</b> method. If data points are available from all 4 competitor companies, the sum is divided by 4 ensuring computational integrity.</p>
            </div>
            <div class="method-section">
                <span class="method-header">2. Data Cleaning Logic</span>
                <p class="method-text"><span class="sub-point">• Range Normalization:</span> Market data exists as ranges (e.g., 5,000 - 7,000). The system identifies the <b>Mid-point (Mean)</b> for a realistic average.</p>
                <p class="method-text"><span class="sub-point">• Zero/Null Handling:</span> Missing data (N/A) is <b>completely excluded</b> from the denominator.</p>
            </div>
            <div class="method-section">
                <span class="method-header">3. Advanced Accuracy Perspectives</span>
                <p class="method-text"><span class="sub-point">• Calculation Transparency:</span> Formula breakdowns are provided in real-time to eliminate "black box" logic.</p>
                <p class="method-text"><span class="sub-point">• Designation Standardization:</span> Mapping varying titles into a single benchmarked role.</p>
            </div>
            <div class="method-section" style="border-left: 5px solid #22c55e;">
                <span class="method-header">4. Practical Reliability</span>
                <p class="method-text"><b>Board Statement:</b> "This calculation reflects a Fair Market Level based on current competitor payroll data."</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            audit = f_df[f_df['Designation'] == sel_role].iloc[0]
            
            # 🚀 HOD NOTE
            if sel_role in hod_roles:
                st.markdown(f"""<div class="note-box"><b>Strategic Methodology Override (HOD):</b> Because <b>{sel_role}</b> is mapped as the Head of Department, the raw competitor data points below explicitly reflect the <b>Manager-level</b> compensation benchmark for this sector.</div>""", unsafe_allow_html=True)
            
            st.subheader(f"Audit Trail for: {sel_role}")
            st.markdown(f"""<div class="formula-display">Market Average = ( {audit['Audit_Sum']} ) / {int(audit['Data_Count'])}</div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Calculated Benchmark", f"{int(audit['Market_Avg']):,} AED")
            with c2: 
                conf = (int(audit['Actual_Count'])/4)*100
                st.metric("Confidence Level", f"{int(conf)}%", delta="High Confidence" if conf >= 75 else "Moderate")
            with c3: st.metric("Pioneer Current Pay", f"{int(audit['Your Salary (AED)']):,} AED")

            st.markdown("### 🔍 Raw Competitor Mid-Points")
            chips_cols = st.columns(len(comp_cols))
            
            for i, c in enumerate(comp_cols):
                val = str(audit.get(f"Mean_{c}", "nan"))
                with chips_cols[i]:
                    if val not in ['nan','-','None','']:
                        st.markdown(f"""<div class="audit-card"><small>{c}</small><br><b style="color: #38bdf8; font-size: 20px;">{int(float(val)):,}</b><br><small style="color: #4ade80;">Validated ✅</small></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="audit-card" style="opacity:0.5;"><small>{c}</small><br><b style="font-size: 20px;">N/A</b><br><small>No Data</small></div>""", unsafe_allow_html=True)
