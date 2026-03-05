import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR Intelligence", layout="wide")

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

# 3. GLOBAL DATABASE (ALL 84 DESIGNATIONS FROM YOUR LIST)
FULL_DB = [
    {"Designation": "Accountant", "Pioneer": 6500, "Market_Avg": 9250},
    {"Designation": "Admin Assistant", "Pioneer": 3000, "Market_Avg": 4750},
    {"Designation": "Assistant Engineer (Production)", "Pioneer": 3813, "Market_Avg": 10000},
    {"Designation": "Assistant Sales Manager", "Pioneer": 9500, "Market_Avg": 14250},
    {"Designation": "Assistant Stores Manager", "Pioneer": 18413, "Market_Avg": 10500},
    {"Designation": "Asst. External Relationship Manager", "Pioneer": 21493, "Market_Avg": 14000},
    {"Designation": "Asst. Public Relation Officer", "Pioneer": 11859, "Market_Avg": 9000},
    {"Designation": "Asst. Security Manager", "Pioneer": 14529, "Market_Avg": 15000},
    {"Designation": "Attendant", "Pioneer": 1848, "Market_Avg": 4100},
    {"Designation": "CCR Operator", "Pioneer": 4070, "Market_Avg": 7750},
    {"Designation": "Chief Engineer (Mechanical) (HOD)", "Pioneer": 14685, "Market_Avg": 25000},
    {"Designation": "Cook", "Pioneer": 2151, "Market_Avg": 2500},
    {"Designation": "DEPUTY HR MANAGER", "Pioneer": 9500, "Market_Avg": 16500},
    {"Designation": "Driver", "Pioneer": 2907, "Market_Avg": 4750},
    {"Designation": "Dy. Chief Engineer (Electrical) (HOD)", "Pioneer": 8500, "Market_Avg": 21500},
    {"Designation": "Dy. Chief Engineer (Mechanical)", "Pioneer": 9197, "Market_Avg": 17500},
    {"Designation": "Electrician", "Pioneer": 2302, "Market_Avg": 4500},
    {"Designation": "Finance Coordinator", "Pioneer": 6000, "Market_Avg": 8000},
    {"Designation": "Financial Accountant", "Pioneer": 5155, "Market_Avg": 9250},
    {"Designation": "Financial Analyst", "Pioneer": 8000, "Market_Avg": 12000},
    {"Designation": "First Aid", "Pioneer": 5745, "Market_Avg": 5000},
    {"Designation": "Fitter", "Pioneer": 3388, "Market_Avg": 4100},
    {"Designation": "Foreman", "Pioneer": 3534, "Market_Avg": 7500},
    {"Designation": "Forklift Operator", "Pioneer": 2116, "Market_Avg": 3000},
    {"Designation": "Gardener", "Pioneer": 2000, "Market_Avg": 1700},
    {"Designation": "General Helper", "Pioneer": 1800, "Market_Avg": 2000},
    {"Designation": "Head of Finance", "Pioneer": 25000, "Market_Avg": 30000},
    {"Designation": "Heavy Truck Driver", "Pioneer": 2844, "Market_Avg": 4500},
    {"Designation": "House Keeping Attendant", "Pioneer": 1553, "Market_Avg": 1700},
    {"Designation": "House Keeping Mechanical", "Pioneer": 1500, "Market_Avg": 1700},
    {"Designation": "HR & ADMIN Manager", "Pioneer": 25000, "Market_Avg": 20000},
    {"Designation": "HR Executive (External Relations)", "Pioneer": 7000, "Market_Avg": 8000},
    {"Designation": "HR Executive (Internal HR)", "Pioneer": 4000, "Market_Avg": 8000},
    {"Designation": "HSE Officer", "Pioneer": 4000, "Market_Avg": 8500},
    {"Designation": "HSE Supervisor", "Pioneer": 6000, "Market_Avg": 16500},
    {"Designation": "Hydra Operator", "Pioneer": 2376, "Market_Avg": 3600},
    {"Designation": "Junior Engineer (Instrumentation)", "Pioneer": 5840, "Market_Avg": 8000},
    {"Designation": "Junior IT Help Desk Support", "Pioneer": 3300, "Market_Avg": 7000},
    {"Designation": "Lab Technician", "Pioneer": 3000, "Market_Avg": 6250},
    {"Designation": "Loader Operator", "Pioneer": 1980, "Market_Avg": 3100},
    {"Designation": "Marketing Coordinator", "Pioneer": 5200, "Market_Avg": 6500},
    {"Designation": "Mason", "Pioneer": 2216, "Market_Avg": 2750},
    {"Designation": "Mechanic", "Pioneer": 2400, "Market_Avg": 4500},
    {"Designation": "Office Boy", "Pioneer": 1400, "Market_Avg": 2900},
    {"Designation": "Packer Operator", "Pioneer": 1762, "Market_Avg": 4100},
    {"Designation": "Packing Plant Supervisor", "Pioneer": 5800, "Market_Avg": 7750},
    {"Designation": "Palletizer Operator", "Pioneer": 1800, "Market_Avg": 2750},
    {"Designation": "Planning & Inspection Engineer", "Pioneer": 12000, "Market_Avg": 12500},
    {"Designation": "Plant Coordinator", "Pioneer": 11000, "Market_Avg": 10500},
    {"Designation": "Procurement Executive", "Pioneer": 3000, "Market_Avg": 9000},
    {"Designation": "Production Incharge (HOD)", "Pioneer": 8300, "Market_Avg": 9000},
    {"Designation": "Pump House Operator", "Pioneer": 1867, "Market_Avg": 3250},
    {"Designation": "Purchase Agent", "Pioneer": 4800, "Market_Avg": 8500},
    {"Designation": "Quality Control Manager", "Pioneer": 28000, "Market_Avg": 24000},
    {"Designation": "Raw Materials Supervisor", "Pioneer": 9700, "Market_Avg": 9500},
    {"Designation": "Rigger", "Pioneer": 2273, "Market_Avg": 3600},
    {"Designation": "Sales Coordinator", "Pioneer": 6000, "Market_Avg": 6250},
    {"Designation": "Sales Executive", "Pioneer": 8000, "Market_Avg": 8750},
    {"Designation": "Security Guard", "Pioneer": 1767, "Market_Avg": 2400},
    {"Designation": "Security Manager", "Pioneer": 14758, "Market_Avg": 14500},
    {"Designation": "Security Supervisor", "Pioneer": 4000, "Market_Avg": 7500},
    {"Designation": "Senior Sales & Logistics", "Pioneer": 22800, "Market_Avg": 15500},
    {"Designation": "Shovel Operator", "Pioneer": 2200, "Market_Avg": 3750},
    {"Designation": "Stacker Operator", "Pioneer": 2400, "Market_Avg": 4100},
    {"Designation": "Store House Man", "Pioneer": 1500, "Market_Avg": 3250},
    {"Designation": "Stores Assistant", "Pioneer": 2116, "Market_Avg": 7500},
    {"Designation": "Stores Officer", "Pioneer": 6000, "Market_Avg": 9500},
    {"Designation": "Technician", "Pioneer": 2361, "Market_Avg": 3500},
    {"Designation": "Tester / Gauger", "Pioneer": 2285, "Market_Avg": 5200},
    {"Designation": "Transport Incharge", "Pioneer": 13135, "Market_Avg": 12500},
    {"Designation": "Truck Cum Shovel Operator", "Pioneer": 2800, "Market_Avg": 3800},
    {"Designation": "Tyre Mechanic", "Pioneer": 2000, "Market_Avg": 2750},
    {"Designation": "Weigh Bridge Operator", "Pioneer": 2392, "Market_Avg": 5000},
    {"Designation": "Welder", "Pioneer": 2550, "Market_Avg": 4100},
    {"Designation": "WHR Operator", "Pioneer": 3750, "Market_Avg": 5000},
    {"Designation": "WHR Supervisor", "Pioneer": 5500, "Market_Avg": 10000},
    {"Designation": "Engineer (Instrumentation)", "Pioneer": 5920, "Market_Avg": 10750},
    {"Designation": "Assistant Engineer (Mechanical)", "Pioneer": 6359, "Market_Avg": 10000},
    {"Designation": "Truck Driver - Bulker", "Pioneer": 2000, "Market_Avg": 4750},
    {"Designation": "Senior Engineer (Technical)", "Pioneer": 10000, "Market_Avg": 10000},
    {"Designation": "Sales Administrative Assistant", "Pioneer": 3200, "Market_Avg": 7750},
    {"Designation": "Acting IT Manager", "Pioneer": 11000, "Market_Avg": 16500},
    {"Designation": "Projects Manager", "Pioneer": 16000, "Market_Avg": 20000},
] #

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
    st.markdown("### APP MENU")
    page = st.radio("Select View:", ["📊 Executive Dashboard", "📉 Market Variance Analysis", "📁 Category Breakdown"])
    st.markdown("---")
    search_q = st.text_input("Find Designation", placeholder="Search any of 84 roles...")

# 5. Dashboard View
if page == "📊 Executive Dashboard":
    st.title("Pioneer Cement: Salary Benchmark Dashboard")
    st.caption("Strategic Market Comparison (UAE 2026)")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Designations Scoped", len(df))
    c2.metric("Overall Market Variance", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
    c3.metric("Critical Pay Gaps", len(df[df['Variance %'] < -30]))

    # Filtered Search Data
    filtered = df[df['Designation'].str.contains(search_q, case=False)] if search_q else df
    st.subheader("Interactive Salary Matrix (AED)")
    event = st.dataframe(filtered, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight Section
    if len(event.selection.rows) > 0:
        row = filtered.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 AI Strategic Insight: {row['Designation']}")
        v = row['Variance %']
        st.markdown(f"""
        <div class="salary-card">
            <div class="ai-insight-box">
                <b>Gemini HR Verdict:</b> This role is currently positioned <b>{abs(v)}%</b> 
                {'below' if v < 0 else 'above'} market standards. 
                {"🚨 Immediate market correction is critical." if v < -35 else "⚠️ Talent retention risk detected." if v < -15 else "✅ Fair market compensation."}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 6. Analysis View (Gathi UI)
elif page == "📉 Market Variance Analysis":
    st.title("Market Disparity Analysis")
    st.write("Visualizing deviation from market median across 84 designations.")
    
    # Interactive Plotly Chart
    fig = px.bar(df.sort_values('Variance %'), x='Designation', y='Variance %', 
                 color='Variance %', color_continuous_scale='RdYlGn',
                 title="Salary Deviation by Role (%)")
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

elif page == "📁 Category Breakdown":
    st.title("Designation Categorization")
    t1, t2 = st.tabs(["Management & HOD", "Operations & Technical"])
    with t1:
        st.dataframe(df[df['Designation'].str.contains("HOD|Manager|Head|Chief", case=False)], use_container_width=True)
    with t2:
        st.dataframe(df[~df['Designation'].str.contains("HOD|Manager|Head|Chief", case=False)], use_container_width=True)
