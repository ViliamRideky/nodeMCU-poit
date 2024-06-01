#include <ESP8266WiFi.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <ArduinoJson.h>

#define DHTPIN 4
#define DHTTYPE    DHT11

DHT_Unified dht(DHTPIN, DHTTYPE); // Vytvorenie objektu DHT

void setup(){
	Serial.begin(115200);
  Serial.print("Hello");
  dht.begin();

  sensor_t sensor;
}

void loop() {
  delay(2000);
  
  sensors_event_t event;
   dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature!"));
  }
  else {
    Serial.print(F("Temperature "));
    Serial.print(event.temperature);
    Serial.println(F(""));
  }

  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity!"));
  }
  else {
    Serial.print(F("Humidity "));
    Serial.print(event.relative_humidity);
    Serial.println(F(""));
  }
}
