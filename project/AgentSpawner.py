# project/AgentSpawner.py
from .Representation import History, Agent
import random
import re

class AgentSpawner:
    def __init__(self, history: History):
        self.history = history

    def _get_next_name(self, agent_type: str) -> str:
        """
        Finds the next sequential name for a given agent type (e.g., "D01", "R05").
        Checks all agents in the *current* agent list.
        """
        max_num = 0
        pattern = re.compile(f"^{agent_type}(\d+)$")
        
        for agent in self.history.agents:
            match = pattern.match(agent.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                    
        next_num = max_num + 1
        return f"{agent_type}{next_num:02d}"

    def find_free_spot(self, start_pos: tuple) -> tuple | None:
        """
        Finds a free spot on the grid, starting from start_pos 
        and searching outwards.
        """
        start_pos = (start_pos[0] % self.history.width, start_pos[1] % self.history.height)
        
        if not self.history.is_occupied(start_pos):
            return start_pos
        
        # Spiral search outwards
        for r in range(1, max(self.history.width, self.history.height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) < r and abs(dy) < r: 
                        continue  # Only check the outer ring
                    
                    x = (start_pos[0] + dx) % self.history.width
                    y = (start_pos[1] + dy) % self.history.height
                    pos = (x, y)
                    if not self.history.is_occupied(pos):
                        return pos
        return None # No free space found

    def spawn(self, agent_type: str, movement_pattern: list, position: tuple, delta_p: float) -> Agent:
        """Creates a new agent with a unique name and adds it to the history's current agent list."""
        final_pos = self.find_free_spot(position)
        if final_pos is None:
            raise RuntimeError("No free space in the world to add a new agent.")
        
        name = self._get_next_name(agent_type)

        new_agent = Agent(name, agent_type, movement_pattern, final_pos, delta_p)
        self.history.add_agent(new_agent)
        return new_agent

    def spawn_randomly(self, agent_type: str = None, movement_pattern: list = None, position: tuple = None, delta_p: float = None) -> Agent:
        """
        Main entry point for creating agents with random defaults if not provided.
        """
        if agent_type is None:
            agent_type = random.choice(('D', 'R'))

        if movement_pattern is None:
            movement_pattern = [0.0] * 9
            if agent_type == 'D':
                movement_pattern[random.randint(0, 8)] = 1.0
            else: # 'R'
                pattern = [random.random() for _ in range(9)]
                total = sum(pattern)
                movement_pattern = [p / total for p in pattern] if total > 0 else [1/9]*9

        if position is None:
            x = random.randint(0, self.history.width - 1)
            y = random.randint(0, self.history.height - 1)
            position = (x, y)
        
        if delta_p is None:
            if agent_type == 'D':
                delta_p = random.uniform(0.1, 0.9)
            else: # 'R'
                delta_p = random.uniform(0.01, 0.1)

        return self.spawn(agent_type, movement_pattern, position, delta_p)