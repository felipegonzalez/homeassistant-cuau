import appdaemon.plugins.hass.hassapi as hass
import json
import requests
import datetime

headers = {'Content-Type' : 'application/x-www-form-urlencoded'}

class APSystems(hass.Hass):


  def initialize(self):
    self.ecu_id = self.args["ecu_id"]
    self.url = "http://api.apsystemsema.com:8073/apsema/v1/ecu/getPowerInfo"
    self.date_today = datetime.datetime.now().strftime("%Y%m%d")
    self.data = {"ecuId":self.ecu_id, "filter":"power", "date":self.date_today}
    # Subscribe to rf changes
    time = datetime.datetime.now()
    self.handle = self.run_every(self.update, time, 60*6)
    self.last_time = 0
    self.last_power =  0
    self.power_today = 0
    self.last_time_data = 0

  def update(self, entity):
    self.log("Calling apsystems")
    self.date_today = datetime.datetime.now().strftime("%Y%m%d")
    self.data = {"ecuId":self.ecu_id, "filter":"power", "date":self.date_today}
    response = requests.post(self.url, data = self.data, headers = headers)
    self.log(response)
    if(response.status_code == 200):
        json_response = json.loads(response.text)
        if(json_response["code"] == "1"):
            self.log("Got code 1, parsing...")
            data = json_response["data"]
            power = json.loads(data["power"])
            times = json.loads(data["time"])
            self.last_time_data = times[-1]
            self.last_power = power[-1]
            print(power)
            self.power_today = sum(list(map(int, power))) / 12
        else:
            self.last_power = 0
            self.power_today = -1
        self.set_state("sensor.pv_power_today_appd", state = self.power_today)
        if(self.last_time_data != self.last_time):
            self.last_time = self.last_time_data
        self.log("Got PV power reading:  {}".format(self.last_power))
        #self.log(self.date_today)
        self.log("Updating PV sensor in hass")
        self.set_state("sensor.pv_power", state = self.last_power)

            