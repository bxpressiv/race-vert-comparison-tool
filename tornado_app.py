import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import streamlit_analytics2 as analytics

# --- PAGE SETUP ---
st.set_page_config(page_title="Race Vert Comparison by mkUltra.run", layout="wide")

with analytics.track():
    # --- LOGO & TITLE ---
    if os.path.exists("logo.png"):
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image("logo.png", use_container_width=True)

    # Restored the full title here
    st.markdown("<h1 style='text-align: center;'>Race Vert Comparison by mkUltra.run</h1>", unsafe_allow_html=True)
    
    # --- VIEW TOGGLE ---
    view_mode = st.radio(
        "Select Comparison Metric:",
        ["Distance (km)", "Percentage (%) of total race"],
        horizontal=True
    )
    st.write("---")

    # --- DATA LOADING ---
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
            path_a = os.path.join(DATA_FOLDER, selected_event_a, f"{selected_year_dist_a}.csv")
            path_b = os.path.join(DATA_FOLDER, selected_event_b, f"{selected_year_dist_b}.csv")

            df_l = pd.read_csv(path_a)
            df_r = pd.read_csv(path_b)
            
            for df in [df_l, df_r]:
                df.columns = df.columns.str.strip()
            df_l = df_l.sort_values('sort', ascending=True)
            df_r = df_r.sort_values('sort', ascending=True)

            y_col = 'Bin'          
            x_col = 'Distance_km' if view_mode == "Distance (km)" else 'Perc'
            unit = "km" if view_mode == "Distance (km)" else "%"

            merged = pd.merge(df_l[[y_col, x_col]], df_r[[y_col, x_col]], on=y_col, suffixes=('_a', '_b'))
            merged['delta'] = merged[f'{x_col}_b'] - merged[f'{x_col}_a']

            CUSTOM_COLORS = ["#803131", "#d63131", "#e77d31", "#efe331", "#d3d388", "#31d431", "#7fd1af", "#4ee6e6", "#3197e9", "#3b36db", "#682d94"]
            max_val = max(df_l[x_col].max(), df_r[x_col].max())
            gap_size = max_val * 0.013  
            axis_range = max_val * 1.6 

            fig = go.Figure()

            # Left Side
            fig.add_trace(go.Bar(
                y=df_l[y_col], x=(df_l[x_col] * -1), orientation='h',
                marker=dict(color=CUSTOM_COLORS[::-1]), base=-gap_size, 
                text=df_l[x_col].apply(lambda x: f"<b>{x:.1f}{unit}</b>" if x > 0 else ""),
                textposition='outside', cliponaxis=False, showlegend=False,
                hovertemplate="Grade: %{y}<br>Value: %{x|abs:.2f}" + unit + "<extra></extra>"
            ))

            # Right Side
            fig.add_trace(go.Bar(
                y=df_r[y_col], x=df_r[x_col], orientation='h',
                marker=dict(color=CUSTOM_COLORS[::-1]), base=gap_size, 
                text=df_r[x_col].apply(lambda x: f"<b>{x:.1f}{unit}</b>" if x > 0 else ""),
                textposition='outside', cliponaxis=False, showlegend=False,
                hovertemplate="Grade: %{y}<br>Value: %{x:.2f}" + unit + "<extra></extra>"
            ))

            for i, row in merged.iterrows():
                d_val = row['delta']
                color = "black" if abs(d_val) <= 1.0 else ("#d63131" if d_val > 0 else "#3197e9")
                prefix = "+" if d_val > 0 else ""
                fig.add_annotation(
                    x=axis_range * 0.95, y=row[y_col], text=f"<b>{prefix}{d_val:.1f}{unit}</b>",
                    showarrow=False, xanchor="center", font=dict(color=color, size=13, family="Arial Black")
                )

            fig.add_annotation(
                x=axis_range * 0.95, y=1.08, xref="x", yref="paper",
                text="<b>Race B has:</b>", showarrow=False, xanchor="center", font=dict(size=14, family="Arial Black")
            )

            fig.update_layout(
                barmode='relative', bargap=0.15, showlegend=False,
                xaxis=dict(range=[-axis_range, axis_range], showticklabels=False, showgrid=False, zeroline=False, fixedrange=True),
                yaxis=dict(title="", tickfont=dict(family="Arial Black", size=13), fixedrange=True),
                margin=dict(l=10, r=10, t=100, b=50), height=850, template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select both an Event and a Year/Distance to view the comparison.")
