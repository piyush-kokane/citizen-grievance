# Citizen Grievance and Service Analytics Platform

## Project Overview

This project analyzes civic complaints using a database,
data analysis, text processing, and machine learning.

## Technologies Used

- Python
- SQLite
- Pandas
- Scikit-learn
- Matplotlib
- Streamlit

## Project Files

- main.py: Runs project steps
- database.py: Creates database tables
- data_generator.py: Generates synthetic complaint data
- text_cleaning.py: Cleans complaint text
- tfidf_features.py: Converts text into TF-IDF features
- model_training.py: Trains and compares models
- eda.py: Analyzes data and generates charts
- app.py: Displays the Streamlit dashboard
- requirements.txt: Lists required libraries
- README.md: Project documentation

## Installation

Install the required libraries:

pip install -r requirements.txt

## Run the Project

Run each command from the project folder:

python main.py database
python main.py data
python main.py clean
python main.py tfidf
python main.py train
python main.py eda

## Launch the Dashboard

streamlit run app.py

## Note

The generated complaints are synthetic sample data.
They are for demonstration and educational purposes only.