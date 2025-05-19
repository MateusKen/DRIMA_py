from projeto import World
import matplotlib.pyplot as plt
import numpy as np

class GraphVisualizer:
    @staticmethod
    def show(world: World, agent_idx: int):
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']

        x = list(range(1,len(world.estados)+1))
        y = np.zeros((len(world.estados),9),dtype=float)

        for i in range(len(world.estados)):
            y[i] = (world.estados[i][agent_idx].padrao_movimento)

        # Substitui os 0s por np.nan para que não sejam plotados
        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        print(len(y))
        print(y)
        for i in range(len(y[0])):
            plt.plot(x, y_masked[:,i], label=labels[i], color=colors[i])
        print(y)

        plt.title(world.agentes[agent_idx].nome)
        plt.legend()
        plt.ylim(0,1.005)
        plt.show()