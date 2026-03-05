import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR Intelligence | Full DB", layout="wide")

# 2. Premium Dark UI Styling
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    </style>
    """, unsafe_allow_html=True)

# 3. THE COMPLETE DATABASE (All 84 Designations)
# Every single row from your provided data sheet is here
FULL_DB = [
    {"Designation": "Accountant", "Dept": "Finance", "Tier": "Professional Staff", "HC": 1, "Pioneer": 6500, "Market": 9250},
    {"Designation": "Admin Assistant", "Dept": "Production", "Tier": "Professional Staff", "HC": 1, "Pioneer": 3000, "Market": 4750},
    {"Designation": "Assistant Engineer (Production)", "Dept": "Production", "Tier": "Professional Staff", "HC": 1, "Pioneer": 3813, "Market": 10000},
    {"Designation": "Assistant Sales Manager", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 1, "Pioneer": 9500, "Market": 14250},
    {"Designation": "Assistant Stores Manager", "Dept": "Sales & Logistics", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 18413, "Market": 10500},
    {"Designation": "Asst. External Relationship Manager", "Dept": "Stores", "Tier": "Professional Staff", "HC": 1, "Pioneer": 21493, "Market": 14000},
    {"Designation": "Asst. Public Relation Officer", "Dept": "External Relationship", "Tier": "Professional Staff", "HC": 1, "Pioneer": 11859, "Market": 9000},
    {"Designation": "Asst. Purchase Officer", "Dept": "Admin", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5225, "Market": 9000},
    {"Designation": "Asst. Security Manager", "Dept": "HSE", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 14529, "Market": 15000},
    {"Designation": "Attendant", "Dept": "Production", "Tier": "Technical Operations", "HC": 9, "Pioneer": 1848, "Market": 4100},
    {"Designation": "Auto Garage Incharge", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 7000, "Market": 7000},
    {"Designation": "CCR Operator", "Dept": "Production", "Tier": "Technical Operations", "HC": 5, "Pioneer": 4070, "Market": 7750},
    {"Designation": "Chemist", "Dept": "QC", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5500, "Market": 9750},
    {"Designation": "Chief Engineer (Mechanical)", "Dept": "Mechanical", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 14685, "Market": 25000},
    {"Designation": "Cook", "Dept": "Admin", "Tier": "Technical Operations", "HC": 3, "Pioneer": 2151, "Market": 2500},
    {"Designation": "DEPUTY HR MANAGER", "Dept": "HR", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 9500, "Market": 16500},
    {"Designation": "Diesel Mechanic", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 3000, "Market": 5000},
    {"Designation": "Driver", "Dept": "Admin", "Tier": "Technical Operations", "HC": 5, "Pioneer": 2907, "Market": 4750},
    {"Designation
