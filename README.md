# Rulito v1.0

**Rulito** es una herramienta en Python para calcular la rentabilidad de operaciones de compra y venta de **USD y USDT** en distintos **exchanges** y **bancos** de Argentina.  
Permite evaluar la mejor opción considerando **cotizaciones actuales** y **comisiones**, incluyendo la posibilidad de recomprar USD en bancos locales.

---

## Características principales

- Consulta precios de **exchanges de criptomonedas** (USDT ↔ ARS) vía **API CriptoYa**.  
- Aplica **comisiones de compra y venta** por exchange.  
- Consulta precios de **bancos locales** y elige la mejor cotización para recomprar USD.  
- Calcula la **ganancia o pérdida neta** de las operaciones.  
- Flujo interactivo en **terminal**, con opción de iniciar con **USD o USDT**.  
- Permite **forzar un exchange** específico para vender o recomprar.  

---

## Requisitos

- Python **3.8+**
- Librerías:
bash
pip install requests

	•	Conexión a Internet para consultar precios.

⸻

📦 Instalación

1.	Clonar el repositorio:

git clone https://github.com/ortizjoaquin/rulito.git
cd rulito
	
2.	Crear un entorno virtual (opcional pero recomendado):

python3 -m venv rulito-env
source rulito-env/bin/activate  # Linux / macOS
rulito-env\Scripts\activate     # Windows

3.	Instalar dependencias:

pip install -r requirements.txt

(si no existe requirements.txt, basta con pip install requests)

⸻

🚀 Cómo usar

Ejecutar el script principal:

python rulito.py

El programa te pedirá:
	1.	Con qué iniciar el flujo: USD o USDT.
	2.	Monto a convertir.
	3.	Comisión aplicable (si corresponde).
	4.	Opcionalmente, forzar un exchange para vender o recomprar.

El script mostrará:
	•	💵 Precio neto de venta de USDT → ARS
	•	💰 ARS obtenidos
	•	🏦 Mejor banco para recomprar USD
	•	📊 Ganancia o pérdida final

⸻

⚙️ Personalización
	•	Exchanges: modificar la lista EXCHANGES y sus comisiones en SELL_FEES y BUY_FEES.
	•	Bancos: modificar la lista BANCOS.
	•	Fallbacks: valores de BNA si la API no responde (BNA_FALLBACK).

⸻

📈 Ejemplo de uso

Con qué vas a iniciar tu rulito? (USD / USDT / SALIR): usd
Ingrese monto en USD: 1000
Ingrese comisión USD→USDT (%): 1

[💵] Pasando 1000 USD → 990 USDT (comisión 1%)
[✅] Mejor precio de venta USDT/ARS: $1465.01 (binancep2p)
ARS obtenidos: $1,450,359.90
[💰] Mejor banco para recomprar USD: BNA a $1350.00
USD recomprados: $1074.34
Ganancia: $74.34 (7.43%)


⸻

📜 Licencia

Proyecto de uso personal y educativo. No constituye asesoramiento financiero.
