import os
import pandas as pd
from extract import extract  # your extract function
from tqdm import tqdm
from multiprocessing import Pool, TimeoutError as MP_TimeoutError

FOLDER = "datasets"
OUTPUT_CSV = "metrics.csv"
SKIPPED_CSV = "skipped_files.csv"
TIMEOUT = 10  # seconds per file

# Collect all files except CSV
filepaths = [
    os.path.join(FOLDER, f)
    for f in os.listdir(FOLDER)
    if not f.endswith(".csv")
]

def safe_extract(filepath):
    """Extract metrics with exception handling."""
    try:
        return extract(filepath)
    except Exception:
        return None

def process_file(args):
    """Wrapper for multiprocessing with timeout."""
    filepath = args
    with Pool(processes=1) as pool:
        async_result = pool.apply_async(safe_extract, (filepath,))
        try:
            result = async_result.get(timeout=TIMEOUT)
            if result:
                return result, None
            else:
                return None, filepath
        except MP_TimeoutError:
            return None, filepath

def main():
    data = []
    skipped = []

    print(f"Found {len(filepaths)} files. Processing...")

    for result, skipped_file in tqdm(map(process_file, filepaths), total=len(filepaths), desc="Extracting metrics"):
        if result:
            data.append(result)
        elif skipped_file:
            skipped.append(skipped_file)

    # Save metrics
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Metrics saved to {OUTPUT_CSV}")

    # Save skipped files
    if skipped:
        pd.DataFrame({"skipped_file": skipped}).to_csv(SKIPPED_CSV, index=False)
        print(f"⚠️ Skipped {len(skipped)} files. See {SKIPPED_CSV}")

if __name__ == "__main__":
    main()
