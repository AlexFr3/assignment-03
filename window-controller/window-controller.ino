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
enum {AUTOMATIC, MANUAL} modeState; 

void setup() {
  pinMode(POT_PIN,INPUT);
  btn = new ButtonImpl(BUTTON_PIN);
  window = new ServoMotorImpl(SERVO_MOTOR_PIN);
  moveWindow(0);
  outputInit();
  MsgService.init();
  modeState = AUTOMATIC;
}

void loop() {
  if(MsgService.isMsgAvailable()){
    Msg *msg = MsgService.receiveMsg();
    int startPos = (msg->getContent().indexOf(':'))+1;
    if (msg->getContent().startsWith("Temperature:"))
    {
      temperature = msg->getContent().substring(startPos).toFloat();
    }else if(msg->getContent().startsWith("Opening:"))
    {
      openingPercentage = msg->getContent().substring(startPos).toFloat();

    }
    delete msg;
  }
  switch (modeState)
  {
    case AUTOMATIC:
    {
      int opening = openingPercentage * 90;
      MsgService.sendMsg("Opening: "+ String(opening));
      moveWindow(opening);

      clearOutput();
      writeMessage("Automatic");
      setNextLine();
      writeMessage("Opening angle: "+ String(opening));
      
      if(btn->isPressed())
      {
        modeState = MANUAL;
      }
      break;
    }

    case MANUAL:
    {
      clearOutput();
      writeMessage("MANUAL  T:"+ String(temperature));
      setNextLine();
      long valueRead = analogRead(POT_PIN);
      long openingValue = (valueRead * 90) / 1023.0;
      MsgService.sendMsg("Opening:"+ String(openingValue));

      writeMessage("Opening angle: "+ String(openingValue));
      moveWindow(openingValue);
      if(btn->isPressed())
      {
        modeState = AUTOMATIC;
      }
      break;
    }
  }
  delay(500);
}

void moveWindow(int angle)
{
  window->on();
  window->setPosition(angle);
  delay(500);
  window->off();
}

