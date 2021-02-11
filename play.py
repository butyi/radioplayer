#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Docstring
"""Butyi's Python3 Auto-DJ RadioPlayer. It plays programme of my radio station."""

# Authorship information
__author__ = "Janos BENCSIK"
__copyright__ = "Copyright 2020, butyi.hu"
__credits__ = "James Robert (jiaaro) for pydub (https://github.com/jiaaro/pydub)"
__license__ = "GPL"
__version__ = "0.0.5"
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
import ftplib, io

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
TextOutFile = "" # Default path if not defined
TextOutFTPhost = ""
TextOutFTPport = 21
TextOutFTPpath = ""
TextOutFTPuser = ""
TextOutFTPpass = ""
Programme = "";
Paths = [] # Empty list for paths of songs
Jingles = [] # Empty list for jingles
JinglePath = ""
JinglePeriod = 15
Songs = [] # Empty list for songs
CurrentProgramme = "Not yet read in";
SongName = "Jingle.mp3"
CurrentSong = False
NextSong = False
JingleOverlap = 1 # Overlap of jingle and following song in secs
RecentlyPlayed = [] # Empty list for recently played songs to prevent soon repeat
LastJingleTimestamp = 0 # Start with a jingle
GaindB = 0 # Increase (os recrease) volume a bit may needed for direct USB connection of transmitter board
TargetGain = 0 # dynalic gain, different for each song
Normalize = False
LowPassFilterHz = 0
Artists = [] # Empty list for Artists
DebugConfigRead = False # Set True id you want to debug read and evaluation of config.ini
ProgrammeCheckDateTime = datetime.datetime.today()
CurrentSongLength = 0

CfgPath = os.path.dirname(sys.argv[0])+"/config.ini"
if not os.path.exists(CfgPath):
  print("ERROR! Cannot open ini file "+CfgPath)
  exit(1)

#
# CrossFade timings:
#
# volume
#  100% ^-----oldsong--\  |--newsong-----
#       |                \|
#       |                 |\
#       |                 |  \
#   0%  |                 |    \------.
#       |--------------------------------> time
# End of old song                     |
# Start of new song       |
# DropEnd                      |------|
# FadeOut              |-------|
# Overlap                 |----|
#
FadeOut = 8
DropEnd = 0
Overlap = 6


# Start playing
if __name__ == '__main__':

  # Start stopwatch to measure below code execution
  start = time.time()

  while True: # Play forever (exit: Ctrl+C)

    # Put programme name here into info text, because it may changed for next song
    infotext = CurrentProgramme

    # Calculate start of next song. This moment to be used to check the current programme
    if CurrentSong != False:
      CurrentSongLength = (len(CurrentSong)/1000) - Overlap
      ProgrammeCheckDateTime = datetime.datetime.today() + datetime.timedelta(seconds=CurrentSongLength)

    # Read config to know which programme to be played
    c = configparser.ConfigParser(inline_comment_prefixes=';')
    c.read(CfgPath)
    for section in c._sections :
      if DebugConfigRead:
        print("Section "+section)
      if section == "Settings":
        if c.has_option(section, 'textoutfile'):
          TextOutFile = c.get(section, 'textoutfile')
        if c.has_option(section, 'textoutftphost'):          TextOutFTPhost = c.get(section, 'textoutftphost')
        if c.has_option(section, 'textoutftpport'):
          TextOutFTPport = c.getint(section, 'textoutftpport')
        if c.has_option(section, 'textoutftppath'):
          TextOutFTPpath = c.get(section, 'textoutftppath')
        if c.has_option(section, 'textoutftpuser'):
          TextOutFTPuser = c.get(section, 'textoutftpuser')
        if c.has_option(section, 'textoutftppass'):
          TextOutFTPpass = c.get(section, 'textoutftppass')
        if c.has_option(section, 'lowpassfilterhz'):
          LowPassFilterHz = c.getint(section, 'lowpassfilterhz')
        if c.has_option(section, 'gaindb'):
          GaindB = c.getint(section, 'gaindb')
        if c.has_option(section, 'normalize'):
          Normalize = True
        continue
      if c.has_option(section, 'months'):
        if str(ProgrammeCheckDateTime.month) not in c.get(section, 'months').split():
          continue
      if c.has_option(section, 'days'):
        if str(ProgrammeCheckDateTime.day) not in c.get(section, 'days').split():
          continue
      if c.has_option(section, 'weekdays'):
        if str(ProgrammeCheckDateTime.weekday()) not in c.get(section, 'weekdays').split():
          continue
      if c.has_option(section, 'hours'):
        if str(ProgrammeCheckDateTime.time().hour) not in c.get(section, 'hours').split():
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
      if c.has_option(section, 'dropend'):
        DropEnd = c.getint(section, 'dropend')
      if c.has_option(section, 'overlap'):
        Overlap = c.getint(section, 'overlap')
      if c.has_option(section, 'jinglepath'):
        JinglePath = c.get(section, 'jinglepath')
      if c.has_option(section, 'jingleperiod'):
        JinglePeriod = c.getint(section, 'jingleperiod')
      if c.has_option(section, 'jingleoverlap'):
        JingleOverlap = c.getint(section, 'jingleoverlap')

      if DebugConfigRead:
        print("  Program:  "+Programme)
        print("  Paths:  "+str(Paths))
        print("  DropEnd:  "+str(DropEnd))
        print("  FadeOut:  "+str(FadeOut))
        print("  Overlap:  "+str(Overlap))
        print("  JinglePath:  "+JinglePath)
        print("  JinglePeriod:  "+str(JinglePeriod))

    if Programme != CurrentProgramme: # When programme changed
      CurrentProgramme = Programme

      # Read jingles in
      if 0 < len(JinglePath):
        for cp, folders, files in os.walk(JinglePath):
          for fi in files:
            if fi.endswith(".mp3"):
              Jingles.append(os.path.join(cp, fi))

      # Clear list for songs
      del Songs[:]

      # Go through all defined Paths to parse songs
      for Path in Paths:

        # Recursive walk in folder
        #Songs = glob.glob("**/*.mp3", recursive=True) # for <= Python 3.5
        for cp, folders, files in os.walk(Path):
          for fi in files:
            if fi.endswith(".mp3"):
              Songs.append(os.path.join(cp, fi))

      # Decrease played list when switch to a folder which contains less songs than before
      while (len(Songs)/2) < len(RecentlyPlayed): # If list is longer than half of songs
        RecentlyPlayed.pop(0) # Drop oldest elements

    # Update infotext
    infotext += "\n" + os.path.basename(SongName)[:-4]
    RecentlyPlayed.append(os.path.basename(SongName)) # Add now playing
    if (len(Songs)/2) < len(RecentlyPlayed): # If list is full
      RecentlyPlayed.pop(0) # Drop oldest element
    while True: # Search a song not in RecentlyPlayed list
      SongName = Songs[random.randrange(0,len(Songs))]
      if os.path.basename(SongName) not in RecentlyPlayed:
        # Ensure to not play consecutive two songs from the same artists
        NewArtists = os.path.basename(SongName).split(" - ")[0].split(" Ft. ")
        Union = set(Artists) & set(NewArtists)
        if 0 == len(Union): # If artist is different
          Artists = NewArtists # Save this artist(s) for next check
          break # Fount the next song

    # Continue to prepare info text
    infotext += "\n" + os.path.basename(SongName)[:-4]
    infotext += "\n" + str(CurrentSongLength) + "\n"

    if CurrentSong != False:
      # Write infotext to stdout
      print("\n\n" + infotext + "\n")

      # Write infotext into file
      if 0 < len(TextOutFile): # If song info is configured to write into a file too
        if 0 < len(TextOutFTPhost) and 0 < len(TextOutFTPuser) and 0 < len(TextOutFTPpass): # FTP write is configured
          ftpsession = ftplib.FTP()
          ftpsession.connect(TextOutFTPhost,TextOutFTPport)
          ftpsession.login(TextOutFTPuser,TextOutFTPpass)
          if 0 < len(TextOutFTPpath):
            ftpsession.cwd(TextOutFTPpath)
          ftpsession.storbinary('STOR '+TextOutFile,io.BytesIO(bytearray(infotext,'utf-8'))) # Update file content
          ftpsession.quit() # Close FTP
        else: # Simple local filesystem write
          with open(TextOutFile, 'w') as f:
            f.write(infotext)

    # Pre-load mp3 to eliminate delay
    NextSong = AudioSegment.from_mp3(SongName) # Load song
    if 0 < DropEnd:
      NextSong = NextSong[:(len(NextSong)-(DropEnd*1000))] # drop end of song
    NextSong = NextSong.fade_out(FadeOut*1000) # Fade out at end

    # Cut high frequency (from 12 kHz) to not disturb 19kHz pilot signal.
    #   This is slow and cause high resource usage for 10-20s each song on my laptop.
    #   I am affraid it will take more time on a smaller hardware like Raspberry Pi
    #   So, instead I propose to prepare all mp3 files with some low pass filter.
    if 0 < LowPassFilterHz:
      NextSong = NextSong.low_pass_filter(LowPassFilterHz)

    TargetGain = GaindB
    if Normalize:
      TargetGain -= NextSong.dBFS;
    if 0 != TargetGain:
      NextSong = NextSong.apply_gain(TargetGain)

    # Wait till start of next song
    if CurrentSong != False:
      SleepTime = (len(CurrentSong)/1000) - Overlap - int((time.time()-start))
      if 0 < SleepTime:
        time.sleep(SleepTime)

    # if there was no jingle since jingleperiod minutes, play once before next song
    if 0 < len(Jingles) and 0 < JinglePeriod:
      if (LastJingleTimestamp+(60*JinglePeriod)) < int(time.time()):
        rnd = int(time.time()) % len(Jingles)
        jin = Jingles[rnd]; # Choose a jingle
        jin = AudioSegment.from_mp3(jin) # Load the choosen jingle
        TargetGain = GaindB
        if Normalize:
          TargetGain -= jin.dBFS;
        TargetGain -= 3 # Be a bit less loud than the music
        if 0 != TargetGain:
          jin = jin.apply_gain(TargetGain)
        MusicPlayer(jin).start() # Play jingle in a separate thread
        time.sleep((len(jin)/1000)-JingleOverlap) # wait to finish the jingle
        LastJingleTimestamp = time.time()

    # Start stopwatch to measure below code execution
    start = time.time()

    # Start playing the next song in a separate thread
    CurrentSong = NextSong
    MusicPlayer(CurrentSong).start()


