from compare import compareByAPD

class DataWriter:
    def __init__(self, comparerResult, totalDuration, wavdir, outdir):

        segments_file = open(outdir + '/segments', 'w')
        utt2spk_file = open(outdir + '/utt2spk', 'w')
        text_file = open(outdir + '/text', 'w')
        wav_file = open(outdir + '/wav.scp', 'w')

        segFileLines = ""
        textFileLines = ""
        utt2spkFileLines = ""
        wavFileLines = ""


        currentDuration = 0.0
        currentPMER = 0.0
        for segment in comparerResult:
            segmentId = segment[compareByAPD.SEGMENT_ID]
            basename = segment[compareByAPD.FILENAME]
            spk = segment[compareByAPD.SPEAKER]
            start = segment[compareByAPD.START_TIME]
            end = segment[compareByAPD.END_TIME]
            words = ' '.join(segment[compareByAPD.TRANSCRIPT])
            currentPMER = segment[compareByAPD.PMER]

            if (len(words) == 0) :
                print basename + str(start) + words + " " + str(segmentId)
                assert len(words) != 0

            segId = '%s_spk-%04d_seg-%07d:%07d' % (basename, spk, start * 100, end * 100)
            spkId = '%s_spk-%04d' % (basename, spk)

            if currentDuration <= totalDuration:
                currentDuration += (end-start)

                segFileLines += '%s %s %.2f %.2f\n' % (segId, basename, start, end)
                textFileLines += '%s %s\n' % (segId, words)
                utt2spkFileLines += '%s %s\n' % (segId, spkId)
                wavFileLines += '%s %s/%s.wav\n' % (basename, wavdir, basename)
            else:
                break

        print "***** Total duration: " + str(currentDuration) + " PMER: " + str(currentPMER)

        segments_file.write(segFileLines)
        text_file.write(textFileLines)
        utt2spk_file.write(utt2spkFileLines)
        wav_file.write(wavFileLines)

        segments_file.close()
        utt2spk_file.close()
        text_file.close()
        wav_file.close()