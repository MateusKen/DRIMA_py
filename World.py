class World:
    def __init__(self, largura, altura, mobilidade_total=True, interacoes_permitidas=None):
        self.largura = largura  # Número de colunas da grade
        self.altura = altura  # Número de linhas da grade
        self.agentes = []  # Lista de todos os agentes
        self.mobilidade_total = mobilidade_total  # Se True, todos os agentes podem se mover
        self.interacoes_permitidas = interacoes_permitidas or []  # Tipos de interação permitidas (ex: ['dd', 'dR'])
