import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

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
    .outsource-text { color: #3b82f6; font-weight: bold; font-size: 18px; }
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

        dept_fix = {"HR Administration": "HR", "Information technology": "IT", "Quality Control": "QC", "Sales and Logistics": "Sales & Logistics", "Stores Section": "Stores", "Procurment": "Procurement"}
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix)
        core_df['Department'] = core_df['Department'].replace(dept_fix)

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
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_v)
        market_df['Market_Avg'] = market_calc[comp_cols].mean(axis=1).round(0)
        m_clean = market_df[['Match_Key', 'Market_Avg'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        final_df = pd.merge(core_df, m_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        final_df['Variance %'] = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'] * 100).round(0).astype(int)

        hc_d = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_D')
        final_df = pd.merge(final_df, hc_d, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_D'].fillna(0).astype(int)

        alloc = final_df.groupby('Match_Key')['Live_HC'].sum().reset_index(name='A')
        act = payroll_df.groupby('Match_Key').size().reset_index(name='Actual')
        comp = pd.merge(act, alloc, on='Match_Key', how='left')
        res = comp[comp['Actual'] > comp['A'].fillna(0)]

        for _, r in res.iterrows():
            key = r['Match_Key']; rem = int(r['Actual'] - r['A'])
            idx_list = final_df[final_df['Match_Key'] == key].index
            if len(idx_list) > 0: final_df.at[idx_list[0], 'Live_HC'] += rem

        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        # Deep Merge for Competitors in Employee Table
        e_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        e_data['Market_Avg'] = e_data['Market_Avg'].fillna(e_data['Salary']).astype(int)
        e_data['Gap (AED)'] = (e_data['Salary'] - e_data['Market_Avg']).astype(int)
        e_data['Gap %'] = ((e_data['Salary'] - e_data['Market_Avg']) / e_data['Market_Avg'] * 100).fillna(0).round(0).astype(int)
        
        type_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        e_data['Employee Type'] = e_data['Match_Key'].map(type_map).fillna("Worker")

        return final_df, e_data, comp_cols
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

    # (Executive Dashboard & Market Analysis sections stay same as previous turn)
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        c3.metric("Avg. Market Gap", f"{int(f_df['Variance %'].mean()) if not f_df.empty else 0}%", delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Deep-Dive Analysis")
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
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Market Summary:</b> Average disparity is {int(f_df['Variance %'].mean())}%. Most vulnerable area is {f_df.groupby('Department')['Variance %'].mean().idxmin()}.</div></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', title="Positioning Matrix", template="plotly_dark"), use_container_width=True)
            with c2: st.plotly_chart(px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Variance %', y='Department', orientation='h', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Dept (%)", template="plotly_dark"), use_container_width=True)
            st.subheader("⚠️ Critical Priority List")
            st.dataframe(f_df[f_df['Variance %'] <= -20][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

    # 👥 PCI EMPLOYEES (ENHANCED INTERFACE)
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        st.caption("Individual payroll analysis against competitive benchmarks.")

        if not f_emp.empty:
            # 1. AI Summary Metrics
            e1, e2, e3, e4 = st.columns(4)
            under_market = f_emp[f_emp['Gap %'] < -10]
            e1.metric("Selected Employees", len(f_emp))
            e2.metric("Under Market (>10%)", len(under_market))
            e3.metric("Avg. AED Gap", f"{int(f_emp['Gap (AED)'].mean())}")
            e4.metric("Risk Level", "Critical" if len(under_market)/len(f_emp) > 0.3 else "Stable")

            # 2. Gemini AI Insight
            worst_emp = f_emp.sort_values('Gap %').iloc[0]
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini Payroll Health Check:</b> {len(under_market)} employees are significantly below market rates. 
                    The highest priority adjustment is <b>{worst_emp['Employee Name']}</b> ({worst_emp['Designation']}) with a <b>{abs(worst_emp['Gap %'])}%</b> gap. 
                    Overall, the {f_emp['Department'].iloc[0] if len(f_emp['Department'].unique())==1 else 'filtered group'} shows a talent retention risk of 
                    <b>{'High' if len(under_market)/len(f_emp) > 0.2 else 'Moderate'}</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 3. Employee Profile Quick-View
            st.subheader("🔍 Employee Spotlight")
            selected_name = st.selectbox("Search and Select Employee to see deep-dive breakdown:", sorted(f_emp['Employee Name'].unique()))
            
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
                        <p><b>Market Avg:</b> {int(edata['Market_Avg'])} AED</p>
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

            # 4. Main Table with Styling
            st.subheader("📊 Full Employee Database")
            search_box = st.text_input("Quick filter by Name or ID:", "")
            display_df = f_emp.copy()
            if search_box:
                display_df = display_df[display_df['Employee Name'].str.contains(search_box, case=False) | display_df['Employee ID'].astype(str).str.contains(search_box)]
            
            # Formatting table for better readability
            def style_gap(val):
                color = '#ef4444' if val < 0 else '#22c55e'
                return f'color: {color}; font-weight: bold'

            st.dataframe(display_df[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap (AED)', 'Gap %']].style.applymap(style_gap, subset=['Gap (AED)', 'Gap %']), use_container_width=True, hide_index=True)
        else:
            st.warning("No employees found in the selected department.")

    elif page == "📈 Increment Planner":
        st.title("📈 Salary Increment Simulator")
        target = st.selectbox("Select Employee:", f_emp['Employee Name'].unique() if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Enter Increment %", 0.0, 100.0, 5.0, 0.5)
            curr = int(data['Salary']); new_s = int(curr * (1 + pct/100))
            st.metric("Simulated Salary", f"{new_s} AED", f"+{new_s - curr}")
            basic = int(new_s * 0.7); rem = new_s - basic
            food = 0 if "Staff" in str(data['Employee Type']) else 300
            st.markdown(f"""<div class="market-box">Basic: {basic} | Food: {food} | Other: {max(0, rem-food)}</div>""", unsafe_allow_html=True)
