# 4. Validated Source Data Points (Raw Mid-points)
st.markdown("---")
st.markdown("### 🔍 Raw Data Audit Trail")
st.write("Each competitor's salary range was normalized to its mid-point for unbiased calculation.")

# Display Data Chips with enhanced visibility
chips_cols = st.columns(len(comp_cols))
for i, c in enumerate(comp_cols):
    val = audit.get(f"Mean_{c}")
    with chips_cols[i]:
        if pd.notna(val) and val > 0:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-top: 4px solid #3b82f6; text-align: center;">
                <small style="color: #94a3b8;">{c}</small><br>
                <b style="color: #38bdf8; font-size: 20px;">{int(val):,}</b><br>
                <small style="color: #4ade80;">Validated ✅</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-top: 4px solid #4b5563; text-align: center; opacity: 0.6;">
                <small style="color: #94a3b8;">{c}</small><br>
                <b style="color: #64748b; font-size: 20px;">N/A</b><br>
                <small>No Data</small>
            </div>
            """, unsafe_allow_html=True)

# Visualizing the Data Spread for the Board
st.markdown("---")
st.subheader("📊 Competitor Comparison Chart (Audit View)")


# Creating a small bar chart for the selected role's competitor data
comp_data = []
for c in comp_cols:
    v = audit.get(f"Mean_{c}")
    if pd.notna(v) and v > 0:
        comp_data.append({"Company": c, "Salary": v})

if comp_data:
    audit_df = pd.DataFrame(comp_data)
    fig_audit = px.bar(audit_df, x='Company', y='Salary', color='Company', 
                       text_auto=',.0f', title=f"Market Spread for {sel_role}",
                       template="plotly_dark")
    st.plotly_chart(fig_audit, use_container_width=True)
