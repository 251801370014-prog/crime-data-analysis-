import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Crime Data Analysis Dashboard",
    page_icon="🚔",
    layout="wide"
)

# TITLE

st.title("🚔 Crime Data Analysis and Visualization")

st.subheader("National Crime Statistics Interactive Dashboard")

st.markdown("""
This project analyzes crime statistics across different
states and years using Python.
""")

st.divider()

# DATASET UPLOAD

st.header("📂 Upload Crime Dataset")

uploaded_file = st.file_uploader(
    "Upload your Crime Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    try:

        # READ DATASET

        df = pd.read_csv(uploaded_file)

        # CLEAN COLUMN NAMES

        df.columns = df.columns.astype(str).str.strip()

        # REMOVE DUPLICATE COLUMNS

        df = df.loc[:, ~df.columns.duplicated()]

        # CLEAN DATA

        df = df.drop_duplicates()

        st.success("Dataset uploaded successfully!")

        # IDENTIFY COLUMNS

        state_col = None
        year_col = None

        for col in df.columns:

            name = col.lower().strip()

            if name in ["state", "state_ut", "state/ut"]:
                state_col = col

            if name in ["year", "years"]:
                year_col = col

        # CONVERT NUMERIC COLUMNS

        for col in df.columns:

            if col != state_col:

                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ""),
                    errors="ignore"
                )

        # IDENTIFY CRIME COLUMNS

        numeric_cols = df.select_dtypes(
            include="number"
        ).columns.tolist()

        crime_columns = [
            col for col in numeric_cols
            if col.lower() not in [
                "year",
                "id",
                "s.no",
                "serial number",
                "total_crimes"
            ]
        ]

        # CALCULATE TOTAL CRIMES

        if "Total_Crimes" not in df.columns:

            if crime_columns:

                df["Total_Crimes"] = df[
                    crime_columns
                ].sum(axis=1)

            else:

                df["Total_Crimes"] = 0

        st.divider()

        # DATASET INFORMATION

        st.header("📊 Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", len(df))

        with col2:
            st.metric("Total Columns", len(df.columns))

        with col3:
            st.metric(
                "Total Crimes",
                f"{int(df['Total_Crimes'].sum()):,}"
            )

        st.divider()

        # DATA PREVIEW

        st.header("📋 Dataset Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        st.write("Dataset Columns:")
        st.write(df.columns.tolist())

        st.divider()

        # FILTERS

        st.header("🔎 Crime Data Filters")

        filtered_df = df.copy()

        if state_col is not None:

            states = sorted(
                df[state_col].dropna().astype(str).unique()
            )

            selected_states = st.multiselect(
                "Select States",
                states,
                default=states
            )

            filtered_df = filtered_df[
                filtered_df[state_col].astype(str).isin(
                    selected_states
                )
            ]

        if year_col is not None:

            years = sorted(
                df[year_col].dropna().unique()
            )

            selected_years = st.multiselect(
                "Select Years",
                years,
                default=years
            )

            filtered_df = filtered_df[
                filtered_df[year_col].isin(selected_years)
            ]

        st.divider()

        # FILTERED STATISTICS

        st.header("📈 Crime Statistics")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Filtered Records",
                len(filtered_df)
            )

        with c2:
            st.metric(
                "Total Crimes",
                f"{int(filtered_df['Total_Crimes'].sum()):,}"
            )

        with c3:

            average = filtered_df["Total_Crimes"].mean()

            st.metric(
                "Average Crimes",
                f"{average:,.2f}"
            )

        st.divider()

        # STATE WISE ANALYSIS

        st.header("🏙️ State-wise Crime Analysis")

        if state_col is not None:

            state_data = filtered_df.groupby(
                state_col
            )["Total_Crimes"].sum().reset_index()

            state_data = state_data.sort_values(
                "Total_Crimes",
                ascending=False
            )

            fig1 = px.bar(
                state_data,
                x=state_col,
                y="Total_Crimes",
                title="Total Crimes by State",
                color="Total_Crimes",
                text_auto=True
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            # TOP STATES

            st.subheader("Top 10 States")

            top_states = state_data.head(10)

            fig2 = px.bar(
                top_states,
                x="Total_Crimes",
                y=state_col,
                orientation="h",
                title="Top 10 States by Crime",
                color="Total_Crimes"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        else:

            st.info("State column not found in dataset.")

        st.divider()

        # YEAR WISE ANALYSIS

        st.header("📅 Year-wise Crime Analysis")

        if year_col is not None:

            year_data = filtered_df.groupby(
                year_col
            )["Total_Crimes"].sum().reset_index()

            fig3 = px.line(
                year_data,
                x=year_col,
                y="Total_Crimes",
                markers=True,
                title="Crime Trends Over Years"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        else:

            st.info("Year column not found in dataset.")

        st.divider()

        # CRIME CATEGORY ANALYSIS

        st.header("🚨 Crime Category Analysis")

        if crime_columns:

            crime_totals = filtered_df[
                crime_columns
            ].sum().reset_index()

            crime_totals.columns = [
                "Crime Category",
                "Total Cases"
            ]

            crime_totals = crime_totals.sort_values(
                "Total Cases",
                ascending=False
            )

            # PIE CHART

            fig4 = px.pie(
                crime_totals,
                names="Crime Category",
                values="Total Cases",
                title="Crime Category Distribution",
                hole=0.3
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

            # BAR CHART

            fig5 = px.bar(
                crime_totals,
               