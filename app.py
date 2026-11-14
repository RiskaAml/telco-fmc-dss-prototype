import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_generator import generate_synthetic_data

st.set_page_config(
    page_title="FMC Churn & NBO DSS",
    page_icon="📡",
    layout="wide",
)

# Corporate styling (TelkomGroup Red #D32F2F, Dark Slate #1E293B, Light Gray/White)
st.markdown(
    """
    <style>
        .main-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 0.95rem;
            color: #475569;
            margin-bottom: 1rem;
        }
        div[data-testid="stMetric"] {
            background-color: #F8FAFC;
            border-left: 4px solid #D32F2F;
            padding: 12px 16px;
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

PROTOTYPE_NOTICE = (
    "Prototype Notice: Macro KPIs reflect 2025 TelkomGroup B2C operational benchmarks. "
    "All 5,000 subscriber records and uplift projections are synthetically simulated for demonstration."
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return generate_synthetic_data(n=5000, seed=42)


df = load_data()

# Sidebar Notice & Info
with st.sidebar:
    st.markdown("### 📡 FMC Churn & NBO DSS")
    st.info(PROTOTYPE_NOTICE)
    st.markdown("---")
    st.markdown("**2025 B2C Operational Context**")
    st.caption(
        "- B2C Revenue Share: ~72% of Group\n"
        "- Mobile Base: 156.1M (~95% Prepaid)\n"
        "- IndiHome B2C Base: 10.3M\n"
        "- Data Traffic: 23.4M TB (+15% YoY)"
    )

# Top Main Page Notice & Title
st.info(PROTOTYPE_NOTICE)
st.markdown(
    '<div class="main-header">FMC Churn Prevention & Next-Best-Offer (NBO) DSS</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">TelkomGroup B2C Convergence & Digital Ecosystem Monetization Prototype</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Executive KPI Overview",
        "🎯 Churn & ARPU Simulator (Interactive DSS)",
        "🔍 Data & Business Rule Explorer",
    ]
)

# ==============================================================================
# TAB 1: EXECUTIVE KPI OVERVIEW
# ==============================================================================
with tab1:
    st.subheader("2025 B2C Operational Benchmarks vs. Value Erosion Gaps")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Data Traffic (2025)",
            value="23.4M TB",
            delta="+15.0% YoY",
        )
    with col2:
        st.metric(
            label="B2C External Revenue",
            value="Rp105.9T",
            delta="-3.4% YoY (Rp105,898B)",
            delta_color="normal",
        )
    with col3:
        st.metric(
            label="Voice & SMS Decline",
            value="-30.4% / -17.1%",
            delta="OTT Substitution Impact",
            delta_color="off",
        )
    with col4:
        st.metric(
            label="IndiHome B2C Base",
            value="10.3M",
            delta="ARPU Pressure (3P → 1P)",
            delta_color="off",
        )

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Segment Distribution & Churn Risk Proportion**")
        seg_risk = (
            df.groupby(["customer_segment", "churn_risk_tier"])
            .size()
            .reset_index(name="subscriber_count")
        )
        fig_seg = px.bar(
            seg_risk,
            x="customer_segment",
            y="subscriber_count",
            color="churn_risk_tier",
            barmode="stack",
            color_discrete_map={
                "High": "#D32F2F",
                "Medium": "#F59E0B",
                "Low": "#1E293B",
            },
            labels={
                "customer_segment": "Customer Segment",
                "subscriber_count": "Subscribers (Simulated)",
                "churn_risk_tier": "Churn Risk Tier",
            },
        )
        fig_seg.update_layout(
            plot_bgcolor="white",
            legend_title_text="Risk Tier",
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    with chart_col2:
        st.markdown("**Data Usage vs. Monthly ARPU by Churn Risk Tier**")
        sample_df = df.sample(n=min(1000, len(df)), random_state=42)
        fig_scatter = px.scatter(
            sample_df,
            x="data_usage_gb",
            y="monthly_arpu_idr",
            color="churn_risk_tier",
            hover_data=["customer_segment", "recommended_offer"],
            color_discrete_map={
                "High": "#D32F2F",
                "Medium": "#F59E0B",
                "Low": "#1E293B",
            },
            labels={
                "data_usage_gb": "Monthly Data Usage (GB)",
                "monthly_arpu_idr": "Monthly ARPU (IDR)",
                "churn_risk_tier": "Churn Risk Tier",
            },
            opacity=0.7,
        )
        fig_scatter.update_layout(
            plot_bgcolor="white",
            legend_title_text="Risk Tier",
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


# ==============================================================================
# TAB 2: CHURN & ARPU SIMULATOR (INTERACTIVE DSS)
# ==============================================================================
with tab2:
    st.subheader("Interactive NBO Campaign & Revenue Impact Simulator")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        selected_segment = st.selectbox(
            "Target Segment",
            options=["All", "IndiHome 1P", "IndiHome 3P", "Telkomsel Prabayar", "Telkomsel Halo"],
            index=0,
        )
    with f_col2:
        selected_risk = st.multiselect(
            "Churn Risk Tier",
            options=["High", "Medium", "Low"],
            default=["High", "Medium"],
        )
    with f_col3:
        conversion_rate_pct = st.slider(
            "Target Conversion Rate (%)",
            min_value=5,
            max_value=40,
            value=15,
            step=1,
        )
    with f_col4:
        incentive_budget_pct = st.slider(
            "Discount / Incentive Budget (%)",
            min_value=0,
            max_value=30,
            value=10,
            step=1,
        )

    sim_df = df.copy()
    if selected_segment != "All":
        sim_df = sim_df[sim_df["customer_segment"] == selected_segment]
    if selected_risk:
        sim_df = sim_df[sim_df["churn_risk_tier"].isin(selected_risk)]
    else:
        sim_df = sim_df.iloc[0:0]

    if sim_df.empty:
        st.warning("No subscribers match the selected segment and risk tier filters. Please adjust your filters.")
    else:
        eligible_df = sim_df[sim_df["recommended_offer"] != "Retain / No Promo Needed"]

        current_monthly_rev = sim_df["monthly_arpu_idr"].sum()
        conv_rate = conversion_rate_pct / 100.0
        disc_rate = incentive_budget_pct / 100.0

        gross_uplift = eligible_df["projected_arpu_uplift"].sum() * conv_rate
        retention_saved = eligible_df["projected_retention_gain"].sum() * conv_rate
        incentive_cost = (gross_uplift + retention_saved) * disc_rate
        net_gain = (gross_uplift + retention_saved) - incentive_cost
        projected_monthly_rev = current_monthly_rev + net_gain

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Targetable Subscribers", f"{len(eligible_df):,} / {len(sim_df):,}")
        m2.metric("Current Simulated Revenue", f"Rp {current_monthly_rev / 1e6:,.1f}M")
        m3.metric("Projected Net Revenue Gain", f"Rp {net_gain / 1e6:,.1f}M", delta=f"+{(net_gain / current_monthly_rev * 100):.2f}%")
        m4.metric("Projected Revenue After NBO", f"Rp {projected_monthly_rev / 1e6:,.1f}M")

        st.markdown("---")
        sim_left, sim_right = st.columns([1.2, 1])

        with sim_left:
            st.markdown("**Current vs. Projected Monthly Revenue (IDR)**")
            fig_rev = go.Figure(
                data=[
                    go.Bar(
                        name="Current Simulated Revenue",
                        x=["Monthly Revenue"],
                        y=[current_monthly_rev],
                        marker_color="#1E293B",
                        text=[f"Rp {current_monthly_rev / 1e6:,.1f}M"],
                        textposition="auto",
                    ),
                    go.Bar(
                        name="Projected Revenue After NBO",
                        x=["Monthly Revenue"],
                        y=[projected_monthly_rev],
                        marker_color="#D32F2F",
                        text=[f"Rp {projected_monthly_rev / 1e6:,.1f}M"],
                        textposition="auto",
                    ),
                ]
            )
            fig_rev.update_layout(
                barmode="group",
                plot_bgcolor="white",
                yaxis_title="Revenue (IDR)",
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        with sim_right:
            st.markdown("**Automated NBO Offer Breakdown**")
            offer_summary = (
                sim_df.groupby(["recommended_offer", "delivery_channel"])
                .agg(
                    subscribers=("subscriber_id", "count"),
                    avg_arpu_idr=("monthly_arpu_idr", "mean"),
                    avg_uplift_idr=("projected_arpu_uplift", "mean"),
                )
                .reset_index()
                .sort_values(by="subscribers", ascending=False)
            )
            offer_summary["avg_arpu_idr"] = offer_summary["avg_arpu_idr"].round(0)
            offer_summary["avg_uplift_idr"] = offer_summary["avg_uplift_idr"].round(0)
            st.dataframe(offer_summary, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: DATA & BUSINESS RULE EXPLORER
# ==============================================================================
with tab3:
    st.subheader("Subscriber Watchlist & Decision Matrix Explorer")

    exp_c1, exp_c2, exp_c3 = st.columns(3)
    with exp_c1:
        exp_seg = st.multiselect(
            "Filter Segment",
            options=sorted(df["customer_segment"].unique()),
            default=sorted(df["customer_segment"].unique()),
        )
    with exp_c2:
        exp_tier = st.multiselect(
            "Filter Risk Tier",
            options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
        )
    with exp_c3:
        exp_offer = st.multiselect(
            "Filter Recommended Offer",
            options=sorted(df["recommended_offer"].unique()),
            default=sorted(df["recommended_offer"].unique()),
        )

    filtered_df = df[
        (df["customer_segment"].isin(exp_seg))
        & (df["churn_risk_tier"].isin(exp_tier))
        & (df["recommended_offer"].isin(exp_offer))
    ]

    if filtered_df.empty:
        st.warning("No records match your current filter selection. Please adjust the filters above.")
    else:
        st.caption(f"Showing {len(filtered_df):,} of {len(df):,} synthetic subscriber records.")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Watchlist (.csv)",
            data=csv_data,
            file_name="fmc_nbo_watchlist_export.csv",
            mime="text/csv",
        )
