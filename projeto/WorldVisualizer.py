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
    def simulate_2(world, interval=500, cell_size=40, margin=0):
        largura = world.largura
        altura = world.altura
        estados = world.estados

        # Calcular o tamanho da figura em polegadas: (pixels / DPI)
        dpi = 100  # 100 dpi = boa resolução padrão
        width_px = largura * cell_size
        height_px = altura * cell_size
        fig_width_in = width_px / dpi
        fig_height_in = height_px / dpi

        fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=dpi)
        fig.subplots_adjust(left=margin, right=1 - margin, top=1 - margin, bottom=margin)
        ax.set_aspect('equal')
        ax.axis('off')  # Remove eixos completamente

        def draw_grid(frame):
            ax.clear()
            ax.set_xlim(0, largura)
            ax.set_ylim(0, altura)
            ax.set_aspect('equal')
            ax.axis('off')

            # Fundo amarelo (vazios)
            for x in range(largura):
                for y in range(altura):
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black'))

            # Agentes
            for agente in estados[frame]:
                x, y = agente.posicao
                cor = 'red' if agente.tipo == 'D' else 'blue'
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=cor, edgecolor='black'))
                ax.text(x + 0.5, y + 0.5, agente.nome.upper(), color='white', weight='bold',
                        ha='center', va='center', fontsize=cell_size * 0.25)

        ani = animation.FuncAnimation(fig, draw_grid, frames=len(estados),
                                    interval=interval, repeat=False)

        plt.show()

    @staticmethod
    def simulate_interval(world, start_frame=0, end_frame=None, interval=500, cell_size=40, margin=0):
        largura = world.largura
        altura = world.altura
        estados = world.estados

        if end_frame is None or end_frame >= len(estados):
            end_frame = len(estados) - 1

        dpi = 100  # 100 dpi = boa resolução padrão
        width_px = largura * cell_size
        height_px = altura * cell_size
        fig_width_in = width_px / dpi
        fig_height_in = height_px / dpi

        fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=dpi)
        fig.subplots_adjust(left=margin, right=1 - margin, top=1 - margin, bottom=margin)
        ax.set_aspect('equal')
        ax.axis('off')

        def draw_grid(frame):
            ax.clear()
            ax.set_xlim(0, largura)
            ax.set_ylim(0, altura)
            ax.set_aspect('equal')
            ax.axis('off')

            # Fundo amarelo (vazios)
            for x in range(largura):
                for y in range(altura):
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black'))

            # Agentes (posição atual no estado)
            agentes = estados[frame]
            for agente in agentes:
                x, y = agente.posicao
                cor = 'red' if agente.tipo == 'D' else 'blue'
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=cor, edgecolor='black'))
                ax.text(x + 0.5, y + 0.5, agente.nome.upper(), color='white', weight='bold',
                        ha='center', va='center', fontsize=cell_size * 0.25)

        ani = animation.FuncAnimation(
            fig,
            draw_grid,
            frames=range(start_frame, end_frame + 1),
            interval=interval,
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