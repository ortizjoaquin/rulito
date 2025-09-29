from prices import obtener_precios_criptoya, elegir_mejor_venta, elegir_mejor_compra
from config import EXCHANGES
from utils import apply_sell_fee, apply_buy_fee

def flujo_usdt():
    try:
        monto_usdt = float(input("Ingrese monto en USDT: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    # Primero se carga precios de exchanges
    precios = obtener_precios_criptoya(EXCHANGES)

    # Vender USDT → ARS
    venta = elegir_mejor_venta(precios)
    ars_obtenidos = monto_usdt * venta["bid_neto"]
    print(f"[✅] Venta USDT/ARS: {venta['exchange'].upper():<12} bid={venta['bid_neto']:.2f}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    # Recompro USDT en exchange con mejor ask
    mejor_compra = elegir_mejor_compra(precios)
    usdt_recomprados = ars_obtenidos / mejor_compra["ask_neto"]

    porcentaje = (usdt_recomprados - monto_usdt) / monto_usdt * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"

    print(f"[✅] Recompra USDT en {mejor_compra['exchange'].upper()}: ${mejor_compra['ask_neto']:.2f}")
    print(f"USDT iniciales: {monto_usdt:.2f} | USDT recomprados: {usdt_recomprados:.6f} | {resultado}: {porcentaje:+.2f}%\n")