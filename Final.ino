#include <DHT.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>

// === DHT11 Setup ===
#define DHTPIN 15
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// === Analog Pins ===
#define MQ7_PIN 34
#define MQ135_PIN 35
#define MICS2714_PIN 32

// === DSM501A ===
#define DSM501A_PIN 33

// === GPS Setup (UART2) ===
HardwareSerial GPS(2);
TinyGPSPlus gps;

// === Timing ===
unsigned long lastLogTime = 0;
const unsigned long interval = 5000;

bool headerPrinted = false;

void setup() {
  Serial.begin(115200);
  GPS.begin(9600, SERIAL_8N1, 16, 17);

  dht.begin();
  pinMode(DSM501A_PIN, INPUT);
}

void loop() {
  while (GPS.available()) {
    gps.encode(GPS.read());
  }

  unsigned long currentTime = millis();
  if (currentTime - lastLogTime >= interval) {
    lastLogTime = currentTime;

    float temp = dht.readTemperature();
    float humid = dht.readHumidity();

    int mq7 = analogRead(MQ7_PIN);
    int mq135 = analogRead(MQ135_PIN);
    int mics = analogRead(MICS2714_PIN);
    int dust = digitalRead(DSM501A_PIN);

    double lat = gps.location.isValid() ? gps.location.lat() : 0.0;
    double lng = gps.location.isValid() ? gps.location.lng() : 0.0;

    // Print CSV header once
    if (!headerPrinted) {
      Serial.println("Latitude,Longitude,Temperature,Humidity,MQ7,MQ135,MICS,Dust");
      headerPrinted = true;
    }

    // Print data row
    Serial.printf("%.6f,%.6f,%.2f,%.2f,%d,%d,%d,%d\n",
                  lat, lng, temp, humid, mq7, mq135, mics, dust);
  }
}
