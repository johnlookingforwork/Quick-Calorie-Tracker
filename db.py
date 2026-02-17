import sqlite3
import os
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "tracker.db")


@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            name TEXT NOT NULL,
            calories REAL NOT NULL DEFAULT 0,
            protein REAL NOT NULL DEFAULT 0,
            carbs REAL NOT NULL DEFAULT 0,
            fat REAL NOT NULL DEFAULT 0,
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_food_log_date ON food_log(date);

        CREATE TABLE IF NOT EXISTS workout_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            calories_burned REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_workout_log_date ON workout_log(date);

        CREATE TABLE IF NOT EXISTS saved_foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            serving_size REAL NOT NULL DEFAULT 1,
            unit TEXT NOT NULL DEFAULT 'serving',
            calories REAL NOT NULL DEFAULT 0,
            protein REAL NOT NULL DEFAULT 0,
            carbs REAL NOT NULL DEFAULT 0,
            fat REAL NOT NULL DEFAULT 0
        );
    """)
    # Seed default settings
    defaults = {
        "daily_calorie_goal": "2500",
        "protein_goal": "150",
        "carbs_goal": "250",
        "fat_goal": "65",
    }
    for key, value in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
    conn.commit()


# --- Settings ---

def get_setting(key: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_setting(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()


# --- Food Log ---

def add_food_log(date: str, time: str, name: str, calories: float, protein: float, carbs: float, fat: float, source: str = "manual"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO food_log (date, time, name, calories, protein, carbs, fat, source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (date, time, name, calories, protein, carbs, fat, source, datetime.now().isoformat()),
    )
    conn.commit()


def get_food_log(date: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM food_log WHERE date = ? ORDER BY time DESC", (date,)
    ).fetchall()
    return [dict(r) for r in rows]


def delete_food_log(entry_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM food_log WHERE id = ?", (entry_id,))
    conn.commit()


# --- Workout Log ---

def add_workout(date: str, name: str, calories_burned: float):
    conn = get_connection()
    conn.execute(
        """INSERT INTO workout_log (date, name, calories_burned, created_at)
           VALUES (?, ?, ?, ?)""",
        (date, name, calories_burned, datetime.now().isoformat()),
    )
    conn.commit()


def get_workouts(date: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM workout_log WHERE date = ? ORDER BY created_at DESC", (date,)
    ).fetchall()
    return [dict(r) for r in rows]


def delete_workout(entry_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM workout_log WHERE id = ?", (entry_id,))
    conn.commit()


# --- Daily Summary ---

def get_daily_summary(date: str) -> dict:
    conn = get_connection()
    food = conn.execute(
        """SELECT COALESCE(SUM(calories),0) as calories,
                  COALESCE(SUM(protein),0) as protein,
                  COALESCE(SUM(carbs),0) as carbs,
                  COALESCE(SUM(fat),0) as fat
           FROM food_log WHERE date = ?""",
        (date,),
    ).fetchone()
    workout = conn.execute(
        "SELECT COALESCE(SUM(calories_burned),0) as burned FROM workout_log WHERE date = ?",
        (date,),
    ).fetchone()
    return {
        "calories": food["calories"],
        "protein": food["protein"],
        "carbs": food["carbs"],
        "fat": food["fat"],
        "burned": workout["burned"],
    }


def get_net_calories_range(start_date: str, end_date: str) -> dict[str, float]:
    """Return {date_str: net_calories} for each date that has any log entries."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT date, COALESCE(SUM(calories),0) as cals
           FROM food_log WHERE date BETWEEN ? AND ? GROUP BY date""",
        (start_date, end_date),
    ).fetchall()
    food_map = {r["date"]: r["cals"] for r in rows}
    rows = conn.execute(
        """SELECT date, COALESCE(SUM(calories_burned),0) as burned
           FROM workout_log WHERE date BETWEEN ? AND ? GROUP BY date""",
        (start_date, end_date),
    ).fetchall()
    burn_map = {r["date"]: r["burned"] for r in rows}
    all_dates = set(food_map) | set(burn_map)
    return {d: food_map.get(d, 0) - burn_map.get(d, 0) for d in all_dates}


def get_date_range_summary(start_date: str, end_date: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT date,
                  COALESCE(SUM(calories),0) as calories,
                  COALESCE(SUM(protein),0) as protein,
                  COALESCE(SUM(carbs),0) as carbs,
                  COALESCE(SUM(fat),0) as fat
           FROM food_log
           WHERE date BETWEEN ? AND ?
           GROUP BY date ORDER BY date""",
        (start_date, end_date),
    ).fetchall()
    return [dict(r) for r in rows]


def get_streak(today: str) -> int:
    """Count consecutive days with at least one food log entry, ending today."""
    conn = get_connection()
    streak = 0
    current = datetime.fromisoformat(today)
    while True:
        date_str = current.strftime("%Y-%m-%d")
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM food_log WHERE date = ?", (date_str,)
        ).fetchone()
        if row["cnt"] > 0:
            streak += 1
            current -= timedelta(days=1)
        else:
            break
    return streak


# --- Saved Foods ---

def get_saved_foods() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM saved_foods ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def add_saved_food(name: str, serving_size: float, unit: str, calories: float, protein: float, carbs: float, fat: float):
    conn = get_connection()
    conn.execute(
        """INSERT INTO saved_foods (name, serving_size, unit, calories, protein, carbs, fat)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, serving_size, unit, calories, protein, carbs, fat),
    )
    conn.commit()


def update_saved_food(food_id: int, name: str, serving_size: float, unit: str, calories: float, protein: float, carbs: float, fat: float):
    conn = get_connection()
    conn.execute(
        """UPDATE saved_foods SET name=?, serving_size=?, unit=?, calories=?, protein=?, carbs=?, fat=?
           WHERE id=?""",
        (name, serving_size, unit, calories, protein, carbs, fat, food_id),
    )
    conn.commit()


def delete_saved_food(food_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM saved_foods WHERE id = ?", (food_id,))
    conn.commit()


# --- Export ---

def export_all_logs() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT date, time, name, calories, protein, carbs, fat, source, 'food' as type
           FROM food_log
           UNION ALL
           SELECT date, '' as time, name, -calories_burned as calories, 0 as protein, 0 as carbs, 0 as fat, 'workout' as source, 'workout' as type
           FROM workout_log
           ORDER BY date DESC, time DESC""",
        conn,
    )
    return df
