# Retorna os vizinhos de um agente no raio especificado (viz. de Moore).
def obter_vizinhos(world, agente, raio=1):
    vizinhos = []
    ax, ay = agente.posicao
    for outro in world.agentes:
        if outro == agente:
            continue
        bx, by = outro.posicao
        dx = abs(bx - ax)
        dy = abs(by - ay)
        if dx <= raio and dy <= raio:
            vizinhos.append(outro)
    return vizinhos

# Atualiza o padrão de movimento de agente1 com base em agente2.
def interagir(agente1, agente2, delta_p, modo='fixo'):
    for direcao in agente1.padrao_movimento:
        if modo == 'fixo':
            incremento = delta_p
        elif modo == 'variável':
            diff = agente2.padrao_movimento[direcao] - agente1.padrao_movimento[direcao]
            incremento = delta_p * diff
        else:
            incremento = 0

        agente1.padrao_movimento[direcao] += incremento

    normalizar_padroes(agente1)

# Aplica interações entre os agentes do mundo.
def aplicar_interacoes(world, delta_p=0.1, modo='fixo', bidirecional=True, raio=1):
    for agente in world.agentes:
        vizinhos = obter_vizinhos(world, agente, raio)
        for vizinho in vizinhos:
            tipo_interacao = agente.tipo + vizinho.tipo
            if tipo_interacao in world.interacoes_permitidas:
                interagir(agente, vizinho, delta_p, modo)
                if bidirecional:
                    interagir(vizinho, agente, delta_p, modo)
