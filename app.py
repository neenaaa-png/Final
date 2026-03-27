import streamlit as st
import pandas as pd
import plotly.express as px
import re
from collections import Counter

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GATEWAYS 2025 – Fest Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] { background: linear-gradient(160deg,#0f172a,#1e3a5f); }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    [data-testid="metric-container"] {
        background: linear-gradient(135deg,#1e3a5f,#0f172a);
        border: 1px solid #334155; border-radius: 14px;
        padding: 18px 20px; color: white !important;
    }
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="stMetricDelta"]
        { color: white !important; }

    .section-header {
        background: linear-gradient(90deg,#1e3a5f,#0f172a);
        color: white; border-radius: 10px;
        padding: 10px 20px; margin-bottom: 18px;
        font-size: 22px; font-weight: 700;
    }
    .insight-card {
        background: #f8fafc; border-left: 4px solid #3b82f6;
        border-radius: 8px; padding: 14px 18px;
        margin: 8px 0; font-size: 14px; color: #1e293b;
    }
    .insight-card strong { color: #1d4ed8; }
    .title-banner {
        background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#1d4ed8 100%);
        color: white; border-radius: 16px;
        padding: 30px 40px; margin-bottom: 28px; text-align: center;
    }
    .title-banner h1 { font-size: 2.4rem; margin: 0; font-weight: 700; }
    .title-banner p  { margin: 6px 0 0; font-size: 1.05rem; opacity: .85; }
</style>
""", unsafe_allow_html=True)

# ── Load CSV ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("fest_dataset.csv")
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df.dropna(subset=['Rating'], inplace=True)
    df['Rating'] = df['Rating'].astype(int)
    df['Amount Paid'] = pd.to_numeric(df['Amount Paid'], errors='coerce').fillna(0).astype(int)
    return df

df = load_data()

# State coordinates for India map
STATE_COORDS = {
    "Karnataka":     (15.3173,  75.7139),
    "Tamil Nadu":    (11.1271,  78.6569),
    "Kerala":        (10.8505,  76.2711),
    "Maharashtra":   (19.7515,  75.7139),
    "Gujarat":       (22.2587,  71.1924),
    "Rajasthan":     (27.0238,  74.2179),
    "Delhi":         (28.7041,  77.1025),
    "Telangana":     (18.1124,  79.0193),
    "Uttar Pradesh": (26.8467,  80.9462),
}

PALETTE = ["#1d4ed8","#7c3aed","#0891b2","#059669","#d97706","#dc2626","#ec4899","#f59e0b"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=70)
    st.markdown("## 🎓 GATEWAYS 2025")
    st.markdown("**National Level Tech Fest**")
    st.markdown("---")
    page = st.radio(
        " Navigate to",
        [" Overview", "Participation Trends", "Feedback & Ratings", "Interactive Dashboard"],
    )
    st.markdown("---")
    st.markdown("### 🔧 Filters")
    selected_states = st.multiselect("Filter by State",  sorted(df['State'].unique()),      default=[])
    selected_events = st.multiselect("Filter by Event",  sorted(df['Event Name'].unique()), default=[])

    fdf = df.copy()
    if selected_states:
        fdf = fdf[fdf['State'].isin(selected_states)]
    if selected_events:
        fdf = fdf[fdf['Event Name'].isin(selected_events)]

    st.markdown(f"**Showing:** {len(fdf)} of {len(df)} participants")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown("""
    <div class="title-banner">
        <h1> GATEWAYS 2025</h1>
        <p>National Level Tech Fest — Analytics Dashboard</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(" Total Participants", len(fdf))
    c2.metric(" Colleges",           fdf['College'].nunique())
    c3.metric(" States",             fdf['State'].nunique())
    c4.metric(" Avg Rating",          f"{fdf['Rating'].mean():.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(" Events",       fdf['Event Name'].nunique())
    c6.metric("Total Revenue", f"₹{fdf['Amount Paid'].sum():,.0f}")
    c7.metric(" Individual",   int((fdf['Event Type'] == 'Individual').sum()))
    c8.metric(" Group",        int((fdf['Event Type'] == 'Group').sum()))

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        ec = fdf['Event Name'].value_counts().reset_index()
        ec.columns = ['Event', 'Count']
        fig = px.bar(ec, x='Count', y='Event', orientation='h',
                     color='Count', color_continuous_scale='Blues',
                     title="Participants per Event")
        fig.update_layout(showlegend=False, height=350,
                          yaxis={'categoryorder': 'total ascending'},
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sc = fdf['State'].value_counts().reset_index()
        sc.columns = ['State', 'Count']
        fig2 = px.pie(sc, names='State', values='Count',
                      color_discrete_sequence=PALETTE,
                      title="State-wise Distribution", hole=0.4)
        fig2.update_layout(height=350,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – PARTICIPATION TRENDS + INDIA MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == " Participation Trends":
    st.markdown('<div class="section-header"> Participation Trends & India Map</div>',
                unsafe_allow_html=True)

    # India Bubble Map
    state_count = fdf['State'].value_counts().reset_index()
    state_count.columns = ['State', 'Participants']
    state_count['lat'] = state_count['State'].map(lambda s: STATE_COORDS.get(s, (20, 77))[0])
    state_count['lon'] = state_count['State'].map(lambda s: STATE_COORDS.get(s, (20, 77))[1])

    fig_map = px.scatter_geo(
        state_count,
        lat='lat', lon='lon',
        size='Participants',
        color='Participants',
        hover_name='State',
        hover_data={'lat': False, 'lon': False, 'Participants': True},
        color_continuous_scale='Blues',
        size_max=55,
        title=" State-wise Participants across India",
        scope='asia',
    )
    fig_map.update_geos(
        center={"lat": 20.5937, "lon": 78.9629},
        projection_scale=4.5,
        showcountries=True, countrycolor="#94a3b8",
        showland=True,  landcolor="#f1f5f9",
        showocean=True, oceancolor="#e0f2fe",
        lataxis_range=[6, 36], lonaxis_range=[66, 98],
    )
    fig_map.update_layout(height=520, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        top_colleges = fdf['College'].value_counts().head(10).reset_index()
        top_colleges.columns = ['College', 'Count']
        fig_col = px.bar(top_colleges, x='College', y='Count',
                         color='Count', color_continuous_scale='Purples',
                         title="Top 10 Colleges by Participation")
        fig_col.update_layout(xaxis_tickangle=-35, showlegend=False,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=380)
        st.plotly_chart(fig_col, use_container_width=True)

    with col2:
        et = fdf.groupby(['Event Name', 'Event Type']).size().reset_index(name='Count')
        fig_et = px.bar(et, x='Event Name', y='Count', color='Event Type',
                        barmode='group', title="Individual vs Group per Event",
                        color_discrete_map={'Individual': '#1d4ed8', 'Group': '#7c3aed'})
        fig_et.update_layout(xaxis_tickangle=-35,
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=380)
        st.plotly_chart(fig_et, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        rev = fdf.groupby('Event Name')['Amount Paid'].sum().reset_index()
        rev.columns = ['Event', 'Revenue']
        rev = rev.sort_values('Revenue', ascending=False)
        fig_rev = px.funnel(rev, x='Revenue', y='Event',
                            title="💰 Revenue Funnel by Event",
                            color_discrete_sequence=['#1d4ed8'])
        fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=380)
        st.plotly_chart(fig_rev, use_container_width=True)

    with col4:
        hm = fdf.groupby(['State', 'Event Name']).size().reset_index(name='Count')
        hm_pivot = hm.pivot(index='State', columns='Event Name', values='Count').fillna(0)
        fig_hm = px.imshow(hm_pivot, text_auto=True, aspect='auto',
                           color_continuous_scale='Blues',
                           title="State × Event Participation Heatmap")
        fig_hm.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=380)
        st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – FEEDBACK & RATINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == " Feedback & Ratings":
    st.markdown('<div class="section-header">Feedback Analysis & Ratings</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        rc = fdf['Rating'].value_counts().sort_index().reset_index()
        rc.columns = ['Rating', 'Count']
        fig_r = px.bar(rc, x='Rating', y='Count', color='Count',
                       color_continuous_scale='Blues',
                       title="⭐ Overall Rating Distribution",
                       labels={'Rating': 'Rating (1-5)', 'Count': 'No. of Participants'})
        fig_r.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig_r, use_container_width=True)

    with col2:
        avg_ev = fdf.groupby('Event Name')['Rating'].mean().round(2).reset_index()
        avg_ev.columns = ['Event', 'Avg Rating']
        avg_ev = avg_ev.sort_values('Avg Rating', ascending=True)
        fig_avg = px.bar(avg_ev, x='Avg Rating', y='Event', orientation='h',
                         color='Avg Rating', color_continuous_scale='RdYlGn',
                         range_color=[1, 5], title="Average Rating per Event")
        fig_avg.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig_avg, use_container_width=True)

    st.markdown("---")

    all_feedback = ' '.join(fdf['Feedback'].dropna().str.lower())
    stop = {'and', 'the', 'a', 'in', 'of', 'to', 'is', 'it', 'was', 'for', 'on', 'with', 'very'}
    words = [w for w in re.findall(r'\b[a-z]+\b', all_feedback) if w not in stop and len(w) > 3]
    word_freq = Counter(words).most_common(20)
    wdf = pd.DataFrame(word_freq, columns=['Word', 'Count'])

    col3, col4 = st.columns(2)
    with col3:
        fig_w = px.bar(wdf, x='Count', y='Word', orientation='h',
                       color='Count', color_continuous_scale='Teal',
                       title="🔤 Top Keywords in Feedback")
        fig_w.update_layout(yaxis={'categoryorder': 'total ascending'},
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450)
        st.plotly_chart(fig_w, use_container_width=True)

    with col4:
        fig_box = px.box(fdf, x='State', y='Rating', color='State',
                         color_discrete_sequence=PALETTE,
                         title="Rating Spread by State")
        fig_box.update_layout(xaxis_tickangle=-35, showlegend=False,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    feedback_cats = fdf['Feedback'].value_counts().reset_index()
    feedback_cats.columns = ['Feedback', 'Count']
    fig_fb = px.treemap(feedback_cats, path=['Feedback'], values='Count',
                        color='Count', color_continuous_scale='Blues',
                        title=" Feedback Category Treemap")
    fig_fb.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=380)
    st.plotly_chart(fig_fb, use_container_width=True)

    fig_sc = px.scatter(fdf, x='Amount Paid', y='Rating',
                        color='Event Name', symbol='Event Type',
                        color_discrete_sequence=PALETTE,
                        title="Amount Paid vs Rating (per Event)",
                        opacity=0.75,
                        hover_data=['College', 'State'])
    fig_sc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=380)
    st.plotly_chart(fig_sc, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – INTERACTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Interactive Dashboard":
    st.markdown('<div class="section-header"> Interactive Insights Dashboard</div>',
                unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Participants", len(fdf))
    kpi2.metric("Avg Rating",          f"{fdf['Rating'].mean():.2f}")
    kpi3.metric("Total Revenue",       f"₹{fdf['Amount Paid'].sum():,}")
    kpi4.metric("High Rated (4-5 )", int((fdf['Rating'] >= 4).sum()))
    kpi5.metric("% Satisfied",         f"{100*(fdf['Rating'] >= 4).mean():.1f}%")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["College Analysis", " State Analysis", " Event Deep Dive"])

    with tab1:
        college_sel = st.selectbox("Select College", sorted(fdf['College'].unique()))
        cdf = fdf[fdf['College'] == college_sel]
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Participants", len(cdf))
        cc2.metric("Avg Rating",   f"{cdf['Rating'].mean():.2f}")
        cc3.metric("Revenue",      f"₹{cdf['Amount Paid'].sum():,}")
        c1, c2 = st.columns(2)
        with c1:
            ev_c = cdf['Event Name'].value_counts().reset_index()
            ev_c.columns = ['Event', 'Count']
            fig = px.pie(ev_c, names='Event', values='Count',
                         title=f"Events – {college_sel}",
                         color_discrete_sequence=PALETTE, hole=0.3)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st_c = cdf['State'].value_counts().reset_index()
            st_c.columns = ['State', 'Count']
            fig2 = px.bar(st_c, x='State', y='Count', color='Count',
                          color_continuous_scale='Blues',
                          title=f"States – {college_sel}")
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        state_sel = st.selectbox("Select State", sorted(fdf['State'].unique()))
        sdf = fdf[fdf['State'] == state_sel]
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Participants", len(sdf))
        sc2.metric("Avg Rating",   f"{sdf['Rating'].mean():.2f}")
        sc3.metric("Revenue",      f"₹{sdf['Amount Paid'].sum():,}")
        s1, s2 = st.columns(2)
        with s1:
            ev_s = sdf['Event Name'].value_counts().reset_index()
            ev_s.columns = ['Event', 'Count']
            fig_s = px.bar(ev_s, x='Event', y='Count',
                           color='Count', color_continuous_scale='Teal',
                           title=f"Popular Events – {state_sel}")
            fig_s.update_layout(xaxis_tickangle=-25, plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig_s, use_container_width=True)
        with s2:
            col_s = sdf['College'].value_counts().reset_index()
            col_s.columns = ['College', 'Count']
            fig_cs = px.pie(col_s, names='College', values='Count',
                            title=f"Colleges from {state_sel}",
                            color_discrete_sequence=PALETTE, hole=0.3)
            fig_cs.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig_cs, use_container_width=True)

    with tab3:
        event_sel = st.selectbox("Select Event", sorted(fdf['Event Name'].unique()))
        edf = fdf[fdf['Event Name'] == event_sel]
        ec1, ec2, ec3, ec4 = st.columns(4)
        ec1.metric("Participants", len(edf))
        ec2.metric("Avg Rating",   f"{edf['Rating'].mean():.2f}")
        ec3.metric("Revenue",      f"₹{edf['Amount Paid'].sum():,}")
        ec4.metric("Top College",  edf['College'].value_counts().idxmax())
        e1, e2 = st.columns(2)
        with e1:
            rat_e = edf['Rating'].value_counts().sort_index().reset_index()
            rat_e.columns = ['Rating', 'Count']
            fig_re = px.bar(rat_e, x='Rating', y='Count',
                            color='Count', color_continuous_scale='RdYlGn',
                            title=f"Ratings – {event_sel}")
            fig_re.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig_re, use_container_width=True)
        with e2:
            st_e = edf['State'].value_counts().reset_index()
            st_e.columns = ['State', 'Participants']
            fig_se = px.bar(st_e, x='State', y='Participants',
                            color='Participants', color_continuous_scale='Blues',
                            title=f"States – {event_sel}")
            fig_se.update_layout(xaxis_tickangle=-30, plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig_se, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Key Actionable Insights")
    top_event   = fdf['Event Name'].value_counts().idxmax()
    top_state   = fdf['State'].value_counts().idxmax()
    top_college = fdf['College'].value_counts().idxmax()
    best_rated  = fdf.groupby('Event Name')['Rating'].mean().idxmax()
    most_rev    = fdf.groupby('Event Name')['Amount Paid'].sum().idxmax()
    low_rated   = fdf.groupby('Event Name')['Rating'].mean().idxmin()
    pct_sat     = 100 * (fdf['Rating'] >= 4).mean()

    for ins in [
        f"<strong> Most Popular Event:</strong> <em>{top_event}</em> attracted the highest number of participants.",
        f"<strong> Leading State:</strong> <em>{top_state}</em> sent the most participants.",
        f"<strong> Top College:</strong> <em>{top_college}</em> had the highest representation.",
        f"<strong> Best Rated Event:</strong> <em>{best_rated}</em> scored the highest average rating.",
        f"<strong> Highest Revenue Event:</strong> <em>{most_rev}</em> generated the most revenue.",
        f"<strong> Needs Improvement:</strong> <em>{low_rated}</em> received the lowest average rating.",
        f"<strong> Satisfaction Rate:</strong> {pct_sat:.1f}% of participants rated 4 or above.",
    ]:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🗃️ Explore Raw Data", expanded=False):
        search = st.text_input("Search by name / college / state / event")
        display_df = fdf.copy()
        if search:
            mask = display_df.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
            )
            display_df = display_df[mask]
        st.dataframe(display_df.drop(columns=['Phone Number']), use_container_width=True, height=400)
        st.download_button("Download Filtered Data",
                           display_df.to_csv(index=False),
                           file_name="gateways2025_filtered.csv",
                           mime="text/csv")
