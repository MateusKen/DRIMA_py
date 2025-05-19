from projeto import World, Agent, WorldUpdater, WorldVisualizer, FileHandler, InterfaceHandler, GraphVisualizer

def main():
    # Configuração do mundo (H1)
    world = World(altura = 10, largura = 10)
    delta_p = 0.1  # Incremento de probabilidade

    # Adiciona agentes (H1)
    world.adicionar_agente(Agent("D01", "D", [1, 0, 0, 0, 0, 0, 0, 0, 0], (2, 2)))
    world.adicionar_agente(Agent("R01", "R", [0.125] * 9, (4, 6)))

    # Atualização do mundo (H5)
    # Visualização (H6)

    updater = WorldUpdater()
    #world_figure, agents_points = WorldVisualizer.plot_world(world)
    for _ in range(100):  # 100 iterações de atualização síncrona
        #WorldVisualizer.update(0.5, world, world_figure, agents_points)

        updater.update_synchronously(world, delta_p)
    #WorldVisualizer.keep_open(world_figure)
    
    GraphVisualizer.show(world,1)

if __name__ == "__main__":
    main()