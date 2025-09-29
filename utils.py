from config import SELL_FEES, BUY_FEES

def format_exchange_text(exchange: str, precio: float, comision: float) -> str:
    return f"{exchange.upper():<12} ${precio:,.2f}" + (f" (comisión {comision*100:.2f}%)" if comision > 0 else "")

def apply_sell_fee(exchange: str, bid: float) -> float:
    return bid * (1 - SELL_FEES.get(exchange.lower(), 0.0))

def apply_buy_fee(exchange: str, ask: float) -> float:
    return ask * (1 + BUY_FEES.get(exchange.lower(), 0.0))

def elegir_mejor_venta(precios):
    mejor = max(precios, key=lambda x: apply_sell_fee(x["exchange"], x["bid"]))
    mejor["bid_neto"] = apply_sell_fee(mejor["exchange"], mejor["bid"])
    return mejor

def elegir_mejor_compra(precios):
    mejor = min(precios, key=lambda x: apply_buy_fee(x["exchange"], x["ask"]))
    mejor["ask_neto"] = apply_buy_fee(mejor["exchange"], mejor["ask"])
    return mejor