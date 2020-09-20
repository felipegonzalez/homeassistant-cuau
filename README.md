# Homeassistant configuration for our house.

Our home automation is based on [Home Assistant](https://www.home-assistant.io/), with 
some [AppDaemon](https://appdaemon.readthedocs.io/en/latest/) apps and some other
python apps to listen to [Xbee](https://www.digi.com/xbee) radios and other wifi sensors.
For our CCTV server we use [xeoma](https://felenasoft.com/xeoma/en/).

## Devices

- Macbook Pro 2011 running Home Assistant
- MacMini 7,1 Late 2014 (Ubuntu) running [xeoma](https://felenasoft.com/xeoma/en/)
- iMac running [doods](https://github.com/snowzach/doods/) for image recognition
- Orbi AC3000 wireless Access point with Satellite
- Airport Extreme 
- Ring Doorbell Pro
- Apple TV (x2)
- Sonos 1 and 3
- Amazon Echo
- Amazon Echo dot (x3)
- Philips Hue lights (x32)
- Gas tank level reader with Wyze cam 2 and custom image processing
- [Kerui Avantgarde Door Windows Detector](https://www.amazon.com/gp/product/B011HOL9A2/) (x5)
- [Sonoff Rf bridge](https://www.amazon.com/Sonoff-Bridge-433-Controllors-Controllor/dp/B076D7Q4J9) with [Tasmota](https://github.com/arendst/Sonoff-Tasmota) firmware
- [Sonoff 4Ch switch](https://www.amazon.com/Sonoff-4CH-Appliances-independently-Compatible/dp/B071JB5LXR) with Tasmota
- Sonoff basic with Tasmota  or ESPhome (x8)
- Sonoff Pow with Tasmota(x1)
- Sonoff s31 with Tasmota (x4)
- Sonoff Touch switches (x2)
- [Zigbee Adafruit adapter](https://www.adafruit.com/product/247) with Zigbee acting as hub
- Custom made Arduino + Zigbee multisensor/controller (x12)
- Raspberry Pi 2 with Camera (x2) running [motion](https://motion-project.github.io/)
- Foscam IP cameras (x2)
- BC1-2MP IP PoE cameras (x2)
- [Amcrest PoE dome camera IP4M-1028E](https://www.amazon.com/gp/product/B073V5T4SY)
- [Wyze cam V2](https://www.wyze.com/product/wyze-cam-v2/) (x2)
- Custom made garden beds irrigation system (Zigbee)
- Custom made garden irrigation system (esp8266)
- Custom made RF garage door opener
- Custom made water level sensor (ultrasonic)
- Custom made weather station
- Custom made pool pump controller with water temperature sensor
- Weather station [Ambient Weather WS-2902](https://www.ambientweather.com/amws2902.html)
- Custom hacked roller blinds remote control
- Google CloudSQL with dumps to BigQuery (via [Stitch](https://www.stitchdata.com/))
