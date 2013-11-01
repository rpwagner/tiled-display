import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateAMConfig():
    c = TileConfig()

    # the local window is the same for most nodes.
    #localWindow = LocalWindow(Rect(0,0,2560, 1024))
    localWindow = LocalWindow(Rect(0,0,2048, 768))
    # this one has two tiles oriented vertically.
    localWindow2rows = LocalWindow(Rect(0,0,1024, 1536))

    """
    t0 = TileDesc( (2048, 768), (0,0),     ":0")
    m6 = MachineDesc( "am-mac6", tiles = [t0], windows=[localWindow])
    c.addMachine(m6)
    """

    t2 = TileDesc( (2048, 768), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (0,0)))
    m3 = MachineDesc( "am-mac3", tiles = [t2], windows=[localWindow])
    c.addMachine(m3)

    t4 = TileDesc( (2048, 768), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (0,768), relative=t2.uid ))
    m1 = MachineDesc( "am-mac1", tiles = [t4], windows=[localWindow])
    c.addMachine(m1)

    """
    t6 = TileDesc( (2048, 768), (0,0), None, location=TileLocation( (2048,0), relative=t0.uid ))
    m5 = MachineDesc( "am-mac5", tiles = [t6], windows=[localWindow])
    c.addMachine(m5)
    """

    t8 = TileDesc( (2048, 768), (0,0), None, location=TileLocation( (2048,0), relative=t2.uid ))
    m4 = MachineDesc( "am-mac4", tiles = [t8], windows=[localWindow])
    c.addMachine(m4)

    t10 = TileDesc( (2048, 768), (0,0), None, location=TileLocation( (0,768), relative=t8.uid ))
    m2 = MachineDesc( "am-mac2", tiles = [t10], windows=[localWindow])
    c.addMachine(m2)

    """
    localWindowB = LocalWindow(Rect(0,0,1024, 768))
    t12 = TileDesc( (1024, 768), (0,0), ":0", location=TileLocation( (2048,0), relative=t6.uid ))
    #t13 = TileDesc( (1024, 768), (1024,0), ":0", location=TileLocation( (0,768), relative=t12.uid ))
    #m8 = MachineDesc( "am-mac8", tiles = [t12, t13], windows=[localWindow])
    m8 = MachineDesc( "am-mac8", tiles = [t12], windows=[localWindowB])
    c.addMachine(m8)

    #t13 = TileDesc( (1024, 768), (1024, 0), ":0", location=TileLocation( (0,768), relative=t12.uid ))
    t13 = TileDesc( (1024, 1536), (0, 0), ":0", location=TileLocation( (0,768), relative=t12.uid ))
    m7 = MachineDesc( "am-mac7", tiles = [t13], windows=[localWindow2rows])
    #m7 = MachineDesc( "am-mac7", tiles = [t13], windows=[localWindow])
    c.addMachine(m7)
"""

    return c

if __name__ == "__main__":

    c = CreateAMConfig()

    SaveConfig(c, "/tmp/testconfig")
    print c.asDict()

    c2 = LoadConfig("/tmp/testconfig")

    if c == c2:
        print "PASS: Saved and reread config matched original."
    else:
        print "FAIL: Saved and reread config did not match original.  Saving as testconfig2 for comparison"
        SaveConfig(c2, "/tmp/testconfig2")

