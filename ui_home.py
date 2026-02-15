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
        f'<div style="font-size:3rem;font-weight:700;color:{color};line-height:1">{abs(remaining):.0f}</div>'
        f'<div style="font-size:0.9rem;color:#999">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- 7-day Streak ---
    streak = db.get_streak(today)
    _render_streak(today, streak)

    # --- Macro Donut Chart ---
    st.subheader("Macros")

    protein_val = summary["protein"]
    carbs_val = summary["carbs"]
    fat_val = summary["fat"]
    total_macros = protein_val + carbs_val + fat_val

    if total_macros > 0:
        fig = go.Figure(data=[go.Pie(
            labels=["Protein", "Carbs", "Fat"],
            values=[protein_val, carbs_val, fat_val],
            hole=0.65,
            marker=dict(colors=["#FF6B6B", "#4ECDC4", "#FFE66D"]),
            textinfo="label+value",
            texttemplate="%{label}<br>%{value:.0f}g",
            textposition="outside",
            textfont_size=12,
            hovertemplate="%{label}: %{value:.0f}g<extra></extra>",
            sort=False,
        )])
        fig.update_layout(
            showlegend=False,
            height=240,
            margin=dict(t=20, b=20, l=20, r=20),
            annotations=[dict(
                text=f"<b>{net_calories:.0f}</b><br>kcal",
                x=0.5, y=0.5,
                font_size=15,
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.caption("Log food to see your macro breakdown")

    # Macro progress bars
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.caption(f"Protein: {protein_val:.0f}/{protein_goal}g")
        st.progress(min(protein_val / protein_goal, 1.0) if protein_goal > 0 else 0)
    with mc2:
        st.caption(f"Carbs: {carbs_val:.0f}/{carbs_goal}g")
        st.progress(min(carbs_val / carbs_goal, 1.0) if carbs_goal > 0 else 0)
    with mc3:
        st.caption(f"Fat: {fat_val:.0f}/{fat_goal}g")
        st.progress(min(fat_val / fat_goal, 1.0) if fat_goal > 0 else 0)

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
