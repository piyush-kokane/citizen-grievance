# Citizen Grievance and Service Analytics Platform

## 1. Project overview

This is a Python demonstration project for generating synthetic civic complaints, preparing complaint text, training text-classification models, exploring evaluation results, and viewing service analytics in a Streamlit dashboard.

The project is designed for experimentation and demonstration. **The generated complaints, citizen records, ward statistics, and resolution outcomes are synthetic. They must not be presented as actual citizen reports or real municipal performance.**

## 2. Main features

- **Synthetic complaint data:** generates citizen, ward, department, and complaint records with varied wording and category frequencies.
- **Ward-level outcome variation:** assigns different target resolution probabilities to wards so the Ward Scorecard can show variation. These rates are simulated, not measured service levels.
- **Text cleaning:** normalizes complaint text and stores cleaned text and basic text features in SQLite.
- **TF-IDF features:** converts text into numeric features for machine-learning models.
- **Model evaluation:** compares a majority-class baseline with Multinomial Naive Bayes, Logistic Regression, and Linear Support Vector Classification.
- **Exploratory analysis:** generates summaries and charts from the dataset.
- **Streamlit dashboard:** provides complaint and service analytics, including a Complaint Preview with Complaint ID, Citizen ID, and Ward ID, along with filters for those IDs and other available complaint fields.

## 3. Technology stack

- Python
- SQLite
- pandas and NumPy
- scikit-learn
- joblib
- Streamlit
- Plotly and Matplotlib/Seaborn

Dependencies are listed in `requirements.txt`.

## 4. Project structure

| File or directory | Purpose |
|---|---|
| `app.py` | Streamlit dashboard and analytics pages |
| `main.py` | Command-line entry point for the processing pipeline |
| `database.py` | SQLite database name, connection helper, and schema creation |
| `data_generator.py` | Creates synthetic citizens, wards, departments, and complaints |
| `text_cleaning.py` | Cleans complaint text and stores text features |
| `tfidf_features.py` | Creates the train/test split and TF-IDF feature artifacts |
| `model_training.py` | Trains classifiers, compares metrics, and saves the selected model |
| `eda.py` | Exploratory analysis and chart generation |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes local/generated files from Git |
| `README.md` | Quick-start overview |
| `DOCUMENTATION.md` | Detailed setup, workflow, and troubleshooting guide |
| `citizen_grievance.db` | Created locally when the database pipeline runs; intentionally not committed |
| `model_artifacts/` | Generated datasets, vectorizer, model files, and evaluation output; intentionally not committed |

## 5. Setup

Run the following commands from the project root—the directory containing `main.py` and `requirements.txt`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run the environment's Python directly using `.venv\Scripts\python.exe`.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Run the pipeline

### Run all steps

```bash
python main.py all
```

The pipeline runs these steps in order:

1. Create SQLite tables.
2. Generate synthetic data.
3. Clean complaint text.
4. Create TF-IDF features and a stratified train/test split.
5. Train and evaluate the models.
6. Generate exploratory analysis.

### Run a single step

```bash
python main.py database
python main.py data
python main.py clean
python main.py tfidf
python main.py train
python main.py eda
```

Run steps in order when building the project from scratch. For example, model training requires the TF-IDF artifacts produced by the `tfidf` step.

> **Important:** Running `python main.py data` regenerates the synthetic dataset and clears/replaces generated records in the relevant database tables. Back up any local database you need before running this command. The `.gitignore` rules prevent local database files from being committed by default.

## 7. Launch the dashboard

After installing dependencies, run:

```bash
streamlit run app.py
```

Streamlit prints a local URL in the terminal. Open that URL in a browser. Stop the app with `Ctrl+C` in the terminal.

### Complaint Preview

The Complaint Preview table includes the complaint identifier and the related citizen and ward identifiers. Use the ID filters to narrow the preview by Complaint ID, Citizen ID, or Ward ID. These filters are intended to be combined with the other available complaint filters.

## 8. Data and database notes

The database file is named `citizen_grievance.db` and is created in the current working directory. The schema includes tables for:

- wards
- departments
- citizens
- staff
- complaints
- status history
- department reassignments
- resolutions
- cleaned text features
- duplicate complaint pairs

The exact records depend on the generated dataset and which pipeline steps have been run. The dashboard and pipeline should be launched from the project root so that the relative database and artifact paths resolve consistently.

## 9. Machine-learning workflow and evaluation

The TF-IDF step uses a reproducible, stratified train/test split. The vectorizer is fitted only on training text and then applied to the holdout text, avoiding leakage from the test vocabulary/IDF statistics into training.

The training step compares:

- Majority-class baseline
- Multinomial Naive Bayes
- Logistic Regression
- Linear Support Vector Classifier

Reported metrics include accuracy, balanced accuracy, macro F1, weighted F1, a classification report, and a confusion matrix. The selected model is chosen using macro F1, with balanced accuracy and accuracy used as tie-breakers.

Generated artifacts are written under `model_artifacts/`, including the TF-IDF vectorizer, training/test matrices and labels, a dataset CSV, model comparison results, the selected model, its name, and a confusion matrix.

A score below 100% is not automatically better, and a 100% score is not automatically wrong. However, perfect scores on synthetic text can indicate that labels are too easy to infer or that examples are overly repetitive. Assess the system on a separate, independently labelled real-world dataset before making claims about production performance.

## 10. Git and generated files

The supplied `.gitignore` excludes local virtual environments, Python caches, SQLite databases, generated model artifacts, generated CSVs/charts, logs, and common editor files. This helps keep generated or potentially sensitive data out of source control.

The ignore rules are intentionally conservative. If a CSV, image, or other generated artifact is a curated example that should be versioned, use a narrow force-add only after checking that it contains no private data, or revise the relevant ignore rule for that file.

Suggested first commit:

```bash
git init
git add .gitignore README.md DOCUMENTATION.md requirements.txt *.py
git status
git commit -m "Add citizen grievance analytics project"
```

Review `git status` before committing. Do not commit real citizen data, credentials, local database files, or generated model files unless there is an explicit, reviewed reason to do so.

## 11. Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and install the requirements again:

```bash
pip install -r requirements.txt
```

### No cleaned complaints or TF-IDF artifacts

Run the steps in order:

```bash
python main.py database
python main.py data
python main.py clean
python main.py tfidf
python main.py train
```

### Dashboard cannot find the database or artifacts

Run commands from the project root. The project uses relative paths for `citizen_grievance.db` and `model_artifacts/`.

### Model results look unexpectedly perfect

Check for repeated or near-duplicate templates, target leakage, and labels that can be inferred from wording. Evaluate on a holdout dataset that is independent of the generated templates, ideally with human-labelled examples from a separate time period or source.

### Ward resolution rates look different after regeneration

The ward-specific resolution probabilities are randomized synthetic parameters. Regenerating the dataset can change the sampled counts and observed percentages. These figures are for dashboard demonstrations only.

## 12. Limitations and responsible use

- Data is synthetic and does not describe actual citizens, wards, or municipal operations.
- Synthetic model metrics do not establish real-world accuracy or fairness.
- Ward resolution percentages are generated for demonstration and must not be used to rank actual public-service teams.
- Before using real complaint records, establish appropriate privacy, access-control, retention, and data-quality practices.
