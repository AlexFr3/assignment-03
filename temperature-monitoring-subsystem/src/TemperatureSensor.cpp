#include "TemperatureSensor.h"
#include "Arduino.h"

TemperatureSensor::TemperatureSensor(int pin){
  this->pin = pin;
  pinMode(pin, INPUT);
}

float TemperatureSensor::getTemperature(){
    int valueRead = analogRead(this->pin);
    float voltage = valueRead * (4.8 / 1024.0); 
    float celsius = (voltage - 0.5) * 100;
    return celsius;
}