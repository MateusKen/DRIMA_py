# python
from projeto import World, MovementHandler, InteractionHandler
from . import TrueRNGSource
import random

class WorldUpdater:
    @staticmethod
    def update_synchronously(world: World):
        # Passa os valores de delta_p globais armazenados no world
        InteractionHandler.handle_all_interactions(world) # , world.delta_p_det, world.delta_p_rand
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
        use_local_delta_p = (world.delta_p_mode == "Local")

        for agent in agents_to_update:
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
            WorldUpdater.update_asynchronously(world, iterations)

    @staticmethod
    def update_synchronously_true_rng(world: World):
        InteractionHandler.handle_all_interactions(world)
        MovementHandler.move_all_agents_true_rng(world)
        world.estados.append([ag.clone() for ag in world.agentes])

    @staticmethod
    def update_synchronously_multiple_true_rng(world: World, iterations: int):
        for _ in range(iterations):
            WorldUpdater.update_synchronously_true_rng(world)

    @staticmethod
    def update_asynchronously_true_rng(world: World, iterations: int):
        rng = TrueRNGSource.get_generator()
        all_agents = world.agentes

        if not all_agents:
            return

        num_to_pick = min(iterations, len(all_agents))
        agents_to_update = rng.sample(all_agents, k=num_to_pick)

        use_local_delta_p = (world.delta_p_mode == "Local")

        for agent in agents_to_update:
            neighbors = world.get_neighbors(agent)
            if neighbors:
                neighbor = rng.choice(neighbors)

                delta_p_to_use = 0.0

                if use_local_delta_p:
                    delta_p_to_use = neighbor.delta_p
                else:
                    if neighbor.tipo == "D":
                        delta_p_to_use = world.delta_p_det
                    else:
                        delta_p_to_use = world.delta_p_rand

                InteractionHandler.handle_interaction(agent, neighbor, delta_p_to_use)

            MovementHandler.move_agent_true_rng(agent, world)

    @staticmethod
    def update_asynchronously_multiple_true_rng(world: World, iterations: int, times: int):
        for _ in range(times):
            WorldUpdater.update_asynchronously_true_rng(world, iterations)