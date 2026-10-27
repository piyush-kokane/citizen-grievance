"""Train and honestly evaluate several text classifiers."""
import os

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

ARTIFACT_DIR = "model_artifacts"

def train_models():
    required = ["X_train.joblib", "X_test.joblib", "y_train.joblib", "y_test.joblib"]
    missing = [f for f in required if not os.path.exists(os.path.join(ARTIFACT_DIR, f))]
    if missing:
        print("Missing training artifacts:", ", ".join(missing))
        print("Run: python main.py data && python main.py clean && python main.py tfidf")
        return

    X_train = joblib.load(os.path.join(ARTIFACT_DIR, "X_train.joblib"))
    X_test = joblib.load(os.path.join(ARTIFACT_DIR, "X_test.joblib"))
    y_train = joblib.load(os.path.join(ARTIFACT_DIR, "y_train.joblib"))
    y_test = joblib.load(os.path.join(ARTIFACT_DIR, "y_test.joblib"))

    models = {
        "Majority-class baseline": DummyClassifier(strategy="most_frequent"),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Logistic Regression": LogisticRegression(
            max_iter=1500, class_weight="balanced", C=1.0, random_state=42
        ),
        "Linear Support Vector Classifier": LinearSVC(
            class_weight="balanced", C=0.7, random_state=42
        ),
    }

    rows, fitted = [], {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        row = {
            "Model": name,
            "Accuracy": round(accuracy_score(y_test, pred), 4),
            "Balanced Accuracy": round(balanced_accuracy_score(y_test, pred), 4),
            "Macro F1": round(f1_score(y_test, pred, average="macro", zero_division=0), 4),
            "Weighted F1": round(f1_score(y_test, pred, average="weighted", zero_division=0), 4),
        }
        rows.append(row)
        fitted[name] = (model, pred)
        print("  " + " | ".join(f"{k}: {v}" for k, v in row.items() if k != "Model"))

    results = pd.DataFrame(rows).sort_values(
        ["Macro F1", "Balanced Accuracy", "Accuracy"], ascending=False
    )
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    results.to_csv(os.path.join(ARTIFACT_DIR, "model_comparison.csv"), index=False)

    best_name = results.iloc[0]["Model"]
    best_model, best_pred = fitted[best_name]
    joblib.dump(best_model, os.path.join(ARTIFACT_DIR, "best_model.joblib"))
    with open(os.path.join(ARTIFACT_DIR, "best_model_name.txt"), "w", encoding="utf-8") as f:
        f.write(best_name)

    pd.DataFrame(confusion_matrix(y_test, best_pred, labels=sorted(pd.Series(y_test).unique())),
                 index=sorted(pd.Series(y_test).unique()),
                 columns=sorted(pd.Series(y_test).unique())).to_csv(
        os.path.join(ARTIFACT_DIR, "best_model_confusion_matrix.csv")
    )

    print("\nModel comparison (sorted by macro F1):")
    print(results.to_string(index=False))
    print(f"\nSelected model: {best_name}")
    print("\nPer-class report:")
    print(classification_report(y_test, best_pred, zero_division=0))
    if (results["Accuracy"] >= 1.0).all():
        print("\nWARNING: every model scored 100%. Inspect for duplicate/template leakage or overly easy labels.")
    print("Metrics are holdout estimates, not a guarantee of real-world performance.")

if __name__ == "__main__":
    train_models()
