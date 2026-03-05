import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pioneer Cement Salary Analytics", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background-color: white; border-radius: 10px; }
    .hod-badge { color: #d32f2f; font-weight: bold; border: 1px solid #d32f2f; padding: 2px 5px; border-radius: 5px; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 1. Data Preparation - All 80+ Designations based on Images
#
raw_data = [
    # MANAGEMENT & HODs
    ["Management", "Production Incharge (HOD)", 8300, 22500, "15k - 30k"],
    ["Management", "Chief Engineer (Mech) (HOD)", 14685, 24000, "18k - 30k"],
    ["Management", "Dy. Chief Engineer (Electri) (HOD)", 8500, 20000, "18k - 25k"],
    ["Management", "Head of Finance", 25000, 30000, "25k - 35k"],
    ["Management", "HR & ADMIN Manager", 25000, 26000, "18k - 35k"],
    ["Management", "Quality Control Manager", 28000, 24000, "18k - 30k"],
    ["Management", "HR Executive (External Relations)", 7000, 9500, "6k - 12k"],
    ["Management", "HR Executive (Internal HR)", 4000, 8000, "6k - 10k"],
    ["Management", "DEPUTY HR MANAGER", 9500, 16000, "14k - 25k"],
    
    # ENGINEERING & TECHNICAL
    ["Engineering", "Planning & Inspection Engineer", 12000, 14000, "5k - 20k"],
    ["Engineering", "Dy. Chief Engineer (Mech)", 9196.50, 15000, "8k - 22k"],
    ["Engineering", "Assistant Engineer (Mech)", 6359, 10500, "5k - 15k"],
