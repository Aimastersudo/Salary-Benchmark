import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Pioneer HR | Salary Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .salary-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    .ai-insight-box { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; color: #93c5fd; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA LOADER - Updated for New CSV Structure
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("salary_data.csv", encoding='utf-8-sig')
        
        # Clean column names to avoid space errors
        df.columns = df.columns.str.strip()
        
        # ⚠️ Check if 'Market Salary' exists. If not, show an error warning.
        if 'Market Salary' not in df.columns:
            st.error("🚨 Error: 'Market Salary' column is missing in your CSV. Please add it to calculate market variance.")
            return None
            
        # Clean Pioneer Salary (Remove Commas and make it integer)
        df['Your Salary (AED)'] = df['Your Salary (AED)'].astype(str).str.replace(',', '').astype(float)
        df['Market Salary'] = df['Market Salary'].astype(str).str.replace(',', '').astype(float)
        
        # Calculate Market Variance %
        df['Variance %'] = ((df['Your Salary (AED)'] - df['Market Salary']) / df['Market Salary'] * 100).round(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"System Error: {e}")
        return None

df = load_data()

if df is not None:
    # 4. Sidebar Filters
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/111827/f8fafc?text=PIONEER+AI", use_column_width=True)
        page = st.radio("MAIN MENU", ["📊 Executive Dashboard", "📉 Market Analysis", "📁 Structural Groups"])
        st.markdown("---")
        
        all_depts = sorted(df['Department'].dropna().unique())
        selected_depts = st.multiselect("Filter Departments:", all_depts, default=all_depts)
        search_q = st.text_input("Find Designation", placeholder="Search roles...")

    # Filter Logic
    f_df = df[df['Department'].isin(selected_depts)]
    if search_q:
        f_df = f_df[f_df['Designation'].str.contains(search_q, case=False, na=False)]

    # 5. Dashboard View
    if page == "📊 Executive Dashboard":
        st.title("Strategic Salary Benchmark Dashboard")
        
        # Metrics - Using 'Num of Designation' as Headcount
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Designations Scoped", len(f_df))
        c2.metric("Total Headcount", int(f_df['Num of Designation'].sum())) 
        
        avg_variance = f"{f_df['Variance %'].mean():.0f}%" if not f_df.empty else "0%"
        c3.metric("Avg. Market Gap", avg_variance, delta_color="inverse")
        c4.metric("Critical Gaps (<-30%)", len(f_df[f_df['Variance %'] < -30]))

        # Data Table
        display_cols = ['Designation', 'Department', 'Employee Type', 'Num of Designation', 'Your Salary (AED)', 'Market Salary', 'Variance %']
        st.subheader("Interactive Salary Matrix (AED)")
        event = st.dataframe(f_df[display_cols], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

        # AI Insight
        if len(event.selection.rows) > 0:
            row = f_df.iloc[event.selection.rows[0]]
            st.markdown(f"### 📋 Strategic Analysis: {row['Designation']}")
            st.markdown(f"""
            <div class="salary-card">
                <div class="ai-insight-box">
                    <b>Gemini HR Analysis:</b> Current pay for {row['Designation']} in the {row['Department']} 
                    department is {abs(row['Variance %'])}% below market levels. With a current headcount of <b>{row['Num of Designation']}</b>, 
                    talent retention should be closely monitored by Management.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 6. Analysis View
    elif page == "📉 Market Analysis":
        st.title("Market Disparity by Structural Tier")
        tier_avg = f_df.groupby('Employee Type')['Variance %'].mean().reset_index()
        fig = px.bar(tier_avg, x='Employee Type', y='Variance %', color='Employee Type', title="Avg. Market Variance by Employee Type (%)")
        fig.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Avg. Variance by Department (%)")
        dept_avg = f_df.groupby('Department')['Variance %'].mean().reset_index().sort_values('Variance %')
        fig2 = px.bar(dept_avg, x='Department', y='Variance %', color='Variance %', color_continuous_scale='RdYlGn')
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # 7. Groups View
    elif page == "📁 Structural Groups":
        st.title("Organizational Tier Breakdown")
        display_cols = ['Designation', 'Department', 'Num of Designation', 'Your Salary (AED)', 'Market Salary', 'Variance %']
        
        # Fetching unique employee types to create dynamic tabs
        emp_types = df['Employee Type'].dropna().unique().tolist()
        if emp_types:
            tabs = st.tabs(emp_types)
            for i, emp_type in enumerate(emp_types):
                with tabs[i]:
                    st.dataframe(f_df[f_df['Employee Type'] == emp_type][display_cols], use_container_width=True, hide_index=True)
