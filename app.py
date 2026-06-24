import sqlite3
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from generate_football_db import build_bundesliga_database

st.set_page_config(page_title="DFL Sports & Capital Intelligence Platform", layout="wide")

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(script_dir, "bundesliga_intelligence.db")

# Self-healing database check with enterprise metrics validation
def verify_and_build_db():
    if not os.path.exists(DB_FILE):
        build_bundesliga_database()
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT annual_wage_bill_million FROM clubs LIMIT 1;")
        conn.close()
    except sqlite3.OperationalError:
        conn.close()
        build_bundesliga_database()

verify_and_build_db()

def run_query(query):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("DFL Sports & Capital Intelligence Platform")
st.caption(
    "Data note: club valuations, TV revenue, and wage bills are real 2025/26 baseline anchors. "
    "Matchday performance stats (xG, injuries, points) are procedurally generated to demonstrate "
    "the analytics pipeline, not live match data."
)
st.markdown("---")

# FIX: previously this radio was defined with only 3 options here, then a SECOND
# st.sidebar.radio() with 4 options was created inside the Module 3 block. That made
# Module 4 unreachable and would throw a duplicate-widget error if triggered.
# It's now defined once, with all 4 options, at the top.
st.sidebar.title("DFL Executive Control Panel")
module = st.sidebar.radio("Select Analytics Module:", [
    "1. Relegation Capital Risk Matrix",
    "2. Wage Bill Efficiency (ROI)",
    "3. Academy Strategic Intelligence",
    "4. Interactive Executive SQL Sandbox"
])

# ========================================================
# MODULE 1: RELEGATION CAPITAL RISK MATRIX
# ========================================================
if module == "1. Relegation Capital Risk Matrix":
    st.header("Bundesliga Telemetry & Relegation Risk Engine")
    st.markdown("Isolating performance decay trends and corresponding corporate exposure risks.")
    st.markdown("---")

    query = """
    WITH PerformanceAgg as (
        SELECT 
            club_id,
            SUM(points_earned) as total_points,
            ROUND(AVG(xg_generated), 2) as avg_xg_gen,
            ROUND(AVG(xg_conceded), 2) as avg_xg_con,
            SUM(goals_scored) - SUM(goals_conceded) as goal_diff,
            SUM(CASE WHEN matchday > 24 THEN points_earned ELSE 0 END) as trailing_form,
            AVG(active_injury_count) as avg_injuries
        FROM matchday_logs
        GROUP BY club_id
    )
    SELECT 
        c.club_name, c.squad_value_million, c.annual_tv_revenue_million,
        p.total_points, p.goal_diff, p.trailing_form, ROUND(p.avg_injuries, 1) as avg_injuries,
        ROUND(
            (CASE WHEN p.trailing_form <= 6 THEN 40 WHEN p.trailing_form <= 12 THEN 20 ELSE 0 END) +
            (CASE WHEN (p.avg_xg_gen - p.avg_xg_con) < -0.3 THEN 30 WHEN (p.avg_xg_gen - p.avg_xg_con) < 0 THEN 15 ELSE 0 END) +
            (CASE WHEN p.avg_injuries >= 5 THEN 20 ELSE 5 END) +
            (CASE WHEN c.squad_value_million < 100 THEN 10 ELSE 0 END)
        , 2) as risk_score,
        ROUND((c.annual_tv_revenue_million * 0.45) + (c.squad_value_million * 0.25), 2) as financial_exposure
    FROM PerformanceAgg p
    JOIN clubs c ON p.club_id = c.club_id
    ORDER BY risk_score DESC;
    """
    df = run_query(query)

    critical_clubs = df[df['risk_score'] >= 50]
    col1, col2 = st.columns(2)
    col1.metric("Clubs Flagged at Critical Threat Level (Score >= 50)", f"{len(critical_clubs)} Teams")
    col2.metric("Total Cumulative Market Capital Exposed", f"€{critical_clubs['financial_exposure'].sum():,.1f}M")

    with st.expander("How the risk score is calculated"):
        st.markdown(
            "This is an illustrative heuristic, not a validated predictive model: "
            "40 pts for weak trailing form, 30 pts for negative xG differential, "
            "20 pts for high injury load, 10 pts for squad value under €100M."
        )

    st.markdown("---")
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.scatterplot(data=df, x='risk_score', y='financial_exposure', size='squad_value_million', hue='club_name', palette='tab20', sizes=(50, 400), ax=ax)
    ax.axvline(50, color='red', linestyle='--', alpha=0.7, label="Risk Threshold")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    st.pyplot(fig)
    plt.close()

# ========================================================
# MODULE 2: WAGE BILL EFFICIENCY (ROI)
# ========================================================
elif module == "2. Wage Bill Efficiency (ROI)":
    st.header("Wage Expenditure Performance Efficiency Matrix")
    st.markdown("Measuring sporting return on investment: Capital spending relative to points achieved.")
    st.markdown("---")

    query = """
    SELECT 
        c.club_name,
        c.annual_wage_bill_million,
        SUM(m.points_earned) as total_points,
        ROUND(c.annual_wage_bill_million * 1000000 / SUM(m.points_earned), 2) as cost_per_point_euro
    FROM matchday_logs m
    JOIN clubs c ON m.club_id = c.club_id
    GROUP BY c.club_id
    ORDER BY cost_per_point_euro ASC;
    """
    df = run_query(query)
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df, x='cost_per_point_euro', y='club_name', palette='Blues_r', hue='club_name', legend=False)
    ax.set_xlabel("Capital Spent Per Single League Point Earned (€)")
    ax.set_ylabel("")
    st.pyplot(fig)
    plt.close()

# ========================================================
# MODULE 3: ACADEMY STRATEGIC INTELLIGENCE
# ========================================================
elif module == "3. Academy Strategic Intelligence":
    st.header("Academy Structural Contribution Log")
    st.markdown("Evaluating market procurement replacement cost savings generated by home-grown talent.")
    st.markdown("---")

    query = """
    SELECT 
        c.club_name,
        c.academy_graduates_in_squad,
        SUM(m.minutes_played_by_academy) as total_academy_minutes,
        c.academy_graduates_in_squad * 2.5 as calculated_market_savings_millions
    FROM matchday_logs m
    JOIN clubs c ON m.club_id = c.club_id
    GROUP BY c.club_id
    ORDER BY total_academy_minutes DESC;
    """
    df = run_query(query)
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.scatterplot(data=df, x='total_academy_minutes', y='calculated_market_savings_millions', size='academy_graduates_in_squad', hue='club_name', palette='Set2', sizes=(100, 500))
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    ax.set_xlabel("Total Accumulated On-Pitch Academy Minutes")
    ax.set_ylabel("Calculated Capital Procurement Savings (€ Millions)")
    st.pyplot(fig)
    plt.close()

# ========================================================
# MODULE 4: INTERACTIVE EXECUTIVE SQL SANDBOX
# ========================================================
elif module == "4. Interactive Executive SQL Sandbox":
    st.header("Enterprise SQL Analytics Sandbox")
    st.markdown("Run custom ad-hoc relational queries directly against the live Bundesliga database telemetry.")

    with st.expander("View Live Database Schema & Architecture"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Table: `clubs`**")
            st.code("""
- club_id (INTEGER, PK)
- club_name (TEXT)
- squad_value_million (REAL)
- annual_tv_revenue_million (REAL)
- stadium_capacity (INTEGER)
- annual_wage_bill_million (REAL)
- academy_graduates_in_squad (INTEGER)
            """, language="markdown")
        with col2:
            st.markdown("**Table: `matchday_logs`**")
            st.code("""
- log_id (INTEGER, PK)
- club_id (INTEGER, FK)
- matchday (INTEGER)
- points_earned (INTEGER)
- xg_generated (REAL)
- xg_conceded (REAL)
- goals_scored (INTEGER)
- goals_conceded (INTEGER)
- active_injury_count (INTEGER)
- minutes_played_by_academy (INTEGER)
            """, language="markdown")

    st.markdown("---")
    st.subheader("Executive Quick-Queries")
    preset_option = st.selectbox("Select a pre-configured scenario to load:", [
        "--- Select a Query Preset ---",
        "Top 5 Highest Scoring Matchdays per Club",
        "Worst Injury Crises vs Points Dropped",
        "Stadium Attendance Value Density (TV vs Capacity)"
    ])

    default_sql = "SELECT * FROM clubs LIMIT 5;"
    if preset_option == "Top 5 Highest Scoring Matchdays per Club":
        default_sql = """SELECT c.club_name, m.matchday, m.goals_scored \nFROM matchday_logs m \nJOIN clubs c ON m.club_id = c.club_id \nWHERE m.goals_scored >= 4 \nORDER BY m.goals_scored DESC \nLIMIT 10;"""
    elif preset_option == "Worst Injury Crises vs Points Dropped":
        default_sql = """SELECT c.club_name, COUNT(m.matchday) as high_injury_matchdays, AVG(m.points_earned) as avg_points_during_crisis \nFROM matchday_logs m \nJOIN clubs c ON m.club_id = c.club_id \nWHERE m.active_injury_count >= 7 \nGROUP BY c.club_name \nORDER BY avg_points_during_crisis ASC;"""
    elif preset_option == "Stadium Attendance Value Density (TV vs Capacity)":
        default_sql = """SELECT club_name, stadium_capacity, annual_tv_revenue_million, \nROUND((stadium_capacity * 1.0) / annual_tv_revenue_million, 2) as seats_per_million_tv \nFROM clubs \nORDER BY seats_per_million_tv DESC;"""

    st.subheader("Live SQL Query Terminal")
    user_sql = st.text_area("Edit your SQLite statement below:", value=default_sql, height=150)

    if st.button("Execute Live Query"):
        try:
            sandbox_df = run_query(user_sql)
            st.success("Query executed successfully!")
            st.dataframe(sandbox_df)

            csv = sandbox_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Result Set to CSV",
                data=csv,
                file_name="dfl_custom_query_export.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"SQL Syntax Error: {e}")
