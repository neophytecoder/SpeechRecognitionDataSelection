from parser import xmlParser
import sys

def accumulateAndSortData(alignData):
    fileNames = alignData.keys()
    accumulatedData = []

    for fileName in fileNames:
        idx = 0
        for segment in alignData[fileName]:
            segment["filename"] = fileName
            segment["segmentid"] = idx
            accumulatedData.append(segment)

            idx += 1

    accumulatedDataTemp = sorted(accumulatedData, key=lambda mydict: mydict[xmlParser.PMER])

    return accumulatedDataTemp

def filterSegmentsByThreshold(sortedAccumulatedData, threshold):
    selectedData = []
    for segment in sortedAccumulatedData:
        awd = segment[xmlParser.AWD]
        if segment[xmlParser.PMER] > threshold and awd >= 0.165 and awd <= 0.66:
            return set(selectedData)
        selectedData.append((segment["filename"], segment["segmentid"]))

if __name__ == '__main__':
    fileList = sys.argv[1]
    alignFolderOne = sys.argv[2]
    alignFolderTwo = sys.argv[3]
    thresholdOne = float(sys.argv[4])
    thresholdTwo = float(sys.argv[5])

    # parse the files
    alignDataOne = xmlParser.XmlParser(alignFolderOne, fileList).getData()
    alignDataTwo = xmlParser.XmlParser(alignFolderTwo, fileList).getData()

    # accumulate and sort files
    accumulatedAlignDataOne = accumulateAndSortData(alignDataOne)
    accumulatedAlignDataTwo = accumulateAndSortData(alignDataTwo)

    # get set of segments
    selectedDataAlignDataOne = filterSegmentsByThreshold(accumulatedAlignDataOne, thresholdOne)
    selectedDataAlignDataTwo = filterSegmentsByThreshold(accumulatedAlignDataTwo, thresholdTwo)

    print "STATISTICS..."
    print "AM one has these, but not in AM two: " + str(len(selectedDataAlignDataOne - selectedDataAlignDataTwo))
    print "AM two has these, but not in AM one: " + str(len(selectedDataAlignDataTwo - selectedDataAlignDataOne))
    print "Similar segments: " + str(len(selectedDataAlignDataOne & selectedDataAlignDataTwo))
    print "Total segments AM one: " + str(len(selectedDataAlignDataOne))
    print "Total segment AM two: " + str(len(selectedDataAlignDataTwo))

