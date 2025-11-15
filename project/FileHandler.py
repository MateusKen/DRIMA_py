# project/FileHandler.py
from .Representation import History, Agent
import json
import gzip
import os

def load_config(path='drima.json') -> dict:
    """
    Loads the simulation config file.
    It maintains compatibility with Portuguese keys from old files.
    """
    try:
        with open(path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Return a default config if file does not exist
        config = {
            "largura_da_grade": 20, "altura_da_grade": 20, "delta_p_deterministico": 0.5,
            "delta_p_aleatorio": 0.2, "numero_de_iteracoes": 100, "modo_da_interacao": 0
        }

    # Ensure default keys exist if missing
    config.setdefault('delta_p_mode', 'Global')
    config.setdefault('async_sub_iterations', 1)
    
    # Ensure legacy keys (if missing) have some default
    config.setdefault("largura_da_grade", 20)
    config.setdefault("altura_da_grade", 20)
    config.setdefault("delta_p_deterministico", 0.5)
    config.setdefault("delta_p_aleatorio", 0.2)
    config.setdefault("numero_de_iteracoes", 100)
    config.setdefault("modo_da_interacao", 0)

    return config

def save_config(config, path='drima.json'):
    """Saves the config file (using Portuguese keys for compatibility)."""
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)

def load_history_from_config(path='drima.json') -> History:
    """
    Creates a new History object based on a config file.
    It reads the Portuguese keys from the config.
    """
    config = load_config(path)
    return History(
        config["largura_da_grade"], 
        config["altura_da_grade"],
        config["delta_p_deterministico"], 
        config["delta_p_aleatorio"],
        delta_p_mode=config.get("delta_p_mode", "Global")
    )

def save_history_json(history: History, config, path='saved_states.json'):
    """Saves the history states and config to a JSON file (uncompressed)."""
    states_data = []
    for state in history.states:
        # Saves with English keys
        frame = [
            {
                "name": agent.name, 
                "type": agent.type, 
                "position": agent.position,
                "movement_pattern": agent.movement_pattern,
                "delta_p": agent.delta_p
            } for agent in state
        ]
        states_data.append(frame)

    data = {"config": config, "states": states_data}
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def save_history_json_gzipped(history: History, config, path='saved_states.json.gz'):
    """Saves the history states and config to a gzipped JSON file."""
    states_data = []
    for state in history.states:
        # Saves with English keys
        frame = [
            {
                "name": agent.name, 
                "type": agent.type, 
                "position": list(agent.position),
                "movement_pattern": agent.movement_pattern,
                "delta_p": agent.delta_p
            } for agent in state
        ]
        states_data.append(frame)

    data = {"config": config, "states": states_data}
    
    json_string = json.dumps(data, indent=2)
    json_bytes = json_string.encode('utf-8')
    
    with gzip.open(path, 'wb', compresslevel=9) as f:
        f.write(json_bytes)
    
    print(f"History data saved and compressed to: {path}")

def load_history_json_gzipped(path='saved_states.json.gz') -> dict[str, any]:
    """
    Loads config and states from a gzipped JSON file.
    This function ONLY loads the data; it does not reconstruct agents.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Compressed file not found: {path}")

    with gzip.open(path, 'rb') as f:
        json_bytes = f.read()
    
    json_string = json_bytes.decode('utf-8')
    data = json.loads(json_string)
    
    print(f"History data loaded and decompressed from: {path}")
    
    # Ensure loaded config has recent default values (even if from old save)
    if "config" in data:
        config = data["config"]
        config.setdefault('delta_p_mode', 'Global')
        config.setdefault('async_sub_iterations', 1)
        config.setdefault("largura_da_grade", 20)
        config.setdefault("altura_da_grade", 20)
        config.setdefault("delta_p_deterministico", 0.5)
        config.setdefault("delta_p_aleatorio", 0.2)
        config.setdefault("numero_de_iteracoes", 100)
        config.setdefault("modo_da_interacao", 0)
    
    return data