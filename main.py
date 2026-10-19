import time
import json
import os
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA
# ==========================================
PUERTO_MODBUS = 502
REGISTRO_DISTANCIA = 100  # Registro en el ESP32
ARCHIVO_JSON = "registro_conexion.json"

def gestionar_archivo_json(accion, ip=None, estado=None):
    """
    Centraliza la lectura y escritura del archivo JSON.
    'leer' retorna la última IP guardada con conexión exitosa o None.
    'escribir' almacena la IP con marca de tiempo y estado.
    """
    if accion == "leer":
        if os.path.exists(ARCHIVO_JSON):
            try:
                with open(ARCHIVO_JSON, 'r') as archivo:
                    datos = json.load(archivo)
                    if datos.get("conexion_exitosa"):
                        return datos.get("direccion_ip")
            except (json.JSONDecodeError, OSError):
                return None
        return None

    elif accion == "escribir":
        datos = {
            "direccion_ip": ip,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "conexion_exitosa": estado
        }
        with open(ARCHIVO_JSON, 'w') as archivo:
            json.dump(datos, archivo, indent=4)

def monitorear_esp32():
    # ==========================================
    # 2. RESOLUCIÓN DE DIRECCIÓN IP
    # ==========================================
    ip_actual = gestionar_archivo_json("leer")

    if ip_actual:
        print(f"[SISTEMA] Cargando última IP exitosa registrada: {ip_actual}")
    else:
        print("[SISTEMA] No hay IP válida almacenada en el sistema.")
        ip_actual = input("[INPUT] Ingresa la dirección IP del ESP32: ").strip()

    cliente = None

    # Bucle de validación y establecimiento de conexión
    while True:
        cliente = ModbusTcpClient(ip_actual, port=PUERTO_MODBUS)
        print(f"\n[RED] Intentando conectar al ESP32 en {ip_actual}:{PUERTO_MODBUS}...")

        if cliente.connect():
            print("[MODBUS] Conexión establecida con éxito.")
            gestionar_archivo_json("escribir", ip_actual, True)
            break
        else:
            print(f"[ERROR] No se pudo conectar con {ip_actual}.")
            gestionar_archivo_json("escribir", ip_actual, False)
            ip_actual = input("[INPUT] Ingresa una nueva dirección IP: ").strip()

    # ==========================================
    # 3. LECTURA DE REGISTROS (POLLING)
    # ==========================================
    print("\n[MODBUS] Iniciando sondeo del sensor ultrasónico... (Ctrl+C para salir)\n")

    try:
        while True:
            # Petición al registro 100 (Holding Registers)
            respuesta = cliente.read_holding_registers(address=REGISTRO_DISTANCIA, count=1)

            if respuesta.isError():
                print("[ERROR] Fallo al leer el registro Modbus ( Timeout o trama corrupta ).")
            else:
                distancia = respuesta.registers[0]
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Distancia recibida: {distancia} cm")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[SISTEMA] Monitoreo detenido por el usuario.")
    except ModbusException as e:
        print(f"\n[ERROR] Excepción de protocolo Modbus: {e}")
    finally:
        if cliente:
            cliente.close()
            print("[RED] Socket TCP cerrado correctamente.")

if __name__ == "__main__":
    monitorear_esp32()