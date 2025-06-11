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
    interaction_count = 3
    
    new_world = World(grid_width,grid_height,delta_p_det, delta_p_rand)
    new_world.agentes = agents
    agent_spawner = AgentSpawner.AgentSpawner(new_world)
    
    for agent in new_world.agentes:
        agent_spawner.try_respawn(agent)

    new_world.estados.append([ag.clone() for ag in agents])

    if iteration_mode == 0:
        WorldUpdater.update_synchronously_multiple(new_world, iterations)
    else:
        WorldUpdater.update_asynchronously_multiple(new_world, interaction_count, iterations)

    return new_world

def reload_world(world: World, agent_spawner: AgentSpawner,path='drima.json') -> World:
    agents = world.agentes
    entries = load_config(path)
    iterations = entries["numero_de_iteracoes"]
    iteration_mode = entries["modo_da_interacao"]
    world.reset_agents()
    world.estados = []
    interaction_count = 3
    
    for agent in world.agentes:
        agent_spawner.try_respawn(agent)

    world.estados.append([ag.clone() for ag in agents])

    if iteration_mode == 0:
        WorldUpdater.update_synchronously_multiple(world, iterations)
    else:
        WorldUpdater.update_asynchronously_multiple(world, interaction_count, iterations)

    return world

# Salva o mundo em um arquivo json.
def save_world_json(world, config, path='saved_states.json'):
    states_data = []
    for state in world.estados:
        frame = []
        for agent in state:
            frame.append({
                "nome": agent.nome,
                "tipo": agent.tipo,
                "posicao": agent.posicao,
                "padrao_movimento": agent.padrao_movimento
            })
        states_data.append(frame)

    data = {
        "config": config,
        "states": states_data
    }

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)



def load_world_json(path='saved_states.json'):
    with open(path, 'r') as f:
        data = json.load(f)
    return data["config"], data["states"]



