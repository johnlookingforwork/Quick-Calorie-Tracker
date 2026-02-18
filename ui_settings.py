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

    st.divider()

    # --- Saved Foods ---
    st.subheader("Saved Foods")

    # Add new saved food
    with st.expander("Add New Saved Food"):
        with st.form("add_saved_food_form", clear_on_submit=True):
            name = st.text_input("Food Name")
            c1, c2 = st.columns(2)
            with c1:
                serving_size = st.number_input("Serving Size", min_value=0.1, value=1.0, step=0.5)
                unit = st.text_input("Unit", value="serving")
                calories = st.number_input("Calories (kcal)", min_value=0.0, value=None, step=10.0, placeholder="0")
            with c2:
                protein = st.number_input("Protein (g)", min_value=0.0, value=None, step=1.0, placeholder="0")
                carbs = st.number_input("Carbs (g)", min_value=0.0, value=None, step=1.0, placeholder="0")
                fat = st.number_input("Fat (g)", min_value=0.0, value=None, step=1.0, placeholder="0")
            submitted = st.form_submit_button("Add Food", type="primary")
            if submitted and name:
                db.add_saved_food(name, serving_size, unit, calories or 0, protein or 0, carbs or 0, fat or 0)
                st.rerun()

    # List saved foods
    foods = db.get_saved_foods()
    if not foods:
        st.info("No saved foods yet. Add one above!")
    else:
        for food in foods:
            with st.expander(f"{food['name']} — {food['calories']:g} kcal per {food['serving_size']:g} {food['unit']}"):
                with st.form(f"edit_food_{food['id']}", clear_on_submit=False):
                    name = st.text_input("Name", value=food["name"], key=f"ef_name_{food['id']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        serving_size = st.number_input("Serving Size", min_value=0.1, value=float(food["serving_size"]), step=0.5, key=f"ef_ss_{food['id']}")
                        unit = st.text_input("Unit", value=food["unit"], key=f"ef_unit_{food['id']}")
                        calories = st.number_input("Calories", min_value=0.0, value=float(food["calories"]), step=10.0, key=f"ef_cal_{food['id']}")
                    with c2:
                        protein = st.number_input("Protein (g)", min_value=0.0, value=float(food["protein"]), step=1.0, key=f"ef_pro_{food['id']}")
                        carbs = st.number_input("Carbs (g)", min_value=0.0, value=float(food["carbs"]), step=1.0, key=f"ef_carb_{food['id']}")
                        fat = st.number_input("Fat (g)", min_value=0.0, value=float(food["fat"]), step=1.0, key=f"ef_fat_{food['id']}")
                    c_save, c_del = st.columns(2)
                    with c_save:
                        if st.form_submit_button("Update"):
                            db.update_saved_food(food["id"], name, serving_size, unit, calories, protein, carbs, fat)
                            st.rerun()
                    with c_del:
                        if st.form_submit_button("Delete", type="secondary"):
                            db.delete_saved_food(food["id"])
                            st.rerun()
