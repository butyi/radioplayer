# radioplayer

CLI radio music player with configurable programme and cross mixing

## Introduction

First of all, this player is not a universal, "support-everything" player.
I have written only those function what I needed. I have idea what kind of
radio content I want. Since I haven't found easily a sufficient player, 
I decided I write exactly what I want. 
This was easier than search one by trying and get know several players.

## Requiremens

What I need are:
- Work without monitor, without mouse, without keyboard
- Work till the infinity without need of any user action
- Work from command line, without graphical interface
- Configurable by human readable text file
- Fade out some seconds at end of songs
- Start next song before previous has ended (mix them)
- Different type of songs to be played in different part of the day (programmes)
- Sometime jingle must be played also cross mixed with songs
- Write fresh info into a file about programme name, current song and next song
  for radio homepage.
- Scan the configured folders recursively.
- Choose random song from the defined folders.
- Remember some amount of already played songs and do not repeat them soon.
  Amount to be half of number of all songs in the current programme.
  
## Configuration

The script reads config.ini file as configuration. 
In this file there are sections and parameters.
There is one special section, the "Settings".
This settings contains general configurations. Now it is only one. 
- Songinfo text file path. This is optional.

Other sections are programmes. Name of section is name of the programme.
The programmes are proceeded from top to down. Later has higher priority, since
more bottom programme will overwrite prevoius in internal variables.
Program parameters are 

Programme sections have these sepection parameters
- Hours when the programme is played. This is list of hours separated by
  space.
  Optional. If not defined, programme will be played all day.
- Weekdays can also be defined. This is number list, where 0 means Monday.
  If defined, programme will only be played at that days of week.
  This is also a space separated list
  Optional. If not defined, programme will be each day of week.
- Days when the programme is played. This is list of days separated by
  space.
  Optional. If not defined, programme will be played on all days of month.
- Months when the programme is played. This is list of months separated by
  space.
  Optional. If not defined, programme will be played on all months.
- Folder path(s) of songs to be played. 9 path parameters are supported.
  Path1 - Path9. At least the first (Path1) definition is mandatory. Otherwise
  programme is not matched, so skipped.

When the above selection matches a programme, below parameters are updated if
those are defined. These parameters have default value, so not mandatory.
Furthermore, these are just updated when a programme matches. So, these
can be programme specific.

- FadeOut is length of fade down the end of song in seconds.
- StartNext is seconds of overlap of two consecutive songs.
- JinglePath is a path where jingles are stored.
- JinglePeriod is the minimum minutes between two jingles

## Script

Script reads in the configuration at each song change. It makes possible to edit
config file during playing. The change will be execured automatic without 
restart the script. 

I use ffplay to play. It decodes mp3 into a wav file in /tmp folder.
This will be played and deleted automatic after play has been finished. 

RadioPlayer now supports only mp3 files, since I call `AudioSegment.from_mp3`. 

## Preparation

I have prepared my mp3 files before using the RadioPlayer.

Split silence from start and end of songs. The next command will do it into
separate 'trim' subfolder. `find` is needed to not stop the batch command if
an mp3 file is faulty. *.mp3 solution will stop. Be careful, this also slitted
once my song at the middle, because there was a silent period in that.

`find . -type f -name '*.mp3' -print -exec mp3splt -r -o @f -d ./trim "{}" 2>&1 \; | tee ./trim.log`

Normalize volume of songs. The next command will do it. 
`find` is needed to not stop the batch command if an mp3 file is faulty. 
*.mp3 solution will stop. This command just update gain property in IDv3 tag.
Does not re-encode the mp3 files.

`find . -type f -name '*.mp3' -print -exec normalize-audio "{}" 2>&1 \; | tee ./gain.log`

Both command saves the stout and stderr into log file to see which files are faulty.

## Usage

- Install a command line mp3 player. I use ffmpeg. Google it how to install.
- Ensure mp3 files are on your file system. Let be your user name is "king".
  Copy some mp3 files into your home (/home/king) folder.
- Write/update the config.ini file with your specific settings.
  A minimum config what is just enough to work is:
  `[KingShuffle]\
  Path1 = /home/king`
- Start the script by `python play.py`

## Warranty

It does what it does, how it does. 
It works for me. Of course not all use cases or fault cases are handled. 
So it comes without any warranty. But feel free to improve it or fix it bugs.

## License

This is free. You can do anything you want with it.
While I am using Linux, I've got so many support from free projects,
I am happy if I can give something back to the community.

## Keywords

RadioPlayer, Radio Player, AutoDJ, mp3 Player, Script, Command Line, CLI,
Configurable, Mixer, No GUI, Linux, Raspberry Pi.

###### 2020 Janos BENCSIK


