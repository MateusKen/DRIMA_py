from projeto import World, MovementHandler, InteractionHandler
import random

class WorldUpdater:
    @staticmethod
    def update_synchronously(world: World, delta_p: float):
        InteractionHandler.handle_all_interactions(world, delta_p)
        MovementHandler.move_all_agents(world)

    @staticmethod
    def update_asynchronously(world: World, delta_p: float, iterations: int):
        for _ in range(iterations):
            agent = random.choice(world.agents)
            neighbors = world.get_neighbors(agent)
            if neighbors:
                neighbor = random.choice(neighbors)
                InteractionHandler.handle_interaction(agent, neighbor, delta_p)
            MovementHandler.move_agent(agent, world)