# project/InterfaceHandler.py
# Old interface deprecated
from .Representation import History, Agent
from .FileHandler import FileHandler
from .GraphVisualizer import GraphVisualizer
from .WorldVisualizer import WorldVisualizer
from .WorldUpdater import WorldUpdater
from .AgentSpawner import AgentSpawner
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

class InterfaceHandler:
    def __init__(self, history: History, agent_spawner: AgentSpawner):
        self.root = tk.Tk()
        self.history = history
        self.agent_spawner = agent_spawner
        self.entries = {}
        self.buttons = [] # Holds buttons for resizing
        
    def create_menu(self, width, height):
        self.root.title("Menu de Opções") # UI text kept in Portuguese
        self.root.geometry(f"{width}x{height}")

        # Buttons (UI text kept in Portuguese)
        self.buttons = [
            tk.Button(self.root, text="Mostrar Simulação", command=self.on_simulation_interval),
            tk.Button(self.root, text="Mostrar Gráfico de um Agente", command=self.on_show_graphics),
            tk.Button(self.root, text="Adicionar Agente", command=self.on_add_agent),
            tk.Button(self.root, text="Remover Agente", command=self.on_remove_agent),
            tk.Button(self.root, text="Configurar Parâmetros", command=self.on_parameter_conf),
            tk.Button(self.root, text="Salvar Mundo", command=self.on_save_states),
            tk.Button(self.root, text="Carregar Mundo", command=self.on_load_states),
            tk.Button(self.root, text="Sair", command=self.on_exit)
        ]

        for i, btn in enumerate(self.buttons):
            btn.grid(row=i, column=0, padx=20, pady=10, sticky="nsew")
            self.root.rowconfigure(i, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.bind("<Configure>", self.resize)
        self.root.mainloop()

    def config_interface(self):
        data = FileHandler.load_config(path="drima.json")
        
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Parâmetros")
        row = 0
        for key, value in data.items():
            tk.Label(config_window, text=key).grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

            entry = tk.Entry(config_window)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=10, pady=5)
            self.entries[key] = entry
            row += 1
            
        save_button = tk.Button(config_window, text="Salvar", command=lambda:self.on_save_config(config_window))
        save_button.grid(row=row, columnspan=2, pady=10)

    def on_simulation_button(self):
        try:
            data = FileHandler.load_config()
            WorldVisualizer.simulate_2(self.history)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível exibir a simulação: {e}")

    def on_show_graphics(self):
        GraphWindow(self.root, self.history)

    def on_simulation_interval(self):
        SimulationIntervalWindow(self.root, self.history)

    def on_add_agent_random(self):
        num = simpledialog.askinteger("Quantidade de Agentes", "Quantos agentes deseja criar?")
        if num:
            try:
                for _ in range(num):
                    self.agent_spawner.spawn_randomly()
                # This logic is complex, needs full reload
                self.history = FileHandler.load_history_from_config("drima.json") 
                self.history.agents = self.agent_spawner.history.agents # Re-link
                messagebox.showinfo("Sucesso", f"{num} agentes criados.")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar agentes: {e}")

    def on_add_agent(self):
        AgentInsertWindow(self)

    def on_remove_agent(self):
        name = simpledialog.askstring("Remover Agente", "Digite o nome do agente a ser removido:")
        if name:
            try:
                # remove_agent now handles states list as well
                agent = self.history.remove_agent(name) 
                if agent:
                    messagebox.showinfo("Sucesso", f"O agente '{agent.name}' foi removido com sucesso.")
                else:
                    messagebox.showerror("Erro", f"O agente '{name}' não foi encontrado.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover agente:\n{e}")

    def show_remove_agents_interface(self):
        # ... (complex UI logic, left as is) ...
        pass

    def on_parameter_conf(self):
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
        
        FileHandler.save_config(config_data, path="drima.json")
        
        self.history.reset_agents_to_initial_state()
        # Reload history object with new config
        self.history = FileHandler.load_history_from_config("drima.json")
        self.agent_spawner.history = self.history # Re-link spawner
        
        config_window.destroy()
    
    def resize(self, event):
        scale = (event.width * 0.5 + event.height * 0.5) / 2
        min_font_size = 12
        max_font_size = 24
        font_size = max(min_font_size, min(int(scale // 50), max_font_size))
        for btn in self.buttons:
            btn.config(font=("Arial", font_size))
    
    def on_save_states(self):
        try:
            config = FileHandler.load_config("drima.json")
            path = filedialog.asksaveasfilename(defaultextension=".json.gz", filetypes=[("Gzipped JSON", "*.json.gz")])
            if path:
                # Save using the new gzipped function with English keys
                FileHandler.save_history_json_gzipped(self.history, config, path)
                messagebox.showinfo("Sucesso", f"Dados do mundo salvos em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar mundo: {e}")

    def on_load_states(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Gzipped JSON", "*.json.gz"), ("JSON files", "*.json")])
            if not path:
                return

            data = {}
            if path.endswith(".gz"):
                data = FileHandler.load_history_json_gzipped(path)
            else:
                # Legacy support for uncompressed JSON
                config, states_data = FileHandler.load_history_json(path)
                data = {"config": config, "states": states_data}

            config = data["config"]
            states_data = data["states"]
            FileHandler.save_config(config, "drima.json") # Save as current config

            # Reconstruct states with compatibility logic
            reconstructed_states = []
            for frame in states_data:
                state = []
                for agent_data in frame:
                    # ** COMPATIBILITY LOGIC **
                    ag = Agent(
                        name=agent_data.get("name", agent_data.get("nome")),
                        agent_type=agent_data.get("type", agent_data.get("tipo")),
                        position=tuple(agent_data.get("position", agent_data.get("posicao"))),
                        movement_pattern=agent_data.get("movement_pattern", agent_data.get("padrao_movimento")),
                        delta_p=agent_data.get("delta_p", 0.1)
                    )
                    state.append(ag)
                reconstructed_states.append(state)

            # Re-initialize history object with new config
            self.history = FileHandler.load_history_from_config("drima.json")
            self.agent_spawner.history = self.history # Re-link spawner
            
            # Load the reconstructed states
            self.history.states = reconstructed_states
            self.history.agents = [ag.clone() for ag in reconstructed_states[0]]
            
            messagebox.showinfo("Sucesso", "Mundo carregado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar estados: {e}")

    def on_print_states(self):
        print(self.history)

# --- Sub-windows ---

class GraphWindow:
    def __init__(self, root, history):
        self.history = history
        self.window = tk.Toplevel(root)
        self.window.title("Seleção de Gráfico")
        self.window.geometry("350x220")
        
        font_default = ("Arial", 12)
        
        name_frame = tk.Frame(self.window)
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Digite o nome do agente:", font=font_default).pack()
        self.name_entry = tk.Entry(name_frame, font=font_default, width=15)
        self.name_entry.pack(pady=8)

        tk.Label(self.window, text="Intervalo da história", font=font_default).pack(pady=10)
        interval_frame = tk.Frame(self.window)
        interval_frame.pack()

        self.start_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.start_entry.pack(side=tk.LEFT, padx=10)
        tk.Label(interval_frame, text="até", font=font_default).pack(side=tk.LEFT)
        self.end_entry = tk.Entry(interval_frame, font=font_default, width=5)
        self.end_entry.pack(side=tk.LEFT, padx=10)

        tk.Button(self.window, text="Plotar gráfico", font=font_default, command=self.plot_graph).pack(pady=20)

    def plot_graph(self):
        name = self.name_entry.get().strip()
        start_str = self.start_entry.get().strip()
        end_str = self.end_entry.get().strip()

        if not name or not start_str.isdigit() or not end_str.isdigit():
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        start = int(start_str)
        end = int(end_str)

        if start > end:
            messagebox.showerror("Erro", "O início não pode ser maior que o fim.")
            return
        
        if end >= len(self.history.states):
             end = len(self.history.states) - 1 # Adjust to max available

        try:
            GraphVisualizer.show_by_name_interval(self.history, name, start, end)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar o gráfico:\n{e}")
        
class AgentInsertWindow:
    def __init__(self, interface_handler : InterfaceHandler):
        self.history = interface_handler.history
        self.spawner = interface_handler.agent_spawner
        self.window = tk.Toplevel(interface_handler.root)
        self.window.title("Adicionar Novo Agente")
        self.window.geometry("500x550")
        font_default = ("Arial", 12)

        tk.Label(self.window, text="Tipo do Agente (opcional):", font=font_default).pack(pady=5)
        self.type_var = tk.StringVar(value="")  # empty = random
        tipo_frame = tk.Frame(self.window)
        tipo_frame.pack()
        tk.Radiobutton(tipo_frame, text="Aleatório", variable=self.type_var, value="", font=font_default).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(tipo_frame, text="R", variable=self.type_var, value="R", font=font_default).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(tipo_frame, text="D", variable=self.type_var, value="D", font=font_default).pack(side=tk.LEFT, padx=10)

        tk.Label(self.window, text="Posição (x, y) (opcional):", font=font_default).pack(pady=5)
        pos_frame = tk.Frame(self.window)
        pos_frame.pack()
        self.x_entry = tk.Entry(pos_frame, font=font_default, width=5)
        self.x_entry.pack(side=tk.LEFT, padx=5)
        self.y_entry = tk.Entry(pos_frame, font=font_default, width=5)
        self.y_entry.pack(side=tk.LEFT, padx=5)

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

        tk.Button(self.window, text="Adicionar Agente", font=font_default, command=self.add_agent).pack(pady=20)

    def add_agent(self):
        try:
            agent_type = self.type_var.get() if self.type_var.get() else None

            x_str = self.x_entry.get().strip()
            y_str = self.y_entry.get().strip()
            position = None
            if x_str and y_str:
                position = (int(x_str), int(y_str))

            mov_values = []
            for entry in self.mov_entries:
                val_str = entry.get().strip()
                mov_values.append(float(val_str) if val_str else 0.0)

            movement_pattern = mov_values if any(mov_values) else None
            
            self.spawner.history = self.history # Ensure spawner is linked
            agent = self.spawner.spawn_randomly(agent_type=agent_type, movement_pattern=movement_pattern, position=position) 
            
            # Add to initial state
            if not self.history.states:
                 self.history.states = [[ag.clone() for ag in self.history.agents]]
            else:
                 self.history.states[0].append(agent.clone())

            messagebox.showinfo("Sucesso", f"Agente {agent.name} adicionado com sucesso!")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar agente:\n{e}")

class SimulationIntervalWindow:
    def __init__(self, root, history):
        self.history = history
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
        start_str = self.start_entry.get().strip()
        end_str = self.end_entry.get().strip()

        if not start_str.isdigit() or not end_str.isdigit():
            messagebox.showerror("Erro", "Preencha os dois campos com números válidos.")
            return

        start = int(start_str)
        end = int(end_str)

        if start > end:
            messagebox.showerror("Erro", "O início não pode ser maior que o fim.")
            return
            
        if end >= len(self.history.states):
            end = len(self.history.states) - 1

        try:
            WorldVisualizer.simulate_interval(self.history, start, end)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a simulação: {e}")