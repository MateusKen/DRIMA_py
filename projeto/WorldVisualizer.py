import matplotlib.pyplot as plt
from projeto import World

class WorldVisualizer:
    @staticmethod
    def plot_world(world: World):
        """
        Plota o estado atual do mundo com os agentes.
        """
        plt.figure(figsize=(8, 8))
        for agente in world.agentes:
            if agente.tipo == "D":
                plt.scatter(agente.posicao[0], agente.posicao[1], color="red", label="D-agent")
            else:
                plt.scatter(agente.posicao[0], agente.posicao[1], color="blue", label="R-agent")
        plt.xlim(0, world.altura)
        plt.ylim(0, world.largura)
        plt.grid(True)
        plt.show()