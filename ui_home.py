from datetime import datetime, timedelta

import streamlit as st
import db


def _fmt(n: float) -> str:
    """Format number: drop .0 decimals, keep meaningful ones."""
    return f"{n:g}"


def _pct(val: float, goal: float) -> float:
    """Percentage clamped to 0-100."""
    if goal <= 0:
        return 0
    return min(val / goal * 100, 100)


def render():
    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")
    summary = db.get_daily_summary(today)
    cal_goal = int(db.get_setting("daily_calorie_goal"))
    protein_goal = int(db.get_setting("protein_goal"))
    carbs_goal = int(db.get_setting("carbs_goal"))
    fat_goal = int(db.get_setting("fat_goal"))

    net_calories = summary["calories"] - summary["burned"]
    remaining = cal_goal - net_calories

    protein_val = summary["protein"]
    carbs_val = summary["carbs"]
    fat_val = summary["fat"]

    protein_left = max(protein_goal - protein_val, 0)
    carbs_left = max(carbs_goal - carbs_val, 0)
    fat_left = max(fat_goal - fat_val, 0)

    # --- Week day strip ---
    _render_week_strip(today_dt)

    # --- Summary card (Cal AI style) ---
    cal_pct = _pct(net_calories, cal_goal)
    p_pct = _pct(protein_val, protein_goal)
    c_pct = _pct(carbs_val, carbs_goal)
    f_pct = _pct(fat_val, fat_goal)

    cal_color = "#222" if remaining >= 0 else "#FF6B6B"

    st.markdown(f"""
    <div style="background:#F7F7F7;border-radius:20px;padding:24px 20px 20px;margin:8px 0 12px">
        <!-- Calorie ring + number -->
        <div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:18px">
            <div style="position:relative;width:64px;height:64px">
                <svg viewBox="0 0 36 36" style="width:64px;height:64px;transform:rotate(-90deg)">
                    <circle cx="18" cy="18" r="14" fill="none" stroke="#E8E8E8" stroke-width="3.5"/>
                    <circle cx="18" cy="18" r="14" fill="none" stroke="{cal_color}" stroke-width="3.5"
                            stroke-dasharray="{cal_pct * 0.88:.1f} 88" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="text-align:left">
                <div style="font-size:2.4rem;font-weight:700;color:{cal_color};line-height:1">{_fmt(abs(remaining))}</div>
                <div style="font-size:0.8rem;color:#999">Calories {'left' if remaining >= 0 else 'over'}</div>
            </div>
        </div>

        <!-- 3 macro mini-rings -->
        <div style="display:flex;justify-content:space-around;text-align:center">
            {_macro_ring("Protein", protein_left, protein_goal, p_pct, "#FF6B6B")}
            {_macro_ring("Carbs", carbs_left, carbs_goal, c_pct, "#4ECDC4")}
            {_macro_ring("Fat", fat_left, fat_goal, f_pct, "#FFD93D")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Today's Log ---
    st.subheader("Recently logged")
    food_entries = db.get_food_log(today)
    workout_entries = db.get_workouts(today)

    if not food_entries and not workout_entries:
        st.caption("Nothing logged yet today.")
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


def _macro_ring(label: str, left: float, goal: float, pct: float, color: str) -> str:
    """Return HTML for a small macro ring with value below."""
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center">
        <div style="position:relative;width:44px;height:44px">
            <svg viewBox="0 0 36 36" style="width:44px;height:44px;transform:rotate(-90deg)">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#E8E8E8" stroke-width="4"/>
                <circle cx="18" cy="18" r="14" fill="none" stroke="{color}" stroke-width="4"
                        stroke-dasharray="{pct * 0.88:.1f} 88" stroke-linecap="round"/>
            </svg>
        </div>
        <div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(left)}g</div>
        <div style="font-size:0.65rem;color:#999">{label} left</div>
    </div>
    """


def _render_week_strip(today_dt: datetime):
    """Render a Cal AI-style week day strip with today highlighted."""
    start = today_dt - timedelta(days=today_dt.weekday() + 1)  # Sunday
    days = []
    for i in range(7):
        day = start + timedelta(days=i)
        letter = day.strftime("%a")[0]
        date_num = day.day
        is_today = day.date() == today_dt.date()

        if is_today:
            days.append(
                f'<div style="display:flex;flex-direction:column;align-items:center">'
                f'<span style="font-size:0.65rem;color:#999;margin-bottom:2px">{letter}</span>'
                f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:30px;height:30px;border-radius:50%;background:#222;color:#fff;'
                f'font-size:0.8rem;font-weight:600">{date_num}</span></div>'
            )
        else:
            days.append(
                f'<div style="display:flex;flex-direction:column;align-items:center">'
                f'<span style="font-size:0.65rem;color:#999;margin-bottom:2px">{letter}</span>'
                f'<span style="font-size:0.8rem;color:#666;height:30px;line-height:30px">{date_num}</span></div>'
            )

    st.markdown(
        f'<div style="display:flex;justify-content:space-around;padding:4px 0 0">'
        f'{"".join(days)}</div>',
        unsafe_allow_html=True,
    )
