# project/Representation.py
from typing import List
import re

class Agent:
    def __init__(self, name, agent_type, movement_pattern, position, delta_p):
        self.name = name
        self.type = agent_type
        self.movement_pattern = movement_pattern
        self.position = position
        self.delta_p = delta_p  # Agent's local delta_p
        
    def clone(self):
        return Agent(
            name=self.name,
            agent_type=self.type,  # <--- CORRIGIDO
            movement_pattern=self.movement_pattern.copy(),
            position=self.position,
            delta_p=self.delta_p
        )
    
    def normalize_pattern(self):
        """Normalizes the agent's movement pattern so all probabilities sum to 1."""
        total = sum(self.movement_pattern)
        if total == 0: 
            return
        self.movement_pattern = [p / total for p in self.movement_pattern]

    def __repr__(self):
        return f"Agent({self.name}, type={self.type}, pos={self.position})"

class History:
    """
    This class acts as the main container for the simulation, aligning with 
    the TCC's documentation (Metodologia, Ch. 3).
    It stores the configuration and the temporal sequence of "worlds" (states).
    """
    def __init__(self, width, height, delta_p_det, delta_p_rand, delta_p_mode="Global", world_mobility=True, interaction_types=None):
        self.width = width
        self.height = height
        self.delta_p_det = delta_p_det     # Global delta_p D
        self.delta_p_rand = delta_p_rand   # Global delta_p R
        self.delta_p_mode = delta_p_mode   # "Global" or "Local"
        self.agents: List[Agent] = []      # The current state of all agents
        self.states: List[List[Agent]] = [] # The list of all past states (the "history")
        self.world_mobility = world_mobility
        self.interaction_types = interaction_types or []

    def __str__(self):
        return (
            f"width={self.width}\n"
            f"height={self.height}\n"
            f"delta_p_deterministic={self.delta_p_det}\n"
            f"delta_p_random={self.delta_p_rand}\n"
            f"delta_p_mode={self.delta_p_mode}\n"
            f"agents={self.agents}\n"
            f"states_count={len(self.states)}\n"
        )
                        
    def add_agent(self, agent: Agent) -> Agent:
        """Adds an agent to the current list of agents if not already present."""
        if not any(a.name == agent.name for a in self.agents):
            self.agents.append(agent)
        return agent

    def remove_agent(self, agent_name: str) -> Agent | None:
        """Removes an agent from the current list and all past states."""
        agent_to_remove = self.find_agent_by_name(agent_name)
        
        if agent_to_remove:
            self.agents.remove(agent_to_remove)
            # Also remove from past states to maintain consistency
            for state in self.states:
                agent_in_state = next((a for a in state if a.name == agent_name), None)
                if agent_in_state:
                    state.remove(agent_in_state)
            return agent_to_remove
        return None

    def find_agent_index(self, agent_name: str) -> int:
        """Finds the index of an agent by its name in the current agent list."""
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                return i
        return -1

    def find_agent_indices_by_pattern(self, pattern: str) -> List[int]:
        """Finds all agent indices matching a regex pattern."""
        regex = re.compile(pattern)
        return [i for i, agent in enumerate(self.agents) if regex.fullmatch(agent.name)]

    def find_agent_index_in_state(self, agent_name: str, state_index: int) -> int:
        """Finds the index of an agent in a specific historical state."""
        if state_index >= len(self.states):
             return -1
        for i in range(len(self.states[state_index])):
            if self.states[state_index][i].name == agent_name:
                return i
        return -1
        
    def find_agent_by_name(self, agent_name: str) -> Agent | None:
        """Finds the agent object by its name in the current agent list."""
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None

    def is_occupied(self, position: tuple[int, int]) -> bool:
        """Checks if a given position is occupied in the current agent list."""
        return any(agent.position == position for agent in self.agents)

    def reset_agents_to_initial_state(self):
        """Resets the current agents to match the initial state (state 0)."""
        if not self.states: 
            return
        # Clone agents from the first state back to the current state
        self.agents = [ag.clone() for ag in self.states[0]]

    def get_neighbors(self, agent: Agent, radius: int = 1) -> List[Agent]:
        """
        Gets all neighbors of an agent within a given radius,
        using periodic boundary conditions (toroidal topology).
        """
        neighbors = []
        for other in self.agents:
            if other == agent: 
                continue
            
            # Moore neighborhood condition with periodic boundaries
            dx = abs(agent.position[0] - other.position[0])
            dy = abs(agent.position[1] - other.position[1])
            
            # Account for toroidal wrap-around
            dx = min(dx, self.width - dx)
            dy = min(dy, self.height - dy)
            
            if dx <= radius and dy <= radius:
                neighbors.append(other)
        return neighbors

    def __repr__(self):
        return f"History({self.width}x{self.height}, agents={len(self.agents)}, states={len(self.states)})"