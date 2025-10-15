
import customtkinter as ctk

class TelaAjustavel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.minimizado = False  # Estado do painel
        self.configurar_janela()
        self.criar_frames_principais()
        self.criar_layout_opcoes()
        self.criar_layout_funcional()
        self.preencher_frames()

    def configurar_janela(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Tela Ajustável")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{int(largura*0.8)}x{int(altura*0.8)}+100+50")

    def criar_frames_principais(self):
        self.frame_funcional = ctk.CTkFrame(self, fg_color="#2e3b4e")
        self.frame_funcional.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        self.frame_opcoes = ctk.CTkFrame(self, fg_color="#1e2227")
        self.frame_opcoes.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)
        # Botão filho direto de frame_opcoes
        self.btn_minimizar = ctk.CTkButton(
            self.frame_opcoes, text="⮞", width=28, height=28, command=self.toggle_opcoes, fg_color="#23272e",
            corner_radius=14
        )
        self.btn_minimizar.place(relx=0.1, rely=0.02)  # Use relx maior para garantir visibilidade no frame estreito

    def criar_layout_opcoes(self):
        self.frame_controles = ctk.CTkFrame(self.frame_opcoes, fg_color="#23272e")
        self.frame_controles.pack(fill="x", padx=10, pady=(40, 5))

        self.simulacao_rodando = False

        def alternar_simulacao():
            if not self.simulacao_rodando:
                self.btn_iniciar.configure(
                    text="Parar Simulação",
                    fg_color="#e74c3c",
                    hover_color="#b93222"
                )
                self.simulacao_rodando = True
            else:
                self.btn_iniciar.configure(
                    text="Iniciar Simulação",
                    fg_color="#27ae60",
                    hover_color="#219150"
                )
                self.simulacao_rodando = False

        btn_font = ("Arial", 10)
        btn_height = 22

        self.btn_iniciar = ctk.CTkButton(
            self.frame_controles,
            text="Iniciar Simulação",
            height=btn_height,
            font=btn_font,
            fg_color="#27ae60",
            hover_color="#219150",
            command=alternar_simulacao
        )
        self.btn_iniciar.pack(fill="x", pady=2)

        self.btn_resetar = ctk.CTkButton(self.frame_controles, text="Resetar Simulação", height=btn_height,
                                         font=btn_font)
        self.btn_resetar.pack(fill="x", pady=2)
        self.btn_montar = ctk.CTkButton(self.frame_controles, text="Montar Mundo", height=btn_height, font=btn_font)
        self.btn_montar.pack(fill="x", pady=2)
        self.btn_carregar = ctk.CTkButton(self.frame_controles, text="Carregar Mundo", height=btn_height, font=btn_font)
        self.btn_carregar.pack(fill="x", pady=2)
        self.btn_exportar = ctk.CTkButton(self.frame_controles, text="Exportar Mundo", height=btn_height, font=btn_font)
        self.btn_exportar.pack(fill="x", pady=2)

        self.frame_variaveis = ctk.CTkFrame(self.frame_opcoes, fg_color="#23272e")
        self.frame_variaveis.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        label_font = ("Arial", 11)
        combo_font = ("Arial", 10)
        combo_height = 24

        # Frame para os botões do agente
        frame_botoes_agente = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_botoes_agente.pack(fill="x", pady=(8, 0))

        # Botão Adicionar em cima, cresce horizontalmente
        self.btn_adicionar_agente = ctk.CTkButton(
            frame_botoes_agente, text="Adicionar Agente", height=26, font=("Arial", 11)
        )
        self.btn_adicionar_agente.pack(fill="x", expand=True, pady=(0, 2))
        self.btn_adicionar_agente.configure(command=self.abrir_janela_rosa_dos_ventos)

        # Frame horizontal para Remover + Entry, cresce horizontalmente
        frame_remover = ctk.CTkFrame(frame_botoes_agente, fg_color="transparent", height=26)
        frame_remover.pack(fill="x", expand=True)
        frame_remover.pack_propagate(False)

        self.btn_remover_agente = ctk.CTkButton(
            frame_remover, text="Remover Agente", height=26, width=80, font=("Arial", 11)
        )
        self.btn_remover_agente.pack(side="left", padx=(0, 2))
        self.btn_remover_agente.configure(command=self.remover_agente)

        self.entry_nome_agente = ctk.CTkEntry(
            frame_remover
        )
        self.entry_nome_agente.insert(0, "DIGITE O NOME DO AGENTE")
        self.entry_nome_agente.pack(side="left", fill="x", expand=True)

        def limpar_entry_nome_agente(event):
            if self.entry_nome_agente.get() == "DIGITE O NOME DO AGENTE":
                self.entry_nome_agente.delete(0, "end")

        self.entry_nome_agente.bind("<FocusIn>", limpar_entry_nome_agente)

        # Frame horizontal para largura, altura e modo de grafos
        def validar_positivo(valor):
            if valor == "":
                return True
            try:
                return int(valor) > 0
            except ValueError:
                return False

        vcmd_positivo = (self.register(validar_positivo), "%P")

        frame_dimensoes = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_dimensoes.pack(fill="x", pady=(6, 0))

        self.modo_grafos_var = ctk.BooleanVar(value=False)
        self.switch_modo_grafos = ctk.CTkSwitch(
            frame_dimensoes,
            text="Modo de Grafos",
            variable=self.modo_grafos_var,
            font=("Arial", 11)
        )
        self.switch_modo_grafos.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(frame_dimensoes, text="Largura", font=label_font).pack(side="left", padx=(0, 4))
        self.entry_largura_mundo = ctk.CTkEntry(
            frame_dimensoes, width=70, height=combo_height, font=combo_font,
            validate="key", validatecommand=vcmd_positivo
        )
        self.entry_largura_mundo.pack(side="left", padx=(0, 10))
        self.entry_largura_mundo.insert(0, "20")

        ctk.CTkLabel(frame_dimensoes, text="Altura", font=label_font).pack(side="left", padx=(0, 4))
        self.entry_altura_mundo = ctk.CTkEntry(
            frame_dimensoes, width=70, height=combo_height, font=combo_font,
            validate="key", validatecommand=vcmd_positivo
        )
        self.entry_altura_mundo.pack(side="left")
        self.entry_altura_mundo.insert(0, "20")

        # Comboboxes
        ctk.CTkLabel(self.frame_variaveis, text="Modo de Atualização", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox_modo_atualizacao = ctk.CTkComboBox(self.frame_variaveis, values=["Síncrono", "Assíncrono"],
                                                         font=combo_font, height=combo_height)
        self.combobox_modo_atualizacao.pack(fill="x", pady=2)
        self.combobox_modo_atualizacao.configure(state="readonly")

        ctk.CTkLabel(self.frame_variaveis, text="Modo de mobilidade", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox_modo_mobilidade = ctk.CTkComboBox(self.frame_variaveis, values=["Total", "Parcial"],
                                                        font=combo_font, height=combo_height)
        self.combobox_modo_mobilidade.pack(fill="x", pady=2)
        self.combobox_modo_mobilidade.configure(state="readonly")

        ctk.CTkLabel(self.frame_variaveis, text="Modo de interação", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox_modo_interacao = ctk.CTkComboBox(self.frame_variaveis, values=["Fixo", "Variável"],
                                                       font=combo_font, height=combo_height)
        self.combobox_modo_interacao.pack(fill="x", pady=2)
        self.combobox_modo_interacao.configure(state="readonly")

        ctk.CTkLabel(self.frame_variaveis, text="Modo de normalização", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox_modo_normalizacao = ctk.CTkComboBox(self.frame_variaveis, values=["Tradicional", "Alternativo"],
                                                          font=combo_font, height=combo_height)
        self.combobox_modo_normalizacao.pack(fill="x", pady=2)
        self.combobox_modo_normalizacao.configure(state="readonly")

        # delta_p_D
        ctk.CTkLabel(self.frame_variaveis, text="delta_p_D", font=label_font).pack(anchor="w", pady=(2, 0))
        frame_slider_delta_p_D = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_slider_delta_p_D.pack(fill="x", pady=4)
        self.slider_delta_p_D = ctk.CTkSlider(frame_slider_delta_p_D, from_=0.0001, to=1, number_of_steps=10000,
                                              height=16)
        self.slider_delta_p_D.pack(side="left", fill="x", expand=True)
        self.entry_slider_delta_p_D = ctk.CTkEntry(frame_slider_delta_p_D, width=55, height=combo_height,
                                                   font=combo_font)
        self.entry_slider_delta_p_D.pack(side="left", padx=(8, 0))
        self.entry_slider_delta_p_D.insert(0, f"{self.slider_delta_p_D.get():.4f}")

        def atualizar_entry_slider_delta_p_D(valor):
            self.entry_slider_delta_p_D.delete(0, "end")
            self.entry_slider_delta_p_D.insert(0, f"{float(valor):.4f}")

        self.slider_delta_p_D.configure(command=atualizar_entry_slider_delta_p_D)

        def on_entry_slider_delta_p_D_change(event):
            try:
                valor = float(self.entry_slider_delta_p_D.get())
            except ValueError:
                valor = 0.0001

            if valor < 0.0001:
                valor = 0.0001
            elif valor > 1:
                valor = 1.0

            self.slider_delta_p_D.set(valor)
            self.entry_slider_delta_p_D.delete(0, "end")
            self.entry_slider_delta_p_D.insert(0, f"{valor:.4f}")

        self.entry_slider_delta_p_D.bind("<Return>", on_entry_slider_delta_p_D_change)
        self.entry_slider_delta_p_D.bind("<FocusOut>", on_entry_slider_delta_p_D_change)

        # delta_p_R
        ctk.CTkLabel(self.frame_variaveis, text="delta_p_R", font=label_font).pack(anchor="w", pady=(2, 0))
        frame_slider_delta_p_R = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_slider_delta_p_R.pack(fill="x", pady=4)
        self.slider_delta_p_R = ctk.CTkSlider(frame_slider_delta_p_R, from_=0.0001, to=1, number_of_steps=10000,
                                              height=16)
        self.slider_delta_p_R.pack(side="left", fill="x", expand=True)
        self.entry_slider_delta_p_R = ctk.CTkEntry(frame_slider_delta_p_R, width=55, height=combo_height,
                                                   font=combo_font)
        self.entry_slider_delta_p_R.pack(side="left", padx=(8, 0))
        self.entry_slider_delta_p_R.insert(0, f"{self.slider_delta_p_R.get():.4f}")

        def atualizar_entry_slider_delta_p_R(valor):
            self.entry_slider_delta_p_R.delete(0, "end")
            self.entry_slider_delta_p_R.insert(0, f"{float(valor):.4f}")

        self.slider_delta_p_R.configure(command=atualizar_entry_slider_delta_p_R)

        def on_entry_slider_delta_p_R_change(event):
            try:
                valor = float(self.entry_slider_delta_p_R.get())
            except ValueError:
                valor = 0.0001

            if valor < 0.0001:
                valor = 0.0001
            elif valor > 1:
                valor = 1.0

            self.slider_delta_p_R.set(valor)
            self.entry_slider_delta_p_R.delete(0, "end")
            self.entry_slider_delta_p_R.insert(0, f"{valor:.4f}")

        self.entry_slider_delta_p_R.bind("<Return>", on_entry_slider_delta_p_R_change)
        self.entry_slider_delta_p_R.bind("<FocusOut>", on_entry_slider_delta_p_R_change)

        self.btn_minimizar.lift()

    def remover_agente(self):
        popup = ctk.CTkToplevel(self)
        nome = self.entry_nome_agente.get()  # Pega o valor atual do textbox
        # Aqui você pode usar 'nome' para remover o agente do seu sistema
        popup.title("Confirmação")
        popup.geometry("300x120")
        popup.grab_set()
        ctk.CTkLabel(popup, text=f"Deseja realmente remover o agente {nome}?", font=("Arial", 12)).pack(pady=16)
        frame_botoes = ctk.CTkFrame(popup, fg_color="transparent")
        frame_botoes.pack(pady=4)

        def confirmar():
            popup.destroy()

            def resetar_entry():
                self.entry_nome_agente.delete(0, "end")
                self.entry_nome_agente.insert(0, "DIGITE O NOME DO AGENTE")
                self.entry_nome_agente.focus_set()
                self.entry_nome_agente.select_range(0, "end")

            self.after(10, resetar_entry)

        def cancelar():
            popup.destroy()

        ctk.CTkButton(frame_botoes, text="Sim", command=confirmar, width=80).pack(side="left", padx=8)
        ctk.CTkButton(frame_botoes, text="Não", command=cancelar, width=80).pack(side="left", padx=8)

    def abrir_janela_rosa_dos_ventos(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Adicionar Agente")
        popup.geometry("420x560")
        popup.grab_set()

        # Validação para inteiro
        def validar_inteiro(valor):
            if valor == "":
                return True
            try:
                int(valor)
                return True
            except ValueError:
                return False

        # Validação para float
        def validar_float(valor):
            if valor == "":
                return True
            try:
                float(valor) >= 0
                return True
            except ValueError:
                return False

        vcmd_int = (popup.register(validar_inteiro), "%P")
        vcmd_float = (popup.register(validar_float), "%P")

        # Marcadores de seleção
        tipo_aleatorio = ctk.BooleanVar(value=True)
        tipo_r = ctk.BooleanVar(value=True)
        tipo_d = ctk.BooleanVar(value=True)

        def on_aleatorio():
            tipo_aleatorio.set(True)
            tipo_r.set(True)
            tipo_d.set(True)

        def on_r():
            tipo_aleatorio.set(False)
            tipo_r.set(True)
            tipo_d.set(False)

        def on_d():
            tipo_aleatorio.set(False)
            tipo_r.set(False)
            tipo_d.set(True)

        ctk.CTkLabel(popup, text="Tipo do Agente:", font=("Arial", 12)).pack(pady=(16, 4))
        tipo_var = ctk.StringVar(value="Aleatório")
        frame_tipos = ctk.CTkFrame(popup, fg_color="transparent")
        frame_tipos.pack(pady=2)
        ctk.CTkCheckBox(frame_tipos, text="Aleatório", variable=tipo_aleatorio, command=on_aleatorio).pack(side="left",                                                                              padx=8)
        ctk.CTkCheckBox(frame_tipos, text="R", variable=tipo_r, command=on_r).pack(side="left", padx=8)
        ctk.CTkCheckBox(frame_tipos, text="D", variable=tipo_d, command=on_d).pack(side="left", padx=8)

        # Entradas de posição (inteiro)
        ctk.CTkLabel(popup, text="Posição (X, Y):", font=("Arial", 12)).pack(pady=(18, 4))
        frame_pos = ctk.CTkFrame(popup, fg_color="transparent")
        frame_pos.pack(pady=2)
        entry_x = ctk.CTkEntry(frame_pos, width=60, placeholder_text="X", validate="key", validatecommand=vcmd_int)
        entry_x.pack(side="left", padx=6)
        entry_y = ctk.CTkEntry(frame_pos, width=60, placeholder_text="Y", validate="key", validatecommand=vcmd_int)
        entry_y.pack(side="left", padx=6)

        # Entradas para cada direção (float)
        ctk.CTkLabel(popup, text="Ações por Direção:", font=("Arial", 12)).pack(pady=(18, 4))
        frame_direcoes = ctk.CTkFrame(popup, fg_color="transparent")
        frame_direcoes.pack(pady=2)

        direcoes_grid = [
            ["NO", "N", "NE"],
            ["O", "X", "L"],
            ["SO", "S", "SE"]
        ]
        entries_direcoes = {}
        self.direcoes_zeradas = False

        def zerar_outras_direcoes(event, direcao_atual):
            if not self.direcoes_zeradas:
                for direcao, entry in entries_direcoes.items():
                    if direcao != direcao_atual:
                        entry.delete(0, "end")
                        entry.insert(0, "0.0000")
                self.direcoes_zeradas = True

        valor_padrao = round(1 / 9, 4)  # 0.1111

        for row, linha in enumerate(direcoes_grid):
            for col, direcao in enumerate(linha):
                label = ctk.CTkLabel(frame_direcoes, text=direcao)
                label.grid(row=row * 2, column=col, padx=8, pady=(2, 0))
                entry = ctk.CTkEntry(frame_direcoes, width=60, validate="key", validatecommand=vcmd_float)
                entry.insert(0, f"{valor_padrao:.4f}")
                entry.grid(row=row * 2 + 1, column=col, padx=8, pady=(0, 6))
                entries_direcoes[direcao] = entry
                entry.bind("<KeyRelease>", lambda event, d=direcao: zerar_outras_direcoes(event, d))

        # Botões
        frame_botoes = ctk.CTkFrame(popup, fg_color="transparent")
        frame_botoes.pack(pady=18)

        def adicionar():
            # Validação das posições
            x = entry_x.get()
            y = entry_y.get()
            try:
                x_int = int(x)
                y_int = int(y)
                if x_int < 0 or y_int < 0:
                    raise ValueError
            except (ValueError, TypeError):
                aviso = ctk.CTkToplevel(popup)
                aviso.title("Erro")
                aviso.geometry("320x120")
                aviso.grab_set()
                ctk.CTkLabel(aviso, text="Informe valores inteiros não negativos para X e Y.", font=("Arial", 12)).pack(
                    pady=16)
                ctk.CTkButton(aviso, text="OK", command=aviso.destroy).pack(pady=8)
                return

            # Validação das direções
            soma = 0.0
            valores = {}
            for direcao, entry in entries_direcoes.items():
                try:
                    valor = float(entry.get())
                except ValueError:
                    valor = 0.0
                valores[direcao] = valor
                soma += valor

            if soma > 1.0 + 1e-6:  # Tolerância para ponto flutuante
                aviso = ctk.CTkToplevel(popup)
                aviso.title("Erro")
                aviso.geometry("320x120")
                aviso.grab_set()
                ctk.CTkLabel(aviso, text="A soma das probabilidades não pode ser maior que 1.",
                             font=("Arial", 12)).pack(pady=16)
                ctk.CTkButton(aviso, text="OK", command=aviso.destroy).pack(pady=8)
                return

            if soma < 1.0 - 1e-6:
                def prosseguir():
                    restante = 1.0 - soma
                    entry_x = entries_direcoes["X"]
                    try:
                        atual = float(entry_x.get())
                    except ValueError:
                        atual = 0.0
                    entry_x.delete(0, "end")
                    entry_x.insert(0, f"{atual + restante:.4f}")
                    confirm.destroy()
                    popup.destroy()

                def cancelar():
                    confirm.destroy()

                confirm = ctk.CTkToplevel(popup)
                confirm.title("Confirmação")
                confirm.geometry("340x140")
                confirm.grab_set()
                ctk.CTkLabel(confirm,
                             text="A soma das probabilidades é menor que 1.\nDeseja prosseguir?\nO restante será adicionado à direção X.",
                             font=("Arial", 12)).pack(pady=12)
                frame = ctk.CTkFrame(confirm, fg_color="transparent")
                frame.pack(pady=8)
                ctk.CTkButton(frame, text="Sim", command=prosseguir, width=80).pack(side="left", padx=8)
                ctk.CTkButton(frame, text="Não", command=cancelar, width=80).pack(side="left", padx=8)
                return

            popup.destroy()

        def cancelar():
            popup.destroy()

        ctk.CTkButton(frame_botoes, text="Adicionar", command=adicionar, width=100).pack(side="left", padx=12)
        ctk.CTkButton(frame_botoes, text="Cancelar", command=cancelar, width=100).pack(side="left", padx=12)

    def toggle_opcoes(self):
        if not self.minimizado:
            self.frame_controles.pack_forget()
            self.frame_variaveis.pack_forget()
            self.frame_opcoes.place_configure(relx=0.965, relwidth=0.035)
            self.frame_funcional.place_configure(relx=0, relwidth=0.965)
            self.btn_minimizar.place_configure(relx=0.1, rely=0.02)
            self.btn_minimizar.lift()
            self.btn_minimizar.configure(text="⮜")
            self.minimizado = True
        else:
            self.frame_controles.pack(fill="x", padx=10, pady=(40, 5))  # Mantém o espaçamento correto
            self.frame_variaveis.pack(fill="both", expand=True, padx=10, pady=(5, 10))
            self.frame_opcoes.place_configure(relx=0.7, relwidth=0.3)
            self.frame_funcional.place_configure(relx=0, relwidth=0.7)
            self.btn_minimizar.place_configure(relx=0.05, rely=0.02)
            self.btn_minimizar.lift()
            self.btn_minimizar.configure(text="⮞")

            self.minimizado = False

    def criar_layout_funcional(self):
        self.container_pequenos = ctk.CTkFrame(self.frame_funcional, fg_color="transparent")
        self.container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.32)
        self.criar_frame_grafico()
        self.criar_frame_logs()
        self.criar_frame_simulacao()

    def criar_frame_grafico(self):
        self.frame_grafico_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#3e4b5e")
        self.frame_grafico_externo.pack(side="left", expand=True, fill="both", padx=(0, 5))
        topo = ctk.CTkFrame(self.frame_grafico_externo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(
            topo,
            text="Gráfico",
            font=("Arial", 13, "bold")
        ).pack(side="left", anchor="nw", pady=0, padx=0)

        # Botão de filtro
        self.btn_filtro = ctk.CTkButton(
            topo,
            text="Filtro",
            width=60,
            command=self.janela_filtro  # Defina este método
        )
        self.btn_filtro.pack(side="right", padx=2, pady=2)

        # Botão de exportar
        self.btn_exportar_grafico = ctk.CTkButton(
            topo,
            text="Exportar",
            width=70,
            command=self.acao_exportar_grafico  # Defina este método
        )
        self.btn_exportar_grafico.pack(side="right", padx=2, pady=2)

        # Botão expandir
        ctk.CTkButton(
            topo,
            text="Expandir",
            width=70,
            command=self.popup_grafico
        ).pack(side="right", padx=2, pady=2)

        self.tabview_graficos = ctk.CTkTabview(self.frame_grafico_externo)
        self.tabview_graficos.pack(expand=True, fill="both", padx=1, pady=0)
        self.tabview_graficos.add("Gráfico 1")
        self.tabview_graficos.add("Gráfico 2")
        self.tabview_graficos.add("Gráfico 3")

        self.scroll_grafico1 = ctk.CTkScrollableFrame(self.tabview_graficos.tab("Gráfico 1"))
        self.scroll_grafico1.pack(expand=True, fill="both")

    def acao_filtro(self):
        print("Ação de filtro do gráfico")

    def acao_exportar_grafico(self):
        print("Ação de exportar gráfico")

    def janela_filtro(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Filtro de Gráfico")
        popup.geometry("370x320")  # Aumenta o tamanho da janela

        popup.lift()
        popup.focus_force()
        popup.grab_set()

        ctk.CTkLabel(popup, text="Filtrar por texto:", font=("Arial", 12)).pack(anchor="w", padx=16, pady=(12, 2))
        entry_texto = ctk.CTkEntry(popup, width=220)
        entry_texto.pack(anchor="w", padx=16, pady=2)

        ctk.CTkLabel(popup, text="Ou selecione um item:", font=("Arial", 12)).pack(anchor="w", padx=16, pady=(12, 2))
        itens = ["Item 1", "Item 2", "Item 3"]
        combo_itens = ctk.CTkComboBox(popup, values=itens, width=220)
        combo_itens.pack(anchor="w", padx=16, pady=2)

        ctk.CTkLabel(popup, text="Período de tempo:", font=("Arial", 12)).pack(anchor="w", padx=16, pady=(12, 2))
        frame_periodo = ctk.CTkFrame(popup, fg_color="transparent")
        frame_periodo.pack(anchor="w", padx=16, pady=2)
        ctk.CTkLabel(frame_periodo, text="Início:", width=40).pack(side="left")
        entry_inicio = ctk.CTkEntry(frame_periodo, width=80)
        entry_inicio.pack(side="left", padx=(2, 8))
        ctk.CTkLabel(frame_periodo, text="Fim:", width=30).pack(side="left")
        entry_fim = ctk.CTkEntry(frame_periodo, width=80)
        entry_fim.pack(side="left", padx=2)

        def aplicar_filtro():
            texto = entry_texto.get()
            item = combo_itens.get()
            inicio = entry_inicio.get()
            fim = entry_fim.get()
            print(f"Filtro: texto={texto}, item={item}, inicio={inicio}, fim={fim}")
            popup.destroy()

        ctk.CTkButton(popup, text="Aplicar Filtro", command=aplicar_filtro).pack(pady=(18, 12))

    def popup_grafico(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Gráfico - Expandido")
        popup.geometry("600x400")
        popup.grab_set()

        topo = ctk.CTkFrame(popup, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(
            topo,
            text="Gráfico",
            font=("Arial", 13, "bold")
        ).pack(side="left", anchor="nw", pady=0, padx=0)

        btn_filtro = ctk.CTkButton(
            topo,
            text="Filtro",
            width=60,
            command=self.janela_filtro
        )
        btn_filtro.pack(side="right", padx=2, pady=2)

        btn_exportar = ctk.CTkButton(
            topo,
            text="Exportar",
            width=70,
            command=self.acao_exportar_grafico
        )
        btn_exportar.pack(side="right", padx=2, pady=2)

        tabview = ctk.CTkTabview(popup)
        tabview.pack(expand=True, fill="both", padx=10, pady=10)
        tabview.add("Gráfico 1")
        tabview.add("Gráfico 2")
        tabview.add("Gráfico 3")
        ctk.CTkLabel(tabview.tab("Gráfico 1"), text="Conteúdo do Gráfico 1").pack(anchor="w")
        ctk.CTkLabel(tabview.tab("Gráfico 2"), text="Conteúdo do Gráfico 2").pack(anchor="w")
        ctk.CTkLabel(tabview.tab("Gráfico 3"), text="Conteúdo do Gráfico 3").pack(anchor="w")

    def criar_frame_logs(self):
        self.frame_logs_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#4e5b6e")
        self.frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))
        topo = ctk.CTkFrame(self.frame_logs_externo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=(2, 0), padx=6)

        btn_filtro = ctk.CTkButton(
            topo,
            text="Filtro",
            width=60,
            command=self.janela_filtro
        )
        btn_filtro.pack(side="right", padx=2, pady=2)

        btn_exportar = ctk.CTkButton(
            topo,
            text="Exportar",
            width=70,
            command=self.acao_exportar_grafico
        )
        btn_exportar.pack(side="right", padx=2, pady=2)

        ctk.CTkButton(
            topo,
            text="Expandir",
            width=70,
            command=self.popup_logs
        ).pack(side="right", padx=2, pady=2)

        # Cor de fundo do frame de logs destacada
        self.frame_logs = ctk.CTkScrollableFrame(self.frame_logs_externo, fg_color="#232b38")
        self.frame_logs.pack(expand=True, fill="both")

    def popup_logs(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Logs - Expandido")
        popup.geometry("400x400")
        popup.grab_set()

        topo = ctk.CTkFrame(popup, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=(2, 0), padx=6)

        btn_filtro = ctk.CTkButton(
            topo,
            text="Filtro",
            width=60,
            command=self.janela_filtro
        )
        btn_filtro.pack(side="right", padx=2, pady=2)

        btn_exportar = ctk.CTkButton(
            topo,
            text="Exportar",
            width=70,
            command=self.acao_exportar_grafico
        )
        btn_exportar.pack(side="right", padx=2, pady=2)

        # Cor de fundo do frame de logs destacada
        frame = ctk.CTkScrollableFrame(popup, fg_color="#232b38")
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        for i in range(10):
            ctk.CTkLabel(
                frame,
                text=f"Pequeno 2 - {i + 1}"
            ).pack(anchor="w", padx=5, pady=2, fill="x")

    def criar_frame_simulacao(self):
        self.frame_simulacao = ctk.CTkFrame(self.frame_funcional, fg_color="#5e6b7e")
        self.frame_simulacao.place(relx=0.02, rely=0.37, relwidth=0.96, relheight=0.6)
        topo = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Simulação", font=("Arial", 15, "bold")).pack(side="left", anchor="nw", pady=(4, 0),
                                                                              padx=8)
        # Adicione o contador aqui:
        self.contador_iteracoes = ctk.CTkLabel(topo, text="Iterações: 0", font=("Arial", 14))
        self.contador_iteracoes.pack(side="right", padx=8)
        ctk.CTkButton(
            topo,
            text="Expandir",
            width=70,
            command=self.popup_simulacao
        ).pack(side="right", padx=2, pady=2)

    def popup_simulacao(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Simulação - Expandido")
        popup.geometry("600x400")
        popup.grab_set()

        topo = ctk.CTkFrame(popup, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Simulação", font=("Arial", 15, "bold")).pack(side="left", anchor="nw", pady=(4, 0),
                                                                              padx=8)
        # Contador de iterações na tela expandida
        ctk.CTkLabel(topo, text=self.contador_iteracoes.cget("text"), font=("Arial", 14)).pack(side="right", padx=8)
        # Botão expandir não é necessário aqui

        ctk.CTkLabel(popup, text="Frame Grande", font=("Arial", 24)).pack(expand=True)

    def popup_logs(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Logs - Expandido")
        popup.geometry("400x400")
        popup.grab_set()

        topo = ctk.CTkFrame(popup, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=(2, 0), padx=6)

        btn_filtro = ctk.CTkButton(
            topo,
            text="Filtro",
            width=60,
            command=self.janela_filtro
        )
        btn_filtro.pack(side="right", padx=2, pady=2)

        btn_exportar = ctk.CTkButton(
            topo,
            text="Exportar",
            width=70,
            command=self.acao_exportar_grafico
        )
        btn_exportar.pack(side="right", padx=2, pady=2)

        # Cor de fundo do frame de logs destacada
        frame = ctk.CTkScrollableFrame(popup, fg_color="#232b38")
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        for i in range(10):
            ctk.CTkLabel(
                frame,
                text=f"Pequeno 2 - {i + 1}"
            ).pack(anchor="w", padx=5, pady=2, fill="x")

    def preencher_frames(self):
        for i in range(10):
            ctk.CTkLabel(
                self.tabview_graficos.tab("Gráfico 1"),
                text=f"Pequeno 1 - {i + 1}"
            ).pack(anchor="w", padx=5, pady=1)
            ctk.CTkLabel(
                self.frame_logs,
                text=f"Pequeno 2 - {i + 1}"
            ).pack(anchor="w", padx=5, pady=2, fill="x")
        ctk.CTkLabel(self.frame_simulacao, text="Frame Grande", font=("Arial", 24)).pack(expand=True)