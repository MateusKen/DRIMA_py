from .FrameLogs import FrameLogs
import customtkinter as ctk

class PainelFuncional:
    def __init__(self, master, filtro_callback, exportar_callback, expandir_grafico_callback, expandir_logs_callback, expandir_simulacao_callback):
        self.frame = ctk.CTkFrame(master, fg_color="#2e3b4e")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.container_pequenos = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.container_pequenos.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.32)

        # Gráfico
        self.frame_grafico_externo = ctk.CTkFrame(self.container_pequenos, fg_color="#3e4b5e")
        self.frame_grafico_externo.pack(side="left", expand=True, fill="both", padx=(0, 5))
        topo = ctk.CTkFrame(self.frame_grafico_externo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Gráfico", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=0, padx=0)
        ctk.CTkButton(topo, text="Filtro", width=60, command=filtro_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo, text="Exportar", width=70, command=exportar_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo, text="Expandir", width=70, command=expandir_grafico_callback).pack(side="right", padx=2, pady=2)

        self.tabview_graficos = ctk.CTkTabview(self.frame_grafico_externo)
        self.tabview_graficos.pack(expand=True, fill="both", padx=1, pady=0)
        self.tabview_graficos.add("Gráfico 1")
        self.tabview_graficos.add("Gráfico 2")
        self.tabview_graficos.add("Gráfico 3")
        self.scroll_grafico1 = ctk.CTkScrollableFrame(self.tabview_graficos.tab("Gráfico 1"))
        self.scroll_grafico1.pack(expand=True, fill="both")

        # Logs
        self.logs = FrameLogs(
            self.container_pequenos,
            filtro_callback=filtro_callback,
            exportar_callback=exportar_callback,
            expandir_callback=expandir_logs_callback
        )

        # Simulação
        self.frame_simulacao = ctk.CTkFrame(self.frame, fg_color="#5e6b7e")
        self.frame_simulacao.place(relx=0.02, rely=0.37, relwidth=0.96, relheight=0.6)
        topo_sim = ctk.CTkFrame(self.frame_simulacao, fg_color="transparent")
        topo_sim.pack(fill="x")
        ctk.CTkLabel(topo_sim, text="Simulação", font=("Arial", 15, "bold")).pack(side="left", anchor="nw", pady=(4, 0), padx=8)
        ctk.CTkButton(topo_sim, text="Expandir", width=70, command=expandir_simulacao_callback).pack(side="right", padx=2, pady=2)

    def preencher_grafico(self, textos):
        for texto in textos:
            ctk.CTkLabel(self.tabview_graficos.tab("Gráfico 1"), text=texto).pack(anchor="w", padx=5, pady=1)

    def preencher_simulacao(self, texto):
        ctk.CTkLabel(self.frame_simulacao, text=texto, font=("Arial", 24)).pack(expand=True)