import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flTile.tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation

c = TileConfig()

t0 = TileDesc( (1280, 1024), ":0")
t1 = TileDesc( (1280, 1024), ":0", location=TileLocation( (1280,0), relative=t0.uid))
m1 = MachineDesc( "am-mac1", tiles = [t0, t1])
c.addMachine(m1)

t2 = TileDesc( (1280, 1024), ":0", location=TileLocation( (0,1024), relative=t0.uid ))
t3 = TileDesc( (1280, 1024), ":0", location=TileLocation( (1280,0), relative=t2.uid ))
m2 = MachineDesc( "am-mac2", tiles = [t2, t3])
c.addMachine(m2)

SaveConfig(c, "/tmp/testconfig")
print c.asDict()

c2 = LoadConfig("/tmp/testconfig")

if c == c2:
    print "PASS: Saved and reread config matched original."
else:
    print "FAIL: Saved and reread config did not match original.  Saving as testconfig2 for comparison"
    SaveConfig(c2, "/tmp/testconfig2")

