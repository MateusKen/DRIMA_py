from projeto import World, MovementHandler, InteractionHandler
import random

class WorldUpdater:
    @staticmethod
    def update_synchronously(world: World):
        # MODIFICAÇÃO: A chamada agora só passa o 'world'
        InteractionHandler.handle_all_interactions(world)
        MovementHandler.move_all_agents(world)
        world.estados.append([ag.clone() for ag in world.agentes]) 
   
    @staticmethod
    def update_synchronously_multiple(world: World, iterations: int):
        for _ in range(iterations):
            WorldUpdater.update_synchronously(world)

    @staticmethod
    def update_asynchronously(world: World, iterations: int):
        all_agents = world.agentes
    
        # Se não houver agentes, não faz nada
        if not all_agents:
            return

        # 1. Determina quantos agentes únicos escolher.
        # Não podemos escolher mais agentes únicos do que o total disponível.
        num_to_pick = min(iterations, len(all_agents))

        # 2. Seleciona 'num_to_pick' agentes únicos da lista
        agents_to_update = random.sample(all_agents, k=num_to_pick)

        # 3. Itera sobre a lista de agentes únicos (em vez de 'for _ in range(iterations)')
        
        # MODIFICAÇÃO: Verifica o modo uma vez antes do loop
        use_local_delta_p = (world.delta_p_mode == "Local")

        for agent in agents_to_update:
            # O resto da sua lógica de interação e movimento permanece
            neighbors = world.get_neighbors(agent)
            if neighbors:
                neighbor = random.choice(neighbors)
                
                delta_p_to_use = 0.0
                
                if use_local_delta_p:
                    # Usa o delta_p local do agente INFLUENCIADOR (neighbor)
                    delta_p_to_use = neighbor.delta_p
                else:
                    # Usa o delta_p global baseado no tipo do influenciador
                    if neighbor.tipo == "D":
                        delta_p_to_use = world.delta_p_det
                    else:
                        delta_p_to_use = world.delta_p_rand
                
                # Aplica a interação com o valor de delta_p decidido
                InteractionHandler.handle_interaction(agent, neighbor, delta_p_to_use)

            MovementHandler.move_agent(agent, world)

    
    @staticmethod
    def update_asynchronously_multiple(world: World, iterations: int, times: int):
     for _ in range(times):
        WorldUpdater.update_asynchronously(world,iterations)