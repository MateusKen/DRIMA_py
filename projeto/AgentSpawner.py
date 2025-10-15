# projeto/AgentSpawner.py
from .Representacao import World, Agent
import random
import re

class AgentSpawner:
    def __init__(self, world: World):
        self.world = world
        # Os contadores dcount e rcount foram removidos daqui para serem dinâmicos.

    def _get_next_name(self, agent_type: str) -> str:
        """
        Verifica todos os agentes existentes do mesmo tipo, encontra o maior número
        em seus nomes e retorna o próximo número sequencial formatado.
        """
        max_num = 0
        # Expressão regular para encontrar o número no final de nomes como "R01", "D15", etc.
        pattern = re.compile(f"^{agent_type}(\d+)$")
        
        for agent in self.world.agentes:
            match = pattern.match(agent.nome)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                    
        next_num = max_num + 1
        return f"{agent_type}{next_num:02d}"

    def find_free_spot(self, start_pos: tuple) -> tuple or None:
        """Encontra um local livre, começando pela posição sugerida."""
        start_pos = (start_pos[0] % self.world.largura, start_pos[1] % self.world.altura)
        
        if not self.world.is_occupied(start_pos):
            return start_pos
        
        for r in range(1, max(self.world.largura, self.world.altura)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) < r and abs(dy) < r: continue # Apenas a borda do raio
                    
                    x = (start_pos[0] + dx) % self.world.largura
                    y = (start_pos[1] + dy) % self.world.altura
                    pos = (x, y)
                    if not self.world.is_occupied(pos):
                        return pos
        return None

    def spawn(self, type: str, moving_pattern: list, position: tuple) -> Agent:
        """Cria um agente com um nome único e o posiciona no mundo."""
        final_pos = self.find_free_spot(position)
        if final_pos is None:
            raise RuntimeError("Não há espaço livre no mundo para adicionar um novo agente.")
        
        # Geração de nome dinâmica e corrigida
        name = self._get_next_name(type)

        new_agent = Agent(name, type, moving_pattern, final_pos)
        self.world.adicionar_agente(new_agent)
        return new_agent

    def spawn_randomly(self, type: str = None, moving_pattern: list = None, position: tuple = None) -> Agent:
        """
        Ponto de entrada principal para criar agentes com valores padrão se não forem fornecidos.
        """
        if type is None:
            type = random.choice(('D', 'R'))

        if moving_pattern is None:
            moving_pattern = [0.0] * 9
            if type == 'D':
                moving_pattern[random.randint(0, 8)] = 1.0
            else: # 'R'
                pattern = [random.random() for _ in range(9)]
                total = sum(pattern)
                moving_pattern = [p / total for p in pattern] if total > 0 else [1/9]*9

        if position is None:
            x = random.randint(0, self.world.largura - 1)
            y = random.randint(0, self.world.altura - 1)
            position = (x, y)
        
        # Chama o método spawn corrigido
        return self.spawn(type, moving_pattern, position)