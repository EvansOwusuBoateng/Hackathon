import pandas as pd
import numpy as np

def wrangle(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Print the number of null values in the data
    null_values = df.isnull().sum()

    # Check for duplicate observations, print the number of duplicate observations and remove duplicate rows
    duplicate_rows = df.duplicated().sum()
    df = df.drop_duplicates()

    # Check for different variations of the date column name
    date_columns = ['date', 'Date', 'DATE', 'timestamp', 'Timestamp', 'TIMESTAMP', 'period', 'Period', 'PERIOD']
    for col in date_columns:
        if col in df.columns:
            # Convert the date column to datetime format
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                # Handle various date formats
                pass  # This could include additional handling as needed

            # Set the date column as the index
            df = df.set_index(col)
            break

    # Replace null values in floating-point columns with mean rounded to 3 decimal places
    float_columns = df.select_dtypes(include=np.floating).columns
    for col in float_columns:
        df[col] = df[col].fillna(df[col].mean().round(3))

    # Replace null values in integer columns with mean rounded to nearest whole number
    int_columns = df.select_dtypes(include=np.integer).columns
    for col in int_columns:
        df[col] = df[col].fillna(round(df[col].mean()))

    # Replace null values in categorical columns with the most frequent value
    categorical_columns = df.select_dtypes(include='object').columns
    for col in categorical_columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df, null_values, duplicate_rows
