import random

DIRECOES = {
    'cima': (0, -1),
    'baixo': (0, 1),
    'esquerda': (-1, 0),
    'direita': (1, 0)
}

def calcular_proximo_movimento(agente):
    if agente.tipo == 'd':
        # Determinístico: pega a direção com maior valor
        direcao = max(agente.padrao_movimento, key=agente.padrao_movimento.get)
    elif agente.tipo == 'r':
        # Randômico: sorteia com base nas probabilidades
        direcoes = list(agente.padrao_movimento.keys())
        pesos = list(agente.padrao_movimento.values())
        direcao = random.choices(direcoes, weights=pesos, k=1)[0]
    else:
        return agente.posicao  # tipo inválido

    dx, dy = DIRECOES[direcao]
    nova_pos = (agente.posicao[0] + dx, agente.posicao[1] + dy)
    return nova_pos

def atualizar_posicoes(world):
    for agente in world.agentes:
        if world.mobilidade_total or agente.tipo == 'r':  # Ex: parcial permite só 'r'
            nova_pos = calcular_proximo_movimento(agente)
            nova_pos = world.aplicar_periodicidade(nova_pos)
            agente.posicao = nova_pos
