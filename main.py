import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from projeto.GraphVisualizer import GraphVisualizer
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import math

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
        self.log_message("Resetting agents to a new default set.")
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
        
        # --- INÍCIO DA LÓGICA MODIFICADA ---
        num_agentes = len(temp_world.agentes) or 1
        async_iters = 1 # Valor padrão
        
        if not modo_sincrono:
            try:
                # Pega o valor da config, com padrão 1
                async_iters = int(self.config.get('async_sub_iterations', 1))
            except ValueError:
                async_iters = 1 # Volta ao padrão 1 se o valor for inválido
            
            # Garante que o valor esteja dentro dos limites (1 até N agentes)
            if async_iters > num_agentes:
                async_iters = num_agentes
            if async_iters < 1:
                async_iters = 1
        # --- FIM DA LÓGICA MODIFICADA ---

        # Recria a lista de estados a partir do estado 0
        self.world.estados = [[ag.clone() for ag in temp_world.agentes]]

        for i in range(iteracoes):
            if modo_sincrono:
                WorldUpdater.update_synchronously(temp_world)
            else:
                # --- LINHA MODIFICADA ---
                # Usa o novo valor de iterações assíncronas
                WorldUpdater.update_asynchronously(temp_world, iterations=async_iters)
            
            self.world.estados.append([ag.clone() for ag in temp_world.agentes])

        self.log_message(f"Simulation completed with {len(self.world.estados) - 1} steps generated.")
        
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

        # --- Main Controls ---
        frame_controles = ctk.CTkFrame(self.wrapper_opcoes, fg_color="transparent")
        frame_controles.pack(fill="x", padx=10, pady=(10, 5))

        self.btn_animar = ctk.CTkButton(frame_controles, text="Animate History", height=btn_height, font=btn_font,
                                        fg_color="#27ae60", hover_color="#219150", command=self.alternar_animacao)
        self.btn_animar.pack(fill="x", pady=2)

        ctk.CTkButton(frame_controles, text="Load World", height=btn_height,
                      font=btn_font, command=self.carregar_mundo_de_arquivo).pack(fill="x", pady=2)

        ctk.CTkButton(frame_controles, text="Export World", height=btn_height,
                      font=btn_font, command=self.salvar_mundo_em_arquivo).pack(fill="x", pady=2)

        # --- Agent Management ---
        frame_agentes = ctk.CTkFrame(self.wrapper_opcoes, fg_color="#23272e")
        frame_agentes.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(frame_agentes, text="Agent Management", font=("Arial", 13, "bold")).pack(pady=(5, 10))

        ctk.CTkButton(frame_agentes, text="Add Agent", command=self.abrir_janela_adicionar_agente).pack(fill="x",
                                                                                                        padx=10, pady=5)

        remover_frame = ctk.CTkFrame(frame_agentes, fg_color="transparent")
        remover_frame.pack(fill="x", padx=10, pady=5)

        self.entry_nome_agente = ctk.CTkEntry(remover_frame, placeholder_text="Agent name")
        self.entry_nome_agente.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(remover_frame, text="Remove", width=80, command=self.remover_agente).pack(side="left")

        ctk.CTkButton(frame_agentes, text="Reset Agents to Default", command=self._resetar_agentes_mundo,
                      font=btn_font, height=btn_height).pack(fill="x", padx=10, pady=(10, 5))

        # --- World Settings ---
        frame_config = ctk.CTkFrame(self.wrapper_opcoes, fg_color="#23272e")
        frame_config.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_config, text="World Settings", font=("Arial", 13, "bold")).pack(pady=(5, 10))

        def criar_slider_com_entry(parent, text, initial_value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            ctk.CTkLabel(frame, text=text, font=("Arial", 11)).pack(side="left", padx=(0, 10))

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

        def criar_campo_config(parent, text, initial_value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(frame, text=text, font=("Arial", 11)).pack(side="left")
            entry = ctk.CTkEntry(frame, width=120)
            entry.insert(0, str(initial_value))
            entry.pack(side="right")
            return entry

        self.entry_largura = criar_campo_config(frame_config, "Grid Width", self.config['largura_da_grade'])
        self.entry_altura = criar_campo_config(frame_config, "Grid Height", self.config['altura_da_grade'])
        self.entry_iteracoes = criar_campo_config(frame_config, "No. of Iterations", self.config['numero_de_iteracoes'])

        mode_frame = ctk.CTkFrame(frame_config, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(mode_frame, text="Interaction Mode", font=("Arial", 11)).pack(side="left")

        # --- INÍCIO DAS MODIFICAÇÕES ---
        
        # 1. Criar a Entry para iterações assíncronas (padrão 1 se não existir)
        default_async_iters = self.config.get('async_sub_iterations', 1)
        self.entry_async_iter = ctk.CTkEntry(mode_frame, width=50)
        self.entry_async_iter.insert(0, str(default_async_iters))
        # Não fazer .pack() ainda, o _toggle_async_entry fará isso

        # 2. Criar ComboBox e ligar o 'command'
        self.combo_modo = ctk.CTkComboBox(mode_frame, values=["Synchronous", "Asynchronous"], width=120,
                                            command=self._toggle_async_entry) # Adicionado command
        
        # self.combo_modo.pack(side="right") # <-- LINHA REMOVIDA
        
        # 3. Definir o estado inicial e chamar o toggle
        initial_mode = "Synchronous" if self.config['modo_da_interacao'] == 0 else "Asynchronous"
        self.combo_modo.set(initial_mode)
        self._toggle_async_entry(initial_mode) # Chama para definir a visibilidade e ORDEM inicial
        
        # --- FIM DAS MODIFICAÇÕES ---

        ctk.CTkButton(frame_config, text="Save and Apply Config", command=self.salvar_e_aplicar_config).pack(fill="x",
                                                                                                            padx=10,
                                                                                                            pady=15)

    def criar_layout_funcional(self):
        # ... (sem alterações)
        container_pequenos = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.25)

        frame_grafico = ctk.CTkFrame(container_pequenos, fg_color="#3e4b5e")
        frame_grafico.pack(side="left", expand=True, fill="both", padx=(0, 5))
        ctk.CTkButton(frame_grafico, text="Show Agent Graph", command=self.abrir_janela_grafico).pack(expand=True,padx=10, pady=5)

        frame_logs_externo = ctk.CTkFrame(container_pequenos, fg_color="#4e5b6e")
        frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))
        ctk.CTkLabel(frame_logs_externo, text="Logs", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        self.frame_logs = ctk.CTkScrollableFrame(frame_logs_externo, fg_color="#232b38")
        self.frame_logs.pack(expand=True, fill="both", padx=5, pady=5)
        def update_label_wraps(event):
            padding = 30
            new_width = event.width - padding
            if new_width < 100: new_width = 100
            for child in self.frame_logs.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(wraplength=new_width)
        self.frame_logs.bind("<Configure>", update_label_wraps)
        self.log_message("Interface initiated.")

        self.criar_frame_simulacao()

    def _toggle_async_entry(self, choice):
        """Mostra ou esconde a caixa de iterações assíncronas."""
        
        # 1. Desempacota ambos os widgets para garantir uma re-ordenação limpa
        self.entry_async_iter.pack_forget()
        self.combo_modo.pack_forget()

        # 2. Re-empacota na ordem correta
        # Para obter [ComboBox] [Entry]
        # O widget empacotado PRIMEIRO (entry) fica mais à direita.
        # O widget empacotado SEGUNDO (combo_modo) fica à esquerda do primeiro.
        
        if choice == "Asynchronous":
            self.entry_async_iter.pack(side="right", padx=(5, 0))
            self.combo_modo.pack(side="right")
        else:
            # Se for "Synchronous", apenas empacota η ComboBox
            self.combo_modo.pack(side="right")

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

        self.label_historia_titulo = ctk.CTkLabel(frame_controles_historia, text="History:", font=("Arial", 14))
        self.label_historia_titulo.pack(side="left", padx=5)

        self.slider_historia = ctk.CTkSlider(frame_controles_historia, from_=0, to=1,
                                             command=self.atualizar_view_pelo_slider)
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
            self.config['modo_da_interacao'] = 0 if self.combo_modo.get() == "Synchronous" else int(self.entry_async_iter.get())
            
            # --- LINHA ADICIONADA ---
            # Salva o valor da nova caixa (mesmo se estiver oculta)
            self.config['async_sub_iterations'] = int(self.entry_async_iter.get())

            FileHandler.save_config(self.config, 'drima.json')
            self.log_message("Config saved. Recalculating simulation with current agents.")

            # Re-inicializa o mundo com os novos parâmetros, mas preservando os agentes
            self._inicializar_mundo(primeira_vez=False)
            self._executar_simulacao_completa()

        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid value. Please check all fields.\nDetail: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving:\n{e}")

    def abrir_janela_adicionar_agente(self):
        # ... (sem alterações)
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Agent")
        popup.geometry("400x550")
        popup.grab_set()

        frame_topo = ctk.CTkFrame(popup, fg_color="transparent")
        frame_topo.pack(fill="x", padx=15, pady=10)

        tipo_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        tipo_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(tipo_frame, text="Agent Type", font=("Arial", 12, "bold")).pack()
        tipo_var = ctk.StringVar(value="R")
        ctk.CTkRadioButton(tipo_frame, text="Random (R)", variable=tipo_var, value="R").pack(anchor="w", padx=10)
        ctk.CTkRadioButton(tipo_frame, text="Deterministic (D)", variable=tipo_var, value="D").pack(anchor="w", padx=10)

        pos_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        pos_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(pos_frame, text="Position (X, Y)", font=("Arial", 12, "bold")).pack()
        pos_entries_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        pos_entries_frame.pack(pady=5)
        entry_x = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="X")
        entry_x.pack(side="left", padx=5)
        entry_y = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="Y")
        entry_y.pack(side="left", padx=5)
        ctk.CTkLabel(pos_frame, text="(Optional)", font=("Arial", 9)).pack()

        ctk.CTkLabel(popup, text="Actions by Direction", font=("Arial", 12, "bold")).pack(pady=(15, 5))

        direcoes_frame = ctk.CTkFrame(popup, fg_color="transparent")
        direcoes_frame.pack(pady=5)

        grid_layout = [
            ("NW", 0, 0), ("N", 0, 1), ("NE", 0, 2),
            ("W", 1, 0), ("X", 1, 1), ("E", 1, 2),
            ("SW", 2, 0), ("S", 2, 1), ("SE", 2, 2)
        ]

        direction_entries = {}
        valor_padrao = f"{1 / 9:.4f}"

        for direcao, row, col in grid_layout:
            label = ctk.CTkLabel(direcoes_frame, text=direcao, width=60)
            label.grid(row=row * 2, column=col, padx=5, pady=(5, 0))
            entry = ctk.CTkEntry(direcoes_frame, width=60, justify="center")
            entry.insert(0, valor_padrao)
            entry.grid(row=row * 2 + 1, column=col, padx=5)
            direction_entries[direcao] = entry

        def atualizar_campos_x():
            if not toggle_x_var.get():
                direction_entries["X"].configure(state="normal")  # Habilita para editar
                direction_entries["X"].delete(0, "end")
                direction_entries["X"].insert(0, "0.0000")
                direction_entries["X"].configure(state="disabled")  # Desabilita após editar
                prob = 1.0 / 8
                for direcao, entry in direction_entries.items():
                    if direcao != "X":
                        entry.delete(0, "end")
                        entry.insert(0, f"{prob:.4f}")
            else:
                direction_entries["X"].configure(state="normal")
                direction_entries["X"].delete(0, "end")
                direction_entries["X"].insert(0, f"{1 / 9:.4f}")
                prob = 1.0 / 9
                for direcao, entry in direction_entries.items():
                    if direcao != "X":
                        entry.delete(0, "end")
                        entry.insert(0, f"{prob:.4f}")

        toggle_x_var = ctk.BooleanVar(value=True)  # Adicione esta linha antes do CTkCheckBox

        ctk.CTkCheckBox(
            popup,
            text="Allow movement in X (stay in place)",
            variable=toggle_x_var,
            command=atualizar_campos_x
        ).pack(pady=(5, 10))

        atualizar_campos_x()

        def _criar_agente_final(padrao_ui, tipo, pos):
            # ... (sem alterações)
            padrao_movimento = [
                padrao_ui['E'], padrao_ui['NE'], padrao_ui['N'], padrao_ui['NW'],
                padrao_ui['W'], padrao_ui['SW'], padrao_ui['S'], padrao_ui['SE'],
                padrao_ui['X']
            ]
            novo_agente = self.agent_spawner.spawn_randomly(
                type=tipo, position=pos, moving_pattern=padrao_movimento
            )
            self.world.estados[0].append(novo_agente.clone())
            self.log_message(f"Agent '{novo_agente.nome}' added. Recalculating history...")
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
                if not toggle_x_var.get():
                    grid_values["X"] = 0.0
                soma = sum(grid_values.values())

                TOLERANCE = 1e-6
                if soma > 1.0 + TOLERANCE:
                    messagebox.showerror("Validation Error",
                                         f"The sum of probabilities cannot be greater than 1.0 (current sum: {soma:.4f}).",
                                         parent=popup)
                    return

                if tipo == 'D':
                    ones = sum(1 for v in grid_values.values() if math.isclose(v, 1.0))
                    zeros = sum(1 for v in grid_values.values() if math.isclose(v, 0.0))
                    if not (ones == 1 and zeros == 8):
                        messagebox.showerror("Validation Error",
                                             "For Deterministic agents, one direction must be 1.0 and all others 0.0.",
                                             parent=popup)
                        return

                if math.isclose(soma, 1.0, rel_tol=TOLERANCE):
                    _criar_agente_final(grid_values, tipo, pos)
                else:
                    confirm_popup = ctk.CTkToplevel(popup)
                    confirm_popup.title("Confirm Normalization")
                    confirm_popup.geometry("380x150")
                    confirm_popup.grab_set()

                    msg = f"The sum of probabilities is {soma:.4f}.\nDo you want to normalize the values to sum 1.0?"
                    ctk.CTkLabel(confirm_popup, text=msg, wraplength=350).pack(pady=15, padx=10)

                    btn_frame = ctk.CTkFrame(confirm_popup, fg_color="transparent")
                    btn_frame.pack(pady=10)

                    def sim_normalizar():
                        confirm_popup.destroy()
                        normalized_values = {k: v / soma for k, v in grid_values.items()}
                        _criar_agente_final(normalized_values, tipo, pos)

                    ctk.CTkButton(btn_frame, text="Yes, Normalize", command=sim_normalizar).pack(side="left", padx=10)
                    ctk.CTkButton(btn_frame, text="No, Fix Manually", command=confirm_popup.destroy).pack(side="left",
                                                                                                        padx=10)

            except ValueError:
                messagebox.showerror("Error", "Position and movement values must be valid numbers.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add agent:\n{e}", parent=popup)

        botoes_frame = ctk.CTkFrame(popup, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=15, pady=20)
        ctk.CTkButton(botoes_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)
        ctk.CTkButton(botoes_frame, text="Add", command=adicionar).pack(side="right", padx=5)

    def remover_agente(self):
        # ... (sem alterações)
        nome_agente = self.entry_nome_agente.get()
        if not nome_agente:
            self.log_message("ERROR: Please enter an agent name to remove.", error=True)
            return

        agente_encontrado = None
        for agente in self.world.estados[0]:
            if agente.nome == nome_agente:
                agente_encontrado = agente
                break

        if agente_encontrado:
            self.world.estados[0].remove(agente_encontrado)
            self.log_message(f"Agent '{nome_agente}' removed. Recalculating history...")
            self._executar_simulacao_completa()
            self.entry_nome_agente.delete(0, "end")
        else:
            self.log_message(f"ERROR: Agent '{nome_agente}' not found in the initial state.", error=True)

    def alternar_animacao(self):
        # ... (sem alterações)
        if not self.simulacao_rodando:
            self.simulacao_rodando = True
            self.btn_animar.configure(text="Stop Animation", fg_color="#e74c3c", hover_color="#b93222")
            self.animar_passo()
        else:
            self.simulacao_rodando = False
            self.btn_animar.configure(text="Animate History", fg_color="#27ae60", hover_color="#219150")

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
        path = filedialog.askopenfilename(defaultextension=".gz", filetypes=[("JSON, Gzip files", "*.json *.gz"),
                                                                            ("Gzip files", "*.gz"),
                                                                            ("All files", "*.*")])
        if not path: return
        try:
            root, ext = os.path.splitext(path)
            if ext == '.json':
                with open(path, 'r') as f:
                    data = json.load(f)
                self.config = data["config"]

            if ext == '.gz':
                data = FileHandler.load_world_json_gzipped(path)
                self.config = data["config"]

            FileHandler.save_config(self.config, 'drima.json')
            self._inicializar_mundo()

            self.world.estados = []
            for frame_data in data["states"]:
                estado = [Agent(a["nome"], a["tipo"], a["padrao_movimento"], tuple(a["posicao"])) for a in frame_data]
                self.world.estados.append(estado)

            self.world.agentes = [ag.clone() for ag in self.world.estados[0]]
            self.log_message(f"World loaded from: {path.split('/')[-1]}")

            self.entry_d.delete(0, 'end')
            self.entry_d.insert(0, f"{self.config['delta_p_deterministico']:.4f}")
            self.entry_r.delete(0, 'end')
            self.entry_r.insert(0, f"{self.config['delta_p_aleatorio']:.4f}")
            self.slider_d.set(self.config['delta_p_deterministico'])
            self.slider_r.set(self.config['delta_p_aleatorio'])
            self.entry_largura.delete(0, 'end')
            self.entry_largura.insert(0, self.config['largura_da_grade'])
            self.entry_altura.delete(0, 'end')
            self.entry_altura.insert(0, self.config['altura_da_grade'])
            self.entry_iteracoes.delete(0, 'end')
            self.entry_iteracoes.insert(0, self.config['numero_de_iteracoes'])
            self.combo_modo.set("Synchronous" if self.config['modo_da_interacao'] == 0 else "Asynchronous")

            # --- INÍCIO DAS LINHAS ADICIONADAS ---
            # Atualiza a nova entry com o valor da config (ou padrão 1)
            default_async_iters = self.config.get('async_sub_iterations', 1)
            self.entry_async_iter.delete(0, 'end')
            self.entry_async_iter.insert(0, str(default_async_iters))
            
            # Garante que a visibilidade da entry esteja correta
            self._toggle_async_entry(self.combo_modo.get())
            # --- FIM DAS LINHAS ADICIONADAS ---

            self._executar_simulacao_completa()

        except Exception as e:
            self.log_message(f"ERROR loading file: {e}", error=True)

    def salvar_mundo_em_arquivo(self):
        # ... (sem alterações)
        path = filedialog.asksaveasfilename(defaultextension=".gz",
                                            filetypes=[("Gzip files", ".gz"),
                                                     ("All files", ".*")])
        if not path: return
        try:
            FileHandler.save_world_json_gzipped(self.world, self.config, path)
            self.log_message(f"World history saved to: {path.split('/')[-1]}")
        except Exception as e:
            self.log_message(f"ERROR saving file: {e}", error=True)

    def abrir_janela_grafico(self):

        popup = ctk.CTkToplevel(self)
        popup.title("Advanced Graph Filter")
        popup.geometry("600x450")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select agents:", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        nomes_agentes = [agente.nome for agente in self.world.agentes]
        agentes_vars = {nome: ctk.BooleanVar(value=False) for nome in nomes_agentes}

        # Custom dropdown
        dropdown_frame = ctk.CTkFrame(popup, fg_color="transparent")
        dropdown_frame.pack(padx=15, pady=10, fill="x")

        btn_selecao = ctk.CTkButton(dropdown_frame, text="None selected")
        btn_selecao.pack(fill="x")

        dropdown_open = [False]

        def atualizar_texto_botao():
            selecionados = [nome for nome, var in agentes_vars.items() if var.get()]
            texto = ", ".join(selecionados) if selecionados else "None selected"
            btn_selecao.configure(text=texto)

        def fechar_dropdown(event=None):
            if dropdown_open[0]:
                dropdown_window.destroy()
                dropdown_open[0] = False

        def abrir_dropdown(event=None):
            nonlocal dropdown_window
            if dropdown_open[0]:
                fechar_dropdown()
                return
            dropdown_open[0] = True
            x = btn_selecao.winfo_rootx()
            y = btn_selecao.winfo_rooty() + btn_selecao.winfo_height()
            dropdown_window = ctk.CTkToplevel(popup, fg_color="#222e3c")
            dropdown_window.overrideredirect(True)
            dropdown_window.geometry(f"250x300+{x}+{y}")
            frame = ctk.CTkScrollableFrame(dropdown_window, fg_color="transparent", height=220)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            for nome in nomes_agentes:
                cb = ctk.CTkCheckBox(frame, text=nome, variable=agentes_vars[nome],
                                     command=atualizar_texto_botao)
                cb.pack(anchor="w", padx=5, pady=2)
            ctk.CTkButton(dropdown_window, text="OK", command=fechar_dropdown).pack(pady=10)
            dropdown_window.bind("<FocusOut>", lambda e: fechar_dropdown())
            dropdown_window.focus_set()

        dropdown_window = None
        btn_selecao.configure(command=abrir_dropdown)

        # --- History Range ---
        frame_history = ctk.CTkFrame(popup, fg_color="transparent")
        frame_history.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(frame_history, text="History Range:", font=("Arial", 12)).pack(side="left")
        entry_start_frame = ctk.CTkEntry(frame_history, width=70, placeholder_text="Start")
        entry_start_frame.insert(0, "0")
        entry_start_frame.pack(side="left", padx=5)
        ctk.CTkLabel(frame_history, text="to").pack(side="left")
        entry_end_frame = ctk.CTkEntry(frame_history, width=70, placeholder_text="End")
        entry_end_frame.insert(0, str(len(self.world.estados) - 1))
        entry_end_frame.pack(side="left", padx=5)

        # --- Direction Checkboxes ---
        ctk.CTkLabel(popup, text="Directions to Display:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        frame_directions = ctk.CTkFrame(popup, fg_color="transparent")
        frame_directions.pack(fill="x", padx=15)

        grid_layout = [
            ("NW", 0, 0), ("N", 0, 1), ("NE", 0, 2),
            ("W", 1, 0), ("X", 1, 1), ("L", 1, 2),
            ("SW", 2, 0), ("S", 2, 1), ("SE", 2, 2)
        ]
        direction_vars = {}
        for direcao, row, col in grid_layout:
            var = ctk.IntVar(value=1)
            cb = ctk.CTkCheckBox(frame_directions, text=direcao, variable=var, onvalue=1, offvalue=0)
            cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            direction_vars[direcao] = var

        def gerar_grafico():
            selecionados = [nome for nome, var in agentes_vars.items() if var.get()]
            if not selecionados:
                self.log_message("ERROR: Please select at least one agent.", error=True)
                return
            try:
                start = int(entry_start_frame.get()) if entry_start_frame.get() else 0
                end = int(entry_end_frame.get()) if entry_end_frame.get() else len(self.world.estados) - 1
            except ValueError:
                self.log_message("ERROR: Invalid interval.", error=True)
                return
            titulo = "Movement Pattern Graph"
            agent_indices = [i for i, ag in enumerate(self.world.agentes) if ag.nome in selecionados]
            directions_selected = {k: v.get() for k, v in direction_vars.items()}

            popup.destroy()

            janela_grafico = ctk.CTkToplevel(self)
            janela_grafico.title(titulo)
            janela_grafico.geometry("900x600")
            janela_grafico.grab_set()

            frame = ctk.CTkScrollableFrame(janela_grafico, width=850, height=550)
            frame.pack(padx=20, pady=20, fill="both", expand=True)

            from PIL import ImageTk
            images = GraphVisualizer.show_images(
                self.world,
                agent_filter=lambda idx, ag: idx in agent_indices,
                interval=(start, end),
                title=titulo,
                directions=directions_selected
            )
            labels = [self.world.agentes[idx].nome for idx in agent_indices]

            for img in images:
                photo = ImageTk.PhotoImage(img)
                label = ctk.CTkLabel(frame, image=photo, text="")
                label.image = photo
                label.pack(pady=10)

            def exportar_imagens():
                from tkinter import filedialog
                import os
                import matplotlib.pyplot as plt
                import numpy as np

                pasta = filedialog.askdirectory(title="Select folder to export the image")
                if not pasta:
                    self.log_message("Export cancelled: No folder selected.", error=True)
                    return

                n = len(images)
                fig, axs = plt.subplots(n, 1, figsize=(10, 3 * n))
                if n == 1:
                    axs = [axs]

                for i, idx in enumerate(agent_indices):
                    agente = self.world.agentes[idx]
                    y = np.zeros((end - start + 1, 9), dtype=float)
                    for j in range(start, end + 1):
                        y[j - start] = self.world.estados[j][idx].padrao_movimento
                    y_masked = np.where(y == 0, np.nan, y)
                    x = list(range(start + 1, end + 2))
                    colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#008000', '#9ACD32', '#FFA500', '#FF8C00',
                              '#ADD8E6']
                    labels_dir = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']
                    dir_indices = [k for k, l in enumerate(labels_dir) if directions_selected.get(l, 1)]
                    for dir_idx in dir_indices:
                        axs[i].plot(x, y_masked[:, dir_idx], label=labels_dir[dir_idx],
                                    color=colors[dir_idx % len(colors)], alpha=0.7)
                    axs[i].set_title(agente.nome)
                    axs[i].set_ylim(0, 1.05)
                    axs[i].set_xlim(left=start + 1)
                    axs[i].legend(loc='upper right', fontsize=8)

                fig.tight_layout()
                caminho = os.path.join(pasta, "all_agents_graph.png")
                fig.savefig(caminho)
                plt.close(fig)
                self.log_message("Export completed! The image was saved successfully.")

            ctk.CTkButton(janela_grafico, text="Export Image", command=exportar_imagens).pack(pady=10)

        ctk.CTkButton(popup, text="Generate Graph", command=gerar_grafico).pack(pady=15)

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
        color = "#e74c3c" if error else "white"
        try:
            padding = 30
            current_width = self.frame_logs.winfo_width() - padding
            if current_width < 100: current_width = 300
        except:
            current_width = 300
        label = ctk.CTkLabel(self.frame_logs, text=f"> {message}",
                             text_color=color,
                             font=("Consolas", 10),
                             wraplength=current_width,
                             justify="left")
        label.pack(anchor="w", padx=5, pady=2, fill="x")

if __name__ == "__main__":
    app = TelaAjustavel()
    app.mainloop()