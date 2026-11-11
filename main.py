import os
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from projeto.GraphVisualizer import GraphVisualizer
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import math

from projeto import (
    World, Agent, AgentSpawner, FileHandler, WorldUpdater, TrueRNGSource
)

class TelaAjustavel(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.simulacao_rodando = False
        # NOVO: guarda cada linha de log já exibida, na ordem em que
        # apareceu, para o botão "Download Logs" poder exportar tudo para
        # um .txt (ver log_message/exportar_logs).
        self._log_entries = []
        # NOVO: uma única janela de tooltip, reutilizada (mostrada/escondida
        # com deiconify/withdraw, nunca destruída e recriada) para todas as
        # legendas da interface — ver _adicionar_tooltip/_mostrar_tooltip/
        # _esconder_tooltip. Criada sob demanda, na primeira vez que algum
        # tooltip precisar aparecer.
        self._tooltip_window = None
        self._tooltip_label = None
        self._tooltip_auto_hide_id = None
        # NOVO: controla se a simulação completa (toda a história) já foi
        # calculada para a configuração/agentes atuais. Enquanto for False,
        # estamos na "fase de configuração": adicionar/remover agentes e
        # mudar parâmetros só atualiza o estado inicial (frame 0), sem
        # recalcular a história inteira. Isso só acontece quando o usuário
        # confirma a tela "Edit Configuration".
        self._mundo_construido = False
        self.config = FileHandler.load_config('drima.json')

        # NOVO: se a config salva pedia TrueRNG habilitado, tenta reconectar
        # no dispositivo agora. Se falhar (desconectado, driver ausente, etc.),
        # volta silenciosamente para o gerador pseudo-aleatório padrão e
        # avisa depois, quando a área de logs já existir.
        self._mensagem_inicial_truerng = None
        if self.config.get('usar_truerng', False):
            sucesso, mensagem = TrueRNGSource.set_enabled(True)
            if not sucesso:
                self.config['usar_truerng'] = False
            self._mensagem_inicial_truerng = (mensagem, not sucesso)

        self._inicializar_mundo(primeira_vez=True) # Chama para criar os agentes iniciais

        self.configurar_janela()
        self.criar_frames_principais()
        self.criar_layout_funcional()

        if self._mensagem_inicial_truerng is not None:
            mensagem, era_erro = self._mensagem_inicial_truerng
            self.log_message(mensagem, error=era_erro)

        # NOVO: não calcula mais a história completa automaticamente.
        # O usuário descreve a configuração/agentes desejados primeiro e só
        # então confirma a tela "Edit Configuration" para gerar a simulação.
        self._atualizar_estado_controles_historia()
        self.log_message("Describe the desired world configuration and agents in 'Edit Configuration', then confirm to generate the simulation.")
        self.after(100, lambda: self.atualizar_visualizacao_simulacao(0))

        # NOVO: abre a tela de configuração automaticamente ao iniciar, para
        # o usuário já descrever a configuração inicial desejada de cara.
        self.after(150, self.abrir_janela_editar_configuracao)

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
            self.config['delta_p_deterministico'], self.config['delta_p_aleatorio'],
            delta_p_mode=self.config.get('delta_p_mode', 'Global')
        )
        self.agent_spawner = AgentSpawner(self.world)

        if primeira_vez or not agentes_atuais:
            usar_true_rng = self.config.get('usar_truerng', False)
            for _ in range(5):
                try:
                    if usar_true_rng:
                        self.agent_spawner.spawn_randomly_true_rng()
                    else:
                        self.agent_spawner.spawn_randomly()
                except RuntimeError as e: print(e); break
            self.world.estados = [[ag.clone() for ag in self.world.agentes]]
        else:
            self.world.agentes = agentes_atuais
            self.world.estados = [[ag.clone() for ag in agentes_atuais]]

    def _marcar_mundo_como_nao_construido(self):
        """
        NOVO: marca a simulação atual como desatualizada em relação à
        configuração/agentes descritos. Usado por toda ação de "configuração"
        (adicionar/remover agente, salvar config, alternar TrueRNG) para que
        nenhuma delas recalcule a história sozinha — isso evita o gargalo de
        rodar o mundo inteiro a cada pequena mudança.
        """
        self._mundo_construido = False
        if hasattr(self, 'slider_historia'):
            self.slider_historia.configure(to=0)
            self.slider_historia.set(0)
        self._atualizar_estado_controles_historia()

    def _atualizar_estado_controles_historia(self):
        """Habilita/desabilita os controles que dependem de uma história já calculada."""
        estado = "normal" if self._mundo_construido else "disabled"
        if hasattr(self, 'btn_play_pause'):
            self.btn_play_pause.configure(state=estado)
        if hasattr(self, 'slider_historia'):
            self.slider_historia.configure(state=estado)
            self._atualizar_estado_botao_restart(int(self.slider_historia.get()))

    def _atualizar_estado_botao_restart(self, frame_idx):
        """NOVO: o botão de reiniciar só fica ativo se a história já foi
        construída e o usuário avançou além do frame 0."""
        if not hasattr(self, 'btn_restart'):
            return
        pode_reiniciar = self._mundo_construido and frame_idx > 0
        self.btn_restart.configure(state="normal" if pode_reiniciar else "disabled")

    def _construir_mundo(self):
        """
        NOVO: ponto único que calcula e executa a simulação completa
        (toda a história), a partir da configuração e dos agentes descritos
        até agora. Antes disso, adicionar/remover agentes ou mudar
        parâmetros só atualiza o estado inicial (frame 0).

        NOVO: cronometra (time.perf_counter, só sobe monotonicamente — não
        é afetado por ajustes de relógio do sistema) do início deste
        cálculo até o momento em que a história já está pronta para ser
        animada, e registra o resultado no log com 4 casas decimais.
        """
        self.log_message("Building world: calculating full simulation history...")
        inicio = time.perf_counter()

        self._executar_simulacao_completa()
        self._mundo_construido = True
        self._atualizar_estado_controles_historia()

        duracao = time.perf_counter() - inicio
        self.log_message(f"World built and ready to animate in {duracao:.4f}s.")
        messagebox.showinfo("Configuration loaded",
                            f"The configuration was loaded successfully in {duracao:.4f}s.",
                            parent=self)

    def _executar_simulacao_completa(self):
        """Executa a simulação inteira em segundo plano para gerar a história."""
        self.world.agentes = [ag.clone() for ag in self.world.estados[0]]
        
        modo_sincrono = self.config["modo_da_interacao"] == 0
        iteracoes = self.config["numero_de_iteracoes"]

        temp_world = World(
            self.world.largura, self.world.altura, 
            self.world.delta_p_det, self.world.delta_p_rand,
            delta_p_mode=self.world.delta_p_mode
        )
        temp_world.agentes = [ag.clone() for ag in self.world.estados[0]]
        
        num_agentes = len(temp_world.agentes) or 1
        async_iters = 1
        
        if not modo_sincrono:
            try:
                async_iters = int(self.config.get('async_sub_iterations', 1))
            except ValueError:
                async_iters = 1
            
            if async_iters > num_agentes: async_iters = num_agentes
            if async_iters < 1: async_iters = 1

        self.world.estados = [[ag.clone() for ag in temp_world.agentes]]

        # NOVO: escolhe entre a atualização pseudo-aleatória original e a
        # versão que usa o TrueRNG (hardware), conforme o botão da interface.
        usar_true_rng = self.config.get('usar_truerng', False)

        for i in range(iteracoes):
            if modo_sincrono:
                if usar_true_rng:
                    WorldUpdater.update_synchronously_true_rng(temp_world)
                else:
                    WorldUpdater.update_synchronously(temp_world)
            else:
                if usar_true_rng:
                    WorldUpdater.update_asynchronously_true_rng(temp_world, iterations=async_iters)
                else:
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
        # NOVO: o painel lateral de opções foi removido — a área de
        # simulação (quadriculado, gráfico, logs e configuração) agora
        # ocupa a tela inteira.
        self.frame_funcional = ctk.CTkFrame(self, fg_color="#2e3b4e")
        self.frame_funcional.place(relx=0, rely=0, relwidth=1, relheight=1)

    def criar_layout_funcional(self):
        # ... (sem alterações)
        container_pequenos = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.25)

        frame_grafico = ctk.CTkFrame(container_pequenos, fg_color="#3e4b5e")
        frame_grafico.pack(side="left", expand=True, fill="both", padx=(0, 5))
        ctk.CTkButton(frame_grafico, text="Show Agent Graph", command=self.abrir_janela_grafico).pack(expand=True,padx=10, pady=5)

        frame_logs_externo = ctk.CTkFrame(container_pequenos, fg_color="#4e5b6e")
        frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))

        frame_logs_topo = ctk.CTkFrame(frame_logs_externo, fg_color="transparent")
        frame_logs_topo.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame_logs_topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left")
        # NOVO: exporta todas as linhas de log já geradas para um .txt.
        ctk.CTkButton(frame_logs_topo, text="Download Logs", width=110, height=22,
                      font=("Arial", 11), command=self.exportar_logs).pack(side="right")
        ctk.CTkButton(frame_logs_topo, text="Clear Logs", width=90, height=22,
                      font=("Arial", 11), fg_color="#e74c3c", hover_color="#b93222",
                      command=self.limpar_logs).pack(side="right", padx=(0, 5))

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

    def criar_frame_configuracao(self, parent):
        """
        NOVO: painel de configuração rápida, ao lado do quadriculado —
        reúne os controles que antes viviam no painel lateral removido
        (Load World, Export World e o botão que abre 'Edit Configuration';
        o switch do TrueRNG se mudou para dentro de 'Edit Configuration',
        onde faz mais sentido estar junto do restante das configurações
        do mundo).

        Colapsável e dimensionado pelo próprio conteúdo: não usa
        expand/fill="both" (o que o deixaria do tamanho da seção vizinha),
        então sua largura acompanha apenas a largura dos botões. Começa
        escondido — só aparece ao clicar no ícone de mundo (🌍), nos
        controles de história.
        """
        btn_font = ("Arial", 11)
        btn_height = 24
        largura_botoes = 160

        self.frame_config_rapida = ctk.CTkFrame(parent, fg_color="#23272e")
        # NOVO: não empacota aqui — o painel começa colapsado/escondido.
        self._painel_configuracao_visivel = False

        ctk.CTkLabel(self.frame_config_rapida, text="Configuration", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkButton(self.frame_config_rapida, text="Edit Configuration", command=self.abrir_janela_editar_configuracao,
                      font=btn_font, height=btn_height, width=largura_botoes,
                      fg_color="#2980b9", hover_color="#1f618d"
                      ).pack(padx=10, pady=2)

        ctk.CTkButton(self.frame_config_rapida, text="Load World", height=btn_height, font=btn_font, width=largura_botoes,
                      command=self.carregar_mundo_de_arquivo).pack(padx=10, pady=2)

        ctk.CTkButton(self.frame_config_rapida, text="Export World", height=btn_height, font=btn_font, width=largura_botoes,
                      command=self.salvar_mundo_em_arquivo).pack(padx=10, pady=(2, 10))

    def _adicionar_tooltip(self, widget, texto):
        """
        NOVO: registra a legenda de 'widget'. A exibição em si usa UMA ÚNICA
        janela de tooltip compartilhada por toda a interface (ver
        _mostrar_tooltip/_esconder_tooltip) — nunca criamos uma nova
        CTkToplevel por hover, só reposicionamos/mostramos ou escondemos a
        mesma janela. Isso evita de vez o bug de legendas presas/duplicadas
        na tela: como só existe UMA janela possível, não há como duas
        ficarem visíveis ao mesmo tempo, e cliques no próprio widget (que
        antes podiam atrapalhar o bind de "<Leave>", como no botão de
        play/pause) não têm nenhum efeito sobre ela.
        """
        widget.bind("<Enter>", lambda event: self._mostrar_tooltip(widget, texto), add="+")
        widget.bind("<Leave>", lambda event: self._esconder_tooltip(), add="+")

    def _mostrar_tooltip(self, widget, texto):
        """Mostra (ou reposiciona) a janela de tooltip compartilhada, por até 2 segundos."""
        if self._tooltip_window is None:
            self._tooltip_window = ctk.CTkToplevel(self)
            self._tooltip_window.overrideredirect(True)
            self._tooltip_window.attributes("-topmost", True)
            self._tooltip_label = ctk.CTkLabel(self._tooltip_window, text="", fg_color="#1e2227",
                                               text_color="white", corner_radius=4, font=("Arial", 10))
            self._tooltip_label.pack(padx=6, pady=3)
            self._tooltip_window.withdraw()

        if self._tooltip_auto_hide_id is not None:
            try:
                self.after_cancel(self._tooltip_auto_hide_id)
            except Exception:
                pass
            self._tooltip_auto_hide_id = None

        try:
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height() + 4
        except Exception:
            return

        self._tooltip_label.configure(text=texto)
        self._tooltip_window.geometry(f"+{x}+{y}")
        self._tooltip_window.deiconify()
        self._tooltip_window.lift()
        # Some sozinha depois de 2s, independente do "<Leave>" disparar.
        self._tooltip_auto_hide_id = self.after(2000, self._esconder_tooltip)

    def _esconder_tooltip(self):
        """Esconde a janela de tooltip compartilhada (sem destruí-la — é reutilizada depois)."""
        if self._tooltip_auto_hide_id is not None:
            try:
                self.after_cancel(self._tooltip_auto_hide_id)
            except Exception:
                pass
            self._tooltip_auto_hide_id = None
        if self._tooltip_window is not None:
            try:
                self._tooltip_window.withdraw()
            except Exception:
                pass

    def _notificar_estado_truerng(self, sucesso, mensagem, parent=None):
        """
        NOVO: sempre que o TrueRNG é conectado ou desconectado, mostra um
        popup com o resultado, para o usuário saber o estado do dispositivo
        (em vez de depender só da linha no log).
        """
        if sucesso:
            messagebox.showinfo("TrueRNG", mensagem, parent=parent)
        else:
            messagebox.showerror("TrueRNG", mensagem, parent=parent)

    def _alternar_painel_configuracao(self):
        """NOVO: colapsa/expande o painel de configuração, ao lado do quadriculado."""
        if self._painel_configuracao_visivel:
            self.frame_config_rapida.pack_forget()
            self._painel_configuracao_visivel = False
        else:
            # Sem fill/expand: o tamanho do painel acompanha só o próprio
            # conteúdo (os botões), em vez de esticar verticalmente para
            # preencher a altura do quadriculado.
            self.frame_config_rapida.pack(side="top", anchor="n", pady=(8, 0))
            self._painel_configuracao_visivel = True

    def criar_frame_simulacao(self):
        # ... (sem alterações)
        self.frame_simulacao = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        self.frame_simulacao.place(relx=0.02, rely=0.30, relwidth=0.96, relheight=0.68)

        # NOVO: o canvas ocupa a linha toda; o ícone de mundo (🌍) e o
        # painel de configuração ficam sobrepostos (via place) no canto
        # superior direito do próprio canvas — assim ficam colados ao
        # quadriculado, em vez de "longe" dele numa coluna separada que só
        # empurrava para a borda da janela (o plot é quadrado e centralizado
        # dentro de uma área bem mais larga).
        frame_canvas = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        frame_canvas.pack(side="top", fill="both", expand=True)

        self.figura_sim = Figure(dpi=100, facecolor="#2e3b4e")
        self.ax_sim = self.figura_sim.add_subplot(111)
        self.figura_sim.tight_layout()

        self.canvas_sim = FigureCanvasTkAgg(self.figura_sim, master=frame_canvas)
        self.canvas_sim.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)

        coluna_lado_grid = ctk.CTkFrame(frame_canvas, fg_color="transparent")
        coluna_lado_grid.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

        self.btn_toggle_config = ctk.CTkButton(coluna_lado_grid, text="🌍", width=36, height=28,
                                               font=("Arial", 14), command=self._alternar_painel_configuracao)
        self.btn_toggle_config.pack(side="top", anchor="n")
        self._adicionar_tooltip(self.btn_toggle_config, "Configuration")

        self.criar_frame_configuracao(coluna_lado_grid)

        frame_controles_historia = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        frame_controles_historia.pack(fill="x", padx=5, pady=5)

        # NOVO: ícones de Play/Pause e Restart, abaixo do quadriculado.
        # Começam desabilitados: só habilitam depois que o mundo for
        # construído (ao confirmar 'Edit Configuration' ou carregar um
        # mundo salvo com história).
        self.btn_play_pause = ctk.CTkButton(frame_controles_historia, text="▶", width=36, height=28,
                                            font=("Arial", 14, "bold"), fg_color="#27ae60", hover_color="#219150",
                                            command=self.alternar_animacao, state="disabled")
        self.btn_play_pause.pack(side="left", padx=(0, 4))
        self._adicionar_tooltip(self.btn_play_pause, "Play / pause the history animation")

        self.btn_restart = ctk.CTkButton(frame_controles_historia, text="⏮", width=36, height=28,
                                         font=("Arial", 14, "bold"), command=self._reiniciar_historia,
                                         state="disabled")
        self.btn_restart.pack(side="left", padx=(0, 10))
        self._adicionar_tooltip(self.btn_restart, "Restart to the beginning (frame 0)")

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

    def abrir_janela_adicionar_agente(self, world_alvo=None, spawner_alvo=None, callback_sucesso=None):
        """
        Abre o painel de criação de um novo agente.

        NOVO: aceita opcionalmente um 'world_alvo'/'spawner_alvo' (usados
        por 'Edit Configuration' para adicionar a um rascunho, sem tocar no
        mundo real) e um 'callback_sucesso' chamado com o agente criado no
        lugar do comportamento antigo de aplicar direto em self.world.
        """
        if world_alvo is None:
            world_alvo = self.world
        if spawner_alvo is None:
            spawner_alvo = self.agent_spawner

        popup = ctk.CTkToplevel(self)
        popup.title("Add New Agent")
        popup.geometry("400x600")
        popup.grab_set()

        frame_topo = ctk.CTkFrame(popup, fg_color="transparent")
        frame_topo.pack(fill="x", padx=15, pady=10)

        top_row_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        top_row_frame.pack(fill="x")

        tipo_frame = ctk.CTkFrame(top_row_frame, fg_color="transparent")
        tipo_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(tipo_frame, text="Agent Type", font=("Arial", 12, "bold")).pack()
        tipo_var = ctk.StringVar(value="R")
        ctk.CTkRadioButton(tipo_frame, text="Random (R)", variable=tipo_var, value="R",
                           command=lambda: atualizar_modo()).pack(anchor="w", padx=10)
        ctk.CTkRadioButton(tipo_frame, text="Deterministic (D)", variable=tipo_var, value="D",
                           command=lambda: atualizar_modo()).pack(anchor="w", padx=10)

        pos_frame = ctk.CTkFrame(top_row_frame, fg_color="transparent")
        pos_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(pos_frame, text="Position (X, Y)", font=("Arial", 12, "bold")).pack()
        pos_entries_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        pos_entries_frame.pack(pady=5)
        entry_x = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="X")
        entry_x.pack(side="left", padx=5)
        entry_y = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="Y")
        entry_y.pack(side="left", padx=5)
        ctk.CTkLabel(pos_frame, text="(Optional)", font=("Arial", 9)).pack()

        delta_p_frame = ctk.CTkFrame(frame_topo, fg_color="transparent")
        delta_p_frame.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(delta_p_frame, text="Influence (Δp)", font=("Arial", 12, "bold")).pack()
        entry_delta_p = ctk.CTkEntry(delta_p_frame, width=100, placeholder_text="e.g., 0.1 (Optional)")
        entry_delta_p.pack(pady=5)

        # Área que muda conforme o tipo: R -> probabilidades por direção (ou
        # uniforme, escondendo a grade); D -> escolha de uma única direção.
        acoes_area = ctk.CTkFrame(popup, fg_color="transparent")
        acoes_area.pack(fill="x")

        label_acoes = ctk.CTkLabel(acoes_area, text="Actions by Direction", font=("Arial", 12, "bold"))
        uniform_var = ctk.BooleanVar(value=True)
        uniform_cb = ctk.CTkCheckBox(
            acoes_area,
            text="Uniform probabilities (all directions equal)",
            variable=uniform_var,
            command=lambda: atualizar_modo()
        )
        direcoes_frame = ctk.CTkFrame(acoes_area, fg_color="transparent")
        det_frame = ctk.CTkFrame(acoes_area, fg_color="transparent")

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

        # Agente determinístico: uma única direção marcada.
        det_var = ctk.StringVar(value="N")
        det_radios = {}
        for direcao, row, col in grid_layout:
            rb = ctk.CTkRadioButton(det_frame, text=direcao, variable=det_var, value=direcao, width=60)
            rb.grid(row=row, column=col, padx=12, pady=8, sticky="w")
            det_radios[direcao] = rb

        def atualizar_modo():
            for w in (label_acoes, uniform_cb, direcoes_frame, det_frame, toggle_x_cb):
                w.pack_forget()
            if tipo_var.get() == "R":
                label_acoes.configure(text="Actions by Direction")
                label_acoes.pack(pady=(15, 5))
                uniform_cb.pack(pady=(0, 5))
                if not uniform_var.get():
                    direcoes_frame.pack(pady=5)
                toggle_x_cb.pack(pady=(5, 10))
            else:
                label_acoes.configure(text="Direction")
                label_acoes.pack(pady=(15, 5))
                det_frame.pack(pady=5)

        def atualizar_campos_x():
            if not toggle_x_var.get():
                direction_entries["X"].configure(state="normal")
                direction_entries["X"].delete(0, "end")
                direction_entries["X"].insert(0, "0.0000")
                direction_entries["X"].configure(state="disabled")
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

        toggle_x_var = ctk.BooleanVar(value=True)

        # Só faz sentido para agentes R; fica dentro de acoes_area para
        # manter a ordem de empacotamento ao esconder/mostrar.
        toggle_x_cb = ctk.CTkCheckBox(
            acoes_area,
            text="Allow movement in X (stay in place)",
            variable=toggle_x_var,
            command=atualizar_campos_x
        )

        atualizar_campos_x()
        atualizar_modo()

        def _criar_agente_final(padrao_ui, tipo, pos, delta_p_val):
            padrao_movimento = [
                padrao_ui['E'], padrao_ui['NE'], padrao_ui['N'], padrao_ui['NW'],
                padrao_ui['W'], padrao_ui['SW'], padrao_ui['S'], padrao_ui['SE'],
                padrao_ui['X']
            ]
            if self.config.get('usar_truerng', False):
                novo_agente = spawner_alvo.spawn_randomly_true_rng(
                    type=tipo, position=pos, moving_pattern=padrao_movimento, delta_p=delta_p_val
                )
            else:
                novo_agente = spawner_alvo.spawn_randomly(
                    type=tipo, position=pos, moving_pattern=padrao_movimento, delta_p=delta_p_val
                )

            if callback_sucesso is not None:
                callback_sucesso(novo_agente)
            else:
                world_alvo.estados[0].append(novo_agente.clone())
                self.log_message(f"Agent '{novo_agente.nome}' added. Open 'Edit Configuration' and confirm to apply.")
                self._marcar_mundo_como_nao_construido()
                self.atualizar_visualizacao_simulacao(0)
            popup.destroy()

        def adicionar():
            try:
                tipo = tipo_var.get()
                pos = None
                if entry_x.get() and entry_y.get():
                    pos = (int(entry_x.get()), int(entry_y.get()))

                delta_p_str = entry_delta_p.get().strip()
                delta_p_val = None
                if delta_p_str:
                    delta_p_val = float(delta_p_str)

                if tipo == 'D':
                    grid_values = {d: (1.0 if d == det_var.get() else 0.0) for d in direction_entries}
                elif uniform_var.get():
                    n_dirs = 9 if toggle_x_var.get() else 8
                    grid_values = {d: (0.0 if d == "X" and not toggle_x_var.get() else 1.0 / n_dirs)
                                   for d in direction_entries}
                else:
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

                if math.isclose(soma, 1.0, rel_tol=TOLERANCE):
                    _criar_agente_final(grid_values, tipo, pos, delta_p_val)
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
                        _criar_agente_final(normalized_values, tipo, pos, delta_p_val)

                    ctk.CTkButton(btn_frame, text="Yes, Normalize", command=sim_normalizar).pack(side="left", padx=10)
                    ctk.CTkButton(btn_frame, text="No, Fix Manually", command=confirm_popup.destroy).pack(side="left",
                                                                                                        padx=10)

            except ValueError:
                messagebox.showerror("Error", "Position, delta_p, and movement values must be valid numbers.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add agent:\n{e}", parent=popup)

        botoes_frame = ctk.CTkFrame(popup, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=15, pady=20)
        ctk.CTkButton(botoes_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)
        ctk.CTkButton(botoes_frame, text="Add", command=adicionar).pack(side="right", padx=5)

    def abrir_janela_editar_configuracao(self):
        """
        NOVO: tela única de edição. Reúne a configuração do mundo (grid,
        delta_p, modo de interação/iterações — antigo "World Settings") e a
        configuração inicial dos agentes (adicionar, remover um específico,
        remover todos, desfazer), já que no final tudo é aplicado junto.
        Por isso não existe mais um botão "Save and Apply Config" separado:
        ele virou o passo de confirmação ("Done" -> "Yes, Apply") daqui.

        Tudo acontece sobre um rascunho isolado; nada é aplicado ao mundo
        real até essa confirmação final. Se o usuário responder "não", o
        rascunho é descartado e o mundo atual permanece intacto; se
        responder "sim", a config e o estado inicial são substituídos pelo
        rascunho e a simulação completa é construída.
        """
        # Rascunho isolado: um World/AgentSpawner próprios só para esta edição,
        # para que find_free_spot/geração de nomes funcionem normalmente sem
        # tocar em self.world.
        draft_world = World(
            self.world.largura, self.world.altura,
            self.world.delta_p_det, self.world.delta_p_rand,
            delta_p_mode=self.world.delta_p_mode
        )
        draft_world.agentes = [ag.clone() for ag in self.world.estados[0]]
        draft_spawner = AgentSpawner(draft_world)

        # NOVO: pilha de desfazer — um snapshot dos agentes do rascunho é
        # guardado antes de cada mutação (adicionar, remover um, remover
        # todos), para que "Undo Last Change" possa restaurá-lo.
        historico_desfazer = []

        popup = ctk.CTkToplevel(self)
        popup.title("Edit Configuration")
        # NOVO: altura maior — a janela anterior (640) cortava os botões de
        # baixo (Undo/Remove/Add/Done/Cancel) em telas menores.
        popup.geometry("900x760")
        popup.minsize(860, 700)
        popup.grab_set()

        # NOVO: layout em duas colunas — à esquerda o quadriculado com as
        # ações de agentes, à direita a configuração do mundo.
        conteudo = ctk.CTkFrame(popup, fg_color="transparent")
        conteudo.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        coluna_agentes = ctk.CTkFrame(conteudo, fg_color="transparent")
        coluna_agentes.pack(side="left", fill="both", expand=True, padx=(0, 10))

        coluna_mundo = ctk.CTkFrame(conteudo, fg_color="transparent", width=260)
        coluna_mundo.pack(side="right", fill="y")
        coluna_mundo.pack_propagate(False)

        # ------------------------------------------------------------
        # --- World Settings (agora faz parte desta mesma tela) ---
        # ------------------------------------------------------------
        frame_config = ctk.CTkFrame(coluna_mundo, fg_color="#23272e")
        frame_config.pack(fill="both", expand=True)

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

        def criar_campo_config(parent, text, initial_value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            ctk.CTkLabel(frame, text=text, font=("Arial", 11)).pack(side="left")
            entry = ctk.CTkEntry(frame, width=120)
            entry.insert(0, str(initial_value))
            entry.pack(side="right")
            return entry, frame

        frame_dp_mode = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_dp_mode.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(frame_dp_mode, text="Delta-P Mode", font=("Arial", 11)).pack(side="left")
        default_dp_mode = self.config.get('delta_p_mode', 'Global')

        def alternar_visibilidade_delta_p(choice):
            frame_d_container.pack_forget()
            frame_r_container.pack_forget()
            if choice == "Global":
                frame_r_container.pack(fill="x", pady=5, padx=10, before=frame_largura)
                frame_d_container.pack(fill="x", pady=5, padx=10, before=frame_r_container)

        combo_dp_mode = ctk.CTkComboBox(frame_dp_mode, values=["Global", "Local"], width=120,
                                         command=alternar_visibilidade_delta_p)
        combo_dp_mode.set(default_dp_mode)
        combo_dp_mode.pack(side="right")

        slider_d, entry_d, frame_d_container = criar_slider_com_entry(
            frame_config, "delta_p_D", self.config['delta_p_deterministico'])

        slider_r, entry_r, frame_r_container = criar_slider_com_entry(
            frame_config, "delta_p_R", self.config['delta_p_aleatorio'])

        entry_largura, frame_largura = criar_campo_config(
            frame_config, "Grid Width", self.config['largura_da_grade'])
        frame_largura.pack(fill="x", padx=10, pady=4)

        entry_altura, frame_altura = criar_campo_config(
            frame_config, "Grid Height", self.config['altura_da_grade'])
        frame_altura.pack(fill="x", padx=10, pady=4)

        entry_iteracoes, frame_iteracoes = criar_campo_config(
            frame_config, "No. of Iterations", self.config['numero_de_iteracoes'])
        frame_iteracoes.pack(fill="x", padx=10, pady=4)

        mode_frame = ctk.CTkFrame(frame_config, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkLabel(mode_frame, text="Interaction Mode", font=("Arial", 11)).pack(side="left")

        default_async_iters = self.config.get('async_sub_iterations', 1)
        entry_async_iter = ctk.CTkEntry(mode_frame, width=50)
        entry_async_iter.insert(0, str(default_async_iters))

        def alternar_entry_async(choice):
            entry_async_iter.pack_forget()
            combo_modo.pack_forget()
            if choice == "Asynchronous":
                entry_async_iter.pack(side="right", padx=(5, 0))
                combo_modo.pack(side="right")
            else:
                combo_modo.pack(side="right")

        combo_modo = ctk.CTkComboBox(mode_frame, values=["Synchronous", "Asynchronous"], width=120,
                                      command=alternar_entry_async)

        initial_mode = "Synchronous" if self.config['modo_da_interacao'] == 0 else "Asynchronous"
        combo_modo.set(initial_mode)
        alternar_entry_async(initial_mode)

        alternar_visibilidade_delta_p(combo_dp_mode.get())

        # NOVO: o switch do TrueRNG agora vive aqui, junto do resto da
        # configuração do mundo. Conectar/desconectar o dispositivo é uma
        # ação de hardware imediata (não faz sentido ficar "em rascunho"),
        # então ela já aplica e salva na hora — mas um popup avisa o
        # usuário do resultado (sucesso ou falha) a cada troca.
        frame_truerng = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_truerng.pack(fill="x", padx=10, pady=(0, 10))

        var_true_rng = ctk.BooleanVar(value=self.config.get('usar_truerng', False))

        def alternar_true_rng_rascunho():
            querendo_ligar = var_true_rng.get()
            sucesso, mensagem = TrueRNGSource.set_enabled(querendo_ligar)

            if querendo_ligar and not sucesso:
                # Não conseguiu conectar no dispositivo: mantém desligado e avisa.
                var_true_rng.set(False)

            self.config['usar_truerng'] = TrueRNGSource.is_enabled()
            FileHandler.save_config(self.config, 'drima.json')
            self.log_message(mensagem, error=not sucesso)
            self._notificar_estado_truerng(sucesso, mensagem, parent=popup)

        ctk.CTkSwitch(frame_truerng, text="Use TrueRNG Hardware", variable=var_true_rng,
                      onvalue=True, offvalue=False, command=alternar_true_rng_rascunho).pack(anchor="w")

        # ------------------------------------------------------------
        # --- Initial Agent Configuration (preview + desfazer) ---
        # ------------------------------------------------------------
        ctk.CTkLabel(coluna_agentes, text="Initial Agent Configuration", font=("Arial", 13, "bold")).pack(pady=(0, 5))

        frame_preview = ctk.CTkFrame(coluna_agentes, fg_color="#2e3b4e")
        frame_preview.pack(fill="both", expand=True, pady=(0, 10))

        figura_preview = Figure(dpi=100, facecolor="#2e3b4e")
        ax_preview = figura_preview.add_subplot(111)
        canvas_preview = FigureCanvasTkAgg(figura_preview, master=frame_preview)
        canvas_preview.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        def redesenhar_preview():
            ax_preview.clear()
            self._desenhar_grid_agentes(ax_preview, draft_world.largura, draft_world.altura, draft_world.agentes)
            canvas_preview.draw()

        def atualizar_estado_undo():
            btn_undo.configure(state="normal" if historico_desfazer else "disabled")

        def salvar_checkpoint():
            """Guarda o estado atual do rascunho antes de uma mutação, para o Undo."""
            historico_desfazer.append([ag.clone() for ag in draft_world.agentes])
            atualizar_estado_undo()

        def desfazer():
            if not historico_desfazer:
                return
            draft_world.agentes = historico_desfazer.pop()
            self.log_message("[Edit Configuration] Last change undone.")
            atualizar_combo()
            redesenhar_preview()
            atualizar_estado_undo()

        frame_undo = ctk.CTkFrame(coluna_agentes, fg_color="transparent")
        frame_undo.pack(fill="x", pady=(0, 5))
        btn_undo = ctk.CTkButton(frame_undo, text="Undo Last Change", state="disabled", command=desfazer)
        btn_undo.pack(fill="x")

        # --- Remover um agente específico (combobox com os existentes no rascunho) ---
        frame_remover = ctk.CTkFrame(coluna_agentes, fg_color="transparent")
        frame_remover.pack(fill="x", pady=5)

        combo_agente = ctk.CTkComboBox(frame_remover, values=[])
        combo_agente.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def atualizar_combo():
            nomes = [a.nome for a in draft_world.agentes]
            combo_agente.configure(values=nomes)
            combo_agente.set(nomes[0] if nomes else "")

        def remover_selecionado():
            nome = combo_agente.get()
            if not nome:
                self.log_message("ERROR: No agent selected to remove.", error=True)
                return
            agente_obj = draft_world.encontrar_agente_obj(nome)
            if agente_obj:
                salvar_checkpoint()
                draft_world.agentes.remove(agente_obj)
                self.log_message(f"[Edit Configuration] Agent '{nome}' removed from draft.")
                atualizar_combo()
                redesenhar_preview()

        ctk.CTkButton(frame_remover, text="Remove Selected", width=130,
                      command=remover_selecionado).pack(side="left")

        # --- Remover todos / Adicionar agente ---
        frame_acoes = ctk.CTkFrame(coluna_agentes, fg_color="transparent")
        frame_acoes.pack(fill="x", pady=(0, 10))

        def remover_todos():
            if not draft_world.agentes:
                self.log_message("[Edit Configuration] There are no agents to remove.")
                return
            salvar_checkpoint()
            draft_world.agentes = []
            self.log_message("[Edit Configuration] All agents removed from draft.")
            atualizar_combo()
            redesenhar_preview()

        ctk.CTkButton(frame_acoes, text="Remove All Agents", fg_color="#e74c3c", hover_color="#b93222",
                      command=remover_todos).pack(side="left", fill="x", expand=True, padx=(0, 5))

        def agente_adicionado(novo_agente):
            self.log_message(f"[Edit Configuration] Agent '{novo_agente.nome}' added to draft.")
            atualizar_combo()
            redesenhar_preview()

        def abrir_adicionar():
            salvar_checkpoint()
            self.abrir_janela_adicionar_agente(
                world_alvo=draft_world, spawner_alvo=draft_spawner, callback_sucesso=agente_adicionado
            )

        ctk.CTkButton(frame_acoes, text="Add Agent",
                      command=abrir_adicionar).pack(side="left", fill="x", expand=True, padx=(5, 0))

        # --- Adicionar vários agentes Random de uma vez (posição e padrão aleatórios) ---
        def adicionar_varios():
            dlg = ctk.CTkToplevel(popup)
            dlg.title("Add Multiple Agents")
            dlg.geometry("320x220")
            dlg.grab_set()

            ctk.CTkLabel(dlg, text="Positions and patterns are drawn randomly.\n"
                                   "Deterministic agents get a random direction (including X).",
                         font=("Arial", 11), wraplength=290).pack(pady=(15, 10))

            linhas = ctk.CTkFrame(dlg, fg_color="transparent")
            linhas.pack(pady=5)
            ctk.CTkLabel(linhas, text="Random (R):", width=110, anchor="w").grid(row=0, column=0, pady=4)
            entry_qtd_r = ctk.CTkEntry(linhas, width=70, justify="center")
            entry_qtd_r.insert(0, "0")
            entry_qtd_r.grid(row=0, column=1, pady=4)
            ctk.CTkLabel(linhas, text="Deterministic (D):", width=110, anchor="w").grid(row=1, column=0, pady=4)
            entry_qtd_d = ctk.CTkEntry(linhas, width=70, justify="center")
            entry_qtd_d.insert(0, "0")
            entry_qtd_d.grid(row=1, column=1, pady=4)

            def confirmar():
                try:
                    qtd_r = int(entry_qtd_r.get().strip() or 0)
                    qtd_d = int(entry_qtd_d.get().strip() or 0)
                    if qtd_r < 0 or qtd_d < 0 or qtd_r + qtd_d == 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Enter non-negative integers (at least one above zero).",
                                         parent=dlg)
                    return

                total = qtd_r + qtd_d
                livres = draft_world.largura * draft_world.altura - len(draft_world.agentes)
                if total > livres:
                    messagebox.showerror("Error",
                                         f"Not enough free cells: {livres} available, {total} requested.",
                                         parent=dlg)
                    return

                salvar_checkpoint()
                usar_true_rng = self.config.get('usar_truerng', False)
                spawn = draft_spawner.spawn_randomly_true_rng if usar_true_rng else draft_spawner.spawn_randomly
                for _ in range(qtd_r):
                    spawn(type='R')
                for _ in range(qtd_d):
                    spawn(type='D')
                self.log_message(
                    f"[Edit Configuration] {qtd_r} R and {qtd_d} D random agents added to draft.")
                atualizar_combo()
                redesenhar_preview()
                dlg.destroy()

            botoes = ctk.CTkFrame(dlg, fg_color="transparent")
            botoes.pack(pady=15)
            ctk.CTkButton(botoes, text="Add", width=90, command=confirmar).pack(side="left", padx=5)
            ctk.CTkButton(botoes, text="Cancel", width=90, command=dlg.destroy).pack(side="left", padx=5)

        frame_varios = ctk.CTkFrame(coluna_agentes, fg_color="transparent")
        frame_varios.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(frame_varios, text="Add Multiple Agents",
                      command=adicionar_varios).pack(fill="x")

        # ------------------------------------------------------------
        # --- Confirmação final: valida, salva config, aplica o rascunho e constrói o mundo ---
        # ------------------------------------------------------------
        def validar_novo_config():
            try:
                novo_config = dict(self.config)
                novo_config['largura_da_grade'] = int(entry_largura.get())
                novo_config['altura_da_grade'] = int(entry_altura.get())
                novo_config['numero_de_iteracoes'] = int(entry_iteracoes.get())
                novo_config['delta_p_deterministico'] = float(entry_d.get())
                novo_config['delta_p_aleatorio'] = float(entry_r.get())
                novo_config['modo_da_interacao'] = 0 if combo_modo.get() == "Synchronous" else int(entry_async_iter.get())
                novo_config['async_sub_iterations'] = int(entry_async_iter.get())
                novo_config['delta_p_mode'] = combo_dp_mode.get()
                return novo_config
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid value. Please check all fields.\nDetail: {e}",
                                      parent=popup)
                return None
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while reading settings:\n{e}", parent=popup)
                return None

        def pedir_confirmacao():
            # Valida antes de perguntar: se algo estiver errado, a tela de
            # edição continua aberta para o usuário corrigir.
            novo_config = validar_novo_config()
            if novo_config is None:
                return

            confirm_popup = ctk.CTkToplevel(popup)
            confirm_popup.title("Confirm Changes")
            confirm_popup.geometry("380x160")
            confirm_popup.grab_set()

            msg = (f"Apply these changes to the world configuration?\n"
                   f"The world will start with {len(draft_world.agentes)} agent(s).\n"
                   f"Confirming will save the config and build/run the simulation.")
            ctk.CTkLabel(confirm_popup, text=msg, wraplength=350).pack(pady=15, padx=10)

            btn_frame = ctk.CTkFrame(confirm_popup, fg_color="transparent")
            btn_frame.pack(pady=10)

            def confirmar_sim():
                confirm_popup.destroy()
                popup.destroy()

                self.config = novo_config
                FileHandler.save_config(self.config, 'drima.json')

                self.world = World(
                    self.config['largura_da_grade'], self.config['altura_da_grade'],
                    self.config['delta_p_deterministico'], self.config['delta_p_aleatorio'],
                    delta_p_mode=self.config.get('delta_p_mode', 'Global')
                )
                self.agent_spawner = AgentSpawner(self.world)
                self.world.agentes = [ag.clone() for ag in draft_world.agentes]
                self.world.estados = [[ag.clone() for ag in draft_world.agentes]]

                self.log_message(
                    f"Configuration applied with {len(self.world.agentes)} agent(s). Building world...")
                self._construir_mundo()

            def confirmar_nao():
                confirm_popup.destroy()
                popup.destroy()
                self.log_message("Configuration changes discarded.")

            ctk.CTkButton(btn_frame, text="Yes, Apply", command=confirmar_sim).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No, Discard", command=confirmar_nao).pack(side="left", padx=10)

        frame_fim = ctk.CTkFrame(popup, fg_color="transparent")
        frame_fim.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(frame_fim, text="Cancel",
                      command=lambda: (popup.destroy(),
                                        self.log_message("Configuration changes discarded."))
                      ).pack(side="right", padx=5)
        ctk.CTkButton(frame_fim, text="Done", fg_color="#2980b9", hover_color="#1f618d",
                      command=pedir_confirmacao).pack(side="right", padx=5)

        atualizar_combo()
        redesenhar_preview()

    def alternar_animacao(self):
        # NOVO: o botão agora é um ícone de play/pause (antes era "Animate
        # History"/"Stop Animation" no painel lateral removido).
        if not self._mundo_construido:
            self.log_message("ERROR: Build the world first (open 'Edit Configuration' and confirm).", error=True)
            return

        if not self.simulacao_rodando:
            self.simulacao_rodando = True
            self.btn_play_pause.configure(text="⏸", fg_color="#e74c3c", hover_color="#b93222")
            self.animar_passo()
        else:
            self.simulacao_rodando = False
            self.btn_play_pause.configure(text="▶", fg_color="#27ae60", hover_color="#219150")

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

    def _reiniciar_historia(self):
        """NOVO: volta a visualização para o frame 0 (início) da história."""
        if self.simulacao_rodando:
            self.alternar_animacao()  # para a animação, se estiver rodando
        self.slider_historia.set(0)
        self.atualizar_visualizacao_simulacao(0)

    def carregar_mundo_de_arquivo(self):
        path = filedialog.askopenfilename(defaultextension=".gz", filetypes=[("JSON, Gzip files", "*.json *.gz"),
                                                                            ("Gzip files", "*.gz"),
                                                                            ("All files", "*.*")])
        if not path: return
        try:
            root, ext = os.path.splitext(path)
            data = None 
            
            if ext == '.json':
                with open(path, 'r') as f:
                    data = json.load(f)
                self.config = data["config"]
            elif ext == '.gz':
                data = FileHandler.load_world_json_gzipped(path)
                self.config = data["config"]
            else:
                self.log_message(f"ERROR: Unsupported file format: {ext}", error=True)
                return

            FileHandler.save_config(self.config, 'drima.json')
            
            self._inicializar_mundo(primeira_vez=False) 

            self.world.estados = []
            for frame_data in data["states"]:
                estado = [Agent(
                    a["nome"], 
                    a["tipo"], 
                    a["padrao_movimento"], 
                    tuple(a["posicao"]),
                    a.get("delta_p", 0.1)
                ) for a in frame_data]
                self.world.estados.append(estado)

            if not self.world.estados:
                self.log_message("ERROR: Loaded file contains no states.", error=True)
                self._inicializar_mundo(primeira_vez=True)
                self._construir_mundo()
                return

            self.world.agentes = [ag.clone() for ag in self.world.estados[0]]
            self.log_message(f"World loaded from: {path.split('/')[-1]}")

            # NOVO: os campos de World Settings e agentes agora vivem dentro
            # do popup "Edit Configuration", recriados a partir de
            # self.config/self.world sempre que ele é aberto — então não há
            # mais widgets fixos aqui para sincronizar após o carregamento.

            # NOVO: tenta reconectar o TrueRNG conforme o que veio no arquivo
            # carregado. O switch agora vive dentro de 'Edit Configuration' e
            # lê self.config sempre que é aberto, então não há mais nenhum
            # widget fixo aqui para sincronizar.
            quer_true_rng = self.config.get('usar_truerng', False)
            if quer_true_rng:
                sucesso, mensagem = TrueRNGSource.set_enabled(True)
                if not sucesso:
                    self.config['usar_truerng'] = False
                    self.log_message(f"WARNING: {mensagem}", error=True)

            # O arquivo carregado já traz a história completa calculada,
            # então o mundo é considerado construído a partir daqui.
            self._mundo_construido = True
            self._atualizar_estado_controles_historia()

            if hasattr(self, 'slider_historia'):
                total_frames = len(self.world.estados) - 1
                if total_frames < 0:
                    total_frames = 0

                self.slider_historia.configure(to=total_frames)
                self.slider_historia.set(0)

                self.atualizar_visualizacao_simulacao(0)

        except Exception as e:
            self.log_message(f"ERROR loading file: {e}", error=True)
            import traceback
            traceback.print_exc()

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
        # ... (sem alterações)
        popup = ctk.CTkToplevel(self)
        popup.title("Advanced Graph Filter")
        popup.geometry("600x450")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select agents:", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        nomes_agentes = [agente.nome for agente in self.world.agentes]
        agentes_vars = {nome: ctk.BooleanVar(value=False) for nome in nomes_agentes}

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
                    colors = ['#FF69B4', '#800080', '#0000FF', '#A52A2A', '#00000', '#9ACD32', '#FFA500', '#FF8C00',
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
                caminho = os.path.join(pasta, "imagens/all_agents_graph.png")
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

    def _desenhar_grid_agentes(self, ax, largura, altura, agentes):
        """
        NOVO: desenha o quadriculado do mundo com os agentes fornecidos no
        eixo 'ax'. Compartilhado entre a visualização principal da
        simulação e o preview usado em 'Edit Configuration', para que ambos
        deem o mesmo retorno visual ao usuário.
        """
        for x in range(largura):
            for y in range(altura):
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black', lw=0.5))

        for agente in agentes:
            x, y = agente.posicao
            cor = 'red' if agente.tipo == 'D' else 'blue'
            ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=cor, edgecolor='black', lw=0.5))
            ax.text(x + 0.5, y + 0.5, agente.nome, color='white', ha='center', va='center', fontsize=8, weight='bold')

        ax.set_xlim(0, largura)
        ax.set_ylim(0, altura)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.axis('off')

    def atualizar_visualizacao_simulacao(self, frame_idx=0):
        # ... (sem alterações)
        self.ax_sim.clear()

        largura = self.world.largura
        altura = self.world.altura
        agentes_no_frame = self.world.estados[frame_idx] if frame_idx < len(self.world.estados) else []

        self._desenhar_grid_agentes(self.ax_sim, largura, altura, agentes_no_frame)

        self.canvas_sim.draw()

        total_historia = len(self.world.estados) - 1
        self.entry_historia.delete(0, "end")
        self.entry_historia.insert(0, str(frame_idx))
        self.label_historia_valor.configure(text=f"/ {total_historia}")
        self._atualizar_estado_botao_restart(frame_idx)

    def log_message(self, message, error=False):
        color = "#e74c3c" if error else "white"
        try:
            padding = 30
            current_width = self.frame_logs.winfo_width() - padding
            if current_width < 100: current_width = 300
        except:
            current_width = 300
        texto = f"> {message}"
        label = ctk.CTkLabel(self.frame_logs, text=texto,
                             text_color=color,
                             font=("Consolas", 10),
                             wraplength=current_width,
                             justify="left")
        label.pack(anchor="w", padx=5, pady=2, fill="x")
        # NOVO: guarda a linha para o "Download Logs" poder exportar tudo depois.
        self._log_entries.append(texto)

    def limpar_logs(self):
        """Apaga os logs da tela e da lista exportável: o próximo Download Logs só traz o que vier depois."""
        for child in self.frame_logs.winfo_children():
            child.destroy()
        self._log_entries.clear()

    def exportar_logs(self):
        """NOVO: abre um diálogo para salvar todos os logs já gerados em um arquivo .txt."""
        if not self._log_entries:
            self.log_message("ERROR: There are no logs to export yet.", error=True)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="drima_logs.txt",
            title="Download Logs"
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(self._log_entries) + "\n")
            self.log_message(f"Logs exported to: {path.split('/')[-1]}")
        except Exception as e:
            self.log_message(f"ERROR exporting logs: {e}", error=True)

if __name__ == "__main__":
    app = TelaAjustavel()
    app.mainloop()