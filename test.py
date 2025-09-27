import requests

url = "https://criptoya.com/api/bancostodos"
r = requests.get(url, timeout=6)
data = r.json()

# Bancos que queremos filtrar
bancos = ["bna", "rebanking", "santander", "galicia", "bbva",
          "patagonia", "macro", "hsbc", "brubank", "supervielle", "icbc"]

precios_bancos = {}
for banco in bancos:
    info = data.get(banco.lower())
    if info:
        precios_bancos[banco.upper()] = {"compra": info.get("bid"), "venta": info.get("ask")}
    else:
        precios_bancos[banco.upper()] = {"compra": None, "venta": None}

# Mostramos resultados
for banco, precios in precios_bancos.items():
    print(f"{banco}: compra={precios['compra']}, venta={precios['venta']}")