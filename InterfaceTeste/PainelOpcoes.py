import customtkinter as ctk

class PainelOpcoes:
    def __init__(self, master, btn_minimizar_callback):
        self.frame = ctk.CTkFrame(master, fg_color="#1e2227")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.btn_minimizar = ctk.CTkButton(
            self.frame, text="⮞", width=28, height=28, command=btn_minimizar_callback, fg_color="#23272e",
            corner_radius=14
        )
        self.btn_minimizar.place(relx=0.1, rely=0.02)

        self.frame_controles = ctk.CTkFrame(self.frame, fg_color="#23272e")
        self.frame_controles.pack(fill="x", padx=10, pady=(40, 5))

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

        self.frame_variaveis = ctk.CTkFrame(self.frame, fg_color="#23272e")
        self.frame_variaveis.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        label_font = ("Arial", 11)
        ctk.CTkLabel(self.frame_variaveis, text="Modo de Atualização", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox1 = ctk.CTkComboBox(self.frame_variaveis, values=["Síncrono", "Assíncrono"])
        self.combobox1.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Modo de mobilidade", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox2 = ctk.CTkComboBox(self.frame_variaveis, values=["Total", "Parcial"])
        self.combobox2.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Modo de interação", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox3 = ctk.CTkComboBox(self.frame_variaveis, values=["Fixo", "Variável"])
        self.combobox3.pack(fill="x", pady=2)
        ctk.CTkLabel(self.frame_variaveis, text="Modo de normalização", font=label_font).pack(anchor="w", pady=(2, 0))
        self.combobox4 = ctk.CTkComboBox(self.frame_variaveis, values=["Tradicional", "Alternativo"])
        self.combobox4.pack(fill="x", pady=2)

        # delta_p_D
        ctk.CTkLabel(self.frame_variaveis, text="delta_p_D", font=label_font).pack(anchor="w", pady=(2, 0))
        frame_slider1 = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_slider1.pack(fill="x", pady=4)
        self.slider1 = ctk.CTkSlider(frame_slider1, from_=0, to=100)
        self.slider1.pack(side="left", fill="x", expand=True)
        self.entry_slider1 = ctk.CTkEntry(frame_slider1, width=50)
        self.entry_slider1.pack(side="left", padx=(8, 0))
        self.entry_slider1.insert(0, str(self.slider1.get()))
        self.slider1.configure(command=lambda v: self._atualizar_entry(self.entry_slider1, v))

        # delta_p_R
        ctk.CTkLabel(self.frame_variaveis, text="delta_p_R", font=label_font).pack(anchor="w", pady=(2, 0))
        frame_slider2 = ctk.CTkFrame(self.frame_variaveis, fg_color="transparent")
        frame_slider2.pack(fill="x", pady=4)
        self.slider2 = ctk.CTkSlider(frame_slider2, from_=0, to=100)
        self.slider2.pack(side="left", fill="x", expand=True)
        self.entry_slider2 = ctk.CTkEntry(frame_slider2, width=50)
        self.entry_slider2.pack(side="left", padx=(8, 0))
        self.entry_slider2.insert(0, str(self.slider2.get()))
        self.slider2.configure(command=lambda v: self._atualizar_entry(self.entry_slider2, v))

    def _atualizar_entry(self, entry, valor):
        entry.delete(0, "end")
        entry.insert(0, f"{float(valor):.1f}")