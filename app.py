import streamlit as st
import pandas as pd
import plotly.express as px
import re
from collections import Counter

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GATEWAYS 2025 – Fest Analytics",
    page_icon="https://img.icons8.com/fluency/96/graduation-cap.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = ["#1d4ed8", "#7c3aed", "#0891b2", "#059669", "#d97706", "#dc2626", "#ec4899", "#f59e0b"]

# ── Plotly common layout helper ───────────────────────────────────────────────
def chart_layout(fig, height=380):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(t=40, b=10, l=10, r=10),
    )
    fig.update_traces(marker_line_width=0)
    return fig

# ── Load CSV ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("fest_dataset.csv")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df.dropna(subset=["Rating"], inplace=True)
    df["Rating"] = df["Rating"].astype(int)
    df["Amount Paid"] = pd.to_numeric(df["Amount Paid"], errors="coerce").fillna(0).astype(int)
    return df

df = load_data()

STATE_COORDS = {
    "Karnataka":     (15.3173, 75.7139),
    "Tamil Nadu":    (11.1271, 78.6569),
    "Kerala":        (10.8505, 76.2711),
    "Maharashtra":   (19.7515, 75.7139),
    "Gujarat":       (22.2587, 71.1924),
    "Rajasthan":     (27.0238, 74.2179),
    "Delhi":         (28.7041, 77.1025),
    "Telangana":     (18.1124, 79.0193),
    "Uttar Pradesh": (26.8467, 80.9462),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=64)
    st.title("GATEWAYS 2025")
    st.caption("National Level Tech Fest — Analytics")
    st.divider()

    page = st.radio(
        "Navigate to",
        ["Overview", "Participation Trends", "Feedback & Ratings", "Interactive Dashboard"],
    )
    st.divider()

    st.subheader("Filters")
    selected_states = st.multiselect("Filter by State", sorted(df["State"].unique()), default=[])
    selected_events = st.multiselect("Filter by Event", sorted(df["Event Name"].unique()), default=[])

    fdf = df.copy()
    if selected_states:
        fdf = fdf[fdf["State"].isin(selected_states)]
    if selected_events:
        fdf = fdf[fdf["Event Name"].isin(selected_events)]

    st.divider()
    st.info(f"Showing **{len(fdf)}** of **{len(df)}** participants")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("GATEWAYS 2025")
    st.subheader("National Level Tech Fest — Analytics Dashboard")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Participants", len(fdf))
    c2.metric("Colleges",           fdf["College"].nunique())
    c3.metric("States",             fdf["State"].nunique())
    c4.metric("Avg Rating",         f"{fdf['Rating'].mean():.2f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Events",        fdf["Event Name"].nunique())
    c6.metric("Total Revenue", f"Rs. {fdf['Amount Paid'].sum():,.0f}")
    c7.metric("Individual",    int((fdf["Event Type"] == "Individual").sum()))
    c8.metric("Group",         int((fdf["Event Type"] == "Group").sum()))

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        ec = fdf["Event Name"].value_counts().reset_index()
        ec.columns = ["Event", "Count"]
        fig = px.bar(ec, x="Count", y="Event", orientation="h",
                     color="Count", color_continuous_scale="Blues",
                     title="Participants per Event")
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)

    with col2:
        sc = fdf["State"].value_counts().reset_index()
        sc.columns = ["State", "Count"]
        fig2 = px.pie(sc, names="State", values="Count",
                      color_discrete_sequence=PALETTE,
                      title="State-wise Distribution", hole=0.45)
        fig2.update_traces(marker=dict(line=dict(color="white", width=1.5)))
        st.plotly_chart(chart_layout(fig2, 360), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – PARTICIPATION TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Participation Trends":
    st.title("Participation Trends")
    st.caption("Event-wise, college-wise breakdowns and India map")
    st.divider()

    st.subheader("State-wise Participants across India")
    state_count = fdf["State"].value_counts().reset_index()
    state_count.columns = ["State", "Participants"]
    state_count["lat"] = state_count["State"].map(lambda s: STATE_COORDS.get(s, (20, 77))[0])
    state_count["lon"] = state_count["State"].map(lambda s: STATE_COORDS.get(s, (20, 77))[1])

    fig_map = px.scatter_geo(
        state_count, lat="lat", lon="lon",
        size="Participants", color="Participants",
        hover_name="State",
        hover_data={"lat": False, "lon": False, "Participants": True},
        color_continuous_scale="Viridis",
        size_max=55, scope="asia",
        title="State-wise Participants across India",
    )
    fig_map.update_geos(
        center={"lat": 20.5937, "lon": 78.9629},
        projection_scale=4.5,
        showcountries=True, countrycolor="#94a3b8",
        showland=True,  landcolor="#f1f5f9",
        showocean=True, oceancolor="#e0f2fe",
        lataxis_range=[6, 36], lonaxis_range=[66, 98],
    )
    st.plotly_chart(chart_layout(fig_map, 520), use_container_width=True)

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Colleges")
        top_colleges = fdf["College"].value_counts().head(10).reset_index()
        top_colleges.columns = ["College", "Count"]
        fig_col = px.bar(top_colleges, x="College", y="Count",
                         color="Count", color_continuous_scale="Purples",
                         title="Top 10 Colleges by Participation")
        fig_col.update_layout(xaxis_tickangle=-35, showlegend=False)
        st.plotly_chart(chart_layout(fig_col), use_container_width=True)

    with col2:
        st.subheader("Individual vs Group")
        et = fdf.groupby(["Event Name", "Event Type"]).size().reset_index(name="Count")
        fig_et = px.bar(et, x="Event Name", y="Count", color="Event Type",
                        barmode="group", title="Individual vs Group per Event",
                        color_discrete_map={"Individual": "#1d4ed8", "Group": "#7c3aed"})
        fig_et.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(chart_layout(fig_et), use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Revenue Funnel")
        rev = fdf.groupby("Event Name")["Amount Paid"].sum().reset_index()
        rev.columns = ["Event", "Revenue"]
        rev = rev.sort_values("Revenue", ascending=False)
        fig_rev = px.funnel(rev, x="Revenue", y="Event",
                            title="Revenue Funnel by Event",
                            color_discrete_sequence=["#1d4ed8"])
        st.plotly_chart(chart_layout(fig_rev), use_container_width=True)

    with col4:
        st.subheader("State x Event Heatmap")
        hm = fdf.groupby(["State", "Event Name"]).size().reset_index(name="Count")
        hm_pivot = hm.pivot(index="State", columns="Event Name", values="Count").fillna(0)
        fig_hm = px.imshow(hm_pivot, text_auto=True, aspect="auto",
                           color_continuous_scale="Blues",
                           title="State x Event Participation Heatmap")
        st.plotly_chart(chart_layout(fig_hm), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – FEEDBACK & RATINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Feedback & Ratings":
    st.title("Feedback & Ratings")
    st.caption("Participant feedback analysis and rating breakdowns")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        rc = fdf["Rating"].value_counts().sort_index().reset_index()
        rc.columns = ["Rating", "Count"]
        fig_r = px.bar(rc, x="Rating", y="Count", color="Count",
                       color_continuous_scale="Blues",
                       title="Overall Rating Distribution",
                       labels={"Rating": "Rating (1-5)", "Count": "No. of Participants"})
        st.plotly_chart(chart_layout(fig_r, 350), use_container_width=True)

    with col2:
        avg_ev = fdf.groupby("Event Name")["Rating"].mean().round(2).reset_index()
        avg_ev.columns = ["Event", "Avg Rating"]
        avg_ev = avg_ev.sort_values("Avg Rating", ascending=True)
        fig_avg = px.bar(avg_ev, x="Avg Rating", y="Event", orientation="h",
                         color="Avg Rating", color_continuous_scale="RdYlGn",
                         range_color=[1, 5], title="Average Rating per Event")
        st.plotly_chart(chart_layout(fig_avg, 350), use_container_width=True)

    st.divider()

    all_feedback = " ".join(fdf["Feedback"].dropna().str.lower())
    stop = {"and", "the", "a", "in", "of", "to", "is", "it", "was", "for", "on", "with", "very"}
    words = [w for w in re.findall(r"\b[a-z]+\b", all_feedback) if w not in stop and len(w) > 3]
    word_freq = Counter(words).most_common(20)
    wdf = pd.DataFrame(word_freq, columns=["Word", "Count"])

    col3, col4 = st.columns(2)
    with col3:
        fig_w = px.bar(wdf, x="Count", y="Word", orientation="h",
                       color="Count", color_continuous_scale="Teal",
                       title="Top Keywords in Feedback")
        fig_w.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(chart_layout(fig_w, 450), use_container_width=True)

    with col4:
        fig_box = px.box(fdf, x="State", y="Rating", color="State",
                         color_discrete_sequence=PALETTE,
                         title="Rating Spread by State")
        fig_box.update_layout(xaxis_tickangle=-35, showlegend=False)
        st.plotly_chart(chart_layout(fig_box, 450), use_container_width=True)

    st.divider()

    feedback_cats = fdf["Feedback"].value_counts().reset_index()
    feedback_cats.columns = ["Feedback", "Count"]
    fig_fb = px.treemap(feedback_cats, path=["Feedback"], values="Count",
                        color="Count", color_continuous_scale="Blues",
                        title="Feedback Category Treemap")
    st.plotly_chart(chart_layout(fig_fb, 380), use_container_width=True)

    fig_sc = px.scatter(fdf, x="Amount Paid", y="Rating",
                        color="Event Name", symbol="Event Type",
                        color_discrete_sequence=PALETTE,
                        title="Amount Paid vs Rating (per Event)",
                        opacity=0.75,
                        hover_data=["College", "State"])
    st.plotly_chart(chart_layout(fig_sc, 380), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – INTERACTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Interactive Dashboard":
    st.title("Interactive Insights Dashboard")
    st.caption("Drill down by college, state, and event")
    st.divider()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Participants", len(fdf))
    kpi2.metric("Avg Rating",         f"{fdf['Rating'].mean():.2f}")
    kpi3.metric("Total Revenue",      f"Rs. {fdf['Amount Paid'].sum():,}")
    kpi4.metric("High Rated (4-5)",   int((fdf["Rating"] >= 4).sum()))
    kpi5.metric("% Satisfied",        f"{100*(fdf['Rating'] >= 4).mean():.1f}%")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["College Analysis", "State Analysis", "Event Deep Dive"])

    with tab1:
        college_sel = st.selectbox("Select College", sorted(fdf["College"].unique()))
        cdf = fdf[fdf["College"] == college_sel]
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Participants", len(cdf))
        cc2.metric("Avg Rating",   f"{cdf['Rating'].mean():.2f}")
        cc3.metric("Revenue",      f"Rs. {cdf['Amount Paid'].sum():,}")
        c1, c2 = st.columns(2)
        with c1:
            ev_c = cdf["Event Name"].value_counts().reset_index()
            ev_c.columns = ["Event", "Count"]
            fig = px.pie(ev_c, names="Event", values="Count",
                         title=f"Events — {college_sel}",
                         color_discrete_sequence=PALETTE, hole=0.35)
            st.plotly_chart(chart_layout(fig, 320), use_container_width=True)
        with c2:
            st_c = cdf["State"].value_counts().reset_index()
            st_c.columns = ["State", "Count"]
            fig2 = px.bar(st_c, x="State", y="Count", color="Count",
                          color_continuous_scale="Blues",
                          title=f"States — {college_sel}")
            st.plotly_chart(chart_layout(fig2, 320), use_container_width=True)

    with tab2:
        state_sel = st.selectbox("Select State", sorted(fdf["State"].unique()))
        sdf = fdf[fdf["State"] == state_sel]
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Participants", len(sdf))
        sc2.metric("Avg Rating",   f"{sdf['Rating'].mean():.2f}")
        sc3.metric("Revenue",      f"Rs. {sdf['Amount Paid'].sum():,}")
        s1, s2 = st.columns(2)
        with s1:
            ev_s = sdf["Event Name"].value_counts().reset_index()
            ev_s.columns = ["Event", "Count"]
            fig_s = px.bar(ev_s, x="Event", y="Count",
                           color="Count", color_continuous_scale="Teal",
                           title=f"Popular Events — {state_sel}")
            fig_s.update_layout(xaxis_tickangle=-25)
            st.plotly_chart(chart_layout(fig_s, 320), use_container_width=True)
        with s2:
            col_s = sdf["College"].value_counts().reset_index()
            col_s.columns = ["College", "Count"]
            fig_cs = px.pie(col_s, names="College", values="Count",
                            title=f"Colleges from {state_sel}",
                            color_discrete_sequence=PALETTE, hole=0.35)
            st.plotly_chart(chart_layout(fig_cs, 320), use_container_width=True)

    with tab3:
        event_sel = st.selectbox("Select Event", sorted(fdf["Event Name"].unique()))
        edf = fdf[fdf["Event Name"] == event_sel]
        ec1, ec2, ec3, ec4 = st.columns(4)
        ec1.metric("Participants", len(edf))
        ec2.metric("Avg Rating",   f"{edf['Rating'].mean():.2f}")
        ec3.metric("Revenue",      f"Rs. {edf['Amount Paid'].sum():,}")
        ec4.metric("Top College",  edf["College"].value_counts().idxmax())
        e1, e2 = st.columns(2)
        with e1:
            rat_e = edf["Rating"].value_counts().sort_index().reset_index()
            rat_e.columns = ["Rating", "Count"]
            fig_re = px.bar(rat_e, x="Rating", y="Count",
                            color="Count", color_continuous_scale="RdYlGn",
                            title=f"Ratings — {event_sel}")
            st.plotly_chart(chart_layout(fig_re, 300), use_container_width=True)
        with e2:
            st_e = edf["State"].value_counts().reset_index()
            st_e.columns = ["State", "Participants"]
            fig_se = px.bar(st_e, x="State", y="Participants",
                            color="Participants", color_continuous_scale="Blues",
                            title=f"States — {event_sel}")
            fig_se.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(chart_layout(fig_se, 300), use_container_width=True)

    st.divider()
    st.subheader("Key Actionable Insights")

    top_event   = fdf["Event Name"].value_counts().idxmax()
    top_state   = fdf["State"].value_counts().idxmax()
    top_college = fdf["College"].value_counts().idxmax()
    best_rated  = fdf.groupby("Event Name")["Rating"].mean().idxmax()
    most_rev    = fdf.groupby("Event Name")["Amount Paid"].sum().idxmax()
    low_rated   = fdf.groupby("Event Name")["Rating"].mean().idxmin()
    pct_sat     = 100 * (fdf["Rating"] >= 4).mean()

    col_a, col_b = st.columns(2)
    with col_a:
        st.success(f"**Most Popular Event:** {top_event}")
        st.info(f"**Leading State:** {top_state}")
        st.success(f"**Top College:** {top_college}")
        st.info(f"**Best Rated Event:** {best_rated}")
    with col_b:
        st.success(f"**Highest Revenue Event:** {most_rev}")
        st.warning(f"**Needs Improvement:** {low_rated} received the lowest average rating.")
        st.info(f"**Satisfaction Rate:** {pct_sat:.1f}% of participants rated 4 or above.")

    st.divider()
    with st.expander("Explore Raw Data", expanded=False):
        search = st.text_input("Search by name / college / state / event")
        display_df = fdf.copy()
        if search:
            mask = display_df.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
            )
            display_df = display_df[mask]
        st.dataframe(display_df.drop(columns=["Phone Number"]), use_container_width=True, height=400)
        st.download_button(
            "Download Filtered Data",
            display_df.to_csv(index=False),
            file_name="gateways2025_filtered.csv",
            mime="text/csv",
        )