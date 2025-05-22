from projeto import FileHandler, GraphVisualizer, WorldVisualizer, World, WorldUpdater, AgentSpawner
import tkinter as tk
from tkinter import messagebox, simpledialog

class InterfaceHandler:
    def __init__(self, world: World):
        self.root = tk.Tk()
        self.world = world
        self.agent_spawner = AgentSpawner.AgentSpawner(self.world)
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
            tk.Button(self.root, text="Adicionar Agente", command=self.on_add_agent),
            tk.Button(self.root, text="Remover Agentes", command=self.show_remove_agents_interface),
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
            WorldVisualizer.simulate_2(self.world)
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

    def on_add_agent(self):
        """
        Adiciona ao tabuleiro aleatoriamente um número determinado de agentes
        """
        num = simpledialog.askinteger("Quantidade de Agentes", "Quantos agentes deseja criar?")
        if num:
            
            try:
                for _ in range(num):
                    self.agent_spawner.spawn_randomly()
                self.world = FileHandler.load_world_2(self.world.agentes)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar agentes: {e}")

    def show_remove_agents_interface(self):
        """
        Remove um intervalo de agentes escolhidos. Ex se selecionado Deterministico
        Intervalo inicial: 2
        Intervalo final: 7

        serão removidos: D2,D3,D4,D5,D6,D7.
        """

        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remover Agentes")
        remove_window.geometry("380x280")  # Tamanho maior da janela

        tipo_var = tk.StringVar(value='D')  # Default: Determinístico

        # Título
        tk.Label(remove_window, text="Remover Agentes", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(15, 15)
        )

        # Tipo de agente
        tk.Label(remove_window, text="Tipo de agente", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w", padx=20
        )
        tipo_frame = tk.Frame(remove_window)
        tipo_frame.grid(row=1, column=1, sticky="w", padx=10)
        tk.Radiobutton(tipo_frame, text="Determinístico", font=("Arial", 11),
                        variable=tipo_var, value='D').pack(side="left", padx=5)
        tk.Radiobutton(tipo_frame, text="Aleatório", font=("Arial", 11),
                        variable=tipo_var, value='R').pack(side="left", padx=5)

        # Intervalo inicial
        tk.Label(remove_window, text="Intervalo Inicial", font=("Arial", 12)).grid(
            row=2, column=0, sticky="w", padx=20, pady=(10, 5)
        )
        entry_ini = tk.Entry(remove_window, font=("Arial", 12), width=15)
        entry_ini.grid(row=2, column=1, padx=10, pady=(10, 5))

        # Intervalo final
        tk.Label(remove_window, text="Intervalo Final", font=("Arial", 12)).grid(
            row=3, column=0, sticky="w", padx=20, pady=(5, 10)
        )
        entry_fim = tk.Entry(remove_window, font=("Arial", 12), width=15)
        entry_fim.grid(row=3, column=1, padx=10, pady=(5, 10))

        # Botão confirmar
        def confirmar():
            tipo = tipo_var.get()
            try:
                start = int(entry_ini.get())
                end = int(entry_fim.get())
                if start > end:
                    raise ValueError("Início maior que fim.")
                removidos = 0
                for i in range(start, end + 1):
                    nome = f"{tipo}{i:02d}"
                    try:
                        removido = self.world.remover_agente(nome)
                        print(f"removido = {removido.nome}")
                        removidos += 1
                    except Exception:
                        pass  # Agente não encontrado — segue
                messagebox.showinfo("Resultado", f"{removidos} agente(s) removido(s) com sucesso.")
                remove_window.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover agentes: {e}")
        tk.Button(remove_window, text="Confirmar", font=("Arial", 12),
        width=15, height=1, command=confirmar).grid(row=4, column=0, columnspan=2, pady=15)

        

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