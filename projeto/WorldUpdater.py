from projeto import World, MovementHandler, InteractionHandler
import random

class WorldUpdater:
    @staticmethod
    def update_synchronously(world: World):
        InteractionHandler.handle_all_interactions(world, world.delta_p_det, world.delta_p_rand)
        MovementHandler.move_all_agents(world)
        world.estados.append([ag.clone() for ag in world.agentes]) 
   
    @staticmethod
    def update_synchronously_multiple(world: World, iterations: int):
        for _ in range(iterations):
            WorldUpdater.update_synchronously(world)

    @staticmethod
    def update_asynchronously(world: World, iterations: int):
        for _ in range(iterations):
            agent = random.choice(world.agents)
            neighbors = world.get_neighbors(agent)
            if neighbors:
                neighbor = random.choice(neighbors)
                InteractionHandler.handle_interaction(agent, neighbor, world.delta_p_det, world.delta_p_rand)
            MovementHandler.move_agent(agent, world)
        world.estados.append([ag.clone() for ag in world.agentes]) 
    
    @staticmethod
    def update_asynchronously_multiple(world: World, iterations: int, times: int):
     for _ in range(times):
        WorldUpdater.update_asynchronously(iterations)