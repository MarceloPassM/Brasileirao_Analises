import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.db import query

st.set_page_config(page_title="Head-to-Head", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family:'Barlow',sans-serif; background:#0a0f14; color:#e2e8f0; }
h1,h2,h3 { font-family:'Barlow Condensed',sans-serif; }
[data-testid="stSidebar"] { background:#060b0f !important; border-right:2px solid #1a2332; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
.stat-box { background:#0d1b2a; border:1px solid #1e3a5f; border-radius:8px;
            padding:0.8rem 1rem; text-align:center; margin:4px 0; }
.stat-label { font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase; color:#4a6580; }
.stat-val   { font-size:1.6rem; font-weight:800; font-family:'Barlow Condensed',sans-serif; }
</style>
""", unsafe_allow_html=True)

todos_times = sorted(query("SELECT DISTINCT mandante FROM jogos")["mandante"].tolist())
anos_disp   = sorted(query("SELECT DISTINCT ano FROM jogos")["ano"].tolist())

with st.sidebar:
    time1 = st.selectbox("Time 1:", todos_times,
                         index=todos_times.index("Flamengo") if "Flamengo" in todos_times else 0)
    time2 = st.selectbox("Time 2:", todos_times,
                         index=todos_times.index("Palmeiras") if "Palmeiras" in todos_times else 1)
    anos_sel = st.multiselect("Temporadas:", anos_disp, default=anos_disp)

st.markdown("# Head-to-Head")

col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
with col_t1:
    st.markdown(f"<h2 style='text-align:right;color:#3b82f6'>{time1}</h2>", unsafe_allow_html=True)
with col_vs:
    st.markdown("<div style='font-family:Barlow Condensed,sans-serif;font-size:3rem;font-weight:800;text-align:center;color:#1e3a5f;padding:0.5rem 0'>vs</div>", unsafe_allow_html=True)
with col_t2:
    st.markdown(f"<h2 style='color:#ef4444'>{time2}</h2>", unsafe_allow_html=True)

if time1 == time2:
    st.warning("Selecione dois times diferentes.")
    st.stop()

if not anos_sel:
    st.warning("Selecione pelo menos uma temporada.")
    st.stop()

anos_str = ",".join(map(str, anos_sel))

@st.cache_data
def get_h2h(t1, t2, anos_str):
    sql = f"""
    SELECT * FROM jogos
    WHERE ano IN ({anos_str})
      AND ((mandante = '{t1}' AND visitante = '{t2}')
        OR (mandante = '{t2}' AND visitante = '{t1}'))
    ORDER BY ano, rodada
    """
    return query(sql)

df = get_h2h(time1, time2, anos_str)

if df.empty:
    st.info("Nenhum confronto encontrado para os filtros selecionados.")
    st.stop()

v1 = ((df["mandante"] == time1) & (df["resultado"] == "V. Mandante")).sum() + \
     ((df["visitante"] == time1) & (df["resultado"] == "V. Visitante")).sum()
v2 = ((df["mandante"] == time2) & (df["resultado"] == "V. Mandante")).sum() + \
     ((df["visitante"] == time2) & (df["resultado"] == "V. Visitante")).sum()
emp = (df["resultado"] == "Empate").sum()

gols1 = (df[df["mandante"] == time1]["gols_mandante"].sum() +
         df[df["visitante"] == time1]["gols_visitante"].sum())
gols2 = (df[df["mandante"] == time2]["gols_mandante"].sum() +
         df[df["visitante"] == time2]["gols_visitante"].sum())

total = len(df)

st.markdown("")
ca, cb, cc = st.columns(3)
stats = [
    (ca, time1, v1, f"{v1/total*100:.0f}%", "#3b82f6"),
    (cb, "Empates", emp, f"{emp/total*100:.0f}%", "#94a3b8"),
    (cc, time2, v2, f"{v2/total*100:.0f}%", "#ef4444"),
]
for col, label, val, pct, cor in stats:
    with col:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-label">{label}</div>
          <div class="stat-val" style="color:{cor}">{val}</div>
          <div class="stat-label">{pct} dos jogos</div>
        </div>""", unsafe_allow_html=True)

st.markdown("")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Distribuicao de Resultados")
    fig_pie = go.Figure(go.Pie(
        labels=[f"Vitorias {time1}", "Empates", f"Vitorias {time2}"],
        values=[v1, emp, v2],
        marker_colors=["#3b82f6", "#64748b", "#ef4444"],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(size=11),
    ))
    fig_pie.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0f14",
        height=300, margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("### Gols nos Confrontos")
    fig_gols = go.Figure()
    fig_gols.add_trace(go.Bar(
        name=time1, x=["Gols Marcados"], y=[gols1],
        marker_color="#3b82f6", text=[gols1], textposition="outside",
    ))
    fig_gols.add_trace(go.Bar(
        name=time2, x=["Gols Marcados"], y=[gols2],
        marker_color="#ef4444", text=[gols2], textposition="outside",
    ))
    fig_gols.update_layout(
        barmode="group", template="plotly_dark",
        plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=300, margin=dict(l=0, r=0, t=20, b=0),
        xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor="#1a2332",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_gols, use_container_width=True)

st.markdown("### Historico de Confrontos")

display = df[["ano", "rodada", "mandante", "gols_mandante", "gols_visitante", "visitante", "resultado"]].copy()
display.columns = ["Ano", "Rodada", "Mandante", "GM", "GV", "Visitante", "Resultado"]

st.dataframe(display, use_container_width=True, hide_index=True)

placar = df.apply(lambda r: f"{r['gols_mandante']}x{r['gols_visitante']}", axis=1)
mais_comum = placar.value_counts().head(3)
st.markdown("**Placares mais frequentes:**")
for placar_str, count in mais_comum.items():
    st.markdown(f"- `{placar_str}` — {count}x")