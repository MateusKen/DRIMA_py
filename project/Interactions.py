# project/Interactions.py
from .Representation import History, Agent

class InteractionHandler:
    @staticmethod
    def handle_interaction(agent1: Agent, agent2: Agent, delta_p: float):
        """
        Processes the interaction between two agents.
        Only Random (R) agents (agent1) can be influenced.
        """
        # According to DRIMA model (Oliveira, 2010), 
        # Deterministic (D) agents are immutable attractors.
        if agent1.type == "D":
            return
        
        # The R agent (agent1) is "attracted" to the other agent's pattern.
        for i in range(len(agent1.movement_pattern)):
            if agent1.movement_pattern[i] < agent2.movement_pattern[i]:
                agent1.movement_pattern[i] += delta_p

        # Re-normalize probabilities after influence
        agent1.normalize_pattern()

    @staticmethod
    def handle_all_interactions(history: History):
        """
        Processes all interactions in the world (SYNCHRONOUS MODE).
        Checks history.delta_p_mode to decide which delta_p to use.
        """
        
        use_local_delta_p = (history.delta_p_mode == "Local")
        
        # Create a snapshot of agents to calculate interactions
        agents_at_start_of_step = history.agents
        
        for agent in agents_at_start_of_step:
            # Get neighbors from the same snapshot
            neighbors = history.get_neighbors(agent) 
            
            for neighbor in neighbors:
                
                delta_p_to_use = 0.0
                
                if use_local_delta_p:
                    # Use the local delta_p of the INFLUENCER (neighbor)
                    delta_p_to_use = neighbor.delta_p
                else:
                    # Use the global delta_p based on the influencer's type
                    if neighbor.type == "D":
                        delta_p_to_use = history.delta_p_det
                    else:
                        delta_p_to_use = history.delta_p_rand

                # Apply the interaction with the decided delta_p value
                # Note: handle_interaction ensures only R agents are modified.
                InteractionHandler.handle_interaction(agent, neighbor, delta_p_to_use)

    def handle_all_interactions_2(history: History, delta_p: float):
        """
        (Legacy function) Applies interactions between all agents (synchronous).
        """
        already_interacted = set()
        for agent in history.agents:
            if agent.name in already_interacted:
                continue

            neighbors = history.get_neighbors(agent)
            for neighbor in neighbors:
                # Example: only R (random) are influenced by D
                if agent.type == 'R' and neighbor.type == 'D':
                    # This function would also need to check history.delta_p_mode
                    InteractionHandler.handle_interaction(agent, neighbor, delta_p)
                    already_interacted.add(agent.name)
                    print(f"{agent.name} <- {neighbor.name}")