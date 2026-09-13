import sqlite3

conn = sqlite3.connect("recover_ai.db")
cursor = conn.cursor()

columns = [
    ("razorpay_payment_link_id", "TEXT"),
    ("razorpay_payment_id", "TEXT"),
    ("payment_link_url", "TEXT"),
    ("payment_link_reference_id", "TEXT"),
]

for column_name, column_type in columns:
    try:
        cursor.execute(
            f"ALTER TABLE recovery_cases ADD COLUMN {column_name} {column_type}"
        )
        print(f"Added: {column_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Already exists: {column_name}")
        else:
            raise

conn.commit()
conn.close()

print("Database migration completed.")