from datetime import datetime, timedelta

import streamlit as st
import db

NUM_DAYS = 14


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


def _date_circle_color(net_cals: float | None, goal: int) -> str:
    """Return border/ring color based on calorie goal progress.

    None = no data (gray donut outline)
    >= 100% goal met = green
    >= 75% almost met = orange
    < 75% = red
    """
    if net_cals is None:
        return "#E0E0E0"
    pct = net_cals / goal if goal > 0 else 0
    if pct >= 1.0:
        return "#FF6B6B"  # over goal — red
    if pct >= 0.75:
        return "#FFB347"  # almost — orange
    if pct > 0:
        return "#4ECDC4"  # under goal, some data — green/teal
    return "#E0E0E0"  # zero


def render():
    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")

    cal_goal = int(db.get_setting("daily_calorie_goal"))
    protein_goal = int(db.get_setting("protein_goal"))
    carbs_goal = int(db.get_setting("carbs_goal"))
    fat_goal = int(db.get_setting("fat_goal"))

    if "selected_date" not in st.session_state:
        st.session_state.selected_date = today

    # --- Date strip: last NUM_DAYS days ---
    strip_dates = [today_dt - timedelta(days=NUM_DAYS - 1 - i) for i in range(NUM_DAYS)]
    strip_strs = [d.strftime("%Y-%m-%d") for d in strip_dates]

    # Get calorie data for all dates in one query
    net_map = db.get_net_calories_range(strip_strs[0], strip_strs[-1])

    sel_date = st.session_state.selected_date

    # Build scrollable circle strip
    circles = []
    for d in strip_dates:
        d_str = d.strftime("%Y-%m-%d")
        letter = d.strftime("%a")[0]
        num = d.day
        is_sel = d_str == sel_date
        net = net_map.get(d_str)
        ring_color = _date_circle_color(net, cal_goal)

        if is_sel:
            # Selected: solid dark background
            circles.append(
                f'<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0">'
                f'<span style="font-size:0.6rem;color:#999;margin-bottom:2px">{letter}</span>'
                f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:32px;height:32px;border-radius:50%;background:#222;color:#fff;'
                f'font-size:0.75rem;font-weight:600">{num}</span></div>'
            )
        elif net is not None:
            # Has data: colored ring around number
            circles.append(
                f'<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0">'
                f'<span style="font-size:0.6rem;color:#999;margin-bottom:2px">{letter}</span>'
                f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:32px;height:32px;border-radius:50%;'
                f'border:2.5px solid {ring_color};'
                f'font-size:0.75rem;color:#444;font-weight:500">{num}</span></div>'
            )
        else:
            # No data: plain number, faint donut outline
            circles.append(
                f'<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0">'
                f'<span style="font-size:0.6rem;color:#999;margin-bottom:2px">{letter}</span>'
                f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:32px;height:32px;border-radius:50%;'
                f'border:2px dashed #E0E0E0;'
                f'font-size:0.75rem;color:#BBB">{num}</span></div>'
            )

    st.markdown(
        '<div style="display:flex;gap:6px;overflow-x:auto;padding:4px 0;'
        '-webkit-overflow-scrolling:touch;scrollbar-width:none">'
        f'{"".join(circles)}</div>',
        unsafe_allow_html=True,
    )

    # Date picker (compact select)
    st.markdown(
        '<style>'
        '.st-key-date_sel {margin-top:-4px;}'
        '.st-key-date_sel [data-baseweb="select"] {max-height:30px;min-height:30px;font-size:0.75rem;}'
        '.st-key-date_sel [data-baseweb="select"] > div {padding:2px 8px;min-height:30px;}'
        '</style>',
        unsafe_allow_html=True,
    )
    with st.container(key="date_sel"):
        day_labels = [f"{d.strftime('%a, %b %d')}" for d in strip_dates]
        sel_idx = strip_strs.index(sel_date) if sel_date in strip_strs else len(strip_strs) - 1
        picked = st.selectbox("Date", day_labels, index=sel_idx, label_visibility="collapsed", key="date_picker")
        if picked:
            new_date = strip_strs[day_labels.index(picked)]
            if new_date != sel_date:
                st.session_state.selected_date = new_date
                st.rerun()

    # --- Summary card ---
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

    cal_ring = _svg_ring(cal_pct, cal_color, 64, 3.5)
    p_ring = _svg_ring(p_pct, "#FF6B6B", 44, 4)
    c_ring = _svg_ring(c_pct, "#4ECDC4", 44, 4)
    f_ring = _svg_ring(f_pct, "#FFD93D", 44, 4)

    card_html = (
        '<div style="background:#F7F7F7;border-radius:20px;padding:24px 20px 20px;margin:4px 0 12px">'
        '<div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:18px">'
        f'<div>{cal_ring}</div>'
        '<div style="text-align:left">'
        f'<div style="font-size:2.4rem;font-weight:700;color:{cal_color};line-height:1">{_fmt(abs(remaining))}</div>'
        f'<div style="font-size:0.8rem;color:#999">Calories {"left" if remaining >= 0 else "over"}</div>'
        '</div></div>'
        '<div style="display:flex;justify-content:space-around;text-align:center">'
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'{p_ring}'
        f'<div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(protein_left)}g</div>'
        f'<div style="font-size:0.65rem;color:#999">Protein left</div></div>'
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'{c_ring}'
        f'<div style="font-size:0.85rem;font-weight:600;margin-top:4px">{_fmt(carbs_left)}g</div>'
        f'<div style="font-size:0.65rem;color:#999">Carbs left</div></div>'
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
