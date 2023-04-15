<?php

if($argc<2){
  echo "ERROR! Missing parameter. First parameter is mandatory and shall be the path of MP3 files.\n";
  exit;
}
$musicpath=trim($argv[1]);

$renames = "";

//Config
$checksimilarity = true;
$similarity_exclude = array(
  "I Have A Dream",
  "Best Of My Love",
  "Ennio Morricone - A Fistful Of"
);


//Accepted '&' in artists
$andinartistnames = array(
  "Smokey Robinson & The Miracles",
  "Kool & The Gang",
  "James Last & Orchestra",
  "Daryl Hall & John Oates",
  "Bruce & Bongo",
  "Earth Wind & Fire",
  "Katrina & The Waves",
  "Mel & Kim",
  "Captain & Tennille",
  "Mike & The Mechanics",
  "Mc Hawer & Tekkno",
  "Touch & Go",
  "Tones & I",
  "Heavy D & The Boyz",
  "Jazzy Jeff & The Fresh Prince",
  "Derek & The Dominos",
  "Hall & Oats",
  "The Mamas & The Papas",
  "Simon & Garfunkel",
  "Tony Orlando & Dawn",
  "Peter & Gordon",
  "England Dan & John Ford Coley",
  "Monchy & Alexandra",
  "Sergio Mendez & Brazil 66",
  "Peaches & Herb",
  "Mcfadden & Whitehead",
  "KC & The Sunshine Band",
  "Ella Fitzgerald & Louis Armstrong",
  "Tegan & Sara",
  "C & C Music Factory",
  "Dr Hook & The Medicine Show",
  "Jesse & Joy",
  "Marina & The Diamonds",
  "Rock & Roll",
  "Romano & Sapienza",
  "Milk & Sugar",
  "Phats & Small",
  "Lilly Wood & The Prick",
  "Redhead Kingpin & Fbi",
  "Romeo & Julia",
  "Bart & Baker",
  "Bery & Váci Eszter",
  "Grace Potter & The Nocturnals",
  "Ashford & Simpson",
  "Marnik & Smack",
  "Lisa Lisa & Cult Jam",
  "Sly & The Family Stone",
  "Zager & Evans"
);

$skipsimilaritycheck = array(
  "Jean Michel Jarre - Oxygene",
  "Jean Michel Jarre - Equinoxe",
  "Jean Michel Jarre - Magnetic Fields",
  "Depeche Mode - A Question Of",
);

$allowedmultiplecapitals = array(
  "GM", //GM 49
  "EZ", //EZ Rollers
  "BTS",
);

$suspiciouswords = array(
  '/(feat)\s/i',
  '/(video)\s/i',
  '/(lyric)\s/i',
  '/(official)\s/i',
  '/(remix)\s/i'
);

system("find $musicpath -type f -name '*.mp3' -printf \"%P\n\" > ./songs.txt");

//Trim path from songs
$paths=file("./songs.txt");

foreach($paths as $key => $line){
  $line=trim($line);

  $a = explode("/",$line);
  $song = array_pop($a);
  //array_shift($a);//drop '.'
  //array_shift($a);//drop 'music'
  $path = implode("/",$a);
  //echo "path = '$path', song = '$song'\n";
  //exit;

  $files[$key]=$song;
}


//Check all song filenames
$artists=array();
foreach($files as $key => $line){

  //Add artist(s) to array
  $a = explode(" - ",$line);
  if(2 == count($a)){
    $a = explode(" Ft. ",$a[0]);
    foreach($a as $i){
      if(array_key_exists($i,$artists)){
        $artists[$i]++;
      } else {
        $artists[$i]=1;
      }
    }
  }

  //PMJs filenames are not yet formated, skip from check
  if(false!==strpos($line,"PMJ ")){
    continue;
  }

//  if(preg_match('/\s(\S+n\')\s/i',$line,$regs){//"n'"
//    echo $line." -> (".$regs[1].")\n";
//  }
  if(false === strpos($line,"-")){
    echo $line." -> missing '-'\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }

  if(false === strpos($line,"(") && false !== strpos($line,")")){
    echo $line." -> missing '('\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }

  if(false !== strpos($line,"(") && false === strpos($line,")")){
    echo $line." -> missing ')'\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }

  if(preg_match('/\s(With)\s.+ - /i',$line,$regs)){//search 'With' which maybe to be replaced with 'Ft.'
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/ (And) .+ - /i',$line,$regs)){//search 'And' which maybe to be replaced with 'Ft.'
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/ (&) .+ - /i',$line,$regs)){//search '&' which maybe to be replaced with 'Ft.'
    $found=false;
    foreach($andinartistnames as $i){
      if(false !== strpos($line,$i)){
        $found=true;
        break;
      }
    }
    if($found)continue;
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/\s(\S+\'\S*)/i',$line,$regs)){//apostrof
    if(false !== strpos($line,"'s"))continue;
    if(false !== strpos($line,"'ve"))continue;
    if(false !== strpos($line,"'ll"))continue;
    if(false !== strpos($line,"'d"))continue;
    if(false !== strpos($line,"n't"))continue;
    if(false !== strpos($line,"I'm"))continue;
    if(false !== strpos($line,"'re"))continue;
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/(  )/i',$line,$regs)){//double space
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/\s([a-z]\S*)\s/',$line,$regs)){//word starting with small letter
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/^([a-z]\S*)\s/',$line,$regs)){//first word starting with small letter
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/([A-Z]{2}\S*)/',$line,$regs)){//Second or futher capital letter 
    if(!in_array($regs[1],$allowedmultiplecapitals)){
      echo $line." -> (".$regs[1].")\n";
      $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
    }
  }
  foreach($suspiciouswords as $i){//suspicious words
    if(preg_match($i,$line,$regs)){
      echo $line." -> (".$regs[1].")\n";
      $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
    }
  }
  if(preg_match('/ \-[^\-]*\-/',$line,$regs)){//double '-'
    echo $line." -> (more than one '-')\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/ (\-\S)/',$line,$regs)){//No space after '-'
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/ (\S\-)/',$line,$regs)){//No space before '-'
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/\s(ft\.)\s/',$line,$regs)){//ft with small F
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/\s([Ff]t)[^\.]/',$line,$regs)){//Ft without dot
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }
  if(preg_match('/(,)/',$line,$regs)){//','
    echo $line." -> (".$regs[1].")\n";
    $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
  }

  if($checksimilarity){
    //Find similar songs which maybe duplicated due to file name typo
    $found=false;
    foreach($skipsimilaritycheck as $i){//skip those which are reported but not failure 
      if(false !== strpos($line,$i)){
        $found=true;
        break;
      }
    }
    if(!$found){//If not to be skipped
      foreach($files as $line2){
        $line2=trim($line2);
        $similarity = similar_text_lyani($line, $line2);
        if(80 < $similarity && $similarity < 100){
          $skip = false;
          foreach($similarity_exclude as $exclude){
            if(false !== strpos($line,$exclude) ){
              $skip = true;
              break;
            }
            if(false !== strpos($line2,$exclude) ){
              $skip = true;
              break;
            }
          }
          if($skip)continue;
          $similarity = intval($similarity);
          echo "similarity = $similarity % -> '$line' and '$line2'\n";
          $renames.='mv "'.trim($paths[$key]).'" "'.trim($paths[$key]).'"'.PHP_EOL;
        }
      }
    }
  }

}

if(strlen($renames))file_put_contents("renames.sh",$renames);


//Formated print of artists
ksort($artists);
$str="";
foreach($artists as $artist => $num){
  $str.=$artist." -> ".$num."\r\n";
}
file_put_contents("artists.txt",$str);


//own text simiratity function
function similar_text_lyani($s1,$s2){
  $s1 = explode(" ",str_replace(".mp3","",$s1));
  $s2 = explode(" ",str_replace(".mp3","",$s2));
  $s1 = array_combine($s1, $s1);
  $s2 = array_combine($s2, $s2);
  if(2 < abs(count($s1)-count($s2))){
    return 0;
  }
  $numofwordsinboth = 0;
  foreach($s1 as $w){
    if (($key = array_search($w, $s2)) !== false) {
      $numofwordsinboth++;
      //unset($s2[$key]);
    }
  }
  $numofwords = count($s1);
  if($numofwords < count($s2))$numofwords = count($s2);
  return ( $numofwordsinboth * 100 / $numofwords );
}

?>
