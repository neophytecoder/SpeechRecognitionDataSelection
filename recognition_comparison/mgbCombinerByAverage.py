import sys
from compare import compareByAverage
import json
from writer import writeData


def validation(wordData, phoneData):
    fileNames = wordData.keys()
    assert len(wordData.keys()) == len(phoneData.keys())
    for fileName in fileNames:
        #print fileName
        #print str(ii) + " " + str(len(phoneData[fileName])) + " " +  str(len(wordData[fileName]))
        #print phoneData[fileName][0]
        #print wordData[fileName][0]
        assert fileName in phoneData
        assert len(phoneData[fileName]) == len(wordData[fileName])

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

    comparer = compareByAverage.CompareByAverage(prf_models, prf_phones_models, alignData)
    print "write to file"
    writeData.DataWriter(comparer.getData(), total_duration, wavDir, outDir)
    pass



