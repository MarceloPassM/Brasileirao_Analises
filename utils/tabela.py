import pandas as pd
from utils.db import query
from utils.penalidades import PENALIDADES


def calcular_tabela(ano: int, ate_rodada: int = 38) -> pd.DataFrame:
    sql = f"""
    WITH mandante AS (
        SELECT mandante AS time, ano, rodada,
            CASE resultado
                WHEN 'V. Mandante'  THEN 3
                WHEN 'Empate'       THEN 1
                ELSE 0 END AS pts,
            CASE resultado WHEN 'V. Mandante'  THEN 1 ELSE 0 END AS v,
            CASE resultado WHEN 'Empate'       THEN 1 ELSE 0 END AS e,
            CASE resultado WHEN 'V. Visitante' THEN 1 ELSE 0 END AS d,
            gols_mandante AS gp, gols_visitante AS gc
        FROM jogos
        WHERE ano = {ano} AND rodada <= {ate_rodada}
    ),
    visitante AS (
        SELECT visitante AS time, ano, rodada,
            CASE resultado
                WHEN 'V. Visitante' THEN 3
                WHEN 'Empate'       THEN 1
                ELSE 0 END AS pts,
            CASE resultado WHEN 'V. Visitante' THEN 1 ELSE 0 END AS v,
            CASE resultado WHEN 'Empate'       THEN 1 ELSE 0 END AS e,
            CASE resultado WHEN 'V. Mandante'  THEN 1 ELSE 0 END AS d,
            gols_visitante AS gp, gols_mandante AS gc
        FROM jogos
        WHERE ano = {ano} AND rodada <= {ate_rodada}
    ),
    combined AS (SELECT * FROM mandante UNION ALL SELECT * FROM visitante)
    SELECT
        time,
        COUNT(*)                AS j,
        SUM(v)                  AS v,
        SUM(e)                  AS e,
        SUM(d)                  AS d,
        SUM(gp)                 AS gp,
        SUM(gc)                 AS gc,
        SUM(gp) - SUM(gc)       AS sg,
        SUM(pts)                AS pts,
        ROUND(SUM(pts) * 100.0 / (COUNT(*) * 3), 1) AS aprov
    FROM combined
    GROUP BY time
    ORDER BY pts DESC, v DESC, sg DESC, gp DESC
    """
    df = query(sql).reset_index(drop=True)
    df.columns = ["Time","J","V","E","D","GP","GC","SG","Pts","Aprov%"]

    # Aplicar penalidades se houver para o ano
    if ano in PENALIDADES:
        max_rodada = int(query(f"SELECT MAX(rodada) FROM jogos WHERE ano={ano}").iloc[0, 0])
        if ate_rodada >= max_rodada:
            for time, ajuste in PENALIDADES[ano].items():
                mask = df["Time"] == time
                if mask.any():
                    df.loc[mask, "Pts"] = df.loc[mask, "Pts"] + ajuste

    # Reordenar apos penalidades
    df = df.sort_values(["Pts", "V", "SG", "GP"], ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "Pos"
    return df


def evolucao_pontos(ano: int, times: list) -> pd.DataFrame:
    rows = []
    n_rodadas = query(f"SELECT MAX(rodada) FROM jogos WHERE ano={ano}").iloc[0,0]
    for rodada in range(1, int(n_rodadas) + 1):
        tab = calcular_tabela(ano, rodada)
        for time in times:
            pts = tab.loc[tab["Time"] == time, "Pts"].values
            rows.append({
                "rodada": rodada,
                "time": time,
                "pts": int(pts[0]) if len(pts) else 0
            })
    return pd.DataFrame(rows)