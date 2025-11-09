# projeto/Representacao.py
from typing import List
import re

class Agent:
    def __init__(self, nome, tipo, padrao_movimento, posicao, delta_p):
        self.nome = nome
        self.tipo = tipo
        self.padrao_movimento = padrao_movimento
        self.posicao = posicao
        self.delta_p = delta_p
    def clone(self):
        return Agent(
            nome=self.nome,
            tipo=self.tipo,
            padrao_movimento=self.padrao_movimento.copy(),
            posicao=self.posicao,
            delta_p=self.delta_p
        )
    
    def normalizar_padroes(self):
        total = sum(self.padrao_movimento)
        if total == 0: return
        self.padrao_movimento = [p / total for p in self.padrao_movimento]

    def __repr__(self):
        return f"Agent({self.nome}, tipo={self.tipo}, pos={self.posicao})"

class World:
    def __init__(self, largura, altura, delta_p_det, delta_p_rand, mobilidade_total=True, interacoes_permitidas=None):
        self.largura = largura
        self.altura = altura
        self.delta_p_det = delta_p_det
        self.delta_p_rand = delta_p_rand
        self.agentes: List[Agent] = []
        self.estados: List[List[Agent]] = []
        self.mobilidade_total = mobilidade_total
        self.interacoes_permitidas = interacoes_permitidas or []

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

    def encontrar_agentes(self, pattern: str) -> list[int]:
        regex = re.compile(pattern)
        return [i for i, agent in enumerate(self.agentes) if regex.fullmatch(agent.nome)]

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

    def adicionar_agente(self, agente: Agent):
        if not any(a.nome == agente.nome for a in self.agentes):
            self.agentes.append(agente)
    
    def remover_agente(self, nome_agente: str) -> Agent | None:
        agente_para_remover = self.encontrar_agente_obj(nome_agente)
        if agente_para_remover:
            self.agentes.remove(agente_para_remover)
            # Também remover dos estados
            for estado in self.estados:
                agente_no_estado = next((a for a in estado if a.nome == nome_agente), None)
                if agente_no_estado:
                    estado.remove(agente_no_estado)
            return agente_para_remover
        return None

    def encontrar_agente(self, nome_agente: str) -> int:
        for i, agente in enumerate(self.agentes):
            if agente.nome == nome_agente:
                return i
        return -1

    def encontrar_agente_obj(self, nome_agente: str) -> Agent | None:
        for agente in self.agentes:
            if agente.nome == nome_agente:
                return agente
        return None

    def is_occupied(self, position: tuple) -> bool:
        return any(agent.posicao == position for agent in self.agentes)

    def reset_agents(self):
        if not self.estados: return
        # Clona os agentes do primeiro estado para o estado atual
        self.agentes = [ag.clone() for ag in self.estados[0]]

    def get_neighbors(self, agente: Agent, radius: int = 1) -> List[Agent]:
        neighbors = []
        for outro in self.agentes:
            if outro == agente: continue
            # Condição de vizinhança de Moore com bordas periódicas
            dx = abs(agente.posicao[0] - outro.posicao[0])
            dy = abs(agente.posicao[1] - outro.posicao[1])
            dx = min(dx, self.largura - dx)
            dy = min(dy, self.altura - dy)
            if dx <= radius and dy <= radius:
                neighbors.append(outro)
        return neighbors

    def __repr__(self):
        return f"World({self.largura}x{self.altura}, agentes={len(self.agentes)})"