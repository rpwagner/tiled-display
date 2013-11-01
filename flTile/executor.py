import os, sys
import string, cgi, time, socket, traceback
from subprocess import Popen, PIPE, STDOUT
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler

import fcntl
import posix

def CheckXineramaEnabled():
    # grep -i \""Xinerama\"" /var/log/Xorg.0.log
    output = Popen(["grep", "-i", "\"Xinerama\"", "/var/log/Xorg.0.log"], stdout=PIPE).communicate()[0]
    words = output.split()
    enabledStr = words[-1]
    enabledStr = enabledStr.replace("\"", "")
    return int(enabledStr)


def ReplaceAmMacPathWithOcularPath(amMacPath):
    if amMacPath:
        tmpPath = amMacPath.replace("/sandbox/insley/movies", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/home/insley/MOLECULES", "/disks/space0/eolson/data/images/insley_MOLECULES")
        tmpPath = tmpPath.replace("/homes/hereld/TCSpix", "/disks/space0/eolson/data/images/hereld/TCSpix")
        tmpPath = tmpPath.replace("/home/eolson/am-macs/data", "/disks/space0/eolson/data/images")
        tmpPath = tmpPath.replace("/disks/space0/eolson/movies/AM", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/sandbox/eolson/movies", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/disks/space0/insley/movies", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/disks/space0/eolson/movies", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/mcs/www.mcs.anl.gov/research/fl/flinternal/AM", "/disks/space0/eolson/data")
        tmpPath = tmpPath.replace("/mcs/www.mcs.anl.gov/research/fl/flinternal/NOAA", "/disks/space0/eolson/data/images/NOAA")
        tmpPath = tmpPath.replace(".tdmovie", ".mp4")
        return tmpPath
    else:
        return amMacPath

posttestHtml = """

<html>
<title>Active Mural Control</title>
<body>
<h1>Active Mural Control</h1>
<form action="control.cgi" method="post">
<p>Application &nbsp;&nbsp;<select name="appId">
  <option>ImageViewer</option>
</select></p>
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Action &nbsp;&nbsp;<select name="action">
  <option>Start</option>
  <option>Stop</option>
</select></p>
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Preset &nbsp;&nbsp;<select name="preset">
  <option>Demo1 Pictures</option>
  <option>TCSANLMural</option>
  <option>Molecules</option>
  <option>ChicagoMap</option>
  <option>Cityscapes</option>
  <option>EnzoUniverseSimulation</option>
</select></p>
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Collection &nbsp;&nbsp;<input type="text" name="collection">
</input>
</p>

<p><input type="submit" value="   Go   " /></p?
</form>
</body></html>
"""
#<p>Application p;&nbsp;&nbsp;<input type="text" name="appId" size="40"/></p>
#<p>Action <input type="text" name="action" size="40"/></p>

class ExecutorHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        print "GET:", self.path, self.path.startswith("/control.cgi")
        if self.path == "/posttest.html" or self.path == "/":
            # print dir(self)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(posttestHtml)
            return
        elif self.path.startswith("/control.cgi"):
            print "process control get";
            trailingLine = self.path.split("?")[1]
            entries = trailingLine.split("&")
            entryDict = {}
            for entry in entries:
                if "=" in entry:
                    pos = entry.index("=")
                    key = entry[:pos] 
                    value = entry[pos+1:]
                    entryDict[key] = value
            print entryDict
            appId = None
            action = None
            collection = None
            preset = None
            scale = None
            pos = None
            if "appId" in entryDict:
                appId = entryDict["appId"]
            if "preset" in entryDict:
                preset = entryDict["preset"]
            if "collection" in entryDict:
                collection = entryDict["collection"]
            if "action" in entryDict:
                action = entryDict["action"]
            if "scale" in entryDict:
                scale = entryDict["scale"]
            if "pos" in entryDict:
                pos = entryDict["pos"]

            print "preset: ", preset, "collection:", collection, "appId:", appId, "action:", action, "scale:", scale, "pos:", pos

            cmd, args, msg = self.processRequest(preset, collection, appId, action, scale, pos)
            self.runCmd(cmd, args, self.wfile)
            


        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self._do_POST()
        except:
            traceback.print_exc()

    def _do_POST(self):
        try:
            if self.path == "/control.cgi":
                print "POST path:", self.path
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                length = int(self.headers.getheader('content-length'))
                appId = None
                action = None
                collection = None
                preset = None
                scale = None
                pos = None

                print "ctype:", ctype
                if ctype == 'multipart/form-data' :
                    query=cgi.parse_multipart(self.rfile, pdict)
                    appId = query.get('appId')
                    action = query.get('action')
                    collection = query.get('collection')
                    preset = query.get('preset')
                    scale = query.get('scale')
                    pos = query.get('pos')
                elif ctype =='application/x-www-form-urlencoded':
                    #http://www.velocityreviews.com/forums/t341231-how-to-read-posted-data.html
                    qs = self.rfile.read(length)
                    body=cgi.parse_qs(qs, pdict)
                    print "body:", body
                    appId = body.get('appId')
                    action = body.get('action')
                    collection = body.get('collection')
                    preset = body.get('preset')
                    scale = body.get('scale')
                    pos = body.get('pos')

                if appId != None:
                    appId = appId[0]
                if action != None:
                    action = action[0]
                if collection != None:
                    collection = collection[0]
                if preset != None:
                    preset = preset[0]
                if scale != None:
                    scale = scale[0]
                if pos != None:
                    pos = pos[0]

                print "preset: ", preset, "collection:", collection, "appId:", appId, "action:", action, "scale: ", scale, "pos:", pos

                cmd, args, msg = self.processRequest(preset, collection, appId, action, scale, pos)


                print "Before send response"
                self.send_response(301)

                self.end_headers()
                print "After end headers"
                self.wfile.write("<HTML>%s</HTML>" % msg)
                self.wfile.flush()
                print "After write html %s" % msg

                self.runCmd(cmd, args, self.wfile)

                """
                if cmd != None and "am-mac" in socket.gethostname():
                    print "Before start cmd"
                    # Make the file descriptor not get inherited when a process is spawned.
                    fd = self.wfile
                    old = fcntl.fcntl(fd, fcntl.F_GETFD)
                    fcntl.fcntl(fd, fcntl.F_SETFD, old | fcntl.FD_CLOEXEC)

                    print "Debug:", cmd, args
                    cmd = "/bin/sleep"
                    args = ["30"]
                    print "Debug:", cmd, args
                    pid = Popen([cmd] + args).pid
                    #import threading
                    #threading.Thread(target=Popen, args=[[cmd] + args]).start()
                    #os.system(cmd + " " + " ".join(args) + " & ")
                    print "After start cmd"
                """

            else:
                self.send_response(301)
                self.end_headers()
                self.wfile.write("<HTML>File not found %s.</HTML>" % self.path)
        except:
            traceback.print_exc()
            

    def processRequest(self, preset, collection, appId, action, scale=None, pos=None):
                cmd = None
                args = []
                if appId != None and action != None:
                    print "processReq, appId != None, action != None"
                    # do command
                    msg = "DefaultResponse"
                    if action.lower() == "start":
                        print "processReq, action == start"
                        #cmd = "sh mpiTileArg.sh /home/eolson/am-macs/data/largeImageViewable &"
                        #print cmd

                        dataDir = ""
                        defaultDataDir = "/home/eolson/am-macs/data/largeImageViewable"

                        msg = "Starting Image Viewer on Active Mural."

                        doingCollection=False

                        # Check if "collection" set first otherwise use preset.
                        if collection != None and len(collection) > 0:
                            if type(collection) == type(""):
                                collection = collection.replace("%20", " ")
                                print "SPACE REPLACE COLLECTION:", collection
                                collection = ReplaceAmMacPathWithOcularPath(collection)
                                print "AFTER REPLACE:", collection
                            if os.path.exists(collection): # orig, one path
                                print "processReq, doing collection, singlepath"
                                dataDir = collection
                                doingCollection=True
                            elif " " in collection:
                                print "processReq, doing collection, maybe multipath"
                                doingCollection=True
                                rawpaths = collection.split()
                                dataDir = ""
                                for rawpath in rawpaths:
                                    # check if it's a layout
                                    print "CHECKING FOR LAYOUT:", rawpath
                                    if rawpath.endswith("tile-description.txt"):
                                        print "Adding movie layout"
                                        if len(dataDir) > 0:
                                            dataDir += " "
                                        dataDir += "--movieLayout %s" % rawpath
                                    else:
                                        if len(rawpath.strip()) > 0:
                                            if len(dataDir) > 0:
                                                dataDir += " "
                                            dataDir += "%s" % rawpath.strip()
                                print "multi collection path:", dataDir
                        if doingCollection:
                            pass
                        elif preset != None:
                            print "processReq, doing preset"
                            if preset.lower() == "molecules":
                                dataDir = "/home/insley/MOLECULES/THREE-T"
                            elif preset.lower() == "tcsanlmural":
                                #dataDir = "/homes/hereld/TCS11jek10k/tcs11-jek10k.png"
                                dataDir = "/homes/hereld/TCSpix/tcs18-uyr10K.png"
                            elif preset.lower() == "chicagomap":
                                dataDir = "/home/eolson/am-macs/data/binns/map1.png"
                            elif preset.lower() == "cityscapes":
                                dataDir = "/home/eolson/am-macs/data/cities"
                            elif preset.lower() == "enzouniverse":
                                dataDir = "/sandbox/eolson/movies/enzo.tdmovie"
                            else:
                                dataDir = defaultDataDir
                        else: # demo1
                            print "processReq, not doing collection or preset"
                            dataDir = defaultDataDir

                        if len(dataDir) == 0 and not os.path.exists(dataDir):
                            dataDir = defaultDataDir

                        scaleArg = ""
                        if None != scale:
                            scaleArg = " --scale=%s " % scale
                        print "scale arg? ", scaleArg

                        posArg = ""
                        if None != pos:
                            posArg = " --pos=%s " % pos
                        print "pos arg? ", posArg

                        #exePath = "/home/eolson/am-macs/src/flPy/flTile/mpiTileArg.sh"

                        if "am-mac" in socket.gethostname():
                            #longArgs = (" -np 8 -machinefile /home/eolson/am-macs/machinefile /home/eolson/am-macs/local/bin/pyMPI tileImage.py -c am24screens " + dataDir + scaleArg).split(" ")
                            #longArgs = (" -np 8 -machinefile /home/eolson/am-macs/machinefile /home/eolson/am-macs/local/bin/myPyMPI tileImage.py -c am24screens " + dataDir + scaleArg + posArg).split(" ")
                            #longArgs = (" -np 6 -machinefile /home/eolson/am-macs/machinefile_nomac1or2 /home/eolson/am-macs/local/bin/myPyMPI tileImage.py -c am24screens_nomac1or2 " + dataDir + scaleArg + posArg).split(" ")
                            longArgs = (" -np 4 -machinefile /home/eolson/am-macs/machinefile_3458 /home/eolson/am-macs/local/bin/myPyMPI tileImage.py -c am24screens_3458_4tiles " + dataDir + scaleArg + posArg).split(" ")
                            #longArgs = (" -np 7 -machinefile /home/eolson/am-macs/machinefile_no_mac6 /home/eolson/am-macs/local/bin/myPyMPI tileImage.py -c am24screens_swap56 " + dataDir + scaleArg + posArg).split(" ")
                            #os.system(cmd)
                            #pid = Popen(["/bin/sh", exePath, dataDir]).pid
                            #pid = Popen(["/usr/bin/mpirun"] + longArgs ).pid
                            cmd = "/usr/bin/mpirun"
                            args = longArgs
                            #print "After start job"
                        elif "ocular" in socket.gethostname():
                            dataDir = ReplaceAmMacPathWithOcularPath(dataDir)

                            if ".mp4" in dataDir or ".mov" in dataDir:
                                cmd = "/usr/bin/xine"
                                args = ["--no-splash","--auto-play=Fh", "--loop=loop", dataDir]
                            else:
                                if 0==CheckXineramaEnabled():
                                    cmd = "/home/eolson/src/flTile/am24screens_ocular_8tiles_8displays.sh"
                                    print "Xinerama is disabled."
                                else:
                                    cmd = "/home/eolson/src/flTile/am1screen.sh"
                                    print "Xinerama is enabled."
                                args = (dataDir + scaleArg + posArg).split()

                    elif action.lower() == "startkinect":
                        msg = "Starting Kinect on Active Mural."
                        if "am-mac" in socket.gethostname():
                            cmd = "/home/eolson/am-macs/scripts/startkinect.py"
                            args = []
                        elif "ocular" in socket.gethostname():
                            cmd = "/home/eolson/scripts/startkinect.py"
                            args = []
                    elif action.lower() == "stopkinect":
                        msg = "Stopping Kinect on Active Mural."
                        if "am-mac" in socket.gethostname():
                            cmd = "/home/eolson/am-macs/scripts/stopkinect.py"
                            args = []
                        elif "ocular" in socket.gethostname():
                            cmd = "/home/eolson/scripts/stopkinect.py"
                            args = []
                    elif action.lower() == "startpaint":
                        if "ocular" in socket.gethostname():
                            cmd = "/usr/bin/tuxpaint"
                            args = ["--nolockfile"]
                    elif action.lower() == "stoppaint":
                        if "ocular" in socket.gethostname():
                            cmd = "/home/eolson/scripts/stopapp.py"
                            args = ["tuxpaint"]

                    else: # action == stop
                        #cmd = "killall pyMPI &"
                        #print cmd
                        msg = "Stopping Image Viewer on Active Mural."
                        if "am-mac" in socket.gethostname():
                            #os.system(cmd)
                            #cmd = "/usr/bin/killall"
                            cmd = "/home/eolson/am-macs/scripts/stopapp.py"
                            args = ["pyMPI", "java"]
                            #pid = Popen(["/usr/bin/killall", "pyMPI"]).pid
                        elif "ocular" in socket.gethostname():
                            #cmd = "/usr/bin/killall"
                            #args = ["xine", "tileImage.py", "pyMPI"]
                            cmd = "/home/eolson/scripts/stopapp.py"
                            args = ["xine", "flTile"]
                else:
                    print "Not doing anything, appId or action is None:", appId, action
                    msg = "You must choose an application and an action"
                #print "returning:", cmd, args, msg
                return cmd, args, msg

    def runCmd(self, cmd, args, wfile):
                if cmd != None and ("am-mac" in socket.gethostname() or "ocular" in socket.gethostname()):
                    print "Before start cmd", cmd, args
                    # Make the file descriptor not get inherited when a process is spawned.
                    fd = wfile
                    old = fcntl.fcntl(fd, fcntl.F_GETFD)
                    fcntl.fcntl(fd, fcntl.F_SETFD, old | fcntl.FD_CLOEXEC)

                    #print "Debug:", cmd, args
                    #cmd = "/bin/sleep"
                    #args = ["30"]
                    #print "Debug:", cmd, args
                    pid = Popen([cmd] + args).pid
                    #import threading
                    #threading.Thread(target=Popen, args=[[cmd] + args]).start()
                    #os.system(cmd + " " + " ".join(args) + " & ")
                    print "After start cmd"
    
        
def main(port, debug=False):
    try:
        server = HTTPServer(('', port), ExecutorHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down'
        server.socket.close()

if __name__ == "__main__":
    port = 8080
    debug=False
    if len(sys.argv) > 1:
       port = int(sys.argv[1])
       debug=True
    main(port=port, debug=debug)

