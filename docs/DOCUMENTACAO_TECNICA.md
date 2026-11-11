# Documentação Técnica: Simulador DRIMA

**Dynamics of Randomly Interacting Moving Agents**

Igor Benites Moura, Gabriel Gonzaga Chung e Mateus Kenzo Iochimoto
Faculdade de Computação e Informática (FCI), Universidade Presbiteriana Mackenzie, São Paulo, SP – Brasil

> Esta é a versão atualizada da documentação técnica. A versão original em PDF, de 17 de novembro de 2025, continua em [`DOCUMENTACAO_TECNICA_DRIMA.pdf`](../DOCUMENTACAO_TECNICA_DRIMA.pdf).
>
> **O que mudou em relação ao PDF:**
> - integração opcional com o gerador de números aleatórios por hardware **TrueRNG**;
> - interface reformulada: o painel lateral deu lugar à tela única **Edit Configuration**, que trabalha sobre um rascunho, com pré-visualização, desfazer e criação de vários agentes de uma vez;
> - a história só é calculada quando a configuração é confirmada, e o tempo de construção é registrado;
> - controles ▶ / ⏸ / ⏮ da história, exportação e limpeza de logs, e geração de executável com PyInstaller;
> - Δp local por agente e seletor Global/Local; modo assíncrono com sub-iterações configuráveis;
> - gráficos de vários agentes com exportação de imagem;
> - formato de arquivo `.json.gz` (o PDF citava `.zip`) e pasta `projeto/` (o PDF citava `project/`);
> - novos módulos `WorldVisualizer.py`, `Normalizacao.py` e `TrueRNGSource.py`.
>
> As figuras ainda são da interface anterior.

## Sumário

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Guia de instalação e execução](#2-guia-de-instalação-e-execução)
3. [Manual do usuário (interface gráfica)](#3-manual-do-usuário-interface-gráfica)
4. [Modelo de simulação](#4-modelo-de-simulação)
5. [Fonte de aleatoriedade: TrueRNG](#5-fonte-de-aleatoriedade-truerng)
6. [Arquitetura do software](#6-arquitetura-do-software)
7. [Formato dos arquivos](#7-formato-dos-arquivos)

---

## 1. Visão geral do projeto

O Simulador DRIMA é uma aplicação para modelar, executar e analisar simulações de sistemas multiagente. O foco é estudar a **evolução do comportamento** e a **propagação de influência** em uma população de agentes com regras dinâmicas.

### 1.1 Componentes principais

- **Agentes Determinísticos (D):** agentes "teimosos" ou "influenciadores", com padrão de movimento fixo que nunca muda. Sempre se movem na direção de maior probabilidade.
- **Agentes Randômicos (R):** agentes "influenciáveis" ou "indecisos". O padrão de movimento é uma distribuição de probabilidade alterada pela influência dos vizinhos, e a direção de cada passo é sorteada segundo essa distribuição.

### 1.2 Tecnologias utilizadas

| Item | Tecnologia |
| --- | --- |
| Linguagem | Python 3.10+ |
| Interface gráfica | CustomTkinter |
| Visualização de dados | Matplotlib (e Pillow para exibir/exportar os gráficos) |
| Aleatoriedade por hardware | TrueRNG via porta serial (`pyserial`), opcional |
| Formato de dados | JSON |
| Compressão | gzip (`.json.gz`) |
| Empacotamento | PyInstaller (`main.spec`), opcional |

---

## 2. Guia de instalação e execução

### 2.1 Pré-requisitos

- Python 3.10 ou mais recente
- `pip`
- Opcional: um dispositivo TrueRNG com o driver instalado

### 2.2 Instalação

```bash
git clone https://github.com/MateusKen/DRIMA_py.git
cd DRIMA_py
pip install -r requirements.txt
```

### 2.3 Estrutura de arquivos

Os `import`s dependem desta estrutura; execute sempre a partir da raiz.

```
DRIMA_py/
├── main.py              # ponto de entrada (interface gráfica)
├── main.spec            # configuração do PyInstaller
├── drima.json           # configuração padrão
├── requirements.txt
├── configuracoes/       # mundos salvos e exemplos
├── assets/, imagens/    # imagens da documentação
├── docs/                # esta documentação
└── projeto/
    ├── __init__.py
    ├── Representacao.py
    ├── AgentSpawner.py
    ├── Interacoes.py
    ├── Movimento.py
    ├── Normalizacao.py
    ├── WorldUpdater.py
    ├── WorldVisualizer.py
    ├── GraphVisualizer.py
    ├── FileHandler.py
    ├── TrueRNGSource.py
    └── InterfaceTeste.py
```

### 2.4 Execução

```bash
python main.py
```

A janela *DRIMA Simulation Interface* abre com 5 agentes aleatórios e, logo em seguida, a tela **Edit Configuration**. A história só é calculada depois que a configuração é confirmada (seção 3.3).

### 2.5 Gerar um executável (opcional)

```bash
pip install pyinstaller
pyinstaller main.spec
```

O `main.spec` declara como *hidden imports* os módulos do `pyserial` usados pelo TrueRNG. O executável é gerado em `dist/`.

---

## 3. Manual do usuário (interface gráfica)

### 3.1 Tela principal

A interface ocupa uma única tela:

- **Topo, à esquerda — Show Agent Graph:** abre a janela *Advanced Graph Filter* (seção 3.6).
- **Topo, à direita — Logs:** console com o status do sistema, a construção do mundo (com o tempo gasto), o estado do TrueRNG e mensagens de erro (em vermelho).
  - **Download Logs:** salva todas as linhas exibidas em um `.txt`.
  - **Clear Logs:** limpa a área de logs e o que seria exportado.
- **Centro — grade da simulação:** estado da iteração atual. Agentes D em vermelho, agentes R em azul, células vazias em amarelo.
- **Canto superior direito da grade — 🌍:** abre ou recolhe o painel de configuração (seção 3.2).
- **Base — controles da história:**
  - **▶ / ⏸:** inicia ou pausa a reprodução a partir do ponto atual.
  - **⏮:** volta ao frame 0; só fica ativo depois de avançar.
  - **Slider e campo `t / N`:** vão direto para uma iteração.

Enquanto a história não foi construída, ▶, ⏮ e o slider ficam desabilitados.

### 3.2 Painel de configuração (🌍)

- **Edit Configuration:** abre a tela de edição (seção 3.3).
- **Load World:** carrega um mundo salvo (`.json.gz` ou `.json`) com a configuração e a história. Se o arquivo pedir o TrueRNG, tenta reconectá-lo; se falhar, avisa no log.
- **Export World:** salva a configuração e a história completa em `.json.gz`.

### 3.3 Tela *Edit Configuration*

Reúne a configuração do mundo e a dos agentes iniciais. Tudo é feito sobre um **rascunho** isolado (um `World` e um `AgentSpawner` próprios); o mundo atual só muda na confirmação final.

**Coluna da esquerda — Initial Agent Configuration**

- **Pré-visualização** da grade com os agentes do rascunho.
- **Add Agent:** abre a janela *Add New Agent* (seção 3.4).
- **Add Multiple Agents:** informa quantos agentes R e quantos D criar; posições e padrões são sorteados.
- **Remove Selected:** remove o agente escolhido na lista.
- **Remove All Agents:** esvazia o rascunho.
- **Undo Last Change:** desfaz a última adição ou remoção (pilha de *snapshots*).

**Coluna da direita — World Settings**

- **Delta-P Mode (Global / Local):** de onde vem a força de influência (seção 4.2). No modo *Local*, os sliders globais ficam ocultos.
- **Sliders `delta_p_D` e `delta_p_R`:** Δp global para influenciadores determinísticos e randômicos.
- **Grid Width, Grid Height, No. of Iterations.**
- **Interaction Mode (Synchronous / Asynchronous):** regra de atualização (seção 4.3). No modo assíncrono aparece um campo com o número de agentes sorteados por passo.
- **Use TrueRNG Hardware:** liga ou desliga o TrueRNG (seção 5). Diferente do resto da tela, é aplicado **na hora** e salvo no `drima.json`, porque conecta ou desconecta o dispositivo; um aviso mostra o resultado. Se a conexão falhar, o switch volta para desligado.

**Confirmação**

- **Done:** valida os campos. Se algo estiver inválido, mostra o erro e mantém a tela aberta. Se estiver tudo certo, pergunta:
  - **Yes, Apply:** grava a configuração no `drima.json`, substitui os agentes iniciais pelos do rascunho e constrói a história. Ao final, o log e um aviso mostram o tempo de construção (medido com `time.perf_counter`).
  - **No, Discard:** descarta o rascunho.
- **Cancel:** fecha sem alterar nada.

### 3.4 Janela *Add New Agent*

![Janela Add New Agent](../assets/add_new_agent.png)

- **Agent Type:** *Random (R)* ou *Deterministic (D)*.
- **Position (X, Y):** opcional. Se ficar vazio, a posição é sorteada; se estiver ocupada, o agente vai para a célula livre mais próxima.
- **Influence (Δp):** opcional. É o Δp **local** do agente, usado no modo *Local* quando ele é o influenciador. Se ficar vazio, é sorteado: entre 0,1 e 0,9 para agentes D e entre 0,01 e 0,1 para agentes R.
- **Agente R:**
  - **Uniform probabilities (all directions equal):** marcado por padrão; todas as direções recebem a mesma probabilidade.
  - Desmarcado, aparece a rosa dos ventos com as 9 direções (NW, N, NE, W, X, E, SW, S, SE; `X` = ficar parado).
  - **Allow movement in X (stay in place):** marcado, preenche as 9 direções com 1/9; desmarcado, bloqueia `X` em 0 e distribui 1/8 entre as outras 8.
  - Se a soma não for 1, a janela *Confirm Normalization* oferece `Yes, Normalize` (divide cada valor pela soma) ou `No, Fix Manually`.
- **Agente D:** escolhe-se **uma única direção** em uma grade de botões.

Com o TrueRNG ligado, os valores sorteados (posição, Δp) vêm do dispositivo.

### 3.5 Janela *Add Multiple Agents*

Campos *Random (R)* e *Deterministic (D)* com a quantidade de cada tipo (inteiros não negativos, pelo menos um maior que zero). Posição, padrão de movimento e Δp de cada agente são sorteados.

### 3.6 Janela *Advanced Graph Filter*

![Janela Advanced Graph Filter](../assets/filtro_grafico.png)

- **Select agents:** lista suspensa com seleção múltipla. É gerado um gráfico por agente.
- **History Range (Start / End):** limita o intervalo de iterações exibido.
- **Directions to Display:** liga ou desliga cada uma das 9 direções.
- **Generate Graph:** abre a janela com os gráficos; nela, **Export Image** salva os gráficos como imagem.

![Exemplo de gráfico](../assets/grafico_r_nconverge.png)

*Exemplo de saída: cenário de não convergência, em que o agente R oscila entre direções sem se fixar em nenhuma.*

---

## 4. Modelo de simulação

### 4.1 Grade, vizinhança e movimento

- A grade é **toroidal**: quem sai por uma borda entra pela oposta.
- A vizinhança é de **Moore com raio 1**: as 8 células ao redor, também com bordas periódicas.
- O padrão de movimento é uma lista de 9 probabilidades, na ordem L, NE, N, NO, O, SO, S, SE, X.
- **Agente D:** move-se sempre na direção de maior probabilidade.
- **Agente R:** sorteia a direção com pesos iguais às probabilidades.

### 4.2 Interação e Δp

Só agentes R são influenciados. Quando um agente R interage com um vizinho:

1. para cada direção em que o vizinho tem probabilidade **maior** que a do agente R, o agente R soma Δp nessa direção;
2. o padrão do agente R é normalizado para voltar a somar 1.

| Modo | Δp usado |
| --- | --- |
| **Global** | `delta_p_D` se o vizinho (influenciador) é D; `delta_p_R` se é R |
| **Local** | o Δp do próprio vizinho influenciador (`agent.delta_p`) |

### 4.3 Modos de atualização

- **Síncrono:** em cada passo, todos os agentes interagem com todos os vizinhos e, em seguida, todos se movem.
- **Assíncrono:** em cada passo, são sorteados até `async_sub_iterations` agentes distintos. Cada um interage com **um** vizinho escolhido ao acaso e se move logo em seguida, antes do próximo agente sorteado.

Cada passo gera um "mundo" que é guardado na história, e é essa história que a interface reproduz.

### 4.4 Normalização

O método usado pela simulação é o tradicional (`Agent.normalizar_padroes`): divide cada probabilidade pela soma total. O módulo `Normalizacao.py` reúne também uma variante *uniforme*, que distribui a soma igualmente entre as direções; ela ainda não está ligada à simulação.

---

## 5. Fonte de aleatoriedade: TrueRNG

### 5.1 Objetivo

Permitir que as simulações usem números **verdadeiramente aleatórios**, gerados por hardware (TrueRNG, família ubld.it — [TrueRNG.net](https://TrueRNG.net)), no lugar do gerador pseudo-aleatório do Python, para comparar o comportamento do modelo nos dois casos.

### 5.2 Onde a aleatoriedade é usada

Com `usar_truerng` ligado, o simulador chama as versões `_true_rng` das rotinas:

| Etapa | Rotina |
| --- | --- |
| Criação dos agentes (tipo, padrão, posição, Δp) | `AgentSpawner.spawn_randomly_true_rng` |
| Movimento dos agentes R | `MovementHandler.move_agent_true_rng` / `move_all_agents_true_rng` |
| Passo síncrono | `WorldUpdater.update_synchronously_true_rng` |
| Passo assíncrono (sorteio dos agentes e do vizinho) | `WorldUpdater.update_asynchronously_true_rng` |

Todas obtêm o gerador por `TrueRNGSource.get_generator()`, que devolve o dispositivo quando ele está habilitado e o módulo `random` do Python caso contrário.

### 5.3 Funcionamento do `TrueRNGSource`

- **Detecção:** percorre as portas seriais e procura os VID:PID conhecidos (`04D8:F5FE`, `04D8:EBB5`, `16D0:0AA0`).
- **Conexão:** abre a porta (300 baud, timeout de 5 s), ativa DTR/RTS e lê um byte de teste; se nada chegar, alterna o DTR e tenta de novo antes de desistir com uma mensagem de diagnóstico.
- **Interface compatível com `random`:**
  - `random()` — float em [0, 1) com 53 bits de entropia (7 bytes lidos);
  - `uniform(a, b)`;
  - `randint(a, b)` — amostragem por rejeição, sem viés de módulo;
  - `choice`, `choices` (com pesos) e `sample` (sem repetição).
- **Concorrência:** as leituras são protegidas por um `threading.Lock`.
- **Instância única:** `set_enabled(True/False)` conecta ou fecha o dispositivo e devolve `(sucesso, mensagem)`; `is_enabled()` informa o estado.

### 5.4 Falhas e fallback

Se o `pyserial` não estiver instalado, se nenhum dispositivo for encontrado ou se a porta não responder, `set_enabled` devolve a falha com uma mensagem explicativa, a interface mostra o aviso e a simulação segue com o gerador pseudo-aleatório. Isso vale também ao abrir o programa com `usar_truerng: true` no `drima.json` e ao carregar um mundo salvo com essa opção.

---

## 6. Arquitetura do software

Os módulos de `projeto/` contêm a lógica da simulação; `main.py` contém a interface.

| Módulo | Responsabilidade |
| --- | --- |
| `Representacao.py` | Classes `Agent` (nome, tipo, padrão de movimento, posição, Δp local) e `World` (grade, parâmetros de Δp, modo, agentes e história). Inclui a busca de vizinhos. |
| `AgentSpawner.py` | Criação de agentes. `_get_next_name` gera nomes sequenciais e únicos (ex.: `R05` depois de `R04`); `find_free_spot` procura a célula livre mais próxima; `spawn_randomly` e `spawn_randomly_true_rng` sorteiam os atributos não informados. |
| `Interacoes.py` | `InteractionHandler`: regra de influência e escolha do Δp conforme o modo Global/Local. |
| `Movimento.py` | `MovementHandler`: movimento determinístico ou ponderado na grade toroidal, com versões para o TrueRNG. |
| `Normalizacao.py` | Métodos de normalização do padrão de movimento (tradicional e uniforme). |
| `WorldUpdater.py` | Motor da simulação: passos síncrono e assíncrono, com versões pseudo-aleatórias e TrueRNG. |
| `TrueRNGSource.py` | Acesso ao TrueRNG pela porta serial, com interface compatível com `random` e fallback (seção 5). |
| `WorldVisualizer.py` | Desenho da grade e dos agentes com Matplotlib. |
| `GraphVisualizer.py` | Gráficos de probabilidade por direção ao longo da história, com filtro de agentes, intervalo e direções. |
| `FileHandler.py` | Leitura e escrita do `drima.json` e dos mundos em `.json` e `.json.gz`; completa chaves ausentes com valores padrão. |
| `InterfaceTeste.py` | Protótipo de interface; não é usado pelo `main.py`. |

---

## 7. Formato dos arquivos

### 7.1 `drima.json`

| Chave | Descrição |
| --- | --- |
| `largura_da_grade`, `altura_da_grade` | Dimensões da grade |
| `delta_p_deterministico` | Δp global para influenciadores D |
| `delta_p_aleatorio` | Δp global para influenciadores R |
| `delta_p_mode` | `Global` ou `Local` |
| `numero_de_iteracoes` | Tamanho da história |
| `modo_da_interacao` | `0` = síncrono; outro valor = assíncrono |
| `async_sub_iterations` | Agentes sorteados por passo no modo assíncrono |
| `usar_truerng` | `true` para usar o TrueRNG (se conectado); padrão `false` |

Chaves ausentes são preenchidas com os valores padrão ao carregar.

### 7.2 Mundos salvos (`.json.gz`)

*Export World* grava um JSON comprimido com gzip contendo a configuração e todos os estados da história. *Load World* aceita esse arquivo ou um `.json` sem compressão. Há exemplos em [`configuracoes/conf_exemplo_uso/`](../configuracoes/conf_exemplo_uso/).
