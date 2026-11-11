# 🧠 DRIMA-Py — Uma Reimplementação Moderna do Modelo DRIMA em Python

<p align="center">
  <img src="assets/banner.png" width="70%" alt="DRIMA-Py Banner">
</p>

> **DRIMA-Py** é uma reimplementação moderna, aberta e extensível do modelo  
> **DRIMA – Dynamics of Reactive Interacting Multi-Agent**, originalmente desenvolvido em Mathematica.  
> Este projeto traz o modelo para Python 3.10 com uma arquitetura modular e visualização interativa.

---

# 📌 Sumário
- [Visão Geral](#visão-geral)
- [Motivação e Objetivos](#motivação-e-objetivos)
- [Funcionalidades](#funcionalidades)
- [Demonstração](#demonstração)
- [TrueRNG: aleatoriedade por hardware](#-truerng-aleatoriedade-por-hardware)
- [Instalação](#instalação)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Conceitos do Modelo](#conceitos-do-modelo)
- [Exemplo de Uso](#exemplo-de-uso)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Autores](#autores)
- [Licença](#licença)

---

# 📘 Visão Geral

O **DRIMA-Py** é um simulador multiagente baseado no modelo **DRIMA**, proposto por Oliveira (2010).  
O sistema representa agentes reativos em uma grade bidimensional que interagem localmente, alterando probabilidades de movimento e produzindo comportamentos coletivos emergentes.

A versão original foi desenvolvida em **Mathematica**, uma linguagem funcional e proprietária, o que limita acessibilidade, reprodutibilidade e extensibilidade.

Esta reimplementação em **Python 3.10** visa democratizar o acesso ao modelo, tornando-o:

✔ aberto  
✔ modular  
✔ explicável  
✔ fácil de estender  
✔ adequado para ensino e pesquisa  

---

# 🎯 Motivação e Objetivos

### 🔹 1. Reproduzir o DRIMA original  
Mantendo a dinâmica entre agentes determinísticos (D) e reativos (R).

### 🔹 2. Criar uma implementação acessível e moderna  
Com uso de Python, Programação Orientada a Objetos, interface gráfica e formatos abertos.

### 🔹 3. Permitir aplicações práticas  
Incluindo simulações sociais, mercado, difusão e vida artificial.

---

# ⚙️ Funcionalidades

- Ambiente bidimensional toroidal
- Agentes determinísticos (D) e reativos (R)
- Interações locais que alteram probabilidades
- **Δp global ou local:** a força de influência pode vir dos parâmetros do mundo (um valor para agentes D e outro para agentes R) ou de cada agente individualmente
- **Atualização síncrona ou assíncrona**, com número configurável de agentes sorteados por passo no modo assíncrono
- **Aleatoriedade por hardware (TrueRNG)** opcional, com volta automática ao gerador pseudo-aleatório
- Tela única de configuração com **rascunho**, pré-visualização, desfazer e criação de vários agentes de uma vez
- Histórico completo da simulação, calculado sob demanda e com o tempo de construção registrado
- Visualização interativa (CustomTkinter)
- Logs exportáveis em `.txt`
- Salvamento e carregamento em `.json.gz`
- Gráficos de probabilidade de **um ou vários agentes**, com filtro de intervalo e direções e exportação em imagem

---

# 🖼️ Demonstração
<p align="center">
<img src="assets/gif_demonstracao.gif" alt="Demonstração" width="80%" />
</p>

## Interface Principal

> As capturas de tela abaixo ainda são da versão anterior da interface e serão atualizadas.

A interface ocupa uma única tela, dividida em três áreas:

- **Topo:** botão **Show Agent Graph** e a área de **Logs**.
- **Centro:** a grade da simulação, com o botão 🌍 no canto superior direito para abrir o painel de configuração.
- **Base:** os controles da história (▶ / ⏸, ⏮, slider e campo `t / N`).

### Fluxo de uso

1. Ao abrir o programa, a janela **Edit Configuration** aparece automaticamente.
2. Nela você descreve o mundo (grade, Δp, modo de interação, iterações, TrueRNG) e os agentes iniciais.
3. Ao clicar em **Done → Yes, Apply**, a história completa é calculada de uma vez; o log mostra o tempo gasto (ex.: `World built and ready to animate in 1.2345s`).
4. A partir daí a história pode ser animada, navegada e analisada nos gráficos.

Enquanto a história não foi construída, os controles de reprodução ficam desabilitados. Mudar agentes ou parâmetros não recalcula nada até a confirmação, o que evita rodar o mundo inteiro a cada pequena alteração.

## Painel de Configuração (🌍)

Painel recolhível ao lado da grade, aberto pelo botão 🌍.

- **Edit Configuration** — abre a tela de edição descrita abaixo.
- **Load World** — carrega um mundo salvo (`.json.gz` ou `.json`), já com a história, e reconecta o TrueRNG se o arquivo pedir.
- **Export World** — salva a configuração e a história completa em `.json.gz`.

## Tela *Edit Configuration*

Tela única com duas colunas. Tudo é feito sobre um **rascunho**: nada muda no mundo atual até a confirmação final.

### Coluna da esquerda — *Initial Agent Configuration*

- **Pré-visualização** da grade com os agentes iniciais (D em vermelho, R em azul).
- **Add Agent** — abre a janela *Add New Agent*.
- **Add Multiple Agents** — informa quantos agentes R e quantos D criar; posições e padrões são sorteados.
- **Remove Selected** — remove o agente escolhido na lista.
- **Remove All Agents** — esvazia o mundo.
- **Undo Last Change** — desfaz a última adição ou remoção.

### Coluna da direita — *World Settings*

**Delta-P Mode: Global / Local** (🔬 / 🌐)  
- **Global:** usa os valores do mundo — `delta_p_D` quando o influenciador é determinístico e `delta_p_R` quando é reativo.
- **Local:** usa o Δp do próprio agente **influenciador**, definido no campo *Influence (Δp)* ao criar o agente. Neste modo, os sliders globais ficam ocultos.

**Delta_p Sliders** (🔧)  
- Ajustam `delta_p_D` e `delta_p_R` pelo slider ou digitando o valor.

**Grid Width / Grid Height / No. of Iterations** (📐 #️⃣)  
- Dimensões da grade toroidal e tamanho da história.

**Interaction Mode: Synchronous / Asynchronous** (🔁)  
- **Síncrono:** em cada passo, todos os agentes interagem com seus vizinhos e depois se movem.
- **Assíncrono:** em cada passo, um subconjunto de agentes é sorteado (sem repetição); cada um interage com **um** vizinho aleatório e se move. O tamanho do sorteio é definido no campo que aparece ao lado do seletor (`async_sub_iterations` no `drima.json`).

**Use TrueRNG Hardware** (🎲)  
- Liga ou desliga o gerador de números **verdadeiramente aleatórios** (ver [TrueRNG](#-truerng-aleatoriedade-por-hardware)).
- É aplicado na hora e salvo no `drima.json`; um aviso mostra se a conexão deu certo. Se o dispositivo não for encontrado, o switch volta para desligado e o programa segue com o gerador pseudo-aleatório do Python.

**Done / Cancel**  
- **Done** valida os campos e pergunta se deve aplicar: **Yes, Apply** grava a configuração, substitui os agentes iniciais pelos do rascunho e constrói a história; **No, Discard** descarta o rascunho.
- **Cancel** fecha sem alterar nada.

## Janela *Add New Agent*

<p align="center">
  <img src="assets/add_new_agent.png" width="50%" alt="Janela Add New Agent">
</p>

- **Agent Type** — `Random (R)` ou `Deterministic (D)`.
- **Position (X, Y)** — opcional. Se ficar vazio, a posição é sorteada; se estiver ocupada, o agente vai para a célula livre mais próxima.
- **Influence (Δp)** — opcional. É o Δp **local** do agente, usado no modo *Local* quando ele é o influenciador.
- **Agente R:**
  - **Uniform probabilities** (marcado por padrão) — todas as direções com a mesma probabilidade.
  - Desmarcando, aparece a rosa dos ventos com as 9 direções (NW, N, NE, W, X, E, SW, S, SE; `X` = ficar parado) para digitar cada probabilidade.
  - **Allow movement in X (stay in place)** — desmarcado, bloqueia `X` em 0.
  - Se a soma não for 1, a janela **Confirm Normalization** oferece `Yes, Normalize` ou `No, Fix Manually`.
- **Agente D:** escolhe-se **uma única direção** em uma grade de botões; ela recebe probabilidade 1.

## Área de Visualização

### Logs

- **O que mostra:** histórico textual de eventos — criação/remoção de agentes, construção do mundo (com o tempo gasto), estado do TrueRNG, salvamentos e erros (em vermelho).
- **Download Logs** — salva todas as linhas exibidas em um `.txt`.
- **Clear Logs** — limpa a área de logs (e o que será exportado depois).

### Animação / História

<p align="center">
<img src="assets/gif_animacao.gif" alt="Animação da história" width="80%" />
</p>

- **▶ / ⏸** — inicia ou pausa a reprodução a partir do ponto atual.
- **⏮** — volta ao início (frame 0); só fica ativo depois de avançar.
- **Slider e campo `t / N`** — vão direto para uma iteração específica.

### Gerar Gráficos — *Advanced Graph Filter*

<p align="center">
  <img src="assets/filtro_grafico.png" width="60%" alt="Janela de filtro de gráficos">
</p>

- `Select agents` — lista suspensa com seleção múltipla; gera um gráfico por agente.  
- `History Range` — campos `Start` / `End` para limitar o intervalo de iterações.  
- `Directions to Display` — checkboxes para as 9 direções.
- `Generate Graph` abre a janela com os gráficos; nela, `Export Image` salva os gráficos como imagem.

---

# 🎲 TrueRNG: aleatoriedade por hardware

O DRIMA-Py pode usar um **TrueRNG** (família ubld.it, [TrueRNG.net](https://TrueRNG.net)) — um gerador de números aleatórios por hardware conectado via USB — no lugar do gerador pseudo-aleatório do Python. Isso permite comparar simulações com aleatoriedade "verdadeira" e pseudo-aleatória.

- **Onde é usado:** no sorteio dos agentes iniciais (tipo, padrão, posição e Δp), no movimento dos agentes R e, no modo assíncrono, no sorteio dos agentes e dos vizinhos de cada passo.
- **Como funciona:** `projeto/TrueRNGSource.py` detecta o dispositivo pelas portas seriais (VID:PID conhecidos), lê os bytes aleatórios e oferece a mesma interface do módulo `random` (`random`, `uniform`, `randint`, `choice`, `choices`, `sample`). Inteiros são sorteados por amostragem por rejeição, sem viés.
- **Sem o dispositivo:** se ele não estiver conectado, ou se o `pyserial` não estiver instalado, o programa avisa e usa o gerador pseudo-aleatório padrão.
- **Requisitos:** `pyserial` (já está no `requirements.txt`) e o driver do dispositivo instalado. Feche outros programas que usem a porta serial do TrueRNG antes de ligar o switch.

---

# 💻 Instalação

```bash
git clone https://github.com/MateusKen/DRIMA_py.git
cd DRIMA_py
```

Ambiente virtual:

```bash
python3.10 -m venv venv
source venv/bin/activate
# ou no Windows
venv\Scripts\activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

---

# ▶️ Como Executar

```bash
python main.py
```

### Gerar um executável (opcional)

O arquivo `main.spec` já inclui os módulos do `pyserial` usados pelo TrueRNG:

```bash
pip install pyinstaller
pyinstaller main.spec
```

O executável é gerado em `dist/`.

---

# 🧱 Estrutura do Projeto

```
DRIMA_py/
├── main.py                       # interface gráfica principal (ponto de entrada)
├── main.spec                     # configuração do PyInstaller para gerar o executável
├── drima.json                    # configuração padrão do mundo
├── requirements.txt
├── docs/
│   └── DOCUMENTACAO_TECNICA.md   # documentação técnica atualizada
├── DOCUMENTACAO_TECNICA_DRIMA.pdf # versão em PDF entregue em nov/2025
├── assets/ e imagens/            # imagens usadas na documentação
├── configuracoes/                # mundos salvos (.json / .gz) e exemplos de uso
└── projeto/
    ├── Representacao.py          # classes Agent e World
    ├── AgentSpawner.py           # criação de agentes com nomes sequenciais
    ├── Interacoes.py             # regras de influência (Δp global/local)
    ├── Movimento.py              # movimento ponderado pelo padrão de cada agente
    ├── Normalizacao.py           # métodos de normalização dos padrões de movimento
    ├── WorldUpdater.py           # motor da simulação (síncrono e assíncrono)
    ├── WorldVisualizer.py        # desenho da grade
    ├── GraphVisualizer.py        # gráficos de probabilidade por agente
    ├── FileHandler.py            # leitura/escrita do drima.json e dos mundos .json.gz
    ├── TrueRNGSource.py          # acesso ao gerador TrueRNG (hardware) com fallback para random
    └── InterfaceTeste.py         # protótipo de interface (não é usado pelo main.py)
```

## ⚙️ Configuração (`drima.json`)

| Chave | Descrição |
| --- | --- |
| `largura_da_grade`, `altura_da_grade` | Dimensões da grade toroidal |
| `delta_p_deterministico` | Δp global usado quando o influenciador é D |
| `delta_p_aleatorio` | Δp global usado quando o influenciador é R |
| `delta_p_mode` | `Global` ou `Local` |
| `numero_de_iteracoes` | Tamanho da história gerada |
| `modo_da_interacao` | `0` = síncrono; outro valor = assíncrono |
| `async_sub_iterations` | Agentes sorteados por passo no modo assíncrono |
| `usar_truerng` | `true` para usar o TrueRNG (se conectado) |

Para a descriçãocompleta da interface e da arquitetura, veja a [documentação técnica](docs/DOCUMENTACAO_TECNICA.md).

---

# 🔍 Conceitos do Modelo

### **Agentes Determinísticos (D)**
- Probabilidades fixas  
- Funcionam como atratores  

### **Agentes Reativos (R)**
- Probabilidades mutáveis  
- Sofrem influência nas interações  

### **Interações**
- Ocorrem entre agentes vizinhos na grade
- Alteram apenas agentes R
- Para cada direção em que o vizinho tem probabilidade maior, o agente R soma Δp; em seguida o padrão é normalizado para somar 1
- O Δp vem dos parâmetros globais do mundo ou do próprio influenciador (modo Local)

### **História**
- Cada iteração gera um “mundo”
- Todos os mundos são armazenados

---

## 🥤 Exemplo Prático: Competição entre duas marcas concorrentes

Para demonstrar o uso do DRIMA-Py, foi construído um cenário simples de **competição entre duas marcas**, representadas como forças opostas que influenciam consumidores.

- O exemplo se encontra nesse path do projeto caso quieram testar:
  [`configuracoes/conf_exemplo_uso/conf_coca_pepsi.gz`](configuracoes/conf_exemplo_uso/conf_coca_pepsi.gz)

### 🔹 Modelagem
- **Agentes Determinísticos (D):** representam as campanhas das marcas.  
  - Marca L → influencia movimento para o Leste  
  - Marca N → influencia movimento para o Norte  
- **Agentes Reativos (R):** representam consumidores, que iniciam com comportamento aleatório e podem ser influenciados.

### 🔹 Dinâmica
1. A simulação inicia com agentes D posicionados na grade.
2. Consumidores (R) movem-se aleatoriamente.
3. Quando um consumidor encontra um agente determinístico:
   - Sua probabilidade de movimento é alterada.
   - Ele passa a “preferir” a direção associada àquela marca.
4. Ao longo das iterações, observamos:
   - **Dispersão**, se as forças forem fracas ou equilibradas.  
   - **Convergência**, se uma marca exercer influência mais forte.

### 🔹 Resultado Esperado
- O modelo mostra como **pequenas influências locais** (encontros entre agentes) podem produzir:
  - preferência coletiva,
  - polarização,
  - ou um mercado indeciso.
- O comportamento emergente depende dos parâmetros das campanhas e da intensidade das interações.

Este exemplo demonstra o potencial do DRIMA-Py para simular dinâmicas sociais e de mercado de forma simples e exploratória.

<p align="center">
  <img src="assets/grafico_r_nconverge.png" width="70%" alt="DRIMA-Py Visualization Area">
</p>

<p align="center">
  <img src="assets/grafico_agente_rconverge.png" width="70%" alt="DRIMA-Py Visualization Area">
</p>

Com esse gráficos é possível observar essas tendências, tanto de indecisão desse mercado como a de convergência, sendo que no primeiro gráfico temos o agente R não convergindo para nenhuma direção específica, enquanto no segundo gráfico temos o agente R convergindo para a direção Leste, influenciado pelo agente D posicionado nessa direção.

---

# 🗺️ Roadmap

### ✔ Concluído
- Reimplementação completa
- Interface gráfica
- Histórico de estados
- Salvamento em JSON.gz
- Δp local por agente
- Modo assíncrono com sub-iterações configuráveis
- Gráficos de múltiplos agentes com exportação de imagem
- Integração com o gerador TrueRNG
- Tela única de configuração com rascunho e desfazer
- Exportação de logs

### 🚧 Futuro
- Métricas de convergência  
- Novos tipos de agentes  
- Automação de experimentos  
- Versão web  

---

# 🤝 Contribuindo

Contribuições são bem-vindas!  
Envie *Issues* e *Pull Requests*.

---

# 👨‍💻 Autores

**Mateus Kenzo Iochimoto**  
📧 [mateus.iochimoto@gmail.com](mailto:mateus.iochimoto@gmail.com)   
🔗  [Linkedin Mateus Kenzo Iochimoto](https://www.linkedin.com/in/mateus-kenzo-iochimoto/)  
🐙  [GitHub MateusKen](https://github.com/MateusKen  )

---

**Gabriel Gonzaga Chung**  
📧 [gabrielgchung@gmail.com](mailto:gabrielgchung@gmail.com)  
🔗 [LinkedIn Gabriel Gonzaga Chung](https://www.linkedin.com/in/gabriel-chung-757822297)  
🐙 [GitHub gabrielc231](https://github.com/gabrielc231)

---

**Igor Benites Moura**  
📧 [contato.igorbenites@gmail.com](mailto:contato.igorbenites@gmail.com)  
🔗 [LinkedIn Igor Benites Moura](https://www.linkedin.com/in/igor-benites-moura?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)  
🐙 [GitHub Darkyie](https://github.com/Darkyie)
