from datetime import datetime

import streamlit as st
import db
import ai


@st.dialog("Log Entry", width="large")
def show():
    tab_ai, tab_saved, tab_workout = st.tabs(["AI Log", "Saved Foods", "Workout"])

    with tab_ai:
        _ai_tab()

    with tab_saved:
        _saved_foods_tab()

    with tab_workout:
        _workout_tab()


def _ai_tab():
    description = st.text_area("Describe what you ate", placeholder="e.g. 2 eggs, toast with butter, orange juice")

    if st.button("Estimate", type="primary", key="ai_estimate_btn"):
        if not description.strip():
            st.warning("Please describe your food first.")
            return
        try:
            with st.spinner("Estimating with AI..."):
                result = ai.estimate_macros(description)
            st.session_state["ai_estimate"] = result
        except Exception as e:
            st.error(f"AI estimation failed: {e}")
            return

    if "ai_estimate" in st.session_state:
        est = st.session_state["ai_estimate"]
        st.subheader(est["name"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{est['calories']:.0f}")
        c2.metric("Protein", f"{est['protein']:.0f}g")
        c3.metric("Carbs", f"{est['carbs']:.0f}g")
        c4.metric("Fat", f"{est['fat']:.0f}g")

        if st.button("Confirm & Log", type="primary", key="ai_confirm_btn"):
            today = datetime.now().strftime("%Y-%m-%d")
            now = datetime.now().strftime("%H:%M")
            db.add_food_log(today, now, est["name"], est["calories"], est["protein"], est["carbs"], est["fat"], source="ai")
            del st.session_state["ai_estimate"]
            st.rerun()


def _saved_foods_tab():
    foods = db.get_saved_foods()
    if not foods:
        st.info("No saved foods. Add some in Settings!")
        return

    food_names = [f["name"] for f in foods]
    selected_name = st.selectbox("Select a saved food", food_names, key="saved_food_select")
    selected = next(f for f in foods if f["name"] == selected_name)

    servings = st.number_input(
        f"Number of servings ({selected['serving_size']:.1f} {selected['unit']} each)",
        min_value=0.25,
        value=1.0,
        step=0.25,
        key="saved_food_servings",
    )

    multiplier = servings
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", f"{selected['calories'] * multiplier:.0f}")
    c2.metric("Protein", f"{selected['protein'] * multiplier:.0f}g")
    c3.metric("Carbs", f"{selected['carbs'] * multiplier:.0f}g")
    c4.metric("Fat", f"{selected['fat'] * multiplier:.0f}g")

    if st.button("Log Food", type="primary", key="saved_log_btn"):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M")
        db.add_food_log(
            today, now,
            f"{selected['name']} x{servings:.1f}",
            selected["calories"] * multiplier,
            selected["protein"] * multiplier,
            selected["carbs"] * multiplier,
            selected["fat"] * multiplier,
            source="saved",
        )
        st.rerun()


def _workout_tab():
    with st.form("workout_form", clear_on_submit=True):
        name = st.text_input("Exercise name", placeholder="e.g. Running, Weight training")
        calories_burned = st.number_input("Calories burned", min_value=0.0, value=0.0, step=25.0)
        submitted = st.form_submit_button("Log Workout", type="primary")
        if submitted and name:
            today = datetime.now().strftime("%Y-%m-%d")
            db.add_workout(today, name, calories_burned)
            st.rerun()
