#!/bin/bash
# Prepare Songs For Radio Transmission (psrt)

# Delete error log is exists
ERRORLOGFILE=psrt_err.log
if [ -f "$ERRORLOGFILE" ]; then
  rm $ERRORLOGFILE
fi

SEP="**********************************************************************"

# For all songs in the current folder
for f in *.mp3
do
  # Print separator line between songs
  echo "$SEP"
  
  # Do anything only if sample rate is not yet 32kHz (means not yet prepared)
  #   I hope there will not be original mp3 files with 32kHz sample rate :-)
  if ! [[ $(exiftool "$f" | sed -n "s/Sample Rate\\s\+:\\s\+//p") = 32000 ]]; then
    echo Now preparing: "$f"
  
    # Analyze and get recommended gain, meantine check broken frames in mp3
    RESULT=`mp3gain -s s -s r "$f" 2>&1`
    if [[ $RESULT == *"error:"* ]]; then
      echo -e "\e[91mError!\e[39m Appended to $ERRORLOGFILE";
      echo -e "$SEP\nError in song: $f\n$RESULT\n\n" >> $ERRORLOGFILE
      continue;
    fi
    GAIN=`echo $RESULT | pcregrep -o1 'Recommended \"Track\" dB change: ([0-9\-\.]+)'`
    echo "Starting gain= $GAIN dB"
  
    # Convert dB to multiplier (-scale in lame)
    SCALE=`php -r 'echo pow(10,('$GAIN' / 20));'`
    echo "It is $SCALE as multipier"

    # Re-encode the song:
    # - Resampling to 32 kHz to ensure not disturb 19kHz stereo pilot signal
    #   since highest frequency is 16kHz with 32 kHz sample rate.
    # - Using polyphase lowpass filter, transition band: 12000 Hz - 12903 Hz
    #   There was still not nice high frequency components, but with this additional
    #   smooth ramp down low pass filter the songs sounds better for me.
    # - Encoding as j-stereo MPEG-1 Layer III VBR(q=2)
    # - Apply previously calculated gain (scale)
    # Finally I expect ReplayGain ~0dB, if scale was successfull
    lame -q 2 -V 2 --vbr-new --resample 32 --lowpass 12.5 --lowpass-width 0.5 --scale $SCALE "$f" tmp && mv tmp "$f"
  
    # Trim silent part from begin and end to sound the cross-fading better
    #   (-25dB treshold, 2s min length, same name)
    mp3splt -r -p th=-25,min=2 -o tmp -d ~/ "$f" && mv ~/tmp.mp3 "$f" 
    
    # Check the normalization again. Here I expect "No changes to ... are necessary",
    #   since necessary gain was already applied during re-encode.
    GAIN=`mp3gain -s s -s r "$f" | pcregrep -o1 'Recommended \"Track\" dB change: ([0-9\-\.]+)'`
    echo "Final gain= $GAIN dB"
    php -r 'if( (-1.0 < '$GAIN') && ('$GAIN' < 1.0) ){ echo "\e[92mOK.\e[39m\n"; exit(0); } else { echo "\e[91mError!\e[39m\n"; exit(1); }'
    if [ $? -ne 0 ]; then
      echo -e "$SEP\nError in song: $f\nFinal gain $GAIN is out of tolerance of -1...+1\n\n" >> $ERRORLOGFILE
    fi
    
  else
    echo Already prepared: "$f"
  fi
done

