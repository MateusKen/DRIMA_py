import tkinter as tk
from tkinter import messagebox
from projeto import FileHandler

root = tk.Tk()

def menu_interface():
    pass

def config_interface():
    data = FileHandler.load_config(path="drima.json")
    entries = {}
    
    root.title("Menu de Opções")
    row = 0
    for key, value in data.items():
        label = tk.Label(root, text=key).grid(row=row, column=0, padx=10, pady=5, sticky="e")

        entry = tk.Entry(root)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, padx=10, pady=5)
        entries[key] = entry

        row += 1
    save_button = tk.Button(root, text="Salvar", command=lambda: on_save_config(entries))
    save_button.grid(row=row, columnspan=2, pady=10)
    root.mainloop()

def on_simulation_button():
    # Aqui você pode chamar sua função real de simulação
    messagebox.showinfo("Simulação", "Simulação em execução...")

def on_show_graphics():
    # Aqui você pode abrir a janela com os gráficos ou gerar visualizações
    messagebox.showinfo("Gráficos", "Gráficos sendo exibidos...")

def on_parameter_conf():
    # Aqui você pode chamar a função ou importar seu editor de configuração
    import subprocess
    subprocess.run(["python", "config_gui_sem_classe.py"])

def on_exit():
    root.destroy()

def on_save_config(data):
    for key, entry in data.items():
        val = entry.get()
        try:
            if "." in val:
                data[key] = float(val)
            else:
                data[key] = int(val)
        except ValueError:
            data[key] = val 
    FileHandler.save_config(data)