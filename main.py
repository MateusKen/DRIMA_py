# main.py
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from project.GraphVisualizer import GraphVisualizer
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import math

# Import refactored classes
from project import (
    History, Agent, AgentSpawner, FileHandler, WorldUpdater
)

class SimulationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.animation_running = False
        self.config = FileHandler.load_config('drima.json')
        self._initialize_history(first_run=True) # Creates the initial agents

        self.configure_window()
        self.create_main_frames()
        self.create_options_layout()
        self.create_functional_layout()

        self._run_full_simulation()
        self.after(100, self.update_simulation_visualization)

    def _initialize_history(self, first_run=False):
        """
        (Re)initializes the history with config parameters.
        Preserves existing agents unless it's the first run.
        """
        current_agents = []
        # Check if history exists and has states before trying to access states[0]
        if not first_run and hasattr(self, 'history') and self.history.states:
            current_agents = [ag.clone() for ag in self.history.states[0]]

        # Load history using the config (which reads Portuguese keys)
        self.history = FileHandler.load_history_from_config('drima.json')
        self.agent_spawner = AgentSpawner(self.history)

        if first_run or not current_agents:
            # Create a default set of agents
            for _ in range(5):
                try: 
                    self.agent_spawner.spawn_randomly()
                except RuntimeError as e: 
                    self.log_message(f"Error spawning agents: {e}", error=True)
                    break
            # Save the initial state
            self.history.states = [[ag.clone() for ag in self.history.agents]]
        else:
            # Restore agents from the previous run
            self.history.agents = current_agents
            self.history.states = [[ag.clone() for ag in current_agents]]

    def _reset_agents_and_history(self):
        """Discards all agents and creates a new random set."""
        self.log_message("Resetting agents to a new default set.")
        self._initialize_history(first_run=True)
        self._run_full_simulation()

    def _run_full_simulation(self):
        """Runs the entire simulation in the background to generate the history."""
        # Ensure we start from the defined initial state
        if not self.history.states:
             self.log_message("Error: Cannot run simulation, no initial state found.", error=True)
             return
             
        self.history.reset_agents_to_initial_state()
        
        # Read config keys (still in Portuguese for compatibility)
        is_synchronous = self.config["modo_da_interacao"] == 0
        iterations = self.config["numero_de_iteracoes"]

        # Create a temporary History object to run the simulation
        temp_history = History(
            self.history.width, self.history.height, 
            self.history.delta_p_det, self.history.delta_p_rand,
            delta_p_mode=self.history.delta_p_mode,
            world_mobility=self.history.world_mobility
        )
        temp_history.agents = [ag.clone() for ag in self.history.states[0]]
        
        num_agents = len(temp_history.agents) or 1
        async_iters = 1
        
        if not is_synchronous:
            try:
                async_iters = int(self.config.get('async_sub_iterations', 1))
            except ValueError:
                async_iters = 1
            
            if async_iters > num_agents: 
                async_iters = num_agents
            if async_iters < 1: 
                async_iters = 1

        # Reset the main history's states, keeping only state 0
        self.history.states = [[ag.clone() for ag in temp_history.agents]]

        # Run the simulation
        for i in range(iterations):
            if is_synchronous:
                # Synchronous update clones and appends its own state
                WorldUpdater.update_synchronously(temp_history)
            else:
                # Asynchronous update clones and appends its own state
                WorldUpdater.update_asynchronously(temp_history, iterations=async_iters)
            
            # Append the *newly created state* from temp_history's list
            self.history.states.append(temp_history.states[-1])

        self.log_message(f"Simulation completed with {len(self.history.states) - 1} steps generated.")
        
        if hasattr(self, 'history_slider'):
            self.history_slider.configure(to=len(self.history.states) - 1)
            self.history_slider.set(0)
            self.update_simulation_visualization(0)

    def configure_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("DRIMA Simulation Interface")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{int(width * 0.85)}x{int(height * 0.85)}+100+50")

    def create_main_frames(self):
        self.functional_frame = ctk.CTkFrame(self, fg_color="#2e3b4e")
        self.functional_frame.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        self.options_frame = ctk.CTkFrame(self, fg_color="#1e2227")
        self.options_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

    def create_options_layout(self):
        self.options_wrapper = ctk.CTkScrollableFrame(self.options_frame, fg_color="transparent", label_text="")
        self.options_wrapper.pack(fill="both", expand=True)

        btn_font = ("Arial", 11)
        btn_height = 24

        # --- Main Controls ---
        controls_frame = ctk.CTkFrame(self.options_wrapper, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.btn_animate = ctk.CTkButton(controls_frame, text="Animate History", height=btn_height, font=btn_font,
                                        fg_color="#27ae60", hover_color="#219150", command=self.toggle_animation)
        self.btn_animate.pack(fill="x", pady=2)

        ctk.CTkButton(controls_frame, text="Load History", height=btn_height,
                      font=btn_font, command=self.load_history_from_file).pack(fill="x", pady=2)

        ctk.CTkButton(controls_frame, text="Export History", height=btn_height,
                      font=btn_font, command=self.save_history_to_file).pack(fill="x", pady=2)

        # --- Agent Management ---
        agents_frame = ctk.CTkFrame(self.options_wrapper, fg_color="#23272e")
        agents_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(agents_frame, text="Agent Management", font=("Arial", 13, "bold")).pack(pady=(5, 10))

        ctk.CTkButton(agents_frame, text="Add Agent", command=self.open_add_agent_window).pack(fill="x",
                                                                                                        padx=10, pady=5)

        remove_frame = ctk.CTkFrame(agents_frame, fg_color="transparent")
        remove_frame.pack(fill="x", padx=10, pady=5)

        self.entry_agent_name = ctk.CTkEntry(remove_frame, placeholder_text="Agent name")
        self.entry_agent_name.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(remove_frame, text="Remove", width=80, command=self.remove_agent).pack(side="left")

        ctk.CTkButton(agents_frame, text="Reset Agents to Default", command=self._reset_agents_and_history,
                      font=btn_font, height=btn_height).pack(fill="x", padx=10, pady=(10, 5))

        # --- World Settings ---
        config_frame = ctk.CTkFrame(self.options_wrapper, fg_color="#23272e")
        config_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(config_frame, text="World Settings", font=("Arial", 13, "bold")).pack(pady=(5, 10))

        # Helper for sliders
        def create_slider_with_entry(parent, text, initial_value, from_=0.0001, to=1.0):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            ctk.CTkLabel(frame, text=text, font=("Arial", 11)).pack(side="left", padx=(0, 10))
            entry = ctk.CTkEntry(frame, width=65)
            entry.pack(side="right")
            slider = ctk.CTkSlider(frame, from_=from_, to=to)
            slider.pack(side="right", fill="x", expand=True, padx=5)
            def update_entry_text(value):
                entry.delete(0, "end")
                entry.insert(0, f"{float(value):.4f}")
            slider.configure(command=update_entry_text)
            slider.set(initial_value)
            update_entry_text(initial_value)
            return slider, entry, frame

        # Helper for simple entry fields
        def create_config_field(parent, text, initial_value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            ctk.CTkLabel(frame, text=text, font=("Arial", 11)).pack(side="left")
            entry = ctk.CTkEntry(frame, width=120)
            entry.insert(0, str(initial_value))
            entry.pack(side="right")
            return entry, frame

        # Delta-P Mode
        frame_dp_mode = ctk.CTkFrame(config_frame, fg_color="transparent")
        frame_dp_mode.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(frame_dp_mode, text="Delta-P Mode", font=("Arial", 11)).pack(side="left")
        default_dp_mode = self.config.get('delta_p_mode', 'Global')
        self.combo_dp_mode = ctk.CTkComboBox(frame_dp_mode, values=["Global", "Local"], width=120,
                                             command=self._toggle_delta_p_visibility)
        self.combo_dp_mode.set(default_dp_mode)
        self.combo_dp_mode.pack(side="right")

        # Delta-P Sliders (created but not packed yet)
        self.slider_d, self.entry_d, self.frame_d_container = create_slider_with_entry(
            config_frame, "delta_p_D", self.config['delta_p_deterministico'])
        
        self.slider_r, self.entry_r, self.frame_r_container = create_slider_with_entry(
            config_frame, "delta_p_R", self.config['delta_p_aleatorio'])

        # Other fields (using Portuguese keys from config)
        self.entry_width, self.frame_width = create_config_field(config_frame, "Grid Width", self.config['largura_da_grade'])
        self.frame_width.pack(fill="x", padx=10, pady=4)

        self.entry_height, self.frame_height = create_config_field(config_frame, "Grid Height", self.config['altura_da_grade'])
        self.frame_height.pack(fill="x", padx=10, pady=4)
        
        self.entry_iterations, self.frame_iterations = create_config_field(config_frame, "No. of Iterations", self.config['numero_de_iteracoes'])
        self.frame_iterations.pack(fill="x", padx=10, pady=4)

        # Interaction Mode
        mode_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(mode_frame, text="Interaction Mode", font=("Arial", 11)).pack(side="left")

        default_async_iters = self.config.get('async_sub_iterations', 1)
        self.entry_async_iter = ctk.CTkEntry(mode_frame, width=50)
        self.entry_async_iter.insert(0, str(default_async_iters))

        self.combo_mode = ctk.CTkComboBox(mode_frame, values=["Synchronous", "Asynchronous"], width=120,
                                            command=self._toggle_async_entry)
        
        initial_mode = "Synchronous" if self.config['modo_da_interacao'] == 0 else "Asynchronous"
        self.combo_mode.set(initial_mode)
        
        # Pack them in correct order
        self._toggle_async_entry(initial_mode) 
        
        # Set initial visibility for Delta-P sliders
        self._toggle_delta_p_visibility(self.combo_dp_mode.get())

        # Save Button
        ctk.CTkButton(config_frame, text="Save and Apply Config", command=self.save_and_apply_config).pack(fill="x",
                                                                                                            padx=10,
                                                                                                            pady=15)

    def create_functional_layout(self):
        small_container = ctk.CTkFrame(self.functional_frame, fg_color="transparent")
        small_container.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.25)

        graph_frame = ctk.CTkFrame(small_container, fg_color="#3e4b5e")
        graph_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
        ctk.CTkButton(graph_frame, text="Show Agent Graph", command=self.open_graph_window).pack(expand=True,padx=10, pady=5)

        logs_outer_frame = ctk.CTkFrame(small_container, fg_color="#4e5b6e")
        logs_outer_frame.pack(side="left", expand=True, fill="both", padx=(5, 0))
        ctk.CTkLabel(logs_outer_frame, text="Logs", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        self.logs_frame = ctk.CTkScrollableFrame(logs_outer_frame, fg_color="#232b38")
        self.logs_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        def update_label_wraps(event):
            padding = 30
            new_width = event.width - padding
            if new_width < 100: new_width = 100
            for child in self.logs_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(wraplength=new_width)
        self.logs_frame.bind("<Configure>", update_label_wraps)
        self.log_message("Interface initiated.")

        self.create_simulation_frame()

    def _toggle_delta_p_visibility(self, choice):
        """Shows or hides the global delta_p sliders based on mode."""
        self.frame_d_container.pack_forget()
        self.frame_r_container.pack_forget()

        if choice == "Global":
            # Re-pack the sliders in the correct order
            self.frame_r_container.pack(fill="x", pady=5, padx=10, before=self.frame_width)
            self.frame_d_container.pack(fill="x", pady=5, padx=10, before=self.frame_r_container)

    def _toggle_async_entry(self, choice):
        """Shows or hides the async iterations entry box."""
        self.entry_async_iter.pack_forget()
        self.combo_mode.pack_forget()
        
        if choice == "Asynchronous":
            self.entry_async_iter.pack(side="right", padx=(5, 0))
            self.combo_mode.pack(side="right")
        else:
            self.combo_mode.pack(side="right")

    def create_simulation_frame(self):
        self.simulation_frame = ctk.CTkFrame(self.functional_frame, fg_color="transparent")
        self.simulation_frame.place(relx=0.02, rely=0.30, relwidth=0.96, relheight=0.68)

        self.sim_figure = Figure(dpi=100, facecolor="#2e3b4e")
        self.sim_ax = self.sim_figure.add_subplot(111)
        self.sim_figure.tight_layout()

        self.sim_canvas = FigureCanvasTkAgg(self.sim_figure, master=self.simulation_frame)
        self.sim_canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)

        history_controls_frame = ctk.CTkFrame(self.simulation_frame, fg_color="transparent")
        history_controls_frame.pack(fill="x", padx=5, pady=5)

        self.history_label_title = ctk.CTkLabel(history_controls_frame, text="History:", font=("Arial", 14))
        self.history_label_title.pack(side="left", padx=5)

        self.history_slider = ctk.CTkSlider(history_controls_frame, from_=0, to=1,
                                             command=self.update_view_from_slider)
        self.history_slider.pack(side="left", fill="x", expand=True)

        self.history_entry = ctk.CTkEntry(history_controls_frame, width=60)
        self.history_entry.pack(side="left", padx=5)
        self.history_entry.bind("<Return>", self.update_view_from_entry)

        self.history_label_value = ctk.CTkLabel(history_controls_frame, text="/ 0", font=("Arial", 14), width=50)
        self.history_label_value.pack(side="left", padx=5)

    def save_and_apply_config(self):
        try:
            # Save config data using Portuguese keys for compatibility
            self.config['largura_da_grade'] = int(self.entry_width.get())
            self.config['altura_da_grade'] = int(self.entry_height.get())
            self.config['numero_de_iteracoes'] = int(self.entry_iterations.get())
            self.config['delta_p_deterministico'] = float(self.entry_d.get())
            self.config['delta_p_aleatorio'] = float(self.entry_r.get())
            
            is_sync = self.combo_mode.get() == "Synchronous"
            self.config['modo_da_interacao'] = 0 if is_sync else 1
            self.config['async_sub_iterations'] = int(self.entry_async_iter.get())
            self.config['delta_p_mode'] = self.combo_dp_mode.get()

            FileHandler.save_config(self.config, 'drima.json')
            self.log_message("Config saved. Recalculating simulation with current agents.")

            # Re-initialize the history, preserving current agents
            self._initialize_history(first_run=False)
            # Re-run the simulation to generate new states
            self._run_full_simulation()

        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid value. Please check all fields.\nDetail: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving:\n{e}")

    # --- THIS IS THE FULLY IMPLEMENTED METHOD ---
    def open_add_agent_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Agent")
        popup.geometry("400x600")
        popup.grab_set()

        top_frame = ctk.CTkFrame(popup, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=10)

        top_row_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        top_row_frame.pack(fill="x")

        type_frame = ctk.CTkFrame(top_row_frame, fg_color="transparent")
        type_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(type_frame, text="Agent Type", font=("Arial", 12, "bold")).pack()
        type_var = ctk.StringVar(value="R")
        ctk.CTkRadioButton(type_frame, text="Random (R)", variable=type_var, value="R").pack(anchor="w", padx=10)
        ctk.CTkRadioButton(type_frame, text="Deterministic (D)", variable=type_var, value="D").pack(anchor="w", padx=10)

        pos_frame = ctk.CTkFrame(top_row_frame, fg_color="transparent")
        pos_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(pos_frame, text="Position (X, Y)", font=("Arial", 12, "bold")).pack()
        pos_entries_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        pos_entries_frame.pack(pady=5)
        entry_x = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="X")
        entry_x.pack(side="left", padx=5)
        entry_y = ctk.CTkEntry(pos_entries_frame, width=60, placeholder_text="Y")
        entry_y.pack(side="left", padx=5)
        ctk.CTkLabel(pos_frame, text="(Optional)", font=("Arial", 9)).pack()

        delta_p_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        delta_p_frame.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(delta_p_frame, text="Influence (Δp)", font=("Arial", 12, "bold")).pack()
        entry_delta_p = ctk.CTkEntry(delta_p_frame, width=100, placeholder_text="e.g., 0.1 (Optional)")
        entry_delta_p.pack(pady=5)

        ctk.CTkLabel(popup, text="Actions by Direction", font=("Arial", 12, "bold")).pack(pady=(15, 5))

        directions_frame = ctk.CTkFrame(popup, fg_color="transparent")
        directions_frame.pack(pady=5)

        grid_layout = [
            ("NW", 0, 0), ("N", 0, 1), ("NE", 0, 2),
            ("W", 1, 0), ("X", 1, 1), ("E", 1, 2),
            ("SW", 2, 0), ("S", 2, 1), ("SE", 2, 2)
        ]

        direction_entries = {}
        default_prob = f"{1 / 9:.4f}"

        for direction, row, col in grid_layout:
            label = ctk.CTkLabel(directions_frame, text=direction, width=60)
            label.grid(row=row * 2, column=col, padx=5, pady=(5, 0))
            entry = ctk.CTkEntry(directions_frame, width=60, justify="center")
            entry.insert(0, default_prob)
            entry.grid(row=row * 2 + 1, column=col, padx=5)
            direction_entries[direction] = entry

        def update_fields_x():
            if not toggle_x_var.get(): # If "Allow X" is UNCHECKED
                direction_entries["X"].configure(state="normal")
                direction_entries["X"].delete(0, "end")
                direction_entries["X"].insert(0, "0.0000")
                direction_entries["X"].configure(state="disabled")
                prob = 1.0 / 8
                for direction, entry in direction_entries.items():
                    if direction != "X":
                        entry.delete(0, "end")
                        entry.insert(0, f"{prob:.4f}")
            else: # If "Allow X" is CHECKED
                direction_entries["X"].configure(state="normal")
                direction_entries["X"].delete(0, "end")
                direction_entries["X"].insert(0, f"{1 / 9:.4f}")
                prob = 1.0 / 9
                for direction, entry in direction_entries.items():
                    if direction != "X":
                        entry.delete(0, "end")
                        entry.insert(0, f"{prob:.4f}")

        toggle_x_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            popup,
            text="Allow movement in X (stay in place)",
            variable=toggle_x_var,
            command=update_fields_x
        ).pack(pady=(5, 10))

        # Run once to set the "X" state based on the default (True)
        # This seems redundant as the default is 1/9, but it's good practice
        # update_fields_x() # Actually not needed, default is correct

        def _create_agent_final(grid_values, agent_type, pos, delta_p_val):
            # Helper to create agent after all validation
            movement_pattern = [
                grid_values['E'], grid_values['NE'], grid_values['N'], grid_values['NW'],
                grid_values['W'], grid_values['SW'], grid_values['S'], grid_values['SE'],
                grid_values['X']
            ]
            
            # Use the spawner to create agent
            new_agent = self.agent_spawner.spawn_randomly(
                agent_type=agent_type, position=pos, movement_pattern=movement_pattern, delta_p=delta_p_val
            )
            
            # Add the new agent to the *initial state* (state 0)
            if not self.history.states: # Ensure state 0 exists
                 self.history.states = [[ag.clone() for ag in self.history.agents]]
            else:
                 self.history.states[0].append(new_agent.clone())

            self.log_message(f"Agent '{new_agent.name}' added. Recalculating history...")
            self._run_full_simulation()
            popup.destroy()

        def add_agent_logic():
            try:
                agent_type = type_var.get()
                pos = None
                if entry_x.get() and entry_y.get():
                    pos = (int(entry_x.get()), int(entry_y.get()))

                delta_p_str = entry_delta_p.get().strip()
                delta_p_val = None
                if delta_p_str:
                    delta_p_val = float(delta_p_str)

                grid_values = {direction: float(entry.get()) for direction, entry in direction_entries.items()}
                
                if not toggle_x_var.get():
                    grid_values["X"] = 0.0
                
                soma = sum(grid_values.values())
                TOLERANCE = 1e-6

                if soma > 1.0 + TOLERANCE:
                    messagebox.showerror("Validation Error",
                                         f"The sum of probabilities cannot be greater than 1.0 (current sum: {soma:.4f}).",
                                         parent=popup)
                    return

                if agent_type == 'D':
                    ones = sum(1 for v in grid_values.values() if math.isclose(v, 1.0))
                    zeros = sum(1 for v in grid_values.values() if math.isclose(v, 0.0))
                    expected_zeros = 8 if toggle_x_var.get() else 9
                    if not (ones == 1 and zeros == 8):
                         # Rerun check for no-X case
                         if not toggle_x_var.get():
                             zeros = sum(1 for v in grid_values.values() if math.isclose(v, 0.0))
                             if not (ones == 1 and zeros == 8): # Still 8, because X is 0.0
                                 messagebox.showerror("Validation Error",
                                             "For Deterministic agents, one direction must be 1.0 and all others 0.0.",
                                             parent=popup)
                                 return
                         else:
                             messagebox.showerror("Validation Error",
                                             "For Deterministic agents, one direction must be 1.0 and all others 0.0.",
                                             parent=popup)
                             return


                if math.isclose(soma, 1.0, rel_tol=TOLERANCE):
                    _create_agent_final(grid_values, agent_type, pos, delta_p_val)
                else:
                    # Ask to normalize
                    if messagebox.askyesno("Confirm Normalization", 
                                             f"The sum of probabilities is {soma:.4f}.\nDo you want to normalize the values to sum 1.0?",
                                             parent=popup):
                        normalized_values = {k: v / soma for k, v in grid_values.items()}
                        _create_agent_final(normalized_values, agent_type, pos, delta_p_val)
                    else:
                        return # User chose to fix manually

            except ValueError:
                messagebox.showerror("Error", "Position, delta_p, and movement values must be valid numbers.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add agent:\n{e}", parent=popup)

        buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=20)
        ctk.CTkButton(buttons_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)
        ctk.CTkButton(buttons_frame, text="Add", command=add_agent_logic).pack(side="right", padx=5)
    # --- END OF open_add_agent_window ---

    def remove_agent(self):
        agent_name = self.entry_agent_name.get()
        if not agent_name:
            self.log_message("ERROR: Please enter an agent name to remove.", error=True)
            return
            
        # Find in the *current* agent list first
        agent_to_remove = self.history.find_agent_by_name(agent_name)

        if agent_to_remove:
            self.history.remove_agent(agent_name) # This removes from self.agents and all states
            self.log_message(f"Agent '{agent_name}' removed. Recalculating history...")
            self._run_full_simulation() # Rerun simulation with the agent removed from state 0
            self.entry_agent_name.delete(0, "end")
        else:
            self.log_message(f"ERROR: Agent '{agent_name}' not found.", error=True)

    def toggle_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.btn_animate.configure(text="Stop Animation", fg_color="#e74c3c", hover_color="#b93222")
            self.animate_step()
        else:
            self.animation_running = False
            self.btn_animate.configure(text="Animate History", fg_color="#27ae60", hover_color="#219150")

    def animate_step(self):
        if not self.animation_running: 
            return

        current_frame = int(self.history_slider.get())
        total_frames = len(self.history.states) - 1

        if current_frame < total_frames:
            next_frame = current_frame + 1
            self.history_slider.set(next_frame)
            self.update_view_from_slider(next_frame)
            self.after(200, self.animate_step) # Adjust speed here
        else:
            self.toggle_animation()

    def load_history_from_file(self):
        path = filedialog.askopenfilename(defaultextension=".gz", filetypes=[("JSON, Gzip files", "*.json *.gz"),
                                                                            ("Gzip files", "*.gz"),
                                                                            ("All files", "*.*")])
        if not path: 
            return
        
        try:
            root, ext = os.path.splitext(path)
            data = None 
            
            if ext == '.json':
                # This seems to be a config-only file, like conf_0.json
                self.config = FileHandler.load_config(path)
                self.log_message(f"Config-only file loaded: {path.split('/')[-1]}")
                self.log_message("Applying config and resetting agents.")
                FileHandler.save_config(self.config, 'drima.json') # Save as current config
                self._initialize_history(first_run=True) # Reset with new config
                self._run_full_simulation() # Run simulation
                
            elif ext == '.gz':
                # This is a full history save file, like conf_coca_pepsi2.gz
                data = FileHandler.load_history_json_gzipped(path)
                self.config = data["config"]
                FileHandler.save_config(self.config, 'drima.json')
                
                # Re-initialize the history object with the loaded config
                # This sets up width, height, etc.
                self._initialize_history(first_run=False) 

                # Reconstruct the states
                self.history.states = []
                for frame_data in data["states"]:
                    state = []
                    for a in frame_data:
                        # ** COMPATIBILITY LOGIC **
                        # Try new English keys, fallback to old Portuguese keys
                        agent = Agent(
                            name=a.get("name", a.get("nome")),
                            agent_type=a.get("type", a.get("tipo")),
                            movement_pattern=a.get("movement_pattern", a.get("padrao_movimento")),
                            position=tuple(a.get("position", a.get("posicao"))),
                            delta_p=a.get("delta_p", 0.1) # delta_p was consistent
                        )
                        state.append(agent)
                    self.history.states.append(state)

                if not self.history.states:
                    self.log_message("ERROR: Loaded file contains no states.", error=True)
                    self._initialize_history(first_run=True)
                    self._run_full_simulation()
                    return

                # Set current agents to match the loaded initial state
                self.history.agents = [ag.clone() for ag in self.history.states[0]]
                self.log_message(f"History file loaded: {path.split('/')[-1]}")
                
            else:
                self.log_message(f"ERROR: Unsupported file format: {ext}", error=True)
                return

            # --- UPDATE UI WITH LOADED CONFIG ---
            # (Uses Portuguese keys for compatibility)
            self.entry_d.delete(0, 'end')
            self.entry_d.insert(0, f"{self.config['delta_p_deterministico']:.4f}")
            self.entry_r.delete(0, 'end')
            self.entry_r.insert(0, f"{self.config['delta_p_aleatorio']:.4f}")
            self.slider_d.set(self.config['delta_p_deterministico'])
            self.slider_r.set(self.config['delta_p_aleatorio'])
            
            self.entry_width.delete(0, 'end')
            self.entry_width.insert(0, self.config['largura_da_grade'])
            self.entry_height.delete(0, 'end')
            self.entry_height.insert(0, self.config['altura_da_grade'])
            self.entry_iterations.delete(0, 'end')
            self.entry_iterations.insert(0, self.config['numero_de_iteracoes'])
            
            current_mode = "Synchronous" if self.config['modo_da_interacao'] == 0 else "Asynchronous"
            self.combo_mode.set(current_mode)

            default_async_iters = self.config.get('async_sub_iterations', 1)
            self.entry_async_iter.delete(0, 'end')
            self.entry_async_iter.insert(0, str(default_async_iters))
            self._toggle_async_entry(current_mode)

            default_dp_mode = self.config.get('delta_p_mode', 'Global')
            self.combo_dp_mode.set(default_dp_mode)
            self._toggle_delta_p_visibility(default_dp_mode)

            # Update slider and visualization
            if hasattr(self, 'history_slider'):
                total_frames = len(self.history.states) - 1
                if total_frames < 0: 
                    total_frames = 0
                
                self.history_slider.configure(to=total_frames)
                self.history_slider.set(0)
                self.update_simulation_visualization(0)

        except Exception as e:
            self.log_message(f"ERROR loading file: {e}", error=True)
            import traceback
            traceback.print_exc()

    def save_history_to_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".gz",
                                            filetypes=[("Gzip files", ".gz"),
                                                     ("All files", ".*")])
        if not path: 
            return
        
        try:
            # Use the refactored function (saves with English keys)
            FileHandler.save_history_json_gzipped(self.history, self.config, path)
            self.log_message(f"History saved to: {path.split('/')[-1]}")
        except Exception as e:
            self.log_message(f"ERROR saving file: {e}", error=True)

    def open_graph_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Advanced Graph Filter")
        popup.geometry("600x450")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select agents:", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        if not self.history.agents:
             self.log_message("No agents to display.", error=True)
             popup.destroy()
             return
             
        agent_names = [agent.name for agent in self.history.agents]
        agent_vars = {name: ctk.BooleanVar(value=False) for name in agent_names}
        
        # --- Dropdown Selector Logic ---
        dropdown_frame = ctk.CTkFrame(popup, fg_color="transparent")
        dropdown_frame.pack(padx=15, pady=10, fill="x")
        
        btn_selecao = ctk.CTkButton(dropdown_frame, text="None selected")
        btn_selecao.pack(fill="x")
        
        dropdown_open = [False]
        dropdown_window = [None] 

        def update_button_text():
            selected = [name for name, var in agent_vars.items() if var.get()]
            text = ", ".join(selected) if selected else "None selected"
            if len(text) > 70: # Truncate if too long
                text = f"{len(selected)} agents selected"
            btn_selecao.configure(text=text)

        def close_dropdown(event=None):
            if dropdown_open[0] and dropdown_window[0] is not None:
                dropdown_window[0].destroy()
                dropdown_open[0] = False
                dropdown_window[0] = None

        def open_dropdown(event=None):
            if dropdown_open[0]:
                close_dropdown()
                return
                
            dropdown_open[0] = True
            x = btn_selecao.winfo_rootx()
            y = btn_selecao.winfo_rooty() + btn_selecao.winfo_height()
            
            dw = ctk.CTkToplevel(popup, fg_color="#222e3c")
            dropdown_window[0] = dw # Store reference
            dw.overrideredirect(True)
            dw.geometry(f"250x300+{x}+{y}")
            
            frame = ctk.CTkScrollableFrame(dw, fg_color="transparent", height=220)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            for name in agent_names:
                cb = ctk.CTkCheckBox(frame, text=name, variable=agent_vars[name],
                                     command=update_button_text)
                cb.pack(anchor="w", padx=5, pady=2)
                
            ctk.CTkButton(dw, text="OK", command=close_dropdown).pack(pady=10)
            dw.bind("<FocusOut>", close_dropdown)
            dw.focus_set()
            
        btn_selecao.configure(command=open_dropdown)
        # --- End Dropdown Logic ---

        frame_history = ctk.CTkFrame(popup, fg_color="transparent")
        frame_history.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(frame_history, text="History Range:", font=("Arial", 12)).pack(side="left")
        entry_start_frame = ctk.CTkEntry(frame_history, width=70, placeholder_text="Start")
        entry_start_frame.insert(0, "0")
        entry_start_frame.pack(side="left", padx=5)
        ctk.CTkLabel(frame_history, text="to").pack(side="left")
        entry_end_frame = ctk.CTkEntry(frame_history, width=70, placeholder_text="End")
        entry_end_frame.insert(0, str(len(self.history.states) - 1))
        entry_end_frame.pack(side="left", padx=5)

        ctk.CTkLabel(popup, text="Directions to Display:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        frame_directions = ctk.CTkFrame(popup, fg_color="transparent")
        frame_directions.pack(fill="x", padx=15)

        grid_layout = [
            ("NW", 0, 0), ("N", 0, 1), ("NE", 0, 2),
            ("W", 1, 0), ("X", 1, 1), ("E", 1, 2),
            ("SW", 2, 0), ("S", 2, 1), ("SE", 2, 2)
        ]
        direction_vars = {}
        for direction, row, col in grid_layout:
            var = ctk.IntVar(value=1)
            cb = ctk.CTkCheckBox(frame_directions, text=direction, variable=var, onvalue=1, offvalue=0)
            cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            direction_vars[direction] = var

        def generate_graph():
            selected_names = [name for name, var in agent_vars.items() if var.get()]
            if not selected_names:
                self.log_message("ERROR: Please select at least one agent.", error=True)
                return
            try:
                start = int(entry_start_frame.get()) if entry_start_frame.get() else 0
                end = int(entry_end_frame.get()) if entry_end_frame.get() else len(self.history.states) - 1
            except ValueError:
                self.log_message("ERROR: Invalid interval.", error=True)
                return
            
            title = "Movement Pattern Graph"
            agent_filter_func = lambda idx, ag: ag.name in selected_names
            directions_selected = {k: v.get() for k, v in direction_vars.items()}

            popup.destroy()

            graph_window = ctk.CTkToplevel(self)
            graph_window.title(title)
            graph_window.geometry("900x600")
            graph_window.grab_set()
            
            graph_frame = ctk.CTkScrollableFrame(graph_window)
            graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            from PIL import ImageTk
            try:
                images = GraphVisualizer.show_images(
                    self.history, # Pass the history object
                    agent_filter=agent_filter_func,
                    interval=(start, end),
                    title=title,
                    directions=directions_selected
                )

                for img in images:
                    photo = ImageTk.PhotoImage(img)
                    label = ctk.CTkLabel(graph_frame, image=photo, text="")
                    label.image = photo # Keep a reference
                    label.pack(pady=10)
            except Exception as e:
                self.log_message(f"Error generating graph images: {e}", error=True)
                graph_window.destroy()
                messagebox.showerror("Graph Error", f"Could not generate graphs:\n{e}")
            
            # ... (rest of export logic) ...
            pass

        ctk.CTkButton(popup, text="Generate Graph", command=generate_graph).pack(pady=15)

    def update_view_from_slider(self, value):
        frame_idx = int(value)
        self.update_simulation_visualization(frame_idx)

    def update_view_from_entry(self, event=None):
        try:
            frame_idx = int(self.history_entry.get())
            max_frame = len(self.history.states) - 1
            if 0 <= frame_idx <= max_frame:
                self.history_slider.set(frame_idx)
                self.update_simulation_visualization(frame_idx)
            else:
                # Revert to current slider value if invalid
                current_value = int(self.history_slider.get())
                self.history_entry.delete(0, "end")
                self.history_entry.insert(0, str(current_value))
        except (ValueError, IndexError):
            # Revert if not a number
            current_value = int(self.history_slider.get())
            self.history_entry.delete(0, "end")
            self.history_entry.insert(0, str(current_value))

    def update_simulation_visualization(self, frame_idx=0):
        self.sim_ax.clear()

        width = self.history.width
        height = self.history.height

        # Draw grid
        for x in range(width):
            for y in range(height):
                self.sim_ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black', lw=0.5))

        # Draw agents from the specified frame
        if frame_idx < len(self.history.states):
            agents_in_frame = self.history.states[frame_idx]
            for agent in agents_in_frame:
                x, y = agent.position
                color = 'red' if agent.type == 'D' else 'blue'
                self.sim_ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=color, edgecolor='black', lw=0.5))
                self.sim_ax.text(x + 0.5, y + 0.5, agent.name, color='white', ha='center', va='center', fontsize=8, weight='bold')

        self.sim_ax.set_xlim(0, width)
        self.sim_ax.set_ylim(0, height)
        self.sim_ax.set_aspect('equal')
        self.sim_ax.invert_yaxis()
        self.sim_ax.axis('off')

        self.sim_canvas.draw()

        # Update slider/entry text
        total_history = len(self.history.states) - 1
        self.history_entry.delete(0, "end")
        self.history_entry.insert(0, str(frame_idx))
        self.history_label_value.configure(text=f"/ {total_history}")

    def log_message(self, message, error=False):
        color = "#e74c3c" if error else "white"
        try:
            padding = 30
            current_width = self.logs_frame.winfo_width() - padding
            if current_width < 100: current_width = 300
        except:
            # Fallback if window not rendered yet
            current_width = 300
            
        label = ctk.CTkLabel(self.logs_frame, text=f"> {message}",
                             text_color=color,
                             font=("Consolas", 10),
                             wraplength=current_width,
                             justify="left")
        label.pack(anchor="w", padx=5, pady=2, fill="x")

if __name__ == "__main__":
    # Ensure the 'project' directory is discoverable
    # This main.py should be in the root, and the other files in a 'project' subfolder.
    import sys
    sys.path.append(os.path.dirname(__file__)) # Add root to path
    
    app = SimulationApp()
    app.mainloop()