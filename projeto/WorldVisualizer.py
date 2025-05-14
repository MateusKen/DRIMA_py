import matplotlib.pyplot as plt
import matplotlib.collections as collections
from projeto import World

class WorldVisualizer:
    @staticmethod
    def update(world: World, figure: plt.Figure, agents_points: list[collections.PatchCollection]):
        """
        Atualiza a Visualizacao
        """
        
        for i, agente in enumerate(world.agentes):
            agents_points[i].set_offsets([agente.posicao])

        figure.canvas.draw()
        figure.canvas.flush_events()
        plt.pause(0.5)

    @staticmethod
    def plot_world(world: World) -> tuple[plt.Figure, list[collections.PathCollection]]:
        """
        Plota o estado atual do mundo com os agentes.
        """
        agents_points = [] 
        plt.ion()
        fig = plt.figure(figsize=(8, 8))
        for agente in world.agentes:
            if agente.tipo == "D":
                point = plt.scatter(agente.posicao[0], agente.posicao[1], color="red", label="D-agent")
                agents_points.append(point)
            else:
                point = plt.scatter(agente.posicao[0], agente.posicao[1], color="blue", label="R-agent")
                agents_points.append(point)
                point.set_array

        plt.xlim(0, world.altura)
        plt.ylim(0, world.largura)
        plt.grid(True)
        fig.canvas.draw()
        return (fig,agents_points)

    @staticmethod
    def keep_open(figure: plt.Figure):
        figure.canvas.draw()
        """
        Mantem aberto a visualizacao do mundo
        """
        input("Aperte 'ENTER' no console para fechar\n")
        plt.close()
