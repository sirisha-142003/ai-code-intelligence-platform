# Code Quality Analyzer

This project provides automated analysis and grouping of code quality for Python and JavaScript projects. It collects code from GitHub, extracts important metrics, and uses clustering to categorize files. The approach uses unsupervised learning due to the lack of labeled data.

## Workflow

The project has the following scripts run in order:

- **fetch.py**: Uses the GitHub API to get Python and JavaScript code files, saving them in the `datasets/` directory.
- **extract.py**: Goes through the collected files to pull out metrics such as code complexity, readability, lines of code, cyclomatic complexity, and docstring presence.
- **export.py**: Puts together the extracted metrics into a CSV file named `metrics.csv`, getting the data ready for machine learning preprocessing.
- **keyword.py**: Does keyword extraction and analysis to find common patterns, libraries, or themes within the code.

## Preprocessing

Data preprocessing includes the following steps:

- Making features the same size using `StandardScaler` to make numerical features normal.
- Changing yes/no features, such as `has_docstring`, to integer values (0 or 1).
- Cutting down dimensions using Principal Component Analysis (PCA). After testing different numbers, 10 components were chosen as the most balanced option.

## Unsupervised Learning

The project uses K-Means clustering for code quality grouping. DBSCAN was tried but dropped because of too much noise and clusters broken into small pieces. Cluster labels (Good, Average, Bad) are given based on statistical analysis of metrics like mean complexity.

## Supervised Learning

Supervised models, including Random Forest, were tested using fake labels made from clustering. Because of overfitting on fake labels, the workflow centers mainly on unsupervised clustering.

## Streamlit App

You can run a web app for code quality prediction using Streamlit:

- Install requirements: `pip install -r requirements.txt`
- Run: `streamlit run app.py`

## Usage

To use the project:

- Install needed packages: `pip install -r requirements.txt`.
- Run the scripts in order: `python fetch.py`, `python extract.py`, `python export.py`.
- For machine learning analysis: Open `code_quality.ipynb` to perform preprocessing, PCA, K-Means clustering, and visualization.
- For prediction: Use `predict.py` (uses the same cluster mapping as training).
- Check results in `metrics.csv` and plots.