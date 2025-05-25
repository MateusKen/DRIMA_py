from projeto import World, WorldUpdater, AgentSpawner
import json

def load_config(path='drima.json') -> dict:
    with open(path, 'r') as f:
        config = json.load(f)
    return config


def save_config(config, path='drima.json'):
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)


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
