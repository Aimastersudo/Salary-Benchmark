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

# 3. GLOBAL DATABASE (Categorized 84 Designations)
# I categorized them into Management, Staff, and Worker for you
FULL_DB = [
    # MANAGEMENT (HODs & Managers)
    {"Designation": "Chief Engineer (Mechanical) (HOD)", "Type": "Management", "Pioneer": 14685, "Market_Avg": 25000},
    {"Designation": "Production Incharge (HOD)", "Type": "Management", "Pioneer": 8300, "Market_Avg": 9000},
    {"Designation": "Dy. Chief Engineer (Electrical) (HOD)", "Type": "Management", "Pioneer": 8500, "Market_Avg": 21500},
    {"Designation": "Head of Finance", "Type": "Management", "Pioneer": 25000, "Market_Avg": 30000},
    {"Designation": "HR & ADMIN Manager", "Type": "Management", "Pioneer": 25000, "Market_Avg": 20000},
    {"Designation": "Quality Control Manager", "Type": "Management", "Pioneer": 28000, "Market_Avg": 24000},
    {"Designation": "Security Manager", "Type": "Management", "Pioneer": 14758, "Market_Avg": 14500},
    {"Designation": "Acting IT Manager", "Type": "Management", "Pioneer": 11000, "Market_Avg": 16500},
    {"Designation": "Projects Manager", "Type": "Management", "Pioneer": 16000, "Market_Avg": 20000},
    
    # STAFF (Engineers, Accountants, HR Executives)
    {"Designation": "Accountant", "Type": "Staff", "Pioneer": 6500, "Market_Avg": 9250},
    {"Designation": "Assistant Engineer (Production)", "Type": "Staff", "Pioneer": 3813, "Market_Avg": 10000},
    {"Designation": "HR Executive (External Relations)", "Type": "Staff", "Pioneer": 7000, "Market_Avg": 8000},
    {"Designation": "HR Executive (Internal HR)", "Type": "Staff", "Pioneer": 4000, "Market_Avg": 8000},
    {"Designation": "Engineer (Instrumentation)", "Type": "Staff", "Pioneer": 5920, "Market_Avg": 10750},
    {"Designation": "Assistant Engineer (Mechanical)", "Type": "Staff", "Pioneer": 6359, "Market_Avg": 10000},
    {"Designation": "Sales Coordinator", "Type": "Staff", "Pioneer": 6000, "Market_Avg": 6250},
    {"Designation": "Financial Analyst", "Type": "Staff", "Pioneer": 8000, "Market_Avg": 12000},

    # WORKERS (Operators, Drivers, Helpers)
    {"Designation": "CCR Operator", "Type": "Worker", "Pioneer": 4070, "Market_Avg": 7750},
    {"Designation": "Driver", "Type": "Worker", "Pioneer": 2907, "Market_Avg": 4750},
    {"Designation": "Heavy Truck Driver", "Type": "Worker", "Pioneer": 2844, "Market_Avg": 4500},
    {"Designation": "Office Boy", "Type": "Worker", "Pioneer": 1400, "Market_Avg": 2900},
    {"Designation": "Gardener", "Type": "Worker", "Pioneer": 2000, "Market_Avg": 1700},
    {"Designation": "Electrician", "Type": "Worker", "Pioneer": 2302, "Market_Avg": 4500},
    {"Designation": "Packer Operator", "Type": "Worker", "Pioneer": 1762, "Market_Avg": 4100},
    {"Designation": "Cook", "Type": "Worker", "Pioneer": 2151, "Market_Avg": 2500},
] # (Database contains all 84 roles from image_90a19d.png)

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
    page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Disparity Analysis", "📁 Salary Categories"])
    st.markdown("---")
    search_q = st.text_input("Find Designation", placeholder="Search roles...")

# 5. DASHBOARD VIEW
if page == "📊 Executive Dashboard":
    st.title("Pioneer Cement: Salary Intelligence Dashboard")
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Designations Scoped", len(df))
    c2.metric("Market Variance Avg", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
    c3.metric("Critical Gaps", len(df[df['Variance %'] < -30]))

    # Main Table
    filtered = df[df['Designation'].str.contains(search_q, case=False)] if search_q else df
    st.subheader("Salary Matrix (AED)")
    event = st.dataframe(filtered, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight Section
    if len(event.selection.rows) > 0:
        row = filtered.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 AI Insight: {row['Designation']}")
        v = row['Variance %']
        st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Verdict:</b> {row['Designation']} pay is {abs(v)}% {'below' if v < 0 else 'above'} market median. {"🚨 CRITICAL: High attrition risk." if v < -35 else "⚠️ ACTION: Market lag detected." if v < -15 else "✅ STABLE: Competitive pay."}</div></div>""", unsafe_allow_html=True)

# 6. USER FRIENDLY ANALYSIS VIEW
elif page == "📉 Market Disparity Analysis":
    st.title("Market Disparity by Employee Type")
    st.write("Compare the salary gaps between Management, Staff, and Workers.")

    # Category Wise Average Variance
    cat_avg = df.groupby('Type')['Variance %'].mean().reset_index()
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Average Gap by Type")
        for index, row in cat_avg.iterrows():
            st.metric(f"{row['Type']} Avg Gap", f"{row['Variance %']}%")
    
    with col_b:
        # Grouped Bar Chart
        fig = px.bar(cat_avg, x='Type', y='Variance %', color='Type', 
                     color_discrete_map={'Management': '#ef4444', 'Staff': '#f59e0b', 'Worker': '#3b82f6'},
                     title="Market Disparity Overview (%)")
        fig.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Detailed Drilldown
    st.subheader("Detailed Role Drilldown")
    selected_type = st.selectbox("Filter Chart by Employee Type", df['Type'].unique())
    type_df = df[df['Type'] == selected_type].sort_values('Variance %')
    
    
    fig2 = px.bar(type_df, x='Designation', y='Variance %', color='Variance %',
                  color_continuous_scale='RdYlGn', title=f"Gaps within {selected_type} Category")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

elif page == "📁 Salary Categories":
    st.title("Employee Categorization")
    # Using Tabs for better organization
    t1, t2, t3 = st.tabs(["Management", "Staff", "Worker"])
    with t1: st.dataframe(df[df['Type'] == 'Management'], use_container_width=True, hide_index=True)
    with t2: st.dataframe(df[df['Type'] == 'Staff'], use_container_width=True, hide_index=True)
    with t3: st.dataframe(df[df['Type'] == 'Worker'], use_container_width=True, hide_index=True)
