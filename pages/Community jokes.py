import streamlit as st
import pandas as pd

df = pd.read_csv(
    "jokes.txt")

st.header("Jokes")

st.dataframe(df)