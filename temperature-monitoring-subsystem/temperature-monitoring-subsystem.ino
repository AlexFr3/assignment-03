#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "Led.h"
#include "TemperatureSensor.h"
#define GREEN_PIN 16
#define RED_PIN 4
#define TEMPERATURE_PIN 34
/*WiFi credentials */
const char* wifiName = "OnePlus9Pro";
const char* wifiPassword = "passwordiot";
const char* mqtt_server = "broker.hivemq.com";
const int mqttPort = 1883;
const char* temperatureTopic = "assignment03-temperature";
const char* frequencyTopic = "assignment03-frequency";
float frequency = 1.0;
WiFiClient espClient;
PubSubClient client(espClient);

enum {CONNECTED, DOWN} networkState; 

Light* redLed;
Light* greenLed;
TemperatureDevice* temp;
void setup_wifi(){
  Serial.println(String("Connecting to ") + wifiName);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiName,wifiPassword);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(char* topic, byte* payload, unsigned int length) {
  if(strcmp(topic, temperatureTopic)){

  } else if(strcmp(topic, frequencyTopic) == 0){
    String message = "";
    for(int i = 0; i < length ; i++){
      message += (char)payload[i];
    }
    frequency = message.toFloat();
  }
}

void reconnect() {
  
  // Loop until we're reconnected
  
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Create a random client ID
    String clientId = String("assignment03-client-")+String(random(0xffff), HEX);

    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(temperatureTopic);
      client.subscribe(frequencyTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  redLed = new Led(RED_PIN);
  greenLed = new Led(GREEN_PIN);
  networkState = DOWN;
  greenLed->switchOff();
  redLed->switchOn();
  temp= new TemperatureSensor(TEMPERATURE_PIN);
  Serial.begin(115200);
  client.setServer(mqtt_server,mqttPort);
  client.setCallback(callback);
}

void loop() {
  Serial.println(temp->getTemperature());
  delay(2000);
  switch (networkState)
  {
    case DOWN:
    {
      Serial.println("Down");
      setup_wifi();
      if(WiFi.status() == WL_CONNECTED){
        redLed->switchOff();
        greenLed->switchOn();
        networkState = CONNECTED;
        reconnect();
      }
      
      break;
    }

    case CONNECTED:
    {
      if(WiFi.status() != WL_CONNECTED || !client.connected()){
        greenLed->switchOff();
        redLed->switchOn();
        networkState = DOWN;
      }
      break;
    }
  }
}
