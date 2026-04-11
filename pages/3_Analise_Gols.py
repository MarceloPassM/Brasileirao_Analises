import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.db import query

st.set_page_config(page_title="Analise de Gols", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family:'Barlow',sans-serif; background:#0a0f14; color:#e2e8f0; }
h1,h2,h3 { font-family:'Barlow Condensed',sans-serif; }
[data-testid="stSidebar"] { background:#060b0f !important; border-right:2px solid #1a2332; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
.kpi { background:#0d1b2a; border:1px solid #1e3a5f; border-radius:8px;
       padding:0.9rem 1rem; text-align:center; }
.kpi .label { font-size:0.63rem; letter-spacing:0.15em; text-transform:uppercase; color:#4a6580; }
.kpi .value { font-size:1.8rem; font-weight:800; font-family:'Barlow Condensed',sans-serif; color:#e2f0ff; }
</style>
""", unsafe_allow_html=True)

anos_disp = sorted(query("SELECT DISTINCT ano FROM jogos")["ano"].tolist())

with st.sidebar:
    anos_sel = st.multiselect("Temporadas:", anos_disp, default=anos_disp)

st.markdown("# Análise de Gols")
st.caption("Distribuição, médias, padrões de casa vs fora e over/under.")

if not anos_sel:
    st.warning("Selecione pelo menos uma temporada.")
    st.stop()

anos_str = ",".join(map(str, anos_sel))

@st.cache_data
def load_gols(anos_str):
    return query(f"""
        SELECT *, gols_mandante + gols_visitante AS total_gols
        FROM jogos WHERE ano IN ({anos_str})
    """)

df = load_gols(anos_str)

media_gols = df["total_gols"].mean()
over25     = (df["total_gols"] > 2.5).mean() * 100
btts       = ((df["gols_mandante"] > 0) & (df["gols_visitante"] > 0)).mean() * 100
max_gols   = df["total_gols"].max()

c1, c2, c3, c4 = st.columns(4)
for col, label, val in zip(
    [c1, c2, c3, c4],
    ["Média de Gols/Jogo", "Over 2.5 (%)", "Ambos Marcam (%)", "Maior Placar (total)"],
    [f"{media_gols:.2f}", f"{over25:.1f}%", f"{btts:.1f}%", f"{int(max_gols)} gols"],
):
    with col:
        st.markdown(f"""
        <div class="kpi">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Distribuição de Gols por Jogo")
    contagem = df["total_gols"].value_counts().sort_index().reset_index()
    contagem.columns = ["Gols", "Jogos"]
    fig_dist = px.bar(
        contagem, x="Gols", y="Jogos",
        color="Gols", color_continuous_scale="Blues",
        text="Jogos",
    )
    fig_dist.add_vline(x=media_gols, line_dash="dash", line_color="#f59e0b",
                       annotation_text=f"Media: {media_gols:.1f}", annotation_position="top right")
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(
        template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=320, margin=dict(l=0, r=0, t=20, b=0),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=True, gridcolor="#1a2332"),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col2:
    st.markdown("### Gols por Temporada")
    por_ano = query(f"""
        SELECT ano,
            AVG(gols_mandante + gols_visitante) AS media_gols,
            AVG(gols_mandante)  AS media_casa,
            AVG(gols_visitante) AS media_fora
        FROM jogos WHERE ano IN ({anos_str})
        GROUP BY ano ORDER BY ano
    """)
    fig_ano = go.Figure()
    fig_ano.add_trace(go.Bar(name="Gols casa", x=por_ano["ano"], y=por_ano["media_casa"],
                             marker_color="#3b82f6"))
    fig_ano.add_trace(go.Bar(name="Gols fora", x=por_ano["ano"], y=por_ano["media_fora"],
                             marker_color="#ef4444"))
    fig_ano.update_layout(
        barmode="stack", template="plotly_dark",
        plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=320, margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=True, gridcolor="#1a2332", title="Media gols/jogo"),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_ano, use_container_width=True)

st.markdown("### Vantagem de Jogar em Casa")

casa_stats = query(f"""
    SELECT
        'Casa' AS local,
        AVG(gols_mandante)  AS gols_avg,
        SUM(CASE WHEN resultado='V. Mandante' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS aprov
    FROM jogos WHERE ano IN ({anos_str})
    UNION ALL
    SELECT
        'Fora' AS local,
        AVG(gols_visitante) AS gols_avg,
        SUM(CASE WHEN resultado='V. Visitante' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS aprov
    FROM jogos WHERE ano IN ({anos_str})
""")

col3, col4 = st.columns(2)
with col3:
    fig_casa = px.bar(
        casa_stats, x="local", y="gols_avg", color="local",
        color_discrete_map={"Casa": "#3b82f6", "Fora": "#ef4444"},
        text=casa_stats["gols_avg"].apply(lambda x: f"{x:.2f}"),
        labels={"gols_avg": "Média de Gols", "local": ""},
        title="Média de Gols (Casa vs Fora)",
    )
    fig_casa.update_traces(textposition="outside")
    fig_casa.update_layout(
        template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=280, margin=dict(l=0, r=0, t=40, b=0), showlegend=False,
        xaxis_showgrid=False, yaxis=dict(showgrid=True, gridcolor="#1a2332"),
    )
    st.plotly_chart(fig_casa, use_container_width=True)

with col4:
    fig_aprov = px.bar(
        casa_stats, x="local", y="aprov", color="local",
        color_discrete_map={"Casa": "#3b82f6", "Fora": "#ef4444"},
        text=casa_stats["aprov"].apply(lambda x: f"{x:.1f}%"),
        labels={"aprov": "Aproveitamento (%)", "local": ""},
        title="Aproveitamento (Casa vs Fora)",
    )
    fig_aprov.update_traces(textposition="outside")
    fig_aprov.update_layout(
        template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=280, margin=dict(l=0, r=0, t=40, b=0), showlegend=False,
        xaxis_showgrid=False, yaxis=dict(range=[0, 60], showgrid=True, gridcolor="#1a2332"),
    )
    st.plotly_chart(fig_aprov, use_container_width=True)

st.markdown("### Ranking de Gols por Time")

gols_time = query(f"""
    SELECT time,
        SUM(gp) AS gols_marcados,
        SUM(gc) AS gols_sofridos,
        SUM(gp) - SUM(gc) AS saldo
    FROM (
        SELECT mandante AS time, gols_mandante AS gp, gols_visitante AS gc
        FROM jogos WHERE ano IN ({anos_str})
        UNION ALL
        SELECT visitante, gols_visitante, gols_mandante
        FROM jogos WHERE ano IN ({anos_str})
    )
    GROUP BY time ORDER BY gols_marcados DESC
""")

fig_rank = go.Figure()
fig_rank.add_trace(go.Bar(name="Gols Marcados", x=gols_time["time"], y=gols_time["gols_marcados"],
                          marker_color="#3b82f6", opacity=0.9))
fig_rank.add_trace(go.Bar(name="Gols Sofridos", x=gols_time["time"], y=gols_time["gols_sofridos"],
                          marker_color="#ef4444", opacity=0.75))
fig_rank.update_layout(
    barmode="group", template="plotly_dark",
    plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=320, margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#1a2332"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig_rank, use_container_width=True)