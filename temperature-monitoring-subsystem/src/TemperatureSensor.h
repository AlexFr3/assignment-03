#ifndef __TEMPERATURESENSOR__
#define __TEMPERATURESENSOR__

#include "TemperatureDevice.h"

class TemperatureSensor: public TemperatureDevice { 
public:
  TemperatureSensor(int pin);
  float getTemperature(); 
private:
  int pin;  
};

#endif