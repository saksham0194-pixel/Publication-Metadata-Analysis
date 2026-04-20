import requests
import time
from multiprocessing import Pool
from collections import Counter

# Configuration
BASE_URL = "http://72.60.221.150:8080"
STUDENT_ID = "MDS202508"  

def get_secret_key():
    # We add a loop here to keep trying if the connection times out
    while True:
        try:
            # We set a timeout of 10 seconds so it doesn't wait forever
            response = requests.post(f"{BASE_URL}/login", json={"student_id": STUDENT_ID}, timeout=10)
            return response.json().get("secret_key")
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            print("Server busy, retrying login in 2 seconds...")
            time.sleep(5)

def mapper(filename_chunk):
    secret_key = get_secret_key()
    counts = Counter()
    for filename in filename_chunk:
        success = False
        while not success:
            res = requests.post(f"{BASE_URL}/lookup", json={"secret_key": secret_key, "filename": filename})
            if res.status_code == 200:
                title = res.json().get("title", "")
                if title:
                    first_word = title.split()[0]
                    counts[first_word] += 1
                success = True
            elif res.status_code == 429:
                time.sleep(1)  # Handle throttling
            else:
                success = True # Skip on other errors
    return counts

def verify_top_10(top_10_list):
    secret_key = get_secret_key()
    res = requests.post(f"{BASE_URL}/verify", json={"secret_key": secret_key, "top_10": top_10_list})
    print(res.json())

if __name__ == "__main__":
    filenames = [f"pub_{i}.txt" for i in range(1000)]
    chunk_size = 100
    chunks = [filenames[i:i + chunk_size] for i in range(0, 1000, chunk_size)]
    
    with Pool(processes=4) as pool:
        results = pool.map(mapper, chunks)
    
    total_counts = Counter()
    for r in results:
        total_counts.update(r)
    
    top_10 = [word for word, count in total_counts.most_common(10)]
    verify_top_10(top_10)