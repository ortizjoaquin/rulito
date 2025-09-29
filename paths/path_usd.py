from prices import obtener_precios_criptoya, elegir_mejor_venta, obtener_bancos, mejor_banco_ask
from config import EXCHANGES, BNA_FALLBACK, USD_USDT_FEE
from utils import apply_sell_fee

def flujo_usd():
    try:
        monto_usd = float(input("Ingrese monto en USD: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    # Primero se carga precios de exchanges
    precios = obtener_precios_criptoya(EXCHANGES)

    # USD → USDT
    usdt_obtenidos = monto_usd * (1 - USD_USDT_FEE)
    print(f"[💵] {monto_usd:.2f} USD → {usdt_obtenidos:.2f} USDT (comisión {USD_USDT_FEE*100:.2f}%)")

    # Vender USDT → ARS
    venta = elegir_mejor_venta(precios)
    ars_obtenidos = usdt_obtenidos * venta["bid_neto"]
    print(f"[✅] Venta USDT/ARS: {venta['exchange'].upper():<12} bid={venta['bid_neto']:.2f}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    # Recompro USD vía banco
    precios_bancos = obtener_bancos()
    print("\nPrecios de bancos cargados:")
    for banco, datos in precios_bancos.items():
        bid = datos["bid"] if datos["bid"] else "N/A"
        ask = datos["ask"] if datos["ask"] else "N/A"
        print(f"{banco.upper():<12} bid={bid} ask={ask}")

    mejor_banco = mejor_banco_ask(precios_bancos)
    if mejor_banco is None:
        mejor_banco = {"banco": "bna", "ask": BNA_FALLBACK}

    usd_recomprados = ars_obtenidos / mejor_banco["ask"]
    porcentaje = (usd_recomprados - monto_usd) / monto_usd * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"

    print(f"\n[💰] Mejor banco para recomprar USD: {mejor_banco['banco'].upper()} a ${mejor_banco['ask']:.2f}")
    print(f"USD iniciales: {monto_usd:.2f} | USD recomprados: {usd_recomprados:.2f} | {resultado}: {porcentaje:+.2f}%\n")