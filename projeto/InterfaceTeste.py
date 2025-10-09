
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
        self.frame_controles.pack(fill="x", padx=10, pady=(40, 5))  # Espaço extra no topo

        # Botões menores
        self.btn_iniciar = ctk.CTkButton(self.frame_controles, text="Iniciar Simulação", height=28, font=("Arial", 12))
        self.btn_iniciar.pack(fill="x", pady=2)
        self.btn_resetar = ctk.CTkButton(self.frame_controles, text="Resetar Simulação", height=28, font=("Arial", 12))
        self.btn_resetar.pack(fill="x", pady=2)
        self.btn_montar = ctk.CTkButton(self.frame_controles, text="Montar Mundo", height=28, font=("Arial", 12))
        self.btn_montar.pack(fill="x", pady=2)
        self.btn_exportar = ctk.CTkButton(self.frame_controles, text="Exportar Mundo", height=28, font=("Arial", 12))
        self.btn_exportar.pack(fill="x", pady=2)

        self.contador_iteracoes = ctk.CTkLabel(self.frame_controles, text="Iterações: 0", font=("Arial", 14))
        self.contador_iteracoes.pack(pady=(8, 2))

        self.frame_variaveis = ctk.CTkFrame(self.frame_opcoes, fg_color="#23272e")
        self.frame_variaveis.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        label_font = ("Arial", 11)

        ctk.CTkLabel(self.frame_variaveis, text="Variável 1", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox1 = ctk.CTkComboBox(self.frame_variaveis, values=["Opção 1", "Opção 2"])
        self.combobox1.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Variável 2", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox2 = ctk.CTkComboBox(self.frame_variaveis, values=["Opção 1", "Opção 2"])
        self.combobox2.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Variável 3", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox3 = ctk.CTkComboBox(self.frame_variaveis, values=["Opção 1", "Opção 2"])
        self.combobox3.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Variável 4", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox4 = ctk.CTkComboBox(self.frame_variaveis, values=["Opção 1", "Opção 2"])
        self.combobox4.pack(fill="x", pady=2)

        ctk.CTkLabel(self.frame_variaveis, text="Variável 5", font=label_font).pack(anchor="w", pady=(2, 0))
        self.slider1 = ctk.CTkSlider(self.frame_variaveis, from_=0, to=100)
        self.slider1.pack(fill="x", pady=4)

        ctk.CTkLabel(self.frame_variaveis, text="Variável 6", font=label_font).pack(anchor="w", pady=(2, 0))
        self.slider2 = ctk.CTkSlider(self.frame_variaveis, from_=0, to=100)
        self.slider2.pack(fill="x", pady=4)

        self.btn_minimizar.lift()

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

    def popup_grafico(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Gráfico - Expandido")
        popup.geometry("600x400")
        tabview = ctk.CTkTabview(popup)
        tabview.pack(expand=True, fill="both", padx=10, pady=10)
        tabview.add("Gráfico 1")
        tabview.add("Gráfico 2")
        tabview.add("Gráfico 3")
        # Exemplo: adicionar conteúdo
        ctk.CTkLabel(tabview.tab("Gráfico 1"), text="Conteúdo do Gráfico 1").pack(anchor="w")
        ctk.CTkLabel(tabview.tab("Gráfico 2"), text="Conteúdo do Gráfico 2").pack(anchor="w")
        ctk.CTkLabel(tabview.tab("Gráfico 3"), text="Conteúdo do Gráfico 3").pack(anchor="w")

    def criar_frame_logs(self):
        self.frame_logs_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#4e5b6e")
        self.frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))
        topo = ctk.CTkFrame(self.frame_logs_externo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=(2, 0), padx=6)
        ctk.CTkButton(
            topo,
            text="Expandir",
            width=70,
            command=self.popup_logs
        ).pack(side="right", padx=2, pady=2)
        self.frame_logs = ctk.CTkScrollableFrame(self.frame_logs_externo, fg_color="#4e5b6e")
        self.frame_logs.pack(expand=True, fill="both")

    def popup_logs(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Logs - Expandido")
        popup.geometry("400x400")
        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        # Exemplo: adicionar conteúdo
        for i in range(10):
            ctk.CTkLabel(frame, text=f"Pequeno 2 - {i + 1}").pack(anchor="w")

    def criar_frame_simulacao(self):
        self.frame_simulacao = ctk.CTkFrame(self.frame_funcional, fg_color="#5e6b7e")
        self.frame_simulacao.place(relx=0.02, rely=0.37, relwidth=0.96, relheight=0.6)
        topo = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Simulação", font=("Arial", 15, "bold")).pack(side="left", anchor="nw", pady=(4, 0),
                                                                              padx=8)
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
        ctk.CTkLabel(popup, text="Frame Grande", font=("Arial", 24)).pack(expand=True)

    def preencher_frames(self):
        for i in range(10):
            ctk.CTkLabel(self.tabview_graficos.tab("Gráfico 1"), text=f"Pequeno 1 - {i + 1}").pack(anchor="w", padx=5,
                                                                                                   pady=1)
            ctk.CTkLabel(self.frame_logs, text=f"Pequeno 2 - {i + 1}").pack(anchor="w", padx=5, pady=1)
        ctk.CTkLabel(self.frame_simulacao, text="Frame Grande", font=("Arial", 24)).pack(expand=True)

if __name__ == "__main__":
    app = TelaAjustavel()
    app.mainloop()