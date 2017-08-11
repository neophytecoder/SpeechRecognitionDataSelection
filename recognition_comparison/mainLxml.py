import sys
import re
from subprocess import call, check_output
import math
from lxml import etree


lineRegex1 = re.compile("Speaker sentences[^\\n]+spk-(\\d+)\\s+utt#\\s+(\\d+)[^\\n]+")
lineRegex2 = re.compile("id:\\s+\\(spk-(\\d+)-(\\d+)\\)")
lineRegex3 = re.compile("Labels:\\s+<[^,]+,[^,]+,(\\w+)>")
lineRegex4 = re.compile("File:\\s+([^\\n]+)\\n")
lineRegex5 = re.compile("Channel:[^\\n]+")
lineRegex6 = re.compile("Scores:\\s+\\(#C\\s#S\\s#D\\s#I\\)\\s+(\\d+)\\s(\\d+)\\s(\\d+)\\s(\\d+)")
lineRegex7 = re.compile("Ref times:\\s+t1=\\s+([\\d.]+)\\s+t2=\\s+([\\d.]+)")
lineRegex8 = re.compile("REF:\s*([^\n]*)")
lineRegex8split = re.compile("[\s\*]+")
lineRegex9 = re.compile("HYP:\s*([^\n]*)")
lineRegex9split = re.compile("[\s\*]+")
lineRegex10 = re.compile("H_T1:\s*([^\n]*)")
lineRegex10split = re.compile("[\s\*]+")
lineRegex11 = re.compile("H_T2:\s*([^\n]*)")
lineRegex11split = re.compile("\s+")
lineRegex12 = re.compile("CONF:\s*([^\n]*)")
lineRegex12split = re.compile("\s+")
lineRegex13 = re.compile("Eval:[^\\n]+")
ctmLineRegex = re.compile("^([^\s]+)\s([^\s]+)\s([\.0-9]+)\s([\.0-9]+)\s([^\s]+)\s([\.0-9]+)")

NO_STATE = 0
END_STATE = 14


def check_first_line(line):
    lineRegex = lineRegex1.match(line)
    if lineRegex is not None and lineRegex.group(1) is not None and lineRegex.group(2) is not None:
        speaker = int(lineRegex.group(1))
        utt_id = int(lineRegex.group(2))
        return (1, int(speaker), int(utt_id))
    return (0, 0, 0)

def check_second_line(line, speaker_tmp, utt_id_tmp):
    lineRegex = lineRegex2.match(line)
    if lineRegex is not None and lineRegex.group(1) is not None and lineRegex.group(2) is not None:
        speaker = int(lineRegex.group(1))
        utt_id = int(lineRegex.group(2))
        #if speaker != speaker_tmp or utt_id != utt_id_tmp:
        #    return (0, 0, 0)
        return (2, speaker, utt_id)
    return (0, 0, 0)

def check_third_line(line):
    lineRegex = lineRegex3.match(line)
    if lineRegex is not None and lineRegex.group(1) is not None:
        gender = lineRegex.group(1)
        return (3, gender)
    return (0, None)


def check_4th_line(line):
    lineRegex = lineRegex4.match(line)
    if lineRegex is not None and lineRegex.group(1) is not None:
        file = lineRegex.group(1)
        return (4, file)
    return (0, None)

def check_5th_line(line):
    lineRegex = lineRegex5.match(line)
    if lineRegex is not None:
        return 5
    return 0

def check_6th_line(line):
    lineRegex = lineRegex6.match(line)
    if lineRegex is not None:
        correct = float(lineRegex.group(1))
        substitution = float(lineRegex.group(2))
        deletion = float(lineRegex.group(3))
        insertion = float(lineRegex.group(4))
        return (6, correct, substitution, deletion, insertion)
    return (0, None)

def check_7th_line(line):
    lineRegex = lineRegex7.match(line)
    if lineRegex is not None:
        startTime = lineRegex.group(1)
        endTime = lineRegex.group(2)
        return (7, float(startTime), float(endTime))
    return (0, "", "")

def skip_line(line, lineRegexPattern, currentState):
    lineRegex = lineRegexPattern.match(line)
    if lineRegex is not None:
        return currentState+1
    return 0

def check_words_line(line, lineRegexx, lineRegexxSplit, current_state):
    lineRegex = lineRegexx.match(line)
    if lineRegex is not None:
        referenceWordsSentence = lineRegex.group(1)
        referenceWords = lineRegexxSplit.split(referenceWordsSentence)
        referenceWords = filter(lambda word: len(word)>0, referenceWords)
        referenceWords = map(lambda word: word.upper(), referenceWords)
        return (current_state+1, referenceWords)
    return (0, [])


def check_floats_line(line, lineRegexx, lineRegexxSplit, current_state):
    lineRegex = lineRegexx.match(line)
    if lineRegex is not None:
        referenceWordsSentence = lineRegex.group(1)
        referenceWords = lineRegexxSplit.split(referenceWordsSentence)
        referenceWords = filter(lambda word: len(word) > 0, referenceWords)
        return (current_state+1, referenceWords)
    return (0, [])

def get_list_of_ctm_word(file):
    ctm_words = []
    for line in file:
        ctmGroup = ctmLineRegex.match(line)
        file = ctmGroup.group(1)
        channel = ctmGroup.group(2)
        startTime = float(ctmGroup.group(3))
        endTime = float(ctmGroup.group(4)) + startTime
        word = ctmGroup.group(5)
        confidence = ctmGroup.group(6)
        ctm_words.append((file, startTime, endTime, word, confidence))
        print (file, startTime, endTime, word, confidence)

    return ctm_words


def write_transcript_segments(transcript_name, outputXMLFolder, fileName, tree):
    bodyNode = tree.xpath("//body")[0]
    segmentNode = etree.Element("segments", annotation_id="transcript_"+transcript_name)
    bodyNode.append(segmentNode)
    annotationsNode = tree.xpath("//annotations")[0]
    annotationNode = etree.Element("annotation",
                                   id="transcript_"+transcript_name,
                                   detail="automatic transcription of " + transcript_name,
                                   type="automatic")
    annotationsNode.append(annotationNode)

    #with open(outputXMLFolder + "/" + fileName + ".xml_tmp", "w" ) as output:
    #    print bodyNode
    #    output.write(etree.tostring(bodyNode, pretty_print=True))

    return tree

def make_id(fileName, uttNumber, transcript_name, speaker):
    return ("ID"+fileName+"_utt_"+str(uttNumber)+"_"+transcript_name, "ID"+fileName+"_speaker"+str(speaker)+"_"+transcript_name)

def make_word_id(fileName, wordCount, transcriptName):
    return "ID" + fileName + "_w" + str(wordCount) + "_" + transcriptName



def write_transcript_segment(transcript_name, segment_id, speaker_id, startTime, endTime, AWD, WMER, PMER, hypWords, fileName, wordCount, outputXMLFolder, tree):
    segmentsNode = tree.xpath("//segments[@annotation_id='transcript_"+transcript_name+"']")[0]
    segmentNode = etree.Element("segment", id=segment_id, who=speaker_id, starttime=str(startTime), endtime=str(endTime), WMER=str(WMER), PMER=str(PMER), AWD=str(AWD))
    segmentsNode.append(segmentNode)
    print segment_id

    for word in hypWords:
        wordId = make_word_id(fileName, wordCount, transcript_name)
        elementNode = etree.Element("element", type="word", id=wordId)
        elementNode.text = word
        segmentNode.append(elementNode)
        wordCount = wordCount + 1

    #with open(outputXMLFolder + "/" + fileName + "_tmp.xml", "w" ) as output:
    #    output.write(etree.tostring(segmentsNode, pretty_print=True))

    return (wordCount, tree)


def saveXML(outputXMLFolder, fileName, tree):

    with open(outputXMLFolder + "/" + fileName + ".xml", "w" ) as output:
        output.write(etree.tostring(tree, pretty_print=True))

def get_all_elements(transcript_name, segmentId, tree):
    #print "//segments[@annotation_id='" + transcript_name + "']/segment[@id='" + segmentId + "']/element"
    elements = tree.xpath("//segments[@annotation_id='" + transcript_name + "']/segment[@id='" + segmentId + "']/element")
    return map(lambda element: element.text.strip(), elements)


def findPMER(inputPhoneFile, speaker, startTime, endTime, fileName):
    current_state = NO_STATE
    substitution = 0
    correct = 0
    deletion = 0
    insertion = 0
    speaker_tmp = 0
    fileName_tmp = ""
    startTime_tmp = 0.0
    endTime_tmp = 0.0

    for line in inputPhoneFile:
        if current_state == NO_STATE:
            (current_state, speaker_tmp, utt_id_tmp) = check_first_line(line)
        elif current_state == 1:
            (current_state, speaker, utt_id_tmp) = check_second_line(line, speaker, utt_id)
            assert speaker == speaker_tmp
        elif current_state == 2:
            (current_state, gender) = check_third_line(line)
        elif current_state == 3:
            (current_state, fileName_tmp) = check_4th_line(line)
        elif current_state == 4:
            current_state = check_5th_line(line)
            assert fileName == fileName_tmp
        elif current_state == 5:
            (current_state, correct, substitution, deletion, insertion) = check_6th_line(line)
        elif current_state == 6:
            (current_state, startTime_tmp, endTime_tmp) = check_7th_line(line)
        elif current_state == 7:
            current_state = skip_line(line, lineRegex8, current_state)
            assert abs(startTime - startTime_tmp) < 0.001
            assert abs(endTime - endTime_tmp) < 0.001
        elif current_state == 8:
            current_state = skip_line(line, lineRegex9, current_state)
        elif current_state == 9:
            current_state = skip_line(line, lineRegex10, current_state)
        elif current_state == 10:
            current_state = skip_line(line, lineRegex11, current_state)
        elif current_state == 11:
            current_state = skip_line(line, lineRegex12, current_state)
        elif current_state == 12:
            current_state = skip_line(line, lineRegex13, current_state)
        elif current_state == 13:
            if (substitution + deletion + correct) != 0:
                return round(100.0 * (substitution + deletion + insertion) / (substitution + deletion + correct), 2)
            else:
                return 0.0
    print "fail"
    return 0.0

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print "need a prf file"
        print "need a prf phone file"
        print "need a transcript name"
        print "need an input xml folder"
        print "need an output xml folder"
        sys.exit(1)

    prf_file = sys.argv[1]
    prf_phone_file = sys.argv[2]
    transcript_name = sys.argv[3]
    transcript_name_decode = sys.argv[3] + "_decode"
    inputXMlFolder = sys.argv[4]
    outputXMLFolder = sys.argv[5]

    current_state = NO_STATE

    #write_command = ""
    #write_command_decode = ""

    with open(prf_file, "r") as inputfile, open(prf_phone_file, "r") as inputPhoneFile:
        speaker = 0
        utt_id = 0
        gender = ""
        fileName = ""
        previousFileName = ""
        correct = 0
        substitution = 0
        deletion = 0
        insertion = 0
        startTime = 0.0
        endTime = 0.0
        wordCount = 1
        wordCountDecode = 1

        refWords = []
        hypWords = []
        confWords = []
        refWordsTime = []
        hypWordsTime = []

        tree = None
        tree_decode = None

        for line in inputfile:
            previous_state = current_state
            if current_state == NO_STATE:
                (current_state, speaker, utt_id_tmp) = check_first_line(line)
            elif current_state == 1:
                (current_state, speaker, utt_id_tmp) = check_second_line(line, speaker, utt_id)
            elif current_state == 2:
                (current_state, gender) = check_third_line(line)
            elif current_state == 3:
                (current_state, fileName) = check_4th_line(line)
            elif current_state == 4:
                current_state = check_5th_line(line)
            elif current_state == 5:
                (current_state, correct, substitution, deletion, insertion) = check_6th_line(line)
            elif current_state == 6:
                (current_state, startTime, endTime) = check_7th_line(line)
            elif current_state == 7:
                (current_state, refWords) = check_words_line(line, lineRegex8, lineRegex8split, current_state)
            elif current_state == 8:
                (current_state, hypWords) = check_words_line(line, lineRegex9, lineRegex9split, current_state)
            elif current_state == 9:
                (current_state, refWordsTime) = check_floats_line(line, lineRegex10, lineRegex10split, current_state)
            elif current_state == 10:
                (current_state, hypWordsTime) = check_floats_line(line, lineRegex11, lineRegex11split, current_state)
            elif current_state == 11:
                (current_state, confWords) = check_floats_line(line, lineRegex12, lineRegex12split, current_state)
            elif current_state == 12:
                current_state = skip_line(line, lineRegex13, current_state)
            elif current_state == 13:
                print "save"

                #assert len(hypWords) == len(hypWordsTime)
                #assert len(hypWords) == len(confWords)

                if fileName != previousFileName:
                    if len(previousFileName) != 0:
                        saveXML(outputXMLFolder, previousFileName, tree)
                        print "saved"
                        # break

                    parser = etree.XMLParser(remove_blank_text=True)
                    tree = etree.parse(inputXMlFolder + "/" + fileName + ".xml", parser)
                    print str(tree) + fileName

                    tree = write_transcript_segments(transcript_name, outputXMLFolder, fileName, tree)
                    tree = write_transcript_segments(transcript_name_decode, outputXMLFolder, fileName, tree)
                    wordCount = 1
                    utt_id = 0
                    previousFileName = fileName

                (align_segment_id, align_speaker_id) = make_id(fileName, utt_id + 1, "align", speaker)
                (segment_id, speaker_id) = make_id(fileName, utt_id+1, transcript_name, speaker)
                (segment_id_decode, speaker_id_decode) = make_id(fileName, utt_id + 1, transcript_name_decode, speaker)

                align_element_words = get_all_elements("transcript_align", align_segment_id, tree)
                print align_element_words

                AWD = 0.0
                WMER = 0.0
                PMER = 0.0
                if len(hypWords) != 0:
                    AWD = round((endTime - startTime*1.0) / len(hypWords), 2)

                if (substitution + deletion + correct) != 0:
                    WMER = round(100.0 * (substitution + deletion + insertion) / (substitution + deletion + correct), 2)
                else:
                    sys.stderr.write("Zero refwords: " + str(refWords) + fileName + utt_id)
                    sys.stderr.flush()

                PMER = findPMER(inputPhoneFile, speaker, startTime, endTime, fileName)

                (wordCount_tmp, tree) = write_transcript_segment(transcript_name, segment_id, speaker_id,
                                                                          startTime, endTime, AWD, WMER, PMER, align_element_words,
                                                                          fileName, wordCount, outputXMLFolder, tree)
                (wordCount_tmp2, tree) = write_transcript_segment(transcript_name_decode, segment_id_decode, speaker_id_decode,
                                                                          startTime, endTime, AWD, WMER, PMER, hypWords,
                                                                          fileName, wordCount, outputXMLFolder, tree)
                wordCount = wordCount_tmp

                utt_id = utt_id + 1
                current_state = 0

            if current_state == 0:
                speaker = 0
                gender = ""
                fileName = ""
                correct = 0
                substitution = 0
                deletion = 0
                insertion = 0
                startTime = 0.0
                endTime = 0.0

                refWords = []
                hypWords = []
                confWords = []
                refWordsTime = []
                hypWordsTime = []

        if tree is not None:
            saveXML(outputXMLFolder, previousFileName, tree)
            tree = None
