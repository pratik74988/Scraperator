import sqlite3

conn = sqlite3.connect("backend\db.sqlite3")
cursor = conn.cursor()

# list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# show data from each table
for table in tables:
    print(f"\nData from {table[0]}:")
    cursor.execute(f"SELECT * FROM {table[0]}")
    for row in cursor.fetchall():
        print(row)

conn.close()
