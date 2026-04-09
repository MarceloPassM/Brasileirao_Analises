import duckdb
import pandas as pd
from pathlib import Path
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"

@st.cache_resource(show_spinner=False)
def get_connection():
    con = duckdb.connect(":memory:")
    df = pd.read_csv(DATA_DIR / "jogos.csv")
    con.register("jogos", df)
    return con

def query(sql: str) -> pd.DataFrame:
    return get_connection().execute(sql).df()