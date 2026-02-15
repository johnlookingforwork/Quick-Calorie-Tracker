from datetime import datetime

import streamlit as st
import db


def _fmt(n: float) -> str:
    return f"{n:g}"


def render():
    st.header("Calendar")

    selected_date = st.date_input("Select a date", value=datetime.now().date(), key="calendar_date")
    date_str = selected_date.strftime("%Y-%m-%d")

    # Day summary
    summary = db.get_daily_summary(date_str)
    cal_goal = int(db.get_setting("daily_calorie_goal"))
    net = summary["calories"] - summary["burned"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eaten", _fmt(summary['calories']))
    c2.metric("Burned", _fmt(summary['burned']))
    c3.metric("Net", _fmt(net))
    c4.metric("Goal", _fmt(cal_goal))

    st.divider()

    # Food entries
    food_entries = db.get_food_log(date_str)
    workout_entries = db.get_workouts(date_str)

    if not food_entries and not workout_entries:
        st.info(f"No entries for {selected_date.strftime('%B %d, %Y')}")
    else:
        if food_entries:
            st.subheader("Food")
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
                    if st.button("🗑️", key=f"cal_del_food_{entry['id']}", help="Delete"):
                        db.delete_food_log(entry["id"])
                        st.rerun()

        if workout_entries:
            st.subheader("Workouts")
            for entry in workout_entries:
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"🏋️ **{entry['name']}** — -{_fmt(entry['calories_burned'])} kcal")
                with col_del:
                    if st.button("🗑️", key=f"cal_del_workout_{entry['id']}", help="Delete"):
                        db.delete_workout(entry["id"])
                        st.rerun()

    st.divider()

    # CSV Export
    st.subheader("Export Data")
    df = db.export_all_logs()
    if df.empty:
        st.info("No data to export yet.")
    else:
        csv = df.to_csv(index=False)
        st.download_button(
            "Download All Logs (CSV)",
            data=csv,
            file_name="calorie_tracker_export.csv",
            mime="text/csv",
            type="primary",
        )
