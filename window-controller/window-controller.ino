#define POT_PIN A0
#define BUTTON_PIN 8
#define SERVO_MOTOR_PIN 3
#include "output.h"
#include "servo_motor_impl.h"
#include "ButtonImpl.h"
#include "MsgService.h"
Button *btn;
ServoMotor *window;
float temperature = 15.0;
float openingPercentage = 0;
long openingDashboard = 0;
long openingValue = 0;
enum states{AUTOMATIC, MANUAL, DASHBOARD};
states modeState = AUTOMATIC;
int lastOpening = -1;
states lastMode = AUTOMATIC;
float lastTemperature = 0;
bool switchDashboard = false;

void setup() {
  outputInit();
  pinMode(POT_PIN,INPUT);
  btn = new ButtonImpl(BUTTON_PIN);
  window = new ServoMotorImpl(SERVO_MOTOR_PIN);
  moveWindow(0);
  MsgService.init();
  modeState = AUTOMATIC;
}

void loop() {
    while(MsgService.isMsgAvailable()){
    Msg *msg = MsgService.receiveMsg();
    int startPos = (msg->getContent().indexOf(':'))+1;
    if (msg->getContent().startsWith("F:")) {
      switchDashboard = true;
      openingDashboard = msg->getContent().substring(startPos).toFloat() * 90.0;
    }
    else if (msg->getContent().startsWith("T:"))
    {
      temperature = msg->getContent().substring(startPos).toFloat();
    }else
    {
      if(msg->getContent().substring(startPos).toFloat() <= 1 && msg->getContent().substring(startPos).toFloat() >= 0)
      {
        openingPercentage = msg->getContent().substring(startPos).toFloat();
      }
    }
    delete msg;
    delay(500);
  }
  switch (modeState)
  {
    case AUTOMATIC:
    {
      if(switchDashboard) {
        switchDashboard = false;
        modeState = DASHBOARD;
        break;
      }
      openingValue = openingPercentage * 90.0;
      moveWindow(openingValue);

      if (lastMode != AUTOMATIC || lastOpening != openingValue)
      {
        clearOutput();
        writeMessage("Automatic");
        delay(100);
        setNextLine();
        writeMessage("Opening: "+ String((openingValue/90.0)*100)+"%");
        delay(100);
      }
      if(btn->isPressed())
      {
        modeState = MANUAL;
      }
      break;
    }

    case MANUAL:
    { 
      if(switchDashboard) {
        switchDashboard = false;
        modeState = DASHBOARD;
        break;
      }
      long valueRead = analogRead(POT_PIN);
      openingValue = (valueRead * 90) / 1023.0;
      if (lastMode != MANUAL || lastOpening != openingValue || lastTemperature != temperature)
      {
        clearOutput();
        writeMessage("MANUAL  T:"+ String(temperature));
        delay(100);
        setNextLine();
        writeMessage("Opening: "+ String(openingValue)+"%");
        delay(100);
        moveWindow(openingValue);
      }
      if(btn->isPressed())
      {
        modeState = AUTOMATIC;
      }
      break;
    }
    case DASHBOARD:
    {
      moveWindow(openingDashboard);

      if (lastMode != DASHBOARD || lastOpening != openingDashboard)
      {
        clearOutput();
        writeMessage("Dashboard");
        delay(100);
        setNextLine();
        writeMessage("Opening: "+ String((openingDashboard/90.0)*100)+"%");
        delay(100);
      }

      openingValue = openingDashboard;
      
      if(btn->isPressed())
      {
        modeState = AUTOMATIC;
      }
      break;
    }
  }
  lastTemperature = temperature;
  lastOpening = openingValue;
  lastMode= modeState;
  MsgService.sendMsg(String((openingValue/90.0)*100) + "\n");
  delay(1000);
}

void moveWindow(int angle)
{
  window->on();
  window->setPosition(angle);
  delay(250);
  window->off();
}

