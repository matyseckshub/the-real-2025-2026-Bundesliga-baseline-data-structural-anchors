import sqlite3
import random
import os

def build_bundesliga_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "bundesliga_intelligence.db")
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. CLUB FINANCIAL & STRUCTURAL METADATA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clubs (
        club_id INTEGER PRIMARY KEY,
        club_name TEXT NOT NULL,
        squad_value_million REAL NOT NULL,
        annual_tv_revenue_million REAL NOT NULL,
        stadium_capacity INTEGER NOT NULL,
        annual_wage_bill_million REAL NOT NULL,
        academy_graduates_in_squad INTEGER NOT NULL
    );
    """)

    # 2. MATCHDAY TELEMETRY & PERFORMANCE LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matchday_logs (
        log_id INTEGER PRIMARY KEY,
        club_id INTEGER NOT NULL,
        matchday INTEGER NOT NULL,
        points_earned INTEGER NOT NULL,
        xg_generated REAL NOT NULL,
        xg_conceded REAL NOT NULL,
        goals_scored INTEGER NOT NULL,
        goals_conceded INTEGER NOT NULL,
        active_injury_count INTEGER NOT NULL,
        minutes_played_by_academy INTEGER NOT NULL,
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    );
    """)

    # Real-world 2025/2026 baseline data anchors
    bundesliga_teams = [
        ("FC Bayern München", 920.0, 85.0, 75000, 260.0, 4),
        ("Borussia Dortmund", 480.0, 78.0, 81365, 140.0, 6),
        ("Bayer 04 Leverkusen", 620.0, 74.0, 30210, 150.0, 3),
        ("RB Leipzig", 510.0, 70.0, 47069, 130.0, 2),
        ("VfB Stuttgart", 280.0, 62.0, 60449, 85.0, 7),
        ("Eintracht Frankfurt", 260.0, 58.0, 58000, 75.0, 5),
        ("TSG 1899 Hoffenheim", 140.0, 50.0, 30150, 55.0, 4),
        ("SV Werder Bremen", 110.0, 46.0, 42100, 42.0, 5),
        ("SC Freiburg", 135.0, 48.0, 34700, 48.0, 11), 
        ("FC Augsburg", 95.0, 42.0, 30660, 38.0, 3),
        ("1. FC Heidenheim", 65.0, 38.0, 15000, 28.0, 2),
        ("VfL Wolfsburg", 180.0, 52.0, 30000, 68.0, 4),
        ("Mainz 05", 90.0, 40.0, 33305, 34.0, 8),
        ("Borussia Mönchengladbach", 120.0, 45.0, 54022, 48.0, 6),
        ("FC St. Pauli", 55.0, 35.0, 29546, 24.0, 4),
        ("Holstein Kiel", 42.0, 32.0, 15034, 20.0, 3),
        ("VfL Bochum", 48.0, 34.0, 26000, 22.0, 4),
        ("Union Berlin", 115.0, 44.0, 22012, 44.0, 3)
    ]

    for club in bundesliga_teams:
        cursor.execute("""
        INSERT INTO clubs (club_name, squad_value_million, annual_tv_revenue_million, stadium_capacity, annual_wage_bill_million, academy_graduates_in_squad)
        VALUES (?, ?, ?, ?, ?, ?)
        """, club)
        club_id = cursor.lastrowid

        # STOCHASTIC SHOCK COEFFICIENTS: Generated purely organically per run
        goalkeeper_variance = random.choice(["Elite", "Standard", "Slump"])
        injury_proneness = random.choice(["High_Load", "Normal"])
        tactical_efficiency = random.choice(["Overperforming", "Expected", "Underperforming"])

        for md in range(1, 35):
            base_xg_gen = random.uniform(1.2, 2.4) if club[2] > 60 else random.uniform(0.8, 1.6)
            base_xg_con = random.uniform(0.7, 1.3) if club[2] > 60 else random.uniform(1.3, 2.2)
            
            if tactical_efficiency == "Underperforming":
                base_xg_gen *= 0.85
            elif tactical_efficiency == "Overperforming":
                base_xg_gen *= 1.15
                
            g_conceded_factor = 1.3 if goalkeeper_variance == "Slump" else (0.8 if goalkeeper_variance == "Elite" else 1.0)
            
            xg_gen = round(max(0.2, base_xg_gen), 2)
            xg_con = round(max(0.2, base_xg_con), 2)
            
            goals_scored = max(0, int(random.gauss(xg_gen, 0.8)))
            goals_conceded = max(0, int(random.gauss(xg_con * g_conceded_factor, 0.8)))
            
            if goals_scored > goals_conceded:
                points = 3
            elif goals_scored == goals_conceded:
                points = 1
            else:
                points = 0
                
            injuries = random.randint(3, 9) if injury_proneness == "High_Load" and md > 20 else random.randint(1, 4)
            academy_minutes = random.randint(180, 450) if club[0] in ["SC Freiburg", "Mainz 05", "VfB Stuttgart"] else random.randint(0, 180)

            cursor.execute("""
            INSERT INTO matchday_logs (club_id, matchday, points_earned, xg_generated, xg_conceded, goals_scored, goals_conceded, active_injury_count, minutes_played_by_academy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (club_id, md, points, xg_gen, xg_con, goals_scored, goals_conceded, injuries, academy_minutes))

    conn.commit()
    conn.close()
    print("Database built cleanly.")

if __name__ == "__main__":
    build_bundesliga_database()