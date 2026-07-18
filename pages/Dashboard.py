import streamlit as st
import pandas as pd


st.write("YF quant Dashboard")

tab1, tab2 = st.tabs(["Trades", "Jokes"])
with tab1:
    st.write("Trade history:")
    name = st.text_input("Enter your name. if no trades were executed under your name, it won't appear")
    df = pd.read_csv("FILE.txt")
    if name:
        joke_series = df.loc[df[" name"] == name, ["trades", " win_rate", " pnl", " strat"]]
        st.dataframe(joke_series)
with tab2:
    st.write("Memes of yours")
    name = st.text_input("Enter your name again so we can tell your jokes.")
    data = pd.read_csv("jokes.txt")
    if name:
        # 1. Find the row matching the strategy name and pull the 'Jokes' column
        joke_series = data.loc[data["Name"] == name, " Joke"]

        # 2. Check if a match was found, then print the first result
        if not joke_series.empty:
            st.write(joke_series.iloc[0])
        else:
            st.warning("No joke found under your name. either you have not created one or enter your name correctly.")
