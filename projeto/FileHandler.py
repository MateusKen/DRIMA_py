# projeto/FileHandler.py
from .Representacao import World, Agent
from .AgentSpawner import AgentSpawner
from .WorldUpdater import WorldUpdater
import json

def load_config(path='drima.json') -> dict:
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Retorna um padrão se o arquivo não existir
        return {
            "largura_da_grade": 20, "altura_da_grade": 20, "delta_p_deterministico": 0.5,
            "delta_p_aleatorio": 0.2, "numero_de_iteracoes": 100, "modo_da_interacao": 0
        }

def save_config(config, path='drima.json'):
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)

# Função descontinuada em favor da inicialização na UI
def load_world(path='drima.json') -> World:
    config = load_config(path)
    return World(
        config["largura_da_grade"], config["altura_da_grade"],
        config["delta_p_deterministico"], config["delta_p_aleatorio"]
    )

def save_world_json(world, config, path='saved_states.json'):
    states_data = []
    for state in world.estados:
        frame = [
            {
                "nome": agent.nome, "tipo": agent.tipo, "posicao": agent.posicao,
                "padrao_movimento": agent.padrao_movimento
            } for agent in state
        ]
        states_data.append(frame)

    data = {"config": config, "states": states_data}
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_world_json(path='saved_states.json'):
    with open(path, 'r') as f:
        data = json.load(f)
    return data["config"], data["states"]