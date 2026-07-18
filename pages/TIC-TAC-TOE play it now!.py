import streamlit as st
import datetime

st.title("YF tic tac toe in Quant dashboard!")

# 1. Initialize the game state if it doesn't exist yet
if "board" not in st.session_state:
    st.session_state.board = [""] * 9  # 9 blank spaces for the 3x3 grid
    st.session_state.turn = "X"        # X always goes first
    st.session_state.winner = None

# NEW HISTORY INITIALIZATION LAYER 📜
if "history" not in st.session_state:
    st.session_state.history = []

# Tracker flag to make sure each win is only logged once per round
if "logged_current_match" not in st.session_state:
    st.session_state.logged_current_match = False

# 2. Check if someone won the game
def check_winner():
    b = st.session_state.board
    # All 8 possible winning combinations (rows, columns, diagonals)
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontal rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Vertical columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for line in lines:
        if b[line[0]] == b[line[1]] == b[line[2]] != "":
            return b[line[0]]
    if "" not in b:
        return "Tie"
    return None

# 3. Handle what happens when a button is clicked
def play_turn(index):
    if st.session_state.board[index] == "" and not st.session_state.winner:
        st.session_state.board[index] = st.session_state.turn
        winner = check_winner()

        if winner:
            st.session_state.winner = winner
            # Trigger the logging mechanism immediately upon victory confirmation
            if not st.session_state.logged_current_match:
                timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
                if winner == "Tie":
                    log_text = f"🤝 Tie Game at {timestamp}"
                else:
                    log_text = f"🏆 Player {winner} Won at {timestamp}"
                st.session_state.history.insert(0, log_text)
                st.session_state.logged_current_match = True
        else:
            # Switch turns between X and O
            st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

# 4. Display status text or celebrate a win
if st.session_state.winner == "Tie":
    st.info("🤝 It's a tie game!")
elif st.session_state.winner:
    st.success(f"🎉 Player {st.session_state.winner} Wins!")
    st.balloons()
else:
    st.write(f"🎮 Player **{st.session_state.turn}**, it's your turn!")

# 5. Draw the 3x3 grid using Streamlit columns
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        idx = row * 3 + col
        button_label = st.session_state.board[idx] if st.session_state.board[idx] != "" else " "

        # Disable buttons if space is taken or game is over
        is_disabled = st.session_state.board[idx] != "" or st.session_state.winner is not None

        cols[col].button(
            label=button_label,
            key=f"btn_{idx}",
            on_click=play_turn,
            args=(idx,),
            use_container_width=True,
            disabled=is_disabled
        )

st.write("---")
if st.button("🔄 Reset Game"):
    st.session_state.board = [""] * 9
    st.session_state.turn = "X"
    st.session_state.winner = None
    st.session_state.logged_current_match = False  # Ready for the next match log!
    st.rerun()

# 📊 6. LIVE RENDER SECTOR FOR THE MATCH HISTORY DIARY
st.subheader("📜 YF Global Match History Logs")
if st.session_state.history:
    for entry in st.session_state.history:
        st.info(entry)
else:
    st.write("📡 The network archive is empty. Finish a match to write the first telemetry log line!")