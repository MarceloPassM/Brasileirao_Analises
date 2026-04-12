"""
add_2025.py
Converte o arquivo brasileirao-2025.json e anexa os dados ao jogos.csv existente.
"""
import json
import pandas as pd

ARQUIVO_JSON  = "data/brasileirao-2025.json"
ARQUIVO_CSV   = "data/jogos.csv"

print("Lendo JSON do Brasileirao 2025...")
with open(ARQUIVO_JSON, encoding="utf-8") as f:
    data = json.load(f)

# carregar CSV existente para pegar o ultimo jogo_id
df_atual = pd.read_csv(ARQUIVO_CSV)
proximo_id = df_atual["jogo_id"].max() + 1
print(f"jogos.csv atual: {len(df_atual)} jogos")
print(f"Proximo jogo_id: {proximo_id}")

# converter JSON para DataFrame
jogos = []
jogo_id = proximo_id

for rodada_str, lista in sorted(data.items(), key=lambda x: int(x[0])):
    rodada = int(rodada_str)
    for jogo in lista:
        mandante  = jogo["clubs"]["home"]
        visitante = jogo["clubs"]["away"]
        gm = int(jogo["goals"]["home"])
        gv = int(jogo["goals"]["away"])

        if gm > gv:
            resultado = "V. Mandante"
        elif gm < gv:
            resultado = "V. Visitante"
        else:
            resultado = "Empate"

        jogos.append({
            "jogo_id":        jogo_id,
            "ano":            2025,
            "rodada":         rodada,
            "mandante":       mandante,
            "visitante":      visitante,
            "gols_mandante":  gm,
            "gols_visitante": gv,
            "resultado":      resultado,
        })
        jogo_id += 1

df_2025 = pd.DataFrame(jogos)

print(f"\nJogos de 2025 convertidos: {len(df_2025)}")
print("Times encontrados:", sorted(df_2025["mandante"].unique()))

# verificar se 2025 ja existe no CSV
if 2025 in df_atual["ano"].values:
    print("\nAVISO: ano 2025 ja existe no jogos.csv. Removendo antes de adicionar...")
    df_atual = df_atual[df_atual["ano"] != 2025]


df_final = pd.concat([df_atual, df_2025], ignore_index=True)
df_final = df_final.sort_values(["ano", "rodada"]).reset_index(drop=True)
df_final.to_csv(ARQUIVO_CSV, index=False)

print(f"\nArquivo salvo: {ARQUIVO_CSV}")
print(f"Total de jogos exportados: {len(df_final)}")
print()
print("Jogos por ano:")
print(df_final.groupby("ano").size().rename("jogos").to_string())