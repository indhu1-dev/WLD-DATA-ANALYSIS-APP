import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEAL = "#007f78"
GOLD = "#d5a800"
INK = "#33221e"
MIST = "#e8e3dc"


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": INK}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Trebuchet MS", "color": INK},
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        hoverlabel={"font": {"family": "Trebuchet MS"}},
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eee9e2", zeroline=False)
    return fig


def group_mix_chart(df: pd.DataFrame) -> go.Figure:
    counts = (
        df.groupby("Which Employee Engagement Group you are in?", as_index=False)
        .agg({"Core team members": "sum", "Women core team members": "sum"})
        .rename(columns={"Which Employee Engagement Group you are in?": "Group type"})
    )
    counts["Other core members"] = counts["Core team members"] - counts["Women core team members"]
    plot_df = counts.melt(
        id_vars="Group type",
        value_vars=["Women core team members", "Other core members"],
        var_name="Member category",
        value_name="Members",
    )
    fig = px.bar(
        plot_df,
        x="Group type",
        y="Members",
        color="Member category",
        text="Members",
        barmode="stack",
        color_discrete_map={"Women core team members": TEAL, "Other core members": MIST},
        labels={"Members": "Core team members", "Group type": "", "Member category": ""},
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{text:.0f}", textposition="inside")
    return _base_layout(fig, "Core-team representation by group type")


def core_team_chart(df: pd.DataFrame) -> go.Figure:
    plot_df = df.sort_values("Core team members", ascending=True)
    fig = px.bar(
        plot_df,
        x="Core team members",
        y="Employee Engagement Group (BRG/CoP/Club) Name",
        orientation="h",
        color="Women core team members",
        color_continuous_scale=[MIST, TEAL],
        labels={"Core team members": "Core team members", "Employee Engagement Group (BRG/CoP/Club) Name": ""},
        hover_data={"Women core team members": True, "Core team members": True},
    )
    fig.update_traces(marker_line_width=0)
    fig.update_coloraxes(colorbar_title="Women")
    return _base_layout(fig, "Core team size by group")


def women_share_chart(df: pd.DataFrame) -> go.Figure:
    plot_df = df.sort_values("Women share of core team", ascending=True)
    fig = px.bar(
        plot_df,
        x="Women share of core team",
        y="Employee Engagement Group (BRG/CoP/Club) Name",
        orientation="h",
        text="Women share of core team",
        color_discrete_sequence=[GOLD],
        labels={"Women share of core team": "Women share (%)", "Employee Engagement Group (BRG/CoP/Club) Name": ""},
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside", marker_line_width=0)
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return _base_layout(fig, "Women representation within core teams")


def leadership_representation_chart() -> go.Figure:
    plot_df = pd.DataFrame(
        {
            "Leadership level": ["Senior Director", "Director", "Senior ADM", "ADM"],
            "Total leaders": [1, 6, 0, 53],
            "Women leaders": [1, 0, 0, 12],
        }
    )
    plot_df["Women / total"] = plot_df.apply(
        lambda row: f"{row['Women leaders']} / {row['Total leaders']}"
        + ("*" if row["Leadership level"] == "Senior ADM" else ""),
        axis=1,
    )
    fig = px.bar(
        plot_df,
        x="Women leaders",
        y="Leadership level",
        orientation="h",
        text="Women / total",
        color_discrete_sequence=[TEAL],
        labels={"Women leaders": "Women leaders", "Leadership level": ""},
        hover_data={"Women leaders": True, "Total leaders": True},
    )
    fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
    fig.update_xaxes(range=[0, 60], dtick=10)
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=["ADM", "Senior ADM", "Director", "Senior Director"],
    )
    return _base_layout(fig, "Women leaders by level (women / total)")


