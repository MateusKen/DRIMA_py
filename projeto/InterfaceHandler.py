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
    def handle_all_interactions(world: World):
        """
        Processa todas as interações no mundo (MODO SÍNCRONO).
        MODIFICAÇÃO: Não recebe mais delta_p_det/rand.
        Verifica world.delta_p_mode para decidir qual delta_p usar.
        """
        
        use_local_delta_p = (world.delta_p_mode == "Local")

        for agent in world.agentes:
            neighbors = world.get_neighbors(agent)
            for neighbor in neighbors:
                
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
                    # Esta função não está sendo usada pela main.py,
                    # mas se estivesse, precisaria ser atualizada
                    # para também checar o world.delta_p_mode
                    InteractionHandler.handle_interaction(agent, neighbor, delta_p)
                    already_interacted.add(agent.nome)
                    print(f"{agent.nome} <- {neighbor.nome}")