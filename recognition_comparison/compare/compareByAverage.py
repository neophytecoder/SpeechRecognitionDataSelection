from parser import commonParser
from parser import xmlParser

SPEAKER = "SPEAKER"
PMER = "PMER"
WMER = "WMER"
APD = "APD"
AWD = "AWD"
START_TIME = "start"
END_TIME = "end"
TRANSCRIPT = "transcript"
FILENAME = "filename"
SEGMENT_ID = "id"


class CompareByAverage:
    def __init__(self, wordDatas, phoneDatas, alignData):
        self.selectedData = []

        self.wordDatas = wordDatas
        self.phoneDatas = phoneDatas
        self.alignData = alignData

        self.addAverageModels()

        tempSelectedData = sorted(self.selectedData, key=lambda tup: tup[PMER])
        self.selectedData = tempSelectedData

        currentDuration = 0.0
        for segment in self.selectedData:
            pmer = segment[PMER]
            awd = segment[AWD]
            apd = segment[APD]
            currentDuration += (segment[END_TIME] - segment[START_TIME])
            print "%f %f %f %f" % (pmer, awd, apd, currentDuration)

    def addAverageModels(self):
        wordData = self.wordDatas
        phoneData = self.phoneDatas
        alignData = self.alignData

        numberOfModel = len(wordData)
        fileNames = wordData[0].keys()


        for fileName in fileNames:
            numberOfSegment = len(wordData[0][fileName])
            numberOfPhoneSegment = len(phoneData[0][fileName])
            assert numberOfSegment == numberOfPhoneSegment

            for segmentNumber in xrange(0, numberOfSegment):
                totalPMER = 0.0
                totalWMER = 0.0
                totalAPD = 0.0
                totalAWD = 0.0

                alignSegment = alignData[fileName][segmentNumber]

                for modelNumber in xrange(0, numberOfModel):
                    wordSegment = wordData[modelNumber][fileName][segmentNumber]
                    phoneSegment = phoneData[modelNumber][fileName][segmentNumber]

                    totalWMER += wordSegment[commonParser.MATCHED_ERROR_RATE]
                    totalPMER += phoneSegment[commonParser.MATCHED_ERROR_RATE]
                    totalAWD += wordSegment[commonParser.AVERAGE_DURATION]
                    totalAPD += phoneSegment[commonParser.AVERAGE_DURATION]

                wordSegment = wordData[0][fileName][segmentNumber]
                averagePMER = totalPMER / numberOfModel
                averageWMER = totalWMER / numberOfModel
                averageAPD = totalAPD / numberOfModel
                averageAWD = totalAWD / numberOfModel
                transcript = alignSegment[xmlParser.TRANSCRIPT]

                if (averageAWD >= 0.166 and averageAWD <= 0.65 and averageAPD >= 0.03 and averageAPD <= 0.25):
                    newSegment = self.createSegment(wordSegment, averagePMER, averageWMER, averageAPD, averageAWD,
                                                    transcript, fileName, segmentNumber)
                    self.selectedData.append(newSegment)



    def createSegment(self, wordDatum, pmer, wmer, apd, awd, transcript, fileName, segmentId):
        segment = {}
        segment[SPEAKER] = wordDatum[commonParser.SPEAKER]
        segment[PMER] = pmer
        segment[WMER] = wmer
        segment[APD] = apd
        segment[AWD] = awd
        segment[START_TIME] = wordDatum[commonParser.START_TIME]
        segment[END_TIME] = wordDatum[commonParser.END_TIME]
        segment[TRANSCRIPT] = transcript
        segment[FILENAME] = fileName
        segment[SEGMENT_ID] = segmentId

        if len(transcript) == 0:
            print ' '.join(transcript) + fileName + str(SEGMENT_ID)
            assert len(transcript) != 0

        return segment

    def getData(self):
        return self.selectedData
