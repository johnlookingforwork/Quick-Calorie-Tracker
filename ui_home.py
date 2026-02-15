from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import db


def _fmt(n: float) -> str:
    """Format number: drop .0 decimals, keep meaningful ones."""
    return f"{n:g}"


def render():
    today = datetime.now().strftime("%Y-%m-%d")
    summary = db.get_daily_summary(today)
    cal_goal = int(db.get_setting("daily_calorie_goal"))
    protein_goal = int(db.get_setting("protein_goal"))
    carbs_goal = int(db.get_setting("carbs_goal"))
    fat_goal = int(db.get_setting("fat_goal"))

    st.header("Today")

    # --- Big Number: Only Remaining ---
    net_calories = summary["calories"] - summary["burned"]
    remaining = cal_goal - net_calories

    if remaining >= 0:
        color = "#4ECDC4"
        label = "remaining"
    else:
        color = "#FF6B6B"
        label = "over goal"

    st.markdown(
        f'<div style="text-align:center;margin:0.5rem 0 0.8rem">'
        f'<div style="font-size:3rem;font-weight:700;color:{color};line-height:1">{_fmt(abs(remaining))}</div>'
        f'<div style="font-size:0.9rem;color:#999">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- 7-day Streak ---
    streak = db.get_streak(today)
    _render_streak(today, streak)

    # --- 3 Macro Donut Charts ---
    st.subheader("Macros")

    protein_val = summary["protein"]
    carbs_val = summary["carbs"]
    fat_val = summary["fat"]

    macros = [
        ("Protein", protein_val, protein_goal, "#FF6B6B"),
        ("Carbs", carbs_val, carbs_goal, "#4ECDC4"),
        ("Fat", fat_val, fat_goal, "#FFE66D"),
    ]

    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
    )

    for i, (name, val, goal, color) in enumerate(macros, 1):
        remainder = max(goal - val, 0)
        fig.add_trace(go.Pie(
            labels=[name, ""],
            values=[val, remainder],
            hole=0.7,
            marker=dict(colors=[color, "#F0F0F0"]),
            textinfo="none",
            hovertemplate=f"{name}: {_fmt(val)}g / {_fmt(goal)}g<extra></extra>",
            sort=False,
        ), row=1, col=i)

    fig.update_layout(
        showlegend=False,
        height=160,
        margin=dict(t=5, b=5, l=5, r=5),
        annotations=[
            dict(text=f"<b>{_fmt(macros[0][1])}</b><br><span style='font-size:9px'>/{_fmt(macros[0][2])}g</span>",
                 x=0.11, y=0.5, font_size=13, showarrow=False),
            dict(text=f"<b>{_fmt(macros[1][1])}</b><br><span style='font-size:9px'>/{_fmt(macros[1][2])}g</span>",
                 x=0.5, y=0.5, font_size=13, showarrow=False),
            dict(text=f"<b>{_fmt(macros[2][1])}</b><br><span style='font-size:9px'>/{_fmt(macros[2][2])}g</span>",
                 x=0.89, y=0.5, font_size=13, showarrow=False),
        ],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Labels below donuts
    st.markdown(
        '<div style="display:flex;justify-content:space-around;text-align:center;margin-top:-8px">'
        f'<span style="color:#FF6B6B;font-size:0.75rem;font-weight:600">Protein</span>'
        f'<span style="color:#4ECDC4;font-size:0.75rem;font-weight:600">Carbs</span>'
        f'<span style="color:#C8B400;font-size:0.75rem;font-weight:600">Fat</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # --- Today's Log ---
    st.subheader("Today's Log")
    food_entries = db.get_food_log(today)
    workout_entries = db.get_workouts(today)

    if not food_entries and not workout_entries:
        st.info("No entries yet. Tap + to log your first meal!")
    else:
        for entry in food_entries:
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"**{entry['name']}** — {_fmt(entry['calories'])} kcal "
                    f"<small style='color:gray'>({entry['time']})</small>",
                    unsafe_allow_html=True,
                )
                st.caption(f"P: {_fmt(entry['protein'])}g  C: {_fmt(entry['carbs'])}g  F: {_fmt(entry['fat'])}g")
            with col_del:
                if st.button("🗑️", key=f"del_food_{entry['id']}", help="Delete"):
                    db.delete_food_log(entry["id"])
                    st.rerun()

        for entry in workout_entries:
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(f"🏋️ **{entry['name']}** — -{_fmt(entry['calories_burned'])} kcal")
            with col_del:
                if st.button("🗑️", key=f"del_workout_{entry['id']}", help="Delete"):
                    db.delete_workout(entry["id"])
                    st.rerun()


def _render_streak(today: str, streak: int):
    """Render 7-day streak circles."""
    today_dt = datetime.fromisoformat(today)
    circles = []
    for i in range(6, -1, -1):
        day = today_dt - timedelta(days=i)
        label = day.strftime("%a")[0]
        has_entry = streak > i

        color = "#FF6B6B" if has_entry else "#E0E0E0"
        text_color = "white" if has_entry else "#999"
        circles.append(
            f'<span style="display:inline-block;width:32px;height:32px;line-height:32px;'
            f'border-radius:50%;background:{color};color:{text_color};text-align:center;'
            f'margin:0 3px;font-size:12px;font-weight:bold">{label}</span>'
        )

    st.markdown(
        f'<div style="text-align:center;margin:4px 0">{"".join(circles)}'
        f'<br><small style="color:gray">{streak} day streak</small></div>',
        unsafe_allow_html=True,
    )
