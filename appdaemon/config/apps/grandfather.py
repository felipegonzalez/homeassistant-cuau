import appdaemon.plugins.hass.hassapi as hass
from queue import Queue
import threading
import time
import os.path
import datetime


# Grandfather clock APP inspired by @areeshmu:
#
# https://community.home-assistant.io/t/grand-father-clock-chime/9465
#
# Implements a Grandfather clock that sounds chimes through a media player
#
# Args:
#
# player - media player to use for chimes
# volume - volume to use for chimes
# media - path to media files (see link above for download)
#
# Version 1.0:
#   Initial Version

class Grandfather(hass.Hass):

  def initialize(self):
   
    time = datetime.time(0, 0, 0)
    self.run_hourly(self.check_chime, time)
    
  def check_chime(self, kwargs):
    chime = True
    #self.verbose_log("Checking Chime")
    #if "mute_if_home" in self.args and self.get_state(self.args["mute_if_home"]) == "home":
      #self.verbose_log("Wendy is home")
    #  chime = False
    #if self.noone_home():
    #  #self.verbose_log ("No one is home")
    #  chime = False
    if not self.now_is_between(self.args["start_time"], self.args["end_time"]):
      #self.verbose_log("It's early or late")
      chime = False
    if chime:
      #self.verbose_log("Chiming")
      self.chime()
      
  def chime(self):
    hour = self.time().hour
    print(self.time())
    if hour > 12:
      hour = hour - 12
    media = "{0}/cuckoo-clock-{1:0=2d}.wav".format(self.args["media"], hour)
    sound = self.get_app("Sound")
    sound.play(path = media, content = "music", volume = self.args["volume"], length = 65)
    
    