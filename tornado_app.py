import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import streamlit_analytics2 as analytics # New Import

# --- PAGE SETUP ---
st.set_page_config(page_title="Race Vert Comparison by mkUltra.run", layout="wide")

# --- ANALYTICS WRAPPER ---
# This starts recording everything below it
with analytics.track():
    
    # --- SIDEBAR ---
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=200)

    view_mode = st.sidebar.radio(
        "Select Comparison Metric:",
        ["Distance (km)", "Percentage (%) of total race"]
    )

    st.markdown("<h1 style='text-align: center;'>Race Vert Comparison by mkUltra.run</h1>", unsafe_allow_html=True)

    # --- DATA LOADING HIERARCHY ---
    DATA_FOLDER = "race_data"

    def get_race_hierarchy(root_path):
        hierarchy = {}
        if os.path.exists(root_path):
            races = sorted([d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))])
            for race in races:
                race_path = os.path.join(root_path, race)
                files = sorted([f.replace('.csv', '') for f in os.listdir(race_path) if f.endswith('.csv')])
                if files:
                    hierarchy[race] = [" "] + files
        return hierarchy

    race_dict = get_race_hierarchy(DATA_FOLDER)

    if not race_dict:
        st.info("Please organize your 'race_data' folder into subfolders.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Race A")
            selected_event_a = st.selectbox("Select Event", [" "] + list(race_dict.keys()), key="race_a_event")
            selected_year_dist_a = " "
            if selected_event_a != " ":
                selected_year_dist_a = st.selectbox("Select Year and Distance", race_dict[selected_event_a], key="year_a")

        with col2:
            st.markdown("### Race B")
            selected_event_b = st.selectbox("Select Event", [" "] + list(race_dict.keys()), key="race_b_event")
            selected_year_dist_b = " "
            if selected_event_b != " ":
                selected_year_dist_b = st.selectbox("Select Year and Distance", race_dict[selected_event_b], key="year_b")

        if selected_year_dist_a != " " and selected_year_dist_b != " ":
            # [Plotly logic remains exactly the same as the previous version]
            # ... (omitted for brevity, keep your finalized chart code here)
            
            # Ensure the chart uses the new width parameter:
            st.plotly_chart(fig, width="stretch")
        else:
            st.write("---")
            st.info("Please select both an Event and a Year/Distance to view the comparison.")

# --- END OF ANALYTICS WRAPPER ---