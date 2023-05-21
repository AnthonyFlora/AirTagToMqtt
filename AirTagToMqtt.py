
from collections import defaultdict
from os import stat
import paho.mqtt.client as mqtt
from time import sleep
import json

# -----------------------------------------------------------------------------

class AirTagToMqtt:

    def __init__(self) -> None:
        self.config = self.read_config('./config')
        self.mqtt_client = self.connect_to_broker()
    

    def run(self):
        prev_time = 0
        while True:
            curr_time = stat(self.config['FINDMY_CACHE_PATH']).st_mtime
            if prev_time != curr_time:
                print('%0.6f -> %0.6f change detected' % (prev_time, curr_time))
                self.on_cache_update()
                prev_time = curr_time
                sleep(5)

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
        mqtt_client = mqtt.Client("source")
        mqtt_client.on_disconnect = self.on_disconnect
        mqtt_client.username_pw_set(username, password)
        mqtt_client.connect(host, int(port), int(keepalive))
        return mqtt_client

    def on_connect(self, client, userdata, flags, rc):
        print('connected')

    def on_disconnect(self, client, userdata, rc):
        self.mqtt_client.reconnect()

    def on_cache_update(self):
        self.mqtt_client.loop()
        with open(self.config['FINDMY_CACHE_PATH']) as f:
            data = json.load(f)
            for i in data:
                msg  = '{'
                msg += ('\'time\': %15.3f, ' % (float(i['location']['timeStamp']) / 1000))
                msg += ('\'lat\': %0.15f, ' % i['location']['latitude'])
                msg += ('\'long\': %0.15f, ' % i['location']['longitude'])
                msg += ('\'serial\': %s, ' % i['serialNumber'])
                msg += ('\'name\': %s' % i['name'])
                msg += ('}')
                print(msg)
                topic = self.config['MQTT_TOPIC'] + '/' + i['serialNumber']
                self.mqtt_client.publish(topic, msg, qos=1, retain=True)


# -----------------------------------------------------------------------------

if __name__ == '__main__':

    app = AirTagToMqtt()
    app.run()


    








