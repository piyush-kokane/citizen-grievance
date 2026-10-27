"""Create leakage-safe TF-IDF features and a reproducible holdout split."""
import os
import sqlite3

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from database import DATABASE_NAME

OUTPUT_DIR = "model_artifacts"
RANDOM_STATE = 42
TEST_SIZE = 0.25

def create_tfidf_features():
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        data = pd.read_sql_query("""
            SELECT c.complaint_id, c.category, c.created_at, tf.cleaned_text
            FROM complaints c
            JOIN text_features tf ON c.complaint_id = tf.complaint_id
            WHERE tf.cleaned_text IS NOT NULL AND TRIM(tf.cleaned_text) != ''
        """, connection)
    finally:
        connection.close()

    if data.empty:
        print("No cleaned complaints found. Run `python main.py data` then `python main.py clean`.")
        return

    data = data.dropna(subset=["category", "cleaned_text"]).copy()
    data["category"] = data["category"].astype(str)
    data["cleaned_text"] = data["cleaned_text"].astype(str)
    data = data[data["cleaned_text"].str.strip().ne("")]
    if data["category"].nunique() < 2:
        print("At least two categories are required for classification.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    train_idx, test_idx = train_test_split(
        data.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=data["category"],
    )
    train_text = data.loc[train_idx, "cleaned_text"]
    test_text = data.loc[test_idx, "cleaned_text"]
    y_train = data.loc[train_idx, "category"]
    y_test = data.loc[test_idx, "category"]

    # Fit vocabulary/IDF on training text only; the test set must not influence
    # feature construction or evaluation.
    vectorizer = TfidfVectorizer(
        max_features=5000, ngram_range=(1, 2), min_df=2,
        max_df=0.98, stop_words="english", sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(train_text)
    X_test = vectorizer.transform(test_text)

    joblib.dump(vectorizer, os.path.join(OUTPUT_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(X_train, os.path.join(OUTPUT_DIR, "X_train.joblib"))
    joblib.dump(X_test, os.path.join(OUTPUT_DIR, "X_test.joblib"))
    joblib.dump(y_train, os.path.join(OUTPUT_DIR, "y_train.joblib"))
    joblib.dump(y_test, os.path.join(OUTPUT_DIR, "y_test.joblib"))
    data.to_csv(os.path.join(OUTPUT_DIR, "complaints_dataset.csv"), index=False)

    print(f"Records: {len(data):,}; train: {len(y_train):,}; test: {len(y_test):,}")
    print(f"Train classes: {y_train.nunique()}; test classes: {y_test.nunique()}")
    print(f"TF-IDF features: {X_train.shape[1]:,}")
    print("Split is stratified and reproducible; vectorizer was fit on training data only.")

if __name__ == "__main__":
    create_tfidf_features()
