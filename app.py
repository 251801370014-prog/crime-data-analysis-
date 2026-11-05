import streamlit as st
import pandas as pd
import plotly.express as px
import re

# PAGE SETTINGS
st.set_page_config(
    page_title="Crime Analysis Dashboard",
    page_icon="🚔",
    layout="wide"
)

# TITLE
st.title("🚔 Crime Data Analysis and Visualization")
st.markdown("### National Crime Statistics Interactive Dashboard")

st.markdown("---")

# DATASET UPLOAD
uploaded_file = st.file_uploader(
    "Upload Crime Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        # CLEAN COLUMN NAMES
        df.columns = [
            str(col).replace("\ufeff", "").strip()
            for col in df.columns
        ]

        st.success("Dataset uploaded successfully!")

        # IDENTIFY STATE AND YEAR COLUMNS
        def normalize(col):
            return re.sub(r'[^a-z0-9]', '', str(col).lower())

        state_col = None
        year_col = None

        for col in df.columns:

            name = normalize(col)

            if name in [
                "state", "stateut",
                "statename", "stateunionterritory"
            ]:
                state_col = col

            if name in [
                "year", "financialyear",
                "crimeyear", "calendaryear"
            ]:
                year_col = col

        # CONVERT NUMERIC DATA
        for col in df.columns:

            if col != state_col:
                df[col] = pd.to_numeric(
                    df[col], errors="coerce"
                )

        # IDENTIFY CRIME COLUMNS
        keywords = [
            "murder", "kidnap", "abduction",
            "crime", "rape", "robbery",
            "theft", "burglary", "assault",
            "rioting", "dacoity", "arson",
            "cheating", "forgery", "women",
            "children", "cyber", "ipc",
            "sll", "hurt"
        ]

        crime_columns = []

        for col in df.columns:

            name = normalize(col)

            if col in [state_col, year_col]:
                continue

            if name in [
                "totalcrimes", "totalcrime",
                "totalcases", "total"
            ]:
                continue

            if any(word in name for word in keywords):

                if pd.api.types.is_numeric_dtype(df[col]):
                    crime_columns.append(col)

        # FALLBACK NUMERIC COLUMNS
        if not crime_columns:

            excluded = [
                "year", "population",
                "rate", "id", "serial",
                "index", "number"
            ]

            crime_columns = [
                col for col in df.select_dtypes(
                    include="number"
                ).columns
                if not any(
                    word in normalize(col)
                    for word in excluded
                )
            ]

        # TOTAL CRIMES
        total_col = next(
            (
                col for col in df.columns
                if normalize(col) in [
                    "totalcrimes",
                    "totalcrime",
                    "totalcases"
                ]
            ),
            None
        )

        if total_col is not None:
            df["Total_Crimes"] = df[total_col].fillna(0)

        elif crime_columns:
            df["Total_Crimes"] = (
                df[crime_columns].fillna(0).sum(axis=1)
            )

        else:
            st.error("No crime-related numeric columns found.")
            st.stop()

        # SIDEBAR FILTERS
        st.sidebar.title("Dashboard Filters")

        filtered_df = df.copy()

        if year_col is not None:

            years = sorted(
                df[year_col].dropna().unique().tolist()
            )

            if years:

                selected_years = st.sidebar.multiselect(
                    "Select Year",
                    years,
                    default=years
                )

                filtered_df = filtered_df[
                    filtered_df[year_col].isin(selected_years)
                ]

        if state_col is not None:

            states = sorted(
                df[state_col].dropna().astype(str).unique()
            )

            selected_states = st.sidebar.multiselect(
                "Select State",
                states,
                default=states
            )

            filtered_df = filtered_df[
                filtered_df[state_col].astype(str).isin(
                    selected_states
                )
            ]

        # STATISTICS
        st.subheader("📊 Crime Statistics")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Crimes",
            f"{filtered_df['Total_Crimes'].sum():,.0f}"
        )

        col2.metric(
            "Average Crimes",
            f"{filtered_df['Total_Crimes'].mean():,.0f}"
        )

        col3.metric(
            "Total Records",
            len(filtered_df)
        )

        col4.metric(
            "Total States",
            filtered_df[state_col].nunique()
            if state_col else "N/A"
        )

        st.divider()

        # YEAR WISE ANALYSIS
        if year_col is not None:

            st.subheader("📈 Year-wise Crime Analysis")

            yearly = filtered_df.groupby(
                year_col
            )["Total_Crimes"].sum().reset_index()

            fig1 = px.line(
                yearly,
                x=year_col,
                y="Total_Crimes",
                markers=True,
                title="Year-wise Total Crimes"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        # STATE WISE ANALYSIS
        if state_col is not None:

            st.subheader("📍 State-wise Crime Analysis")

            state_data = filtered_df.groupby(
                state_col
            )["Total_Crimes"].sum().reset_index()

            state_data = state_data.sort_values(
                "Total_Crimes",
                ascending=False
            ).head(10)

            fig2 = px.bar(
                state_data,
                x=state_col,
                y="Total_Crimes",
                color="Total_Crimes",
                title="Top 10 States by Total Crimes"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # CRIME CATEGORY ANALYSIS
        st.subheader("🥧 Crime Category Distribution")

        if crime_columns:

            category_data = filtered_df[
                crime_columns
            ].sum().reset_index()

            category_data.columns = [
                "Crime Category", "Count"
            ]

            fig3 = px.pie(
                category_data,
                names="Crime Category",
                values="Count",
                title="Crime Category Distribution",
                hole=0.4
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

            # CATEGORY BAR CHART
            fig4 = px.bar(
                category_data.sort_values(
                    "Count",
                    ascending=False
                ),
                x="Crime Category",
                y="Count",
                color="Count",
                title="Crime Type Comparison"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

        # TOP CRIMES
        st.subheader("🏆 Top Crime Records")

        top_crimes = filtered_df.sort_values(
            "Total_Crimes",
            ascending=False
        ).head(10)

        st.dataframe(
            top_crimes,
            use_container_width=True
        )

        # DOWNLOAD DATA
        st.subheader("⬇️ Download Dataset")

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Crime Data CSV",
            csv,
            "crime_analysis.csv",
            "text/csv"
        )

        st.success(
            "Crime Data Analysis Completed Successfully!"
        )

    except Exception as e:

        st.error(f"Error: {e}")

else:

    st.info(
        "Please upload your Crime Dataset CSV file."
    )

    st.markdown(
        "### Features of Crime Analysis Dashboard"
    )

    st.write("📊 Crime Statistics")
    st.write("📈 Year-wise Analysis")
    st.write("📍 State-wise Analysis")
    st.write("🥧 Crime Category Distribution")
    st.write("🏆 Top 10 Crime Records")
    st.write("⬇️ Dataset Download")