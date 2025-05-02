class Agent:
    def __init__(self, nome, tipo, padrao_movimento, posicao):
        self.nome = nome
        self.tipo = tipo  # 'd' (determinístico) ou 'r' (randômico)
        self.padrao_movimento = padrao_movimento  # exemplo: 'direita', 'esquerda', etc.
        self.posicao = posicao  # (x, y)
