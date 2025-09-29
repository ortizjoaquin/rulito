import tkinter as tk
from paths.path_ars import flujo_ars
from paths.path_usd import flujo_usd
from paths.path_usdt import flujo_usdt

def mostrar_resultado(resultado):
    if isinstance(resultado, str):
        return resultado
    return f"""
Camino: {resultado['camino']}
ARS final: {resultado['ars_final']:.2f}
Resultado: {resultado['porcentaje']:+.2f}%
"""

def calcular():
    monto = float(entry_monto.get())
    opcion = var_opcion.get()

    if opcion == "ARS":
        resultado = flujo_ars(monto)
    elif opcion == "USD":
        resultado = flujo_usd(monto)
    else:
        resultado = flujo_usdt(monto)

    label_resultado.config(text=mostrar_resultado(resultado))

def iniciar_gui():
    global entry_monto, var_opcion, label_resultado
    root = tk.Tk()
    root.title("Rulito v1.0")

    tk.Label(root, text="Monto inicial:").pack()
    entry_monto = tk.Entry(root)
    entry_monto.pack()

    var_opcion = tk.StringVar(value="ARS")
    tk.Radiobutton(root, text="ARS", variable=var_opcion, value="ARS").pack()
    tk.Radiobutton(root, text="USD", variable=var_opcion, value="USD").pack()
    tk.Radiobutton(root, text="USDT", variable=var_opcion, value="USDT").pack()

    tk.Button(root, text="Calcular", command=calcular).pack()

    label_resultado = tk.Label(root, text="", justify="left")
    label_resultado.pack()

    root.mainloop()