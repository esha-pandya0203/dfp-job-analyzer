import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os 
import plotly.graph_objects as go
import plotly.express as px


def show_overview(job_data, bls_data, bls_dict):
    """Show overview dashboard"""
    st.header("📈 United States Employment Overview")
    
    if 'employment_level' in bls_data and 'unemployment_level' in bls_data:
    # Merge datasets on Date
        merged = pd.merge(
            bls_data['employment_level'][['Date', 'employment_level']],
            bls_data['unemployment_level'][['Date', 'unemployment_level']],
            on='Date',
            how='inner'
        ).sort_values('Date')

        st.sidebar.header("Filters")
        start_date, end_date = st.sidebar.slider(
            "Select Date Range:",
            min_value=merged['Date'].min().to_pydatetime(),
            max_value=merged['Date'].max().to_pydatetime(),
            value=(merged['Date'].min().to_pydatetime(), merged['Date'].max().to_pydatetime())
        )

        filtered = merged[(merged['Date'] >= start_date) & (merged['Date'] <= end_date)]

        st.subheader("📊 Employment vs Unemployment Over Time")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(filtered['Date'], filtered['employment_level'], label='Employment Level', linewidth=2)
        ax.plot(filtered['Date'], filtered['unemployment_level'], label='Unemployment Level', linewidth=2, color='red')
        ax.set_title("US Employment vs Unemployment Levels")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of People (in thousands)")
        ax.legend()
        st.pyplot(fig)

    else:
        st.error("Missing employment or unemployment data files.")

    # Load projections dataset
    projections_path = os.path.join("data/raw_data", "employment_projections_tech.csv")
    if os.path.exists(projections_path):
        print("employment projects")
        projections_df = pd.read_csv(projections_path)
        projections_df.columns = projections_df.columns.str.strip()

        # Select only relevant columns
        cols = [
            "Occupation Title",
            "2024 Percent of Occupation",
            "Projected 2034 Percent of Occupation",
            "2024 Percent of Industry",
            "Projected 2034 Percent of Industry",
        ]
        df_proj = projections_df[cols].copy()

        # Option to choose which metric to visualize
        st.subheader("💼 Tech Employment Projections (2024 vs. 2034)")

        metric = st.radio(
            "Select Comparison Metric:",
            options=[
                "Percent of Occupation",
                "Percent of Industry"
            ],
            index=0
        )

        # Rename columns dynamically based on selected metric
        if metric == "Percent of Occupation":
            col_2024 = "2024 Percent of Occupation"
            col_2034 = "Projected 2034 Percent of Occupation"
        else:
            col_2024 = "2024 Percent of Industry"
            col_2034 = "Projected 2034 Percent of Industry"

        # Keep top 10 or so to keep it readable
        top_df = df_proj.nlargest(10, col_2034)

        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(
                name='2024',
                x=top_df["Occupation Title"],
                y=top_df[col_2024],
                marker_color='steelblue'
            ),
            go.Bar(
                name='2034 (Projected)',
                x=top_df["Occupation Title"],
                y=top_df[col_2034],
                marker_color='orange'
            )
        ])

        fig.update_layout(
            barmode='group',
            title=f"Tech Occupations — 2024 vs 2034 {metric}",
            xaxis_title="Occupation Title",
            yaxis_title=f"{metric} (%)",
            xaxis_tickangle=-45,
            legend_title="Year",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Projections file not found: employment_projections_tech.csv")

    #SKILLS 

    if not job_data.empty and 'code' in job_data.columns:
        most_common_code = job_data['code'].mode().iloc[0] if not job_data['code'].mode().empty else '15-0000'
        category_name = bls_dict.get(most_common_code, 'Computer Occupations')
        st.subheader(f"🛠️ Skills Trends for {category_name}")
    else:
        st.subheader("🛠️ Skills Trends for Computer Occupations")
        
    all_skills = []
    for skills in job_data['skills']:
        if isinstance(skills, list):
            all_skills.extend(skills)
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().head(10)
        fig = px.bar(
            x=skill_counts.values,
            y=skill_counts.index,
            orientation='h',
            title="Top Skills in Computer Occupations",
            labels={'x': 'Frequency', 'y': 'Skills'}
        )
        fig.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Frequency",
            yaxis_title="Skills"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No skills data available")
    
  