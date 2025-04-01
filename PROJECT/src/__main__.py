#__main__.py

import sys
import os
import tkinter as tk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.GUI.ventana_principal import MainApp
from src.GUI.estilos import configurar_estilos

# Lanza la aplicacion
if __name__ == "__main__":
    root = tk.Tk()

    configurar_estilos(root)

    app = MainApp(root)
    root.mainloop()