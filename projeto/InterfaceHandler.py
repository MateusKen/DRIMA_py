from projeto import FileHandler, GraphVisualizer, WorldVisualizer, World, Agent, WorldUpdater, AgentSpawner
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

class InterfaceHandler:
    def __init__(self, world: World, agent_spawner: AgentSpawner):
        self.root = tk.Tk()
        self.world = world
        self.agent_spawner = agent_spawner
        self.entries = {}
        self.buttons = [] # Guarda botoes para redimensionamento
        

    def create_menu(self, width, height):
        self.root.title("Menu de Opções")
        self.root.geometry(f"{width}x{height}")

        # Botões
        self.buttons = [
            #tk.Button(self.root, text="Iterar Mundos", command=self.on_iterate_button),
            tk.Button(self.root, text="Mostrar Simulação", command=self.on_simulation_interval),
            tk.Button(self.root, text="Mostrar Gráfico de um Agente", command=self.on_show_graphics),
            tk.Button(self.root, text="Adicionar Agente", command=self.on_add_agent),
            tk.Button(self.root, text="Remover Agente", command=self.on_remove_agent),
            tk.Button(self.root, text="Configurar Parâmetros", command=self.on_parameter_conf),
            tk.Button(self.root, text="Salvar Mundo", command=self.on_save_states),
            tk.Button(self.root, text="Carregar Mundo", command=self.on_load_states),
            #tk.Button(self.root, text="Imprime Mundo", command=self.on_print_states),
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

    """ def on_show_graphics(self):
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
                messagebox.showerror("Erro", f"Não foi possível exibir o gráfico: {e}") """
    def on_show_graphics(self):
        GraphWindow(self.root, self.world)

    def on_simulation_interval(self):
        SimulationIntervalWindow(self.root, self.world)

    def on_add_agent_random(self):
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

    def on_add_agent(self):
        AgentInsertWindow(self)

    def on_remove_agent(self):
        nome = simpledialog.askstring("Remover Agente", "Digite o nome do agente a ser removido:")

        if nome:
            try:
                idx = self.world.encontrar_agente(nome)
                if idx == -1:
                    messagebox.showerror("Erro", f"O agente '{nome}' não foi encontrado.")
                    return
                self.world.reset_agents()

                removido = self.world.agentes.pop(idx)
                self.world = FileHandler.load_world_2(self.world.agentes)
                messagebox.showinfo("Sucesso", f"O agente '{removido.nome}' foi removido com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover agente:\n{e}")

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
                        #self.world = FileHandler.load_world_2(self.world)
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
        
        self.world.reset_agents()
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
    
    def on_save_states(self):
        try:
            config = FileHandler.load_config("drima.json")
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if path:
                FileHandler.save_world_json(self.world, config, path)
                messagebox.showinfo("Sucesso", f"dados do mundo salvos em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar mundo: {e}")

    def on_load_states(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if path:
                config, states = FileHandler.load_world_json(path)


                reconstructed_states = []
                for frame in states:
                    estado = []
                    for agent_data in frame:
                        ag = Agent(
                            nome=agent_data["nome"],
                            tipo=agent_data["tipo"],
                            posicao=tuple(agent_data["posicao"]),
                            padrao_movimento=agent_data["padrao_movimento"]
                        )
                        estado.append(ag)
                    reconstructed_states.append(estado)

                self.world.estados = reconstructed_states
                self.world.agentes = [ag.clone() for ag in reconstructed_states[0]]
                messagebox.showinfo("Sucesso", "Mundo carregado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar estados: {e}")

    def on_print_states(self):
        print(self.world)

class GraphWindow:
    def __init__(self, root, world):
        self.world = world
        self.window = tk.Toplevel(root)
        self.window.title("Seleção de Gráfico")
        self.window.geometry("350x220")  # janela um pouco menor e mais justa

        font_default = ("Arial", 12)

        # Nome do agente (centralizado)
        name_frame = tk.Frame(self.window)
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Digite o nome do agente:", font=font_default).pack()
        self.name_entry = tk.Entry(name_frame, font=font_default, width=15)
        self.name_entry.pack(pady=8)

        # Intervalo da história
        tk.Label(self.window, text="Intervalo da história", font=font_default).pack(pady=10)

        interval_frame = tk.Frame(self.window)
        interval_frame.pack()

        self.start_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.start_entry.pack(side=tk.LEFT, padx=10)
        tk.Label(interval_frame, text="até", font=font_default).pack(side=tk.LEFT)
        self.end_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.end_entry.pack(side=tk.LEFT, padx=10)

        # Botão de confirmar
        tk.Button(self.window, text="Plotar gráfico", font=font_default, command=self.plot_graph).pack(pady=20)

    def plot_graph(self):
        name = self.name_entry.get().strip()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()

        if not name or not start.isdigit() or not end.isdigit():
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        start = int(start)
        end = int(end)

        if start > end:
            messagebox.showerror("Erro", "O início não pode ser maior que o fim.")
            return

        try:
            from projeto import GraphVisualizer
            GraphVisualizer.show_by_name_interval(self.world, name, start, end)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar o gráfico:\n{e}")
        
class AgentInsertWindow:
    def __init__(self, interface_handler : InterfaceHandler):
        self.world = interface_handler.world
        self.spawner = interface_handler.agent_spawner
        self.window = tk.Toplevel(interface_handler.root)
        self.window.title("Adicionar Novo Agente")
        self.window.geometry("500x550")
        font_default = ("Arial", 12)

        # Nome não será mais necessário, pois o AgentSpawner já nomeia automaticamente

        # Tipo
        tk.Label(self.window, text="Tipo do Agente (opcional):", font=font_default).pack(pady=5)
        self.tipo_var = tk.StringVar(value="")  # vazio = aleatório
        tipo_frame = tk.Frame(self.window)
        tipo_frame.pack()
        tk.Radiobutton(tipo_frame, text="Aleatório", variable=self.tipo_var, value="", font=font_default).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(tipo_frame, text="R", variable=self.tipo_var, value="R", font=font_default).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(tipo_frame, text="D", variable=self.tipo_var, value="D", font=font_default).pack(side=tk.LEFT, padx=10)

        # Posição
        tk.Label(self.window, text="Posição (x, y) (opcional):", font=font_default).pack(pady=5)
        pos_frame = tk.Frame(self.window)
        pos_frame.pack()
        self.x_entry = tk.Entry(pos_frame, font=font_default, width=5)
        self.x_entry.pack(side=tk.LEFT, padx=5)
        self.y_entry = tk.Entry(pos_frame, font=font_default, width=5)
        self.y_entry.pack(side=tk.LEFT, padx=5)

        # Padrão de movimento
        tk.Label(self.window, text="Padrão de Movimento (opcional, 9 direções):", font=font_default).pack(pady=10)
        labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE', 'X']
        self.mov_entries = []
        for label_text in labels:
            mov_frame = tk.Frame(self.window)
            mov_frame.pack()
            tk.Label(mov_frame, text=label_text, font=font_default, width=5).pack(side=tk.LEFT)
            entry = tk.Entry(mov_frame, font=font_default, width=10)
            entry.pack(side=tk.LEFT)
            self.mov_entries.append(entry)

        # Botão
        tk.Button(self.window, text="Adicionar Agente", font=font_default, command=self.add_agent).pack(pady=20)

    def add_agent(self):
        try:
            # Coleta tipo
            tipo = self.tipo_var.get() if self.tipo_var.get() else None

            # Coleta posição
            x_str = self.x_entry.get().strip()
            y_str = self.y_entry.get().strip()
            position = None
            if x_str and y_str:
                position = (int(x_str), int(y_str))

            # Coleta padrão de movimento
            mov_values = []
            for entry in self.mov_entries:
                val_str = entry.get().strip()
                mov_values.append(float(val_str) if val_str else 0.0)

            # Se tudo vazio, assume None para deixar o Spawner decidir
            moving_pattern = mov_values if any(mov_values) else None
            self.spawner.world = self.world
            agent = self.spawner.spawn_randomly(type=tipo, moving_pattern=moving_pattern, position=position) 
            FileHandler.reload_world(self.world, self.spawner)

            messagebox.showinfo("Sucesso", f"Agente {agent.nome} adicionado com sucesso!")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar agente:\n{e}")

class SimulationIntervalWindow:
    def __init__(self, root, world):
        self.world = world
        self.window = tk.Toplevel(root)
        self.window.title("Simular intervalo")
        self.window.geometry("300x200")

        font_default = ("Arial", 12)

        tk.Label(self.window, text="Escolha o intervalo da Historia:", font=font_default).pack(pady=10)

        interval_frame = tk.Frame(self.window)
        interval_frame.pack()

        self.start_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.start_entry.pack(side=tk.LEFT, padx=10)
        tk.Label(interval_frame, text="até", font=font_default).pack(side=tk.LEFT)
        self.end_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.end_entry.pack(side=tk.LEFT, padx=10)

        tk.Button(self.window, text="Iniciar Simulação", font=font_default, command=self.start_simulation).pack(pady=20)

    def start_simulation(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()

        if not start.isdigit() or not end.isdigit():
            messagebox.showerror("Erro", "Preencha os dois campos com números válidos.")
            return

        start = int(start)
        end = int(end)

        if start > end:
            messagebox.showerror("Erro", "O início não pode ser maior que o fim.")
            return

        try:
            from projeto import WorldVisualizer
            WorldVisualizer.simulate_interval(self.world, start, end)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a simulação: {e}")