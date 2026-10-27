import re
import sqlite3

import pandas as pd

from database import DATABASE_NAME


def clean_text(text):
    """Convert complaint text into a clean, consistent format."""

    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def process_complaints():
    """Clean complaints and save their text features in SQLite."""

    connection = sqlite3.connect(DATABASE_NAME)

    complaints = pd.read_sql_query(
        """
        SELECT complaint_id, complaint_text
        FROM complaints
        """,
        connection,
    )

    if complaints.empty:
        connection.close()
        print("No complaints found. Generate sample data first.")
        return

    print(f"Cleaning {len(complaints)} complaints...")

    complaints["cleaned_text"] = complaints["complaint_text"].apply(
        clean_text
    )

    complaints["word_count"] = complaints["cleaned_text"].apply(
        lambda text: len(text.split())
    )

    cursor = connection.cursor()
    cursor.execute("DELETE FROM text_features")

    records = [
        (
            int(row.complaint_id),
            row.cleaned_text,
            int(row.word_count),
        )
        for row in complaints.itertuples(index=False)
    ]

    cursor.executemany(
        """
        INSERT INTO text_features (
            complaint_id, cleaned_text, word_count
        ) VALUES (?, ?, ?)
        """,
        records,
    )

    connection.commit()
    connection.close()

    print("Text cleaning completed successfully.")
    print("Cleaned text and word counts saved to the database.")


if __name__ == "__main__":
    process_complaints()