"""
utils/penalidades.py
Ajustes de pontos por decisoes disciplinares fora de campo.
Valores positivos = ganho de pontos, negativos = perda de pontos.
"""

PENALIDADES = {
    2003: {
        "Sao Caetano":  +3,
        "Internacional": +2,
        "Juventude":     +3,
        "Fluminense":    +2,
        "Ponte Preta":   -1,
        "Paysandu":      -8,
        "Corinthians":   +2,
    },
    2004: {
        "Sao Caetano": -24,
    },
    2010: {
        "Gremio Prudente": -3,
    },
    2013: {
        "Flamengo":    -4,
        "Portuguesa":  -4,
    },
    2016: {
        "Santa Cruz": -3,
    },
    2018: {
        "Sport": -3,
    },
}