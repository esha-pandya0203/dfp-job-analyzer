import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os 
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
from utils.job_title_mapping import BLS_SOC_MAPPING

def show_overview(job_data, bls_data, onet_data=None):
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
    if not job_data.empty and 'soc_code' in job_data.columns:
        category_name = BLS_SOC_MAPPING[job_data['soc_code'].iloc[0]]['soc_title']
        st.subheader(f"🛠️ Skills Trends for {category_name}")
    else:
        st.subheader("🛠️ Skills Trends for Computer Occupations")
        
    # Priority: Use ONet technical skills if available, otherwise fall back to job data
    all_skills = []
    
    if onet_data is not None and not onet_data.empty:
        # Extract technical skills from ONet data
        st.info("📊 Using O*NET Technical Skills Data")
        
        # Debug: Show ONet data info
        
        # Look for technical skills in ONet data
        for _, row in onet_data.iterrows():
            # Check if row has technical skills data
            if 'technology_skills' in row and pd.notna(row['technology_skills']):
                skills_str = str(row['technology_skills'])
                
                try:
                    # Parse technical skills (assuming it's stored as a string representation of a list)
                    import ast
                    
                    # Clean the string - remove extra quotes if present
                    cleaned_str = skills_str.strip()
                    if cleaned_str.startswith('"') and cleaned_str.endswith('"'):
                        cleaned_str = cleaned_str[1:-1]
                    
                    skills = ast.literal_eval(cleaned_str)
                    if isinstance(skills, list):
                        skill_list = [skill.strip() for skill in skills if skill.strip()]
                        all_skills.extend(skill_list)
                except Exception as e:
                    # If parsing fails, try extracting skills using regex
                    import re
                    # Extract quoted strings from the skills string
                    skill_matches = re.findall(r"'([^']+)'", skills_str)
                    if skill_matches:
                        all_skills.extend([skill.strip() for skill in skill_matches if skill.strip()])
                    else:
                        # Fallback to simple comma splitting
                        skills = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
                        all_skills.extend(skills)
    else:
        # Fall back to job posting skills
        st.info("📊 Using Job Posting Skills Data")
        if not job_data.empty and 'matched_skills' in job_data.columns:
            for skills in job_data['matched_skills']:
                if isinstance(skills, list):
                    all_skills.extend(skills)
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().head(15)
        
        # Create two columns for side-by-side visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Original bar chart
            fig_bar = px.bar(
                x=skill_counts.values,
                y=skill_counts.index,
                orientation='h',
                title="Top Skills Frequency (Bar Chart)",
                labels={'x': 'Frequency', 'y': 'Skills'},
                color=skill_counts.values,
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Frequency",
                yaxis_title="Skills",
                height=500
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Word Cloud
            st.write("**Skills Word Cloud**")
            
            # Get top 15 most frequent skills to avoid overcrowding
            top_skills = skill_counts.head(15)
            
            # Create word cloud
            try:
                from wordcloud import WordCloud
                import random
                
                # Prepare word cloud data - dictionary of skill names and frequencies
                wordcloud_data = dict(top_skills)
                
                # Define color function - use different hues but maintain same saturation and brightness
                def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                    # Define multiple colors with similar brightness levels
                    colors = [
                        'rgb(46, 134, 171)',   # Blue
                        'rgb(171, 46, 134)',   # Magenta
                        'rgb(134, 171, 46)',   # Yellow-green
                        'rgb(171, 134, 46)',   # Orange-yellow
                        'rgb(46, 171, 134)',   # Cyan-green
                        'rgb(134, 46, 171)',   # Purple
                        'rgb(171, 86, 46)',    # Orange
                        'rgb(46, 86, 171)',    # Dark blue
                        'rgb(86, 171, 46)',    # Green
                        'rgb(171, 46, 86)',    # Dark red
                        'rgb(46, 171, 86)',    # Jade green
                        'rgb(86, 46, 171)',    # Dark purple
                        'rgb(171, 134, 86)',   # Brown-yellow
                        'rgb(86, 171, 134)',   # Turquoise
                        'rgb(134, 86, 171)',   # Light purple
                    ]
                    # Select color based on word hash to ensure consistent colors for same word
                    return colors[hash(word) % len(colors)]
                
                # Create word cloud object
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    max_words=15,
                    relative_scaling=0.5,
                    random_state=42,
                    color_func=color_func  # Use custom color function
                ).generate_from_frequencies(wordcloud_data)
                
                # Display word cloud
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Skills Word Cloud (Size = Frequency)', fontsize=16, pad=20)
                
                st.pyplot(fig)
                plt.close(fig)
                
            except ImportError:
                st.error("WordCloud library not installed. Please install it with: pip install wordcloud")
                
                # Fallback: display skills list
                st.write("**Top Skills by Frequency:**")
                for i, (skill, freq) in enumerate(top_skills.items(), 1):
                    # Calculate font size based on frequency
                    font_size = min(24, max(12, int(12 + (freq / top_skills.max()) * 12)))
                    st.markdown(f"<span style='font-size:{font_size}px; margin:5px;'>{skill} ({freq})</span>", 
                               unsafe_allow_html=True)
        
        # Add summary statistics
        st.subheader("📊 Skills Summary")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Total Unique Skills", len(pd.Series(all_skills).value_counts()))
        
        with col4:
            st.metric("Most Frequent Skill", skill_counts.index[0], f"{skill_counts.values[0]} times")
        
        with col5:
            avg_frequency = skill_counts.mean()
            st.metric("Average Frequency", f"{avg_frequency:.1f}")
            
    else:
        st.info("No skills data available")
    
  