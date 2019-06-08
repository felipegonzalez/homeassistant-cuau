import appdaemon.plugins.hass.hassapi as hass
import json



class MotionLights(hass.Hass):


  def initialize(self):
    self.handle_group = {}
    self.grouping = json.loads(self.args["grouping"])
    print(self.grouping)
    motion_sensors = self.grouping.keys()
    # Subscribe to sensors
    for sensor in motion_sensors:
      self.handle_group[self.grouping[sensor]["lights"]] = None
      if('brightness' in self.grouping[sensor].keys()):
        brightness = self.grouping[sensor]['brightness']
      else:
        brightness = 255
      if('alt' in self.grouping[sensor].keys()):
        bright_alt = self.grouping[sensor]["alt"]['bright_alt']
        entity_alt = self.grouping[sensor]["alt"]['entity_alt']
        state_alt = self.grouping[sensor]["alt"]["state_alt"]
      else:
        bright_alt = None
        entity_alt = None
        state_alt = None
      self.listen_state(self.motion, sensor, 
                        group = self.grouping[sensor]["lights"], 
                        mode = self.grouping[sensor]["use_sleep"],
                        delay = self.grouping[sensor]["delay"],
                        brightness = brightness, entity_alt = entity_alt,
                        bright_alt = bright_alt, state_alt = state_alt)
  def motion(self, entity, attribute, old, new, kwargs):
    group = kwargs.get('group', None)
    use_sleep = kwargs.get('mode', None)
    delay = kwargs.get('delay', None)
    brightness = kwargs.get('brightness', None)
    bright_sleep = kwargs.get('bright_sleep', None)
    bright_alt = kwargs.get('bright_alt', None)
    entity_alt = kwargs.get('entity_alt', None)
    if new == "on" and old == "off":
      #if "entity_on" in self.args:
      self.log("Motion detected: turning {} on".format(group))
      #bright = 255
      if(self.get_state("input_boolean.sleep_mode")=="on" and use_sleep):
        brightness = 30
        if(bright_sleep is not None):
          brightness = bright_sleep
      if(entity_alt is not None):
        state_alt = self.get_state(entity_alt)
        if(state_alt != state_alt):
          brightness = bright_alt
      #  brightness = 30
      #  if(bright_sleep is not None):
      #    brightness = bright_tv

        #else:
        #  brightness = 30
      # if(self.get_state("input_boolean.watch_tv_mode")=="on" and use_sleep):
      #   if(bright_tv is not None):
      #     brightness = bright_tv
      #   else:
      #     brightness = 30
      #if(self.get_state("input_boolean.dark_house")=="on"):
      self.turn_on(group, brightness = brightness, transition = 0, kelvin = 2500)
      self.cancel_timer(self.handle_group[group])
    if new == "off" and old == "on":
      self.handle_group[group] = self.run_in(self.light_off, delay, group = group, sensor = entity)
  
  def light_off(self, kwargs):
    #if "entity_off" in self.args:
    group = kwargs.get('group', None)
    sensor = kwargs.get('sensor', None)
    transition = kwargs.get('transition', 30)
    #self.log()
    if(self.get_state(sensor) == 'off'):
      self.log("Turning {} off".format(group))
      self.turn_off(group, transition = transition)
      self.cancel_timer(self.handle_group[group])
      self.handle_group[group] = self.run_in(self.light_off, 60*5, transition = 0, group = group)
    #else:
    #  bright = 255
    #  self.turn_on(group, brightness = bright)
    #  self.cancel_timer(self.handle_group[group])
    #  self.handle_group[group] = self.run_in(self.light_off, 120, group = group, entity = entity)

  def cancel(self, kwargs):
    group = kwargs.get('group', None)
    self.cancel_timer(self.handle_group[group])
      
