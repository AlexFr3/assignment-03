import paho.mqtt.client as mqtt
import time
from collections import deque
T1 = 15
T2 = 25
F1 = 0.001
F2 = 0.002
DT = 10
N = 10
broker = "192.168.34.156"
temperatureTopic = "assignment03-temperature"
frequencyTopic = "assignment03-frequency"
port = 1883
lastNtemperatures = deque(maxlen=N)
cryticalEnter = time.time()
alarmState = False
STATS = {
    "sum": 0,
    "max": -272.15,
    "min": float('inf'),
    "count": 0
}


def message_received(client, userData, msg):
    payload = msg.payload.decode()
    print("Temperatura ricevuta: " + str(payload))
    temperature = float(payload)
    lastNtemperatures.append(temperature)
    print(lastNtemperatures)
    if temperature > STATS["max"]:
        STATS["max"] = temperature
    if temperature < STATS["min"]:
        STATS["min"] = temperature
    STATS["sum"] += temperature
    STATS["count"] += 1
    
    #Normal state
    if temperature <= T1:
        cryticalEnter = time.time()
        frequency = F1
        #TODO: inviare la segnale per aperture di arduino
    #Hot state
    elif temperature <= T2:
        cryticalEnter = time.time()
        frequency = F2
        #TODO: inviare la segnale per aperture di arduino
    #Too hot state
    else:
        frequency = F2
        if time.time()- cryticalEnter >= DT :
            alarmState = True
            #TODO bloccare fino ad intervento operatore su dashboard
    client.publish(frequencyTopic, str(frequency))
    print(STATS)  
        
client = mqtt.Client()
client.on_message = message_received
client.connect(broker, port, 60)
client.subscribe(temperatureTopic)
client.loop_forever()


    