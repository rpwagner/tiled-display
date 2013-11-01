import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateLocalTestConfig():
    c = TileConfig()

    t0 = TileDesc( (200, 200), (0,0),    ":0", localWindowId=0)
    t1 = TileDesc( (200, 200), (200, 0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (200,0), relative=t0.uid), localWindowId=0)
    print "t1 relative:", t1.location.relative
    localWindow = LocalWindow(Rect(0,0,400,200))

    m3 = MachineDesc( "maze", tiles = [t0, t1], windows=[localWindow])
    c.addMachine(m3)
    return c

if __name__ == "__main__":

    c = CreateLocalTestConfig()

    SaveConfig(c, "/tmp/testconfig")
    print c.asDict()

    c2 = LoadConfig("/tmp/testconfig")

    if c == c2:
        print "PASS: Saved and reread config matched original."
    else:
        print "FAIL: Saved and reread config did not match original.  Saving as testconfig2 for comparison"
        SaveConfig(c2, "/tmp/testconfig2")

