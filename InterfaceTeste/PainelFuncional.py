from .FrameLogs import FrameLogs
import customtkinter as ctk

class PainelFuncional:
    def __init__(
        self, master,
        filtro_callback, exportar_callback,
        expandir_grafico_callback, expandir_logs_callback, expandir_simulacao_callback
    ):
        self.frame = ctk.CTkFrame(master, fg_color="#2e3b4e")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Container superior (gráfico e logs)
        self.container_pequenos = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.32)

        # Gráfico
        self.frame_grafico_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#3e4b5e")
        self.frame_grafico_externo.pack(side="left", expand=True, fill="both", padx=(0, 5))
        topo_grafico = ctk.CTkFrame(self.frame_grafico_externo, fg_color="transparent")
        topo_grafico.pack(fill="x")
        ctk.CTkLabel(topo_grafico, text="Gráfico", font=("Arial", 13, "bold")).pack(side="left", anchor="nw")
        ctk.CTkButton(topo_grafico, text="Filtro", width=60, command=filtro_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo_grafico, text="Exportar", width=70, command=exportar_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo_grafico, text="Expandir", width=70, command=expandir_grafico_callback).pack(side="right", padx=2, pady=2)

        self.tabview_graficos = ctk.CTkTabview(self.frame_grafico_externo)
        self.tabview_graficos.pack(expand=True, fill="both", padx=1, pady=0)
        self.tabview_graficos.add("Gráfico 1")
        self.tabview_graficos.add("Gráfico 2")
        self.tabview_graficos.add("Gráfico 3")
        self.scroll_grafico1 = ctk.CTkScrollableFrame(self.tabview_graficos.tab("Gráfico 1"))
        self.scroll_grafico1.pack(expand=True, fill="both")

        # Logs
        self.frame_logs_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#4e5b6e")
        self.frame_logs_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))
        topo_logs = ctk.CTkFrame(self.frame_logs_externo, fg_color="transparent")
        topo_logs.pack(fill="x")
        ctk.CTkLabel(topo_logs, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", padx=6)
        ctk.CTkButton(topo_logs, text="Filtro", width=60, command=filtro_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo_logs, text="Exportar", width=70, command=exportar_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo_logs, text="Expandir", width=70, command=expandir_logs_callback).pack(side="right", padx=2, pady=2)

        self.frame_logs = ctk.CTkScrollableFrame(self.frame_logs_externo, fg_color="#232b38")
        self.frame_logs.pack(expand=True, fill="both")

        # Simulação
        self.frame_simulacao = ctk.CTkFrame(self.frame, fg_color="#5e6b7e")
        self.frame_simulacao.place(relx=0.02, rely=0.37, relwidth=0.96, relheight=0.6)
        topo_simulacao = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        topo_simulacao.pack(fill="x")
        ctk.CTkLabel(topo_simulacao, text="Simulação", font=("Arial", 15, "bold")).pack(side="left", anchor="nw", padx=8)
        ctk.CTkButton(topo_simulacao, text="Expandir", width=70, command=expandir_simulacao_callback).pack(side="right", padx=2, pady=2)

    def preencher_frames(self):
        for i in range(10):
            ctk.CTkLabel(self.tabview_graficos.tab("Gráfico 1"), text=f"Pequeno 1 - {i + 1}").pack(anchor="w", padx=5, pady=1)
            ctk.CTkLabel(self.frame_logs, text=f"Pequeno 2 - {i + 1}").pack(anchor="w", padx=5, pady=2, fill="x")
        ctk.CTkLabel(self.frame_simulacao, text="Frame Grande", font=("Arial", 24)).pack(expand=True)