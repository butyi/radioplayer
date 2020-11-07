# radioplayer

CLI radio music player with configurable programme and cross mixing

## Introduction

First of all, this player is not a universal, "support-everything" player.
I have written only those function what I needed. I have idea what kind of
radio content I want. Since I haven't found easily such a player, I decided
I write exactly what I want. This was easier than search one by trying and
get know several players.

## Warranty

It does what it does, how it does. 
It works for me. Of course not all use cases or fault cases are handled. 
So it comes without any warranty. But feel free to improve it or fix it bugs.

## Requiremens

What I need are:
- Fade out some seconds at end of songs
- Start next song before previous has ended (mix them)
- Different type of songs to be played in different part of the day (programmes)
- Sometime jingle must be played also cross mixed
- Write fresh info into a file about programme name, current song and next song
  for radio homepage.
- Choose random song from the defined folder.

## Configuration

The script reads config.ini file as configuration. 
In this file there are sections and parameters.
There is one mandatory section, the "Settings".
This settings contains general configurations, like 
- Songinfo text file path
- Jingle settings (path of jingles, cross-fade parameters)

Other sections are programmes. Name of sections are name of programme.
The programmes are proceeded from top to down. Later has higher priority, since
more bottom programme will overwrite prevoius in internal variables. It also
means the first should be the default program. Special programmes should be
below.

Programme sections have these parameters
- Folder path of songs to be played
- Hours between the programme to be played. These are FirstHour and LastHour.
  If FirstHour=5 and LastHour=6, the programme will be played between 5:00 - 6:59.
  If FirstHour is not defined, default is 0.
  If LastHour is not defined, default is 23.
  If non of them are defined, programme will be played all day.
- Weekday can also be defined. This is number, where 0 means Monday.
  If defined, programme will only be played at that days of week.
  Only one defined day is supported.
  
The songs cross-fade parameters can be defined in both Settings and any programme.
If once is defined in Setting section, value will be used for all programmes.
Define different value for any specific programme. 
Thease are FadeOut and StartNext. Both are in seconds.
- FadeOut is length of fade down the end of song in seconds
- StartNext is seconds of overlap of two consecutive songs

## Script

Script reads in the configuration at each hour change. It makes possible to edit
config file during playing. The change will be execured automatic without 
restart the script. 

It decodes mp3 into a wav file in /tmp folder. This will be played, and deleted
automatic after it was played. 

Player now supports only mp3 files, since I call AudioSegment.from_mp3. You can
change it.

For selection simple random number is used. It means it is possible, the same
number is selected two times close to each other. I hope it will not happen too
often.

## Preparation

I have prepared my mp3 files.

Split silence from start and end of songs. The next command will do it into
separate 'trim' subfolder. `find` is needed to not stop the batch command if
an mp3 file is faulty. *.mp3 solution will stop.

`find . -type f -name '*.mp3' -print -exec mp3splt -r -o @f -d ./trim "{}" 2>&1 \; | tee ./trim.log`

Normalize volume of songs. The next command will do it. 
`find` is needed to not stop the batch command if an mp3 file is faulty. 
*.mp3 solution will stop.

`find . -type f -name '*.mp3' -print -exec normalize-audio "{}" 2>&1 \; | tee ./gain.log`

Both command saves the stout and stderr into log file to see which files are faulty.

## License

This is free. You can do anything you want with it.
While I am using Linux, I've got so many support from free projects,
I am happy if I can give something back to the community.

## Keywords

AutoDJ, mp3 player, script, command line, configurable.

###### 2020 Janos BENCSIK


