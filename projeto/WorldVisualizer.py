import matplotlib.pyplot as plt
import matplotlib.collections as collections
from projeto import World

class WorldVisualizer:

    @staticmethod
    def update(interval: int, world: World, figure: plt.Figure, agents_points: list[collections.PatchCollection]):
        """
        Atualiza a Visualizacao
        """
        
        for i, agente in enumerate(world.agentes):
            agents_points[i].set_offsets([agente.posicao])

        figure.canvas.draw()
        figure.canvas.flush_events()
        plt.pause(interval)

    @staticmethod
    def update_to_frame(frame: int, interval: int, world: World, figure: plt.Figure, agents_points: list[collections.PatchCollection]):
        for i in range(len(world.agentes)):
            print(len(world.agentes))
            agent = world.estados[frame][i]
            print(world.estados[0][0], world.estados[1][0])
            agents_points[i].set_offsets([agent.posicao])

        figure.canvas.draw()
        figure.canvas.flush_events()
        plt.pause(interval)
    
    @staticmethod
    def plot_world(world: World) -> tuple[plt.Figure, list[collections.PathCollection]]:
        """
        Plota o estado atual do mundo com os agentes.
        """
        agents_points = [] 
        plt.ion()
        fig = plt.figure(figsize=(8, 8))
        #fig.canvas.mpl_connect('close_event')
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
    def simulate(world: World):
        """
        Cria uma animação dos agentes se movendo no mundo ao longo dos estados.
        """
        world_figure, agent_points = WorldVisualizer.plot_world(world)
        print(len(world.estados))
        print(world.estados, world.agentes)
        for i in range(len(world.estados)):
            WorldVisualizer.update_to_frame(i, 0.2, world, world_figure, agent_points)


    @staticmethod
    def keep_open(figure: plt.Figure):
        """
        Mantem aberto a visualizacao do mundo
        """
        figure.canvas.draw()
        plt.pause(0.2)

    @staticmethod
    def on_close():
        return True