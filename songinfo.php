<?php

// Get currently displayed songs from request parameter
$oldcontent = $_GET['oldcontent'];

// Do it 120 times (two time a sec through 60s)
for($i=0;$i<120;$i++){

  // Read the content of currently playing songs
  $newcontent = file_get_contents("songinfo.txt");

  // Check if songs were changed meantime
  if($newcontent != $oldcontent){
    // Yes, changed, return immediately with the new songs
    header('Content-Type: text/plain');
    echo $newcontent;
    exit;
  }

  // Wait half sec for any update may happen by player script meantime
  usleep(500);
}

// There was no change in the last minute, so
// let return with the currently playing songs
// to not freeze the ajax request for too long time
header('Content-Type: text/plain');
echo $oldcontent;
?>
