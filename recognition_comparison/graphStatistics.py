import sys
from subprocess import check_output
import re
import json
from parser import commonParser

lineRegex = re.compile("([\w\d]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)")

WMER_IDX = 0
AWD_IDX = 1
PMER_IDX = 2
APD_IDX = 3
startTime_IDX = 4
endTime_IDX = 5

def extract_segment_info(datum):
    #print datum
    wordSegment = datum[0]
    phoneSegment = datum[1]
    WMER = wordSegment[commonParser.MATCHED_ERROR_RATE]
    AWD = wordSegment[commonParser.AVERAGE_DURATION]
    startTime = wordSegment[commonParser.START_TIME]
    endTime = wordSegment[commonParser.END_TIME]

    PMER = phoneSegment[commonParser.MATCHED_ERROR_RATE]
    APD = phoneSegment[commonParser.AVERAGE_DURATION]

    return (WMER, AWD, PMER, APD, startTime, endTime)

def sort_by_index(segment_infos, index):
    return sorted(segment_infos, key=lambda tup: tup[index])

def getTotalDuration(segment_infos):
    total_duration = reduce(lambda x, y: x + y,
                            map(lambda tup: tup[endTime_IDX] - tup[startTime_IDX], segment_infos)) * 1.0
    print "TOTAL_DURATION: " + str(total_duration)
    return total_duration


def print_report(segment_infos, mer_idx, awdFilter, apdFilter, info):
    total_duration = getTotalDuration(segment_infos)

    print "****************************************"+info+"****************************************"

    percentages = [0]
    wmers = [0]

    print_100hr = False
    segment_infos_sorted_by_wmer = sort_by_index(segment_infos, mer_idx)
    durations_sorted_by_wmer = map(lambda tup: tup[endTime_IDX] - tup[startTime_IDX], segment_infos_sorted_by_wmer)
    total_duration_so_far = 0.0
    percentage_so_far = 0.01
    for ii in xrange(0, len(segment_infos_sorted_by_wmer)):
        current_awd = segment_infos_sorted_by_wmer[ii][AWD_IDX]
        current_apd = segment_infos_sorted_by_wmer[ii][APD_IDX]
        if awdFilter and (not (current_awd >= 0.165 and current_awd <= 0.66)):
            continue
        if apdFilter and (not (current_apd >= 0.03 and current_apd <= 0.25)):
            continue
        current_wmer = segment_infos_sorted_by_wmer[ii][mer_idx]
        total_duration_so_far += durations_sorted_by_wmer[ii]
        current_percentage = total_duration_so_far * 1.0 / total_duration

        if total_duration_so_far >= 360000 and not print_100hr:
            print "100 hours: WMER: " + str(current_wmer) + "; duration: " + str(total_duration_so_far) + "; percentage: " + str(
                current_percentage)
            print_100hr = True

        if current_percentage >= percentage_so_far:
            percentages.append(current_percentage)
            wmers.append(current_wmer)

            print "WMER: " + str(current_wmer) + "; duration: " + str(total_duration_so_far) + "; percentage: " + str(current_percentage)
            percentage_so_far += 0.01
        assert percentage_so_far <= 1.100
        assert current_percentage <= 1.100

        if ii == len(segment_infos_sorted_by_wmer)-1:
            print "last"
            print "WMER: " + str(current_wmer) + "; duration: " + str(total_duration_so_far) + "; percentage: " + str(current_percentage)
            percentages.append(current_percentage)
            wmers.append(current_wmer)
    print percentages
    print wmers


def print_report_average_duration(segment_infos, AD_idx, info):
    total_duration = getTotalDuration(segment_infos)
    print "\n\n****************************************"+info+"****************************************"
    percentages = [0]
    awds = [0]

    segment_infos_sorted_by_awd = sort_by_index(segment_infos, AD_idx)
    durations_sorted_by_awd = map(lambda tup: tup[endTime_IDX] - tup[startTime_IDX], segment_infos_sorted_by_awd)
    total_duration_so_far = 0.0
    percentage_so_far = 0.01
    for ii in xrange(0, len(segment_infos_sorted_by_awd)):
        current_awd = segment_infos_sorted_by_awd[ii][AD_idx]
        total_duration_so_far += durations_sorted_by_awd[ii]
        # print total_duration_so_far
        current_percentage = total_duration_so_far * 1.0 / total_duration

        if current_percentage >= percentage_so_far:
            percentages.append(current_percentage)
            awds.append(current_awd)

            print "AWD: " + str(current_awd) + "; duration: " + str(
                total_duration_so_far) + "; percentage: " + str(current_percentage)
            percentage_so_far += 0.01
        assert percentage_so_far <= 1.10
        assert current_percentage <= 1.10

        if ii == len(segment_infos_sorted_by_awd) - 1:
            print "last"
            print "AWD: " + str(current_awd) + "; duration: " + str(
                total_duration_so_far) + "; percentage: " + str(current_percentage)
            #percentages.append(current_percentage)
            #awds.append(current_awd)

    print percentages
    print awds


if __name__ == '__main__':
    wordJsonFile = sys.argv[1]
    phoneJsonFile = sys.argv[2]
    awdFilter = sys.argv[3]
    apdFilter = sys.argv[4]

    with open(wordJsonFile, "r") as wordInputFile, \
            open(phoneJsonFile, "r") as phoneInputFile:
        wordData = json.load(wordInputFile)
        phoneData = json.load(phoneInputFile)
        accumulatedSegments = []
        for fileName in wordData.keys():
            for segmentId in xrange(0, len(wordData[fileName])):
                accumulatedSegments.append( (wordData[fileName][segmentId], phoneData[fileName][segmentId]) )
        accumulated_segment_infos = map(lambda datum:extract_segment_info(datum), accumulatedSegments)

        print_report_average_duration(accumulated_segment_infos, AWD_IDX, "average word duration")
        print_report_average_duration(accumulated_segment_infos, APD_IDX, "average phone duration")
        print_report(accumulated_segment_infos, PMER_IDX, awdFilter, apdFilter, "PMER")
        #print_report(accumulated_segment_infos, awdFilter, apdFilter)
        #find_top_wmer_based_on_total_duration(accumulated_segment_infos, 100)
        #find_top_pmer_based_on_total_duration(accumulated_segment_infos, 100)