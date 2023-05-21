
from collections import defaultdict
from os import stat
import paho.mqtt.client as mqtt
from time import sleep
import json

# -----------------------------------------------------------------------------

class AirTagDisplay:

    def __init__(self) -> None:
        self.config = self.read_config('./config')
        self.mqtt_client = self.connect_to_broker()
    
    def run(self):
        self.mqtt_client.loop_forever()

    def read_config(self, path):
        kv = defaultdict(lambda: None)
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                tokens = line.strip().split(' ')
                if len(tokens) == 2:
                    kv[tokens[0]] = tokens[1]
        return kv

    def connect_to_broker(self):
        print('connecting..')
        username = self.config['MQTT_USER']
        password = self.config['MQTT_PASS']
        host = self.config['MQTT_HOST']
        port = self.config['MQTT_PORT']
        keepalive = self.config['MQTT_KEEPALIVE']
        print(username, password, host, port, keepalive)
        mqtt_client = mqtt.Client("sink")
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_disconnect = self.on_disconnect
        mqtt_client.on_message = self.on_message
        mqtt_client.username_pw_set(username, password)
        mqtt_client.connect(host, int(port), int(keepalive))
        return mqtt_client

    def on_connect(self, client, userdata, flags, rc):
        print('connected')
        self.mqtt_client.subscribe(self.config['MQTT_TOPIC'] + "/#", qos=1)

    def on_disconnect(self, client, userdata, rc):
        print('disconnected')

    def on_message(self, client, userdata, msg):
        print('%s' % msg.payload.decode())


# -----------------------------------------------------------------------------

if __name__ == '__main__':

    app = AirTagDisplay()
    app.run()