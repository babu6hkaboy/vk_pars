import requests
import json
import time
import os

ACCESS_TOKEN = "token"
API_VERSION = "5.131"
BASE_URL = "https://api.vk.com/method/"
OUTPUT_FILE = "vk_groups_filtered.json"

def generate_group_id(start_id, batch_size):
    group_ids = []
    for i in range(batch_size):
        group_ids.append(f"club{str(start_id + i).zfill(6)}")
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
                print("Ошибка API:", data.get("error", {}).get("error_msg", "Неизвестная ошибка"))
        else:
            print("Ошибка реквеста:", response.status_code)
    except Exception as e:
        print("Ошибка получения:", e)
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
        print(f"Данные сохранились")
    except Exception as e:
        print("Ошибка сохранения:", e)

def main():
    start_id = 1
    end_id = 100
    batch_size = 10
    delay = 5

    while start_id <= end_id:
        print(f"Старт обработки с {start_id} по {start_id + batch_size - 1}")
        group_ids = generate_group_id(start_id, batch_size)
        groups_info = get_groups_by_ids(group_ids)
        if groups_info:
            save_to_json(groups_info, OUTPUT_FILE)
        else:
            print("Баг не удалось получить информацию")
        start_id += batch_size
        print(f"Await {delay} секунд ")
        time.sleep(delay)

if __name__ == "__main__":
    main()
