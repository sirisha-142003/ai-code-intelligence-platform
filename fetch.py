import os
import requests
import base64
import time
import hashlib
import csv
import random

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_DIR = "datasets"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.csv")
NUM_FILES_PER_LANG = 2000
FILES_PER_KEYWORD = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

seen_hashes = set()
if os.path.exists(META_FILE):
    with open(META_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seen_hashes.add(row["content_hash"])

# Keywords for searching repos
KEYWORDS = [
    'codeforces', 'leetcode', 'hackerrank', 'codechef', 'codewars',
    "data-structures", "algorithms", "interview-prep",
    "django", "flask", "fastapi", "rest-api", "web-scraper",
    "tensorflow", "pytorch", "scikit-learn", "data-analysis", "ml-projects",
    "automation", "scripts", "cli-tool", "python-utils",
    "python-tutorial", "python-examples", "beginner-python", "learn-python",
    "javascript project", "js project", "nodejs", "react", "vue", "angular",
    "express", "nextjs", "nuxtjs", "svelte",
    "frontend", "backend", "fullstack", "web-app", "rest-api",
    "beginner-javascript", "javascript-examples", "learn-javascript",
    "university", "practice", "tutorial", "ai"
]

def search_files(query, per_page=50, page=1):
    url = f"https://api.github.com/search/code?q={query}&per_page={per_page}&page={page}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("items", [])
    return []

def download_file(repo_full_name, path):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    content = r.json().get("content", "")
    encoding = r.json().get("encoding", "")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    return None

def collect_files():
    start_time = time.time()
    collected = {"Python": len([h for h in seen_hashes if h.endswith(".py")]),
                 "JavaScript": len([h for h in seen_hashes if h.endswith(".js")])}

    with open(META_FILE, "a", newline="", encoding="utf-8") as meta:
        writer = csv.writer(meta)
        if os.stat(META_FILE).st_size == 0:
            writer.writerow(["local_file", "repo_url", "original_path", "content_hash", "download_time", "keyword", "language"])

        for lang in ["Python", "JavaScript"]:
            lang_files_needed = NUM_FILES_PER_LANG - collected[lang]
            if lang_files_needed <= 0:
                continue

            while collected[lang] < NUM_FILES_PER_LANG:
                random.shuffle(KEYWORDS)

                for kw in KEYWORDS:
                    page = 1
                    files_downloaded = 0

                    while files_downloaded < FILES_PER_KEYWORD:
                        files = search_files(f"{kw} language:{lang}", per_page=50, page=page)
                        if not files:
                            break

                        for item in files:
                            repo_name = item["repository"]["full_name"]
                            repo_url = item["repository"]["html_url"]
                            path = item["path"]

                            try:
                                content = download_file(repo_name, path)
                                if not content or len(content.splitlines()) < 10:
                                    continue

                                content_hash = hashlib.md5(content.encode()).hexdigest()
                                if content_hash in seen_hashes:
                                    continue
                                seen_hashes.add(content_hash)

                                repo_safe = repo_name.replace("/", "_")
                                local_name = f"{repo_safe}_{path.split('/')[-1]}"
                                save_path = os.path.join(OUTPUT_DIR, local_name)
                                with open(save_path, "w", encoding="utf-8") as f:
                                    f.write(content)

                                writer.writerow([local_name, repo_url, path, content_hash,
                                                 round(time.time() - start_time, 2), kw, lang])
                                collected[lang] += 1
                                files_downloaded += 1
                                print(f"[+] Saved {local_name} ({collected[lang]}/{NUM_FILES_PER_LANG}) [{kw}] [{lang}]")

                                if collected[lang] >= NUM_FILES_PER_LANG or files_downloaded >= FILES_PER_KEYWORD:
                                    break

                            except Exception:
                                continue

                        page += 1
                        time.sleep(0.1)

                    if collected[lang] >= NUM_FILES_PER_LANG:
                        break

    total_time = round(time.time() - start_time, 2)
    print(f"\n✅ Done! Collected Python: {collected['Python']} | JavaScript: {collected['JavaScript']} in {total_time}s")

if __name__ == "__main__":
    collect_files()
