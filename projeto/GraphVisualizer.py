import math
from projeto import World
import matplotlib.animation as animation
import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

class GraphVisualizer:

    @staticmethod
    def show_images(
            world,
            agent_filter=None,
            interval=None,
            title="Movement Pattern Graph",
            directions=None
    ):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if directions is not None:
            # Filtra as direções a serem exibidas
            dir_indices = [i for i, l in enumerate(labels) if directions.get(l, 1)]
        else:
            dir_indices = list(range(9))

        if callable(agent_filter):
            agent_indices = [i for i, ag in enumerate(world.agentes) if agent_filter(i, ag)]
        elif isinstance(agent_filter, str):
            agent_indices = world.encontrar_agentes(agent_filter)
        elif agent_filter is None:
            agent_indices = list(range(len(world.agentes)))
        else:
            raise ValueError("Something went wrong with the agent filter.")

        start, end = 0, len(world.estados) - 1
        if interval:
            start, end = interval

        images = []
        for agent_idx in agent_indices:
            agente = world.agentes[agent_idx]
            y = np.zeros((end - start + 1, 9), dtype=float)
            for i in range(start, end + 1):
                y[i - start] = world.estados[i][agent_idx].padrao_movimento
            y_masked = np.where(y == 0, np.nan, y)
            x = list(range(start + 1, end + 2))

            fig, ax = plt.subplots(figsize=(10, 3))
            for dir_idx in dir_indices:
                ax.plot(
                    x, y_masked[:, dir_idx],
                    label=labels[dir_idx],
                    color=colors[dir_idx % len(colors)],
                    alpha=0.7
                )
            ax.set_title(agente.nome)
            ax.set_ylim(0, 1.05)  # Espaço extra acima de 1
            ax.set_xlim(left=start + 1)
            ax.legend(loc='upper right', fontsize=8)
            fig.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            img = Image.open(buf)
            images.append(img)
        return images

    @staticmethod
    def _criar_figura_agente(world, agent_name):
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        import numpy as np

        agent_idx = world.encontrar_agente(agent_name)
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']

        x = list(range(1, len(world.estados) + 1))
        y = np.zeros((len(world.estados), 9), dtype=float)
        for i in range(len(world.estados)):
            y[i] = world.estados[i][agent_idx].padrao_movimento
        y_masked = np.where(y == 0, np.nan, y)

        figura = Figure(figsize=(8, 3), dpi=100)
        ax = figura.add_subplot(111)
        for i in range(9):
            ax.plot(x, y_masked[:, i], label=labels[i], color=colors[i])
        ax.set_title(agent_name)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        ax.set_ylim(0, 1.005)
        ax.set_xlim(1)
        figura.tight_layout()
        return figura

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
    def show_by_idx_interval(world, agent_idx, start, end):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        x = list(range(start+1, end+2))
        y = np.zeros((end - start + 1, 9), dtype=float)

        for i in range(start, end+1):
            y[i - start] = (world.estados[i][agent_idx].padrao_movimento)

        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        for i in range(len(y[0])):
            plt.plot(x, y_masked[:, i], label=labels[i], color=colors[i])

        plt.title(world.agentes[agent_idx].nome)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylim(0, 1.005)
        plt.xlim(left=start+1)
        plt.show()

    @staticmethod
    def show_by_idx_interval_all_agents(world, start, end):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        x = list(range(start + 1, end + 2))
        plt.figure(figsize=(12, 6))

        for agent_idx, agente in enumerate(world.agentes):
            y = np.zeros((end - start + 1, 9), dtype=float)
            for i in range(start, end + 1):
                y[i - start] = world.estados[i][agent_idx].padrao_movimento
            y_masked = np.where(y == 0, np.nan, y)
            for i in range(len(y[0])):
                plt.plot(
                    x, y_masked[:, i],
                    label=f"{agente.nome} - {labels[i]}",
                    color=colors[i % len(colors)],
                    alpha=0.7
                )

        plt.title("Todos os agentes")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        plt.ylim(0, 1.005)
        plt.xlim(left=start + 1)
        plt.show()


    @staticmethod
    def show_by_name(world: World, agent_name: str):
        agent_idx = world.encontrar_agente(agent_name)
        GraphVisualizer.show_by_idx(world, agent_idx)
    
    @staticmethod
    def show_by_name_interval(world, agent_name, start, end):
        agent_idx = world.encontrar_agente(agent_name)
        GraphVisualizer.show_by_idx_interval(world, agent_idx, start, end)

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