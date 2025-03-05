#include "output.h"
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd = LiquidCrystal_I2C(0x27,20,4);

void outputInit(){
  lcd.init();
  lcd.backlight();
}

void writeMessage(String message){
  lcd.print(message);
}

void setNextLine(){
  lcd.setCursor(0,2);
}

void resetCursor(){
  lcd.setCursor(0, 0);
}

void clearOutput(){
  lcd.clear();
  resetCursor();
}