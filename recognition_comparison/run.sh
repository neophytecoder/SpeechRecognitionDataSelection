#!/bin/bash -u

set -e

. ./cmd.sh

. ./path.sh
# no need cuda

##########################################################
#
#  Initial notes
#
##########################################################

# To this recipe you'll need
# 1) An installation of Kaldi
# 1) SRILM http://www.speech.sri.com/projects/srilm/
# 2) xmlstarlet http://xmlstar.sourceforge.net/

# This script assumes that you are already familiar with Kaldi recipes.


##########################################################
#
#  Actions required from users
#
##########################################################

# TO DO: You will need to place the lists of training and dev data
# (train.full and dev.full) in this working directory, link to the
# usual steps/ and utils/ directories, and create your copies path.sh
# and cmd.sh in this directory.

# TO DO: specify the directories containing the binaries for
# xmlstarlet, SRILM and IRSTLM

#XMLSTARLET=/usr/bin/xmlstarlet
#SRILM=/logiciels/srilm/bin/i686-m64
#IRSTLM=/logiciels/kaldi-trunk-20151111/tools/irstlm/bin
XMLSTARLET=/home/jkarsten/lib/bin
SRILM=/home/jkarsten/srilm/bin/i686-m64
IRSTLM=/home/jkarsten/kaldi/tools/extras/irstlm/trunk/bin

# TO DO: you will need to choose the size of training set you want.
# Here we select according to an upper threshhold on Matching Error
# Rate from the lightly supervised alignment.  When using all the
# training shows, this will give you training data speech segments of
# approximate lengths listed below:

# MER	duration (hrs)
#
# 10 	  240
# 20      400
# 30 	  530
# 40 	  640
# 50 	  740
# all    1210

pmer=0.33 # 88.98 hours
transcript="transcript_align"
LM=mgb2015.150k.p07.3gm.kn
totalDuration=320328

# TO DO: set the location of downloaded WAV files, XML, LM text and the Combilex Lexicon

# Location of downloaded WAV files
WAV_DIR=/home/jkarsten/mgb/wav

# Location of downloaded XML files
XML_DIR=/home/jkarsten/mgb/xml

# Location of downloaded LM text
LM_DIR=/home/jkarsten/mgb/lm

# Location of Combilex lexicon files
LEX_DIR=/home/jkarsten/mgb/lex

#if [ "$#" -eq 0 ]
#then
#    nj=2  # split training into how many jobs
#else
mkdir -p .queue
/bin/rm -f .queue/machines
cat $OAR_FILE_NODES | sort -u > .queue/machines

nj=`cat $OAR_FILE_NODES | sort -u | wc -l`
#fi
echo "Print jobs $nj"

##########################################################
#
#  Recipe
#
##########################################################


#1) Data preparation

export XMLSTARLET SRILM IRSTLM

echo "Preparing training data"
#local/mgb_data_prep.sh $WAV_DIR $XML_DIR $totalDuration $transcript
./mgb_combiner_data_prep.sh $WAV_DIR $XML_DIR $totalDuration $transcript

#echo "Training n-gram language model"
#local/mgb_train_lm.sh $LM_DIR

echo "Preparing dictionary"
local/mgb_prepare_dict.sh $LEX_DIR

echo "Preparing lang dir"
utils/prepare_lang.sh data/local/dict "<unk>" data/local/lang data/lang

echo "Computing features"
mfccdir=data/mfcc_train_mer$totalDuration
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/train_mer$totalDuration exp/mer$totalDuration/make_mfcc/train/log $mfccdir # create mfcc features
steps/compute_cmvn_stats.sh data/train_mer$totalDuration exp/mer$totalDuration/make_mfcc/train/log $mfccdir # compute cmvn stats

#LM=mgb2015.150k.p07.3gm.kn
utils/format_lm.sh data/lang data/local/lm/$LM.arpa.gz data/local/dict/lexicon.txt data/lang_$LM

# 2) Building GMM systems
# This is based on the standard Kaldi GMM receipe

numutts=`cat data/train_mer$totalDuration/feats.scp | wc -l`
utils/subset_data_dir.sh --shortest data/train_mer$totalDuration $[numutts/3] data/train_mer${totalDuration}_short
# take a random 10k from this
utils/subset_data_dir.sh data/train_mer${totalDuration}_short 10000 data/train_mer${totalDuration}_10k
# take first 30k utterances for the first two passes of triphone training
utils/subset_data_dir.sh --first data/train_mer$totalDuration 30000 data/train_mer${totalDuration}_30k

steps/train_mono.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer${totalDuration}_10k data/lang exp/mer$totalDuration/mono 

steps/align_si.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer${totalDuration}_30k data/lang exp/mer$totalDuration/mono exp/mer$totalDuration/mono_ali 

steps/train_deltas.sh --cmd "$train_cmd" \
  3200 30000 data/train_mer${totalDuration}_30k data/lang exp/mer$totalDuration/mono_ali exp/mer$totalDuration/tri1 

steps/align_si.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer${totalDuration}_30k data/lang exp/mer$totalDuration/tri1 exp/mer$totalDuration/tri1_ali 

steps/train_deltas.sh --cmd "$train_cmd" \
  3200 30000 data/train_mer${totalDuration}_30k data/lang exp/mer$totalDuration/tri1_ali exp/mer$totalDuration/tri2

# now train on full data
steps/align_si.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer$totalDuration data/lang exp/mer$totalDuration/tri2 exp/mer$totalDuration/tri2_ali

# Train tri3, which is LDA+MLLT, on full
steps/train_lda_mllt.sh --cmd "$train_cmd" \
  5500 90000 data/train_mer$totalDuration data/lang exp/mer$totalDuration/tri2_ali exp/mer$totalDuration/tri3 


# Train tri4, which is LDA+MLLT+SAT, on train_nodup data
steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer$totalDuration data/lang exp/mer$totalDuration/tri3 exp/mer$totalDuration/tri3_ali_nodup 

steps/train_sat.sh  --cmd "$train_cmd" \
  11500 200000 data/train_mer$totalDuration data/lang exp/mer$totalDuration/tri3_ali_nodup exp/mer$totalDuration/tri4

# align the final models
steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
  data/train_mer$totalDuration data/lang exp/mer$totalDuration/tri4 exp/mer$totalDuration/tri4_ali

# generate graph
utils/mkgraph.sh data/lang_$LM exp/mer$totalDuration/tri4 exp/mer$totalDuration/tri4/graph_$LM

ln -s exp/mer$totalDuration/tri4/graph_$LM exp/mer$totalDuration/tri4/graph

echo "finish training gmm"
