import pandas as pd
import numpy as np


def wrangle(df):
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
                # Handle date columns with only month and day
                try:
                    df[col] = pd.to_datetime(df[col], format='%m/%d')
                except ValueError:
                    # Handle date columns with only year and month
                    try:
                        df[col] = pd.to_datetime(df[col], format='%Y-%m')
                    except ValueError:
                        # Handle date columns with only year
                        try:
                            df[col] = pd.to_datetime(df[col], format='%Y')
                        except ValueError:
                            # Handle date columns with month and year
                            try:
                                df[col] = pd.to_datetime(df[col], format='%b %Y')
                            except ValueError:
                                # Handle date columns with month name and day
                                try:
                                    df[col] = pd.to_datetime(df[col], format='%b %d')
                                except ValueError:
                                    # Handle date columns with day, month name, and year
                                    df[col] = pd.to_datetime(df[col], format='%d %b %Y')

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
