import sys
from parser import xmlParser

if __name__ == '__main__':
    fileList = sys.argv[1]
    alignFolder = sys.argv[2]

    alignData = xmlParser.XmlParser(alignFolder, fileList)
    alignData.writeData("align.json")
    alignData = alignData.getData()