# project/WorldUpdater.py
from .Representation import History
from .Movement import MovementHandler
from .Interactions import InteractionHandler
import random

class WorldUpdater:
    @staticmethod
    def update_synchronously(history: History):
        """
        Performs one synchronous update step:
        1. All agents interact (based on state t).
        2. All agents move (based on state t).
        3. A new state (t+1) is saved to the history.
        """
        # 1. Handle interactions based on current agent state
        InteractionHandler.handle_all_interactions(history)
        
        # 2. Move all agents
        MovementHandler.move_all_agents(history)
        
        # 3. Save the new state
        history.states.append([ag.clone() for ag in history.agents]) 
   
    @staticmethod
    def update_synchronously_multiple(history: History, iterations: int):
        """Performs multiple synchronous update steps."""
        for _ in range(iterations):
            WorldUpdater.update_synchronously(history)

    @staticmethod
    def update_asynchronously(history: History, iterations: int):
        """
        Performs an asynchronous update.
        'iterations' number of agents are randomly chosen to interact and move.
        A single new state is saved at the end.
        """
        all_agents = history.agents
    
        if not all_agents:
            return

        # 1. Determine how many unique agents to pick.
        num_to_pick = min(iterations, len(all_agents))

        # 2. Select 'num_to_pick' unique agents from the list.
        agents_to_update = random.sample(all_agents, k=num_to_pick)

        # 3. Iterate over the list of unique agents.
        
        # Check the delta_p mode once before the loop
        use_local_delta_p = (history.delta_p_mode == "Local")

        for agent in agents_to_update:
            # Agent interacts with one random neighbor
            neighbors = history.get_neighbors(agent)
            if neighbors:
                neighbor = random.choice(neighbors)
                
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
                
                # Apply the interaction
                InteractionHandler.handle_interaction(agent, neighbor, delta_p_to_use)

            # Agent moves
            MovementHandler.move_agent(agent, history)
            
        # 4. After all async updates, save the resulting state
        history.states.append([ag.clone() for ag in history.agents])

    
    @staticmethod
    def update_asynchronously_multiple(history: History, iterations: int, times: int):
     """
     Performs 'times' number of asynchronous update steps.
     In each step, 'iterations' agents are updated.
     """
     for _ in range(times):
        WorldUpdater.update_asynchronously(history, iterations)