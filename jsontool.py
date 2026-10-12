import json
def get_value(file: str, key: str):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[key]
    except FileNotFoundError:
        print("File not found")
        return None
def write_value(file: str, key: str, value):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data[key] = value
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        print("File not found")
        return None
