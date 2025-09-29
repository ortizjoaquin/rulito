from prices import obtener_precios_criptoya, elegir_mejor_venta, elegir_mejor_compra, obtener_bancos, mejor_banco_ask
from config import EXCHANGES, BANCOS, BNA_FALLBACK, USD_USDT_FEE
from utils import apply_sell_fee, apply_buy_fee

def flujo_ars():
    try:
        monto_ars = float(input("Ingrese monto en ARS: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    # Obtener bancos antes de los exchanges
    precios_bancos = obtener_bancos()
    print("\nPrecios de bancos cargados:")
    for banco, datos in precios_bancos.items():
        bid = datos["bid"] if datos["bid"] else "N/A"
        ask = datos["ask"] if datos["ask"] else "N/A"
        print(f"{banco.upper():<12} bid={bid} ask={ask}")

    mejor_banco = mejor_banco_ask(precios_bancos)
    if mejor_banco is None:
        mejor_banco = {"banco": "bna", "ask": BNA_FALLBACK}

    # Cargar precios de exchanges
    precios = obtener_precios_criptoya(EXCHANGES)

    # Camino ARS → USD → USDT → ARS
    usd_comprados = monto_ars / mejor_banco["ask"]
    usdt_obtenidos = usd_comprados * (1 - USD_USDT_FEE)
    mejor_venta = elegir_mejor_venta(precios)
    ars_recomprados = usdt_obtenidos * mejor_venta["bid_neto"]

    # Camino ARS → USDT → ARS
    mejor_compra = elegir_mejor_compra(precios)
    usdt_c2 = monto_ars / mejor_compra["ask_neto"]
    ars_recomprados_c2 = usdt_c2 * elegir_mejor_venta(precios)["bid_neto"]

    print(f"\n--- Monto inicial ARS: {monto_ars:.2f} ---")
    print("\nCamino ARS -> USD -> USDT -> ARS:")
    print(f"USD comprados via banco ({mejor_banco['banco'].upper()}, ask={mejor_banco['ask']:.2f}): {usd_comprados:.2f}")
    print(f"USDT obtenidos (USD -> USDT, comisión {USD_USDT_FEE*100:.2f}%): {usdt_obtenidos:.2f}")
    print(f"ARS recomprados vendiendo USDT en {mejor_venta['exchange'].upper()}: {ars_recomprados:.2f}")

    print("\nCamino ARS -> USDT -> ARS:")
    print(f"USDT comprados directo en exchange ({mejor_compra['exchange'].upper()}, ask neto={mejor_compra['ask_neto']:.2f}): {usdt_c2:.2f}")
    print(f"ARS recomprados vendiendo USDT: {ars_recomprados_c2:.2f}")

    # Comparación y porcentaje
    if ars_recomprados >= ars_recomprados_c2:
        mejor_camino = "ARS -> USD -> USDT -> ARS"
        mejor_final = ars_recomprados
    else:
        mejor_camino = "ARS -> USDT -> ARS"
        mejor_final = ars_recomprados_c2

    porcentaje = (mejor_final - monto_ars) / monto_ars * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"
    print(f"\n✅ Mejor camino: {mejor_camino} ({resultado}: {porcentaje:+.2f}%)\n")