import customtkinter as ctk

class FrameLogs:
    def __init__(self, master, filtro_callback, exportar_callback, expandir_callback):
        self.frame_externo = ctk.CTkFrame(master, fg_color="#4e5b6e")
        self.frame_externo.pack(side="left", expand=True, fill="both", padx=(5, 0))

        topo = ctk.CTkFrame(self.frame_externo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text="Logs", font=("Arial", 13, "bold")).pack(side="left", anchor="nw", pady=(2, 0), padx=6)

        ctk.CTkButton(topo, text="Filtro", width=60, command=filtro_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo, text="Exportar", width=70, command=exportar_callback).pack(side="right", padx=2, pady=2)
        ctk.CTkButton(topo, text="Expandir", width=70, command=expandir_callback).pack(side="right", padx=2, pady=2)

        self.frame_logs = ctk.CTkScrollableFrame(self.frame_externo, fg_color="#232b38")
        self.frame_logs.pack(expand=True, fill="both")

    def preencher_logs(self, textos):
        for texto in textos:
            ctk.CTkLabel(self.frame_logs, text=texto).pack(anchor="w", padx=5, pady=2, fill="x")