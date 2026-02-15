from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
import db


def render():
    today = datetime.now().strftime("%Y-%m-%d")
    summary = db.get_daily_summary(today)
    cal_goal = int(db.get_setting("daily_calorie_goal"))
    protein_goal = int(db.get_setting("protein_goal"))
    carbs_goal = int(db.get_setting("carbs_goal"))
    fat_goal = int(db.get_setting("fat_goal"))

    # Header with settings gear
    col_title, col_gear = st.columns([6, 1])
    with col_title:
        st.header("Today")
    with col_gear:
        if st.button("⚙️", key="settings_btn", help="Settings"):
            st.session_state.page = "settings"
            st.rerun()

    # --- Big Number ---
    net_calories = summary["calories"] - summary["burned"]
    remaining = cal_goal - net_calories

    c1, c2, c3 = st.columns(3)
    c1.metric("Eaten", f"{summary['calories']:.0f} kcal")
    c2.metric("Burned", f"{summary['burned']:.0f} kcal")
    c3.metric("Remaining", f"{remaining:.0f} kcal", delta=None)

    # --- 7-day Streak ---
    streak = db.get_streak(today)
    _render_streak(today, streak)

    # --- Macro Donut Chart ---
    st.subheader("Macros")
    fig = go.Figure()

    # Actual values
    fig.add_trace(go.Pie(
        labels=["Protein", "Carbs", "Fat"],
        values=[summary["protein"], summary["carbs"], summary["fat"]],
        hole=0.6,
        marker_colors=["#FF6B6B", "#4ECDC4", "#FFE66D"],
        textinfo="label+value",
        texttemplate="%{label}<br>%{value:.0f}g",
        domain={"x": [0, 0.48]},
    ))

    fig.update_layout(
        showlegend=False,
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[
            dict(text=f"{net_calories:.0f}<br>kcal", x=0.24, y=0.5, font_size=16, showarrow=False),
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Macro progress bars
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.caption(f"Protein: {summary['protein']:.0f} / {protein_goal}g")
        st.progress(min(summary["protein"] / protein_goal, 1.0) if protein_goal > 0 else 0)
    with mc2:
        st.caption(f"Carbs: {summary['carbs']:.0f} / {carbs_goal}g")
        st.progress(min(summary["carbs"] / carbs_goal, 1.0) if carbs_goal > 0 else 0)
    with mc3:
        st.caption(f"Fat: {summary['fat']:.0f} / {fat_goal}g")
        st.progress(min(summary["fat"] / fat_goal, 1.0) if fat_goal > 0 else 0)

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
                    f"**{entry['name']}** — {entry['calories']:.0f} kcal "
                    f"<small style='color:gray'>({entry['time']})</small>",
                    unsafe_allow_html=True,
                )
                st.caption(f"P: {entry['protein']:.0f}g  C: {entry['carbs']:.0f}g  F: {entry['fat']:.0f}g")
            with col_del:
                if st.button("🗑️", key=f"del_food_{entry['id']}", help="Delete"):
                    db.delete_food_log(entry["id"])
                    st.rerun()

        for entry in workout_entries:
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(f"🏋️ **{entry['name']}** — -{entry['calories_burned']:.0f} kcal")
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
        day_str = day.strftime("%Y-%m-%d")
        label = day.strftime("%a")[0]
        has_entry = (6 - i) < streak if i < 6 else streak > 0
        # Check the actual day
        if i == 0:
            has_entry = streak > 0
        else:
            # Check if this specific day is within the streak
            has_entry = streak > i

        color = "#FF6B6B" if has_entry else "#E0E0E0"
        text_color = "white" if has_entry else "#999"
        circles.append(
            f'<span style="display:inline-block;width:36px;height:36px;line-height:36px;'
            f'border-radius:50%;background:{color};color:{text_color};text-align:center;'
            f'margin:0 4px;font-size:14px;font-weight:bold">{label}</span>'
        )

    st.markdown(
        f'<div style="text-align:center;margin:8px 0">{"".join(circles)}'
        f'<br><small style="color:gray">{streak} day streak</small></div>',
        unsafe_allow_html=True,
    )
