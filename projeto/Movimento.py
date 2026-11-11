import random
from projeto import World, Agent
from . import TrueRNGSource

class MovementHandler:
    @staticmethod
    def move_agent(agent: Agent, world: World):
        """
        Move um agente com base no seu padrão de movimento.
        """
        # Lista de direções possíveis (Lembrando que o Y é invertido)
        directions = [
            (1, 0),  # E
            (1, -1),  # NE
            (0, -1),  # N
            (-1, -1),  # NW
            (-1, 0),  # W
            (-1, 1),  # SW
            (0, 1),  # S
            (1, 1),  # SE
            (0, 0),  # X (sem movimento)
        ]
        if agent.tipo == "D":
            # Determinístico: move-se na direção com probabilidade máxima
            direction = directions[agent.padrao_movimento.index(max(agent.padrao_movimento))]
        elif agent.tipo == "R":
            # Randômico: escolhe direção com base nas probabilidades
            direction = random.choices(directions, weights=agent.padrao_movimento, k=1)[0]
        else:
            return

        # Atualiza a posição do agente
        new_x = (agent.posicao[0] + direction[0]) % world.altura
        new_y = (agent.posicao[1] + direction[1]) % world.largura
        agent.posicao = (new_x, new_y)

    @staticmethod
    def move_all_agents(world: World):
        """
        Move todos os agentes no mundo.
        """
        for agente in world.agentes:
            MovementHandler.move_agent(agente, world)

    @staticmethod
    def move_agent_true_rng(agent: Agent, world: World):

        rng = TrueRNGSource.get_generator()

        directions = [
            (1, 0),  # E
            (1, -1),  # NE
            (0, -1),  # N
            (-1, -1),  # NW
            (-1, 0),  # W
            (-1, 1),  # SW
            (0, 1),  # S
            (1, 1),  # SE
            (0, 0),  # X (sem movimento)
        ]
        if agent.tipo == "D":
            direction = directions[agent.padrao_movimento.index(max(agent.padrao_movimento))]
        elif agent.tipo == "R":
            direction = rng.choices(directions, weights=agent.padrao_movimento, k=1)[0]
        else:
            return

        new_x = (agent.posicao[0] + direction[0]) % world.altura
        new_y = (agent.posicao[1] + direction[1]) % world.largura
        agent.posicao = (new_x, new_y)

    @staticmethod
    def move_all_agents_true_rng(world: World):
        for agente in world.agentes:
            MovementHandler.move_agent_true_rng(agente, world)