from projeto import World, Agent

class InteractionHandler:
    @staticmethod
    def handle_interaction(agent1: Agent, agent2: Agent, delta_p: float):
        """
        Processa a interação entre dois agentes.
        Só agentes randômicos podem ser influenciados
        """

        if agent1.tipo == "D":
            return
        
        for i in range(len(agent1.padrao_movimento)):
            if agent1.padrao_movimento[i] < agent2.padrao_movimento[i]:
                agent1.padrao_movimento[i] += delta_p

        agent1.normalizar_padroes()

    @staticmethod
    def handle_all_interactions(world: World, delta_p_det: float, delta_p_rand):
        """
        Processa todas as interações no mundo.
        """
        for agent in world.agentes:
            neighbors = world.get_neighbors(agent)
            for neighbor in neighbors:
                if neighbor.tipo == "D":
                    InteractionHandler.handle_interaction(agent, neighbor, delta_p_det)
                else:
                    InteractionHandler.handle_interaction(agent, neighbor, delta_p_rand)

    def handle_all_interactions_2(world: World, delta_p: float):
        """
        Aplica interações entre todos os agentes no mundo (modo síncrono).
        """
        
        already_interacted = set()
        for agent in world.agentes:
            if agent.nome in already_interacted:
                continue

            neighbors = world.get_neighbors(agent)
            for neighbor in neighbors:
                # Exemplo: apenas R (randômicos) são influenciados por D
                if agent.tipo == 'R' and neighbor.tipo == 'D':
                    InteractionHandler.handle_interaction(agent, neighbor, delta_p)
                    already_interacted.add(agent.nome)
                    print(f"{agent.nome} <- {neighbor.nome}")