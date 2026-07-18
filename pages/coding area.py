import streamlit as st
import pandas as pd
import io, contextlib, ast, subprocess
import requests

# 💻 Desktop layout mode configuration
st.set_page_config(layout="wide", page_title="YF Mini IDE")
st.title("💻 YF Mini IDE + Terminal + File Upload + Gemini Chat")

# Global DataFrame state initialization
if "df" not in st.session_state:
    st.session_state.df = None

# Enter Gemini API key
api_key = st.text_input("🔑 Enter your Gemini API key:", type="password")

# 📂 SECTION 1: FILE UPLOADER
uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx", "txt", "pdf"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv") or uploaded_file.name.endswith(".txt"):
            st.session_state.df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            # Ensure pdfplumber is installed: pip install pdfplumber
            import pdfplumber

            with pdfplumber.open(uploaded_file) as pdf:
                first_page = pdf.pages[0]
                table = first_page.extract_table()
                if table:
                    st.session_state.df = pd.DataFrame(table[1:], columns=table[0])
        else:
            st.session_state.df = pd.read_excel(uploaded_file)
        st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
        st.dataframe(st.session_state.df.head())
    except Exception as e:
        st.error(f"💥 Error loading file: {e}")

# 📝 SECTION 2: CODE EDITOR (LOCKED IN A FORM TO PREVENT TYPING LAG)
st.subheader("📝 PyCharm-Style Blank Sandbox")

# Initialize raw_code in session_state if not present to avoid errors on first load
if "raw_code" not in st.session_state:
    st.session_state.raw_code = (
        "# Manual Sandbox Mode\n"
        "import pandas as pd\n"
        "\n"
        "# Access your uploaded file using 'df'\n"
        "if df is not None:\n"
        "    print(df.head())\n"
    )

with st.form("editor_form"):
    from streamlit_monaco import st_monaco

    # Render a truly blank slate. The user is responsible for all imports!
    raw_code = st_monaco(
        value=st.session_state.raw_code,
        language="python",
        theme="vs-dark",
        height="350px"
    )

    # Update session state on change to keep it fresh
    st.session_state.raw_code = raw_code

    submit_button = st.form_submit_button("🚀 Run Pipeline Code")

# Execute block triggers safely on submission event
if submit_button and raw_code:
    # 🛡️ Run Code Diagnostics (Abstract Syntax Tree Parser)
    syntax_error = None
    try:
        ast.parse(raw_code)
    except SyntaxError as se:
        syntax_error = f"🔴 **Syntax Error on Line {se.lineno}:** {se.msg} \n👉 Near: `{se.text.strip() if se.text else ''}`"

    if syntax_error:
        st.error(syntax_error)
    else:
        st.caption("✨ Code Inspections clean. Executing...")
        output_panel = io.StringIO()
        try:
            with contextlib.redirect_stdout(output_panel):
                # We do NOT pre-inject scikit-learn models or numpy anymore.
                # We ONLY provide access to the uploaded dataframe context reference.
                exec_context = {
                    "df": st.session_state.df
                }
                exec(raw_code, exec_context)
            st.success("✅ Execution complete!")
        except Exception as runtime_err:
            st.error(f"💥 Runtime Exception: {runtime_err}")

        # Draw the terminal console frame
        st.text_area("🖥️ Output Terminal Console", value=output_panel.getvalue(), height=150)

# 🤖 SECTION 3: GEMINI CHAT PANEL
st.subheader("🤖 Gemini Chat")
user_query = st.text_input("Ask Gemini anything about your code or data:")

if st.button("Send to Gemini"):
    if not api_key:
        st.error("❌ Please enter your Gemini API key above.")
    elif not user_query.strip():
        st.warning("⚠️ Please enter a question or prompt.")
    elif not raw_code:
        st.warning("⚠️ No code found in the editor to send with the query.")
    else:
        try:
            # ✅ FIXED: Updated model name to gemini-1.5-flash and API path to v1beta
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": api_key}
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"User query: {user_query}\n\nCode:\n{raw_code}"
                    }]
                }]
            }
            response = requests.post(url, headers=headers, params=params, json=payload)

            if response.status_code == 200:
                gemini_reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success(f"Gemini says:\n\n{gemini_reply}")
            else:
                st.error(f"💥 Gemini API error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"💥 Error calling Gemini API: {e}")

# 🖥️ SECTION 4: SHELL TERMINAL PANEL
st.subheader("🖥️ Terminal")
command = st.text_input("Enter shell command:")
if st.button("Run Command"):
    try:
        # ⚠️ Warning: Running arbitrary shell commands can be dangerous in a shared environment
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.stdout:
            st.text(result.stdout)
        if result.stderr:
            st.error(result.stderr)
    except subprocess.TimeoutExpired:
        st.error("⏱️ Command timed out.")
    except Exception as e:
        st.error(f"💥 Error: {e}")