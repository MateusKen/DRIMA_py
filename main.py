from InterfaceTeste.InterfaceTeste import TelaAjustavel
from projeto import World, Agent, WorldUpdater, WorldVisualizer, FileHandler, InterfaceHandler, GraphVisualizer, AgentSpawner

import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import math

# Importando todas as classes e módulos necessários do seu backend
from projeto import (
    World, Agent, AgentSpawner, FileHandler, WorldUpdater
)

class TelaAjustavel(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.simulacao_rodando = False
        self.config = FileHandler.load_config('drima.json')
        self._inicializar_mundo(primeira_vez=True) # Chama para criar os agentes iniciais

        self.configurar_janela()
        self.criar_frames_principais()
        self.criar_layout_opcoes()
        self.criar_layout_funcional()

        self._executar_simulacao_completa()
        self.after(100, self.atualizar_visualizacao_simulacao)

    def _inicializar_mundo(self, primeira_vez=False):
        """
        (Re)inicializa o mundo com os parâmetros da config.
        Preserva os agentes existentes a menos que seja a primeira inicialização.
        """
        agentes_atuais = []
        if not primeira_vez and hasattr(self, 'world') and self.world.estados:
            agentes_atuais = [ag.clone() for ag in self.world.estados[0]]

        self.world = World(
            self.config['largura_da_grade'], self.config['altura_da_grade'],
            self.config['delta_p_deterministico'], self.config['delta_p_aleatorio']
        )
        self.agent_spawner = AgentSpawner(self.world)

        if primeira_vez or not agentes_atuais:
            # Popula com agentes aleatórios apenas na primeira vez ou se não houver agentes
            for _ in range(5):
                try: self.agent_spawner.spawn_randomly()
                except RuntimeError as e: print(e); break
            self.world.estados = [[ag.clone() for ag in self.world.agentes]]
        else:
            # Preserva os agentes que o usuário já tinha
            self.world.agentes = agentes_atuais
            self.world.estados = [[ag.clone() for ag in agentes_atuais]]

    def _resetar_agentes_mundo(self):
        """Descarta todos os agentes e cria um novo conjunto aleatório."""
        self.log_message("Resetando agentes para um novo conjunto padrão.")
        self._inicializar_mundo(primeira_vez=True) # Força a recriação dos agentes
        self._executar_simulacao_completa()

    def _executar_simulacao_completa(self):
        """Executa a simulação inteira em segundo plano para gerar a história."""
        # Garante que a simulação parta do estado inicial atual
        self.world.agentes = [ag.clone() for ag in self.world.estados[0]]
        
        modo_sincrono = self.config["modo_da_interacao"] == 0
        iteracoes = self.config["numero_de_iteracoes"]

        temp_world = World(self.world.largura, self.world.altura, self.world.delta_p_det, self.world.delta_p_rand)
        temp_world.agentes = [ag.clone() for ag in self.world.estados[0]]
        
        # Recria a lista de estados a partir do estado 0
        self.world.estados = [[ag.clone() for ag in temp_world.agentes]]

        for i in range(iteracoes):
            if modo_sincrono:
                WorldUpdater.update_synchronously(temp_world)
            else:
                WorldUpdater.update_asynchronously(temp_world, iterations=len(temp_world.agentes) or 1)
            
            self.world.estados.append([ag.clone() for ag in temp_world.agentes])

        self.log_message(f"Simulação completa com {len(self.world.estados) - 1} passos gerada.")
        
        if hasattr(self, 'slider_historia'):
            self.slider_historia.configure(to=len(self.world.estados) - 1)
            self.slider_historia.set(0)
            self.atualizar_visualizacao_simulacao(0)

    def configurar_janela(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("DRIMA Simulation Interface")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{int(largura * 0.85)}x{int(altura * 0.85)}+100+50")

    def criar_frames_principais(self):
        self.frame_funcional = ctk.CTkFrame(self, fg_color="#2e3b4e")
        self.frame_funcional.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        self.frame_opcoes = ctk.CTkFrame(self, fg_color="#1e2227")
        self.frame_opcoes.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

    def criar_layout_opcoes(self):
        self.wrapper_opcoes = ctk.CTkScrollableFrame(self.frame_opcoes, fg_color="transparent", label_text="")
        self.wrapper_opcoes.pack(fill="both", expand=True)

        btn_font = ("Arial", 11)
        btn_height = 24
        
        # --- Controles Principais ---
        frame_controles = ctk.CTkFrame(self.wrapper_opcoes, fg_color="transparent")
        frame_controles.pack(fill="x", padx=10, pady=(10, 5))

        self.btn_animar = ctk.CTkButton(frame_controles, text="Animar História", height=btn_height, font=btn_font,
                                       fg_color="#27ae60", hover_color="#219150", command=self.alternar_animacao)
        self.btn_animar.pack(fill="x", pady=2)
        
        ctk.CTkButton(frame_controles, text="Carregar Mundo", height=btn_height,
                      font=btn_font, command=self.carregar_mundo_de_arquivo).pack(fill="x", pady=2)
        
        ctk.CTkButton(frame_controles, text="Exportar Mundo", height=btn_height,
                      font=btn_font, command=self.salvar_mundo_em_arquivo).pack(fill="x", pady=2)
        
        # --- Gerenciamento de Agentes ---
        frame_agentes = ctk.CTkFrame(self.wrapper_opcoes, fg_color="#23272e")
        frame_agentes.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(frame_agentes, text="Gerenciamento de Agentes", font=("Arial", 13, "bold")).pack(pady=(5,10))

        ctk.CTkButton(frame_agentes, text="Adicionar Agente", command=self.abrir_janela_adicionar_agente).pack(fill="x", padx=10, pady=5)
        
        remover_frame = ctk.CTkFrame(frame_agentes, fg_color="transparent")
        remover_frame.pack(fill="x", padx=10, pady=5)
        
        self.entry_nome_agente = ctk.CTkEntry(remover_frame, placeholder_text="Nome do agente")
        self.entry_nome_agente.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(remover_frame, text="Remover", width=80, command=self.remover_agente).pack(side="left")

        ctk.CTkButton(frame_agentes, text="Resetar Agentes para Padrão", command=self._resetar_agentes_mundo,
                      font=btn_font, height=btn_height).pack(fill="x", padx=10, pady=(10, 5))

        # --- Configurações do Mundo ---
        frame_config = ctk.CTkFrame(self.wrapper_opcoes, fg_color="#23272e")
        frame_config.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_config, text="Configurações do Mundo", font=("Arial", 13, "bold")).pack(pady=(5,10))
        
        def criar_slider_com_entry(parent, texto, initial_value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            ctk.CTkLabel(frame, text=texto, font=("Arial", 11)).pack(side="left", padx=(0, 10))
            
            entry = ctk.CTkEntry(frame, width=65)
            entry.pack(side="right")
            
            slider = ctk.CTkSlider(frame, from_=0.0001, to=1.0)
            slider.pack(side="right", fill="x", expand=True, padx=5)

            def update_entry_text(value):
                entry.delete(0, "end")
                entry.insert(0, f"{float(value):.4f}")

            slider.configure(command=update_entry_text)
            
            slider.set(initial_value)
            update_entry_text(initial_value)
            return slider, entry, frame

        self.slider_d, self.entry_d, frame_d = criar_slider_com_entry(
            frame_config, "delta_p_D", self.config['delta_p_deterministico'])
        frame_d.pack(fill="x", pady=5, padx=10)

        self.slider_r, self.entry_r, frame_r = criar_slider_com_entry(
            frame_config, "delta_p_R", self.config['delta_p_aleatorio'])
        frame_r.pack(fill="x", pady=5, padx=10)
        
        def criar_campo_config(parent, texto, valor_inicial):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(frame, text=texto, font=("Arial", 11)).pack(side="left")
            entry = ctk.CTkEntry(frame, width=120)
            entry.insert(0, str(valor_inicial))
            entry.pack(side="right")
            return entry
        
        self.entry_largura = criar_campo_config(frame_config, "Largura da Grade", self.config['largura_da_grade'])
        self.entry_altura = criar_campo_config(frame_config, "Altura da Grade", self.config['altura_da_grade'])
        self.entry_iteracoes = criar_campo_config(frame_config, "Nº de Iterações", self.config['numero_de_iteracoes'])
        
        modo_frame = ctk.CTkFrame(frame_config, fg_color="transparent")
        modo_frame.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(modo_frame, text="Modo de Interação", font=("Arial", 11)).pack(side="left")
        self.combo_modo = ctk.CTkComboBox(modo_frame, values=["Síncrono", "Assíncrono"], width=120)
        self.combo_modo.set("Síncrono" if self.config['modo_da_interacao'] == 0 else "Assíncrono")
        self.combo_modo.pack(side="right")

        ctk.CTkButton(frame_config, text="Salvar e Aplicar Config", command=self.salvar_e_aplicar_config).pack(fill="x", padx=10, pady=15)

    def criar_layout_funcional(self):
        # ... (sem alterações)
        container_pequenos = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.25)
        
        frame_grafico = ctk.CTkFrame(container_pequenos, fg_color="#3e4b5e")
        frame_grafico.pack(side="left", expand=True, fill="both", padx=(0, 5))
        ctk.CTkButton(frame_grafico, text="Mostrar Gráfico de Agente", command=self.popup_grafico).pack(expand=True, padx=10, pady=5)
        
        frame_logs_externo = ctk.CTkFrame(container_pequenos, fg_color="#4e5b6e")
        frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))
        ctk.CTkLabel(frame_logs_externo, text="Logs", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        self.frame_logs = ctk.CTkScrollableFrame(frame_logs_externo, fg_color="#232b38")
        self.frame_logs.pack(expand=True, fill="both", padx=5, pady=5)
        self.log_message("Interface iniciada.")

        self.criar_frame_simulacao()

    def criar_frame_simulacao(self):
        # ... (sem alterações)
        self.frame_simulacao = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        self.frame_simulacao.place(relx=0.02, rely=0.30, relwidth=0.96, relheight=0.68)
        
        self.figura_sim = Figure(dpi=100, facecolor="#2e3b4e")
        self.ax_sim = self.figura_sim.add_subplot(111)
        self.figura_sim.tight_layout()
        
        self.canvas_sim = FigureCanvasTkAgg(self.figura_sim, master=self.frame_simulacao)
        self.canvas_sim.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)

        frame_controles_historia = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        frame_controles_historia.pack(fill="x", padx=5, pady=5)
        
        self.label_historia_titulo = ctk.CTkLabel(frame_controles_historia, text="História:", font=("Arial", 14))
        self.label_historia_titulo.pack(side="left", padx=5)

        self.slider_historia = ctk.CTkSlider(frame_controles_historia, from_=0, to=1, command=self.atualizar_view_pelo_slider)
        self.slider_historia.pack(side="left", fill="x", expand=True)
        
        self.entry_historia = ctk.CTkEntry(frame_controles_historia, width=60)
        self.entry_historia.pack(side="left", padx=5)
        self.entry_historia.bind("<Return>", self.atualizar_view_pela_entry)

        self.label_historia_valor = ctk.CTkLabel(frame_controles_historia, text="/ 0", font=("Arial", 14), width=50)
        self.label_historia_valor.pack(side="left", padx=5)

    # --- MÉTODOS DE LÓGICA E CONTROLE ---
    
    def salvar_e_aplicar_config(self):
        try:
            self.config['largura_da_grade'] = int(self.entry_largura.get())
            self.config['altura_da_grade'] = int(self.entry_altura.get())
            self.config['numero_de_iteracoes'] = int(self.entry_iteracoes.get())
            self.config['delta_p_deterministico'] = float(self.entry_d.get())
            self.config['delta_p_aleatorio'] = float(self.entry_r.get())
            self.config['modo_da_interacao'] = 0 if self.combo_modo.get() == "Síncrono" else 1

            FileHandler.save_config(self.config, 'drima.json')
            self.log_message("Configuração salva. Recalculando simulação com agentes atuais.")
            
            # Re-inicializa o mundo com os novos parâmetros, mas preservando os agentes
            self._inicializar_mundo(primeira_vez=False)
            self._executar_simulacao_completa()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", f"Valor inválido. Verifique os campos.\nDetalhe: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar:\n{e}")

    def abrir_janela_adicionar_agente(self):
        # ... (sem alterações)
        popup = ctk.CTkToplevel(self)
        popup.title("Adicionar Novo Agente")
        popup.geometry("400x520")
        popup.grab_set()

        frame_topo = ctk.CTkFrame(popup, fg_color="transparent")
        frame_topo.pack(fill="x", padx=15, pady=10)

        tipo_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        tipo_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(tipo_frame, text="Tipo do Agente", font=("Arial", 12, "bold")).pack()
        tipo_var = ctk.StringVar(value="R")
        ctk.CTkRadioButton(tipo_frame, text="Randômico (R)", variable=tipo_var, value="R").pack(anchor="w", padx=10)
        ctk.CTkRadioButton(tipo_frame, text="Determinístico (D)", variable=tipo_var, value="D").pack(anchor="w", padx=10)
        
        pos_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        pos_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(pos_frame, text="Posição (X, Y)", font=("Arial", 12, "bold")).pack()
        pos_entries_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        pos_entries_frame.pack(pady=5)
        entry_x = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="X")
        entry_x.pack(side="left", padx=5)
        entry_y = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="Y")
        entry_y.pack(side="left", padx=5)
        ctk.CTkLabel(pos_frame, text="(Opcional)", font=("Arial", 9)).pack()

        ctk.CTkLabel(popup, text="Ações por Direção", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        
        direcoes_frame = ctk.CTkFrame(popup, fg_color="transparent")
        direcoes_frame.pack(pady=5)

        grid_layout = [
            ("NO", 0, 0), ("N", 0, 1), ("NE", 0, 2),
            ("O", 1, 0), ("X", 1, 1), ("L", 1, 2),
            ("SO", 2, 0), ("S", 2, 1), ("SE", 2, 2)
        ]
        
        direction_entries = {}
        valor_padrao = f"{1/9:.4f}"

        for direcao, row, col in grid_layout:
            label = ctk.CTkLabel(direcoes_frame, text=direcao, width=60)
            label.grid(row=row*2, column=col, padx=5, pady=(5,0))
            entry = ctk.CTkEntry(direcoes_frame, width=60, justify="center")
            entry.insert(0, valor_padrao)
            entry.grid(row=row*2 + 1, column=col, padx=5)
            direction_entries[direcao] = entry

        def _criar_agente_final(padrao_ui, tipo, pos):
            # ... (sem alterações)
            padrao_movimento = [
                padrao_ui['L'], padrao_ui['NE'], padrao_ui['N'], padrao_ui['NO'],
                padrao_ui['O'], padrao_ui['SO'], padrao_ui['S'], padrao_ui['SE'],
                padrao_ui['X']
            ]
            novo_agente = self.agent_spawner.spawn_randomly(
                type=tipo, position=pos, moving_pattern=padrao_movimento
            )
            self.world.estados[0].append(novo_agente.clone())
            self.log_message(f"Agente '{novo_agente.nome}' adicionado. Recalculando história...")
            self._executar_simulacao_completa()
            popup.destroy()

        def adicionar():
            # ... (sem alterações)
            try:
                tipo = tipo_var.get()
                pos = None
                if entry_x.get() and entry_y.get():
                    pos = (int(entry_x.get()), int(entry_y.get()))

                grid_values = {direcao: float(entry.get()) for direcao, entry in direction_entries.items()}
                soma = sum(grid_values.values())

                TOLERANCE = 1e-6
                if soma > 1.0 + TOLERANCE:
                    messagebox.showerror("Erro de Validação", f"A soma das probabilidades não pode ser maior que 1.0 (soma atual: {soma:.4f}).", parent=popup)
                    return
                
                if tipo == 'D':
                    ones = sum(1 for v in grid_values.values() if math.isclose(v, 1.0))
                    zeros = sum(1 for v in grid_values.values() if math.isclose(v, 0.0))
                    if not (ones == 1 and zeros == 8):
                         messagebox.showerror("Erro de Validação", "Para agentes Determinísticos, uma direção deve ser 1.0 e todas as outras 0.0.", parent=popup)
                         return
                
                if math.isclose(soma, 1.0, rel_tol=TOLERANCE):
                    _criar_agente_final(grid_values, tipo, pos)
                else:
                    confirm_popup = ctk.CTkToplevel(popup)
                    confirm_popup.title("Confirmar Normalização")
                    confirm_popup.geometry("380x150")
                    confirm_popup.grab_set()
                    
                    msg = f"A soma das probabilidades é {soma:.4f}.\nDeseja normalizar os valores para somarem 1.0?"
                    ctk.CTkLabel(confirm_popup, text=msg, wraplength=350).pack(pady=15, padx=10)

                    btn_frame = ctk.CTkFrame(confirm_popup, fg_color="transparent")
                    btn_frame.pack(pady=10)

                    def sim_normalizar():
                        confirm_popup.destroy()
                        normalized_values = {k: v / soma for k, v in grid_values.items()}
                        _criar_agente_final(normalized_values, tipo, pos)
                    
                    ctk.CTkButton(btn_frame, text="Sim, Normalizar", command=sim_normalizar).pack(side="left", padx=10)
                    ctk.CTkButton(btn_frame, text="Não, Corrigir Manualmente", command=confirm_popup.destroy).pack(side="left", padx=10)

            except ValueError:
                messagebox.showerror("Erro", "Valores de posição e movimento devem ser números válidos.", parent=popup)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível adicionar o agente:\n{e}", parent=popup)

        botoes_frame = ctk.CTkFrame(popup, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=15, pady=20)
        ctk.CTkButton(botoes_frame, text="Cancelar", command=popup.destroy).pack(side="right", padx=5)
        ctk.CTkButton(botoes_frame, text="Adicionar", command=adicionar).pack(side="right", padx=5)

    def remover_agente(self):
        # ... (sem alterações)
        nome_agente = self.entry_nome_agente.get()
        if not nome_agente:
            self.log_message("ERRO: Digite o nome de um agente para remover.", error=True)
            return

        agente_encontrado = None
        for agente in self.world.estados[0]:
            if agente.nome == nome_agente:
                agente_encontrado = agente
                break

        if agente_encontrado:
            self.world.estados[0].remove(agente_encontrado)
            self.log_message(f"Agente '{nome_agente}' removido. Recalculando história...")
            self._executar_simulacao_completa()
            self.entry_nome_agente.delete(0, "end")
        else:
            self.log_message(f"ERRO: Agente '{nome_agente}' não encontrado no estado inicial.", error=True)
            
    def alternar_animacao(self):
        # ... (sem alterações)
        if not self.simulacao_rodando:
            self.simulacao_rodando = True
            self.btn_animar.configure(text="Parar Animação", fg_color="#e74c3c", hover_color="#b93222")
            self.animar_passo()
        else:
            self.simulacao_rodando = False
            self.btn_animar.configure(text="Animar História", fg_color="#27ae60", hover_color="#219150")

    def animar_passo(self):
        # ... (sem alterações)
        if not self.simulacao_rodando: return
        
        current_frame = int(self.slider_historia.get())
        total_frames = len(self.world.estados) - 1
        
        if current_frame < total_frames:
            next_frame = current_frame + 1
            self.slider_historia.set(next_frame)
            self.atualizar_view_pelo_slider(next_frame)
            self.after(200, self.animar_passo)
        else:
            self.alternar_animacao()

    def carregar_mundo_de_arquivo(self):
        # ... (sem alterações)
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.config = data["config"]
            FileHandler.save_config(self.config, 'drima.json')
            
            self._inicializar_mundo() 
            
            self.world.estados = []
            for frame_data in data["states"]:
                estado = [Agent(a["nome"], a["tipo"], a["padrao_movimento"], tuple(a["posicao"])) for a in frame_data]
                self.world.estados.append(estado)

            self.world.agentes = [ag.clone() for ag in self.world.estados[0]]
            self.log_message(f"Mundo carregado de: {path.split('/')[-1]}")
            
            self.entry_d.delete(0, 'end'); self.entry_d.insert(0, f"{self.config['delta_p_deterministico']:.4f}")
            self.entry_r.delete(0, 'end'); self.entry_r.insert(0, f"{self.config['delta_p_aleatorio']:.4f}")
            self.slider_d.set(self.config['delta_p_deterministico'])
            self.slider_r.set(self.config['delta_p_aleatorio'])
            self.entry_largura.delete(0, 'end'); self.entry_largura.insert(0, self.config['largura_da_grade'])
            self.entry_altura.delete(0, 'end'); self.entry_altura.insert(0, self.config['altura_da_grade'])
            self.entry_iteracoes.delete(0, 'end'); self.entry_iteracoes.insert(0, self.config['numero_de_iteracoes'])
            self.combo_modo.set("Síncrono" if self.config['modo_da_interacao'] == 0 else "Assíncrono")
            
            self._executar_simulacao_completa()

        except Exception as e:
            self.log_message(f"ERRO ao carregar arquivo: {e}", error=True)

    def salvar_mundo_em_arquivo(self):
        # ... (sem alterações)
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            FileHandler.save_world_json(self.world, self.config, path)
            self.log_message(f"História do mundo salva em: {path.split('/')[-1]}")
        except Exception as e:
            self.log_message(f"ERRO ao salvar arquivo: {e}", error=True)

    def popup_grafico(self):
        # ... (sem alterações)
        try:
            from projeto import GraphVisualizer
            dialog = ctk.CTkInputDialog(text="Digite o nome do agente:", title="Gerar Gráfico")
            nome_agente = dialog.get_input()
            if nome_agente:
                if self.world.encontrar_agente(nome_agente) != -1:
                    GraphVisualizer.show_by_name(self.world, nome_agente)
                else:
                    self.log_message(f"ERRO: Agente '{nome_agente}' não encontrado.", error=True)
        except ImportError:
            self.log_message("ERRO: Módulo GraphVisualizer não encontrado.", error=True)
        except Exception as e:
            self.log_message(f"ERRO ao gerar gráfico: {e}", error=True)

    # --- MÉTODOS DE VISUALIZAÇÃO E SINCRONIZAÇÃO DE UI ---

    def atualizar_view_pelo_slider(self, value):
        # ... (sem alterações)
        frame_idx = int(value)
        self.atualizar_visualizacao_simulacao(frame_idx)

    def atualizar_view_pela_entry(self, event=None):
        # ... (sem alterações)
        try:
            frame_idx = int(self.entry_historia.get())
            max_frame = len(self.world.estados) - 1
            if 0 <= frame_idx <= max_frame:
                self.slider_historia.set(frame_idx)
                self.atualizar_visualizacao_simulacao(frame_idx)
            else:
                current_value = int(self.slider_historia.get())
                self.entry_historia.delete(0, "end")
                self.entry_historia.insert(0, str(current_value))
        except (ValueError, IndexError):
            current_value = int(self.slider_historia.get())
            self.entry_historia.delete(0, "end")
            self.entry_historia.insert(0, str(current_value))
            
    def atualizar_visualizacao_simulacao(self, frame_idx=0):
        # ... (sem alterações)
        self.ax_sim.clear()
        
        largura = self.world.largura
        altura = self.world.altura

        for x in range(largura):
            for y in range(altura):
                self.ax_sim.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black', lw=0.5))

        if frame_idx < len(self.world.estados):
            agentes_no_frame = self.world.estados[frame_idx]
            for agente in agentes_no_frame:
                x, y = agente.posicao
                cor = 'red' if agente.tipo == 'D' else 'blue'
                self.ax_sim.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=cor, edgecolor='black', lw=0.5))
                self.ax_sim.text(x + 0.5, y + 0.5, agente.nome, color='white', ha='center', va='center', fontsize=8, weight='bold')
        
        self.ax_sim.set_xlim(0, largura)
        self.ax_sim.set_ylim(0, altura)
        self.ax_sim.set_aspect('equal')
        self.ax_sim.invert_yaxis()
        self.ax_sim.axis('off')
        
        self.canvas_sim.draw()
        
        total_historia = len(self.world.estados) - 1
        self.entry_historia.delete(0, "end")
        self.entry_historia.insert(0, str(frame_idx))
        self.label_historia_valor.configure(text=f"/ {total_historia}")

    def log_message(self, message, error=False):
        # ... (sem alterações)
        color = "#e74c3c" if error else "white"
        label = ctk.CTkLabel(self.frame_logs, text=f"> {message}", text_color=color, font=("Consolas", 10))
        label.pack(anchor="w", padx=5)

    interface = TelaAjustavel()
    interface.mainloop()

if __name__ == "__main__":
    app = TelaAjustavel()
    app.mainloop()