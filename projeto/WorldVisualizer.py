import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as collections
import matplotlib.animation as animation
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
            agent = world.estados[frame][i]
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
        #print(len(world.estados))
        #print(world.estados, world.agentes)
        for i in range(len(world.estados)):
            WorldVisualizer.update_to_frame(i, 0.2, world, world_figure, agent_points)


    @staticmethod
    def simulate_2(world: World):
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.set_xlim(0, world.largura)
        ax.set_ylim(0, world.altura)
        ax.set_xticks(range(world.largura))
        ax.set_yticks(range(world.altura))
        ax.set_xticklabels([str(i+1) for i in range(world.largura)])
        ax.set_yticklabels([str(i+1) for i in range(world.altura)])
        ax.grid(True)
        plt.gca().invert_yaxis()

        # Pintar fundo amarelo
        for x in range(world.largura):
            for y in range(world.altura):
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, edgecolor='black', facecolor='yellow')
                ax.add_patch(rect)

        # Cria patches e textos para os agentes
        agent_patches = []
        agent_labels = []
        for agente in world.estados[0]:  # estado inicial
            cor = 'red' if agente.tipo == 'D' else 'blue'
            rect = patches.Rectangle(agente.posicao, 1, 1, linewidth=1, edgecolor='black', facecolor=cor)
            label = ax.text(
                agente.posicao[0] + 0.5,
                agente.posicao[1] + 0.5,
                agente.nome,
                ha='center', va='center',
                color='white', fontsize=8, weight='bold'
            )
            agent_patches.append(rect)
            agent_labels.append(label)
            ax.add_patch(rect)

        def update(frame):
            estado = world.estados[frame]
            for i, agente in enumerate(estado):
                x, y = agente.posicao
                agent_patches[i].set_xy((x, y))
                agent_labels[i].set_position((x + 0.5, y + 0.5))
                agent_labels[i].set_text(agente.nome)
            return agent_patches + agent_labels

        ani = animation.FuncAnimation(
            fig, update,
            frames=len(world.estados),
            interval=300,
            blit=True,
            repeat=False
        )

        plt.show()

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