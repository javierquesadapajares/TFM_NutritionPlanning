# estilos.py

import tkinter as tk
from tkinter import ttk

icon_img_global = None

def configurar_estilos(root):
    """Configura estilos compartidos para todas las ventanas."""
    
    style = ttk.Style(root)
    style.configure("Small.TLabel", font=("Arial", 12))
    style.configure("Small.TButton", font=("Arial", 12))
    style.configure("Small.TEntry", font=("Arial", 12))
    style.configure("Small.TCombobox", font=("Arial", 12))
    style.configure("Left.TLabelframe", font=("Arial", 12, "bold"), borderwidth=2, relief="groove")
    style.configure("Left.TLabelframe.Label", font=("Arial", 12, "bold"))

    icon_img_global = tk.PhotoImage(file="PROJECT/src/GUI/imagenes/icono_manzana.png")
    root.iconphoto(False, icon_img_global)