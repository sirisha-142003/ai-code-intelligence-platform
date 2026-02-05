import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def preprocess_dataset(csv_path):
    df = pd.read_csv(csv_path)
    cols_to_drop = [col for col in ["filename", "language", "quality"] if col in df.columns]
    X = df.drop(columns=cols_to_drop)
    
    for col in ["has_docstring"]:
        if col in X.columns:
            X[col] = X[col].astype(int)
            
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return df, X_scaled, scaler

def reduce_dimensions(X, n_components=10):
    pca = PCA(n_components=n_components, random_state=42)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca
