# project/Movement.py
import random
from .Representation import History, Agent

class MovementHandler:
    @staticmethod
    def move_agent(agent: Agent, history: History):
        """
        Moves a single agent based on its movement pattern.
        Applies periodic boundary conditions (toroidal topology).
        """
        # List of possible directions (Note: Y is often inverted in grids)
        # (dx, dy)
        directions = [
            (1, 0),   # E
            (1, -1),  # NE
            (0, -1),  # N
            (-1, -1), # NW
            (-1, 0),  # W
            (-1, 1),  # SW
            (0, 1),   # S
            (1, 1),   # SE
            (0, 0),   # X (no movement)
        ]
        
        if agent.type == "D":
            # Deterministic: moves in the direction with maximum probability
            max_prob = max(agent.movement_pattern)
            direction_index = agent.movement_pattern.index(max_prob)
            direction = directions[direction_index]
        elif agent.type == "R":
            # Random: chooses direction based on weights
            direction = random.choices(directions, weights=agent.movement_pattern, k=1)[0]
        else:
            # Unknown agent type, no movement
            return

        # Update agent's position with periodic boundary conditions
        # % history.width ensures wrap-around (toroidal)
        new_x = (agent.position[0] + direction[0]) % history.width
        new_y = (agent.position[1] + direction[1]) % history.height
        agent.position = (new_x, new_y)

    @staticmethod
    def move_all_agents(history: History):
        """
        Moves all agents in the current state of the history.
        """
        for agent in history.agents:
            MovementHandler.move_agent(agent, history)