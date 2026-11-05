import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Crime Analysis Dashboard",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 Crime Data Analysis and Visualization")
st.markdown("### National Crime Statistics Interactive Dashboard")

uploaded_file = st.file_uploader(
    "Upload Crime Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    df.columns = [
        str(col).strip().replace(" ", "_")
        for col in df.columns
    ]

    st.success("Dataset uploaded successfully!")

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # Identify columns
    year_col = next(
        (c for c in df.columns if c.lower() == "year"),
        None
    )

    state_col = next(
        (c for c in df.columns
         if c.lower() in ["state", "state_ut", "states"]),
        None
    )

    # Convert numeric columns
    for col in df.columns:
    if col == state_col:
        continue

    converted = pd.to_numeric(
        df[col], errors="coerce"
    )

    if df[col].notna().sum() == converted.notna().sum():
        df[col] = converted

    if df[col].notna().sum() == converted.notna().sum():
        df[col] = converted

    crime_columns = [
        c for c in df.select_dtypes(include="number").columns
        if c != year_col
        and not any(x in c.lower()
                    for x in ["id", "serial", "index"])
    ]

    if not crime_columns:
        st.error("No numerical crime columns found.")

    else:

        df["Total_Crimes"] = df[
            crime_columns
        ].sum(axis=1)

        # Statistics
        st.subheader("📊 Crime Statistics")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Crimes",
            f"{df['Total_Crimes'].sum():,.0f}"
        )

        c2.metric(
            "Average Crimes",
            f"{df['Total_Crimes'].mean():,.0f}"
        )

        c3.metric(
            "Total States",
            df[state_col].nunique()
            if state_col else "N/A"
        )

        st.divider()

        # Year-wise Analysis
        if year_col:

            st.subheader("📈 Year-wise Crime Analysis")

            yearly = df.groupby(
                year_col
            )["Total_Crimes"].sum().reset_index()

            fig1 = px.line(
                yearly,
                x=year_col,
                y="Total_Crimes",
                markers=True,
                title="Year-wise Crime Trends"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        # State-wise Analysis
        if state_col:

            st.subheader("🏙️ State-wise Crime Analysis")

            state_data = df.groupby(
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
                title="Top 10 States by Crimes"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # Crime Category Analysis
        st.subheader("🥧 Crime Category Distribution")

        category_data = pd.DataFrame({
            "Crime Category": crime_columns,
            "Count": [
                df[c].sum() for c in crime_columns
            ]
        })

        fig3 = px.pie(
            category_data,
            names="Crime Category",
            values="Count",
            title="Crime Category Distribution"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # Dataset
        st.subheader("📋 Complete Crime Dataset")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.success("Crime Analysis Completed!")

else:

    st.info(
        "Please upload your Crime Dataset CSV file."
    )
