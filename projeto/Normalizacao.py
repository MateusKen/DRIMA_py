#  Garante que as probabilidades do padrão de movimento somem 1.
def normalizar_padroes(agente, metodo='tradicional'):
  
    padrao = agente.padrao_movimento
    total = sum(padrao.values())

    if total == 0:
        n = len(padrao)
        for direcao in padrao:
            padrao[direcao] = 1 / n
        return

    if metodo == 'tradicional':
        for direcao in padrao:
            padrao[direcao] /= total
    elif metodo == 'uniforme':
        media = total / len(padrao)
        for direcao in padrao:
            padrao[direcao] = media
