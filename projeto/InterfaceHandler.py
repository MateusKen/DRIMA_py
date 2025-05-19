from projeto import FileHandler, GraphVisualizer, WorldVisualizer, World, WorldUpdater
import tkinter as tk
from tkinter import messagebox, simpledialog

class InterfaceHandler:
    def __init__(self, world: World):
        self.root = tk.Tk()
        self.world = world
        self.entries = {}
        self.buttons = [] # Guarda botoes para redimensionamento

    def create_menu(self, width, height):
        self.root.title("Menu de Opções")
        self.root.geometry(f"{width}x{height}")

        # Botões
        self.buttons = [
            #tk.Button(self.root, text="Iterar Mundos", command=self.on_iterate_button),
            tk.Button(self.root, text="Mostrar Simulação", command=self.on_simulation_button),
            tk.Button(self.root, text="Mostrar Gráfico de um Agente", command=self.on_show_graphics),
            #tk.Button(self.root, text="Adicionar Agente", command=self.on_add_agent),
            tk.Button(self.root, text="Configurar Parâmetros", command=self.on_parameter_conf),
            tk.Button(self.root, text="Sair", command=self.on_exit)
        ]

        for i, btn in enumerate(self.buttons):
            btn.grid(row=i, column=0, padx=20, pady=10, sticky="nsew")
            self.root.rowconfigure(i, weight=1)

        self.root.columnconfigure(0, weight=1)  # Permite expansão horizontal dos botões

        # Bind para redimensionar
        self.root.bind("<Configure>", self.resize)

        self.root.mainloop()

    def config_interface(self):
        data = FileHandler.load_config(path="drima.json")
        
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Parâmetros")
        row = 0
        for key, value in data.items():
            label = tk.Label(config_window, text=key).grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

            entry = tk.Entry(config_window)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=10, pady=5)
            self.entries[key] = entry

            row += 1
        save_button = tk.Button(config_window, text="Salvar", command=lambda:self.on_save_config(config_window))
        save_button.grid(row=row, columnspan=2, pady=10)

    def on_simulation_button(self):
        # Aqui você pode chamar sua função real de simulação
        anim = None
        try:
            data = FileHandler.load_config()
            WorldVisualizer.simulate(self.world)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível exibir a simulação: {e}")


    def on_show_graphics(self):
        nome = simpledialog.askstring("Nome do Agente", "Digite o nome do agente:")
        if nome:
            try:
                config = FileHandler.load_config()
                animated = config["grafico_animado"]
                print(len(self.world.estados))
                if animated == 0:
                    anim = GraphVisualizer.show_by_name(self.world, nome)
                else:
                    GraphVisualizer.show_animated_by_name(self.world, nome)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exibir o gráfico: {e}")

    def on_remove_agent(self):
        nome = simpledialog.askstring("Nome do Agente", "Digite o nome do Agente")
        if nome:
            try:
                self.world.remover_agente(nome)
                messagebox.showinfo("Sucesso",f"o {nome} foi removido com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível remover o agente {nome}")

        

    def on_parameter_conf(self):
    # Chama a interface de configuração da própria classe
        self.config_interface()

    def on_exit(self):
        self.root.destroy()

    def on_save_config(self, config_window):
        config_data = {}
        for key, entry in self.entries.items():
            val = entry.get()
            try:
                if "." in val:
                    config_data[key] = float(val)
                else:
                    config_data[key] = int(val)
            except ValueError:
                config_data[key] = val 
        
        FileHandler.save_config(config_data,path="drima.json")
        self.world.estados = []
        self.world = FileHandler.load_world_2([ag.clone() for ag in self.world.agentes])
        config_window.destroy()
    
    def resize(self, event):
        """Ajusta o tamanho da fonte dos botões com base na altura da janela."""
        scale = (event.width * 0.5 + event.height * 0.5) / 2
        min_font_size = 12
        max_font_size = 24
        font_size = max(min_font_size, min(int(scale // 50), max_font_size))  # Escala com altura da janela
        for btn in self.buttons:
            btn.config(font=("Arial", font_size))