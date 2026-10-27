import argparse

from database import create_tables
from data_generator import generate_data
from text_cleaning import process_complaints
from tfidf_features import create_tfidf_features
from model_training import train_models
from eda import run_eda


def run_all():
    """Run the complete project pipeline in order."""

    print("\nSTEP 1: Creating database tables")
    create_tables()

    print("\nSTEP 2: Generating sample data")
    generate_data()

    print("\nSTEP 3: Cleaning complaint text")
    process_complaints()

    print("\nSTEP 4: Creating TF-IDF features")
    create_tfidf_features()

    print("\nSTEP 5: Training machine-learning models")
    train_models()

    print("\nSTEP 6: Generating charts and analysis")
    run_eda()

    print("\nPROJECT PIPELINE COMPLETED!")


def main():
    parser = argparse.ArgumentParser(
        description="Citizen Grievance and Service Analytics Platform"
    )

    parser.add_argument(
        "command",
        choices=[
            "database",
            "data",
            "clean",
            "tfidf",
            "train",
            "eda",
            "all",
        ],
        help="Choose which project step to execute",
    )

    args = parser.parse_args()

    if args.command == "database":
        create_tables()

    elif args.command == "data":
        generate_data()

    elif args.command == "clean":
        process_complaints()

    elif args.command == "tfidf":
        create_tfidf_features()

    elif args.command == "train":
        train_models()

    elif args.command == "eda":
        run_eda()

    elif args.command == "all":
        run_all()


if __name__ == "__main__":
    main()