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

class CompareByApd:
    def __init__(self, wordDatas, phoneDatas, alignData):
        fileNames= wordDatas[0].keys()
        numberASR = len(wordDatas)

        self.selectedData = []
        self.selectedIds = set([])

        self.wordDatas = wordDatas
        self.phoneDatas = phoneDatas
        self.alignData = alignData

        self.sortByPMERStatistics = 0
        self.zeroPMERStatistics = 0
        self.twoSegmentPhonesStatistics = 0
        self.sortByPMERStatisticsDuration = 0
        self.zeroPMERStatisticsDuration = 0
        self.twoSegmentPhonesStatisticsDuration = 0

        #for fileName in fileNames:
        #    numberSegments = len(wordDatas[0][fileName])
        #    self.decideSegments(fileName, numberSegments, numberASR)

        self.sortByPMER()

    def createSegment(self, wordDatum, phoneDatum, transcript, fileName, segmentId):
        segment = {}
        segment[SPEAKER] = wordDatum[commonParser.SPEAKER]
        segment[PMER] = phoneDatum[commonParser.MATCHED_ERROR_RATE]
        segment[WMER] = wordDatum[commonParser.MATCHED_ERROR_RATE]
        segment[APD] = phoneDatum[commonParser.AVERAGE_DURATION]
        segment[AWD] = wordDatum[commonParser.AVERAGE_DURATION]
        segment[START_TIME] = wordDatum[commonParser.START_TIME]
        segment[END_TIME] = wordDatum[commonParser.END_TIME]
        segment[TRANSCRIPT] = transcript
        segment[FILENAME] = fileName
        segment[SEGMENT_ID] = segmentId

        if len(transcript) == 0:
            print ' '.join(transcript) + fileName + str(SEGMENT_ID)
            assert len(transcript) != 0

        return segment


    def sortByPMER(self):
        numberASR = len(self.wordDatas)

        unsortedAllData = []

        # aggregate all data and sort by PMER
        fileNames = self.wordDatas[0].keys()
        for fileName in fileNames:
            for asrTh in xrange(0, numberASR):
                wordSegments = self.wordDatas[asrTh][fileName]
                phoneSegments = self.phoneDatas[asrTh][fileName]
                for segmentTh in xrange(0, len(wordSegments)):
                    unsortedAllData.append((fileName,
                                            segmentTh,
                                            wordSegments[segmentTh][commonParser.MATCHED_ERROR_RATE],
                                            phoneSegments[segmentTh][commonParser.MATCHED_ERROR_RATE],
                                            asrTh,
                                            wordSegments[segmentTh][commonParser.END_TIME] - wordSegments[segmentTh][commonParser.START_TIME]))
        sortedAllData = sorted(unsortedAllData, key=lambda tup:tup[3])

        # select based on top PMER
        for ii in xrange(0, len(sortedAllData)):
            sortedAllDatum = sortedAllData[ii]
            if not (sortedAllDatum[0], sortedAllDatum[1]) in self.selectedIds:
                # create segment
                fileName = sortedAllDatum[0]
                segmentId = sortedAllDatum[1]
                wordDatum = self.wordDatas[sortedAllDatum[4]][fileName][segmentId]
                phoneDatum = self.phoneDatas[sortedAllDatum[4]][fileName][segmentId]
                alignDatum = self.alignData[fileName][segmentId]
                pmer = sortedAllDatum[3]

                # check by AWD and APD
                awd = wordDatum[commonParser.AVERAGE_DURATION]
                apd = phoneDatum[commonParser.AVERAGE_DURATION]
                if (awd < 0.166 or awd > 0.65 or apd < 0.03 or apd > 0.25):
                    continue

                transcript = alignDatum[xmlParser.TRANSCRIPT]
                segment = self.createSegment(wordDatum, phoneDatum, transcript, fileName, segmentId)
                self.selectedData.append(segment)

                print str((fileName, segmentId)) + " " + "sort pmer: " + str(pmer)
                self.selectedIds.add((fileName, segmentId))

                self.sortByPMERStatistics += 1
                self.sortByPMERStatisticsDuration += sortedAllDatum[5]

    def findBestSegmentIdx(self, wordSegment1, wordSegment2, wordSegment3):
        wmer1 = wordSegment1[commonParser.MATCHED_ERROR_RATE]
        wmer2 = wordSegment2[commonParser.MATCHED_ERROR_RATE]
        wmer3 = wordSegment3[commonParser.MATCHED_ERROR_RATE]

        if wmer1 <= wmer2 and wmer1 <= wmer3:
            return 0
        elif wmer2 <= wmer1 and wmer2 <= wmer3:
            return 1
        return 2

    def decideSegments(self, fileName, numberSegment, numberASR):
        for segmentId in xrange(0, numberSegment):
            #################################
            # choose if pmer or wmer is zero
            foundZeroPMERWMER = False
            jj = 0
            while jj < numberASR and not foundZeroPMERWMER:
                wordSegment = self.wordDatas[jj][fileName][segmentId]
                phoneSegment = self.phoneDatas[jj][fileName][segmentId]
                alignSegment = self.alignData[fileName][segmentId]

                awd = wordSegment[commonParser.AVERAGE_DURATION]
                apd = phoneSegment[commonParser.AVERAGE_DURATION]

                if  (awd < 0.166 or awd > 0.65 or apd < 0.03 or apd > 0.25):
                    jj += 1
                    continue

                if phoneSegment[commonParser.MATCHED_ERROR_RATE] <= 0.001:
                    #create segment
                    segment = self.createSegment(wordSegment, phoneSegment, alignSegment[xmlParser.TRANSCRIPT],
                                                 fileName, segmentId)
                    self.selectedData.append(segment)

                    print str((fileName, segmentId)) + " zero mer " + str(phoneSegment[commonParser.MATCHED_ERROR_RATE])
                    self.selectedIds.add((fileName, segmentId))

                    foundZeroPMERWMER = True

                    self.zeroPMERStatistics += 1
                    self.zeroPMERStatisticsDuration += phoneSegment[commonParser.END_TIME] - phoneSegment[commonParser.START_TIME]

                jj += 1

            #################################
            # choose two segments with the same phone sequence
            if not foundZeroPMERWMER:
                wordSegment1 = self.wordDatas[0][fileName][segmentId]
                phoneSegment1 = self.phoneDatas[0][fileName][segmentId]

                wordSegment2 = self.wordDatas[1][fileName][segmentId]
                phoneSegment2 = self.phoneDatas[1][fileName][segmentId]

                wordSegment3 = self.wordDatas[2][fileName][segmentId]
                phoneSegment3 = self.phoneDatas[2][fileName][segmentId]

                awd = wordSegment1[commonParser.AVERAGE_DURATION]
                apd = phoneSegment1[commonParser.AVERAGE_DURATION]

                if (awd < 0.166 or awd > 0.65 or apd < 0.03 or apd > 0.3):
                    continue

                if phoneSegment1[commonParser.HYPOTHESIS] == phoneSegment2[commonParser.HYPOTHESIS] and \
                                phoneSegment2[commonParser.HYPOTHESIS] == phoneSegment3[commonParser.HYPOTHESIS]:

                    bestWordSegmentIdx = self.findBestSegmentIdx(wordSegment1, wordSegment2, wordSegment3)
                    bestWordSegment = self.wordDatas[bestWordSegmentIdx][fileName][segmentId]
                    bestPhoneSegment = self.phoneDatas[bestWordSegmentIdx][fileName][segmentId]
                    transcript = bestWordSegment[commonParser.HYPOTHESIS]
                    segment = self.createSegment(bestWordSegment, bestPhoneSegment,
                                                 transcript, fileName, segmentId)
                    self.selectedData.append(segment)

                    print str((fileName, segmentId)) + " same phone sequence" \
                          + str(bestWordSegment[commonParser.MATCHED_ERROR_RATE]) \
                          + " " + str(bestPhoneSegment[commonParser.MATCHED_ERROR_RATE])
                    self.selectedIds.add((fileName, segmentId))

                    self.twoSegmentPhonesStatistics += 1
                    self.twoSegmentPhonesStatisticsDuration += phoneSegment[commonParser.END_TIME] - phoneSegment[
                        commonParser.START_TIME]


    def getResult(self):
        return self.selectedData

    def getResultId(self):
        return self.selectedIds

    def printStatistics(self):
        print "zero pmers: " + str(self.zeroPMERStatistics)
        print "two phone segments: " + str(self.twoSegmentPhonesStatistics)
        print "sort by pmer: " + str(self.sortByPMERStatistics)

        print "zero pmers duration: " + str(self.zeroPMERStatisticsDuration)
        print "two phone segments duration: " + str(self.twoSegmentPhonesStatisticsDuration)
        print "sort by pmer duration: " + str(self.sortByPMERStatisticsDuration)


