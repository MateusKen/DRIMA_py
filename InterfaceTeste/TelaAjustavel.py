
import customtkinter as ctk

class TelaAjustavel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configurar_janela()

    def criar_frames_principais(self):
        self.frame_funcional = ctk.CTkFrame(self)
        self.frame_funcional.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        self.frame_opcoes = ctk.CTkFrame(self)
        self.frame_opcoes.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

    def configurar_janela(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Tela Ajustável")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{int(largura*0.8)}x{int(altura*0.8)}+100+50")

    def criar_layout_funcional(self):
        self.painel_funcional = PainelFuncional(
            self.frame_funcional,
            comando_filtro=self.janela_filtro,
            comando_exportar=self.acao_exportar_grafico,
            comando_expandir_grafico=self.popup_grafico,
            comando_expandir_logs=self.popup_logs,
            comando_expandir_simulacao=self.popup_simulacao
        )
        self.painel_funcional.preencher_frames()


if __name__ == "__main__":
    app = TelaAjustavel()
    app.mainloop()