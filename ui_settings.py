import streamlit as st
import db


def render():
    st.header("Settings")

    # --- Calorie & Macro Goals ---
    st.subheader("Daily Goals")
    col1, col2 = st.columns(2)
    with col1:
        cal_goal = st.number_input(
            "Calorie Goal (kcal)",
            min_value=500,
            max_value=10000,
            value=int(db.get_setting("daily_calorie_goal")),
            step=50,
            key="settings_cal_goal",
        )
        protein_goal = st.number_input(
            "Protein Goal (g)",
            min_value=0,
            max_value=500,
            value=int(db.get_setting("protein_goal")),
            step=5,
            key="settings_protein_goal",
        )
    with col2:
        carbs_goal = st.number_input(
            "Carbs Goal (g)",
            min_value=0,
            max_value=1000,
            value=int(db.get_setting("carbs_goal")),
            step=5,
            key="settings_carbs_goal",
        )
        fat_goal = st.number_input(
            "Fat Goal (g)",
            min_value=0,
            max_value=500,
            value=int(db.get_setting("fat_goal")),
            step=5,
            key="settings_fat_goal",
        )

    if st.button("Save Goals", type="primary"):
        db.set_setting("daily_calorie_goal", str(cal_goal))
        db.set_setting("protein_goal", str(protein_goal))
        db.set_setting("carbs_goal", str(carbs_goal))
        db.set_setting("fat_goal", str(fat_goal))
        st.success("Goals saved!")
