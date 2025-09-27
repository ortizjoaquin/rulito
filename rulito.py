#!/usr/bin/env python3
# rulito.py - versión completa con comisiones aplicadas a precios

import requests

# ------------------------
# CONFIGURACIÓN (fácil de editar)
# ------------------------
SELL_FEES = {  # comisiones al vender USDT -> ARS (decimal)
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

BUY_FEES = {  # comisiones al comprar USDT con ARS (decimal)
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

# Exchanges que consultamos (debe corresponder a claves de SELL_FEES/BUY_FEES)
EXCHANGES = ["belo", "binance", "satoshitango", "letsbit", "lemoncash",
             "buenbit", "fiwind", "ripio", "binancep2p", "bybitp2p", "okexp2p"]

BANCOS = ["bna", "rebanking", "santander", "galicia", "bbva",
          "patagonia", "macro", "hsbc", "brubank", "supervielle", "icbc"]

# Fallback dólar BNA y precios
BNA_FALLBACK = 1380.0
FALLBACK_BID = 1450.0
FALLBACK_ASK = 1450.0

# ------------------------
# UTILIDADES
# ------------------------

def format_exchange_text(exchange: str, precio: float, comision: float) -> str:
    """Formatea la parte que muestra el precio y la comisión (solo si > 0)."""
    if comision > 0:
        return f"${precio:.2f} ({exchange}, comisión {comision*100:.2f}% incluida)"
    else:
        return f"${precio:.2f} ({exchange})"

def apply_sell_fee(exchange: str, bid: float) -> float:
    """Bid neto (lo que recibís por 1 USDT) aplicando comisión de venta."""
    fee = SELL_FEES.get(exchange.lower(), 0.0)
    return bid * (1 - fee)

def apply_buy_fee(exchange: str, ask: float) -> float:
    """Ask neto (lo que pagás por 1 USDT) incluyendo comisión de compra."""
    fee = BUY_FEES.get(exchange.lower(), 0.0)
    return ask * (1 + fee)

def obtener_precios_criptoya(exchanges):
    """Consulta CriptoYa para la lista de exchanges. Devuelve lista de dicts."""
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
            print(f"[✅] Precios de {ex} obtenidos: bid={bid}, ask={ask}")
        except Exception as e:
            precios.append({"exchange": ex, "bid": FALLBACK_BID, "ask": FALLBACK_ASK})
            print(f"[❌] No se pudo obtener precios de {ex}, usando fallback {FALLBACK_BID}/{FALLBACK_ASK}")
    print("\nTodos los precios cargados.\n")
    return precios

def elegir_mejor_venta(precios, forzar_exchange=None):
    """Devuelve dict {exchange, bid, ask, bid_neto} del mejor (o forzado)."""
    if forzar_exchange:
        for p in precios:
            if p["exchange"].lower() == forzar_exchange.lower():
                p_copy = p.copy()
                p_copy["bid_neto"] = apply_sell_fee(p_copy["exchange"], p_copy["bid"])
                return p_copy
        print(f"[⚠️] Exchange forzado '{forzar_exchange}' no encontrado; usando automático.")
    # elegir el mayor bid_neto
    mejor = None
    for p in precios:
        bid_neto = apply_sell_fee(p["exchange"], p["bid"])
        if (mejor is None) or (bid_neto > mejor["bid_neto"]):
            mejor = p.copy()
            mejor["bid_neto"] = bid_neto
    return mejor

def elegir_mejor_compra(precios, forzar_exchange=None):
    """Devuelve dict {exchange, bid, ask, ask_neto} del mejor (o forzado)."""
    if forzar_exchange:
        for p in precios:
            if p["exchange"].lower() == forzar_exchange.lower():
                p_copy = p.copy()
                p_copy["ask_neto"] = apply_buy_fee(p_copy["exchange"], p_copy["ask"])
                return p_copy
        print(f"[⚠️] Exchange forzado '{forzar_exchange}' no encontrado; usando automático.")
    mejor = None
    for p in precios:
        ask_neto = apply_buy_fee(p["exchange"], p["ask"])
        if (mejor is None) or (ask_neto < mejor["ask_neto"]):
            mejor = p.copy()
            mejor["ask_neto"] = ask_neto
    return mejor

def obtener_bancos():
    """Devuelve diccionario con info de bancos filtrados"""
    try:
        r = requests.get("https://criptoya.com/api/bancostodos", timeout=6)
        data = r.json()
        bancos_filtrados = {}
        for banco in BANCOS:
            if banco in data:
                bancos_filtrados[banco] = {
                    "bid": data[banco].get("bid"),
                    "ask": data[banco].get("ask")
                }
        return bancos_filtrados
    except Exception as e:
        print(f"[⚠️] No se pudo obtener precios de bancos: {e}")
        # fallback con BNA
        return {"bna": {"bid": None, "ask": BNA_FALLBACK}}

def mejor_banco_ask(precios_bancos):
    """Devuelve el banco con el ask más bajo (mejor precio para comprar USD)"""
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
    # 1) ingreso monto y comisión USD->USDT
    try:
        monto_usd = float(input("Ingrese monto en USD: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return
    try:
        com_pct = float(input("Ingrese comisión USD→USDT (%): ").strip()) / 100.0
    except:
        print("Comisión inválida. Usando 0%.")
        com_pct = 0.0

    usdt_obtenidos = monto_usd * (1 - com_pct)
    print(f"\n[💵] Pasando {monto_usd:.2f} USD → {usdt_obtenidos:.6f} USDT (comisión {com_pct*100:.2f}%)")

    # 2) forzar exchange para vender USDT? (busca mejor bid neto si no)
    forced_sell = input("Desea forzar un exchange para vender USDT? (deje vacío para automático): ").strip().lower() or None
    venta = elegir_mejor_venta(precios, forced_sell)
    bid_neto = venta["bid_neto"]
    ars_obtenidos = usdt_obtenidos * bid_neto
    fee_sell = SELL_FEES.get(venta["exchange"].lower(), 0.0)

    print(f"\n[✅] Mejor precio de venta USDT/ARS (neto): {format_exchange_text(venta['exchange'], bid_neto, fee_sell)}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    # 3) Convertir ARS -> USD usando BNA (no recompramos USDT en este flujo)
    precios_bancos = obtener_bancos()
    mejor = mejor_banco_ask(precios_bancos)
    if mejor:
        usd_recomprados = ars_obtenidos / mejor["ask"]
        print(f"\n[💰] Mejor banco para recomprar USD: {mejor['banco'].upper()} a ${mejor['ask']:.2f}")
    else:
        usd_recomprados = ars_obtenidos / BNA_FALLBACK
        print(f"\n[💰] Usando BNA fallback para recomprar USD: ${BNA_FALLBACK:.2f}")

    diff = usd_recomprados - monto_usd
    print("\n[💰] Resultado final (convertido a USD por banco elegido):")
    print(f"USD iniciales: ${monto_usd:.2f}")
    print(f"USD recomprados: ${usd_recomprados:.2f}")
    if diff >= 0:
        print(f"Ganancia: ${diff:.2f} ({(diff/monto_usd)*100:.2f}%)")
    else:
        print(f"Pérdida: ${diff:.2f} ({(diff/monto_usd)*100:.2f}%) -NO RENTABLE-")

def flujo_usdt(precios):
    # 1) ingreso monto USDT
    try:
        monto_usdt = float(input("Ingrese monto en USDT: ").strip())
    except:
        print("Monto inválido. Volviendo al menú.")
        return

    # 2) forzar exchange para vender USDT? (mejor bid neto si no)
    forced_sell = input("Desea forzar un exchange para vender USDT? (deje vacío para automático): ").strip().lower() or None
    venta = elegir_mejor_venta(precios, forced_sell)
    bid_neto = venta["bid_neto"]
    ars_obtenidos = monto_usdt * bid_neto
    fee_sell = SELL_FEES.get(venta["exchange"].lower(), 0.0)

    print(f"\n[✅] Mejor precio de venta USDT/ARS (neto): {format_exchange_text(venta['exchange'], bid_neto, fee_sell)}")
    print(f"ARS obtenidos: ${ars_obtenidos:,.2f}")

    # 3) forzar exchange para recomprar USDT? (mejor ask neto si no)
    forced_buy = input("Desea forzar un exchange para recomprar USDT? (deje vacío para automático): ").strip().lower() or None
    compra = elegir_mejor_compra(precios, forced_buy)
    ask_neto = compra["ask_neto"]
    usdt_recomprados = ars_obtenidos / ask_neto
    fee_buy = BUY_FEES.get(compra["exchange"].lower(), 0.0)
    diff = usdt_recomprados - monto_usdt

    print(f"\n[✅] Mejor precio para recomprar USDT (neto): {format_exchange_text(compra['exchange'], ask_neto, fee_buy)}")
    print(f"USDT recomprados: {usdt_recomprados:.6f}")
    if diff >= 0:
        print(f"Ganancia: {diff:.6f} USDT ({(diff/monto_usdt)*100:.4f}%)")
    else:
        print(f"Pérdida: {diff:.6f} USDT ({(diff/monto_usdt)*100:.4f}%) -NO RENTABLE-")

# ------------------------
# BUCLE PRINCIPAL
# ------------------------
def main():
    while True:
        choice = input("\nCon qué vas a iniciar tu rulito? (USD / USDT / SALIR): ").strip().lower()
        if choice == "salir":
            print("Saliendo. ¡Hasta luego!")
            break
        if choice not in ("usd", "usdt"):
            print("Opción inválida. Ingrese USD, USDT o SALIR.")
            continue

        precios = obtener_precios_criptoya(EXCHANGES)

        if choice == "usd":
            flujo_usd(precios)
        elif choice == "usdt":
            flujo_usdt(precios)

if __name__ == "__main__":
    main()