# project/WorldVisualizer.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as collections
import matplotlib.animation as animation
from .Representation import History

class WorldVisualizer:
    
    @staticmethod
    def update_to_frame(frame: int, interval: int, history: History, figure: plt.Figure, agents_points: list[collections.PatchCollection]):
        """Updates the visualization to a specific frame (legacy)."""
        for i in range(len(history.agents)):
            if frame < len(history.states) and i < len(history.states[frame]):
                agent = history.states[frame][i]
                agents_points[i].set_offsets([agent.position])

        figure.canvas.draw()
        figure.canvas.flush_events()
        plt.pause(interval)
    
    @staticmethod
    def plot_world(history: History) -> tuple[plt.Figure, list[collections.PathCollection]]:
        """Plots the current state of the history (legacy)."""
        agents_points = [] 
        plt.ion()
        fig = plt.figure(figsize=(8, 8))
        
        for agent in history.agents:
            if agent.type == "D":
                point = plt.scatter(agent.position[0], agent.position[1], color="red", label="D-agent")
                agents_points.append(point)
            else:
                point = plt.scatter(agent.position[0], agent.position[1], color="blue", label="R-agent")
                agents_points.append(point)

        plt.xlim(0, history.height)
        plt.ylim(0, history.width)
        plt.grid(True)
        fig.canvas.draw()
        return (fig, agents_points)

    @staticmethod
    def simulate(history: History):
        """Animates the history (legacy)."""
        world_figure, agent_points = WorldVisualizer.plot_world(history)
        for i in range(len(history.states)):
            WorldVisualizer.update_to_frame(i, 0.2, history, world_figure, agent_points)

    @staticmethod
    def simulate_2(history: History, interval=500, cell_size=40, margin=0):
        """
        Creates a modern grid-based animation for the entire history.
        """
        width = history.width
        height = history.height
        states = history.states

        if not states:
            print("Cannot simulate: No states in history.")
            return

        dpi = 100
        width_px = width * cell_size
        height_px = height * cell_size
        fig_width_in = width_px / dpi
        fig_height_in = height_px / dpi

        fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=dpi)
        fig.subplots_adjust(left=margin, right=1 - margin, top=1 - margin, bottom=margin)
        ax.set_aspect('equal')
        ax.axis('off')

        def draw_grid(frame):
            ax.clear()
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)
            ax.set_aspect('equal')
            ax.axis('off')

            # Yellow background (empty cells)
            for x in range(width):
                for y in range(height):
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black'))

            # Agents
            if frame < len(states):
                for agent in states[frame]:
                    x, y = agent.position
                    color = 'red' if agent.type == 'D' else 'blue'
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=color, edgecolor='black'))
                    ax.text(x + 0.5, y + 0.5, agent.name.upper(), color='white', weight='bold',
                            ha='center', va='center', fontsize=cell_size * 0.25)

        ani = animation.FuncAnimation(fig, draw_grid, frames=len(states),
                                    interval=interval, repeat=False)
        plt.show()

    @staticmethod
    def simulate_interval(history: History, start_frame=0, end_frame=None, interval=500, cell_size=40, margin=0):
        """
        Creates a modern grid-based animation for a specific interval of the history.
        """
        width = history.width
        height = history.height
        states = history.states

        if not states:
            print("Cannot simulate: No states in history.")
            return

        if end_frame is None or end_frame >= len(states):
            end_frame = len(states) - 1
        if start_frame < 0:
            start_frame = 0

        dpi = 100
        width_px = width * cell_size
        height_px = height * cell_size
        fig_width_in = width_px / dpi
        fig_height_in = height_px / dpi

        fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=dpi)
        fig.subplots_adjust(left=margin, right=1 - margin, top=1 - margin, bottom=margin)
        ax.set_aspect('equal')
        ax.axis('off')

        def draw_grid(frame): # frame is the index from the range
            ax.clear()
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)
            ax.set_aspect('equal')
            ax.axis('off')

            # Yellow background
            for x in range(width):
                for y in range(height):
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black'))

            # Agents (position in the specific state)
            if frame < len(states):
                agents = states[frame]
                for agent in agents:
                    x, y = agent.position
                    color = 'red' if agent.type == 'D' else 'blue'
                    ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=color, edgecolor='black'))
                    ax.text(x + 0.5, y + 0.5, agent.name.upper(), color='white', weight='bold',
                            ha='center', va='center', fontsize=cell_size * 0.25)

        ani = animation.FuncAnimation(
            fig,
            draw_grid,
            frames=range(start_frame, end_frame + 1),
            interval=interval,
            repeat=False
        )
        plt.show()