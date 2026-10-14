import streamlit as st

from src.charts import core_team_chart, group_mix_chart, women_share_chart
from src.data_loader import GROUP_NAME_COLUMN, GROUP_TYPE_COLUMN, apply_filters, load_data


st.set_page_config(page_title="WLD Engagement Dashboard", page_icon="▰", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Libre+Baskerville:wght@700&display=swap');
    .stApp { background: #f5f2ed; color: #33221e; }
    [data-testid="stHeader"] { background: rgba(245,242,237,0.88); }
    [data-testid="stSidebar"] { background: #33221e; }
    [data-testid="stSidebar"] * { color: #f5f2ed; }
    .block-container { max-width: 1400px; padding-top: 2.5rem; }
    h1, h2, h3 { font-family: 'Libre Baskerville', Georgia, serif; }
    p, label, div { font-family: 'DM Sans', 'Trebuchet MS', sans-serif; }
    .eyebrow { color: #007f78; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; }
    .subtitle { color: #746a63; margin-top: -.8rem; margin-bottom: 1.4rem; }
    .kpi { background: #fffdfa; border-top: 4px solid #d5a800; padding: 1rem 1.1rem; min-height: 115px; box-shadow: 0 2px 10px rgba(51,34,30,.06); }
    .kpi-label { color: #746a63; font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; }
    .kpi-value { color: #33221e; font-size: 2.05rem; font-weight: 700; line-height: 1.25; }
    .kpi-note { color: #007f78; font-size: .8rem; }
    div[data-testid="stPlotlyChart"] { background: #fffdfa; border-top: 3px solid #007f78; padding: .5rem; box-shadow: 0 2px 10px rgba(51,34,30,.06); }
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()

st.sidebar.markdown("## Dashboard filters")
st.sidebar.caption("Filter the survey responses shown below.")
group_types = st.sidebar.multiselect("Group type", sorted(df[GROUP_TYPE_COLUMN].dropna().unique()))
all_group_names = df[GROUP_NAME_COLUMN].dropna().unique()
visible_names = sorted([name for name in all_group_names if not group_types or name in df[df[GROUP_TYPE_COLUMN].isin(group_types)][GROUP_NAME_COLUMN].values])
group_names = st.sidebar.multiselect("Group name", visible_names)

filtered = apply_filters(df, group_types, group_names)

st.markdown('<div class="eyebrow">India Tech Center | Employee engagement</div>', unsafe_allow_html=True)
st.title("WLD Engagement Dashboard")
st.markdown("<div class=\"subtitle\">A focused view of group participation and women’s representation in core teams as of 1 October 2026.</div>", unsafe_allow_html=True)

if filtered.empty:
    st.info("No responses match the current filters.")
    st.stop()

team_total = filtered["Core team members"].sum()
women_total = filtered["Women core team members"].sum()
share = women_total / team_total * 100 if team_total else 0
group_total = filtered[GROUP_NAME_COLUMN].nunique()

kpis = st.columns(4)
for column, label, value, note in [
    (kpis[0], "Groups represented", f"{group_total}", "Clubs, BRGs, and CoPs"),
    (kpis[1], "Core team members", f"{team_total:.0f}", "across selected groups"),
    (kpis[2], "Women core members", f"{women_total:.0f}", f"{share:.0f}% of core teams"),
    (kpis[3], "Women representation", f"{share:.0f}%", "of selected core teams"),
]:
    with column:
        st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

st.markdown("### Participation profile")
left, right = st.columns(2)
with left:
    st.plotly_chart(group_mix_chart(filtered), use_container_width=True, config={"displayModeBar": False}, key="group_mix_participation")
with right:
    st.plotly_chart(core_team_chart(filtered), use_container_width=True, config={"displayModeBar": False}, key="core_team_by_group")

st.markdown("### Women’s representation")
left, right = st.columns(2)
with left:
    st.plotly_chart(women_share_chart(filtered), use_container_width=True, config={"displayModeBar": False}, key="women_share_by_group")
with right:
    st.plotly_chart(group_mix_chart(filtered), use_container_width=True, config={"displayModeBar": False}, key="group_mix_representation")

st.markdown("### Member representation register")
display_columns = [GROUP_TYPE_COLUMN, GROUP_NAME_COLUMN, "Full Name", "Core team members", "Women core team members", "Women share of core team"]
display = filtered[display_columns].rename(columns={GROUP_TYPE_COLUMN: "Group type", GROUP_NAME_COLUMN: "Group name", "Full Name": "Chair name", "Women core team members": "Women core members", "Women share of core team": "Women share (%)"}).copy()
display["Women share (%)"] = display["Women share (%)"].round(1)
st.dataframe(display, use_container_width=True, hide_index=True, column_config={"Women share (%)": st.column_config.NumberColumn(format="%.1f%%")})
