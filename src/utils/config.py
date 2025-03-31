import json

def load_json(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as f:
        return json.load(f)

def load_proxies(file_path):
    data = load_json(file_path)
    return [proxy['proxy'] for proxy in data if proxy.get('scheme') == 'https']
