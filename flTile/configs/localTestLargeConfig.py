import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateLocalTestConfig():
    c = TileConfig()

    t0 = TileDesc( (400, 400), (0,0),    ":0", localWindowId=0)
    t1 = TileDesc( (400, 400), (400, 0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (400,0), relative=t0.uid), localWindowId=0)
    print "t1 relative:", t1.location.relative
    t2 = TileDesc( (400, 400), (0,400),    ":0", localWindowId=0, location=TileLocation( (0,400), relative=t0.uid))
    t3 = TileDesc( (400, 400), (400, 400), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (400,0), relative=t2.uid), localWindowId=0)
    localWindow = LocalWindow(Rect(0,0,800,800))

    m3 = MachineDesc( "maze", tiles = [t0, t1, t2, t3], windows=[localWindow])
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

