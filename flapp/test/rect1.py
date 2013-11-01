import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.pmath.rect import *

rect1 = Rect(0,0,100,100)
rect2 = Rect(10,10,200,200)
rect3 = Rect(-100,-100,100, 500)
rect4 = Rect(-1000,-1000,100, 500)

#print rect1.union(rect2)
assert rect1.union(rect2) == Rect(0,0,210,210)
#print rect1.union(rect3)
assert rect1.union(rect3) == Rect(-100,-100,200,500)
#print rect1.union(rect4)
assert rect1.union(rect4) == Rect(-1000,-1000,1100,1100)


print "Assertions ok"
