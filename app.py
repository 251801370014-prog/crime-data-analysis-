import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Crime Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("🚔 Crime Data Analysis and Visualization")
st.markdown("### National Crime Statistics Interactive Dashboard")

# Upload Dataset
uploaded_file = st.file_uploader(
    "Upload Crime Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    crime_columns = [
        'Murder',
        'Kidnapping_Abduction',
        'Crimes_Against_Women',
        'Robbery',
        'Theft',
        'Cybercrime',
        'Crimes_Against_Children'
    ]

    if 'Total_Crimes' not in df.columns:
       df['Total_Crimes'] = df[crime_columns].sum(axis=1)

    st.success("Dataset uploaded successfully!")

    # Sidebar Filters
    st.sidebar.header("Dashboard Filters")

    if 'Year' in df.columns:
        years = sorted(df['Year'].dropna().unique())
        selected_year = st.sidebar.multiselect(
            "Select Year",
            years,
            default=years
        )
        df = df[df['Year'].isin(selected_year)]

    if 'State_UT' in df.columns:
        states = sorted(df['State_UT'].dropna().unique())
        selected_states = st.sidebar.multiselect(
            "Select State",
            states,
            default=states
        )
        df = df[df['State_UT'].isin(selected_states)]

    # Statistics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Crimes",
        f"{df['Total_Crimes'].sum():,.0f}"
    )

    col2.metric(
        "Average Crimes",
        f"{df['Total_Crimes'].mean():,.0f}"
    )

    col3.metric(
        "Total States",
        df['State_UT'].nunique()
    )

    st.divider()

    # Year-wise Analysis
    st.subheader("📈 Year-wise Crime Analysis")

    if 'Year' in df.columns:
        yearly = df.groupby('Year')['Total_Crimes'].sum().reset_index()

        fig1 = px.line(
            yearly,
            x='Year',
            y='Total_Crimes',
            markers=True,
            title="Year-wise Total Crimes"
        )

        st.plotly_chart(fig1, use_container_width=True)

    # State-wise Analysis
    st.subheader("📊 State-wise Crime Analysis")

    state_data = df.groupby(
        'State_UT'
    )['Total_Crimes'].sum().reset_index()

    state_data = state_data.sort_values(
        'Total_Crimes',
        ascending=False
    ).head(10)

    fig2 = px.bar(
        state_data,
        x='State_UT',
        y='Total_Crimes',
        title="Top 10 States by Total Crimes",
        color='Total_Crimes'
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Crime Category Analysis
    st.subheader("🥧 Crime Category Distribution")

    available_columns = [
        c for c in crime_columns if c in df.columns
    ]

    category_data = df[available_columns].sum().reset_index()
    category_data.columns = ['Crime Category', 'Count']

    fig3 = px.pie(
        category_data,
        names='Crime Category',
        values='Count',
        title="Crime Category Distribution"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Dataset
    st.subheader("📋 Crime Dataset")
    st.dataframe(df, use_container_width=True)

    st.success("Crime Analysis Completed!")

else:
    st.info("Please upload your Kaggle Crime Dataset CSV file.")