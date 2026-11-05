     # Clean column names
    df.columns = df.columns.str.strip()

    # Identify state column
    for col in df.columns:
        if col.lower().strip() in ['state', 'state_ut', 'state/ut']:
            df.rename(columns={col: 'State_UT'}, inplace=True)
            break

    # Identify year column
    for col in df.columns:
        if col.lower().strip() in ['year', 'years']:
            df.rename(columns={col: 'Year'}, inplace=True)
            break

    # Identify numeric crime columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    crime_columns = [
        col for col in numeric_cols
        if col not in ['Year', 'ID', 'S.No']
        and col != 'Total_Crimes'
    ]

    if 'Total_Crimes' not in df.columns:
        df['Total_Crimes'] = df[crime_columns].sum(axis=1)

    st.success("Dataset uploaded successfully!")