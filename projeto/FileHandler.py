# projeto/FileHandler.py
from .Representacao import World, Agent
from .AgentSpawner import AgentSpawner
from .WorldUpdater import WorldUpdater
import json
import gzip
import os

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

def save_world_json_gzipped(world, config, path='saved_states.json.gz'):
    """
    Salva o estado do mundo e a configuração em um arquivo JSON comprimido com Gzip.
    
    Args:
        world (object): O objeto World contendo a lista de estados.
                        Espera-se que world.estados seja uma lista de frames,
                        onde cada frame é uma lista de objetos 'agent'
                        com atributos como nome, tipo, posicao, padrao_movimento.
        config (dict): A configuração do mundo.
        path (str): O caminho do arquivo .gz onde os dados serão salvos.
    """
    states_data = []
    for state in world.estados:
        frame = []
        for agent in state:
            # Garante que 'posicao' seja uma lista/tupla serializável, se for um vetor ou objeto
            posicao_serializavel = list(agent.posicao) if hasattr(agent.posicao, '__iter__') else agent.posicao
            
            frame.append(
                {
                    "nome": agent.nome, 
                    "tipo": agent.tipo, 
                    "posicao": posicao_serializavel, # Certifica-se de que é serializável
                    "padrao_movimento": agent.padrao_movimento
                }
            )
        states_data.append(frame)

    data = {"config": config, "states": states_data}
    
    # 1. Serializar o objeto Python para uma string JSON
    json_string = json.dumps(data, indent=2)
    
    # 2. Codificar a string JSON para bytes
    json_bytes = json_string.encode('utf-8')
    
    # 3. Comprimir os bytes usando gzip
    # compresslevel=9 é o nível máximo de compressão (pode ser mais lento)
    gzipped_bytes = gzip.compress(json_bytes, compresslevel=9)
    
    # 4. Escrever os bytes comprimidos no arquivo .gz
    with open(path, 'wb') as f: # 'wb' para escrita binária
        f.write(gzipped_bytes)
    
    print(f"Dados do mundo salvos e comprimidos em: {path}")

def load_world_json(path='saved_states.json'):
    with open(path, 'r') as f:
        data = json.load(f)
    return data["config"], data["states"]

def load_world_json_gzipped(path='saved_states.json.gz') -> dict[str, any]:
    """
    Carrega a configuração e os estados do mundo de um arquivo JSON comprimido com Gzip.
    
    Args:
        path (str): O caminho do arquivo .gz a ser carregado.
        
    Returns:
        tuple: Uma tupla contendo (config, states).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo comprimido não encontrado: {path}")

    # 1. Ler os bytes comprimidos do arquivo .gz
    with open(path, 'rb') as f: # 'rb' para leitura binária
        gzipped_bytes = f.read()
    
    # 2. Descomprimir os bytes
    json_bytes = gzip.decompress(gzipped_bytes)
    
    # 3. Decodificar os bytes para uma string JSON
    json_string = json_bytes.decode('utf-8')
    
    # 4. Desserializar a string JSON para um objeto Python
    data = json.loads(json_string)
    
    print(f"Dados do mundo carregados e descomprimidos de: {path}")
    
    return data