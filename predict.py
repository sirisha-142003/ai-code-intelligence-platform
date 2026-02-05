from extract import extract
import joblib
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


def predict_code_quality(filepath, metrics_csv='data/metrics.csv'):
    # Load trained models
    scaler = joblib.load("data/scaler.pkl")
    pca = joblib.load("data/pca.pkl")
    kmeans = joblib.load("data/kmeans.pkl")
    cluster_mapping = joblib.load("data/cluster_mapping.pkl")

    # Load training feature columns
    train_df = pd.read_csv(metrics_csv)
    cols_to_drop = [col for col in ["filename", "language"] if col in train_df.columns]
    feature_columns = [col for col in train_df.columns if col not in cols_to_drop]

    # Extract features from new code
    new_code_features = extract(filepath)

    # Convert to DataFrame
    X_new_df = pd.DataFrame([new_code_features], columns=feature_columns)

    # Ensure correct datatype
    if "has_docstring" in X_new_df.columns:
        X_new_df["has_docstring"] = X_new_df["has_docstring"].astype(int)

    # Scale → PCA → Predict
    X_new_scaled = scaler.transform(X_new_df)
    X_new_pca = pca.transform(X_new_scaled)

    cluster = kmeans.predict(X_new_pca)[0]
    label = cluster_mapping.get(cluster, "Unknown")

    return cluster, label
