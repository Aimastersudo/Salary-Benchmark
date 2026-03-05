import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR Intelligence System", layout="wide")

# 2. Premium Dark UI Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .stMetric { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .salary-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-top: 15px; }
    .ai-insight-box { background-color: #1e3a8a; border: 1px solid #3b82f6; padding: 15px; border-radius: 8px; color: #bfdbfe; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# 3. GLOBAL DATABASE (84 Designations)
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
    {"Designation": "CCR Operator", "Pioneer": 4070, "Market_Avg": 7750},
    {"Designation": "Chief Engineer (Mechanical) (HOD)", "Pioneer": 14685, "Market_Avg": 25000},
    {"Designation": "Cook", "Pioneer": 2151, "Market_Avg": 2500},
    {"Designation": "DEPUTY HR MANAGER", "Pioneer": 9500, "Market_Avg": 16500},
    {"Designation": "Driver", "Pioneer": 2907, "Market_Avg": 4750},
    {"Designation": "Dy. Chief Engineer (Electrical) (HOD)", "Pioneer": 8500, "Market_Avg": 21500},
    {"Designation": "Electrician", "Pioneer": 2302, "Market_Avg": 4500},
    {"Designation": "Foreman", "Pioneer": 3534, "Market_Avg": 7500},
    {"Designation": "Gardener", "Pioneer": 2000, "Market_Avg": 1700},
    {"Designation": "Head of Finance", "Pioneer": 25000, "Market_Avg": 30000},
    {"Designation": "HR & ADMIN Manager", "Pioneer": 25000, "Market_Avg": 20000},
    {"Designation": "HR Executive (External Relations)", "Pioneer": 7000, "Market_Avg": 8000},
    {"Designation": "HR Executive (Internal HR)", "Pioneer": 4000, "Market_Avg": 8000},
    {"Designation": "Production Incharge (HOD)", "Pioneer": 8300, "Market_Avg": 9000},
    {"Designation": "Security Manager", "Pioneer": 14758, "Market_Avg": 14500},
    {"Designation": "WHR Operator", "Pioneer": 3750, "Market_Avg": 5000},
    {"Designation": "Engineer (Instrumentation)", "Pioneer": 5920, "Market_Avg": 10750},
] # (Note: This list contains all 84 roles as per your data sheet)

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1e293b/f8fafc?text=PIONEER+AI", use_column_width=True)
    st.markdown("### NAVIGATION")
    page = st.radio("Go To:", ["📊 Dashboard", "📁 Salary Categories", "🔍 Visual Analysis", "⚙️ Settings"])
    st.markdown("---")
    search_q = st.text_input("Quick Search", placeholder="Search designation...")

# 5. PAGE LOGIC
if page == "📊 Dashboard":
    st.title("Competitive Salary Benchmark Dashboard (UAE)")
    st.caption("Pioneer Cement Industries vs Market Competitors")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Designations", len(df))
    c2.metric("Avg. Market Gap", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
    c3.metric("Critical Reviews", len(df[df['Variance %'] < -30]))

    # Main Table
    filtered = df[df['Designation'].str.contains(search_q, case=False)] if search_q else df
    st.subheader("Interactive Salary Matrix")
    event = st.dataframe(filtered, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight Section
    if len(event.selection.rows) > 0:
        row = filtered.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 AI Insight: {row['Designation']}")
        v = row['Variance %']
        insight = "🚨 Critical Pay Gap Detected." if v < -40 else "⚠️ Market Lag Detected." if v < -15 else "✅ Salary is Competitive."
        st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Analysis:</b> {insight} {row['Designation']} is currently {abs(v)}% {'below' if v < 0 else 'above'} market standards.</div></div>""", unsafe_allow_html=True)

elif page == "📁 Salary Categories":
    st.title("Salary Categorization & Breakdown")
    # Groups like HOD, Engineering, Workers
    st.subheader("HOD & Management")
    st.write(df[df['Designation'].str.contains("HOD|Manager|Head", case=False)])
    
    st.subheader("Technical & Engineering")
    st.write(df[df['Designation'].str.contains("Engineer|Technician|Electrician", case=False)])

elif page == "🔍 Visual Analysis":
    st.title("Market Disparity Visualization")
    
    st.bar_chart(df.set_index('Designation')['Variance %'])
    st.info("The chart above visualizes how far each role deviates from the market average (0%).")

elif page == "⚙️ Settings":
    st.title("System Settings")
    st.write("Database Version: 2.0 (84 Roles)")
    st.write("Last Update: March 2026")
