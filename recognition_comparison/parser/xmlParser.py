from lxml import etree
import json

PMER = "PMER"
WMER = "WMER"
AWD = "AWD"
START_TIME = "start"
END_TIME = "end"
TRANSCRIPT = "transcript"

class XmlParser:
    def __init__(self, inputXMlFolder, fileList):
        self.data = {}

        with open(fileList, "r") as inputFile:
            for fileName in inputFile:
                fileName = fileName.strip()
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(inputXMlFolder + "/" + fileName + ".xml", parser)

                self.parseTree(tree, fileName)


    def parseTree(self, tree, fileName):
        segmentNodes = tree.xpath("//segments[@annotation_id='transcript_align']/segment")
        for segmentNode in segmentNodes:
            lineData = {}

            #print segmentNode.get("PMER")

            lineData[PMER] = float(segmentNode.get("PMER"))
            lineData[WMER] = float(segmentNode.get("WMER"))
            lineData[AWD] = float(segmentNode.get("AWD"))
            lineData[START_TIME] = float(segmentNode.get("starttime"))
            lineData[END_TIME] = float(segmentNode.get("endtime"))
            lineData[TRANSCRIPT] = segmentNode.xpath("element/text()")

            if not fileName in self.data:
                self.data[fileName] = []
            self.data[fileName].append(lineData)

    def getData(self):
        return self.data

    def writeData(self, fileName):
        with open(fileName, 'w') as outfile:
            json.dump(self.data, outfile)
            print "writing finish"
