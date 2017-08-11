import sys
from subprocess import check_output
import re

lineRegex = re.compile("([\w\d]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)\s([\d.]+)")

def extract_segment_info(line):
    line = line.strip()
    matchedLine = lineRegex.match(line)
    segmentId = matchedLine.group(1)
    WMER = float(matchedLine.group(2))
    PMER = float(matchedLine.group(3))
    AWD = float(matchedLine.group(4))
    startTime = float(matchedLine.group(5))
    endTime = float(matchedLine.group(6))
    return (segmentId, WMER, PMER, AWD, startTime, endTime)

def get_all_infos(segments_id, fileName):
    command = "xml sel -t -m \"//segments[@annotation_id='"+segments_id+"']/segment\"  -v \"concat(@id, ' ', @WMER,' ',@PMER, ' ',@AWD,' ', @starttime, ' ', @endtime)\" -n "
    command += fileName
    out = check_output(command, shell=True)
    if len(out) != 0:
        return map(extract_segment_info, out.splitlines())
    return []

def sort_by_wmer(segment_infos):
    return sorted(segment_infos, key=lambda tup: tup[1])

def sort_by_pmer(segment_infos):
    return sorted(segment_infos, key=lambda tup: tup[2])

def sort_by_awd(segment_infos):
    return sorted(segment_infos, key=lambda tup: tup[3])

def print_report(segment_infos):
    total_duration = reduce(lambda x, y: x + y, map(lambda tup: tup[5] - tup[4], segment_infos)) * 1.0
    print total_duration

    print "****************************************WMER****************************************"
    percentages = [0]
    wmers = [0]

    print_100hr = False
    segment_infos_sorted_by_wmer = sort_by_wmer(segment_infos)
    durations_sorted_by_wmer = map(lambda tup: tup[5] - tup[4], segment_infos_sorted_by_wmer)
    total_duration_so_far = 0.0
    percentage_so_far = 0.01
    for ii in xrange(0, len(segment_infos_sorted_by_wmer)):
        current_awd = segment_infos_sorted_by_wmer[ii][3]
        if not (0.165<=current_awd<=0.66):
            continue
        current_wmer = segment_infos_sorted_by_wmer[ii][1]
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


    print "\n\n****************************************PMER****************************************"
    percentages = [0]
    pmers = [0]

    print_100hr = False
    segment_infos_sorted_by_pmer = sort_by_pmer(segment_infos)
    durations_sorted_by_pmer = map(lambda tup: tup[5] - tup[4], segment_infos_sorted_by_pmer)
    total_duration_so_far = 0.0
    percentage_so_far = 0.01
    for ii in xrange(0, len(segment_infos_sorted_by_pmer)):
        current_awd = segment_infos_sorted_by_pmer[ii][3]
        if not (0.165 <= current_awd <= 0.66):
            continue
        current_pmer = segment_infos_sorted_by_pmer[ii][2]
        total_duration_so_far += durations_sorted_by_pmer[ii]
        #print total_duration_so_far
        current_percentage = total_duration_so_far * 1.0 / total_duration

        if total_duration_so_far >= 360000 and not print_100hr:
            print "100 hours: PMER: " + str(current_pmer) + "; duration: " + str(total_duration_so_far) + "; percentage: " + str(
                current_percentage)
            print_100hr = True

        if current_percentage >= percentage_so_far:
            percentages.append(current_percentage)
            pmers.append(current_pmer)

            print "PMER: " + str(current_pmer) + "; duration: " + str(
                total_duration_so_far) + "; percentage: " + str(current_percentage)
            percentage_so_far += 0.01
        assert percentage_so_far <= 1.10
        assert current_percentage <= 1.10

        if ii == len(segment_infos_sorted_by_pmer)-1:
            print "last"
            print "PMER: " + str(current_pmer) + "; duration: " + str(
                total_duration_so_far) + "; percentage: " + str(current_percentage)
            percentages.append(current_percentage)
            pmers.append(current_pmer)

    print percentages
    print pmers

    print "\n\n****************************************AWD****************************************"
    percentages = [0]
    awds = [0]

    segment_infos_sorted_by_awd = sort_by_awd(segment_infos)
    durations_sorted_by_awd = map(lambda tup: tup[5] - tup[4], segment_infos_sorted_by_awd)
    total_duration_so_far = 0.0
    percentage_so_far = 0.01
    for ii in xrange(0, len(segment_infos_sorted_by_awd)):
        current_awd = segment_infos_sorted_by_awd[ii][3]
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

        if ii == len(segment_infos_sorted_by_pmer) - 1:
            print "last"
            print "AWD: " + str(current_awd) + "; duration: " + str(
                total_duration_so_far) + "; percentage: " + str(current_percentage)
            #percentages.append(current_percentage)
            #awds.append(current_awd)

    print percentages
    print awds


def find_top_wmer_based_on_total_duration(segments_infos, total_duration_needed):
    total_duration = reduce(lambda x, y: x + y, map(lambda tup: tup[5] - tup[4], segments_infos))

    print "**********WMER**********"
    segment_infos_sorted_by_wmer = sort_by_wmer(segment_infos)
    durations_sorted_by_wmer = map(lambda tup: tup[5] - tup[4], segment_infos_sorted_by_wmer)
    total_duration_so_far = 0.0
    for ii in xrange(0, len(segment_infos_sorted_by_wmer)):
        current_awd = segment_infos_sorted_by_wmer[ii][3]
        if not (0.165 <= current_awd <= 0.66):
            continue
        current_wmer = segment_infos_sorted_by_wmer[ii][1]
        total_duration_so_far += durations_sorted_by_wmer[ii]
        if total_duration_so_far >= total_duration_needed:
            print "top wmer threshold: " + str(current_wmer)
            break

def find_top_pmer_based_on_total_duration(segments_infos, total_duration_needed):
    total_duration = reduce(lambda x, y: x + y, map(lambda tup: tup[5] - tup[4], segments_infos))

    print "**********PMER**********"
    segment_infos_sorted_by_pmer = sort_by_pmer(segment_infos)
    durations_sorted_by_pmer = map(lambda tup: tup[5] - tup[4], segment_infos_sorted_by_pmer)
    total_duration_so_far = 0.0
    for ii in xrange(0, len(segment_infos_sorted_by_pmer)):
        current_awd = segment_infos_sorted_by_pmer[ii][3]
        if not (0.165 <= current_awd <= 0.66):
            continue
        current_pmer = segment_infos_sorted_by_pmer[ii][2]
        total_duration_so_far += durations_sorted_by_pmer[ii]
        if total_duration_so_far >= total_duration_needed:
            print "top wmer threshold: " + str(current_pmer)
            break


if __name__ == '__main__':
    transcript_name = sys.argv[1]
    XMLFolder = sys.argv[2]
    listFile = sys.argv[3]

    with open(listFile, "r") as inputFile:
        accumulated_segment_infos = []

        for fileName in inputFile:
            fileName = XMLFolder + "/" + fileName.strip() + ".xml"
            segments_id = "transcript_" +  transcript_name

            # input annotation id: transcript_AM0_s1_decode
            # get transcript id, WMER, PMER, AWD
            # also get start time and end time
            segment_infos = get_all_infos(segments_id, fileName)
            accumulated_segment_infos += segment_infos
            #print len(accumulated_segment_infos)

        print_report(accumulated_segment_infos)
        #find_top_wmer_based_on_total_duration(accumulated_segment_infos, 100)
        #find_top_pmer_based_on_total_duration(accumulated_segment_infos, 100)



