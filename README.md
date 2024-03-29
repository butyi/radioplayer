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
  for radio homepage by FTP upload.
- Scan the configured folders recursively.
- Choose random song from the defined folders.
- Remember some amount of already played songs and do not repeat them soon.
  Amount to be half of number of all songs in the current programme.
- Do not repeat the last 10 artists
- Ensure similar volume for playing
  
## Configuration

The script reads config.ini file as configuration. 
In this file there are sections and parameters.
There is one special section, the "Settings".
This settings contains general configurations. Now it is only one. 
- TextOutFile is songinfo text file path. This is optional.
  - Script also optionally supports to upload Songinfo text file into some webpage by FTP.
    By this feature your webpage can show up to date info which song is playing currently and which will be the next one.
    To use FTP upload feature simple define at least TextOutFTPhost, TextOutFTPuser, TextOutFTPpass.
    If your FTP port is not the defined 21, you can define other by TextOutFTPport.
    If your file to be uploaded not the root folder of FTP, you can define path by TextOutFTPpath.
- HistoryFile is an optional text file path for logging played songs with timestamp.
- ErrLogFile is an optional log file for already handled errors. Even though the error is handled
  make sense to know to fix the root cause later if possible.
- GaindB is constant volume adjustment possibility during playing. This is optional.
- LowPassFilterHz to be used when your songs are not prepared to eliminate
  interference between song high frequencies and 19kHz pilot signal of
  stereo FM transmission. 
  Be carefull, this can take a long time (10-30s for a usual song).
  This can be done in the background while the current song is playig,
  but the problem is if your hardware is slow and the current song is
  shorter than the length of filer algorithm. In this case, there will
  be silent gap in the programme.
  This is also optional.
  Preparation is better instead of this on the fly filter.
- RootPath is an optional path for common part of path of songs of programmes

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
  programme is not matched, so skipped. RootPath is considered for each paths.

When the above selection matches a programme, below parameters are updated if
those are defined. These parameters have default value, so not mandatory.
Furthermore, these are just updated when a programme matches. So, these
can be programme specific.

- DropEnd is seconds to be removed from end of song before fadeout is calculated
- FadeOut is length of fade down the end of song in seconds.
- Overlap is seconds of overlap of two consecutive songs.
- JinglePath is a path where jingles are stored.
- JinglePeriod is the minimum minutes between two jingles. If JinglePeriod = 0, jingle will never be played.
- JingleOverlap is overlap of jingle and following song in secs

## Script

Script reads in the configuration at each song change. It makes possible to edit
config file during playing. The change will be execured automatic without 
restart the script. 

I use ffplay to play. It decodes mp3 into a wav file in /tmp folder.
This will be played and deleted automatic after play has been finished. 

RadioPlayer now supports only mp3 files, since I call `AudioSegment.from_mp3`. 

## Preparation of songs

First you may need to install below tools, if you haven't installed before
- `sudo apt install exiftool pcregrep lame mp3splt`
- `sudo snap install mp3gain`

I have prepared my mp3 files before using by the RadioPlayer.
Preparation was done by `psrt.sh`. 
I have executed this bash file in the folder where songs are.
Preparation overwrites the original mp3 files, so be careful.

Main activities of preparation are:
- Test file errors in song files
- Resample to 32kHz to limit frequencies at 16kHz
- Normalize volume
- Apply additional low pass filter for better high frequencies
- Trim silent and quiet part from begin and end of songs for better cross-fade

For more details, see my comments in the bash file

There are naming and other rules and restrictions regarding MP3 files:
- Only mp3 format is supported
- Each words shall be started by capital letters 
- Each contributors (actors) shall be separated by "Ft."
- Hungarian or other accents are not allowed, only English letters are allowed
- ".mp3" file extension shall be lowercase

Naming convention can be checked by calling script `php checksongs.php ~/synas/music/radio/`.
Same content mp3 files with different names can be searched by script `php search_same_md5.php ~/synas/music/radio/`.
Of course, this path of music files is only valid for me. Change it according to your environment. 

## Prerequisites

- Install raspbian lite image to SD card
- By `sudo raspi-config` change password, set time zone, set keyboard layout, enable SSH, disable other interfaces
- Install git by `sudo apt install git` if `git --version` does not show some available revision
- `cd` to go to home folder
- `mkdir repos` to create repos subfolder
- `cd repos` to go into repos subfolder
- `sudo apt install git`
- Clone the script by `git clone https://github.com/butyi/radioplayer` (note this will istall the script under a radioplayer subfolder)
- Install python3 by `sudo apt install python3` if `python3 --version` does not show some available revision
- If you do not yet have pip, install it by `sudo apt install python3-pip`
- You need to install pydub using pip by `pip3 install pydub`
- Set python3 as default python by `sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1`
  and check it by `sudo update-alternatives --config python`
- Install at least ffmpeg by `sudo apt install ffmpeg` to be a player on the system

## Usage

- Ensure mp3 files are on your file system. For example if your user name is "king".
  Copy some mp3 files into a foled in your home (e.g. /home/king/repos/radioplayer/music).
- Write/update the config.ini file with your specific settings.
  A minimum config what is just enough to work is:
  `[KingShuffle]`<br>`Path1 = /home/king/repos/radioplayer/music`
- Start the script by `python3 play.py`

## Radio station on Raspberry Pi
Of course I have installed the player on a Raspberry Pi. Now I have RPi 4 with 4GB RAM.
The following steps I have made to get it work:
- Steps in Prerequisites paragraph
- If you use USB sound card, you can set it as default this way:
  - Check card numbers by `aplay -l`
  - Set your card ad default in file `sudo nano ~/.asoundrc`
  - Important, On Raspberry Pi USB audio devices do not support to be open device more times, therefore cross-mix does not work.
    In this case, to prevent "cannot open, device busy" error, set Overlap parameters to zero in config. See [this topic][1].
- Set device audio output to 3.5mm jack by select 'Headphone' in raspi-config.
  Check it by `amixer` to see which is the current output. In my case `Simple mixer control 'Headphone',0`.
  Note that while there is connected HDMI monitor with integrated sound, Raspberry Pi may put music to monitor and not to 3.5mm jack.
  But when I removed the monitor (stand-alone operation), music came out on 3.5mm jack.
- Volume setting 
  - `amixer set Headphone -- 96%`
  - minus 10 dB in config.ini 
  are sufficient for me.
- Enable SSH in raspi-config interface settings.
- Get know RPi IP address
  `hostname -I`
- Connect to rpi from PC
  - `ssh pi@192.168.0.137`
  - Most likely you need to create/update RSA key for SSH
- Copy (or update) songs to RPi through SSH
  `rsync -luvrt --delete -e ssh /home/butyi/synas/music/radio/* pi@192.168.0.137:/home/pi/synas/music/radio`
- Test the player manually by steps in Usage paragraph
- Now, create the bash file which will be called at boot
  - `cd`
  - `nano boot.sh`
  - Add these lines:
    - `#!/bin/bash`
    - `sleep 15` to be time to have everything initialized, especially the audio device.
    - `amixer set Headphone -- 96%` to set system volume
    - `python /home/pi/repos/radioplayer/play.py` start the player
  - `chmod +x boot.sh` to set it as executable
- Try `boot.sh` script by call it: `./boot.sh`
- To start `boot.sh` script at boot as a demon, add this line `@reboot ./home/pi/boot.sh > /dev/null 2>&1 &` to crontab (`crontab -e`).
  Last & is to run the script in the background, so that the Pi will boot as normal.
- Try it by reboot RPi `sudo reboot now`.
- Finally set only read memory card feature by `sudo raspi-config` and `4. Performance options` -> `P3 Overlay File System`
  This feature ensures to be memory card (as boot device) in secure against data corruption due to interrupted write due to power supply
  cut. Remember that while this feature is active, all changes are only done in RAM, and will lost at power off. If you want to
  change anything in memory card, first switch this off.
- From now on just power up RPi and enjoy the music.

## Radio webpage

There are files (songinfo.txt, songinfo.php, index.html) which to be used for create a webpage which always
shows fresh info about radio station, like programme, currently playing song, next song and remaining time
of current song. There steps are needed to get is use.
- Configure the script to upload up to date songinfo.txt file to your webpage host by FTP
- Upload once songinfo.php and index.html files to your webpage host.
- Execute the player script
- Open directly songinfo.txt on your webpage to see if it really uploaded by player script
- Update link of your webpage in index.html in JavaScript
- Open index.html by a Browser. It shows the songs and updated automatic without reload the complete page (AJAX technic)
For more details see content of index.html

## Warranty

It does what it does, how it does. 
It works for me. Of course not all use cases or fault cases are handled. 
So it comes without any warranty. But feel free to improve it or fix its bugs.

## License

This is free. You can do anything you want with it.
While I am using Linux, I've got so many support from free projects,
I am happy if I can give something back to the community.

## Keywords

RadioPlayer, Radio Player, AutoDJ, mp3 Player, Script, Command Line, CLI, Bash,
Configurable, Mixer, No GUI, Linux, Raspberry Pi.

## Links

[1]: https://raspberrypi.stackexchange.com/questions/28248/raspberry-pi-usb-soundcard-outputting-from-multiple-programs

###### 2020 Janos BENCSIK


