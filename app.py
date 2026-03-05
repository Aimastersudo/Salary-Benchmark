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

        # Bridge for known discrepancies
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

        # Dept Standardization (Standardize to Clean Names)
        dept_fix = {
            "HR Administration": "HR", 
            "Information technology": "IT", 
            "Quality Control": "QC", 
            "Sales and Logistics": "Sales & Logistics", 
            "Stores Section": "Stores",
            "Procurment": "Procurement",
            "Procurement": "Procurement"
        }
        payroll_df['Department'] = payroll_df['Department'].replace(dept_fix)
        core_df['Department'] = core_df['Department'].replace(dept_fix)

        # Split Slash Departments in Core
        rows = []
        for _, row in core_df.iterrows():
            dv = str(row['Department'])
            if '/' in dv:
                for sd in [s.strip() for s in dv.split('/')]:
                    nr = row.copy(); nr['Department'] = sd; rows.append(nr)
            else: rows.append(row)
        core_df = pd.DataFrame(rows)

        # Market Average calculation
        def parse_val(v):
            v = str(v).replace(',', '').replace('AED', '').strip()
            if v in ['-', '', 'nan']: return np.nan
            if '-' in v:
                p = [float(i.strip()) for i in v.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(v)
            except: return np.nan

        comp_cols = [c for c in market_df.columns if c not in ['#', 'Designation', 'Match_Key']]
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_val)
        market_df['Market_Avg'] = market_calc[comp_cols].mean(axis=1).round(0)
        market_clean = market_df[['Match_Key', 'Market_Avg'] + comp_cols].dropna(subset=['Market_Avg']).drop_duplicates(subset=['Match_Key'])

        # Dashboard Data Merge
        core_df['Your Salary (AED)'] = core_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float).round(0)
        final_df = pd.merge(core_df, market_clean, on='Match_Key', how='left')
        final_df['Market_Avg'] = final_df['Market_Avg'].fillna(final_df['Your Salary (AED)']).astype(int)
        final_df['Variance %'] = ((final_df['Your Salary (AED)'] - final_df['Market_Avg']) / final_df['Market_Avg'] * 100).round(0).astype(int)

        # Residual Allocation Headcount Sync (Exactly 200)
        hc_dept = payroll_df.groupby(['Match_Key', 'Department']).size().reset_index(name='HC_Dept')
        final_df = pd.merge(final_df, hc_dept, on=['Match_Key', 'Department'], how='left')
        final_df['Live_HC'] = final_df['HC_Dept'].fillna(0).astype(int)

        allocated = final_df.groupby('Match_Key')['Live_HC'].sum().reset_index(name='A')
        actual = payroll_df.groupby('Match_Key').size().reset_index(name='Actual')
        comp = pd.merge(actual, allocated, on='Match_Key', how='left')
        res = comp[comp['Actual'] > comp['A'].fillna(0)]

        for _, r in res.iterrows():
            key = r['Match_Key']; rem = int(r['Actual'] - r['A'])
            idx_list = final_df[final_df['Match_Key'] == key].index
            if len(idx_list) > 0: final_df.at[idx_list[0], 'Live_HC'] += rem

        # Employee Data
        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_data = pd.merge(payroll_df, market_clean[['Match_Key', 'Market_Avg']], on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        emp_data['Gap (AED)'] = (emp_data['Salary'] - emp_data['Market_Avg']).astype(int)
        emp_data['Gap %'] = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'] * 100).fillna(0).round(0).astype(int)
        type_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(type_map).fillna("Worker")

        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None, None, None

df, emp_df, comp_columns = load_databases()

if df is not None:
    # 4. SIDEBAR
    with st.sidebar:
        logo_path = None
        for ext in ["jpg", "png", "jpeg"]:
            if os.path.exists(f"PCI_Logo.{ext}"): logo_path = f"PCI_Logo.{ext}"; break
        if logo_path: st.image(logo_path, use_container_width=True)
        else: st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PCI+HR+AI", use_container_width=True)
            
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "👥 PCI Employees", "📈 Increment Planner"])
        st.markdown("---")
        depts = sorted(df['Department'].dropna().unique())
        sel_depts = st.multiselect("Filter Dept:", depts, default=depts)

    f_df = df[df['Department'].isin(sel_depts)]
    f_emp = emp_df[emp_df['Department'].isin(sel_depts)]

    # 📊 EXECUTIVE DASHBOARD
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        if "Truck Driver - Bulker" in f_df['Designation'].values:
            st.markdown("""<div class="note-box"><b>📌 Note:</b> Bulker Driver salaries are consistent across the industry due to trip-based allowance structures.</div>""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations", len(f_df))
        total_hc = int(f_df['Live_HC'].sum())
        c2.metric("Total Headcount", total_hc) 
        
        # 🚀 Fix NaN for mean variance
        m_var = f_df['Variance %'].mean()
        avg_v = f"{int(m_var)}%" if not f_df.empty and pd.notna(m_var) else "0%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))
        
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Role Specific Deep-Dive")
        sel_role = st.selectbox("Select a Designation for AI Analysis:", f_df['Designation'].unique())
        if sel_role:
            row = f_df[f_df['Designation'] == sel_role].iloc[0]
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini HR Analysis:</b> For <b>{row['Designation']}</b>, the current Pioneer salary is <b>{abs(row['Variance %'])}% {'below' if row['Variance %'] < 0 else 'above'}</b> the market average of {row['Market_Avg']} AED. 
                    With <b>{row['Live_HC']}</b> employees in this role, the retention risk is <b>{'Critical' if row['Variance %'] < -25 else 'High' if row['Variance %'] < -15 else 'Low'}</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(len(comp_columns))
            for i, comp in enumerate(comp_columns):
                val = str(row.get(comp, "nan"))
                with cols[i]:
                    if val in ['nan', '-', '', 'None']: st.markdown(f"""<div class="market-box"><small>{comp}</small><br><span class="outsource-text">Outsource</span></div>""", unsafe_allow_html=True)
                    else: st.markdown(f"""<div class="market-box"><small>{comp}</small><br><span class="value-text">{val}</span></div>""", unsafe_allow_html=True)

    # 📉 MARKET ANALYSIS (ENHANCED)
    elif page == "📉 Market Analysis":
        st.title("📊 Market Disparity & Financial Impact")
        
        if not f_df.empty:
            # Calculation fixes
            mean_v = f_df['Variance %'].mean()
            avg_var = int(mean_v) if pd.notna(mean_v) else 0
            
            dept_means = f_df.groupby('Department')['Variance %'].mean()
            worst_dept = dept_means.idxmin() if not dept_means.empty else "N/A"
            worst_val = int(dept_means.min()) if not dept_means.empty else 0
            
            # Total cost to align (only for underpaid)
            f_df['Monthly_Gap'] = (f_df['Market_Avg'] - f_df['Your Salary (AED)']) * f_df['Live_HC']
            total_monthly_impact = int(f_df[f_df['Monthly_Gap'] > 0]['Monthly_Gap'].sum())

            # 🚀 Gemini Strategic Summary
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini Strategic Market Intelligence:</b><br>
                    • Pioneer Cement is currently <b>{abs(avg_var)}%</b> behind industry benchmarks on average.<br>
                    • The <b>{worst_dept}</b> department is the most vulnerable with a <b>{abs(worst_val)}%</b> market gap.<br>
                    • To align all underpaid roles to market average, a monthly budget adjustment of <b>{total_monthly_impact:,} AED</b> is estimated.<br>
                    • Talent risk is highest in roles overlapping with competitors like <b>Emirates Steel</b> and <b>JK Cement</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Overall Market Gap", f"{avg_var}%")
            m2.metric("Most Vulnerable Dept", worst_dept, f"{worst_val}%")
            m3.metric("Est. Alignment Cost", f"{total_monthly_impact:,} AED/mo")

            st.divider()

            # Enhanced Charts
            c1, c2 = st.columns(2)
            with c1:
                # Market Positioning Bubble Chart
                fig_bubble = px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department',
                                        hover_name='Designation', title="Positioning Matrix (Bubble Size = Headcount)",
                                        labels={'Market_Avg': 'Market Salary', 'Your Salary (AED)': 'Pioneer Salary'})
                fig_bubble.add_shape(type='line', x0=0, y0=0, x1=max(f_df['Market_Avg']), y1=max(f_df['Market_Avg']), line=dict(color='gray', dash='dash'))
                fig_bubble.update_layout(template="plotly_dark")
                st.plotly_chart(fig_bubble, use_container_width=True)

            with c2:
                # Top 10 Disparity Roles
                top_gaps = f_df[f_df['Variance %'] < 0].sort_values('Variance %').head(10)
                fig_gap = px.bar(top_gaps, x='Variance %', y='Designation', orientation='h', color='Variance %',
                                 color_continuous_scale='RdYlGn_r', title="Top 10 Critical Role Disparities")
                fig_gap.update_layout(template="plotly_dark")
                st.plotly_chart(fig_gap, use_container_width=True)

            st.subheader("⚠️ High-Priority Adjustment List")
            st.caption("Roles with >15% negative variance compared to market average.")
            high_risk = f_df[f_df['Variance %'] <= -15].sort_values('Variance %')
            st.dataframe(high_risk[['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
        else:
            st.warning("No data available for the selected filters.")

    # 👥 PCI EMPLOYEES
    elif page == "👥 PCI Employees":
        st.title("👥 Individual Salary vs Market Benchmarks")
        search = st.text_input("Search Employee Name:", "")
        if search: f_emp = f_emp[f_emp['Employee Name'].str.contains(search, case=False, na=False)]
        
        def color_g(v): return f"color: {'#ef4444' if v < 0 else '#22c55e'}"
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap (AED)', 'Gap %']].style.applymap(color_g, subset=['Gap (AED)', 'Gap %']), use_container_width=True, hide_index=True)

    # 📈 INCREMENT PLANNER
    elif page == "📈 Increment Planner":
        st.title("📈 Salary Increment Simulator")
        target = st.selectbox("Select Employee:", f_emp['Employee Name'].unique() if not f_emp.empty else [])
        if target:
            data = f_emp[f_emp['Employee Name'] == target].iloc[0]
            pct = st.number_input("Enter Increment Percentage (%)", 0.0, 100.0, 5.0, 0.5)
            curr = int(data['Salary'])
            new_s = int(curr * (1 + pct/100))
            
            st.markdown("---")
            res1, res2 = st.columns(2)
            res1.metric("Current Salary", f"{curr} AED")
            res2.metric("Simulated New Salary", f"{new_s} AED", f"+{new_s - curr}")

            # Breakdown
            basic = int(new_s * 0.7)
            rem = new_s - basic
            is_staff = "Staff" in str(data['Employee Type'])
            food = 0 if is_staff else 300
            other = max(0, rem - food)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"""<div class="market-box"><small>Basic (70%)</small><br><b class="value-text">{basic}</b></div>""", unsafe_allow_html=True)
            with c2: st.markdown(f"""<div class="market-box"><small>Food Allowance</small><br><b class="value-text">{food}</b></div>""", unsafe_allow_html=True)
            with c3: st.markdown(f"""<div class="market-box"><small>Other Allowances</small><br><b class="value-text">{other}</b></div>""", unsafe_allow_html=True)
