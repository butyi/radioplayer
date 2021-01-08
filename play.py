#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Docstring
"""Butyi's Python3 Auto-DJ RadioPlayer. It plays programme of my radio station."""

# Authorship information
__author__ = "Janos BENCSIK"
__copyright__ = "Copyright 2020, butyi.hu"
__credits__ = "James Robert (jiaaro) for pydub (https://github.com/jiaaro/pydub)"
__license__ = "GPL"
__version__ = "0.0.3"
__maintainer__ = "Janos BENCSIK"
__email__ = "radioplayer@butyi.hu"
__status__ = "Prototype"

# Import section
import time, glob, random, os, threading, datetime, sys
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread
from threading import Event
import configparser

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

# define global variables
ScriptPath = os.getcwd()
TextOutFile = "" # Default path if not defined
Programme = "";
Paths = [] # Empty list for paths of songs
FadeOut = 8
StartNext = 6
JinglePath = ""
JinglePeriod = 15
Songs = [] # Empty list for songs
CurrentProgramme = "Not yet read in";
SongName = "Jingle.mp3"
CurrentSong = False
JingleStartNext = 1 # Overlap of jingle and following song in secs
RecentlyPlayed = [] # Empty list for recently played songs to prevent soon repeat
LastJingleTimestamp = 0 # Start with a jingle
GaindB = 0 # Increase (os recrease) volume a bit may needed for direct USB connection of transmitter board
TargetGain = 0 # dynalic gain, different for each song
Normalize = False
LowPassFilterHz = 0
Artists = [] # Empty list for Artists

# Start playing
if __name__ == '__main__':
  while True: # Play forever (exit: Ctrl+C)

    # Start code execution stopwatch
    start = time.time()

    # Put programme name here into info, because it may changed for next song
    infotext = CurrentProgramme

    # Read config to know which programme to be played
    c = configparser.ConfigParser(inline_comment_prefixes=';')
    c.read(os.path.dirname(sys.argv[0])+"/config.ini")
    for section in c._sections :
      if section == "Settings":
        if c.has_option(section, 'textoutfile'):
          TextOutFile = c.get(section, 'textoutfile')
        if c.has_option(section, 'lowpassfilterhz'):
          LowPassFilterHz = c.getint(section, 'lowpassfilterhz')
        if c.has_option(section, 'gaindb'):
          GaindB = c.getint(section, 'gaindb')
        if c.has_option(section, 'normalize'):
          Normalize = True
        continue
      if c.has_option(section, 'months'):
        if str(datetime.datetime.today().month) not in c.get(section, 'months').split():
          continue
      if c.has_option(section, 'days'):
        if str(datetime.datetime.today().day) not in c.get(section, 'days').split():
          continue
      if c.has_option(section, 'weekdays'):
        if str(datetime.datetime.today().weekday()) not in c.get(section, 'weekdays').split():
          continue
      if c.has_option(section, 'hours'):
        if str(datetime.datetime.today().time().hour) not in c.get(section, 'hours').split():
          continue
      if not c.has_option(section, 'path1' ):
        continue
      Programme = section;
      del Paths[:];
      for x in range(1,10):
        if c.has_option(section, 'path'+str(x) ):
          Paths.append( c.get(section, 'path'+str(x) ) )
      if c.has_option(section, 'fadeout'):
        FadeOut = c.getint(section, 'fadeout')
      if c.has_option(section, 'startnext'):
        StartNext = c.getint(section, 'startnext')
      if c.has_option(section, 'jinglepath'):
        JinglePath = c.get(section, 'jinglepath')
      if c.has_option(section, 'jingleperiod'):
        JinglePeriod = c.getint(section, 'jingleperiod')

      if False: # Set True to debug programme selection
        print("After section "+section)
        print("  Program:  "+Programme)
        print("  Paths:  "+str(Paths))
        print("  FadeOut:  "+str(FadeOut))
        print("  StartNext:  "+str(StartNext))
        print("  JinglePath:  "+JinglePath)
        print("  JinglePeriod:  "+str(JinglePeriod))

    if Programme != CurrentProgramme: # When programme changed
      CurrentProgramme = Programme

      # Read jingles in
      if 0 < len(JinglePath):
        os.chdir(JinglePath)
        jingles = glob.glob("*.mp3")

      # Clear list for songs
      del Songs[:]

      # Go through all defined Paths to parse songs
      for Path in Paths:

        # Jump into path
        os.chdir(Path)

        # Recursive walk in folder
        #Songs = glob.glob("**/*.mp3", recursive=True) # for <= Python 3.5
        for cp, folders, files in os.walk(Path):
          for fi in files:
            if fi.endswith(".mp3"):
              Songs.append(os.path.join(cp, fi))

      # Clear recently played list
      del RecentlyPlayed[:]

    # Update infotext
    infotext += "\n" + os.path.basename(SongName)[:-4]
    RecentlyPlayed.append(os.path.basename(SongName)) # Add now playing
    if (len(Songs)/2) < len(RecentlyPlayed): # If list is full
      RecentlyPlayed.pop(0) # Drop oldest element
    while True: # Search a song not in RecentlyPlayed list
      SongName = Songs[random.randrange(0,len(Songs))]
      if os.path.basename(SongName) not in RecentlyPlayed:
        NewArtists = os.path.basename(SongName).split(" - ")[0].split(" Ft. ")
        Union = set(Artists) & set(NewArtists)
        if 0 == len(Union):
          Artists = NewArtists
          break
    infotext += "\n" + os.path.basename(SongName)[:-4] + "\n"
    print("\n\n" + infotext + "\n")

    # Write infotext into file
    if 0 < len(TextOutFile):
      with open(TextOutFile, 'w') as f:
        f.write(infotext)

    # Pre-load mp3 to eliminate delay
    songofwait = CurrentSong
    CurrentSong = AudioSegment.from_mp3(SongName) # Load song
    CurrentSong = CurrentSong.fade_out(FadeOut*1000) # Fade out at end

    # Cut high frequency (from 12 kHz) to not disturb 19kHz pilot signal.
    #   This is slow and cause high resource usage for 10-20s each song on my laptop.
    #   I am affraid it will take more time on a smaller hardware like Raspberry Pi
    #   So, instead I propose to prepare all mp3 files with some low pass filter.
    if 0 < LowPassFilterHz:
      CurrentSong = CurrentSong.low_pass_filter(LowPassFilterHz)

    TargetGain = GaindB
    if Normalize:
      TargetGain -= CurrentSong.dBFS;
    if 0 != TargetGain:
      CurrentSong = CurrentSong.apply_gain(TargetGain)

    # Wait till start of next song
    if songofwait != False:
      sleeptime = (len(songofwait)/1000) - StartNext - int((time.time()-start))
      if 0 < sleeptime:
        time.sleep(sleeptime)

    # if there was no jingle since jingleperiod minutes, play once before next song
    if 0 < len(JinglePath):
      if (LastJingleTimestamp+(60*JinglePeriod)) < int(time.time()):
        rnd = int(time.time()) % len(jingles)
        jin = JinglePath + "/" + jingles[rnd]; # Choose a jingle
        jin = AudioSegment.from_mp3(jin) # Load the choosen jingle
        TargetGain = GaindB
        if Normalize:
          TargetGain -= jin.dBFS;
        TargetGain -= 3 # Be a bit less loud than the music
        if 0 != TargetGain:
          jin = jin.apply_gain(TargetGain)
        MusicPlayer(jin).start() # Play jingle in a separate thread
        time.sleep((len(jin)/1000)-JingleStartNext) # wait to finish the jingle
        LastJingleTimestamp = time.time()

    MusicPlayer(CurrentSong).start() # Play next song in a separate thread


