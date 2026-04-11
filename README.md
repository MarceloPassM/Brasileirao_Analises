# Brasileirao Analytics

Dashboard interativo para análise do Campeonato Brasileiro Série A (2003–2024), construído com Streamlit, DuckDB e Plotly.

---

## Funcionalidades

**Classificação** — Tabela completa por temporada com zonas dinâmicas por ano (Libertadores, Pré-Libertadores, Sul-Americana e Rebaixamento), aproveitamento e saldo de gols. Inclui ajustes de pontuação por penalidades disciplinares aplicadas ao longo da história do campeonato.

**Evolução na Tabela** — Acompanhe a pontuação acumulada e a posição na tabela de qualquer combinação de times ao longo das rodadas. Também exibe o aproveitamento separado por primeiro e segundo turno.

**Head-to-Head** — Histórico completo de confrontos diretos entre dois times, com distribuição de vitórias, gols marcados, placares mais frequentes, desempenho separado por mando de campo (casa e fora) e filtro por temporada.

**Análise de Gols** — Distribuição de gols por jogo, médias por temporada, vantagem de jogar em casa vs. fora, ranking de gols marcados e sofridos, e métricas como Over 2.5 e percentual de jogos em que ambos os times marcam.

**Zona de Rebaixamento** — Evolução da posição dos times rebaixados ao longo da temporada, pontuação final e aproveitamento nos últimos 10 jogos.

---

## Tecnologias

| Ferramenta | Uso |
|---|---|
| Python 3.11 | Linguagem principal |
| Streamlit | Interface do dashboard |
| DuckDB | Consultas SQL sobre os CSVs |
| Plotly | Gráficos interativos |
| Pandas | Manipulação de dados |

---

## Estrutura do Projeto

```
Brasileirao_Analises/
├── app.py                        # Página principal — Classificação
├── pipeline_data.py              # Converte CSV original para jogos.csv
├── requirements.txt
├── data/
│   ├── jogos.csv                 # Dataset ativo (2003–2024)
│   ├── campeonato-brasileiro-full.csv  # Fonte original
│   └── generate_data.py          # Gerador de dados sintéticos (legado)
├── pages/
│   ├── 1_Evolucao_na_Tabela.py
│   ├── 2_Head_to_Head.py
│   ├── 3_Analise_Gols.py
│   └── 4_Zona_Rebaixamento.py
└── utils/
    ├── db.py                     # Conexão DuckDB com cache
    ├── tabela.py                 # Cálculo da classificação
    └── penalidades.py            # Ajustes disciplinares por ano
```

---

## Como Rodar Localmente

**Pré-requisitos:** Python 3.11+

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/Brasileirao_Analises.git
cd Brasileirao_Analises

# Instale as dependências
pip install -r requirements.txt

# Gere o dataset (necessário na primeira vez)
python pipeline_data.py

# Inicie o dashboard
streamlit run app.py
```

---

## Dados

- **Fonte:** [adaoduque/Brasileirao_Dataset](https://github.com/adaoduque/Brasileirao_Dataset)
- **Cobertura:** 2003 a 2024 — 8.785 jogos
- **Correção aplicada:** os jogos das rodadas 28 a 38 do Brasileirão 2020, disputados em janeiro e fevereiro de 2021 por conta da pandemia, foram reclassificados para o ano correto (2020)

---

## Penalidades Históricas

Alguns times tiveram pontos adicionados ou subtraídos por decisões disciplinares fora de campo. Esses ajustes são aplicados apenas na tabela final de cada temporada:

| Ano | Time | Ajuste |
|---|---|---|
| 2003 | São Caetano | +3 |
| 2003 | Internacional | +2 |
| 2003 | Juventude | +3 |
| 2003 | Fluminense | +2 |
| 2003 | Corinthians | +2 |
| 2003 | Ponte Preta | −1 |
| 2003 | Paysandu | −8 |
| 2004 | São Caetano | −24 |
| 2010 | Grêmio Prudente | −3 |
| 2013 | Flamengo | −4 |
| 2013 | Portuguesa | −4 |
| 2016 | Santa Cruz | −3 |
| 2018 | Sport | −3 |

---

## Autor

Desenvolvido por **Marcelo Passamai Marques**
[LinkedIn](https://www.linkedin.com/in/marcelo-passamai-marques/)