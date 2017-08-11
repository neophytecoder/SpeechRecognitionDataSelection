import sys
from parser import commonParser
from parser import xmlParser
from compare import compareByAPD
from random import randint
import copy
import json
from writer import writeData


def validation(wordData, phoneData):
    fileNames = wordData.keys()
    assert len(wordData.keys()) == len(phoneData.keys())
    for fileName in fileNames:
        assert fileName in phoneData
        assert len(phoneData[fileName]) == len(wordData[fileName])

def testMe():
    prf_file = "data/ctm_words.filt.filt.prf"
    prf_phone_file = "data/ctm_phones.filt.filt.prf"

    parser = commonParser.CommonParser(prf_file)
    wordData = parser.getData()
    parser = commonParser.CommonParser(prf_phone_file)
    phoneData = parser.getData()
    validation(wordData, phoneData)

    parser = xmlParser.XmlParser(
        "/Users/juankarsten/Documents/Education/Nancy/Internship/kaldi-script/s3_scripts/recognition_comparison",
        "test.one")
    alignData = parser.getData()

    shortWordData = {
        "20080401_004000_bbcone_miracle_on_the_estate": wordData["20080401_004000_bbcone_miracle_on_the_estate"][0:10]
    }
    shortPhoneData = {
        "20080401_004000_bbcone_miracle_on_the_estate": phoneData["20080401_004000_bbcone_miracle_on_the_estate"][0:10]
    }
    shortAlignData = {
        "20080401_004000_bbcone_miracle_on_the_estate": alignData["20080401_004000_bbcone_miracle_on_the_estate"][0:10]
    }

    shortWordData2 = copy.deepcopy(shortWordData)
    shortPhoneData2 = copy.deepcopy(shortPhoneData)

    shortWordData3 = copy.deepcopy(shortWordData)
    shortPhoneData3 = copy.deepcopy(shortPhoneData)

    fileName = "20080401_004000_bbcone_miracle_on_the_estate"
    shortWordData2[fileName][0][commonParser.MATCHED_ERROR_RATE] = 0.0
    shortPhoneData3[fileName][6][commonParser.MATCHED_ERROR_RATE] = 0.0

    shortPhoneData3[fileName][7][commonParser.MATCHED_ERROR_RATE] = 1
    shortPhoneData2[fileName][3][commonParser.MATCHED_ERROR_RATE] = 1.5
    shortPhoneData3[fileName][9][commonParser.MATCHED_ERROR_RATE] = 1000.0

    for ii in xrange(0, 10):
        segment = shortPhoneData2[fileName][ii]
        segment[commonParser.HYPOTHESIS] = [chr(randint(0, 23) + ord('a')) for ii in xrange(0, 5)]
        shortPhoneData2[fileName][ii] = segment

    for ii in xrange(0, 10):
        segment = shortPhoneData3[fileName][ii]
        segment[commonParser.HYPOTHESIS] = [chr(randint(0, 23) + ord('a')) for ii in xrange(0, 5)]
        shortPhoneData3[fileName][ii] = segment

    segment = shortPhoneData2[fileName][9]
    segment2 = shortPhoneData3[fileName][9]
    segment[commonParser.HYPOTHESIS] = segment2[commonParser.HYPOTHESIS]
    shortPhoneData2[fileName][9] = segment
    shortPhoneData3[fileName][9] = segment

    # print str(shortPhoneData) + "\n\n\n"
    # print str(shortWordData) + "\n\n\n"

    comparer = compareByAPD.CompareByApd([shortWordData, shortWordData2, shortWordData3],
                                         [shortPhoneData, shortPhoneData2, shortPhoneData3],
                                         shortAlignData)

if __name__ == '__main__':
    if len(sys.argv) < 8:
        sys.exit(1)
    #1. input file: wav dir, xml dir, out dir, filelist,  align, total duration, (prf, prf_phone)*
    #2. parse prf and prf_phone
    #3. parse align
    #4. compare each asr
    #5. write xml to files
    #6. total duration

    # read std.in
    print sys.argv
    wavDir = sys.argv[1]
    xmlDir = sys.argv[2]
    outDir = sys.argv[3]
    fileList = sys.argv[4]
    alignFolder = sys.argv[5]
    total_duration = float(sys.argv[6])
    prf_files = []
    prf_phone_files = []
    for ii in xrange(7, len(sys.argv), 2):
        prf_files.append(sys.argv[ii])
        prf_phone_files.append(sys.argv[ii+1])

    # get all models
    #alignData = xmlParser.XmlParser(alignFolder, fileList)
    #alignData.writeData("align.json")
    #alignData = alignData.getData()
    alignData = None
    with open("align.json", "r") as inFile:
        alignData = json.load(inFile)

    prf_models = []
    prf_phones_models = []

    for modelTh in xrange(0, len(prf_files)):
        print "parsing" + prf_files[modelTh]
        with open(prf_files[modelTh]+".json", "r") as inFile:
            prf_models.append(json.load(inFile))
        with open(prf_phone_files[modelTh] + ".json", "r") as inFile:
            prf_phones_models.append(json.load(inFile))
        validation(prf_models[-1], prf_phones_models[-1])

    comparer = compareByAPD.CompareByApd(prf_models, prf_phones_models, alignData)
    comparer.printStatistics()
    print "write to file"
    writeData.DataWriter(comparer.getResult(), total_duration, wavDir, outDir)
    pass



