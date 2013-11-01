
from ctypes import *
import os
libtest = cdll.LoadLibrary(os.getcwd() + '/libTestDataSrc.so')

x=c_float()
y=c_float()
libtest.newDataXY(byref(x), byref(y))
print x.value,y.value

