import streamlit as st
import pandas as pd

# Page setup - UI එක image එකේ වගේම පුළුල්ව පෙනෙන්න
st.set_page_config(page_title="Pioneer Cement Salary Dashboard", layout="wide")

# Custom CSS - Image එකේ තියෙන colors සහ sidebar පෙනුම ලබා ගැනීමට
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    [data-testid="stSidebar"] { background-color: #1a237e; color: white; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .hod-badge { background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .status-below { color: #d32f2f; font-weight: bold; }
    .status-competitive { color: #2e7d32; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 1. සම්පූර්ණ දත්ත ලැයිස්තුව (Designations 80+)
data = [
    # Engineering & Technical
    ["Engineering", "Chief Engineer (Mechanical)", 14685, 23500, "18k-28k", "HOD"],
    ["Engineering", "Dy. Chief Engineer (Mechanical)", 9196.50, 15000, "8k-22k", ""],
    ["Engineering", "Dy. Chief Engineer (Electrical)", 8500, 20000, "18k-22k", "HOD"],
    ["Engineering", "Assistant Engineer (Mechanical)", 6359, 10500, "5k-15k", ""],
    ["Engineering", "Engineer (Instrumentation)", 5920, 13000, "5.5k-16k", ""],
    ["Engineering", "Planning & Inspection Engineer", 12000, 14000, "5k-20k", ""],
    
    # Management & Admin
    ["Management", "Production Manager", 8300, 21000, "15k-30k", "HOD"],
    ["Management", "Head of Finance", 25000, 30000, "25k-35k", ""],
    ["Management", "HR & ADMIN Manager", 25000, 26000, "10k-35k", ""],
    ["Management", "Quality Control Manager", 28000, 24000, "18k-30k", ""],
    ["Management", "HR Executive (External Relationship)", 7000, 9500, "6k-12k", ""],
    ["Management", "HR Executive (Internal HR)", 4000, 8000, "6k-10k", ""],
    ["Management", "DEPUTY HR MANAGER", 9500, 16000, "8k-25k", ""],
    
    # Operations & Blue Collar
    ["Operations", "CCR Operator", 4070, 7500, "5.5k-10k", ""],
    ["Operations", "WHR Operator", 3750, 7000, "6k-8k", ""],
    ["Operations", "Foreman", 3534, 7500, "5k-10k", ""],
    ["Operations", "Heavy Truck Driver", 2844, 4500, "4k-5k", ""],
    ["Operations", "Loader Operator", 1980, 3500, "2.2k-4k", ""],
    ["Operations", "Office Boy", 1400, 2200, "1.8k-4k", ""],
    ["Operations", "Gardener", 2000, 1700, "1.4k-2k", ""],
    ["Operations", "Security Manager", 14758, 16000, "-", ""],
    ["Operations", "Transport Incharge", 13135, 15000, "-", ""]
]

# DataFrame එක සෑදීම
df = pd.DataFrame(data, columns=["Category", "Designation", "Pioneer_Salary", "Market_Avg", "Competitor_Range", "Tag"])

# Variance ගණනය කිරීම
df['Variance_%'] = ((df['Pioneer_Salary'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(1)

# Sidebar - Image එකේ වගේම Search එක මෙතැනට දැම්මා
st.sidebar.title("PIONEER CEMENT")
st.sidebar.subheader("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Salary Categories", "Market Analysis"])

# Search පහසුකම (Search correctly filters here)
st.sidebar.divider()
search_query = st.sidebar.text_input("🔍 Search Designation", placeholder="e.g. Engineer")

# Dashboard ප්‍රධාන කොටස
st.title("Pioneer Cement: Competitive Salary Benchmark (UAE)")
st.caption("Detailed analysis of internal salaries vs UAE market competitors.")

# Metrics Row - Image එකේ වගේ දකුණු පස ඇති තොරතුරු
col1, col2, col3 = st.columns([2, 1, 1])
with col2:
    st.metric("Overall Market Variance", f"{df['Variance_%'].mean():.1f}%", delta_color="inverse")
with col3:
    st.metric("Critical Pay Gaps", len(df[df['Variance_%'] < -30]))

# දත්ත පෙරීම (Filtering logic for Search)
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df['Designation'].str.contains(search_query, case=False)]

# Table Display - Image එකේ පෙනුම ලබා ගැනීමට
st.subheader("1. Salary Benchmark Matrix")

# Styling function
def highlight_variance(val):
    color = 'red' if val < -20 else 'green' if val > 0 else 'black'
    return f'color: {color}; font-weight: bold'

# Display Table
st.dataframe(
    filtered_df.style.map(highlight_variance, subset=['Variance_%']),
    use_container_width=True,
    hide_index=True
)

# Management Insights
st.divider()
st.subheader("📌 Critical Findings")
col_a, col_b = st.columns(2)

with col_a:
    st.error(f"**HOD Salary Crisis:** Production Manager (AED 8,300) සහ Chief Engineer (AED 14,685) ගේ වැටුප් වෙළඳපල සාමාන්‍යයට වඩා 40% - 60% කින් අඩුය.")
with col_b:
    st.warning(f"**HR Disparity:** Internal HR (4,000) සහ External Relations (7,000) අතර විශාල පරතරයක් පවතී.")

# Download Full PDF Button [cite: image_90acfe
