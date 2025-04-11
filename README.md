# DRIMA_py

## Docs com planejamento do projeto
https://docs.google.com/document/d/17sgB7QWikpEKB7HPlL6xomL7Jco8mc1_2d8XpsIiHXw/edit?usp=sharing

## Projeto TCC - Implementação do DRIMA em python
O artigo apresenta DRIMA (Dynamics of Randomly Interacting Moving Agents), um modelo computacional simples de sistemas multiagentes reativos implementado em Mathematica. Ele explora como agentes interagem em uma grade bidimensional, influenciando e sendo influenciados pelos padrões de movimento uns dos outros. Os agentes são de dois tipos:

### D-agentes (determinísticos): Movem-se em uma direção fixa.
R-agentes (aleatórios): Movem-se com probabilidades definidas para cada direção.
As interações entre os agentes alteram os padrões de movimento de forma que:

### R-agentes são "atraídos" pelos D-agentes, tornando-se progressivamente mais determinísticos.
O comportamento emergente depende de fatores como a intensidade da interação, a vizinhança considerada e os modos de normalização.
A implementação em Mathematica utiliza uma abordagem funcional e foi projetada para ser minimalista, mas com potencial para explorar dinâmicas complexas. O artigo discute os principais componentes do sistema, como:

Representação de agentes e do mundo (grade, mobilidade, propriedades e tipos de interação).
Interações diretas entre agentes e seu impacto nos padrões de movimento.
Normalização de probabilidades para garantir que os movimentos dos agentes permaneçam consistentes.
O modelo foi concebido para estudar sistemas emergentes e dinâmicas de atração em um nível abstrato, com aplicações metafóricas em áreas como comportamento do consumidor, aprendizagem e sistemas físicos.

# Proposta de Projeto: Reimplementação do DRIMA em Python
Para reimplementar o DRIMA em Python, o projeto deve incluir os seguintes componentes principais e tarefas de desenvolvimento:

