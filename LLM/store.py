import json
import os
from threading import Lock

lock = Lock()

def save_to_json_file(data, filename='data.json'):
    with lock:
        if os.path.exists(filename):
            with open(filename, 'r+') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
                existing_data.append(data)
                f.seek(0)
                json.dump(existing_data, f, indent=4)
        else:
            with open(filename, 'w') as f:
                json.dump([data], f, indent=4)

def get_latest_data(filename='data.json'):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        try:
            existing_data = json.load(f)
            if not existing_data:
                return None
            return existing_data[-1]  
        except json.JSONDecodeError:
            return None
