import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.db import query
from utils.tabela import calcular_tabela

st.set_page_config(page_title="Zona de Rebaixamento", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family:'Barlow',sans-serif; background:#0a0f14; color:#e2e8f0; }
h1,h2,h3 { font-family:'Barlow Condensed',sans-serif; }
[data-testid="stSidebar"] { background:#060b0f !important; border-right:2px solid #1a2332; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

anos_disp = sorted(query("SELECT DISTINCT ano FROM jogos")["ano"].tolist())

with st.sidebar:
    ano = st.selectbox("Temporada:", anos_disp, index=len(anos_disp) - 1)

# Numero de times e rodadas do ano selecionado
max_rodada  = int(query(f"SELECT MAX(rodada) FROM jogos WHERE ano={ano}").iloc[0, 0])
total_times = int(query(f"SELECT COUNT(DISTINCT mandante) FROM jogos WHERE ano={ano}").iloc[0, 0])

# Numero de rebaixados por ano
REB_POR_ANO = {2003: 2}
n_reb = REB_POR_ANO.get(ano, 4)

st.markdown(f"# Zona de Rebaixamento — {ano}")
st.caption(f"Evolução dos times que fecharam a temporada nas últimas {n_reb} posições.")

@st.cache_data
def get_rebaixados(ano, max_rodada, n_reb):
    tab_final = calcular_tabela(ano, max_rodada)
    rebaixados = tab_final.tail(n_reb)["Time"].tolist()
    return rebaixados, tab_final

rebaixados, tab_final = get_rebaixados(ano, max_rodada, n_reb)

st.markdown("### Times Rebaixados")
cols = st.columns(n_reb)
for i, time in enumerate(rebaixados):
    with cols[i]:
        stats = tab_final[tab_final["Time"] == time].iloc[0]
        st.markdown(f"""
        <div style='background:#1a0610;border:1px solid #7f1d1d;border-radius:8px;
                    padding:0.9rem;text-align:center'>
          <div style='font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#7f1d1d'>
            Rebaixado
          </div>
          <div style='font-size:1.3rem;font-weight:800;font-family:"Barlow Condensed",sans-serif;
                      color:#fca5a5;margin:4px 0'>{time}</div>
          <div style='font-size:0.75rem;color:#6b1515'>
            {stats['Pts']} pts · {stats['Aprov%']}% aprov.<br>
            {stats['GP']}GP / {stats['GC']}GC
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("")
st.markdown("### Evolução da Posição — Times Rebaixados")
st.caption(f"Posição na tabela ao longo das {max_rodada} rodadas.")

@st.cache_data
def get_posicoes(ano, max_rodada):
    rows = []
    for r in range(1, max_rodada + 1):
        tab = calcular_tabela(ano, r).reset_index()
        for _, linha in tab.iterrows():
            rows.append({
                "rodada": r,
                "time": linha["Time"],
                "pos": int(linha["Pos"]),
                "pts": int(linha["Pts"])
            })
    return pd.DataFrame(rows)

with st.spinner("Calculando evolução..."):
    df_pos = get_posicoes(ano, max_rodada)

df_rel = df_pos[df_pos["time"].isin(rebaixados)]

cores_rel = ["#ef4444", "#f97316", "#eab308", "#a855f7"]
limite_reb = total_times - n_reb + 0.5

fig = go.Figure()
for i, time in enumerate(rebaixados):
    sub = df_rel[df_rel["time"] == time]
    fig.add_trace(go.Scatter(
        x=sub["rodada"], y=sub["pos"], mode="lines+markers",
        name=time, line=dict(color=cores_rel[i], width=2.5),
        marker=dict(size=4),
    ))

fig.add_hrect(y0=limite_reb, y1=total_times + 0.5, fillcolor="#ef4444", opacity=0.08)
fig.add_hline(y=limite_reb, line_dash="dash", line_color="#ef4444",
              annotation_text=f"Limite do rebaixamento ({int(limite_reb + 0.5)})",
              annotation_position="right")

fig.update_layout(
    template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=400, margin=dict(l=0, r=120, t=20, b=0),
    xaxis=dict(title="Rodada", showgrid=False, dtick=5),
    yaxis=dict(title="Posicao", autorange="reversed",
               tickvals=list(range(1, total_times + 1)), showgrid=True, gridcolor="#1a2332"),
    legend=dict(orientation="h", y=1.08),
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Pontuacao Final — Zona de Rebaixamento")
    tab_bottom = tab_final.tail(n_reb + 2).reset_index()
    pts_limite = tab_final.iloc[total_times - n_reb - 1]["Pts"]

    fig_pts = px.bar(
        tab_bottom, x="Time", y="Pts",
        color="Pts", color_continuous_scale=["#7f1d1d", "#ef4444", "#f97316"],
        text="Pts",
    )
    fig_pts.update_traces(textposition="outside")
    fig_pts.add_hline(y=pts_limite, line_dash="dot", line_color="#64748b",
                      annotation_text=f"Limite ({pts_limite} pts)")
    fig_pts.update_layout(
        template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        xaxis_showgrid=False,
        yaxis=dict(showgrid=True, gridcolor="#1a2332"),
    )
    st.plotly_chart(fig_pts, use_container_width=True)

with col2:
    st.markdown("### Aproveitamento nos Ultimos 10 Jogos")
    rows_ult = []
    for time in rebaixados:
        ult = query(f"""
            SELECT *,
                CASE WHEN (mandante='{time}' AND resultado='V. Mandante')
                          OR (visitante='{time}' AND resultado='V. Visitante') THEN 3
                     WHEN resultado='Empate' THEN 1
                     ELSE 0 END AS pts
            FROM jogos
            WHERE ano={ano} AND (mandante='{time}' OR visitante='{time}')
            ORDER BY rodada DESC LIMIT 10
        """)
        total_pts = ult["pts"].sum()
        aprov = total_pts / 30 * 100
        rows_ult.append({"time": time, "pts_ult10": total_pts, "aprov_ult10": aprov})

    df_ult = pd.DataFrame(rows_ult)
    fig_ult = px.bar(
        df_ult, x="time", y="aprov_ult10", color="time",
        color_discrete_sequence=cores_rel,
        text=df_ult["aprov_ult10"].apply(lambda x: f"{x:.0f}%"),
        labels={"aprov_ult10": "Aproveitamento (%)", "time": ""},
    )
    fig_ult.update_traces(textposition="outside")
    fig_ult.update_layout(
        template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
        height=300, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
        xaxis_showgrid=False,
        yaxis=dict(range=[0, 70], showgrid=True, gridcolor="#1a2332"),
    )
    st.plotly_chart(fig_ult, use_container_width=True)

with st.expander("Tabela completa (foco no Z4)"):
    st.dataframe(tab_final.tail(n_reb + 4), use_container_width=True)