import pandas as pd
import numpy as np
from itertools import combinations

np.random.seed(42)

TIMES_POR_ANO = {
    2021: ["Atlético-MG","Flamengo","Fortaleza","Fluminense","Corinthians",
           "RB Bragantino","Palmeiras","América-MG","Athletico-PR","Santos",
           "Internacional","Cuiabá","São Paulo","Ceará","Juventude",
           "Grêmio","Sport","Bahia","Botafogo","Chapecoense"],
    2022: ["Palmeiras","Internacional","Fluminense","Flamengo","Corinthians",
           "Athletico-PR","Botafogo","RB Bragantino","América-MG","São Paulo",
           "Santos","Atlético-MG","Ceará","Fortaleza","Coritiba",
           "Goiás","Avaí","Cuiabá","Juventude","Atlético-GO"],
    2023: ["Botafogo","Palmeiras","Grêmio","Atlético-MG","Flamengo",
           "Red Bull Bragantino","São Paulo","Fluminense","Internacional","Corinthians",
           "Athletico-PR","Fortaleza","Cuiabá","Santos","América-MG",
           "Goiás","Cruzeiro","Vasco","Bahia","Coritiba"],
    2024: ["Botafogo","Palmeiras","Flamengo","Fortaleza","Internacional",
           "São Paulo","Cruzeiro","Vasco","Fluminense","Atlético-MG",
           "Athletico-PR","Corinthians","Bahia","RB Bragantino","Grêmio",
           "Juventude","Cuiabá","Criciúma","Atlético-GO","Vitória"],
    2025: ["Flamengo","Palmeiras","Botafogo","São Paulo","Fluminense",
           "Corinthians","Internacional","Atlético-MG","Fortaleza","Grêmio",
           "Athletico-PR","Cruzeiro","Bahia","RB Bragantino","Vasco",
           "Sport","Ceará","Mirassol","Juventude","Santos"],
}

FORCA = {
    2021: {"Atlético-MG":9.5,"Flamengo":9.0,"Palmeiras":8.5,"Fortaleza":7.5,"Fluminense":7.0,"Corinthians":6.5,"RB Bragantino":6.5,"Athletico-PR":6.5,"América-MG":6.0,"Santos":5.5,"Internacional":6.0,"Cuiabá":4.5,"São Paulo":6.0,"Ceará":5.5,"Juventude":4.5,"Grêmio":5.0,"Sport":4.0,"Bahia":4.0,"Botafogo":4.5,"Chapecoense":3.0},
    2022: {"Palmeiras":9.5,"Internacional":7.5,"Fluminense":7.0,"Flamengo":8.5,"Corinthians":7.0,"Athletico-PR":7.0,"Botafogo":6.0,"RB Bragantino":6.5,"América-MG":5.5,"São Paulo":6.0,"Santos":5.5,"Atlético-MG":7.5,"Ceará":5.0,"Fortaleza":6.5,"Coritiba":4.0,"Goiás":4.5,"Avaí":3.5,"Cuiabá":4.5,"Juventude":4.0,"Atlético-GO":4.5},
    2023: {"Botafogo":8.5,"Palmeiras":9.5,"Grêmio":7.0,"Atlético-MG":7.5,"Flamengo":8.0,"Red Bull Bragantino":6.5,"São Paulo":7.0,"Fluminense":8.0,"Internacional":6.5,"Corinthians":6.0,"Athletico-PR":6.0,"Fortaleza":6.5,"Cuiabá":4.5,"Santos":4.5,"América-MG":4.0,"Goiás":3.5,"Cruzeiro":5.0,"Vasco":5.0,"Bahia":5.5,"Coritiba":3.5},
    2024: {"Botafogo":9.5,"Palmeiras":9.0,"Flamengo":8.5,"Fortaleza":8.0,"Internacional":7.0,"São Paulo":6.5,"Cruzeiro":6.0,"Vasco":5.5,"Fluminense":6.0,"Atlético-MG":7.5,"Athletico-PR":5.5,"Corinthians":5.5,"Bahia":6.0,"RB Bragantino":6.0,"Grêmio":5.0,"Juventude":4.5,"Cuiabá":4.0,"Criciúma":4.0,"Atlético-GO":4.5,"Vitória":4.0},
    2025: {"Flamengo":9.0,"Palmeiras":9.0,"Botafogo":8.0,"São Paulo":7.5,"Fluminense":7.0,"Corinthians":6.5,"Internacional":7.0,"Atlético-MG":7.5,"Fortaleza":7.5,"Grêmio":6.5,"Athletico-PR":6.0,"Cruzeiro":6.5,"Bahia":6.0,"RB Bragantino":6.0,"Vasco":5.5,"Sport":4.5,"Ceará":5.0,"Mirassol":4.0,"Juventude":4.5,"Santos":5.5},
}

def simular(casa, fora, ano):
    fc = FORCA[ano].get(casa, 5.0) + 0.8
    ff = FORCA[ano].get(fora, 5.0)
    gc = int(np.random.poisson(fc * 0.22))
    gf = int(np.random.poisson(ff * 0.18))
    return gc, gf

jogos = []
jid = 1

for ano in range(2021, 2026):
    times = TIMES_POR_ANO[ano]
    rodada_max = 38 if ano < 2025 else 12

    pares_ida   = list(combinations(range(len(times)), 2))
    pares_volta = [(b, a) for a, b in pares_ida]

    np.random.shuffle(pares_ida)
    np.random.shuffle(pares_volta)

    for rodada in range(1, 39):
        if rodada > rodada_max:
            break
        if rodada <= 19:
            bloco = pares_ida[(rodada-1)*10 : rodada*10]
        else:
            bloco = pares_volta[(rodada-19-1)*10 : (rodada-19)*10]

        for i, j in bloco:
            casa  = times[i]
            fora  = times[j]
            gc, gf = simular(casa, fora, ano)
            res = "V. Mandante" if gc > gf else ("V. Visitante" if gc < gf else "Empate")
            jogos.append({
                "jogo_id": jid, "ano": ano, "rodada": rodada,
                "mandante": casa, "visitante": fora,
                "gols_mandante": gc, "gols_visitante": gf,
                "resultado": res
            })
            jid += 1

df = pd.DataFrame(jogos)
df.to_csv("data/jogos.csv", index=False)
print(f"Jogos gerados: {len(df)}")
print(df.groupby("ano").size().rename("jogos"))