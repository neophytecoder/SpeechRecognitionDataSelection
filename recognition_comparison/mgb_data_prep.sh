#!/bin/bash

# Training data prepartion for MGB Challenge 2015 (Peter Bell, University of Edinburgh)

set -e

if [ $# -ne 4 ]; then
  echo "Usage: $0 <wav-dir> <xml-dir> <pmer-sel> <transcript-sel>"
  exit 1;
fi

wavdir=$1
xmldir=$2
pmer=$3
transcript=$4

dir=data/train_mer$pmer
mkdir -p $dir

rm -f $dir/{wav.scp,feats.scp,utt2spk,spk2utt,segments,text}

cat train.full | while read basename; do
    #echo "//segments[@annotation_id='${transcript}']"
    [ ! -e $xmldir/$basename.xml ] && echo "Missing $xmldir/$basename.xml" && exit 1
    $XMLSTARLET/xml sel -t -m "//segments[@annotation_id='${transcript}']" -m "segment" -n -v  "concat(@who,' ',@starttime,' ',@endtime,' ',@WMER, ' ', @PMER, ' ', @AWD, ' ')" -m "element" -v "concat(text(),' ')" $xmldir/$basename.xml | local/add_to_datadir.py $basename $dir $pmer
    echo $basename $wavdir/$basename.wav >> $dir/wav.scp
done

sort -k 2 $dir/utt2spk | utils/utt2spk_to_spk2utt.pl > $dir/spk2utt

utils/fix_data_dir.sh $dir
utils/validate_data_dir.sh --no-feats $dir

echo "Training data preparation succeeded"
