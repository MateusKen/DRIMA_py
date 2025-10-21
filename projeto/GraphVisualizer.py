# projeto/GraphVisualizer.py
from .Representacao import World
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class GraphVisualizer:
    
    @staticmethod
    def show_filtered_graph(world: World, agent_name: str, start_frame: int, end_frame: int, directions_to_show: dict):
  
        agent_idx = world.encontrar_agente(agent_name)
        if agent_idx == -1:
            raise ValueError(f"Agent '{agent_name}' not found.")

        if start_frame < 0: start_frame = 0
        if end_frame >= len(world.estados): end_frame = len(world.estados) - 1
        if start_frame > end_frame:
             raise ValueError("Start frame cannot be after end frame.")


        labels = ['L', 'NE', 'N', 'NO', 'O', 'SO', 'S', 'SE', 'X']
        colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00', '#ADD8E6']

        
        x = list(range(start_frame, end_frame + 1))
        y = np.zeros((len(x), 9), dtype=float)

        for i, frame_idx in enumerate(x):
            try:
                
                agente_no_estado = next(ag for ag in world.estados[frame_idx] if ag.nome == agent_name)
                y[i] = agente_no_estado.padrao_movimento
            except StopIteration:
              
                y[i] = np.nan 
        
        y_masked = np.where(y == 0, np.nan, y)

        plt.figure(figsize=(12, 6))
        
        for i, label in enumerate(labels):
           
            if directions_to_show.get(label, False):
                plt.plot(x, y_masked[:, i], label=label, color=colors[i])

        plt.title(f"Movement Pattern for {agent_name} (Frames {start_frame}-{end_frame})")
        plt.xlabel("History (Frame)")
        plt.ylabel("Probability")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylim(0, 1.005)
        plt.xlim(left=start_frame, right=end_frame)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout(rect=[0, 0, 0.85, 1]) 
        plt.show()

    @staticmethod
    def show_by_name(world: World, agent_name: str):
       
        directions = {
            'L': True, 'NE': True, 'N': True, 'NO': True, 'O': True, 
            'SO': True, 'S': True, 'SE': True, 'X': True
        }
        GraphVisualizer.show_filtered_graph(world, agent_name, 0, len(world.estados) - 1, directions)
