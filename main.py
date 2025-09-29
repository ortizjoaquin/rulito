from paths.path_ars import flujo_ars
from paths.path_usd import flujo_usd
from paths.path_usdt import flujo_usdt

def main():
    print("Bienvenido a Rulito\n")

    while True:
        opcion = input("Con qué vas a iniciar tu rulito? (USD / USDT / ARS / SALIR): ").strip().upper()

        if opcion == "USD":
            flujo_usd()
        elif opcion == "USDT":
            flujo_usdt()
        elif opcion == "ARS":
            flujo_ars()
        elif opcion == "SALIR":
            print("Saliendo de Rulito. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intenta de nuevo.\n")

if __name__ == "__main__":
    main()