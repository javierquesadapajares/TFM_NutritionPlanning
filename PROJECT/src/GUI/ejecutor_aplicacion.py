# ejecutor_aplicacion.py - Lanza la aplicación para ejecutar el algoritmo evolutivo

import tkinter as tk
from src.GUI.ventana_principal import MainApp
from src.GUI.estilos import configurar_estilos

def run():
    root = tk.Tk()
    configurar_estilos(root)
    MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    run()