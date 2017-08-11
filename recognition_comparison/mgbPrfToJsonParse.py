import sys
from parser import commonParser

if __name__ == '__main__':

    if len(sys.argv) % 2 != 1:
        print "must have prf word and prf phone files"
        sys.exit(1)

    prf_files = []
    prf_phone_files = []
    for ii in xrange(1, len(sys.argv), 2):
        prf_files.append(sys.argv[ii])
        prf_phone_files.append(sys.argv[ii + 1])

    prf_models = []
    prf_phones_models = []

    for modelTh in xrange(0, len(prf_files)):
        print "parsing" + prf_files[modelTh]
        parser = commonParser.CommonParser(prf_files[modelTh])
        prf_models.append(parser.getData())
        parser.writeData(prf_files[modelTh] + ".json")

        print "parsing" + prf_phone_files[modelTh]
        parser = commonParser.CommonParser(prf_phone_files[modelTh])
        prf_phones_models.append(parser.getData())
        parser.writeData(prf_phone_files[modelTh] + ".json")