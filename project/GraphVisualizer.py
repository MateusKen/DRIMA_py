# project/GraphVisualizer.py
import math
from .Representation import History
import matplotlib.animation as animation
import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

class GraphVisualizer:

    @staticmethod
    def show_images(
            history: History,
            agent_filter=None,
            interval=None,
            title="Movement Pattern Graph",
            directions=None
    ):
        """
        Generates a list of PIL Images for agent movement patterns.
        """
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if directions is not None:
            dir_indices = [i for i, l in enumerate(labels) if directions.get(l, 1)]
        else:
            dir_indices = list(range(9))

        if callable(agent_filter):
            agent_indices = [i for i, ag in enumerate(history.agents) if agent_filter(i, ag)]
        elif isinstance(agent_filter, str):
            agent_indices = history.find_agent_indices_by_pattern(agent_filter)
        elif agent_filter is None:
            agent_indices = list(range(len(history.agents)))
        else:
            raise ValueError("Something went wrong with the agent filter.")

        start, end = 0, len(history.states) - 1
        if interval:
            start, end = interval
        
        # Ensure interval is valid
        if end >= len(history.states):
            end = len(history.states) - 1
        if start < 0:
            start = 0

        images = []
        for agent_idx in agent_indices:
            if agent_idx >= len(history.agents):
                print(f"Warning: Agent index {agent_idx} out of bounds. Skipping.")
                continue
                
            agent = history.agents[agent_idx]
            y = np.zeros((end - start + 1, 9), dtype=float)
            
            for i in range(start, end + 1):
                if i < len(history.states) and agent_idx < len(history.states[i]):
                    y[i - start] = history.states[i][agent_idx].movement_pattern
                else:
                    y[i - start] = np.nan # Mark as missing data
                    
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
            ax.set_title(agent.name)
            ax.set_ylim(0, 1.05)
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
    def _create_agent_figure(history: History, agent_name: str):
        """Creates a Matplotlib Figure for a single agent."""
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        import numpy as np

        agent_idx = history.find_agent_index(agent_name)
        if agent_idx == -1:
             raise ValueError(f"Agent '{agent_name}' not found.")
             
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#000080', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']

        x = list(range(1, len(history.states) + 1))
        y = np.zeros((len(history.states), 9), dtype=float)
        for i in range(len(history.states)):
            if i < len(history.states) and agent_idx < len(history.states[i]):
                 y[i] = history.states[i][agent_idx].movement_pattern
            else:
                 y[i] = np.nan
                 
        y_masked = np.where(y == 0, np.nan, y)

        figure = Figure(figsize=(8, 3), dpi=100)
        ax = figure.add_subplot(111)
        for i in range(9):
            ax.plot(x, y_masked[:, i], label=labels[i], color=colors[i])
        ax.set_title(agent_name)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        ax.set_ylim(0, 1.005)
        ax.set_xlim(1)
        figure.tight_layout()
        return figure

    @staticmethod
    def update(frame, x, y_masked, lines):
        """Helper function for animation."""
        for i, line in enumerate(lines):
            line.set_data(x[:frame], y_masked[:frame, i])
        return lines

    @staticmethod
    def show_by_idx(history: History, agent_idx: int):
        """Plots the graph for one agent by its index."""
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if agent_idx >= len(history.agents):
            raise IndexError("Agent index out of range.")

        x = list(range(1, len(history.states) + 1))
        y = np.zeros((len(history.states), 9), dtype=float)

        for i in range(len(history.states)):
            if i < len(history.states) and agent_idx < len(history.states[i]):
                y[i] = (history.states[i][agent_idx].movement_pattern)
            else:
                y[i] = np.nan

        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        for i in range(len(y[0])):
            plt.plot(x, y_masked[:, i], label=labels[i], color=colors[i])

        plt.title(history.agents[agent_idx].name)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlim(1)
        plt.ylim(0, 1.005)
        plt.show()
    
    @staticmethod
    def show_by_idx_interval(history: History, agent_idx: int, start: int, end: int):
        """Plots the graph for one agent over a specific interval."""
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if agent_idx >= len(history.agents):
            raise IndexError("Agent index out of range.")
        if end >= len(history.states):
            end = len(history.states) - 1
            
        x = list(range(start + 1, end + 2))
        y = np.zeros((end - start + 1, 9), dtype=float)

        for i in range(start, end + 1):
            if i < len(history.states) and agent_idx < len(history.states[i]):
                y[i - start] = (history.states[i][agent_idx].movement_pattern)
            else:
                y[i-start] = np.nan

        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        for i in range(len(y[0])):
            plt.plot(x, y_masked[:, i], label=labels[i], color=colors[i])

        plt.title(history.agents[agent_idx].name)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylim(0, 1.005)
        plt.xlim(left=start + 1)
        plt.show()

    @staticmethod
    def show_by_idx_interval_all_agents(history: History, start: int, end: int):
        """Plots all agents on a single graph over an interval."""
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if end >= len(history.states):
            end = len(history.states) - 1

        x = list(range(start + 1, end + 2))
        plt.figure(figsize=(12, 6))

        for agent_idx, agent in enumerate(history.agents):
            y = np.zeros((end - start + 1, 9), dtype=float)
            for i in range(start, end + 1):
                if i < len(history.states) and agent_idx < len(history.states[i]):
                    y[i - start] = history.states[i][agent_idx].movement_pattern
                else:
                    y[i-start] = np.nan
                    
            y_masked = np.where(y == 0, np.nan, y)
            for i in range(len(y[0])):
                plt.plot(
                    x, y_masked[:, i],
                    label=f"{agent.name} - {labels[i]}",
                    color=colors[i % len(colors)],
                    alpha=0.7
                )

        plt.title("All Agents")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        plt.ylim(0, 1.005)
        plt.xlim(left=start + 1)
        plt.show()


    @staticmethod
    def show_by_name(history: History, agent_name: str):
        """Plots the graph for one agent by its name."""
        agent_idx = history.find_agent_index(agent_name)
        if agent_idx == -1:
             raise ValueError(f"Agent '{agent_name}' not found.")
        GraphVisualizer.show_by_idx(history, agent_idx)
    
    @staticmethod
    def show_by_name_interval(history: History, agent_name: str, start: int, end: int):
        """Plots the graph for one agent by name over an interval."""
        agent_idx = history.find_agent_index(agent_name)
        if agent_idx == -1:
             raise ValueError(f"Agent '{agent_name}' not found.")
        GraphVisualizer.show_by_idx_interval(history, agent_idx, start, end)

    @staticmethod
    def show_animated_by_idx(history: History, agent_idx: int):
        """Shows an animated plot for one agent."""
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        if agent_idx >= len(history.agents):
            raise IndexError("Agent index out of range.")

        x = np.arange(1, len(history.states) + 1)
        y = np.zeros((len(history.states), 9), dtype=float)

        for i in range(len(history.states)):
            if i < len(history.states) and agent_idx < len(history.states[i]):
                y[i] = history.states[i][agent_idx].movement_pattern
            else:
                y[i] = np.nan

        y_masked = np.where(y == 0, np.nan, y)

        fig, ax = plt.subplots(figsize=(12, 6))
        lines = []
        for i in range(9):
            line, = ax.plot([], [], label=labels[i], color=colors[i])
            lines.append(line)

        ax.set_xlim(1, len(history.states))
        ax.set_ylim(0, 1.005)
        ax.set_title(history.agents[agent_idx].name)
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
    def show_animated_by_name(history: History, agent_name: str):
        """Shows an animated plot for one agent by name."""
        agent_idx = history.find_agent_index(agent_name)
        if agent_idx == -1:
             raise ValueError(f"Agent '{agent_name}' not found.")
        GraphVisualizer.show_animated_by_idx(history, agent_idx)