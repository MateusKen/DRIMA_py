from projeto import World, Agent, WorldUpdater, WorldVisualizer

def main():
    # Configuração do mundo (H1)
    world = World(altura = 10, largura = 10)
    delta_p = 0.1  # Incremento de probabilidade

    # Adiciona agentes (H1)
    world.adicionar_agente(Agent("D01", "D", [1, 0, 0, 0, 0, 0, 0, 0, 0], (2, 2)))
    world.adicionar_agente(Agent("R01", "R", [0.125] * 9, (4, 6)))

    # Atualização do mundo (H5)
    updater = WorldUpdater()
    for _ in range(100):  # 100 iterações de atualização síncrona
        # Visualização (H6)
        WorldVisualizer.plot_world(world)
        updater.update_synchronously(world, delta_p)

    
print()
if __name__ == "__main__":
    main()