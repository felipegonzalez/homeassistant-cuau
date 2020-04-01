import appdaemon.plugins.hass.hassapi as hass
import json



class MotionLights(hass.Hass):


  def initialize(self):
    # this dictionary keeps timers for groups
    self.timer_handle = {}
    self.sleep_mode = self.get_state("input_boolean.sleep_mode")
    # data
    self.original_grouping = json.loads(self.args["grouping"])
    self.grouping = json.loads(self.args["grouping"])
    print(self.grouping)
    # Suscribe to sensors
    motion_sensors = self.grouping.keys()
    for sensor in motion_sensors:
      self.timer_handle[self.grouping[sensor]["lights"]] = None
      # set brightness states
      if('brightness' in self.grouping[sensor].keys()):
        pass
      else:
        self.grouping[sensor]["brightness"] = 255
        self.original_grouping[sensor]["brightness"] = 255

      if("media" in self.grouping[sensor].keys()):
        self.listen_state(self.adapt_brightness, self.grouping[sensor]["media"])
      if("occupancy" in self.grouping[sensor].keys()):
        self.listen_state(self.occupancy, self.grouping[sensor]["occupancy"])
      # listen to motion sensors
      self.listen_state(self.motion, sensor, 
                        group = self.grouping[sensor]["lights"], 
                        mode = self.grouping[sensor]["use_sleep"],
                        delay = self.grouping[sensor]["delay"])
    # listen to sleep mode and tv watching
    self.listen_state(self.adapt_brightness, "input_boolean.sleep_mode")

  def adapt_brightness(self, entity, attribute, old, new, kwargs):
    self.sleep_mode = self.get_state("input_boolean.sleep_mode")
    # when going into sleep mode:
    if(entity == "input_boolean.sleep_mode" and new == "on"):
      for sensor in self.grouping.keys():
        if(self.grouping[sensor]["use_sleep"] == "dim"):
          self.grouping[sensor]["brightness"] = 40
        if(self.grouping[sensor]["use_sleep"] == "dark"):
          self.turn_off(self.grouping[sensor]["lights"], transition = 20)
          self.grouping[sensor]["brightness"] = 0
    if(entity == "input_boolean.sleep_mode" and new == "off"):
      # restore brightness values
      for sensor in self.grouping.keys():          
        self.grouping[sensor]["brightness"] = self.original_grouping[sensor]["brightness"]
    
    #### # adapt brightness for tv watching
    if(entity == "media_player.bedroom" and self.sleep_mode == "off"):
      if(old == "playing"):
        self.grouping["binary_sensor.motion_recamara"]["brightness"] = 255
        self.grouping["binary_sensor.motion_bano_principal"]["brightness"] = 255
        self.grouping["binary_sensor.motion_vestidor"]["brightness"] = 255
      if(new == "playing"):
        self.grouping["binary_sensor.motion_recamara"]["brightness"] = 50
        self.grouping["binary_sensor.motion_bano_principal"]["brightness"] = 50
        self.grouping["binary_sensor.motion_vestidor"]["brightness"] = 60
      group = self.grouping["binary_sensor.motion_recamara"]["lights"]
      self.log("Adapting lights for TV watching in bedroom.")
      self.turn_on(group, brightness = self.grouping["binary_sensor.motion_recamara"]["brightness"], 
          transition = 30, kelvin = 2500)

  def occupancy(self, entity, attribute, old, new, kwargs):
    if(new > 0):
      self.grouping

  def motion(self, entity, attribute, old, new, kwargs):
    group = kwargs.get('group', None)
    use_sleep = kwargs.get('mode', None)
    delay = kwargs.get('delay', None)
    if new == "on" and old == "off":
      self.log("Motion detected: turning {} on".format(group))
      if(self.sleep_mode == "off" or use_sleep != "dark"):
        self.turn_on(group, brightness = self.grouping[entity]["brightness"], 
          transition = 0, kelvin = 2500)
      self.cancel_timer(self.timer_handle[group])
    if new == "off" and old == "on":
      # set timer to turn off
      self.timer_handle[group] = self.run_in(self.light_off, delay, group = group, sensor = entity)
  
  def light_off(self, kwargs):
    #if "entity_off" in self.args:
    group = kwargs.get('group', None)
    sensor = kwargs.get('sensor', None)
    transition = kwargs.get('transition', 30)
    #self.log()
    if(self.get_state(sensor) == 'off'):
      self.log("Turning {} off".format(group))
      self.turn_off(group, transition = transition)
      self.cancel_timer(self.timer_handle[group])
      self.timer_handle[group] = self.run_in(self.light_off, 60*5, transition = 0, group = group)
    #else:
    #  bright = 255
    #  self.turn_on(group, brightness = bright)
    #  self.cancel_timer(self.handle_group[group])
    #  self.handle_group[group] = self.run_in(self.light_off, 120, group = group, entity = entity)

  def cancel(self, kwargs):
    group = kwargs.get('group', None)
   
      
