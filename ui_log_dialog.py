from datetime import datetime

import streamlit as st
import db
import ai


def _fmt(n: float) -> str:
    return f"{n:g}"


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
        c1.metric("Calories", _fmt(est['calories']))
        c2.metric("Protein", f"{_fmt(est['protein'])}g")
        c3.metric("Carbs", f"{_fmt(est['carbs'])}g")
        c4.metric("Fat", f"{_fmt(est['fat'])}g")

        if st.button("Confirm & Log", type="primary", key="ai_confirm_btn"):
            today = datetime.now().strftime("%Y-%m-%d")
            now = datetime.now().strftime("%H:%M")
            db.add_food_log(today, now, est["name"], est["calories"], est["protein"], est["carbs"], est["fat"], source="ai")
            del st.session_state["ai_estimate"]
            st.rerun()


def _saved_foods_tab():
    foods = db.get_saved_foods()

    if foods:
        food_names = [f["name"] for f in foods]
        selected_name = st.selectbox("Select a saved food", food_names, key="saved_food_select")
        selected = next(f for f in foods if f["name"] == selected_name)

        servings = st.number_input(
            f"Number of servings ({_fmt(selected['serving_size'])} {selected['unit']} each)",
            min_value=0.25,
            value=1.0,
            step=0.25,
            key="saved_food_servings",
        )

        multiplier = servings
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", _fmt(selected['calories'] * multiplier))
        c2.metric("Protein", f"{_fmt(selected['protein'] * multiplier)}g")
        c3.metric("Carbs", f"{_fmt(selected['carbs'] * multiplier)}g")
        c4.metric("Fat", f"{_fmt(selected['fat'] * multiplier)}g")

        if st.button("Log Food", type="primary", key="saved_log_btn"):
            today = datetime.now().strftime("%Y-%m-%d")
            now = datetime.now().strftime("%H:%M")
            db.add_food_log(
                today, now,
                f"{selected['name']} x{_fmt(servings)}",
                selected["calories"] * multiplier,
                selected["protein"] * multiplier,
                selected["carbs"] * multiplier,
                selected["fat"] * multiplier,
                source="saved",
            )
            st.rerun()
    else:
        st.info("No saved foods yet. Create one below!")

    # --- Add new saved food inline ---
    with st.expander("Create New Saved Food"):
        with st.form("dialog_add_saved_food", clear_on_submit=True):
            name = st.text_input("Food Name")
            serving_size = st.number_input("Serving Size", min_value=0.1, value=1.0, step=0.5, key="dlg_sf_ss")
            unit = st.text_input("Unit", value="serving", key="dlg_sf_unit")
            calories = st.number_input("Calories (kcal)", min_value=0.0, value=0.0, step=10.0, key="dlg_sf_cal")
            protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=1.0, key="dlg_sf_pro")
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0, step=1.0, key="dlg_sf_carb")
            fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=1.0, key="dlg_sf_fat")
            if st.form_submit_button("Save Food", type="primary") and name:
                db.add_saved_food(name, serving_size, unit, calories, protein, carbs, fat)
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
