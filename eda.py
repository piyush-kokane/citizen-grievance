import os
import sqlite3

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from database import DATABASE_NAME


OUTPUT_DIR = "charts"


def run_eda():
    """Analyze complaint data and save charts."""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    connection = sqlite3.connect(DATABASE_NAME)

    complaints = pd.read_sql_query(
        """
        SELECT
            complaint_id,
            category,
            status,
            priority,
            ward_id,
            department_id,
            created_at,
            resolved_at
        FROM complaints
        """,
        connection,
    )

    departments = pd.read_sql_query(
        """
        SELECT department_id, department_name
        FROM departments
        """,
        connection,
    )

    connection.close()

    if complaints.empty:
        print("No complaints found. Generate sample data first.")
        return

    print("\n========== COMPLAINT ANALYSIS ==========")
    print(f"Total complaints: {len(complaints)}")

    print("\nComplaints by status:")
    print(complaints["status"].value_counts().to_string())

    print("\nComplaints by priority:")
    print(complaints["priority"].value_counts().to_string())

    print("\nComplaints by category:")
    print(complaints["category"].value_counts().to_string())

    # Chart 1: Complaints by status
    complaints["status"].value_counts().plot(
        kind="bar",
        title="Complaints by Status",
    )
    plt.xlabel("Status")
    plt.ylabel("Number of Complaints")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "complaints_by_status.png"))
    plt.close()

    # Chart 2: Complaints by category
    complaints["category"].value_counts().plot(
        kind="bar",
        title="Complaints by Category",
    )
    plt.xlabel("Category")
    plt.ylabel("Number of Complaints")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "complaints_by_category.png"))
    plt.close()

    # Chart 3: Complaints by priority
    complaints["priority"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        title="Complaints by Priority",
    )
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "complaints_by_priority.png"))
    plt.close()

    # Chart 4: Complaints by ward
    complaints["ward_id"].value_counts().sort_index().plot(
        kind="bar",
        title="Complaints by Ward",
        figsize=(12, 5),
    )
    plt.xlabel("Ward ID")
    plt.ylabel("Number of Complaints")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "complaints_by_ward.png"))
    plt.close()

    # Chart 5: Complaints by department
    department_counts = (
        complaints.groupby("department_id")
        .size()
        .rename("complaints")
        .reset_index()
        .merge(departments, on="department_id", how="left")
        .sort_values("complaints", ascending=False)
    )

    department_counts.plot(
        x="department_name",
        y="complaints",
        kind="bar",
        legend=False,
        title="Complaints by Department",
        figsize=(10, 5),
    )
    plt.xlabel("Department")
    plt.ylabel("Number of Complaints")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "complaints_by_department.png")
    )
    plt.close()

    # Chart 6: Complaints created per month
    complaints["created_at"] = pd.to_datetime(
        complaints["created_at"], errors="coerce"
    )

    monthly = (
        complaints.dropna(subset=["created_at"])
        .set_index("created_at")
        .resample("MS")
        .size()
    )

    monthly.plot(
        kind="line",
        marker="o",
        title="Complaints Created per Month",
        figsize=(10, 5),
    )
    plt.xlabel("Month")
    plt.ylabel("Number of Complaints")
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "monthly_complaints.png")
    )
    plt.close()

    print("\nCharts saved in the 'charts' folder.")
    print("EDA completed successfully.")


if __name__ == "__main__":
    run_eda()