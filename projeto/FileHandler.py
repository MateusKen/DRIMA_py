import json

def load_config(path='config.json'):
    with open(path, 'r') as f:
        config = json.load(f)
    return config


def save_config(config, path='config.json'):
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)