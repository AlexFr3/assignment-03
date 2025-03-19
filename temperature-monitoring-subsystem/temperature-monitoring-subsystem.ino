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
const char* mqtt_server = "192.168.177.156";
const int mqttPort = 1883;
const char* temperatureTopic = "assignment03-temperature";
const char* frequencyTopic = "assignment03-frequency";
float frequency = 0.001;
WiFiClient espClient;
PubSubClient client(espClient);

enum {CONNECTED, DOWN} networkState; 
/*
mosquitto_pub -h 192.168.177.156 -t "assignment03-frequency" -m "0.00005"
mosquitto_sub -h 192.168.177.156 -t "assignment03-temperature" -v
netstat -an | grep 1883
mosquitto -v
*/
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
  Serial.println(String("Message arrived on [") + topic + "] len: " + length );

  if(strcmp(topic, temperatureTopic) == 0){

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
  client.loop();
  Serial.println("Frequenza: " +  String(frequency, 6));
  switch (networkState)
  {
    case DOWN:
    {
      Serial.println("Down");
      setup_wifi();
      if(WiFi.status() == WL_CONNECTED){
        reconnect();
        redLed->switchOff();
        greenLed->switchOn();
        networkState = CONNECTED;
      }
      
      break;
    }

    case CONNECTED:
    {

      if(WiFi.status() != WL_CONNECTED || !client.connected()){
        greenLed->switchOff();
        redLed->switchOn();
        networkState = DOWN;
      } else {
        float temperature = temp->getTemperature();
        String msg = String(temperature);
        Serial.println(msg);
        client.publish(temperatureTopic, msg.c_str());
        float timeStop = millis() +  (1 / frequency);
        while(millis() <= timeStop && WiFi.status() == WL_CONNECTED && client.connected()) {
          client.loop();
        }
        
      }
      break;
    }
  }
}
