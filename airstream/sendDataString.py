#!/usr/bin/python

# A simple script to send a string data message, such as "quit".

#   In this case we could use simpler blocking tcp socket code, but it's 
#     easier to just reuse the existing asynchronous code.

#  The use case for this is to make a quick cgi script that sends a 
#    hardcoded message (quit) to the non-publicly accessible input server.
#    To send more data, you could connect directly to the input server or 
#    modify this code into a forwarder with persistent connections.
#    A forwarder could be a service/daemon, keeping the connection open to 
#    the input server, and receiving external messages in some way such as 
#    an http server or a websockets server (twisted could be used easily).

import os, sys, time
# import a plain reactor first since we don't need our own
#   event loop like App normally does.
from twisted.internet import reactor

from windowSender import UserGeneratedInputClientFactory



def run(host=None, port=None, msgStr="defaultmsg"):

    def shutdown():
        print "Shutting down"
        reactor.stop()

    def connectionMade(connectionFactory):
        print "Sending msg:", msgStr
        connectionFactory.connection.sendDataString(msgStr)
        reactor.callLater(2.0, shutdown) # quit after sending the msg

    f = UserGeneratedInputClientFactory()
    f.setVerbose(True)
    f.setConnectionMadeCallback(connectionMade)
    print "Connecting to:", host, port
    reactor.connectTCP(host, port, f)

    reactor.run()
    print "Exiting."

if __name__ == "__main__":
  if (len(sys.argv) > 2):
      host = sys.argv[1]
      port = int(sys.argv[2])
      msgStr = sys.argv[3]
      print "Read msgStr:", msgStr
      run(host, port, msgStr)
  else:
      print "Usage: ", sys.argv[0], "<airstreamhost> <airstreamport> <msgStr>"

