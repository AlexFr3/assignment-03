import paho.mqtt.client as mqtt
import time
from collections import deque
import serial

T1 = 15
T2 = 25
F1 = 0.001
F2 = 0.002
DT = 10
N = 10
broker = "broker.hivemq.com"
temperatureTopic = "assignment03-temperature"
frequencyTopic = "assignment03-frequency"
port = 1883
lastNtemperatures = deque(maxlen=N)
cryticalEnter = time.time()
alarmState = False

arduino = serial.Serial('/dev/cu.usbmodem11301', 9600, timeout=1)
time.sleep(2) 

STATS = {
    "sum": 0,
    "max": -272.15,
    "min": float('inf'),
    "count": 0
}

def send_msg(message):
    arduino.write(f"{message}\n".encode())  
def read_msg():
    try:
        if arduino.in_waiting > 0:  
            msg = arduino.readline().decode('utf-8').strip() 
            return msg
    except Exception as e:
        print(f"Errore nella lettura: {e}")
    return None

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
    
    message = read_msg()
    if message!=None:
        print("Messaggio ricevuto: " + str(message))
    send_msg("Temperature:" + str(temperature))    
    #Normal state
    if temperature < T1:
        cryticalEnter = time.time()
        frequency = F1
        opening = 0
        #TODO: inviare la segnale per aperture di arduino
    #Hot state
    elif temperature <= T2:
        cryticalEnter = time.time()
        frequency = F2
        opening = 0.01 + 0.99 * ((temperature - T1) / (T2 - T1))
        #TODO: inviare la segnale per aperture di arduino
    #Too hot state
    else:
        frequency = F2
        opening = 1
        if time.time()- cryticalEnter >= DT :
            alarmState = True
            #TODO bloccare fino ad intervento operatore su dashboard
    client.publish(frequencyTopic, str(frequency))
    print(STATS)  
    send_msg("Opening:" + opening)
    
client = mqtt.Client()
client.on_message = message_received
client.connect(broker, port, 60)
client.subscribe(temperatureTopic)
client.loop_forever()


    