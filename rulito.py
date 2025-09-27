#!/usr/bin/env python3
# rulito.py - versión completa 1.0 con comisiones aplicadas y salida estética

import requests

# ------------------------
# CONFIGURACIÓN
# ------------------------
SELL_FEES = {
    "belo": 0.0,
    "binance": 0.01,
    "satoshitango": 0.01,
    "letsbit": 0.0,
    "lemoncash": 0.005,
    "buenbit": 0.0,
    "fiwind": 0.0,
    "ripio": 0.005,
    "binancep2p": 0.0,
    "bybitp2p": 0.0,
    "okexp2p": 0.0,
}

BUY_FEES = {
    "belo": 0.0,
    "binance": 0.0,
    "satoshitango": 0.01,
    "letsbit": 0.0,
    "lemoncash": 0.01,
    "buenbit": 0.0,
    "fiwind": 0.0,
    "ripio": 0.005,
    "binancep2p": 0.0,
    "bybitp2p": 0.0,
    "okexp2p": 0.0,
}

EXCHANGES = ["belo", "binance", "satoshitango", "letsbit", "lemoncash",
             "buenbit", "fiwind", "ripio", "binancep2p", "bybitp2p", "okexp2p"]

BANCOS = ["bna", "rebanking", "santander", "galicia", "bbva",
          "patagonia", "macro", "hsbc", "brubank", "supervielle", "icbc"]

BNA_FALLBACK = 1380.0
FALLBACK_BID = 1450.0
FALLBACK_ASK = 1450.0

USD_USDT_FEE = 0.04  # Comisión global USD→USDT

# ------------------------
# UTILIDADES
# ------------------------
def format_exchange_text(exchange: str, precio: float, comision: float) -> str:
    return f"{exchange.upper():<12} ${precio:,.2f}" + (f" (comisión {comision*100:.2f}%)" if comision > 0 else "")

def apply_sell_fee(exchange: str, bid: float) -> float:
    return bid * (1 - SELL_FEES.get(exchange.lower(), 0.0))

def apply_buy_fee(exchange: str, ask: float) -> float:
    return ask * (1 + BUY_FEES.get(exchange.lower(), 0.0))

def obtener_precios_criptoya(exchanges):
    precios = []
    print("\nObteniendo precios de exchanges...\n")
    for ex in exchanges:
        try:
            url = f"https://criptoya.com/api/{ex}/USDT/ARS/1"
            r = requests.get(url, timeout=6)
            data = r.json()
            bid = float(data.get("bid", FALLBACK_BID))
            ask = float(data.get("ask", FALLBACK_ASK))
            precios.append({"exchange": ex, "bid": bid, "ask": ask})
            print(f"[✅] {ex.upper():<12} bid={bid:,.2f} ask={ask:,.2f}")
        except:
            precios.append({"exchange": ex, "bid": FALLBACK_BID, "ask": FALLBACK_ASK})
            print(f"[❌] {ex.upper():<12} usando fallback {FALLBACK_BID}/{FALLBACK_ASK}")
    print("\nTodos los precios cargados.\n")
    return precios

def elegir_mejor_venta(precios):
    mejor = max(precios, key=lambda x: apply_sell_fee(x["exchange"], x["bid"]))
    mejor["bid_neto"] = apply_sell_fee(mejor["exchange"], mejor["bid"])
    return mejor

def elegir_mejor_compra(precios):
    mejor = min(precios, key=lambda x: apply_buy_fee(x["exchange"], x["ask"]))
    mejor["ask_neto"] = apply_buy_fee(mejor["exchange"], mejor["ask"])
    return mejor

def obtener_bancos():
    try:
        r = requests.get("https://criptoya.com/api/bancostodos", timeout=6)
        data = r.json()
        bancos_filtrados = {}
        for banco in BANCOS:
            if banco in data:
                bancos_filtrados[banco] = {"bid": data[banco].get("bid"), "ask": data[banco].get("ask")}
        return bancos_filtrados
    except:
        return {"bna": {"bid": None, "ask": BNA_FALLBACK}}

def mejor_banco_ask(precios_bancos):
    mejor = None
    for banco, datos in precios_bancos.items():
        if datos["ask"] is None:
            continue
        if (mejor is None) or (datos["ask"] < mejor["ask"]):
            mejor = {"banco": banco, "ask": datos["ask"]}
    return mejor

# ------------------------
# FLUJOS
# ------------------------
def flujo_usd(precios):
    try:
        monto_usd = float(input("Ingrese monto en USD: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    usdt_obtenidos = monto_usd * (1 - USD_USDT_FEE)
    print(f"\n[💵] {monto_usd:.2f} USD → {usdt_obtenidos:.2f} USDT (comisión {USD_USDT_FEE*100:.2f}%)")

    venta = elegir_mejor_venta(precios)
    ars_obtenidos = usdt_obtenidos * venta["bid_neto"]
    print(f"[✅] Venta USDT/ARS: {format_exchange_text(venta['exchange'], venta['bid_neto'], SELL_FEES[venta['exchange']])}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    precios_bancos = obtener_bancos()
    mejor = mejor_banco_ask(precios_bancos)
    usd_recomprados = ars_obtenidos / (mejor["ask"] if mejor else BNA_FALLBACK)
    print(f"\n[💰] Mejor banco para recomprar USD: {mejor['banco'].upper() if mejor else 'BNA'} a ${mejor['ask'] if mejor else BNA_FALLBACK:.2f}")

    porcentaje = (usd_recomprados - monto_usd) / monto_usd * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"
    print(f"USD iniciales: {monto_usd:.2f} | USD recomprados: {usd_recomprados:.2f} | {resultado}: {porcentaje:+.2f}%\n")

def flujo_usdt(precios):
    try:
        monto_usdt = float(input("Ingrese monto en USDT: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    venta = elegir_mejor_venta(precios)
    ars_obtenidos = monto_usdt * venta["bid_neto"]
    print(f"\n[✅] Venta USDT/ARS: {format_exchange_text(venta['exchange'], venta['bid_neto'], SELL_FEES[venta['exchange']])}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    compra = elegir_mejor_compra(precios)
    usdt_recomprados = ars_obtenidos / compra["ask_neto"]
    print(f"[✅] Recompra USDT: {format_exchange_text(compra['exchange'], compra['ask_neto'], BUY_FEES[compra['exchange']])}")

    porcentaje = (usdt_recomprados - monto_usdt) / monto_usdt * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"
    print(f"USDT iniciales: {monto_usdt:.2f} | USDT recomprados: {usdt_recomprados:.6f} | {resultado}: {porcentaje:+.2f}%\n")

def flujo_ars(precios):
    try:
        monto_ars = float(input("Ingrese monto en ARS: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    # --- Obtener bancos ---
    precios_bancos = obtener_bancos()
    if not precios_bancos:
        precios_bancos = {"bna": {"bid": None, "ask": BNA_FALLBACK}}

    print("\nPrecios de bancos cargados:")
    for banco, datos in precios_bancos.items():
        ask = datos["ask"] if datos["ask"] is not None else "N/A"
        bid = datos["bid"] if datos["bid"] is not None else "N/A"
        print(f"{banco.upper():<12} bid={bid} ask={ask}")

    mejor_banco = mejor_banco_ask(precios_bancos)
    if mejor_banco is None:
        mejor_banco = {"banco": "bna", "ask": BNA_FALLBACK}

    # --- Camino 1: ARS -> USD -> USDT -> ARS ---
    usd_comprados = monto_ars / mejor_banco["ask"]
    usdt_obtenidos = usd_comprados * (1 - USD_USDT_FEE)

    mejor_venta = elegir_mejor_venta(precios)
    ars_recomprados = usdt_obtenidos * mejor_venta["bid_neto"]

    print(f"\n--- Monto inicial ARS: {monto_ars:.2f} ---")
    print("\nCamino ARS -> USD -> USDT -> ARS:")
    print(f"USD comprados via banco ({mejor_banco['banco'].upper()}, ask={mejor_banco['ask']:.2f}): {usd_comprados:.2f}")
    print(f"USDT obtenidos (USD -> USDT, comisión {USD_USDT_FEE*100:.2f}%): {usdt_obtenidos:.2f}")
    print(f"ARS recomprados vendiendo USDT: {ars_recomprados:.2f}")

    # --- Camino 2: ARS -> USDT -> ARS ---
    mejor_compra = None
    usdt_c2 = None
    for p in precios:
        ask_neto = apply_buy_fee(p["exchange"], p["ask"])
        if (mejor_compra is None) or (ask_neto < mejor_compra["ask_neto"]):
            mejor_compra = p.copy()
            mejor_compra["ask_neto"] = ask_neto
            usdt_c2 = monto_ars / ask_neto

    ars_recomprados_c2 = usdt_c2 * elegir_mejor_venta(precios)["bid_neto"]

    print("\nCamino ARS -> USDT -> ARS:")
    print(f"USDT comprados directo en exchange ({mejor_compra['exchange'].upper()}, ask neto={mejor_compra['ask_neto']:.2f}): {usdt_c2:.2f}")
    print(f"ARS recomprados vendiendo USDT: {ars_recomprados_c2:.2f}")

    # --- Comparación y porcentaje ---
    if ars_recomprados >= ars_recomprados_c2:
        mejor_camino = "ARS -> USD -> USDT -> ARS"
        mejor_ars = ars_recomprados
    else:
        mejor_camino = "ARS -> USDT -> ARS"
        mejor_ars = ars_recomprados_c2

    porcentaje = (mejor_ars - monto_ars) / monto_ars * 100
    resultado = "Ganancia" if porcentaje >= 0 else "Pérdida"
    print(f"\n✅ Mejor camino: {mejor_camino} ({resultado}: {porcentaje:+.2f}%)\n")

# ------------------------
# MAIN
# ------------------------
def main():
    while True:
        choice = input("\nCon qué vas a iniciar tu rulito? (USD / USDT / ARS / SALIR): ").strip().lower()
        if choice == "salir":
            print("Saliendo. ¡Hasta luego!")
            break
        if choice not in ("usd", "usdt", "ars"):
            print("Opción inválida. Ingrese USD, USDT, ARS o SALIR.")
            continue

        precios = obtener_precios_criptoya(EXCHANGES)

        if choice == "usd":
            flujo_usd(precios)
        elif choice == "usdt":
            flujo_usdt(precios)
        elif choice == "ars":
            flujo_ars(precios)

if __name__ == "__main__":
    main()