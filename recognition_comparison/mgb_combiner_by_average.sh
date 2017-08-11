#!/bin/bash

# Training data prepartion for MGB Challenge 2015 (Peter Bell, University of Edinburgh)

totalDuration=320328

set -e

if [ $# -le 2 ]; then
  echo "Usage: $0 <wav-dir> <xml-dir> <pmer-sel> <transcript-sel> <prfs>"
  exit 1;
fi

wavdir=$1
xmldir=$2
totalDuration=$3


decode1="decode_res_train.200_fst+merall_mgb2015.full.genres.4gm.kn.arpa.subtitles.arpa.lambda0.9.mixed.limitsubtitles+sevenWeek.160k.wlist.arpa.1e-9.arpa_automatic"
decode2="decode_res_train.200_fst+merall_mgb2015.wordList.4gm.kn.arpa.gz.1e-9.arpa_automatic"
decode3="decode_res_train.200_fst+merall_sevenWeekTranscriptions.arpa.subtitles.arpa.lambda0.9.mixed.limitsubtitles+sevenWeek.160k.wlist.arpa.gz.1e-9.arpa_automatic"
words="/decode_dev/best-path_11_0.0/ctm_words.filt.filt.prf"
phones="/decode_dev/best-path_11_0.0/ctm_phones.filt.filt.prf"
prfs="${decode1}${words} ${decode1}${phones}"
prfs="${prfs} ${decode2}${words} ${decode2}${phones}"
prfs="${prfs} ${decode3}${words} ${decode3}${phones}"

dir=data/train_mer$totalDuration
mkdir -p $dir

rm -f $dir/{wav.scp,feats.scp,utt2spk,spk2utt,segments,text}

python mgbCombinerByAverage.py $wavdir $xmldir $dir "train.full" $xmldir $totalDuration $prfs

sort -k 2 $dir/utt2spk | utils/utt2spk_to_spk2utt.pl > $dir/spk2utt

utils/fix_data_dir.sh $dir
utils/validate_data_dir.sh --no-feats $dir

echo "Training data preparation succeeded"