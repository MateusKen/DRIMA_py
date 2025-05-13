from projeto import World, Agent

class InteractionHandler:
    @staticmethod
    def handle_interaction(agent1: Agent, agent2: Agent, delta_p: float):
        """
        Processa a interação entre dois agentes.
        """
        for i in range(len(agent1.padrao_movimento)):
            if agent1.padrao_movimento[i] < agent2.padrao_movimento[i]:
                agent1.padrao_movimento[i] += delta_p
            agent1.normalizar_padroes()

    @staticmethod
    def handle_all_interactions(world: World, delta_p: float):
        """
        Processa todas as interações no mundo.
        """
        for agent in world.agentes:
            neighbors = world.get_neighbors(agent)
            for neighbor in neighbors:
                InteractionHandler.handle_interaction(agent, neighbor, delta_p)