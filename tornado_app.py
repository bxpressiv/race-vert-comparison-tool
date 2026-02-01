import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import streamlit_analytics2 as analytics

# --- PAGE SETUP ---
st.set_page_config(page_title="Race Vert Comparison by mkUltra.run", layout="wide")

analytics_password = st.secrets.get("analytics", {}).get("password", "")

with analytics.track(unsafe_password=analytics_password):
    
    # --- LOGO & TITLE ---
    if os.path.exists("logo.png"):
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image("logo.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>Race Vert Comparison by mkUltra.run</h1>", unsafe_allow_html=True)
    st.write("") 

    DATA_FOLDER = "race_data"

    def get_race_hierarchy(root_path):
        hierarchy = {}
        if os.path.exists(root_path):
            races = sorted([d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))])
            for race in races:
                race_path = os.path.join(root_path, race)
                files = sorted([f.replace('.csv', '') for f in os.listdir(race_path) if f.endswith('.csv')])
                if files:
                    hierarchy[race] = files
        return hierarchy

    race_dict = get_race_hierarchy(DATA_FOLDER)

    if not race_dict:
        st.info("Please organize your 'race_data' folder.")
    else:
        # --- RACE SELECTIONS ---
        st.markdown("### 🏃 Select Races")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Race A")
            # Standardization: ensuring key and help match the 'working' version
            sel_event_a = st.selectbox("Event", [" "] + list(race_dict.keys()), key="a_event", help="Type to search")
            sel_year_a = " "
            if sel_event_a != " ":
                sel_year_a = st.selectbox("Year/Distance", [" "] + race_dict[sel_event_a], key="a_year")

        with col2:
            st.markdown("#### Race B")
            # FIX: Applying the exact same search logic and help text to Box B
            sel_event_b = st.selectbox("Event", [" "] + list(race_dict.keys()), key="b_event", help="Type to search")
            sel_year_b = " "
            if sel_event_b != " ":
                sel_year_b = st.selectbox("Year/Distance", [" "] + race_dict[sel_event_b], key="b_year")

        st.write("---")

        # --- DATA & CHARTING ---
        if sel_year_a != " " and sel_year_b != " ":
            
            # --- CENTRED RADIO BUTTONS (Above Graph) ---
            col_v1, col_v2, col_v3 = st.columns([1, 1, 1])
            with col_v2:
                view_mode = st.radio(
                    "Select Comparison Metric:",
                    ["Distance (km)", "Percentage (%)"],
                    horizontal=True,
                    label_visibility="visible"
                )

            path_a = os.path.join(DATA_FOLDER, sel_event_a, f"{sel_year_a}.csv")
            path_b = os.path.join(DATA_FOLDER, sel_event_b, f"{sel_year_b}.csv")

            df_l = pd.read_csv(path_a)
            df_r = pd.read_csv(path_b)
            
            for df in [df_l, df_r]:
                df.columns = df.columns.str.strip()
            df_l = df_l.sort_values('sort', ascending=True)
            df_r = df_r.sort_values('sort', ascending=True)

            y_col = 'Bin'          
            x_col = 'Distance_km' if view_mode == "Distance (km)" else 'Percentage' # Ensure internal logic matches toggle
            unit = "km" if view_mode == "Distance (km)" else "%"

            merged = pd.merge(df_l[[y_col, x_col]], df_r[[y_col, x_col]], on=y_col, suffixes=('_a', '_b'))
            merged['delta'] = merged[f'{x_col}_b'] - merged[f'{x_col}_a']

            CUSTOM_COLORS = ["#803131", "#d63131", "#e77d31", "#efe331", "#d3d388", "#31d431", "#7fd1af", "#4ee6e6", "#3197e9", "#3b36db", "#682d94"]
            max_val = max(df_l[x_col].max(), df_r[x_col].max())
            axis_range = max_val * 1.7 

            fig = go.Figure()
            
            # Left Bar
            fig.add_trace(go.Bar(
                y=df_l[y_col], x=(df_l[x_col] * -1), orientation='h', 
                marker=dict(color=CUSTOM_COLORS[::-1]), 
                base=- (max_val * 0.01), 
                text=df_l[x_col].apply(lambda x: f"<b>{x:.1f}{unit}</b>" if x > 0 else ""), 
                textposition='outside', cliponaxis=False
            ))
            # Right Bar
            fig.add_trace(go.Bar(
                y=df_r[y_col], x=df_r[x_col], orientation='h', 
                marker=dict(color=CUSTOM_COLORS[::-1]), 
                base=(max_val * 0.01), 
                text=df_r[x_col].apply(lambda x: f"<b>{x:.1f}{unit}</b>" if x > 0 else ""), 
                textposition='outside', cliponaxis=False
            ))

            # Differences
            for i, row in merged.iterrows():
                d_val = row['delta']
                color = "black" if abs(d_val) <= 1.0 else ("#d63131" if d_val > 0 else "#3197e9")
                prefix = "+" if d_val > 0 else ""
                fig.add_annotation(x=axis_range * 0.88, y=row[y_col], text=f"<b>{prefix}{d_val:.1f}{unit}</b>", showarrow=False, xanchor="right", font=dict(color=color, size=12))

            fig.add_annotation(x=axis_range * 0.88, y=1.08, xref="x", yref="paper", text="<b>Race B has:</b>", showarrow=False, xanchor="right", font=dict(size=13))

            fig.update_layout(barmode='relative', bargap=0.15, showlegend=False, xaxis=dict(range=[-axis_range * 0.8, axis_range], showticklabels=False, showgrid=False, zeroline=False, fixedrange=True), yaxis=dict(title="", tickfont=dict(size=11), fixedrange=True), margin=dict(l=10, r=80, t=100, b=50), height=850, template="plotly_white")

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
