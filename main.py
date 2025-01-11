import requests
import json
import time
import os
import concurrent.futures

ACCESS_TOKEN = "token"
API_VERSION = "5.131"
BASE_URL = "https://api.vk.com/method/"
OUTPUT_FILE = "vk_groups_filtered.json"

def generate_group_id(start_id, batch_size):
    group_ids = []
    for i in range(batch_size):
        group_ids.append(f"public{start_id + i}")
    return group_ids

def get_groups_by_ids(group_ids):
    try:
        params = {
            "group_ids": ",".join(group_ids),
            "fields": "city,members_count,description,photo_200",
            "access_token": ACCESS_TOKEN,
            "v": API_VERSION
        }
        response = requests.get(BASE_URL + "groups.getById", params=params)
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                return [
                    {
                        "external_id": group.get("id"),
                        "username": group.get("screen_name"),
                        "full_name": group.get("name"),
                        "bio": group.get("description"),
                        "avatar_url": group.get("photo_200"),
                        "city": group.get("city", {}).get("title") if group.get("city") else None,
                        "followers": group.get("members_count"),
                    }
                    for group in data["response"]
                ]
            else:
                print("API Error:", data.get("error", {}).get("error_msg", "Unknown error"))
        else:
            print("Request error:", response.status_code)
    except Exception:
        print("Fetching error:")
    return []

def save_to_json(data, filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []
        existing_data.extend(data)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
        print(f"Data saved successfully")
    except Exception:
        print("Saving error:")

def main():
    start_id = 1
    end_id = 1000
    batch_size = 10 
    delay = 0
    max_threads = 10

    while start_id <= end_id:
        print(f"Processing from {start_id} to {start_id + batch_size * max_threads - 1}")
        group_id_batches = [
            generate_group_id(start_id + i * batch_size, batch_size)
            for i in range(max_threads)
        ]
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
            future_to_batch = {
                executor.submit(get_groups_by_ids, batch): batch for batch in group_id_batches
            }
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    result = future.result()
                    if result:
                        results.extend(result)
                except Exception:
                    print(f'Error {Exception}')
        if results:
            save_to_json(results, OUTPUT_FILE)
        else:
            print('Cant fetch INFO about public')
        
        start_id += batch_size * max_threads
        print(f'Waiting {delay} seconds before the next operation')
        time.sleep(delay)
            

if __name__ == "__main__":
    main()
