#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Docstring
"""Butyi's Python Auto-DJ Radio Player. It plays programme of my radio station."""

# Authorship information
__author__ = "Janos BENCSIK"
__copyright__ = "Copyright 2020, butyi.hu"
__license__ = "GPL"
__version__ = "0.0.0"
__maintainer__ = "Janos BENCSIK"
__email__ = "padp@butyi.hu"
__status__ = "Prototype"

# Import section
import time, glob, os, random, threading, datetime
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread
from threading import Event
from ConfigParser import ConfigParser

# Code
version = "V0.00 2020.10.30.";
scriptpath = os.getcwd()

# Subfunctions, classes
class MusicPlayer(Thread):
    def __init__(self, song):
        Thread.__init__(self)
        self.song = song
        self._stopper = Event()
        self.setName('MusicThread')
    def run(self):
        play(self.song)
    def stop(self):
        self._stopper.set()

def ReadConfig():
  c = ConfigParser()
  c.read(scriptpath+"/config.ini")
  fadeout = 10
  startnext = 8
  ret = dict.fromkeys(range(24), {"name":"","path":"","fadeout":fadeout,"startnext":startnext})
  for section in c._sections :
    if c.has_option(section, 'fadeout'):
      fadeout = c.getint(section, 'fadeout')
    if c.has_option(section, 'startnext'):
      startnext = c.getint(section, 'startnext')
    if not c.has_option(section, 'path'): continue
    Path = c.get(section, 'path')  
    if c.has_option(section, 'weekday'):
      if c.getint(section, 'weekday') != datetime.datetime.today().weekday(): continue
    FirstHour = 0
    if c.has_option(section, 'firsthour'):
      FirstHour = c.getint(section, 'firsthour')
    LastHour = 23
    if c.has_option(section, 'lasthour'):
      LastHour = c.getint(section, 'lasthour')
    if FirstHour <= LastHour:
      for h in range(FirstHour, LastHour+1):
        ret[h] = {"name":section,"path":Path,"fadeout":fadeout,"startnext":startnext}
    else: # Day overflow
      for h in range(FirstHour, 24):
        ret[h] = {"name":section,"path":Path,"fadeout":fadeout,"startnext":startnext}
      for h in range(0, LastHour+1):
        ret[h] = {"name":section,"path":Path,"fadeout":fadeout,"startnext":startnext}
  return {"settings":dict(c.items("Settings")), "programme":ret[datetime.datetime.today().time().hour]}



# Save hour for step hour detection
prevhour = datetime.datetime.today().time().hour
lastjingle = 0

# Select current programme
config = ReadConfig()
CurrentPath = config["programme"]["path"];

# Read jingles in
os.chdir(config["settings"]["jinglepath"])
jingles = glob.glob("*.mp3")

# Read songs in and select first a random one
os.chdir(CurrentPath)
songs = glob.glob("*.mp3")
song = songs[random.randrange(0,len(songs))]

# Load first mp3
s = AudioSegment.from_mp3(CurrentPath + "/" + song) # Load song
s = s.fade_out(config["programme"]["fadeout"]*1000)

# Start playing
if __name__ == '__main__':
  while True: # Play forever (exit: Ctrl+C)

    # if there was no jingle since jingleperiod minutes, play once before next song 
    if (lastjingle+(60*int(config["settings"]["jingleperiod"]))) < int(time.time()):
      sig = AudioSegment.from_mp3(config["settings"]["jinglepath"] + "/" + jingles[random.randrange(0,len(jingles))]) # Load a jingle
      MusicPlayer(sig).start() # Play jingle in a separate thread
      time.sleep((len(sig)/1000)-int(config["settings"]["jinglestartnext"])) # wait to finish the jingle
      lastjingle = time.time()
      codeexecutiontime = 0 # Is this needed?????

    start = time.time() # Start code execution stopwatch
    MusicPlayer(s).start() # Play next song in a separate thread

    # Put programme name here into info, because it may changed for next song
    infotext = "Programme: " + config["programme"]["name"]

    # Check current hour here, update songs array if needed
    currenthour = datetime.datetime.today().time().hour
    if prevhour != currenthour: # When hour changed
      config = ReadConfig()
      if CurrentPath != config["programme"]["path"]: # When programme changed
        CurrentPath = config["programme"]["path"];
        os.chdir(CurrentPath)
        songs = glob.glob("*.mp3")
      prevhour = currenthour

    # Update infotext
    infotext += "\nNow playing: " + song[:-4]
    song = songs[random.randrange(0,len(songs))] # Choose next song
    infotext += "\nNext song: " + song[:-4] + "\n"
    print("\n\n" + infotext + "\n")

    try:
      f = open(config["settings"]["textoutfile"], "w")
      f.write(infotext)
      f.close()
    except OSError as err:
      print("OS error: {0}".format(err))
    except:
      print("Unexpected error:", sys.exc_info()[0])
      raise

    # Pre-load mp3 to eliminate delay
    currentsong = s
    s = AudioSegment.from_mp3(CurrentPath + "/" + song) # Load song
    s = s.fade_out(config["programme"]["fadeout"]*1000)

    # Wait till start of next song
    time.sleep((len(currentsong)/1000) - config["programme"]["startnext"] - int((time.time()-start)))

