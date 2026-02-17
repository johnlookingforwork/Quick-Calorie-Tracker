# Quick Calorie Tracker

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quick-calorie-tracker-ravfpsjxqxqrxqygtfbfae.streamlit.app/)

**[Live Demo](https://quick-calorie-tracker-ravfpsjxqxqrxqygtfbfae.streamlit.app/)**

A high-velocity, AI-powered calorie and macro tracking application built with Streamlit. Designed for users who want to log meals in seconds using natural language or a personalized library of saved foods.

## Key Features

- **GPT-4 Magic**: Describe your meal in plain English (e.g., "Two slices of avocado toast and a poached egg") and let AI estimate the macros and calories instantly.
- **Smart Saved Foods**: Build a custom library. Log meals by entering servings (e.g., 1.5 servings) and the app automatically scales the calories/macros.
- **Visual Momentum**:
  - *7-Day Streak*: Red/Yellow/Green status circles to visualize your consistency.
  - *Macro Donut*: Real-time breakdown of Protein, Carbs, and Fats.
- **Workout Offset**: Log exercise to automatically increase your remaining caloric allowance for the day.
- **Privacy First**: Data is stored locally on your device. No account creation required.
- **Calendar View**: Review your caloric history and trends over previous weeks.
- **Data Portability**: Export your entire history to a CSV file at any time.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend/Backend | Streamlit |
| AI Engine | OpenAI GPT-4o |
| Data Visualization | Plotly / Altair |
| Storage | SQLite / Local Browser Cache |
| Language | Python 3.9+ |

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/johnlookingforwork/quick-calorie-tracker.git
   cd quick-calorie-tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_sk_key_here
   DAILY_CALORIE_GOAL=2500
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## UI Structure

- **Home**: View your daily "Big Number" (Remaining Calories), 7-day momentum circles, and macro donut chart.
- **Navigation**: A footer-based navigation system to switch between Home, Calendar, and Settings.
- **The Log Button [+]**: A dedicated action button to quickly trigger AI estimation, Saved Food logging, or Workout entry.

## Data Logic

The app calculates your daily status using the following formula:

$$Remaining = Daily\ Goal - Consumed\ Calories + Exercise\ Burned$$

For saved foods, the calculation scales linearly:

$$Adjusted\ Macro = Base\ Macro \times Servings\ Input$$
