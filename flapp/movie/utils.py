from subprocess import Popen, PIPE, STDOUT

def GetMovieFPS(path):
    #mplayer -vo null -nosound 0_0.mpg -ss 00:10:00 -endpos 00:00:01
    output = Popen(["mplayer", "-vo", "null", "-nosound", path, "-endpos", "00:00:01"], stdout=PIPE, stderr=STDOUT).communicate()[0]
    linestart = output.index("VIDEO: ")
    lineend = linestart + output[linestart:].index("\n")
    #print "line start,end:", linestart, lineend
    line = output[linestart:lineend]
    #print "line:", line
    words = line.split()
    #print "words:", words
    fpsIndex = words.index("fps") - 1
    fps = float(words[fpsIndex])
    return fps

def GetMovieDuration(path):
    output = Popen(["ffmpeg", "-i", path], stdout=PIPE, stderr=STDOUT).communicate()[0]
    start = output.index("Duration: ")
    end = output.index(", start: ")
    duration = output[start+len("Duration: "):end]
    hours, mins,secs = duration.split(":")
    totalSecs = float(hours)* 60 * 60 + float(mins) * 60 + float(secs)
    return totalSecs

if __name__=="__main__":
    import sys
    path = sys.argv[1]
    duration =  GetMovieDuration(path)
    FPS =  GetMovieFPS(path)
    print "duration:", duration
    print "FPS:", FPS
