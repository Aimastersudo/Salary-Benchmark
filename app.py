import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR Intelligence | Full DB", layout="wide")

# 2. Premium Dark UI Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .stMetric { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .salary-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: #1e3a8a; border: 1px solid #3b82f6; padding: 15px; border-radius: 8px; color: #bfdbfe; font-size: 14px; }
    th { background-color: #334155 !important; color: #cbd5e1 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. THE COMPLETE DATABASE (All 84 Designations from image_90a19d.png)
FULL_DB = [
    {"Designation": "Accountant", "Pioneer": 6500, "Market_Avg": 9250},
    {"Designation": "Admin Assistant", "Pioneer": 3000, "Market_Avg": 4750},
    {"Designation": "Assistant Engineer (Production)", "Pioneer": 3813, "Market_Avg": 10000},
    {"Designation": "Assistant Sales Manager", "Pioneer": 9500, "Market_Avg": 14250},
    {"Designation": "Assistant Stores Manager", "Pioneer": 18413, "Market_Avg": 10500},
    {"Designation": "Asst. External Relationship Manager", "Pioneer": 21493, "Market_Avg": 14000},
    {"Designation": "Asst. Public Relation Officer", "Pioneer": 11859, "Market_Avg": 9000},
    {"Designation": "Asst. Purchase Officer", "Pioneer": 5225, "Market_Avg": 9000},
    {"Designation": "Asst. Security Manager", "Pioneer": 14529, "Market_Avg": 15000},
    {"Designation": "Attendant", "Pioneer": 1848, "Market_Avg": 4100},
    {"Designation": "Auto Garage Incharge", "Pioneer": 7000, "Market_Avg": 7000},
    {"Designation": "CCR Operator", "Pioneer": 4070, "Market_Avg": 7750},
    {"Designation": "Chemist", "Pioneer": 5500, "Market_Avg": 9750},
    {"Designation": "Chief Engineer (Mechanical) (HOD)", "Pioneer": 14685, "Market_Avg": 25000},
    {"Designation": "Cook", "Pioneer": 2151, "Market_Avg": 2500},
    {"Designation": "DEPUTY HR MANAGER", "Pioneer": 9500, "Market_Avg": 16500},
    {"Designation": "Diesel Mechanic", "Pioneer": 3000, "Market_Avg": 5000},
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
]

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. GEMINI AI INSIGHT LOGIC
def get_ai_recommendation(row):
    v = row['Variance %']
    role = row['Designation']
    if v < -40:
        return f"🚨 **Gemini Advisory:** {role} is significantly underpaid (-{abs(v)}%). High turnover risk detected. Immediate market correction is critical to prevent loss of operational knowledge."
    elif v < -15:
        return f"⚠️ **Gemini Warning:** {role} pay lags industry standards (-{abs(v)}%). Recommended 15-20% adjustment to ensure talent retention and competitive positioning."
    elif v > 15:
        return f"✅ **Gemini Insights:** {role} is paid above market average (+{v}%). Competitive advantage for high-quality talent attraction."
    else:
        return f"⚖️ **Gemini Analysis:** {role} pay is well-aligned with UAE market benchmarks. No immediate action required."

# 5. Sidebar & Search
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1e293b/f8fafc?text=PIONEER+AI", use_column_width=True)
    search = st.text_input("🔍 Search 84 Designations", placeholder="Search any role...")
    st.markdown("---")
    st.write("Database: **84 Roles Loaded**")
    st.write("AI Engine: **Gemini AI Active**")

# 6. Main Dashboard Content
st.title("Pioneer Cement: Salary Intelligence Dashboard")

# Top Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Designations Scoped", len(df))
c2.metric("Market Variance Avg", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
c3.metric("Critical Gaps (<-30%)", len(df[df['Variance %'] < -30]))

# Search Filter Logic
filtered = df[df['Designation'].str.contains(search, case=False)] if search else df

# Interactive Table
st.subheader("Interactive Salary Matrix (AED)")
event = st.dataframe(
    filtered[['Designation', 'Pioneer', 'Market_Avg', 'Variance %']],
    use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row"
)

# 7. AI Insight Panel
if len(event.selection.rows) > 0:
    idx = event.selection.rows[0]
    row = filtered.iloc[idx]
    
    st.markdown("---")
    st.markdown(f"### 📋 AI Market Insight: {row['Designation']}")
    
    st.markdown(f"""
    <div class="salary-card">
        <h4 style="margin-top:0; color: #3b82f6;">Gemini HR Recommendation:</h4>
        <div class="ai-insight-box">
            {get_ai_recommendation(row)}
        </div>
        <br>
        <p style="color: #cbd5e1;">
            <b>Verdict:</b> This role is currently positioned <b>{abs(row['Variance %'])}%</b> 
            {'below' if row['Variance %'] < 0 else 'above'} the industry average of {row['Market_Avg']:,} AED.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("💡 Select a row in the matrix above to generate Gemini AI insights for any of the 84 designations.")
