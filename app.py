import streamlit as st
from predict import predict_code_quality
from extract import extract
import tempfile
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import datetime

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="AI Code Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Code Intelligence Platform")
st.write("Analyze and compare Python code using AI-powered quality prediction.")
st.divider()

# -----------------------------------
# DATABASE SETUP
# -----------------------------------
def init_db():
    conn = sqlite3.connect("analysis_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            score INTEGER,
            grade TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


def save_analysis(mode, score, grade):
    conn = sqlite3.connect("analysis_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (timestamp, mode, score, grade)
        VALUES (?, ?, ?, ?)
    """, (str(datetime.datetime.now()), mode, score, grade))
    conn.commit()
    conn.close()


# -----------------------------------
# Sidebar Controls
# -----------------------------------
st.sidebar.header("⚙ Configuration")

analysis_mode = st.sidebar.selectbox(
    "Select Mode",
    ["Single Code Analysis", "Code Comparison"]
)

if st.sidebar.button("📜 View Analysis History"):
    conn = sqlite3.connect("analysis_history.db")
    df = pd.read_sql_query("SELECT * FROM history", conn)
    conn.close()
    st.subheader("📜 Analysis History")
    st.dataframe(df)


# -----------------------------------
# Utility Functions
# -----------------------------------
def get_score_and_grade(label):
    if label.lower() == "good":
        return 85, "A"
    elif label.lower() == "average":
        return 65, "B"
    else:
        return 40, "C"


def generate_suggestions(label, metrics):
    suggestions = []
    if label.lower() in ["average", "bad"]:
        if metrics.get("cyclomatic_complexity", 0) > 5:
            suggestions.append("⚠ Reduce cyclomatic complexity.")
        if metrics.get("num_comments", 0) == 0:
            suggestions.append("⚠ Add comments.")
        if metrics.get("has_docstring", 0) == 0:
            suggestions.append("⚠ Add docstrings.")
        if metrics.get("num_functions", 0) <= 1:
            suggestions.append("⚠ Break into reusable functions.")
    else:
        suggestions.append("✔ Code structure looks good.")
    return suggestions


def radar_chart(metrics1, metrics2):
    selected_keys = [
        "cyclomatic_complexity",
        "num_functions",
        "num_comments",
        "num_imports",
        "nesting_depth",
        "avg_line_length"
    ]

    values1 = [metrics1.get(k, 0) for k in selected_keys]
    values2 = [metrics2.get(k, 0) for k in selected_keys]

    angles = np.linspace(0, 2 * np.pi, len(selected_keys), endpoint=False).tolist()
    values1 += values1[:1]
    values2 += values2[:1]
    angles += angles[:1]

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, values1)
    ax.fill(angles, values1, alpha=0.25)

    ax.plot(angles, values2)
    ax.fill(angles, values2, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([k.replace("_", "\n") for k in selected_keys])

    st.pyplot(fig)


# -----------------------------------
# SINGLE CODE ANALYSIS
# -----------------------------------
if analysis_mode == "Single Code Analysis":

    st.subheader("📄 Single Code Analysis")

    input_mode = st.radio("Input Method", ["Paste Code", "Upload .py File"])

    if input_mode == "Paste Code":
        code_input = st.text_area("Paste Python Code", height=300)
    else:
        uploaded_file = st.file_uploader("Upload Python File", type=["py"])
        if uploaded_file:
            code_input = uploaded_file.read().decode("utf-8")
            st.text_area("Code Preview", code_input, height=300)
        else:
            code_input = ""

    if st.button("🔍 Analyze Code"):

        if code_input.strip():

            with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False, encoding="utf-8") as tmp:
                tmp.write(code_input)
                path = tmp.name

            try:
                cluster, label = predict_code_quality(path)
                score, grade = get_score_and_grade(label)
                metrics = extract(path)
                suggestions = generate_suggestions(label, metrics)

                save_analysis("Single", score, grade)

                st.progress(score / 100)
                st.metric("Score", f"{score}/100")
                st.metric("Grade", grade)

                st.subheader("📌 Metrics")
                cols = st.columns(3)
                for i, (k, v) in enumerate(metrics.items()):
                    cols[i % 3].metric(k.replace("_", " ").title(), v)

                st.subheader("🤖 Suggestions")
                for s in suggestions:
                    st.write(s)

            finally:
                os.remove(path)


# -----------------------------------
# CODE COMPARISON MODE
# -----------------------------------
if analysis_mode == "Code Comparison":

    st.subheader("⚔ Compare Two Python Files")

    file1 = st.file_uploader("Upload First File", type=["py"], key="file1")
    file2 = st.file_uploader("Upload Second File", type=["py"], key="file2")

    if file1 and file2:

        code1 = file1.read().decode("utf-8")
        code2 = file2.read().decode("utf-8")

        with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False, encoding="utf-8") as tmp1:
            tmp1.write(code1)
            path1 = tmp1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False, encoding="utf-8") as tmp2:
            tmp2.write(code2)
            path2 = tmp2.name

        cluster1, label1 = predict_code_quality(path1)
        cluster2, label2 = predict_code_quality(path2)

        score1, grade1 = get_score_and_grade(label1)
        score2, grade2 = get_score_and_grade(label2)

        save_analysis("Comparison File1", score1, grade1)
        save_analysis("Comparison File2", score2, grade2)

        metrics1 = extract(path1)
        metrics2 = extract(path2)

        col1, col2 = st.columns(2)
        col1.metric("File 1 Score", f"{score1}/100")
        col2.metric("File 2 Score", f"{score2}/100")

        if score1 > score2:
            st.success("🏆 File 1 is better.")
        elif score2 > score1:
            st.success("🏆 File 2 is better.")
        else:
            st.info("🤝 Both files are equal.")

        st.subheader("📈 Radar Chart Comparison")
        radar_chart(metrics1, metrics2)

        os.remove(path1)
        os.remove(path2)
