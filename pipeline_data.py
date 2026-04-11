"""
pipeline_data.py
Converte o campeonato-brasileiro-full.csv para o formato jogos.csv usado no projeto.
Execute na raiz do projeto:
    python pipeline_data.py
"""
import pandas as pd

ARQUIVO_ORIGINAL = "data/campeonato-brasileiro-full.csv"
ARQUIVO_SAIDA    = "data/jogos.csv"

print("Lendo arquivo original...")
df = pd.read_csv(ARQUIVO_ORIGINAL)
print(f"Total de jogos lidos: {len(df)}")

# Converter data para datetime
df["data_dt"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
df["ano"] = df["data_dt"].dt.year

# Correcao: jogos com data em 2021 mas anteriores a maio de 2021
# sao continuacao do campeonato 2020 (rodadas 28-38 disputadas em jan/fev 2021)
mascara_2020 = (df["ano"] == 2021) & (df["data_dt"] < "2021-05-01")
df.loc[mascara_2020, "ano"] = 2020

print(f"Jogos corrigidos de 2021 para 2020: {mascara_2020.sum()}")

# Renomear colunas
df = df.rename(columns={
    "ID":               "jogo_id",
    "rodata":           "rodada",
    "mandante_Placar":  "gols_mandante",
    "visitante_Placar": "gols_visitante",
})

# Converter placares para inteiro
df["gols_mandante"]  = pd.to_numeric(df["gols_mandante"],  errors="coerce").fillna(0).astype(int)
df["gols_visitante"] = pd.to_numeric(df["gols_visitante"], errors="coerce").fillna(0).astype(int)

# Criar coluna resultado
def definir_resultado(row):
    if row["gols_mandante"] > row["gols_visitante"]:
        return "V. Mandante"
    elif row["gols_mandante"] < row["gols_visitante"]:
        return "V. Visitante"
    else:
        return "Empate"

df["resultado"] = df.apply(definir_resultado, axis=1)

# Selecionar colunas finais
df_final = df[["jogo_id", "ano", "rodada", "mandante", "visitante",
               "gols_mandante", "gols_visitante", "resultado"]].copy()

df_final = df_final.sort_values(["ano", "rodada"]).reset_index(drop=True)

df_final.to_csv(ARQUIVO_SAIDA, index=False)

print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")
print(f"Total de jogos exportados: {len(df_final)}")
print()
print("Jogos por ano:")
print(df_final.groupby("ano").size().rename("jogos").to_string())