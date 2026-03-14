import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
from groq import Groq
from database import create_database, get_schema, run_query, DB_PATH

# Page config
st.set_page_config(
    page_title="QueryMind - AI SQL Analyst",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #c8d6e5;
}
.stApp { background-color: #080c14; }

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.hero-sub {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2rem;
}
.user-bubble {
    background: linear-gradient(135deg, #1e3a5f, #1a2744);
    border: 1px solid #38bdf830;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 8px 0;
    margin-left: 20%;
    color: #e2e8f0;
}
.bot-bubble {
    background: linear-gradient(135deg, #0f172a, #131c2e);
    border: 1px solid #818cf830;
    border-radius: 16px 16px 16px 4px;
    padding: 14px 18px;
    margin: 8px 0;
    margin-right: 10%;
    color: #c8d6e5;
}
.sql-block {
    background: #0d1117;
    border: 1px solid #30363d;
    border-left: 3px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #79c0ff;
    margin: 10px 0;
    overflow-x: auto;
    white-space: pre-wrap;
}
.insight-box {
    background: linear-gradient(135deg, #0f2027, #0a1628);
    border: 1px solid #f472b630;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 8px;
    color: #f1f5f9;
    font-size: 0.95rem;
    line-height: 1.6;
}
.metric-pill {
    display: inline-block;
    background: #1e3a5f;
    border: 1px solid #38bdf840;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #38bdf8;
    margin: 3px;
}
.example-chip {
    display: inline-block;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #94a3b8;
    margin: 4px;
}
.sidebar-section {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 14px;
}
.stTextInput > div > div > input {
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
    color: #080c14 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
}
div[data-testid="stSidebar"] {
    background-color: #0a0e1a !important;
    border-right: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

# Init DB
if not os.path.exists(DB_PATH):
    with st.spinner("Setting up database for the first time..."):
        create_database()

# Sidebar
with st.sidebar:
    st.markdown("### QueryMind")
    st.divider()

    st.markdown("**Groq API Key**")
    api_key = st.text_input(
        "Paste your key here",
        type="password",
        placeholder="gsk_...",
        help="Get free key at console.groq.com"
    )

    st.divider()
    st.markdown("**Dataset Overview**")
    st.markdown("""
    <div class='sidebar-section'>
    <b>500</b> customers<br>
    <b>20</b> products<br>
    <b>~2000</b> orders<br>
    <b>10</b> Indian cities<br>
    Last 365 days
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("**Tables**")
    for t in ["customers", "products", "orders", "order_items"]:
        st.markdown(f"- `{t}`")

    st.divider()
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main header
st.markdown("<div class='hero-title'>QueryMind</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='hero-sub'>Ask business questions in plain English. Get SQL, results, and insights instantly.</div>",
    unsafe_allow_html=True
)

# Example questions
st.markdown("**Try asking:**")
examples = [
    "Which city has the highest revenue?",
    "Top 5 best-selling products this month",
    "What % of orders were cancelled?",
    "Average order value by loyalty tier",
    "Which brand has the best ratings?",
    "Revenue trend over last 6 months"
]
cols = st.columns(3)
for i, ex in enumerate(examples):
    with cols[i % 3]:
        st.markdown(f"<div class='example-chip'>{ex}</div>", unsafe_allow_html=True)

st.divider()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []


def extract_sql(text: str) -> str:
    """Extract SQL query from LLM response text."""
    patterns = [
        r"```sql\s*(.*?)\s*```",
        r"```\s*(SELECT.*?)\s*```",
        r"(SELECT\s+.*?;)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    if "SELECT" in text.upper():
        start = text.upper().find("SELECT")
        return text[start:].split(";")[0].strip() + ";"
    return ""


def call_llm(client: Groq, system_prompt: str, user_prompt: str) -> str:
    """Make a single call to Groq LLM and return the response text."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()


def ask_groq(question: str, api_key: str) -> dict:
    """Convert a plain English question to SQL, run it, and return insight."""
    client = Groq(api_key=api_key)
    schema = get_schema()

    # Step 1: Generate SQL
    sql_system = """You are an expert SQL analyst. Convert natural language questions to SQLite queries.
Always return the SQL query inside a ```sql ``` code block.
Use proper JOINs, aliases, and limit results to 20 rows unless asked otherwise.
Only return the SQL block, nothing else."""

    sql_user = f"""Database schema:
{schema}

Question: {question}

Write the SQLite query:"""

    sql_text = call_llm(client, sql_system, sql_user)
    sql_query = extract_sql(sql_text)

    if not sql_query:
        return {"error": "Could not generate SQL. Please try rephrasing your question."}

    # Step 2: Run the query
    df, error = run_query(sql_query)

    if error:
        fix_system = "You are an expert SQL debugger. Fix the broken SQLite query and return only the corrected SQL in a ```sql ``` block."
        fix_user = f"Error: {error}\n\nBroken query:\n{sql_query}\n\nSchema:\n{schema}\n\nFixed query:"
        fixed_text = call_llm(client, fix_system, fix_user)
        sql_query = extract_sql(fixed_text)
        df, error = run_query(sql_query)
        if error:
            return {"sql": sql_query, "error": f"Query failed: {error}"}

    # Step 3: Generate business insight
    if df is not None and not df.empty:
        insight_system = "You are a sharp business analyst. Give concise 2-3 sentence data-driven insights. Mention specific numbers. No filler."
        insight_user = f"Question: {question}\nResults (first 5 rows):\n{df.head().to_string()}\nTotal rows: {len(df)}\n\nInsight:"
        insight = call_llm(client, insight_system, insight_user)
    else:
        insight = "No data returned for this query."

    return {
        "sql": sql_query,
        "df": df,
        "insight": insight,
        "rows": len(df) if df is not None else 0
    }


def auto_chart(df: pd.DataFrame):
    """Automatically generate the most appropriate chart for the data."""
    if df is None or df.empty or len(df.columns) < 2:
        return None

    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(include='object').columns.tolist()

    if not numeric_cols:
        return None

    colors = ["#38bdf8", "#818cf8", "#f472b6", "#34d399", "#fb923c"]

    try:
        date_cols = [c for c in cols if "date" in c.lower() or "month" in c.lower()]
        if date_cols:
            fig = px.line(df, x=date_cols[0], y=numeric_cols[0],
                          title=f"{numeric_cols[0]} over time",
                          color_discrete_sequence=colors)
            fig.update_layout(paper_bgcolor="#080c14", plot_bgcolor="#0f172a",
                              font=dict(color="#c8d6e5"), title_font_color="#38bdf8")
            return fig

        if text_cols and numeric_cols and len(df) <= 20:
            fig = px.bar(df, x=text_cols[0], y=numeric_cols[0],
                         title=f"{numeric_cols[0]} by {text_cols[0]}",
                         color=numeric_cols[0],
                         color_continuous_scale=["#1e3a5f", "#38bdf8", "#818cf8"])
            fig.update_layout(paper_bgcolor="#080c14", plot_bgcolor="#0f172a",
                              font=dict(color="#c8d6e5"), title_font_color="#38bdf8",
                              showlegend=False)
            return fig

        if text_cols and numeric_cols and len(df) <= 8:
            fig = px.pie(df, names=text_cols[0], values=numeric_cols[0],
                         title=f"{numeric_cols[0]} breakdown",
                         color_discrete_sequence=colors)
            fig.update_layout(paper_bgcolor="#080c14", plot_bgcolor="#0f172a",
                              font=dict(color="#c8d6e5"), title_font_color="#38bdf8")
            return fig

    except Exception:
        pass

    return None


# Chat display
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        data = msg["content"]
        st.markdown("<div class='bot-bubble'>", unsafe_allow_html=True)

        if "error" in data and "sql" not in data:
            st.error(data["error"])
        else:
            if "sql" in data:
                st.markdown(
                    f"<div class='sql-block'>-- Generated SQL\n{data['sql']}</div>",
                    unsafe_allow_html=True
                )
            if "error" in data:
                st.error(data["error"])
            elif "df" in data and data["df"] is not None and not data["df"].empty:
                st.markdown(
                    f"<span class='metric-pill'>{data['rows']} rows returned</span>",
                    unsafe_allow_html=True
                )
                st.dataframe(data["df"], use_container_width=True, height=200)
                chart = auto_chart(data["df"])
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

            if "insight" in data:
                st.markdown(
                    f"<div class='insight-box'><b>Insight:</b> {data['insight']}</div>",
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

# Input
st.divider()
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "question",
        placeholder="e.g. Which city generates the most revenue?",
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    send = st.button("Ask", use_container_width=True)

if send and user_input:
    if not api_key:
        st.error("Please add your Groq API key in the sidebar. Get it free at console.groq.com")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            result = ask_groq(user_input, api_key)
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()
