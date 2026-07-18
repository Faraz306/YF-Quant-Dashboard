import streamlit as st

# Initialize the state variable
if 'meme' not in st.session_state:
    st.session_state.meme = False

st.set_page_config(layout="wide")

st.write(
    "Why do you loose 😭😭😭??? because there's something that says 'MORE MONEY $$$' when you've already hitted the TP 🤣🤣🤣")
st.write(
    "You make a script that places 10000 trades on 100000 symbols and your lot size is 1.0. you place them, and sleep. the next morning, you wake up and say: 'WHERE'S THE MONEY...' you get to know your pocket has a hole which has a paper. written on the paper 'Thanks for letting us cut a hole in your pocket.' you: 'WHAT??????'")
st.write(
    "You are buying. the market climbed. hitted TP, climbed even more, you place a Buy again... then the market fell soo much that it broke the world-record-low... you: 'WHY ME???' others: 'Me too...'. market news: 'BTC Values from 70K$ to 1M$.' you: 'NOT OUR MONEY 😭😭😭'")

st.write("---")

# Click triggers the state change
if st.button("Create your own joke on this app"):
    st.session_state.meme = True

# Display fields if state is active
if st.session_state.meme:
    name = st.text_input("Enter your name")
    joke = st.text_area("Write your joke")

    # Trigger submission only when user hits this button AND fields aren't empty
    if st.button("Publish Joke"):
        if name.strip() and joke.strip():

            # REMOVED: name.split(",") and joke.split(",") (Keep them as plain strings!)
            # FIX: Strip out line breaks and wrap the joke in double quotes so commas inside jokes don't break pandas
            clean_name = name.replace("\n", " ").strip()
            clean_joke = joke.replace("\n", " ").replace('"', '""').strip()

            with open("jokes.txt", "a", encoding="utf-8") as f:
                f.write(f'"{clean_name}","{clean_joke}"\n')

            st.success("Joke published successfully!")
        else:
            st.error("Please fill in both fields before publishing.")
