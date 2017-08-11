#!/usr/bin/env bash

WAV_DIR=/home/jkarsten/mgb/wav
XML_DIR=/home/jkarsten/mgb/xml
totalDuration=320328
transcript="transcript_align"

./mgb_combiner_data_prep.sh $WAV_DIR $XML_DIR $totalDuration $transcript
