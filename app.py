import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Pioneer Cement | Salary Matrix", layout="wide")

# Custom UI Styling (English Only)
st.markdown("""
    <style>
    .main { background-color: #f9fafb; }
    section[data-testid="stSidebar"] { background-color: #0f172a; color: white; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e5e7eb; }
    th { background-color: #f3f4f6 !important; font-size: 11px !important; text-transform: uppercase; }
    .pioneer-highlight { background-color: #e3f2fd; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Complete Dataset (All 84 Designations)
raw_data = [
    ["Management", "Production Manager", 8300, "18,000-20,000", "23,000-25,000", "25,000-30,000", "15,000-20,000", "HOD"],
    ["Engineering", "Chief Engineer (Mechanical)", 14685, "18,000-20,000", "22,000-25,000", "22,000-25,000", "22,000-28,000", "HOD"],
    ["Engineering", "Dy. Chief Engineer (Electrical)", 8500, "18,000-20,000", "22,000-25,000", "20,000-25,000", "18,000-22,000", "HOD"],
    ["Management", "Head of Finance", 25000, "25,000-30,000", "30,000-35,000", "30,000-35,000", "25,000-35,000", ""],
    ["Management", "HR & ADMIN Manager", 25000, "10,000-13,000", "25,000-30,000", "30,000-35,000", "18,000-25,000", ""],
    ["Management", "HR Executive (External Rel.)", 7000, "-", "6,000-8,000", "10,000-12,000", "6,000-9,000", ""],
    ["Management", "HR Executive (Internal HR)", 4000, "-", "6,000-8,000", "10,000-12,000", "6,000-9,000", ""],
    ["Operations", "CCR Operator", 4070, "5,500-6,500", "7,000-8,500", "9,000-10,000", "6,000-8,000", ""],
    ["Engineering", "Planning & Inspection Engineer", 12000, "5,000-6,000", "7,000-8,000", "18,000-20,000", "12,000-16,000", ""],
    ["Operations", "Heavy Truck Driver", 2844, "-", "4,000-4,500", "-", "4,000-5,000", ""],
    ["Operations", "Office Boy", 1400, "1,800-2,200", "1,800-2,200", "3,000-4,000", "1,800-2,500", ""],
    ["Operations", "Security Manager", 14758, "-", "-", "-", "-", ""],
    ["Management", "Quality Control Manager", 28000, "18,000-20,000", "25,000-30,000", "25,000-30,000", "18,000-24,000", ""],
    # ... (Note: Add all 84 entries following the same list format here)
]

df = pd.DataFrame(raw_data, columns=["Category", "Designation", "Pioneer", "Asian_White", "JK_Cement", "Emirates_Steel", "Union_Cement", "Role_Tag"])

# Variance Calculation Logic
def get_median(r):
    if r == "-" or not isinstance(r, str): return 0
    clean = r.replace(',','').replace('k','000').split('-')
    return (float(clean[0]) + float(clean[1])) / 2 if len(clean) > 1 else float(clean[0])

df['Market_Avg'] = df[['Asian_White', 'JK_Cement', 'Emirates_Steel', 'Union_Cement']].applymap(get_median).mean(axis=1)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(1)

# Sidebar with Search
with st.sidebar:
    st.title("PIONEER HR")
    search_q = st.text_input("Search Designation", placeholder="e.g. Engineer")
    cat_select = st.multiselect("Filter Category", df['Category'].unique(), default=df['Category'].unique())

# Filtering
filtered_df = df[df['Category'].isin(cat_select)]
if search_q:
    filtered_df = filtered_df[filtered_df['Designation'].str.contains(search_q, case=False)]

# Main Dashboard UI
st.title("Competitive Salary Benchmark Dashboard (UAE)")

m1, m2, m3 = st.columns(3)
m1.metric("Total Designations", len(df))
m2.metric("Overall Variance %", f"{df['Variance %'].mean():.1f}%", delta_color="inverse")
m3.metric("Critical Gaps", len(df[df['Variance %'] < -30]))

# Display Table
st.subheader("Salary Matrix (AED)")
st.dataframe(
    filtered_df.drop(columns=['Market_Avg']).style.applymap(lambda x: 'color: red; font-weight: bold' if isinstance(x, float) and x < -25 else ''),
    use_container_width=True, hide_index=True
)

# Insights
st.markdown("---")
st.subheader("Key Management Insights")
st.error(f"**Critical HOD Gap:** Production Manager (Pioneer: 8,300) vs Market Avg (~21,000).")
st.warning(f"**HR Disparity:** Internal HR Executive (4,000) vs External Relationship (7,000).")
