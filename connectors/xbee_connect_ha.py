#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import logging
#import logging.handlers
from xbee import ZigBee
import os, sys
sys.path.insert(0,os.path.pardir)
#from settings import r 
#from settings import xbee_dict
#from settings import device_settings
import json
import serial
from binascii import unhexlify
from binascii import hexlify
import paho.mqtt.client as mqtt
import time
#from casitas import app_timer
device_settings = {
        'cajasala':{
        'place':'sala',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bf0582'
        },
        'caja_vestidor':{
        'place':'vestidor',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bef8ba'
        },
        'cajacocina':{
        'place':'cocina',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bf06bd',
        'txcommands':{'strip_cocina':{'turn_on':'1', 'turn_off':'0'}}
        #'txcommands':{'turn_on':'1', 'turn_off':'0'}
        },
        'cajarecamara':{
        'place':'recamara_principal',
        'device_type':'xbeebox',
        'addr_long':'0013a20040c45639'
        },
        'caja_pasillo_recamaras':{
        'place':'pasillo_recamaras',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bf05de',
        'pins':{'dio-4':'motion'}
        },
        'caja_bano_visitas':{
        'place':'bano_visitas',
        'device_type':'xbeebox',
        'addr_long':'0013a20040caaddc',
        'pins':{'dio-1':'motion'}
        },
        'caja_bano_principal':{
        'place':'bano_principal',
        'device_type':'xbeebox',
        'addr_long':'0013a20040c2833b',
        'pins':{'dio-1':'motion'}
        },
        'caja_puerta':{
        'place':'hall_entrada',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bef84d',
        'pins':{'dio-1':'motion', 'dio-2':'door', 'adc-3':'photo', 'dio-0':'none',
        'dio-12':'none', 'dio-4':'none'}
        },
        'caja_estudiof':{
        'place':'estudiof',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bf06d4'
        },
        'caja_consumo_electrico':{
        'place':'casa',
        'device_type':'xbeebox',
        'addr_long':'0013a20040c4605b'
        },
        'caja_estudiot':{
        'place':'estudiot',
        'device_type':'xbeebox',
        'addr_long':'0013a20040be4592'
        },
        'caja_pasillo_comedor':{
        'place':'pasillo_comedor',
        'device_type':'xbeebox',
        'addr_long':'0013a20040c4190d'
        },
        'caja_goteo':{
        'place':'patio',
        'device_type':'xbeebox',
        'addr_long':'0013a20040caadda',
        'children':{'regar':'D2'}
        },
        'caja_terraza':{
        'place':'jardin',
        'device_type':'xbeebox',
        'addr_long':'0013a20040caacd7',
        'txcommands':{'strip_terraza':{'turn_on':'1', 'turn_off':'0'}}
        },
        'caja_garage':{
        'place':'patio',
        'device_type':'xbeebox',
        'addr_long':'0013a20040c059bc',
        'txcommands':{'garage':{'activate':'g'}},
        },
        'caja_comedor':{
        'place':'comedor',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bf962c'
        },
        'caja_filtro_alberca':{
        'place':'patio',
        'device_type':'xbeebox',
        'addr_long':'0013a20040bef862',
        'children':{'bomba':'D2'}
        }
}




#xbee_dict
xbee_dict = {}
for key in device_settings.keys():
        if(device_settings[key]['device_type'] == 'xbeebox'):
                xbee_dict[device_settings[key]['addr_long']] = key

broker_address = "192.168.100.50"
port = 1883
user = "homeassistant"

#SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_PORT = '/dev/tty.usbserial-AH02VCE9'

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag = True
        print("Mqtt client connected")
        client.subscribe("xbeebox/+/send_tx")
        client.subscribe("xbeebox/+/pin/#")
    else:
        client.bad_connection_flag=True
def on_message(client, userdata, msg):
    print("--------")
    xbee = userdata
    print(msg.topic)
    topic_split = msg.topic.split("/")
    print(msg.payload)
    device_name = topic_split[1]
    print(device_name)
    print(device_settings[device_name]['addr_long'])
    dest_addr_long = unhexlify(device_settings[device_name]['addr_long'])
    if(topic_split[2]=="send_tx"):
        xbee.tx(dest_addr_long=dest_addr_long, data = (msg.payload))
    else:
        pin = topic_split[3]
        if(msg.payload==b'1'):
            print("Send on commmand ------- pin")
            print(dest_addr_long)
            print((bytes.fromhex("05")))
            print(pin)
            xbee.remote_at(dest_addr_long= dest_addr_long, parameter=bytes.fromhex('05'), command=hexlify(bytes.fromhex(pin)))
        else:
            xbee.remote_at(dest_addr_long= dest_addr_long, parameter=bytes.fromhex('04'), command=hexlify(bytes.fromhex(pin)))

def on_disconnect(client, userdata, rc):
    print("Attempting reconnect to mqtt broker...")
    client.connected_flag = False
    client.disconnect_flag=True


def monitor():

    print("Activar xbee coordinator...")
    serialConnection = serial.Serial( SERIAL_PORT, 9600,timeout=0.5)
    xbee = ZigBee(serialConnection)
    print("Conexión xbee serial...OK")
    client = mqtt.Client("xbee_reader", userdata = xbee)
    client.username_pw_set(user)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connected_flag = False
    client.on_message = on_message
    client.loop_start()   
    try:
        client.connect(broker_address, port=port)
    except:
        print("Could not connect to mqtt server!")

    print('Iniciar ciclo')
    while True:
        while(not client.connected_flag):
            try:
                client.connect(broker_address, port=port)
                client.subscribe("xbeebox/+/send_tx")
                client.subscribe("xbeebox/+/pin/#")
            except:
                print("Could not connect")
            time.sleep(1)

        response = {}
        response = xbee.wait_read_frame(timeout = 0.2)
        if(len(response)>0 and response['id']!='tx_status'):
            response['source_addr_long'] = response['source_addr_long'].hex()
            response['source_addr'] = response['source_addr'].hex()
            #print(response)
            if(xbee_dict[response['source_addr_long']]=='cajarecamara'):
                print(response)       
            if('rf_data' in response.keys()):
                try:
                    response['rf_data'] = response['rf_data'].decode('utf-8')
                    message = json.dumps({'device_type':'xbeebox', 'device_name':xbee_dict[response['source_addr_long']],
                        'source':response['source_addr_long'], 'type':'rf_data',
                        'content':response['rf_data']})
                    for elem in response['rf_data'].split('\r\n'):
                        try:
                            if(len(elem) > 0):
                                ev_split = elem.split(',')
                                event_type = ev_split[0]
                                payload = ev_split[3]
                                internal_id = ev_split[2]
                                units = ev_split[1]
                                if(event_type=='pir'):
                                    event_type ='motion'
                                    payload = int(payload)==1
                                place = device_settings[xbee_dict[response['source_addr_long']]]['place']
                                topic = "xbeebox/" + place + "/" + event_type + "/" + internal_id + "/" + xbee_dict[response['source_addr_long']] 
                                client.publish(topic, payload)
                                #print(topic)
                                #print(payload)
                        except:
                            print("xxError parsing element")
                            print(elem)
                except:
                    print("Error decoding xbee message")
                    
            if('samples' in response.keys()):
                #response['samples'] = response['rf_data'].decode('utf-8')
                #message = json.dumps({'device_type':'xbeebox', 'device_name':xbee_dict[response['source_addr_long']],
                #    'source':response['source_addr_long'], 'type':'samples',
                #    'content':response['samples']})
                place = device_settings[xbee_dict[response['source_addr_long']]]['place']
                topic = "xbeebox/" + place + "/samples" + "/" + xbee_dict[response['source_addr_long']] 
                payload = json.dumps(response['samples'])
                #print(response["samples"])
                print(topic)
                print(payload)
                client.publish(topic, payload)



if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        pass
