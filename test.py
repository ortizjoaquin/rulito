#!/usr/bin/env python3
# test.py - Comparación caminos ARS -> USD -> USDT -> ARS vs ARS -> USDT -> ARS

import requests

# ------------------------
# CONFIGURACIÓN
# ------------------------
ARS_INICIAL = 100000  # monto inicial en ARS
USD_USDT_FEE = 0.05   # comisión USD -> USDT (solo para camino ARS->USD->USDT->ARS)

EXCHANGES = ["belo", "binance", "satoshitango", "letsbit", "lemoncash",
             "buenbit", "fiwind", "ripio", "binancep2p", "bybitp2p", "okexp2p"]

BUY_FEES = {  # comisión al comprar USDT con ARS
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

BANCOS = ["bna", "rebanking", "santander", "galicia", "bbva",
          "patagonia", "macro", "hsbc", "brubank", "supervielle", "icbc"]

BNA_FALLBACK = 1380.0
FALLBACK_BID = 1450.0
FALLBACK_ASK = 1450.0

# ------------------------
# FUNCIONES
# ------------------------
def obtener_precios_criptoya(exchanges):
    precios = []
    for ex in exchanges:
        try:
            url = f"https://criptoya.com/api/{ex}/USDT/ARS/1"
            r = requests.get(url, timeout=6)
            data = r.json()
            bid = float(data.get("bid", FALLBACK_BID))
            ask = float(data.get("ask", FALLBACK_ASK))
            # aplicar BUY_FEES para neto al comprar
            ask_neto = ask * (1 + BUY_FEES.get(ex.lower(), 0))
            precios.append({"exchange": ex, "bid": bid, "ask": ask, "ask_neto": ask_neto})
        except:
            precios.append({"exchange": ex, "bid": FALLBACK_BID, "ask": FALLBACK_ASK, "ask_neto": FALLBACK_ASK})
    return precios

def obtener_bancos():
    try:
        r = requests.get("https://criptoya.com/api/bancostodos", timeout=6)
        data = r.json()
        bancos_filtrados = {}
        for banco in BANCOS:
            if banco in data:
                bancos_filtrados[banco] = {
                    "bid": data[banco].get("bid", FALLBACK_BID),
                    "ask": data[banco].get("ask", FALLBACK_ASK)
                }
        return bancos_filtrados
    except:
        return {"bna": {"bid": None, "ask": BNA_FALLBACK}}

def elegir_mejor_banco_ask(precios_bancos):
    mejor = None
    for banco, datos in precios_bancos.items():
        if datos["ask"] is None:
            continue
        if (mejor is None) or (datos["ask"] < mejor["ask"]):
            mejor = {"banco": banco, "ask": datos["ask"]}
    return mejor

def elegir_mejor_compra(precios):
    mejor = None
    for p in precios:
        if (mejor is None) or (p["ask_neto"] < mejor["ask_neto"]):
            mejor = p
    return mejor

# ------------------------
# COMPARACIÓN DE CAMINOS
# ------------------------
def main():
    print(f"--- Monto inicial ARS: {ARS_INICIAL} ---\n")

    precios_exchanges = obtener_precios_criptoya(EXCHANGES)
    precios_bancos = obtener_bancos()

    # CAMINO 1: ARS -> USD -> USDT -> ARS
    mejor_banco = elegir_mejor_banco_ask(precios_bancos)
    usd_comprados = ARS_INICIAL / mejor_banco["ask"]
    usdt_obtenidos = usd_comprados * (1 - USD_USDT_FEE)  # comisión USD->USDT
    # mejor venta USDT->ARS
    mejor_venta = max(precios_exchanges, key=lambda x: x["bid"])
    ars_recomprados_c1 = usdt_obtenidos * mejor_venta["bid"]

    print("Camino ARS -> USD -> USDT -> ARS:")
    print(f"USD comprados via banco ({mejor_banco['banco'].upper()}, ask={mejor_banco['ask']}): {usd_comprados:.2f}")
    print(f"USDT obtenidos (USD -> USDT, comisión {USD_USDT_FEE*100:.2f}%): {usdt_obtenidos:.2f}")
    print(f"ARS recomprados vendiendo USDT: {ars_recomprados_c1:.2f}\n")

    # CAMINO 2: ARS -> USDT -> ARS
    mejor_compra = elegir_mejor_compra(precios_exchanges)
    usdt_obtenidos_c2 = ARS_INICIAL / mejor_compra["ask_neto"]
    ars_recomprados_c2 = usdt_obtenidos_c2 * max(precios_exchanges, key=lambda x: x["bid"])["bid"]

    print("Camino ARS -> USDT -> ARS:")
    print(f"USDT comprados directo en exchange ({mejor_compra['exchange'].upper()}, ask neto={mejor_compra['ask_neto']:.2f}): {usdt_obtenidos_c2:.2f}")
    print(f"ARS recomprados vendiendo USDT: {ars_recomprados_c2:.2f}\n")

    # COMPARACIÓN
    if ars_recomprados_c1 > ars_recomprados_c2:
        diff = ars_recomprados_c1 - ARS_INICIAL
        print(f"✅ Mejor camino: ARS -> USD -> USDT -> ARS (ganancia: {diff:.2f})")
    else:
        diff = ars_recomprados_c2 - ARS_INICIAL
        print(f"✅ Mejor camino: ARS -> USDT -> ARS (ganancia: {diff:.2f})")

if __name__ == "__main__":
    main()