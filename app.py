import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
    </style>
    """, unsafe_allow_html=True)

# 3. TRIPLE DATABASE LOADER (Fixing Syntax & Indentation)
@st.cache_data
def load_databases():
    try:
        # Load DBs
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        # Clean spaces
        for df in [core_df, payroll_df, market_df]:
            df.columns = df.columns.str.strip()

        core_df['Designation_Clean'] = core_df['Designation'].astype(str).str.strip().str.title()
        payroll_df['Designation_Clean'] = payroll_df['Designation'].astype(str).str.strip().str.title()
        market_df['Designation_Clean'] = market_df['Designation'].astype(str).str.strip().str.title()

        # Name Corrector logic
        name_corrector = {
            "Marketing Co-Ordinator": "Marketing Coordinator", "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Asst.Security Manager": "Asst. Security Manager", "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager", "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)",
            "Finance Co-Ordinator": "Finance Coordinator", "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support", "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator", "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)",
            "Sales Co-Ordinator": "Sales Coordinator", "Assistant Engineer (Pro": "Assistant Engineer (Production)",
            "Chief Engineer (Mech)": "Chief Engineer (Mechanical)", "Senior Engineer(Technical)": "Senior Engineer (Technical)",
            "Senior Engineer (Technical – Sales)": "Senior Engineer (Technical)", "Plant Co-Ordinator": "Plant Coordinator",
            "Asst.Purchase Officer": "Asst. Purchase Officer", "Senior Sales And Logistic": "Senior Sales & Logistics",
            "Truck Driver - Bulker": "Truck Driver – Bulker", "Truck Driver -  Bulker": "Truck Driver – Bulker", "Masons": "Mason"
        }
        payroll_df['Designation_Clean'] = payroll_df['Designation_Clean'].replace(name_corrector)
        market_df['Designation_Clean'] = market_df['Designation_Clean'].replace(name_corrector)

        # Duplicate fix for Masons & HR
        mason_market = market_df[market_df['Designation_Clean'] == 'Mason'].copy()
        if not mason_market.empty:
            m1, m2 = mason_market.copy(), mason_market.copy()
            m1['Designation_Clean'], m2['Designation_Clean'] = 'Mason (Production)', 'Mason (Mechanical)'
            market_df = pd.concat([market_df, m1, m2], ignore_index=True)

        # Core/Payroll separation
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'

        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')

        # Market Average Calculation
        def parse_salary(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val in ['-', '', 'nan']: return np.nan
            if '-' in val:
                p = [float(i.strip()) for i in val.split('-') if i.strip()]
                return sum(p)/len(p) if p else np.nan
            try: return float(val)
            except: return np.nan

        ignore = ['#', 'Designation', 'Designation_Clean']
        comp_cols = [c for c in market_df.columns if c not in ignore]
        market_calc = market_df.copy()
        for c in comp_cols: market_calc[c] = market_calc[c].apply(parse_salary)
            
        market_df['Calculated Market Salary'] = market_calc[comp_cols].mean(axis=1).round(0)
        market_clean = market_df[['Designation_Clean', 'Calculated Market Salary'] + comp_cols].dropna(subset=['Calculated Market Salary']).drop_duplicates(subset=['Designation_Clean'])

        # Final Merging
        merged_df = pd.merge(core_df, hc_df, on='Designation_Clean', how='left')
        merged_df = pd.merge(merged_df, market_clean, on='Designation_Clean', how='left')

        merged_df['Your Salary (AED)'] = merged_df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float)
        merged_df['Live_HC'] = merged_df['Live_HC'].fillna(0).astype(int)
        merged_df['Calculated Market Salary'] = merged_df['Calculated Market Salary'].fillna(merged_df['Your Salary (AED)'])
        merged_df['Variance %'] = ((merged_df['Your Salary (AED)'] - merged_df['Calculated Market Salary']) / merged_df['Calculated Market Salary'] * 100).round(0).astype(int)

        return merged_df, comp_cols
    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None

df, competitor_columns = load_databases()

if df is not None:
    # 4. Sidebar Filters
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "📁 Structural Groups"])
        st.markdown("---")
        depts = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("Filter Departments:", depts, default=depts)
        search_q = st.text_input("Find Designation", placeholder="Search roles...")

    f_df = df[df['Department'].isin(selected_depts)]
    if search_q: f_df = f_df[f_df['Designation'].str.contains(search_q, case=False, na=False)]

    # -------------------------------------------------------------
    # 📊 EXECUTIVE DASHBOARD
    # -------------------------------------------------------------
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        st.caption("🟢 Live 3-Pillar Architecture Sync")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations Scoped", len(f_df))
        c2.metric("Total Headcount", int(f_df['Live_HC'].sum())) 
        avg_v = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_v, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))

        st.subheader("Interactive Salary Matrix (AED)")
        st.dataframe(f_df[['Designation', 'Department', 'Employee Type', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Deep-Dive Market Analysis")
        selected_role = st.selectbox("Select a Designation for Competitor Breakdown:", f_df['Designation'].unique())
        
        if selected_role:
            row = f_df[f_df['Designation'] == selected_role].iloc[0]
            st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>HR Insight:</b> {row['Designation']} is {abs(row['Variance %'])}% below market average.</div></div>""", unsafe_allow_html=True)
            
            cols = st.columns(len(competitor_columns))
            for i, comp in enumerate(competitor_columns):
                val = str(row[comp])
                if val in ['nan', '-', '', 'None']: val = "Outsource"
                with cols[i]: st.markdown(f"""<div class="market-box"><small>{comp}</small><br><b>{val}</b></div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 📉 MARKET ANALYSIS
    # -------------------------------------------------------------
    elif page == "📉 Market Analysis":
        st.title("📊 In-Depth Market Disparity Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            tier_fig = px.bar(f_df.groupby('Employee Type')['Variance %'].mean().reset_index(), x='Employee Type', y='Variance %', color='Employee Type', title="Variance by Employee Type (%)")
            tier_fig.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(tier_fig, use_container_width=True)
        with col2:
            dept_fig = px.bar(f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %'), x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn', title="Variance by Department (%)")
            dept_fig.update_layout(template="plotly_dark")
            st.plotly_chart(dept_fig, use_container_width=True)

        st.divider()
        st.subheader("⚠️ Top 10 Critical Salary Gaps")
        gap_df = f_df[f_df['Variance %'] < 0].sort_values('Variance %').head(10)
        if not gap_df.empty:
            fig_gap = px.bar(gap_df.melt(id_vars=['Designation'], value_vars=['Your Salary (AED)', 'Calculated Market Salary']), x='Designation', y='value', color='variable', barmode='group', title="Pioneer vs Market (Top 10 Critical)")
            fig_gap.update_layout(template="plotly_dark", xaxis_tickangle=-45)
            st.plotly_chart(fig_gap, use_container_width=True)

    # -------------------------------------------------------------
    # 📁 STRUCTURAL GROUPS
    # -------------------------------------------------------------
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, etype in enumerate(emp_types):
                with tabs[i]: st.dataframe(f_df[f_df['Employee Type'] == etype][['Designation', 'Department', 'Live_HC', 'Your Salary (AED)', 'Calculated Market Salary', 'Variance %']], use_container_width=True, hide_index=True)
