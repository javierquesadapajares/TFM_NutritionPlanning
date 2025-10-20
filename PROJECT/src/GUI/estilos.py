# estilos.py - Estilos usados en la aplicación

import tkinter as tk
from tkinter import ttk
from pathlib import Path

icon_img_global = None

def configurar_estilos(root):
    """Configura estilos compartidos para todas las ventanas."""
    global icon_img_global

    style = ttk.Style(root)
    style.configure("Small.TLabel", font=("Arial", 12))
    style.configure("Small.TButton", font=("Arial", 12))
    style.configure("Small.TEntry", font=("Arial", 12))
    style.configure("Small.TCombobox", font=("Arial", 12))
    style.configure("Left.TLabelframe", font=("Arial", 12, "bold"), borderwidth=2, relief="groove")
    style.configure("Left.TLabelframe.Label", font=("Arial", 12, "bold"))

    # Ruta del icono relativa a este archivo: src/GUI/imagenes/icono_manzana.png
    icon_path = Path(__file__).resolve().parent / "imagenes" / "icono_manzana.png"
    try:
        if icon_path.exists():
            icon_img_global = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(False, icon_img_global)  # mantener referencia global para que no se libere
        else:
            # opcional: avisar por consola si no se encuentra
            print(f"[GUI] Icono no encontrado: {icon_path}")
    except Exception as e:
        print(f"[GUI] No se pudo cargar el icono: {e}")
