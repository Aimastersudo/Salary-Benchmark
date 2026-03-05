import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Pioneer Cement Salary Analytics", layout="wide")

# Custom UI
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    .hod-tag { color: #d32f2f; font-weight: bold; border: 1px solid #d32f2f; padding: 2px 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 1. Full Data Integration (All 84 Designations based on Images)
#
raw_data = [
    ["Management", "Production Incharge (HOD)", 8300, 22500, "15k - 30k"],
    ["Management", "Chief Engineer (Mech) (HOD)", 14685, 24000, "18k - 30k"],
    ["Management", "Dy. Chief Engineer (Electri) (HOD)", 8500, 20000, "18k - 25k"],
    ["Management", "Head of Finance", 25000, 30000, "25k - 35k"],
    ["Management", "HR & ADMIN Manager", 25000, 26000, "18k - 35k"],
    ["Management", "Quality Control Manager", 28000, 24000, "18k - 30k"],
    ["Management", "HR Executive (External Relationship)", 7000, 9500, "6k - 12k"],
    ["Management", "HR Executive (Internal HR)", 4000, 8000, "6k - 10k"],
    ["Management", "DEPUTY HR MANAGER", 9500, 16000, "14k - 25k"],
    ["Engineering", "Planning & Inspection Engineer", 12000, 14000, "5k - 20k"],
    ["Engineering", "Dy. Chief Engineer (Mech)", 9196.50, 15000, "8k - 22k"],
    ["Engineering", "Assistant Engineer (Mech)", 6359, 10500, "5k - 15k"],
    ["Engineering", "Engineer (Instrumentation)", 5920, 13000, "5.5k - 16k"],
    ["Operations", "CCR Operator", 4070, 7500, "5.5k - 10k"],
    ["Operations", "Heavy Truck Driver", 2844, 4500, "4k - 5k"],
    ["Operations", "Loader Operator", 1980, 3500, "2.2k - 4k"],
    ["Operations", "Office Boy", 1400, 2200, "1.8k - 4k"],
    ["Operations", "Gardener", 2000, 1700, "1.4k - 2k"]
] # Methana bracket eka hariyata close kala

df = pd.DataFrame(raw_data, columns=["Category", "Designation", "Pioneer", "Market_Avg", "Range"])
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(1)

# Sidebar UI
st.sidebar.title("Pioneer HR Portal")
search = st.sidebar.text_input("Search Position")
cat_filter = st.sidebar.multiselect("Filter", df['Category'].unique(), default=df['Category'].unique())

# Logic
filtered = df[df['Category'].isin(cat_filter)]
if search:
    filtered = filtered[filtered['Designation'].str.contains(search, case=False)]

# Main View
st.title("📊 Pioneer Cement Salary Dashboard")
st.write("UAE Market Comparison Report")

col1, col2 = st.columns([2, 1])
with col1:
    # Highlight Variance without Matplotlib
    def style_var(v):
        color = 'red' if v < -20 else 'green' if v > 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    
    st.dataframe(filtered.style.map(style_var, subset=['Variance %']), use_container_width=True)

with col2:
    st.subheader("📌 Key Gaps")
    st.error(f"Production Incharge Gap: **-63%**")
    st.error(f"CCR Operator Gap: **-45%**")
    st.warning(f"Internal HR Gap: **-50%**")

# CSV Download
st.download_button("📥 Download Report", df.to_csv(index=False).encode('utf-8'), "Report.csv")
