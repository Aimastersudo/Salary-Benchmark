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

# 3. TRIPLE DATABASE LOADER
@st.cache_data
def load_databases():
    try:
        core_df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        payroll_df = pd.read_csv("actuals_payroll.csv", encoding='utf-8-sig')
        market_df = pd.read_csv("Market_salary.csv", encoding='utf-8-sig')

        for df in [core_df, payroll_df, market_df]:
            df.columns = df.columns.str.strip()

        core_df['Designation_Clean'] = core_df['Designation'].astype(str).str.strip().str.title()
        payroll_df['Designation_Clean'] = payroll_df['Designation'].astype(str).str.strip().str.title()
        market_df['Designation_Clean'] = market_df['Designation'].astype(str).str.strip().str.title()

        name_corrector = {
            "Marketing Co-Ordinator": "Marketing Coordinator",
            "Junior Engineer ( Instrum": "Junior Engineer (Instrumentation)",
            "Asst.Security Manager": "Asst. Security Manager",
            "Asst.Public Relation Offi": "Asst. Public Relation Officer",
            "Asst.External Relationship Manager": "Asst. External Relationship Manager",
            "Dy.Chief Engineer(Mech)": "Dy. Chief Engineer (Mechanical)",
            "Finance Co-Ordinator": "Finance Coordinator",
            "Assistant Engineer (Mech)": "Assistant Engineer (Mechanical)",
            "Junior It Help Desk Suppo": "Junior It Help Desk Support",
            "Truck  Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Truck Cum Shovel Operato": "Truck Cum Shovel Operator",
            "Dy.Chief Engineer(Electri": "Dy. Chief Engineer (Electrical)",
            "Sales Co-Ordinator": "Sales Coordinator",
            "Assistant Engineer (Pro": "Assistant Engineer (Production)",
            "Chief Engineer (Mech)": "Chief Engineer (Mechanical)",
            "Senior Engineer(Technical)": "Senior Engineer (Technical)",
            "Senior Engineer (Technical – Sales)": "Senior Engineer (Technical)",
            "Plant Co-Ordinator": "Plant Coordinator",
            "Asst.Purchase Officer": "Asst. Purchase Officer",
            "Senior Sales And Logistic": "Senior Sales & Logistics",
            "Truck Driver - Bulker": "Truck Driver – Bulker",
            "Truck Driver -  Bulker": "Truck Driver – Bulker",
            "Masons": "Mason"
        }
        payroll_df['Designation_Clean'] = payroll_df['Designation_Clean'].replace(name_corrector)
        market_df['Designation_Clean'] = market_df['Designation_Clean'].replace(name_corrector)

        # Duplicate Market Rows for split roles
        mason_market = market_df[market_df['Designation_Clean'] == 'Mason'].copy()
        if not mason_market.empty:
            mason_prod, mason_mech = mason_market.copy(), mason_market.copy()
            mason_prod['Designation_Clean'], mason_mech['Designation_Clean'] = 'Mason (Production)', 'Mason (Mechanical)'
            market_df = pd.concat([market_df, mason_prod, mason_mech], ignore_index=True)

        hr_market = market_df[market_df['Designation_Clean'] == 'Hr Executive'].copy()
        if not hr_market.empty:
            hr_ext, hr_int = hr_market.copy(), hr_market.copy()
            hr_ext['Designation_Clean'], hr_int['Designation_Clean'] = 'HR Executive (External)', 'HR Executive (Internal)'
            market_df = pd.concat([market_df, hr_ext, hr_int], ignore_index=True)

        # Fix Core & Payroll Duplicates
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        core_df.loc[(core_df['Designation_Clean'] == 'Mason') & (core_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Production', na=False, case=False)), 'Designation_Clean'] = 'Mason (Production)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Mason') & (payroll_df['Department'].str.contains('Mechanical', na=False, case=False)), 'Designation_Clean'] = 'Mason (Mechanical)'

        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        core_df.loc[(core_df['Designation_Clean'] == 'Hr Executive') & (core_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('External', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (External)'
        payroll_df.loc[(payroll_df['Designation_Clean'] == 'Hr Executive') & (payroll_df['Department'].str.contains('HR', na=False, case=False)), 'Designation_Clean'] = 'HR Executive (Internal)'

        hc_df = payroll_df.groupby('Designation_Clean').size().reset_index(name='Live_HC')

        def parse_salary_range(val):
            val = str(val).replace(',', '').replace('AED', '').strip()
            if val == '-' or val == '' or str(val).lower() == 'nan': return np.nan
            if '-' in val:
                parts = [float(p.strip()) for p in val.split('-') if p.strip()]
                return sum(parts) / len(parts) if parts else np.nan
            try: return float(val)
            except: return np.nan

        ignore_cols = ['#', 'Designation', 'Designation_Clean']
        comp_cols = [c for c in market_df.columns if c not in ignore_cols]
        
        market_calc = market_df.copy()
        for c in comp_cols:
            market_calc[c] = market_calc[c].apply(parse_salary_range)
            
        market_df['Calculated Market Salary'] = market_calc[comp_cols].mean(axis=1).round(0)
        market_clean = market_df
