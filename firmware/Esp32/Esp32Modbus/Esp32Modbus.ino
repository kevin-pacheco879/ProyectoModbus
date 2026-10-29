// ==========================================
// CÓDIGO ESP32 - SERVIDOR MODBUS TCP + RX SERIAL
// ==========================================

#include <WiFi.h>
#include <ModbusIP_ESP8266.h>

// Configuración Red Wi-Fi
const char* SSID_WIFI = "Totalplay-51A3";
const char* PASS_WIFI = "51A3E6D5R7ypNWSM";

// Nombre del dispositivo en la red (visible en Angry IP Scanner)
const char* HOSTNAME = "ESP32-Modbus-Sensor";

// Definición de pines para la comunicación Serial2 de Hardware
#define RX2_PIN 16 // Conectar al TX del Arduino
#define TX2_PIN 17 // Conectar al RX del Arduino

// Instancia del Servidor Modbus
ModbusIP mb;

// Dirección del registro Modbus (Holding Register o Input Register)
const int DISTANCIA_IREG = 100;
int ultimaDistancia = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RX2_PIN, TX2_PIN);

  // 1. Configurar el nombre del dispositivo ANTES de conectar
  WiFi.setHostname(HOSTNAME);

  // 2. Conexión Wi-Fi
  WiFi.begin(SSID_WIFI, PASS_WIFI);
  Serial.print("[ESP32] Conectando a Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n[ESP32] Wi-Fi conectado exitosamente.");
  Serial.print("[ESP32] Nombre en la red (Hostname): ");
  Serial.println(WiFi.getHostname());
  Serial.print("[ESP32] Dirección IP asignada: ");
  Serial.println(WiFi.localIP());

  // Configurar servidor Modbus TCP
  mb.server();
  // Crear el Holding Register en la dirección 100 con valor inicial 0
  mb.addHreg(DISTANCIA_IREG, 0);
}

void loop() {
  // Manejar peticiones de clientes Modbus
  mb.task();

  // Leer datos enviados desde el Arduino vía Serial2
  if (Serial2.available() > 0) {
    int distanciaRecibida = Serial2.parseInt();

    if (distanciaRecibida > 0) {
      ultimaDistancia = distanciaRecibida;
      // Actualizar el valor en el registro Modbus
      mb.Hreg(DISTANCIA_IREG, ultimaDistancia);

      Serial.print("[ESP32] Distancia actualizada en Modbus (Reg 100): ");
      Serial.print(ultimaDistancia);
      Serial.println(" cm");
    }
  }

  yield(); // Mantener la estabilidad del Watchdog de la ESP32
}