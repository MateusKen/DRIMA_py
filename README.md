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
- Histórico completo da simulação  
- Visualização interativa (CustomTkinter)  
- Salvamento e carregamento em `.json.gz`  
- Gráficos individuais de probabilidade  

---

# 🖼️ Demonstração

(Insira imagens reais do projeto aqui.)

---

# 💻 Instalação

```bash
git clone https://github.com/SEU_USUARIO/drima-py.git
cd drima-py
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

---

# 🧱 Estrutura do Projeto

```
drima/
├── main.py
├── Representacao.py
├── Movimento.py
├── Interacoes.py
├── AgentSpawner.py
├── GraphVisualizer.py
├── FileHandler.py
└── assets/
```

---

# 🔍 Conceitos do Modelo

### **Agentes Determinísticos (D)**
- Probabilidades fixas  
- Funcionam como atratores  

### **Agentes Reativos (R)**
- Probabilidades mutáveis  
- Sofrem influência nas interações  

### **Interações**
- Ocorrem quando agentes colidem  
- Alteram apenas agentes R  
- Dependem de Δp determinístico e estocástico  

### **História**
- Cada iteração gera um “mundo”
- Todos os mundos são armazenados

---

# 📊 Exemplo de Uso: Competição Entre Marcas

Simulação do comportamento de consumidores expostos a duas campanhas concorrentes.

- Agentes D = campanhas  
- Agentes R = consumidores  

---

# 🗺️ Roadmap

### ✔ Concluído
- Reimplementação completa  
- Interface gráfica  
- Histórico de estados  
- Salvamento em JSON.gz  

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


---

# 📄 Licença

MIT License.
