// === Analog Pins ===
#define MQ7_PIN 34
#define MQ135_PIN 35
#define MICS2714_PIN 32

// === Timing ===
unsigned long lastLogTime = 0;
const unsigned long interval = 5000;

bool headerPrinted = false;

void setup() {
  Serial.begin(115200);
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastLogTime >= interval) {
    lastLogTime = currentTime;

    int mq7 = analogRead(MQ7_PIN);
    int mq135 = analogRead(MQ135_PIN);
    int mics = analogRead(MICS2714_PIN);

    // Print CSV header once
    if (!headerPrinted) {
      Serial.println("MQ7,MQ135,MICS");
      headerPrinted = true;
    }

    // Print data row
    Serial.printf("%d,%d,%d\n", mq7, mq135, mics);
  }
}

