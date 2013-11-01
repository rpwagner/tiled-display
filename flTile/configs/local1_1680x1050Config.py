import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateLocal2TestConfig():
    c = TileConfig()

    t0 = TileDesc( (1680, 1050), (0,0),    ":0", localWindowId=0)
    localWindow2 = LocalWindow(Rect(0,0,1680,1050))
    m3 = MachineDesc( "localhost", tiles = [t0], windows=[localWindow2])
    c.addMachine(m3)

    """
    t0 = TileDesc( (840, 525), (0,0),    ":0", localWindowId=0)
    t1 = TileDesc( (840, 525), (840, 0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (840,0), relative=t0.uid), localWindowId=0)
    print "t1 relative:", t1.location.relative

    t2 = TileDesc( (840, 525), (0,525),    ":0", localWindowId=0, location=TileLocation( (0,525), relative=t0.uid))
    t3 = TileDesc( (840, 525), (840, 525), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (840,0), relative=t2.uid), localWindowId=0)
    #localWindow1 = LocalWindow(Rect(0,525,1680,525))
    localWindow2 = LocalWindow(Rect(0,0,1680,1050))

    m3 = MachineDesc( "localhost", tiles = [t0, t1, t2, t3], windows=[localWindow2])
    c.addMachine(m3)
    #m4 = MachineDesc( "localhost", tiles = [t2, t3], windows=[localWindow2])
    #c.addMachine(m4)
    """
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

