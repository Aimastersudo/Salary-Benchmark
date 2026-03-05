import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
    .value-text { color: #38bdf8; font-size: 18px; font-weight: bold; }
    .status-tag { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER
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
            t = t.replace("Co-Ordinator", "Coordinator").replace("–", "-").replace(" / ", "/")
            return t

        core_df['Match_Key'] = core_df['Designation'].apply(master_clean)
        payroll_df['Match_Key'] = payroll_df['Designation'].apply(master_clean)
        market_df['Match_Key'] = market_df['Designation'].apply(master_clean)

        bridge = {"Asst.Public Relation Offi": "Asst. Public Relation Officer", "Asst.External Relationship Manager": "Asst. External Relationship Manager", "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)", "Truck Cum Shovel Operato": "Truck Cum Shovel Operator", "Junior It Help Desk Suppo": "Junior It Help Desk Support", "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)", "Assistant Engineer (Pro": "Assistant Engineer (Production)", "Chief Engineer (Mech)": "Chief Engineer (Mechanical)", "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)", "Senior Engineer(Technical)": "Senior Engineer (Technical)", "Finance Co-Ordinator": "Finance Coordinator", "Marketing Co-Ordinator": "Marketing Coordinator", "Plant Co-Ordinator": "Plant Coordinator", "Sales Co-Ordinator": "Sales Coordinator", "Senior Sales And Logistic": "Senior Sales & Logistics", "Asst.Security Manager": "Asst. Security Manager", "Asst.Purchase Officer": "Asst. Purchase Officer", "Truck Driver - Bulker": "Truck Driver - Bulker", "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)"}
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
            idx = final_df[final_df['Match_Key'] == key].index
            if len(idx) > 0: final_df.at[idx[0], 'Live_HC'] += rem

        payroll_df['Salary'] = payroll_df['Salary'].astype(str).str.replace(',', '').astype(float).round(0)
        emp_data = pd.merge(payroll_df, m_clean, on='Match_Key', how='left')
        emp_data['Market_Avg'] = emp_data['Market_Avg'].fillna(emp_data['Salary']).astype(int)
        emp_data['Gap %'] = ((emp_data['Salary'] - emp_data['Market_Avg']) / emp_data['Market_Avg'] * 100).fillna(0).round(0).astype(int)
        t_map = dict(zip(core_df['Match_Key'], core_df['Employee Type']))
        emp_data['Employee Type'] = emp_data['Match_Key'].map(t_map).fillna("Worker")
        return final_df, emp_data, comp_cols
    except Exception as e:
        st.error(f"Error: {e}"); return None, None, None

df, emp_df, comp_cols = load_databases()

if df is not None:
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

    # 📈 INCREMENT PLANNER (ENHANCED)
    if page == "📈 Increment Planner":
        st.title("📈 Salary Increment Strategy & Simulator")
        st.caption("Plan and simulate salary adjustments with market intelligence.")

        if not f_emp.empty:
            target_name = st.selectbox("Select Employee to Plan Increment:", sorted(f_emp['Employee Name'].unique()))
            
            if target_name:
                data = f_emp[f_emp['Employee Name'] == target_name].iloc[0]
                
                # Simulation Inputs
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("#### Simulation Controls")
                    pct = st.number_input("Enter Increment Percentage (%)", 0.0, 50.0, 5.0, 0.5)
                    one_time = st.checkbox("Show as One-time Adjustment")
                    
                    curr = int(data['Salary'])
                    new_s = int(curr * (1 + pct/100))
                    market_gap_after = int(((new_s - data['Market_Avg']) / data['Market_Avg']) * 100)
                    
                    st.divider()
                    st.metric("New Proposed Salary", f"{new_s:,} AED", f"+{new_s - curr}")
                    st.metric("Market Gap After Increment", f"{market_gap_after}%", delta=market_gap_after - data['Gap %'])
                
                with col2:
                    # 🚀 Gemini AI Strategy Note
                    st.markdown(f"""
                    <div class="salary-card">
                        <div class="ai-insight-box">
                            <b>Gemini Strategic Advice:</b><br>
                            For {data['Employee Name']} ({data['Designation']}), a {pct}% increment reduces the market gap from {abs(data['Gap %'])}% to {abs(market_gap_after)}%. 
                            {'This adjustment is still below market' if market_gap_after < -5 else 'This adjustment successfully aligns the employee with the market' if -5 <= market_gap_after <= 5 else 'This adjustment places the employee above market average'}. 
                            <br><b>Recommendation:</b> {'Consider a higher adjustment to reach -5% threshold' if market_gap_after < -10 else 'Approved for alignment' if market_gap_after >= -5 else 'Proceed with caution'}.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Gauge Chart for Market Alignment
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = new_s,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Market Position (AED)"},
                        gauge = {
                            'axis': {'range': [None, data['Market_Avg'] * 1.5]},
                            'bar': {'color': "#3b82f6"},
                            'steps': [
                                {'range': [0, data['Market_Avg'] * 0.9], 'color': "#ef4444"},
                                {'range': [data['Market_Avg'] * 0.9, data['Market_Avg'] * 1.1], 'color': "#22c55e"},
                                {'range': [data['Market_Avg'] * 1.1, data['Market_Avg'] * 1.5], 'color': "#eab308"}],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': data['Market_Avg']}}))
                    fig.update_layout(template="plotly_dark", height=300, margin=dict(t=50, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)

                # 4. Component Breakdown
                st.subheader("💰 New Salary Breakdown")
                basic = int(new_s * 0.7); rem = new_s - basic
                food = 0 if "Staff" in str(data['Employee Type']) else 300
                other = max(0, rem - food)
                
                b1, b2, b3 = st.columns(3)
                with b1: st.markdown(f"""<div class="market-box"><small>Basic Salary (70%)</small><br><b class="value-text">{basic:,}</b></div>""", unsafe_allow_html=True)
                with b2: st.markdown(f"""<div class="market-box"><small>Food Allowance</small><br><b class="value-text">{food}</b></div>""", unsafe_allow_html=True)
                with b3: st.markdown(f"""<div class="market-box"><small>Other Allowances</small><br><b class="value-text">{other:,}</b></div>""", unsafe_allow_html=True)

                st.divider()
                st.info(f"Financial Impact: This increment will increase the annual payroll for {data['Department']} by {(new_s - curr)*12:,} AED.")

    # (Other pages remain standard as previous turns)
    elif page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Market_Avg', 'Variance %']], use_container_width=True, hide_index=True)
    elif page == "📉 Market Analysis":
        st.title("📊 Market Disparity Analysis")
        st.plotly_chart(px.scatter(f_df, x='Market_Avg', y='Your Salary (AED)', size='Live_HC', color='Department', hover_name='Designation', template="plotly_dark"), use_container_width=True)
    elif page == "👥 PCI Employees":
        st.title("👥 PCI Employees Intelligence")
        st.dataframe(f_emp[['Employee ID', 'Employee Name', 'Designation', 'Department', 'Salary', 'Market_Avg', 'Gap %']], use_container_width=True, hide_index=True)
