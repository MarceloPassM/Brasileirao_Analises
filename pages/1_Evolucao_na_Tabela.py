import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.db import query
from utils.tabela import calcular_tabela

st.set_page_config(page_title="Evolucão na Tabela", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Barlow', sans-serif; background:#0a0f14; color:#e2e8f0; }
h1,h2,h3 { font-family: 'Barlow Condensed', sans-serif; }
[data-testid="stSidebar"] { background:#060b0f !important; border-right:2px solid #1a2332; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    anos = sorted(query("SELECT DISTINCT ano FROM jogos")["ano"].tolist())
    ano  = st.selectbox("Temporada", anos, index=len(anos) - 1)
    times_ano = sorted(query(f"SELECT DISTINCT mandante FROM jogos WHERE ano={ano}")["mandante"].tolist())
    times_sel = st.multiselect("Times:", times_ano, default=times_ano[:5] if len(times_ano) >= 5 else times_ano)

st.markdown(f"# Evolução na Tabela — {ano}")
st.caption("Acompanhe como cada time foi se posicionando rodada a rodada.")

if not times_sel:
    st.warning("Selecione pelo menos um time no menu lateral.")
    st.stop()

@st.cache_data
def get_evolucao(ano, times, max_r):
    rows = []
    for rodada in range(1, max_r + 1):
        tab = calcular_tabela(ano, rodada)
        tab_reset = tab.reset_index()
        for time in times:
            linha = tab_reset[tab_reset["Time"] == time]
            if not linha.empty:
                rows.append({
                    "rodada": rodada,
                    "time": time,
                    "pts": int(linha["Pts"].values[0]),
                    "pos": int(linha["Pos"].values[0]),
                    "aprov": float(linha["Aprov%"].values[0]),
                })
    return pd.DataFrame(rows)

with st.spinner("Calculando evolucão rodada a rodada..."):
    df_evo = get_evolucao(ano, times_sel, 38)

cores = px.colors.qualitative.Bold

st.markdown("### Pontuação Acumulada por Rodada")

fig_pts = go.Figure()
for i, time in enumerate(times_sel):
    sub = df_evo[df_evo["time"] == time]
    fig_pts.add_trace(go.Scatter(
        x=sub["rodada"], y=sub["pts"],
        mode="lines", name=time,
        line=dict(color=cores[i % len(cores)], width=2.5),
    ))

fig_pts.add_hline(y=45, line_dash="dot", line_color="#22c55e",
                  annotation_text="~G4", annotation_position="right")
fig_pts.add_hline(y=38, line_dash="dot", line_color="#f59e0b",
                  annotation_text="~Sul-Am.", annotation_position="right")

fig_pts.update_layout(
    template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=380, margin=dict(l=0, r=60, t=20, b=0),
    xaxis=dict(title="Rodada", showgrid=False, dtick=5),
    yaxis=dict(title="Pontos", showgrid=True, gridcolor="#1a2332"),
    legend=dict(orientation="h", y=1.08),
)
st.plotly_chart(fig_pts, use_container_width=True)

st.markdown("### Posição na Tabela por Rodada")
st.caption("Quanto mais baixo, melhor — posicão 1 e o líder.")

fig_pos = go.Figure()
for i, time in enumerate(times_sel):
    sub = df_evo[df_evo["time"] == time]
    fig_pos.add_trace(go.Scatter(
        x=sub["rodada"], y=sub["pos"],
        mode="lines", name=time,
        line=dict(color=cores[i % len(cores)], width=2.5),
    ))

fig_pos.add_hrect(y0=0.5, y1=4.5, fillcolor="#22c55e", opacity=0.06,
                  annotation_text="G4 Libertadores", annotation_position="right")
fig_pos.add_hrect(y0=16.5, y1=20.5, fillcolor="#ef4444", opacity=0.06,
                  annotation_text="Rebaixamento", annotation_position="right")

fig_pos.update_layout(
    template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=380, margin=dict(l=0, r=80, t=20, b=0),
    xaxis=dict(title="Rodada", showgrid=False, dtick=5),
    yaxis=dict(title="Posicao", autorange="reversed",
               tickvals=list(range(1, 21)), showgrid=True, gridcolor="#1a2332"),
    legend=dict(orientation="h", y=1.08),
)
st.plotly_chart(fig_pos, use_container_width=True)

st.markdown("### Aproveitamento por Turno")
col1, col2 = st.columns(2)

for col, titulo, r_min, r_max in [
    (col1, "1 Turno (Rod. 1-19)", 1, 19),
    (col2, "2 Turno (Rod. 20-38)", 20, 38),
]:
    with col:
        st.markdown(f"**{titulo}**")
        sub = df_evo[(df_evo["rodada"] >= r_min) & (df_evo["rodada"] <= r_max)]
        if sub.empty:
            st.caption("Dados não disponíveis.")
            continue
        last = sub.groupby("time").last().reset_index().sort_values("pts", ascending=False)
        fig_t = px.bar(
            last, x="time", y="aprov", color="time",
            color_discrete_sequence=cores,
            labels={"aprov": "Aproveitamento (%)", "time": ""},
            text=last["aprov"].apply(lambda x: f"{x:.0f}%"),
        )
        fig_t.update_traces(textposition="outside")
        fig_t.update_layout(
            template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis=dict(showgrid=False, tickangle=-30, tickfont=dict(size=10)),
            yaxis=dict(range=[0, 110], showgrid=True, gridcolor="#1a2332"),
        )
        st.plotly_chart(fig_t, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#2a4a6a; font-size:0.8rem; padding: 8px 0'>
    Desenvolvido por <strong>Marcelo</strong> · 
    <a href='https://github.com/MarceloPassM' target='_blank' style='color:#3b82f6'>GitHub</a>
</div>
""", unsafe_allow_html=True)