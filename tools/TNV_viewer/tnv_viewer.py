import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def create_tab(tab_name):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_name)

    # Sample Matplotlib chart
    fig = Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(1, 1, 1)
    plot.plot([1, 2, 3, 4], [10, 30, 20, 40])
    plot.set_title(f"Chart in {tab_name}")

    canvas = FigureCanvasTkAgg(fig, master=tab)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # LabelFrame for vertical buttons
    button_frame = ttk.LabelFrame(tab, text="Buttons")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    # Buttons on the right side (vertical)
    button1 = ttk.Button(button_frame, text="Buy 1")
    button1.pack(side=tk.TOP, pady=5)

    button2 = ttk.Button(button_frame, text="Short 1")
    button2.pack(side=tk.TOP, pady=5)

    # button3 = ttk.Button(button_frame, text="Flat 1")
    # button3.pack(side=tk.TOP, pady=5)



root = tk.Tk()
root.title("Tabbed Application")

notebook = ttk.Notebook(root)

# Create 5 tabs
tabs = ["OBQ", "MRQ1", "MRQ2", "Last Minute", "Tab 5"]

for tab_name in tabs:
    create_tab(tab_name)

notebook.pack(expand=True, fill="both")

root.geometry("600x400")
root.mainloop()