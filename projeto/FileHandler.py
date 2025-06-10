from projeto import World, WorldUpdater, AgentSpawner
import json
import os

def load_config(path='drima.json') -> dict:
    with open(path, 'r') as f:
        config = json.load(f)
    return config


# Salva as configurações em um arquivo json
def save_config(config, path='drima.json'):
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)


# Carrega o mundo
def load_world(path='drima.json') -> World:
    entries = load_config(path)
    grid_width = entries["altura_da_grade"]
    grid_height = entries["largura_da_grade"]
    delta_p_det = entries["delta_p_deterministico"]
    delta_p_rand = entries["delta_p_aleatorio"]
    iterations = entries["numero_de_iteracoes"]
    iteration_mode = entries["modo_da_interacao"]
    
    new_world = World(grid_width,grid_height,delta_p_det,delta_p_rand)


    

    return new_world

# Carrega o mundo permitindo passar agentes pre-existentes
def load_world_2(agents,path='drima.json') -> World:
    entries = load_config(path)
    grid_width = entries["altura_da_grade"]
    grid_height = entries["largura_da_grade"]
    delta_p_det = entries["delta_p_deterministico"]
    delta_p_rand = entries["delta_p_aleatorio"]
    iterations = entries["numero_de_iteracoes"]
    iteration_mode = entries["modo_da_interacao"]
    
    new_world = World(grid_width,grid_height,delta_p_det, delta_p_rand)
    new_world.agentes = agents
    agent_spawner = AgentSpawner.AgentSpawner(new_world)
    
    for agent in new_world.agentes:
        agent_spawner.try_respawn(agent)

    new_world.estados.append([ag.clone() for ag in agents])

    if iteration_mode == 0:
        WorldUpdater.update_synchronously_multiple(new_world, iterations)
    

    return new_world

# Salva o mundo em um arquivo json.
import json
import os

def save_world_json(world, config, path='saved_states.json'):
    """
    Salva as configurações do mundo e os estados (padrões de movimento dos agentes) em JSON.
    :param world: instância de World contendo os estados.
    :param config: dicionário carregado do drima.json.
    :param path: nome do arquivo de saída.
    """
    # Extrair apenas os padroes de movimento de cada agente por estado
    states_data = []
    for state in world.estados:
        state_snapshot = [agent.padrao_movimento for agent in state]
        states_data.append(state_snapshot)

    data = {
        "config": config,
        "states": states_data
    }

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Config and states saved to: {os.path.abspath(path)}")



def load_world_json(path='saved_states.json'):
    with open(path, 'r') as f:
        data = json.load(f)
    return data["config"], data["states"]



