import re
import json

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

MATCHED_ERROR_RATE = "matchedErrorRate"
START_TIME = "start"
END_TIME = "end"
SPEAKER = "speaker"
FILENAME = "filename"
HYPOTHESIS = "hypothesis"
WORDS_TIME = "time"
CONFIDENCE = "confidence"
AVERAGE_DURATION = "averageDuration"

class CommonParser:
    def __init__(self, wordFile):
        self.inputFile = open(wordFile, "r")

        self.current_state = 0
        self.speaker = 0
        self.fileName = ""
        self.matchedErrorRate = 0.0
        self.startTime = 0.0
        self.endTime = 0.0
        self.data = {}

        for line in self.inputFile:
            self.parseLine(line)


    def check_first_line(self, line):
        lineRegex = lineRegex1.match(line)
        if lineRegex is not None and lineRegex.group(1) is not None and lineRegex.group(2) is not None:
            speaker = int(lineRegex.group(1))
            return 1, int(speaker)
        return 0, 0

    def check_4th_line(self, line):
        lineRegex = lineRegex4.match(line)
        if lineRegex is not None and lineRegex.group(1) is not None:
            file = lineRegex.group(1)
            return 4, file
        return 0, None

    def check_6th_line(self, line):
        lineRegex = lineRegex6.match(line)
        if lineRegex is not None:
            correct = float(lineRegex.group(1))
            substitution = float(lineRegex.group(2))
            deletion = float(lineRegex.group(3))
            insertion = float(lineRegex.group(4))
            return 6, correct, substitution, deletion, insertion
        return 0, None

    def check_7th_line(self, line):
        lineRegex = lineRegex7.match(line)
        if lineRegex is not None:
            startTime = lineRegex.group(1)
            endTime = lineRegex.group(2)
            return 7, float(startTime), float(endTime)
        return 0, "", ""

    def skip_line(self, line, lineRegexPattern):
        lineRegex = lineRegexPattern.match(line)
        if lineRegex is not None:
            return self.current_state + 1
        return 0

    def check_words_line(self, line, lineRegexx, lineRegexxSplit):
        lineRegex = lineRegexx.match(line)
        if lineRegex is not None:
            referenceWordsSentence = lineRegex.group(1)
            referenceWords = lineRegexxSplit.split(referenceWordsSentence)
            referenceWords = filter(lambda word: len(word) > 0, referenceWords)
            referenceWords = map(lambda word: word.upper(), referenceWords)
            return self.current_state + 1, referenceWords
        return (0, [])

    def check_floats_line(self, line, lineRegexx, lineRegexxSplit):
        lineRegex = lineRegexx.match(line)
        if lineRegex is not None:
            referenceWordsSentence = lineRegex.group(1)
            referenceWords = lineRegexxSplit.split(referenceWordsSentence)
            referenceWords = filter(lambda word: len(word) > 0, referenceWords)
            referenceWords = map(lambda val:float(val), referenceWords)
            return self.current_state + 1, referenceWords
        return (0, [])

    def parseLine(self, line):
        if self.current_state == 0:
            (self.current_state, self.speaker) = self.check_first_line(line)
        elif self.current_state == 1:
            self.current_state = self.skip_line(line, lineRegex2)
        elif self.current_state == 2:
            self.current_state = self.skip_line(line, lineRegex3)
        elif self.current_state == 3:
            (self.current_state, self.fileName) = self.check_4th_line(line)
        elif self.current_state == 4:
            self.current_state = self.skip_line(line, lineRegex5)
        elif self.current_state == 5:
            (self.current_state, correct, substitution, deletion, insertion) = self.check_6th_line(line)
            self.matchedErrorRate = (100.0 * (substitution + deletion + insertion)) / (substitution + deletion + correct)
        elif self.current_state == 6:
            (self.current_state, self.startTime, self.endTime) = self.check_7th_line(line)
        elif self.current_state == 7:
            self.current_state = self.skip_line(line, lineRegex8)
        elif self.current_state == 8:
            (self.current_state, self.hypWords) = self.check_words_line(line, lineRegex9, lineRegex9split)
        elif self.current_state == 9:
            self.current_state = self.skip_line(line, lineRegex10)
        elif self.current_state == 10:
            (self.current_state, self.hypWordsTime) = self.check_floats_line(line, lineRegex11, lineRegex11split)
        elif self.current_state == 11:
            (self.current_state, self.confWords) = self.check_floats_line(line, lineRegex12, lineRegex12split)
        elif self.current_state == 12:
            self.current_state = self.skip_line(line, lineRegex13)
        elif self.current_state == 13:
            if not self.fileName in self.data:
                self.data[self.fileName] = []

            lineData = {}

            lineData[MATCHED_ERROR_RATE] = self.matchedErrorRate
            lineData[START_TIME] = self.startTime
            lineData[END_TIME] = self.endTime
            lineData[SPEAKER] = self.speaker
            lineData[FILENAME] = self.fileName
            lineData[HYPOTHESIS] = self.hypWords
            lineData[WORDS_TIME] = self.hypWordsTime
            lineData[CONFIDENCE] = self.confWords
            if (len(self.hypWords)==0):
                lineData[AVERAGE_DURATION] = 0
            else:
                lineData[AVERAGE_DURATION] = ((self.endTime-self.startTime) * 1.0) / len(self.hypWords)

            self.data[self.fileName].append(lineData)

            self.current_state = 0

    def writeData(self, fileName):
        with open(fileName, 'w') as outfile:
            json.dump(self.data, outfile)
            print "writing finish"

    @staticmethod
    def readData(fileName):
        with open(fileName, 'r') as inFile:
            return json.load(inFile)

    def getData(self):
        return self.data