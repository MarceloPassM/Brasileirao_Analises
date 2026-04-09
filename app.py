import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.tabela import calcular_tabela
from utils.db import query

st.set_page_config(
    page_title="Brasileirao Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0a0f14;
    color: #e2e8f0;
}
h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.03em; }
.block-container { padding-top: 1.2rem; }

[data-testid="stSidebar"] {
    background: #060b0f !important;
    border-right: 2px solid #1a2332;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }

.kpi {
    background: linear-gradient(135deg, #0d1b2a, #132336);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.kpi .label { font-size:0.65rem; font-weight:600; letter-spacing:0.15em;
               text-transform:uppercase; color:#4a7fa5; margin-bottom:4px; }
.kpi .value { font-size:2rem; font-weight:800; font-family:'Barlow Condensed',sans-serif;
               color:#e2f0ff; line-height:1; }
.kpi .sub   { font-size:0.72rem; color:#4a6580; margin-top:4px; }

.section { font-size:0.68rem; font-weight:700; letter-spacing:0.18em;
           text-transform:uppercase; color:#2a4a6a;
           border-top:1px solid #1a2332; padding-top:0.6rem; margin-top:0.4rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Brasileirao\n### Analytics")
    st.markdown("---")
    anos_disp = [2021, 2022, 2023, 2024]
    ano = st.selectbox("Temporada", anos_disp, index=3)

    max_rodada = int(query(f"SELECT MAX(rodada) FROM jogos WHERE ano={ano}").iloc[0,0])
    rodada = st.slider("Ate a rodada:", 1, max_rodada, max_rodada)

    st.markdown("---")
    st.markdown("""
**Paginas**
- Classificacao *(voce esta aqui)*
- Evolucao na Tabela
- Head-to-Head
- Analise de Gols
- Zona de Rebaixamento
    """)
    st.markdown("---")
    st.caption("Dados simulados · Serie A 2021-2025")


@st.cache_data
def get_tabela(ano, rodada):
    return calcular_tabela(ano, rodada)

tabela = get_tabela(ano, rodada)

st.markdown(f"# Classificacao — Brasileirao {ano}")
st.caption(f"Rodada {rodada} de {max_rodada}" + (""))

lider    = tabela.iloc[0]
mais_gol = tabela.loc[tabela["GP"].idxmax()]
melhor_a = tabela.loc[tabela["Aprov%"].idxmax()]
menos_gc = tabela.loc[tabela["GC"].idxmin()]

c1, c2, c3, c4 = st.columns(4)
for col, label, val, sub in zip(
    [c1, c2, c3, c4],
    ["Lider", "Mais Gols Marcados", "Melhor Aproveitamento", "Menos Gols Sofridos"],
    [lider["Time"], mais_gol["Time"], melhor_a["Time"], menos_gc["Time"]],
    [f"{lider['Pts']} pts", f"{mais_gol['GP']} gols", f"{melhor_a['Aprov%']}%", f"{menos_gc['GC']} gols"],
):
    with col:
        st.markdown(f"""
        <div class="kpi">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("")

st.markdown('<div class="section">Tabela de Classificacao</div>', unsafe_allow_html=True)
st.markdown("")

def colorir_posicao(pos):
    if pos <= 4:  return "G4"
    if pos <= 6:  return "SUL"
    if pos >= 17: return "REL"
    return "-"

tabela_display = tabela.copy()
tabela_display.insert(0, "Zona", [colorir_posicao(i) for i in range(1, len(tabela) + 1)])

st.dataframe(
    tabela_display,
    use_container_width=True,
    height=int(len(tabela) * 35 + 45),
    column_config={
        "Zona": st.column_config.TextColumn("Zona", width="small"),
        "Aprov%": st.column_config.ProgressColumn("Aprov%", min_value=0, max_value=100, format="%.1f%%"),
        "Pts": st.column_config.NumberColumn("Pts", format="%d"),
    }
)

st.markdown("""
<div style='font-size:0.72rem; color:#2a4a6a; margin-top:4px'>
G4 = Libertadores &nbsp;|&nbsp; SUL = Sul-Americana &nbsp;|&nbsp; REL = Rebaixamento &nbsp;|&nbsp; - = Zona neutra
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="section">Aproveitamento dos Times</div>', unsafe_allow_html=True)

cores = ["#22c55e"]*4 + ["#3b82f6"]*2 + ["#64748b"]*10 + ["#ef4444"]*4
fig = go.Figure(go.Bar(
    x=tabela["Time"], y=tabela["Aprov%"],
    marker_color=cores,
    text=tabela["Aprov%"].apply(lambda x: f"{x:.0f}%"),
    textposition="outside",
))
fig.add_hline(y=50, line_dash="dot", line_color="#475569", annotation_text="50%")
fig.update_layout(
    template="plotly_dark", plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=320, margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=10)),
    yaxis=dict(range=[0, 105], showgrid=True, gridcolor="#1a2332"),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section">Gols Marcados vs Sofridos</div>', unsafe_allow_html=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(name="Gols Marcados", x=tabela["Time"], y=tabela["GP"],
                      marker_color="#3b82f6", opacity=0.85))
fig2.add_trace(go.Bar(name="Gols Sofridos", x=tabela["Time"], y=tabela["GC"],
                      marker_color="#ef4444", opacity=0.75))
fig2.update_layout(
    barmode="group", template="plotly_dark",
    plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    height=300, margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#1a2332"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig2, use_container_width=True)