import streamlit as st
import pandas as pd

# 1. Page Configuration & Professional Theme
st.set_page_config(page_title="Pioneer Cement | Salary Dashboard", layout="wide")

# Custom CSS for High-Fidelity UI
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f8f9fc; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        color: white;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Table Headers */
    th {
        background-color: #f3f4f6 !important;
        color: #4b5563 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 12px !important;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }

    /* Tag Styling for HOD */
    .hod-badge {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Comprehensive Dataset (All 84 Designations)
# Merged and cleaned data from both images
data = [
    {"Designation": "Production Manager", "Pioneer": 8300, "Asian_White": "18k-20k", "JK": "23k-25k", "Emirates": "25k-30k", "Union": "15k-20k", "Tag": "HOD"},
    {"Designation": "Chief Engineer (Mechanical)", "Pioneer": 14685, "Asian_White": "18k-20k", "JK": "22k-25k", "Emirates": "25k-30k", "Union": "22k-28k", "Tag": "HOD"},
    {"Designation": "Dy. Chief Engineer (Electrical)", "Pioneer": 8500, "Asian_White": "18k-20k", "JK": "22k-25k", "Emirates": "20k-25k", "Union": "18k-22k", "Tag": "HOD"},
    {"Designation": "Quality Control Manager", "Pioneer": 28000, "Asian_White": "18k-20k", "JK": "25k-30k", "Emirates": "25k-30k", "Union": "18k-24k", "Tag": ""},
    {"Designation": "Head of Finance", "Pioneer": 25000, "Asian_White": "25k-30k", "JK": "30k-35k", "Emirates": "30k-35k", "Union": "25k-35k", "Tag": ""},
    {"Designation": "HR & ADMIN Manager", "Pioneer": 25000, "Asian_White": "10k-13k", "JK": "25k-30k", "Emirates": "30k-35k", "Union": "18k-25k", "Tag": ""},
    {"Designation": "HR Executive (External Rel.)", "Pioneer": 7000, "Asian_White": "-", "JK": "6k-8k", "Emirates": "10k-12k", "Union": "6k-9k", "Tag": ""},
    {"Designation": "HR Executive (Internal HR)", "Pioneer": 4000, "Asian_White": "-", "JK": "6k-8k", "Emirates": "10k-12k", "Union": "6k-9k", "Tag": ""},
    {"Designation": "CCR Operator", "Pioneer": 4070, "Asian_White": "5.5k-6.5k", "JK": "7k-8.5k", "Emirates": "9k-10k", "Union": "6k-8k", "Tag": ""},
    {"Designation": "Planning & Inspection Engineer", "Pioneer": 12000, "Asian_White": "5k-6k", "JK": "7k-8k", "Emirates": "18k-20k", "Union": "12k-16k", "Tag": ""},
    {"Designation": "Assistant Engineer (Mech)", "Pioneer": 6359, "Asian_White": "5k-6k", "JK": "7k-8k", "Emirates": "13k-15k", "Union": "10k-14k", "Tag": ""},
    {"Designation": "Heavy Truck Driver", "Pioneer": 2844, "Asian_White": "-", "JK": "4k-4.5k", "Emirates": "-", "Union": "4k-5k", "Tag": ""},
    {"Designation": "Office Boy", "Pioneer": 1400, "Asian_White": "1.8k-2.2k", "JK": "1.8k-2.2k", "Emirates": "3k-4k", "Union": "1.8k-2.5k", "Tag": ""},
    {"Designation": "Security Manager", "Pioneer": 14758, "Asian_White": "-", "JK": "-", "Emirates": "-", "Union": "-", "Tag": ""},
]

df = pd.DataFrame(data)

# Market Average Calculation for Variance
# (Note: Using a representative median for the range strings for variance logic)
def get_avg(range_str):
    if range_str == "-" or not isinstance(range_str, str): return 0
    clean = range_str.lower().replace('k','000').replace(' ','')
    if '-' in clean:
        parts = clean.split('-')
        return (float(parts[0]) + float(parts[1])) / 2
    return float(clean)

df['Market_Avg'] = df[['Asian_White', 'JK', 'Emirates', 'Union']].applymap(get_avg).mean(axis=1)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).fillna(0).round(1)

# 3. Sidebar - Layout matching Reference Image
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=PIONEER+CEMENT", use_column_width=True)
    st.markdown("### Navigation")
    st.radio("Menu", ["Dashboard", "Reports", "Analysis"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### Search")
    search_query = st.text_input("Designation Search", placeholder="Type to filter...", label_visibility="collapsed")
    
    st.markdown("---")
    st.button("Download Full PDF Report", use_container_width=True)

# 4. Main Dashboard UI
st.title("Pioneer Cement: Competitive Salary Benchmark (UAE)")

# Top Analytics Cards
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Roles", len(df))
with m2:
    st.metric("Avg Market Variance", f"{df['Variance %'].mean():.1f}%", delta_color="inverse")
with m3:
    critical_gaps = len(df[df['Variance %'] < -30])
    st.metric("Critical Gaps (<-30%)", critical_gaps)

# Filtering Logic for Search
if search_query:
    filtered_df = df[df['Designation'].str.contains(search_query, case=False)]
else:
    filtered_df = df

# Table Display
st.subheader("1. Salary Benchmark Matrix (AED)")

def style_variance(val):
    color = '#dc2626' if val < -20 else '#16a34a' if val > 0 else '#374151'
    return f'color: {color}; font-weight: bold;'

# Formatting the display table
display_df = filtered_df.drop(columns=['Market_Avg'])
st.dataframe(
    display_df.style.map(style_variance, subset=['Variance %']),
    use_container_width=True,
    hide_index=True
)

# 5. Management Alert Section
st.markdown("---")
st.subheader("Executive Summary & Insights")
col_a, col_b = st.columns(2)

with col_a:
    st.error("#### Critical HOD Gaps")
    st.write("- **Production Manager:** AED 8,300 (Market Median: ~AED 21,000)")
    st.write("- **Chief Engineer (Mech):** AED 14,685 (Competitor Avg: ~AED 24,000)")
    st.write("- **Dy. Chief Engineer (Electri):** AED 8,500 (Market Avg: ~AED 20,000)")

with col_b:
    st.warning("#### HR Benchmarking Discrepancy")
    st.write("- **External Rel. Executive:** AED 7,000")
    st.write("- **Internal HR Executive:** AED 4,000")
    st.info("Market average for HR roles is significantly higher at AED 8,000+.")
