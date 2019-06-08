import appdaemon.plugins.hass.hassapi as hass
import json
#import globals

#
# App to republish with retain door rf codes
#
#
# Version 1.0:
#   Initial Version




class DoorSensors(hass.Hass):


  def initialize(self):
    self.codes = {}
    self.rf_bridge = self.args["rf_bridge"]
    # Subscribe to rf changes
    self.handle = self.listen_state(self.get_code, entity = self.rf_bridge)
    self.codes = json.loads(self.args["codes"])
    
  def get_code(self, entity, attribute, old, new, kwargs):
    door_id = new[:5]
    if(door_id in self.codes.keys()):
      topic = self.codes[door_id]
      end_code = new[5]
      #tamper is B
      #low bat is other
      if(end_code == "E"):
        self.call_service("mqtt/publish", topic = topic, payload= "open",
          retain = True)
      if(end_code == "7"):
        topic = self.codes[door_id]
        self.call_service("mqtt/publish", topic = topic, payload = "closed",
          retain = True)
      if(end_code == "B"):
        # send notification of tamper
        self.call_service("persistent_notification/create", message = "Tamper alert on " + topic)
      if(end_code not in ["E","7","B"]):
        self.call_service("persistent_notification/create", message = "Low Battery on " + topic)
        # send check battery notification
    else:
      print("Unknown code: " + new)