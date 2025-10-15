from InterfaceTeste.InterfaceTeste import TelaAjustavel
from projeto import World, Agent, WorldUpdater, WorldVisualizer, FileHandler, InterfaceHandler, GraphVisualizer, AgentSpawner

def main():
    # Configuração do mundo (H1)
    world = FileHandler.load_world()
    # Adiciona agentes (H1)

    agent_spawner = AgentSpawner(world)
    
    # conf_3
    """
    agent_spawner.spawn_randomly(type="D",moving_pattern=[1,0,0,0,0,0,0,0,0])
    agent_spawner.spawn_randomly(type="D",moving_pattern=[0,0,0,0,0,0,0,1,0])
    agent_spawner.spawn_randomly(type="R",moving_pattern=[0.5,0,0,0,0,0,0,0.5,0])
    agent_spawner.spawn_randomly(type="R",moving_pattern=[0.5,0,0,0,0,0,0,0.5,0])
    agent_spawner.spawn_randomly(type="R",moving_pattern=[0.5,0,0,0,0,0,0,0.5,0])
    agent_spawner.spawn_randomly(type="R",moving_pattern=[0.5,0,0,0,0,0,0,0.5,0])
    agent_spawner.spawn_randomly(type="R",moving_pattern=[0.5,0,0,0,0,0,0,0.5,0]) """



    #world.adicionar_agente(Agent("D01", "D", [1, 0, 0, 0, 0, 0, 0, 0, 0], (2, 2)))
    #world.adicionar_agente(Agent("R01", "R", [0.125] * 9, (4, 6)))
    # Atualização do mundo (H5)
    #updater = WorldUpdater()
    # Visualização (H6)
    #world_figure, agents_points = WorldVisualizer.plot_world(world)
    #for _ in range(world.numero_de_iteracoes):  # 100 iterações de atualização síncrona
        #WorldVisualizer.update(0.5, world, world_figure, agents_points)

        #updater.update_synchronously(world)
    #WorldVisualizer.keep_open(world_figure)
    
    world = FileHandler.load_world_2(world.agentes.copy())
    interface = InterfaceHandler(world, agent_spawner)
    interface.create_menu(640,600)

    interface = TelaAjustavel()
    interface.mainloop()

if __name__ == "__main__":
    main()