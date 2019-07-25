import os, os.path
import string
import json
import cherrypy
from cherrypy import tools
import os, sys
sys.path.insert(0,os.path.pardir)
import paho.mqtt.client as mqttClient


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
        },
        'xeoma_server':{
        'ip_address':'192.168.100.51'
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
        if(event_type == "distancia"):
            device_name = "caja_cisterna"
        if(event_type == "motion" or event_type == "no_motion"):
            device_name = "xeoma_server"
        #print(ip_origin)
        #if(ip_origin in ip_dict.keys()):
        #    device_name = ip_dict[ip_origin]
        #else:
        #    device_name = 'unknown'
        if(value == True):
            value = 'True'
        ev = {'device_name':device_name, 'event_type':event_type, 
            'value':value}
        print(ev)
        #r.publish('events', json.dumps(ev))
        # publish with mqttt 
        try:
            #print("topic:")
            #print(device_name + "/" + event_type)
            #print("payload:")
            #print(value)
            if(event_type == "motion" and device_name == "xeoma_server"):
                event_type = value
                value = "ON"
            if(event_type == "no_motion" and device_name == "xeoma_server"):
                event_type = value
                value = "OFF"
            client.publish(device_name + "/" + event_type, value)
            print(device_name + "/" + event_type)
        except:
            print("not connected mqtt")
        return json.dumps(ev)




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


