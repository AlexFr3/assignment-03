import paho.mqtt.client as mqtt
import time
from collections import deque
import serial
from flask import Flask, request, jsonify
import threading
T1 = 15
T2 = 25
F1 = 0.0001
F2 = 0.0002
DT = 10
N = 10
broker = "test.mosquitto.org"
temperatureTopic = "assignment03-temperature"
frequencyTopic = "assignment03-frequency"
port = 1883
lastNtemperatures = deque(maxlen=N)
cryticalEnter = time.time()
alarmState = False
arduino = serial.Serial('/dev/cu.usbmodem1201', 9600, timeout=1)
time.sleep(2) 
arduino.reset_input_buffer()
arduino.reset_output_buffer()

app = Flask(__name__)
@app.route('/temperature', methods=['POST'])
def manage_request():
    data = request.get_json(silent=True)
    if "reset" in data:
        if data["reset"] == True:
            cryticalEnter= time.time()
            alarmState = False
            STATS["status"] = "Normal"
    if "set_opening" in data:
        opening = data["set_opening"]
        send_msg("F:" + str(opening))
        
    print(data)
    return jsonify(STATS), 200
STATS = {
    "sum": 0,
    "max": -272.15,
    "min": float('inf'),
    "count": 0,
    "list": [],
    "status":"Normal",
    "opening": 0
}

def send_msg(message):
    arduino.write(f"{message}\n".encode())
    print(f"Messaggio inviato: {message}")
def read_msg():
    try:
        if arduino.in_waiting > 0:  
            msg = arduino.readline().decode('utf-8').strip() 
            return msg
    except Exception as e:
        print(f"Errore nella lettura: {e}")
    return None

def message_received(client, userData, msg):
    global cryticalEnter
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
    STATS["list"] = list(lastNtemperatures)
    
    message = read_msg()
    while message != None:
        if message:
            STATS["opening"] = float(message)
        message = read_msg()
    send_msg("T:" + str(temperature))
    time.sleep(1)
    #Normal state
    if STATS["status"] == "Alarm":
        frequency = F2
        opening = 1
    elif temperature < T1:
        cryticalEnter = time.time()
        frequency = F1
        opening = 0
        STATS["status"] = "Normal"
    #Hot state
    elif temperature <= T2:
        print("Sono a > 15")
        cryticalEnter = time.time()
        frequency = F2
        opening = 0.01 + 0.99 * ((temperature - T1) / (T2 - T1))
        STATS["status"] = "Hot"
    #Too hot state
    else:
        frequency = F2
        opening = 1
        STATS["status"] = "Too hot"
        if time.time()- cryticalEnter >= DT :
            alarmState = True
            STATS["status"] = "Alarm"
    client.publish(frequencyTopic, str(frequency))
    print(STATS)  
    send_msg("O:" + str(opening))
    
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = message_received
    client.connect(broker, port, 60)
    client.subscribe(temperatureTopic)
    client.loop_forever()

if __name__ == '__main__':
    # avvia in background MQTT
    t = threading.Thread(target=mqtt_thread, daemon=True)
    t.start()
    print("MQTT thread OK, ora lancio Flask…")
    # lancia Flask in main, senza reloader, multi-threaded per poter gestire più POST
    app.run(host='0.0.0.0', port=5006, threaded=True, use_reloader=False)



    