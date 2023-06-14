import sqlite3
import sqlite3
import pandas as pd
   
# Path to the exported SQLite database file
db_path = "C:\Users\Melchizededk\Desktop\app.db"

# Connection to the database   
conn = sqlite3.connect("C:\Users\Melchizedek\Documents\Final year project\ams\db.sqlite3")

# Read the exported data into a pandas DataFrame
exported_data = pd.read_sql_query("SELECT * FROM finger_store", sqlite3.connect(db_path))

# Check for existing records in the database
existing_data = pd.read_sql_query("SELECT * FROM finger_store", conn)

# Filter new and changed records
new_data = exported_data[~exported_data.isin(existing_data)].dropna()

# Insert new and changed records into the database
new_data.to_sql("finger_store", conn, if_exists="append", index=False)

# Close the database connection
conn.close()