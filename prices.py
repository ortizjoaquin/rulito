import requests
from config import FALLBACK_BID, FALLBACK_ASK, BANCOS, BNA_FALLBACK
from utils import elegir_mejor_venta, apply_buy_fee  # si necesitás en algún cálculo adicional
from utils import elegir_mejor_compra



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