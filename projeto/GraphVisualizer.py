from projeto import World
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class GraphVisualizer:
    @staticmethod
    def update(frame, x, y_masked, lines):
        """
        Funcao auxiliar para animacao
        """
        for i, line in enumerate(lines):
            line.set_data(x[:frame], y_masked[:frame, i])
        return lines

    @staticmethod
    def show_by_idx(world: World, agent_idx: int):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        x = list(range(1,len(world.estados)+1))
        y = np.zeros((len(world.estados),9),dtype=float)

        for i in range(len(world.estados)):
            y[i] = (world.estados[i][agent_idx].padrao_movimento)

        # Substitui os 0s por np.nan para que não sejam plotados
        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        for i in range(len(y[0])):
            plt.plot(x, y_masked[:,i], label=labels[i], color=colors[i])

        plt.title(world.agentes[agent_idx].nome)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlim(1)
        plt.ylim(0,1.005)
        plt.show()
    
    @staticmethod
    def show_by_name(world: World, agent_name: str):
        agent_idx = world.encontrar_agente(agent_name)
        GraphVisualizer.show_by_idx(world, agent_idx)
    
    @staticmethod
    def show_animated_by_idx(world: World, agent_idx: int):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        x = np.arange(1, len(world.estados) + 1)
        y = np.zeros((len(world.estados), 9), dtype=float)

        for i in range(len(world.estados)):
            y[i] = world.estados[i][agent_idx].padrao_movimento

        y_masked = np.where(y == 0, np.nan, y)

        fig, ax = plt.subplots(figsize=(12, 6))
        lines = []
        for i in range(9):
            line, = ax.plot([], [], label=labels[i], color=colors[i])
            lines.append(line)

        ax.set_xlim(1, len(world.estados))
        ax.set_ylim(0, 1.005)
        ax.set_title(world.agentes[agent_idx].nome)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        ani = animation.FuncAnimation(
            fig, GraphVisualizer.update,
            frames=len(x) + 1,
            fargs=(x, y_masked, lines),
            interval=25,
            blit=False,
            repeat=False
        )

        plt.show()
        return ani

    @staticmethod
    def show_animated_by_name(world: World, agent_name: str):
        agent_idx = world.encontrar_agente(agent_name)
        GraphVisualizer.show_animated_by_idx(world, agent_idx)