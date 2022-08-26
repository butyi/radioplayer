<?php

if($argc<2){
  echo "ERROR! Missing parameter. First parameter is mandatory and shall be the path of MP3 files.\n";
  exit;
}
$musicpath=trim($argv[1]);

$command="find $musicpath -type f -exec md5sum {} + | sort -k 2 > ./music_md5.txt";
echo "Execution of ".$command." (it takes minutes)\n";
system($command);

echo "Search same contents.\n";
$f=array();
foreach(file("./music_md5.txt") as $l){
  $l=trim($l);
  //df2342de5846a9349fc3f48c19d772ca  ./analogue/2 Unlimited - Do What I Like.mp3
  $a=explode("  ",$l);
  if(is_array($a) && count($a)==2){
    $hash=$a[0];
    $file=$a[1];
    $f[$hash][]=$file;
  } else {
    echo "Line cannot be exploded '$l'\n";
    exit(2);
  }
}

foreach($f as $hash => $files){
  if(count($files)==1)unset($f[$hash]);
}

//print_r($f);
if(0 < count($f)){
  $reportfile="report_music_md5.txt";
  echo "There are ".count($f)." files with same content. See report in $reportfile\n";
  file_put_contents($reportfile,print_r($f,true));
} else {
  echo "There is no files with same content.\n";
}
?>
