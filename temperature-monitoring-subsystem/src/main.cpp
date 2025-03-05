#include <Arduino.h>
#include "Led.h"
// put function declarations here:
int myFunction(int, int);

Light* led;

void setup() {
  // put your setup code here, to run once:
  int result = myFunction(2, 3);
  led=new Led(2);
}

void loop() {
  led->switchOn();
  delay(1000);
  led->switchOff();
  delay(1000);
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}