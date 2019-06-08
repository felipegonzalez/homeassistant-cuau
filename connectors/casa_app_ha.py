import os, os.path
import random
import string
import json
#import sqlite3 as lite
import cherrypy
from cherrypy import tools

import os, sys
sys.path.insert(0,os.path.pardir)
#from settings import r 
#from settings import ip_dict
import paho.mqtt.client as mqttClient
import requests
#from casitas import app_timer


# devices
device_settings = {
        'estacion_meteo':{
        'device_type':'meteo',
        'place':'exterior',
        'ip_address':'estacionyun.local'
        },
        'caja_cisterna':{
        'device_type':'esp6288',
        'ip_address':'192.168.100.153',
        'place':'patio',
        'polling':0
        }
}

ip_dict = {}
for key in device_settings.keys():
        if('ip_address' in device_settings[key].keys()):
                ip_dict[device_settings[key]['ip_address']] = key

cherrypy.server.socket_host = '0.0.0.0'
broker_address = "192.168.100.50"
port = 1883
user = "homeassistant"


def on_connect(client, userdata, flags, rc):
    pass

client = mqttClient.Client("Python")
client.username_pw_set(user)
client.on_connect = on_connect
try:
    print("Connected to mqtt server")
    client.connect(broker_address, port=port)
    client.loop_start()
except:
    print("Could not connect mqtt")


class control(object):

    @cherrypy.expose
    def send_event(self, event_type, value):
        ip_origin = cherrypy.request.remote.ip
        if(ip_origin in ip_dict.keys()):
            device_name = ip_dict[ip_origin]
        else:
            device_name = 'unknown'
        if(value == True):
            value = 'True'
        ev = {'device_name':device_name, 'event_type':event_type, 
            'value':value}
        #r.publish('events', json.dumps(ev))
        # publish with mqttt 
        try:
            #print("topic:")
            #print(device_name + "/" + event_type)
            #print("payload:")
            #print(value)
            client.publish(device_name + "/" + event_type, value)
        except:
            print("not connected mqtt")
        return json.dumps(ev)


    @cherrypy.expose
    @tools.json_out()
    def get_weather(self, **kwargs):
        response = requests.get("http://192.168.100.24/arduino/weather/0").text
        weather_dict =  json.loads(response.rstrip().replace("'", '"'))
        print(weather_dict)
        return weather_dict






if __name__ == '__main__':
    #cherrypy.log.screen = None
    cherrypy.config.update({'server.socket_port':8090})
    conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())

         }
    }
    webapp = control()
    cherrypy.quickstart(webapp, '/', conf)

