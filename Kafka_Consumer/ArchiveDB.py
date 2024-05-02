import sqlite3
import threading
import time
from datetime import datetime, timedelta

def delete_old_records(days):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect('')
        cursor = connection.cursor()

        # Calculate the threshold date
        threshold_date = datetime.now() - timedelta(days=days)

        # Format the datetime object as a string in the format 'd-m-Y'
        formatted_date = threshold_date.strftime("%d-%m-%Y")

        # Convert formatted_date to yyyy-mm-dd format for comparison
        formatted_date_for_comparison = threshold_date.strftime("%Y-%m-%d")

        cursor.execute("DELETE FROM logs_messages_tb WHERE DATE(SUBSTR(dateLog, 7, 4) || '-' || SUBSTR(dateLog, 4, 2) || '-' || SUBSTR(dateLog, 1, 2)) < ?", (formatted_date_for_comparison,))
        connection.commit()

        connection.close()

        print(f"Deleted old records. Next check in 24 hours.")
        time.sleep(24 * 60 * 60)

    except Exception as e:
        print(f"Error: {e}")

# Get the number of days from the user
days_to_keep = int(input("Enter the number of days to keep records: "))

# Start the thread
thread = threading.Thread(target=delete_old_records, args=(days_to_keep,))
thread.start()
