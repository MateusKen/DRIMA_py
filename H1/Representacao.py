import random

class Agent:
    def __init__(self, nome, tipo, padrao_movimento, posicao):
        self.nome = nome
        self.tipo = tipo  # 'd' para determinístico, 'r' para randômico
        self.padrao_movimento = padrao_movimento  # Ex: {'cima': 0.25, 'baixo': 0.25, 'esquerda': 0.25, 'direita': 0.25}
        self.posicao = posicao  # Tupla (x, y)

    def __repr__(self):
        return f"Agente({self.nome}, tipo={self.tipo}, pos={self.posicao})"


class World:
    def __init__(self, largura, altura, mobilidade_total=True, interacoes_permitidas=None):
        self.largura = largura  # Número de colunas da grade
        self.altura = altura  # Número de linhas da grade
        self.agentes = []  # Lista de todos os agentes presentes no mundo
        self.mobilidade_total = mobilidade_total  # True = todos se movem, False = apenas R-agentes
        self.interacoes_permitidas = interacoes_permitidas or []  # Ex: ['dd', 'dR', 'RR']
    
    def adicionar_agente(self, agente):
        self.agentes.append(agente)

    def aplicar_periodicidade(self, posicao):
        x, y = posicao
        return (x % self.largura, y % self.altura) # Uso do operador módulo para simular o "loop" nas bordas

    def __repr__(self):
        return f"World({self.largura}x{self.altura}, agentes={len(self.agentes)})"
