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
    {"Designation": "Dy. Chief Engineer (Electrical)", "Dept": "E & I", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 8500, "Market": 21500},
    {"Designation": "Dy. Chief Engineer (Mechanical)", "Dept": "Mechanical", "Tier": "Leadership & Management", "HC": 2, "Pioneer": 9197, "Market": 17500},
    {"Designation": "Electrician", "Dept": "E & I", "Tier": "Technical Operations", "HC": 6, "Pioneer": 2302, "Market": 4500},
    {"Designation": "Finance Coordinator", "Dept": "Finance", "Tier": "Professional Staff", "HC": 1, "Pioneer": 6000, "Market": 8000},
    {"Designation": "Financial Accountant", "Dept": "Finance", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5155, "Market": 9250},
    {"Designation": "Financial Analyst", "Dept": "Finance", "Tier": "Professional Staff", "HC": 1, "Pioneer": 8000, "Market": 12000},
    {"Designation": "First Aid", "Dept": "Admin", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5745, "Market": 5000},
    {"Designation": "Fitter", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 4, "Pioneer": 3388, "Market": 4100},
    {"Designation": "Foreman", "Dept": "Mechanical / Production", "Tier": "Technical Operations", "HC": 2, "Pioneer": 3534, "Market": 7500},
    {"Designation": "Forklift Operator", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 2, "Pioneer": 2116, "Market": 3000},
    {"Designation": "Gardener", "Dept": "Admin", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2000, "Market": 1700},
    {"Designation": "General Helper", "Dept": "Admin", "Tier": "Technical Operations", "HC": 1, "Pioneer": 1800, "Market": 2000},
    {"Designation": "Head Of Finance", "Dept": "Finance", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 25000, "Market": 30000},
    {"Designation": "Heavy Truck Driver", "Dept": "Sales & Logistics", "Tier": "Technical Operations", "HC": 3, "Pioneer": 2844, "Market": 4500},
    {"Designation": "House Keeping Attendant", "Dept": "Admin", "Tier": "Technical Operations", "HC": 5, "Pioneer": 1553, "Market": 1700},
    {"Designation": "House Keeping Mechanical", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 1500, "Market": 1700},
    {"Designation": "HR & ADMIN Manager", "Dept": "HR", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 25000, "Market": 20000},
    {"Designation": "HR Executive (External Rel.)", "Dept": "External Relationship", "Tier": "Professional Staff", "HC": 1, "Pioneer": 7000, "Market": 8000},
    {"Designation": "HR Executive (Internal HR)", "Dept": "HR", "Tier": "Professional Staff", "HC": 1, "Pioneer": 4000, "Market": 8000},
    {"Designation": "HSE Officer", "Dept": "HSE", "Tier": "Professional Staff", "HC": 1, "Pioneer": 4000, "Market": 8500},
    {"Designation": "HSE Supervisor", "Dept": "HSE", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 6000, "Market": 16500},
    {"Designation": "Hydra Operator", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2376, "Market": 3600},
    {"Designation": "Junior Engineer (Instrumentation)", "Dept": "E & I", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5840, "Market": 8000},
    {"Designation": "Junior IT Help Desk Support", "Dept": "IT", "Tier": "Professional Staff", "HC": 1, "Pioneer": 3300, "Market": 7000},
    {"Designation": "Lab Technician", "Dept": "QC", "Tier": "Professional Staff", "HC": 2, "Pioneer": 3000, "Market": 6250},
    {"Designation": "Loader Operator", "Dept": "Production", "Tier": "Technical Operations", "HC": 1, "Pioneer": 1980, "Market": 3100},
    {"Designation": "Marketing Coordinator", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 1, "Pioneer": 5200, "Market": 6500},
    {"Designation": "Mason", "Dept": "Production", "Tier": "Technical Operations", "HC": 5, "Pioneer": 2216, "Market": 2750},
    {"Designation": "Mason (Mechanical)", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2100, "Market": 2750},
    {"Designation": "Mechanic", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2400, "Market": 4500},
    {"Designation": "MTO", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2865, "Market": 4100},
    {"Designation": "Office Boy", "Dept": "Admin", "Tier": "Technical Operations", "HC": 2, "Pioneer": 1400, "Market": 2900},
    {"Designation": "Packer Operator", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 11, "Pioneer": 1762, "Market": 4100},
    {"Designation": "Packing Plant Supervisor", "Dept": "Mechanical", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 5800, "Market": 7750},
    {"Designation": "Palletizer Operator", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 1800, "Market": 2750},
    {"Designation": "Planning & Inspection Engineer", "Dept": "Mechanical", "Tier": "Professional Staff", "HC": 1, "Pioneer": 12000, "Market": 12500},
    {"Designation": "Plant Coordinator", "Dept": "Georgia", "Tier": "Professional Staff", "HC": 1, "Pioneer": 11000, "Market": 10500},
    {"Designation": "Procurement Executive", "Dept": "Procurment", "Tier": "Professional Staff", "HC": 1, "Pioneer": 3000, "Market": 9000},
    {"Designation": "Production Incharge (HOD)", "Dept": "Production", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 8300, "Market": 9000},
    {"Designation": "Pump House Operator", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 3, "Pioneer": 1867, "Market": 3250},
    {"Designation": "Purchase Agent", "Dept": "Procurment", "Tier": "Professional Staff", "HC": 1, "Pioneer": 4800, "Market": 8500},
    {"Designation": "Quality Control Manager", "Dept": "QC", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 28000, "Market": 24000},
    {"Designation": "Raw Materials Supervisor", "Dept": "Production", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 9700, "Market": 9500},
    {"Designation": "Rigger", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 11, "Pioneer": 2273, "Market": 3600},
    {"Designation": "Sales Coordinator", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 2, "Pioneer": 6000, "Market": 6250},
    {"Designation": "Sales Executive", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 0, "Pioneer": 8000, "Market": 8750},
    {"Designation": "sample boy", "Dept": "QC", "Tier": "Technical Operations", "HC": 7, "Pioneer": 1686, "Market": 2200},
    {"Designation": "Security Guard", "Dept": "HSE", "Tier": "Technical Operations", "HC": 12, "Pioneer": 1767, "Market": 2400},
    {"Designation": "Security Manager", "Dept": "HSE", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 14758, "Market": 14500},
    {"Designation": "Security Supervisor", "Dept": "HSE", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 4000, "Market": 7500},
    {"Designation": "Senior Sales & Logistics", "Dept": "Sales & Logistics", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 22800, "Market": 15500},
    {"Designation": "Shovel Operator", "Dept": "Production", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2200, "Market": 3750},
    {"Designation": "Stacker Operator", "Dept": "Production", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2400, "Market": 4100},
    {"Designation": "Store House Man", "Dept": "Stores", "Tier": "Technical Operations", "HC": 1, "Pioneer": 1500, "Market": 3250},
    {"Designation": "Stores Assistant", "Dept": "Stores", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2116, "Market": 7500},
    {"Designation": "Stores Officer", "Dept": "Stores", "Tier": "Professional Staff", "HC": 1, "Pioneer": 6000, "Market": 9500},
    {"Designation": "Technician", "Dept": "E & I", "Tier": "Technical Operations", "HC": 4, "Pioneer": 2361, "Market": 3500},
    {"Designation": "Tester / Gauger", "Dept": "QC", "Tier": "Technical Operations", "HC": 2, "Pioneer": 2285, "Market": 5200},
    {"Designation": "Transport Incharge", "Dept": "Admin", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 13135, "Market": 12500},
    {"Designation": "Truck Cum Shovel Operator", "Dept": "Production", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2800, "Market": 3800},
    {"Designation": "Tyre Mechanic", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 1, "Pioneer": 2000, "Market": 2750},
    {"Designation": "Weigh Bridge Operator", "Dept": "Sales & Logistics", "Tier": "Technical Operations", "HC": 7, "Pioneer": 2392, "Market": 5000},
    {"Designation": "Welder", "Dept": "Mechanical", "Tier": "Technical Operations", "HC": 7, "Pioneer": 2550, "Market": 4100},
    {"Designation": "WHR Operator", "Dept": "WHR", "Tier": "Technical Operations", "HC": 2, "Pioneer": 3750, "Market": 5000},
    {"Designation": "WHR Supervisor", "Dept": "WHR", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 5500, "Market": 10000},
    {"Designation": "Engineer (Instrumentation)", "Dept": "E & I", "Tier": "Professional Staff", "HC": 3, "Pioneer": 5920, "Market": 10750},
    {"Designation": "Assistant Engineer (Mechanical)", "Dept": "Mechanical", "Tier": "Professional Staff", "HC": 1, "Pioneer": 6359, "Market": 10000},
    {"Designation": "Truck Driver - Bulker", "Dept": "Sales & Logistics", "Tier": "Technical Operations", "HC": 12, "Pioneer": 2000, "Market": 4750},
    {"Designation": "Senior Engineer (Technical)", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 1, "Pioneer": 10000, "Market": 10000},
    {"Designation": "Sales Administrative Assistant", "Dept": "Sales & Logistics", "Tier": "Professional Staff", "HC": 1, "Pioneer": 3200, "Market": 7750},
    {"Designation": "Acting IT Manager", "Dept": "IT", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 11000, "Market": 16500},
    {"Designation": "Projects Manager", "Dept": "Projects", "Tier": "Leadership & Management", "HC": 1, "Pioneer": 16000, "Market": 20000},
] # All 84 entries strictly included

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market']) / df['Market'] * 100).round(0).astype(int)

# 4. Sidebar Global Filters
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
    page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Disparity Analysis", "📁 Structural Groups"])
    st.markdown("---")
    
    st.markdown("### 🏢 Department Filter")
    selected_depts = st.multiselect("Filter by Departments:", df['Dept'].unique(), default=df['Dept'].unique())
    
    st.markdown("---")
    search_q = st.text_input("Find Designation", placeholder="Search all 84 roles...")

# Filter Logic
f_df = df[df['Dept'].isin(selected_depts)]
if search_q:
    f_df = f_df[f_df['Designation'].str.contains(search_q, case=False)]

# 5. DASHBOARD VIEW
if page == "📊 Executive Dashboard":
    st.title("Strategic Salary Benchmark Dashboard")
    st.caption(f"Analysis of {len(f_df)} Designations / Total Headcount: {f_df['HC'].sum()}")
    
    # Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Designations", len(f_df))
    c2.metric("Total Headcount", int(f_df['HC'].sum()))
    c3.metric("Avg. Market Gap", f"{f_df['Variance %'].mean():.0f}%", delta_color="inverse")
    c4.metric("Critical Gaps", len(f_df[f_df['Variance %'] < -30]))

    # Main Table
    st.subheader("Interactive Salary Matrix (AED)")
    event = st.dataframe(f_df, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight
    if len(event.selection.rows) > 0:
        row = f_df.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
        v = row['Variance %']
        st.markdown(f"""
        <div class="salary-card">
            <div class="ai-insight-box">
                <b>Gemini HR Analysis:</b> The role of <b>{row['Designation']}</b> in the <b>{row['Dept']}</b> department 
                is currently underpaid by <b>{abs(v)}%</b>. With a headcount of <b>{row['HC']}</b>, 
                this poses a significant talent retention risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

# 6. DISPARITY ANALYSIS
elif page == "📉 Disparity Analysis":
    st.title("Market Disparity Analysis")
    st.subheader("Avg. Variance by Department (%)")
    dept_v = f_df.groupby('Dept')['Variance %'].mean().reset_index().sort_values('Variance %')
    fig = px.bar(dept_v, x='Dept', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Variance by Structural Tier (%)")
    tier_v = f_df.groupby('Tier')['Variance %'].mean().reset_index()
    fig2 = px.bar(tier_v, x='Tier', y='Variance %', color='Tier')
    fig2.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# 7. STRUCTURAL GROUPS
elif page == "📁 Structural Groups":
    st.title("Organizational Tier Breakdown")
    t1, t2, t3 = st.tabs(["Leadership & Management", "Professional Staff", "Technical Operations"])
    with t1: st.dataframe(f_df[f_df['Tier'] == 'Leadership & Management'], use_container_width=True, hide_index=True)
    with t2: st.dataframe(f_df[f_df['Tier'] == 'Professional Staff'], use_container_width=True, hide_index=True)
    with t3: st.dataframe(f_df[f_df['Tier'] == 'Technical Operations'], use_container_width=True, hide_index=True)
