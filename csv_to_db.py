import pandas as pd
from sqlalchemy import create_engine

# Read data
data = pd.read_csv('used_cars_data_cleaned.csv')  # Or use pd.read_excel for Excel files

# Create a database connection (example with SQLite)
engine = create_engine('mysql://root:@localhost/cardb')

# Write the data to a database table
data.to_sql('cars', con=engine, if_exists='replace', index=False)
