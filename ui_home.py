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


def _svg_ring(pct: float, color: str, size: int, stroke: float) -> str:
    """Return an SVG donut ring."""
    return (
        f'<svg viewBox="0 0 36 36" width="{size}" height="{size}" style="transform:rotate(-90deg)">'
        f'<circle cx="18" cy="18" r="14" fill="none" stroke="#E8E8E8" stroke-width="{stroke}"/>'
        f'<circle cx="18" cy="18" r="14" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-dasharray="{pct * 0.88:.1f} 88" stroke-linecap="round"/></svg>'
    )


def render():
    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")

    cal_goal = int(db.get_setting("daily_calorie_goal"))
    protein_goal = int(db.get_setting("protein_goal"))
    carbs_goal = int(db.get_setting("carbs_goal"))
    fat_goal = int(db.get_setting("fat_goal"))

    # --- Clickable week day strip ---
    week_start = today_dt - timedelta(days=(today_dt.weekday() + 1) % 7)  # Sunday
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    date_labels = {f"{d.strftime('%a')[0]}  {d.day}": d.strftime("%Y-%m-%d") for d in week_dates}
    today_label = next(k for k, v in date_labels.items() if v == today)

    if "selected_date" not in st.session_state:
        st.session_state.selected_date = today

    selected_label = st.segmented_control(
        "week",
        options=list(date_labels.keys()),
        default=next((k for k, v in date_labels.items() if v == st.session_state.selected_date), today_label),
        label_visibility="collapsed",
        key="week_picker",
    )

    if selected_label:
        st.session_state.selected_date = date_labels[selected_label]

    sel_date = st.session_state.selected_date
    summary = db.get_daily_summary(sel_date)

    net_calories = summary["calories"] - summary["burned"]
    remaining = cal_goal - net_calories

    protein_val = summary["protein"]
    carbs_val = summary["carbs"]
    fat_val = summary["fat"]

    protein_left = max(protein_goal - protein_val, 0)
    carbs_left = max(carbs_goal - carbs_val, 0)
    fat_left = max(fat_goal - fat_val, 0)

    cal_pct = _pct(net_calories, cal_goal)
    p_pct = _pct(protein_val, protein_goal)
    c_pct = _pct(carbs_val, carbs_goal)
    f_pct = _pct(fat_val, fat_goal)

    cal_color = "#222" if remaining >= 0 else "#FF6B6B"

    # --- Summary card ---
    cal_ring = _svg_ring(cal_pct, cal_color, 64, 3.5)
    p_ring = _svg_ring(p_pct, "#FF6B6B", 44, 4)
    c_ring = _svg_ring(c_pct, "#4ECDC4", 44, 4)
    f_ring = _svg_ring(f_pct, "#FFD93D", 44, 4)

    card_html = (
        '<div style="background:#F7F7F7;border-radius:20px;padding:24px 20px 20px;margin:4px 0 12px">'
        # Calorie row
        '<div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:18px">'
        f'<div>{cal_ring}</div>'
        '<div style="text-align:left">'
        f'<div style="font-size:2.4rem;font-weight:700;color:{cal_color};line-height:1">{_fmt(abs(remaining))}</div>'
        f'<div style="font-size:0.8rem;color:#999">Calories {"left" if remaining >= 0 else "over"}</div>'
        '</div></div>'
        # Macro row
        '<div style="display:flex;justify-content:space-around;text-align:center">'
        # Protein
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'{p_ring}'
        f'<div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(protein_left)}g</div>'
        f'<div style="font-size:0.65rem;color:#999">Protein left</div></div>'
        # Carbs
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'{c_ring}'
        f'<div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(carbs_left)}g</div>'
        f'<div style="font-size:0.65rem;color:#999">Carbs left</div></div>'
        # Fat
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'{f_ring}'
        f'<div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(fat_left)}g</div>'
        f'<div style="font-size:0.65rem;color:#999">Fat left</div></div>'
        '</div></div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    # --- Day's Log ---
    if sel_date == today:
        st.subheader("Recently logged")
    else:
        sel_dt = datetime.strptime(sel_date, "%Y-%m-%d")
        st.subheader(f"{sel_dt.strftime('%A, %b %d')}")

    food_entries = db.get_food_log(sel_date)
    workout_entries = db.get_workouts(sel_date)

    if not food_entries and not workout_entries:
        st.caption("Nothing logged yet." if sel_date == today else "No entries for this day.")
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
