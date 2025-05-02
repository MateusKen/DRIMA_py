def aplicar_periodicidade(self, posicao):
        x, y = posicao
        return (x % self.largura, y % self.altura)  # Uso do operador módulo para simular o "loop" nas bordas
