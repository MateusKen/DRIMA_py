from projeto import World, Agent
import random as rd

class AgentSpawner:
    def __init__(self, world: World):
        self.world = world
        self.dcount = 1 # contador para os determinítiscos 
        self.rcount = 1 # contador para os aleatórios
    
    def spawn(self, type:str, moving_pattern:list, position : tuple[int,int]) -> Agent:
        """
        Tenta criar (spawn) um agente. Se a posição estiver ocupada, levanta uma exceção.        
        """
        # faz retornar ao inicio do tabuleiro caso a posicao seja maior que o mundo.
        position = (position[0] % self.world.largura,position[1] % self.world.altura)

        # se estiver ocupado, levanta uma excecao
        occupant = self.world.occupied_by(position)
        if occupant:
            raise Exception(f"Posição já ocupada pelo: {occupant.nome}")
        
        name = 'NO_NAME'
        if type == 'D':
            name = f"{type}{self.dcount:02d}"
            self.dcount+=1
        else:
            name = f"{type}{self.rcount:02d}"
            self.rcount+=1
        spawn = Agent(name, type, moving_pattern, position)
        print(f"criado = {spawn}")
        self.world.adicionar_agente(spawn)
        return spawn
    
    def try_spawn(self, type: str, moving_pattern: list, position: tuple) -> Agent | None:
        """
        Tenta criar (spawn) um agente. Se a posição inicial estiver ocupada,
        ele itera pelas posições (x+1, y), (x+2, y), etc., e avança para a próxima linha
        quando a coluna atinge o limite, até encontrar um espaço vazio ou esgotar
        todas as posições no mundo.
        Retorna o Agente criado em caso de sucesso, ou None em caso de falha.
        """
        current_x, current_y = position
        
        # Calcular o número total de posições no mundo
        # Alterado de self.world.width para self.world.largura e self.world.height para self.world.altura
        total_positions = self.world.largura * self.world.altura
        
        # Iterar por todas as posições possíveis a partir da posição inicial
        for _ in range(total_positions):
            try:
                # Tenta criar na posição atual
                print(f"Spawner: try_spawn tentando criar em ({current_x}, {current_y})...")
                agent = self.spawn(type, moving_pattern, (current_x, current_y))
                return agent
            except Exception as e:
                error_message = str(e)
                print(f"Spawner: A criação falhou em ({current_x}, {current_y}). Erro: {error_message}")

                # Se o erro for devido a uma posição ocupada ou fora dos limites, tenta a próxima posição
                # Incrementa x, e se atingir o limite da largura, reseta x e incrementa y
                current_x += 1
                # Alterado de self.world.width para self.world.largura
                if current_x >= self.world.largura:
                    current_x = 0
                    current_y += 1
                
                # Se y atingir o limite da altura, significa que todas as posições foram verificadas
                # Alterado de self.world.height para self.world.altura
                if current_y >= self.world.altura:
                    print("Spawner: Todas as posições no mundo foram verificadas. Não há espaço disponível.")
                    return None
        
        # Este ponto só será alcançado se o loop for concluído sem encontrar um espaço
        print("Spawner: Não foi possível encontrar um espaço vazio após verificar todas as posições.")
        return None

    def spawn_randomly(self, type : str =  None, moving_pattern : list = None, position : tuple = None) -> Agent:
        # caso nao definiu tipo
        if type == None:
            available_types = ('D','R')
            type = rd.choice(available_types)
        
        # caso direcao do movimento nao definida
        if moving_pattern == None and type == 'D':
            moving_pattern = [0] * 9
            moving_pattern[rd.randint(0,len(moving_pattern)-1)] = 1
        
        elif moving_pattern == None and type == 'R':
            total = 100
            temp = total
            moving_pattern = [0] * 9

            # gera as direcoes aleatorias
            for i in range(len(moving_pattern) - 1):
                moving_pattern[i] = rd.randint(0,total - 1)
                if moving_pattern[i] > total:
                    moving_pattern[i] = total
                total -= moving_pattern[i]
                moving_pattern[i] /= temp # normaliza
            moving_pattern[len(moving_pattern)-1] = total/temp
            rd.shuffle(moving_pattern)

        #caso posicao nao definida
        if position == None:
            x = rd.randint(0, self.world.largura)
            y = rd.randint(0, self.world.altura)
            position = (x,y)  

        
        return self.try_spawn(type, moving_pattern, position)
    
    def respawn(self, agent: Agent, position: tuple[int,int]) -> Agent:

        # se estiver ocupado, levanta uma excecao
        occupant = self.world.occupied_by(position)
        if occupant:
            raise Exception(f"Posição já ocupada pelo: {occupant.nome}")

        agent.posicao = position

    def try_respawn(self, agent: Agent) -> Agent | None:
        current_x = rd.randint(0,self.world.largura)
        current_y = rd.randint(0,self.world.altura)
        position = (current_x, current_y)
        # Calcular o número total de posições no mundo
        # Alterado de self.world.width para self.world.largura e self.world.height para self.world.altura
        total_positions = self.world.largura * self.world.altura
        
        # Iterar por todas as posições possíveis a partir da posição inicial
        for _ in range(total_positions):
            try:
                # Tenta criar na posição atual
                print(f"Spawner: try_spawn tentando criar em ({current_x}, {current_y})...")
                agent = self.respawn(agent,position)
                return agent
            
            except Exception as e:
                error_message = str(e)
                print(f"Spawner: A criação falhou em ({current_x}, {current_y}). Erro: {error_message}")

                # Se o erro for devido a uma posição ocupada ou fora dos limites, tenta a próxima posição
                # Incrementa x, e se atingir o limite da largura, reseta x e incrementa y
                current_x += 1
                # Alterado de self.world.width para self.world.largura
                if current_x >= self.world.largura:
                    current_x = 0
                    current_y += 1
                
                # Se y atingir o limite da altura, significa que todas as posições foram verificadas
                # Alterado de self.world.height para self.world.altura
                if current_y >= self.world.altura:
                    print("Spawner: Todas as posições no mundo foram verificadas. Não há espaço disponível.")
                    return None
        
        # Este ponto só será alcançado se o loop for concluído sem encontrar um espaço
        print("Spawner: Não foi possível encontrar um espaço vazio após verificar todas as posições.")
        return None
