import random
from typing import List

class Agent:
    def __init__(self, nome, tipo, padrao_movimento, posicao):
        self.nome = nome # nome do agente | ex: D01, R01
        self.tipo = tipo  # 'd' para determinístico, 'r' para randômico
        self.padrao_movimento = padrao_movimento  # Ex: {'cima': 0.25, 'baixo': 0.25, 'esquerda': 0.25, 'direita': 0.25}
        self.posicao = posicao  # Tupla (x, y)

    def clone(self):
        return Agent(
        nome=self.nome,
        tipo=self.tipo,
        padrao_movimento=self.padrao_movimento.copy(),  # faz cópia da lista
        posicao= (self.posicao[0], self.posicao[1])  # tupla, pode compartilhar
    )

    
    def normalizar_padroes(self, metodo='tradicional'):
        total = sum(self.padrao_movimento)  # Soma os valores da lista
        if total == 0:
            n = len(self.padrao_movimento)
            for i in range(n):
                self.padrao_movimento[i] = 1 / n  # Define valores uniformes
            return
        if metodo == 'tradicional':
            for i in range(len(self.padrao_movimento)):
                self.padrao_movimento[i] /= total  # Normaliza dividindo pelo total
        elif metodo == 'uniforme':
            media = total / len(self.padrao_movimento)
            for i in range(len(self.padrao_movimento)):
                self.padrao_movimento[i] = media  # Define valores uniformes
        else:
            raise ValueError("Método de normalização inválido. Use 'tradicional' ou 'uniforme'.")

    def __repr__(self):
        return f"Agente({self.nome}, tipo={self.tipo}, padrao_movimento={self.padrao_movimento}, pos={self.posicao})"


class World:
    def __init__(self, largura, altura, delta_p_det, delta_p_rand, mobilidade_total=True, interacoes_permitidas=None):
        self.largura = largura  # Número de colunas da grade
        self.altura = altura  # Número de linhas da grade
        self.delta_p_det = delta_p_det # delta_p dos determinísticos
        self.delta_p_rand = delta_p_rand # delta_p dos aleatórios
        self.agentes: List[Agent] = []  # Lista de todos os agentes presentes no mundo
        self.estados: List[List[Agent]] = [] # Lista de todos os "worlds"(estados) 
        self.mobilidade_total = mobilidade_total  # True = todos se movem, False = apenas R-agentes
        self.interacoes_permitidas = interacoes_permitidas or []  # Ex: ['dd', 'dR', 'RR']
    
    def __str__(self):
        return f"largura={self.largura}\naltura={self.altura}\ndelta_p_deterministico={self.delta_p_det}\ndelta_p_aleatorio={self.delta_p_rand}\nagentes={self.agentes}\nestados={self.estados}\n"
                        
    def adicionar_agente(self, agente) -> Agent:
        self.agentes.append(agente)
        return agente

    def remover_agente(self, nome_agente: str) -> Agent:
        removido = self.encontrar_agente(nome_agente)
        if removido == -1:
            return None

        for i in range(len(self.estados)):
            idx = self.encontrar_agente_estado(nome_agente, i)
            if idx != -1:
                self.estados[i].pop(idx)

        return self.agentes.pop(removido)

    def encontrar_agente(self, nome_agente: str) -> int: 
        for i in range(len(self.agentes)):
            if self.agentes[i].nome == nome_agente:
                self.agentes.index
                return i
        return -1

    def encontrar_agente_estado(self, nome_agente: str, iter: int) -> int:
        for i in range(len(self.estados[iter])):
            if self.estados[iter][i].nome == nome_agente:
                return i
        return -1

    def is_occupied(self, position: tuple[int, int]) -> bool:
        """
        Verifica se a posicao esta ocupada.
        """
        for agent in self.agentes:
            if agent.posicao == position:
                return True
            return False
    
    def occupied_by(self, position: tuple[int, int]) -> Agent:
        """
        Retorna quem esta ocupando, se ninguem estiver retorna None.
        """
        for agent in self.agentes:
            if agent.posicao == position:
                return agent
        return None
        
    def is_full(self):
        """
        Verifica se o mundo esta cheio.
        """
        world_size = self.largura * self.altura
        agent_number = len(self.agentes)
        if world_size <= agent_number:
            return True
        return False

    def reset_agents(self):
        if len(self.estados) <= 0:
            return
        
        agents = self.agentes
        states = self.estados

        for i in range(len(states[0])):
            agents[i] = states[0][i]

    def aplicar_periodicidade(self, posicao):
        x, y = posicao
        return (x % self.largura, y % self.altura) # Uso do operador módulo para simular o "loop" nas bordas

    def get_neighbors(self, agente: Agent, radius: int = 1) -> List[Agent]:
        """
        Retorna os vizinhos de um agente dentro de um raio (Moore neighborhood).
        """
        neighbors = []
        for outro in self.agentes:
            if outro == agente:
                continue
            dx = abs(agente.posicao[0] - outro.posicao[0])
            dy = abs(agente.posicao[1] - outro.posicao[1])
            if dx <= radius and dy <= radius:
                neighbors.append(outro)
        return neighbors

    def __repr__(self):
        return f"World({self.largura}x{self.altura}, agentes={len(self.agentes)})"
