import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from movies.analytics import genre_revenue


def render(movies: pd.DataFrame) -> None:
    st.subheader("Allocated revenue by genre")
    st.caption("Each movie's revenue is divided equally among its unique genres. "
               "A movie earning USD 90 million across three genres contributes USD 30 million to each.")
    totals = genre_revenue(movies)
    if totals.revenue.sum() <= 0:
        st.info("There is no positive revenue to display. Adjust or clear the sidebar filters.")
        return
    view = st.radio("Genre chart", ["Ranked bars", "Pie chart"], horizontal=True, key="genre_view")
    if view == "Ranked bars":
        chart = go.Figure(go.Bar(
            x=totals.revenue.tolist(), y=totals.genre.tolist(), orientation="h",
            marker_color="#2563eb", customdata=(totals.revenue / totals.revenue.sum() * 100).tolist(),
            hovertemplate="%{y}<br>Allocated revenue (USD): $%{x:,.2f}"
                          "<br>Share: %{customdata:.2f}%<extra></extra>"))
        chart.update_layout(height=max(360, len(totals) * 29), xaxis_title="Allocated revenue (USD)",
                             yaxis=dict(autorange="reversed"),
                             margin=dict(l=20, r=20, t=20, b=30))
        chart.update_xaxes(tickprefix="$", tickformat="~s")
    else:
        chart = px.pie(totals, names="genre", values="revenue", hole=0.35,
                       color_discrete_sequence=px.colors.qualitative.Alphabet)
        chart.update_traces(textposition="inside", textinfo="percent", sort=False,
                             hovertemplate="%{label}<br>Allocated revenue (USD): $%{value:,.2f}<br>Share: %{percent}<extra></extra>")
        chart.update_layout(height=540, margin=dict(l=20, r=20, t=20, b=20),
                             legend_title_text="Genre", uniformtext_minsize=11, uniformtext_mode="hide")
    st.plotly_chart(chart, key="genre_chart", width="stretch")
    st.caption(f"{len(totals)} unique genres · Allocated revenue (USD): ${totals.revenue.sum():,.2f}")
    with st.expander("See exact genre totals"):
        table = totals.assign(share=totals.revenue / totals.revenue.sum() * 100)
        st.dataframe(table, hide_index=True, width="stretch", column_config={
            "revenue": st.column_config.NumberColumn("Allocated revenue (USD)", format="dollar", step=0.01),
            "share": st.column_config.NumberColumn("Share (%)", format="%.2f"),
        })
