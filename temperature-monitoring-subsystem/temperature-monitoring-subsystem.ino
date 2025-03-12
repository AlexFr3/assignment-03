#include <Arduino.h>
#include "Led.h"
#include "TemperatureSensor.h"
#define GREEN_PIN 16
#define RED_PIN 4
#define TEMPERATURE_PIN 34

enum {CONNECTED, DOWN} networkState; 

Light* redLed;
Light* greenLed;
TemperatureDevice* temp;
void setup() {
  redLed = new Led(RED_PIN);
  greenLed = new Led(GREEN_PIN);
  networkState = DOWN;
  greenLed->switchOff();
  redLed->switchOn();
  temp= new TemperatureSensor(TEMPERATURE_PIN);
  Serial.begin(115200);
}

void loop() {
  Serial.println(temp->getTemperature());
  delay(2000);
  switch (networkState)
  {
    case DOWN:
    {
      Serial.println("Down");
      break;
    }

    case CONNECTED:
    {
      break;
    }
  }
}
