
An example of how to get input device data to an airstream server when the
   source data is obtained in c or c++.


To BUILD:
 Type "make"

Code:
libTestDataSrc.cpp:
  The sample cpp source of the data.  With a real device, cpp code would
  be getting data from the device instead of generating random data.

simpleTestDataSrc.py
  This isn't too bad, but it would require polling each function
  individually.

callbackTestDataSrc.py
  This is better.  After initial setup, call update() when necessary
  and the corresponding data callbacks will be called.
  It's still polling to some extent, but a little more cleanly.

sendExampleDataSrc.py
  minimal full example   (derived from netinput.py)

