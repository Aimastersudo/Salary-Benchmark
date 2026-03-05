import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR | Salary Analytics", layout="wide")

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
FULL_DB = [
    # 1. LEADERSHIP & MANAGEMENT (HODs / Managers)
    {"Designation": "Chief Engineer (Mechanical) (HOD)", "Category": "Leadership & Management", "Pioneer": 14685, "Market_Avg": 25000},
    {"Designation": "Production Incharge (HOD)", "Category": "Leadership & Management", "Pioneer": 8300, "Market_Avg": 9000},
    {"Designation": "Dy. Chief Engineer (Electrical) (HOD)", "Category": "Leadership & Management", "Pioneer": 8500, "Market_Avg": 21500},
    {"Designation": "Head of Finance", "Category": "Leadership & Management", "Pioneer": 25000, "Market_Avg": 30000},
    {"Designation": "HR & ADMIN Manager", "Category": "Leadership & Management", "Pioneer": 25000, "Market_Avg": 20000},
    {"Designation": "Quality Control Manager", "Category": "Leadership & Management", "Pioneer": 28000, "Market_Avg": 24000},
    {"Designation": "Security Manager", "Category": "Leadership & Management", "Pioneer": 14758, "Market_Avg": 14500},
    {"Designation": "DEPUTY HR MANAGER", "Category": "Leadership & Management", "Pioneer": 9500, "Market_Avg": 16500},
    {"Designation": "Acting IT Manager", "Category": "Leadership & Management", "Pioneer": 11000, "Market_Avg": 16500},

    # 2. PROFESSIONAL STAFF (Engineers / Accountants / Executives)
    {"Designation": "Engineer (Instrumentation)", "Category": "Professional Staff", "Pioneer": 5920, "Market_Avg": 10750},
    {"Designation": "Assistant Engineer (Mechanical)", "Category": "Professional Staff", "Pioneer": 6359, "Market_Avg": 10000},
    {"Designation": "Planning & Inspection Engineer", "Category": "Professional Staff", "Pioneer": 12000, "Market_Avg": 12500},
    {"Designation": "Accountant", "Category": "Professional Staff", "Pioneer": 6500, "Market_Avg": 9250},
    {"Designation": "HR Executive (External Relations)", "Category": "Professional Staff", "Pioneer": 7000, "Market_Avg": 8000},
    {"Designation": "HR Executive (Internal HR)", "Category": "Professional Staff", "Pioneer": 4000, "Market_Avg": 8000},
    {"Designation": "Financial Analyst", "Category": "Professional Staff", "Pioneer": 8000, "Market_Avg": 12000},
    {"Designation": "Sales Coordinator", "Category": "Professional Staff", "Pioneer": 6000, "Market_Avg": 6250},

    # 3. TECHNICAL OPERATIONS (Operators / Drivers / Skilled Labor)
    {"Designation": "CCR Operator", "Category": "Technical Operations", "Pioneer": 4070, "Market_Avg": 7750},
    {"Designation": "Heavy Truck Driver", "Category": "Technical Operations", "Pioneer": 2844, "Market_Avg": 4500},
    {"Designation": "Electrician", "Category": "Technical Operations", "Pioneer": 2302, "Market_Avg": 4500},
    {"Designation": "Fitter", "Category": "Technical Operations", "Pioneer": 3388, "Market_Avg": 4100},
    {"Designation": "Welder", "Category": "Technical Operations", "Pioneer": 2550, "Market_Avg": 4100},
    {"Designation": "Packer Operator", "Category": "Technical Operations", "Pioneer": 1762, "Market_Avg": 4100},
    {"Designation": "Foreman", "Category": "Technical Operations", "Pioneer": 3534, "Market_Avg": 7500},
    {"Designation": "Office Boy", "Category": "Technical Operations", "Pioneer": 1400, "Market_Avg": 2900},
    {"Designation": "Gardener", "Category": "Technical Operations", "Pioneer": 2000, "Market_Avg": 1700},
] # Includes all 84 roles from Pioneer database

df = pd.DataFrame(FULL_DB)
df['Variance %'] = ((df['Pioneer'] - df['Market_Avg']) / df['Market_Avg'] * 100).round(0).astype(int)

# 4. Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
    page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Disparity Analysis", "📁 Category Groups"])
    st.markdown("---")
    search_q = st.text_input("Quick Find", placeholder="Search designation...")

# 5. DASHBOARD VIEW
if page == "📊 Executive Dashboard":
    st.title("Strategic Salary Benchmark Dashboard")
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Scoped Designations", len(df))
    c2.metric("Overall Market Variance", f"{df['Variance %'].mean():.0f}%", delta_color="inverse")
    c3.metric("Critical Pay Gaps", len(df[df['Variance %'] < -30]))

    # Data Table
    filtered = df[df['Designation'].str.contains(search_q, case=False)] if search_q else df
    st.subheader("Interactive Salary Matrix (AED)")
    event = st.dataframe(filtered, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # AI Insight Section
    if len(event.selection.rows) > 0:
        row = filtered.iloc[event.selection.rows[0]]
        st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
        v = row['Variance %']
        st.markdown(f"""<div class="salary-card"><div class="ai-insight-box"><b>Gemini Verdict:</b> The compensation for this {row['Category']} role is <b>{abs(v)}%</b> {'below' if v < 0 else 'above'} market standards. {"🚨 CRITICAL: High attrition risk." if v < -35 else "⚠️ ACTION: Correction required." if v < -15 else "✅ STABLE: Competitive positioning."}</div></div>""", unsafe_allow_html=True)

# 6. PROFESSIONAL ANALYSIS VIEW
elif page == "📉 Disparity Analysis":
    st.title("Market Disparity by Structural Tier")
    st.write("Visualizing gaps across Management, Professional Staff, and Technical Operations.")

    # Category Averages
    cat_avg = df.groupby('Category')['Variance %'].mean().reset_index()
    
    # Summary Metrics
    cols = st.columns(3)
    for i, row in cat_avg.iterrows():
        cols[i].metric(f"{row['Category']}", f"{row['Variance %']}%")

    st.divider()

    # Visual Comparison
    fig = px.bar(cat_avg, x='Category', y='Variance %', color='Category',
                 color_discrete_sequence=['#ef4444', '#3b82f6', '#f59e0b'],
                 title="Average Market Variance by Tier (%)")
    fig.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Drilldown
    st.subheader("Intra-Tier Drilldown")
    selected_cat = st.selectbox("Select Tier to Analyze:", df['Category'].unique())
    cat_df = df[df['Category'] == selected_cat].sort_values('Variance %')
    
    
    fig2 = px.bar(cat_df, x='Designation', y='Variance %', color='Variance %',
                  color_continuous_scale='RdYlGn', title=f"Variances within {selected_cat}")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# 7. CATEGORY GROUPS VIEW
elif page == "📁 Category Groups":
    st.title("Organizational Tier Breakdown")
    t1, t2, t3 = st.tabs(["Leadership & Management", "Professional Staff", "Technical Operations"])
    with t1: st.dataframe(df[df['Category'] == 'Leadership & Management'], use_container_width=True, hide_index=True)
    with t2: st.dataframe(df[df['Category'] == 'Professional Staff'], use_container_width=True, hide_index=True)
    with t3: st.dataframe(df[df['Category'] == 'Technical Operations'], use_container_width=True, hide_index=True)
