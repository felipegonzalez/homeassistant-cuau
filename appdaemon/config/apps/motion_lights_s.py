import appdaemon.plugins.hass.hassapi as hass
import json



class MotionLights(hass.Hass):


  def initialize(self):
    # this dictionary keeps timers for groups
    self.timer_handle = {}
    self.manual = {}
    self.sleep_mode = self.get_state("input_boolean.sleep_mode")
    # data
    self.original_grouping = json.loads(self.args["grouping"])
    self.grouping = json.loads(self.args["grouping"])
    print(self.grouping)
    # Suscribe to sensors
    motion_sensors = self.grouping.keys()
    for zone in motion_sensors:
      self.manual[zone] = False
      self.timer_handle[zone] = None
      # set brightness states
      if('brightness' in self.grouping[zone].keys()):
        pass
      else:
        self.grouping[zone]["brightness"] = 255
        self.original_grouping[zone]["brightness"] = 255

      if("media" in self.grouping[zone].keys()):
        self.listen_state(self.adapt_brightness, self.grouping[zone]["media"])
      if("occupancy" in self.grouping[zone].keys()):
        self.listen_state(self.occupancy, self.grouping[zone]["occupancy"])
      # listen to motion sensors
      for ind_sensor in self.grouping[zone]["sensors"]:
        self.listen_state(self.motion, ind_sensor,
                        zone = zone, 
                        group = self.grouping[zone]["lights"], 
                        mode = self.grouping[zone]["use_sleep"],
                        delay = self.grouping[zone]["delay"])
    # listen to sleep mode and tv watching
    self.listen_state(self.adapt_brightness, "input_boolean.sleep_mode")

  def adapt_brightness(self, entity, attribute, old, new, kwargs):
    self.sleep_mode = self.get_state("input_boolean.sleep_mode")
    # when going into sleep mode:
    if(entity == "input_boolean.sleep_mode" and new == "on" and old == "off"):
      for sensor in self.grouping.keys():
        if(self.grouping[sensor]["use_sleep"] == "dim"):
          self.grouping[sensor]["brightness"] = 40
        if(self.grouping[sensor]["use_sleep"] == "dark"):
          self.turn_off(self.grouping[sensor]["lights"], transition = 20)
          self.grouping[sensor]["brightness"] = 0
    if(entity == "input_boolean.sleep_mode" and new == "off" and old == "on"):
      # restore brightness values
      for sensor in self.grouping.keys():          
        self.grouping[sensor]["brightness"] = self.original_grouping[sensor]["brightness"]
    
    #### # adapt brightness for tv watching
    if(not self.get_state("input_boolean.no_controlar_recamara")):
      if(entity == "media_player.bedroom" and self.sleep_mode == "off"):
        if(old == "playing"):
          self.manual["recamara"] = False
          self.grouping["recamara"]["brightness"] = 255
          self.grouping["bano_principal"]["brightness"] = 255
          self.grouping["vestidor"]["brightness"] = 255
        if(new == "playing"):
          self.manual["recamara"] = True
          self.grouping["recamara"]["brightness"] = 70
          self.grouping["bano_principal"]["brightness"] = 70
          self.grouping["vestidor"]["brightness"] = 70
        group = self.grouping["recamara"]["lights"]
        self.log("Adapting lights for TV watching in bedroom.")
        self.turn_on(group, brightness = self.grouping["recamara"]["brightness"], 
          transition = 30, kelvin = 2500)

  def occupancy(self, entity, attribute, old, new, kwargs):
    if(new > 0):
      self.grouping

  def motion(self, entity, attribute, old, new, kwargs):
    zone = kwargs.get('zone', None)
    group = kwargs.get('group', None)
    use_sleep = kwargs.get('mode', None)
    delay = kwargs.get('delay', None)
    if new == "on" and old == "off":
      self.log("Motion detected: turning {} on".format(zone))
      self.log("Sensor active: {}".format(entity))

      if(self.sleep_mode == "off" or use_sleep != "dark"):
        if(not self.manual[zone]):
          self.turn_on(group, brightness = self.grouping[zone]["brightness"], 
            transition = 0, kelvin = 2500)
      self.cancel_timer(self.timer_handle[zone])
    if new == "off" and old == "on":
      # set timer to turn off
      apagar = True
      # check all sensors
      for sensor in self.grouping[zone]['sensors']:
        if (self.get_state(sensor) == "on"):
          apagar = False
      if((not self.manual[zone]) and apagar):
        self.timer_handle[zone] = self.run_in(self.light_off, delay, zone=zone, group = group, sensor = entity)
  
  def light_off(self, kwargs):
    #if "entity_off" in self.args:
    zone = kwargs.get('zone', None)
    group = kwargs.get('group', None)
    sensor = kwargs.get('sensor', None)
    transition = kwargs.get('transition', 30)
    #self.log()
    if(self.get_state(sensor) == 'off'):
      self.log("Turning {} off".format(group))
      self.turn_off(group, transition = transition)
      self.cancel_timer(self.timer_handle[zone])
      self.timer_handle[zone] = self.run_in(self.light_off, 60*5, transition = 0, group = group)
    #else:
    #  bright = 255
    #  self.turn_on(group, brightness = bright)
    #  self.cancel_timer(self.handle_group[group])
    #  self.handle_group[group] = self.run_in(self.light_off, 120, group = group, entity = entity)

  def cancel(self, kwargs):
    group = kwargs.get('group', None)
   
      
