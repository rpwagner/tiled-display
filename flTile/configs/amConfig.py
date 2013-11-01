import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateAMConfig():
    c = TileConfig()

    # currently the local window is the same for all nodes.
    localWindow = LocalWindow(Rect(0,0,2560, 1024))

    t0 = TileDesc( (1280, 1024), (0,0),     ":0")
    t1 = TileDesc( (1280, 1024), (1280, 0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (1050,0), relative=t0.uid))
    print "t1 relative:", t1.location.relative
    m3 = MachineDesc( "am-mac3", tiles = [t0, t1], windows=[localWindow])
    c.addMachine(m3)

    t2 = TileDesc( (1280, 1024), (0,0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (0,840), relative=t0.uid ))
    t3 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (1050,0), relative=t2.uid ))
    m2 = MachineDesc( "am-mac2", tiles = [t2, t3], windows=[localWindow])
    c.addMachine(m2)

    t4 = TileDesc( (1280, 1024), (0,0), ":0", lrtbMullions=(0,0,0,0), location=TileLocation( (0,840), relative=t2.uid ))
    t5 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (1050,0), relative=t4.uid ))
    m1 = MachineDesc( "am-mac1", tiles = [t4, t5], windows=[localWindow])
    c.addMachine(m1)

    t6 = TileDesc( (1280, 1024), (0,0), ":0", location=TileLocation( (1050,0), relative=t1.uid ))
    t7 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (1050,0), relative=t6.uid ))
    m6 = MachineDesc( "am-mac6", tiles = [t6, t7], windows=[localWindow])
    c.addMachine(m6)

    t8 = TileDesc( (1280, 1024), (0,0), ":0", location=TileLocation( (0,840), relative=t6.uid ))
    t9 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (1050,0), relative=t8.uid ))
    m5 = MachineDesc( "am-mac5", tiles = [t8, t9], windows=[localWindow])
    c.addMachine(m5)

    t10 = TileDesc( (1280, 1024), (0,0), ":0", location=TileLocation( (0,840), relative=t8.uid ))
    t11 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (1050,0), relative=t10.uid ))
    m4 = MachineDesc( "am-mac4", tiles = [t10, t11], windows=[localWindow])
    c.addMachine(m4)

    t12 = TileDesc( (1280, 1024), (0,0), ":0", location=TileLocation( (1050,0), relative=t7.uid ))
    #t13 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (0,840), relative=t12.uid ))
    #m8 = MachineDesc( "am-mac8", tiles = [t12, t13], windows=[localWindow])
    m8 = MachineDesc( "am-mac8", tiles = [t12])
    c.addMachine(m8)

    t13 = TileDesc( (1280, 1024), (1280,0), ":0", location=TileLocation( (0,840), relative=t12.uid ))
    t14 = TileDesc( (1280, 1024), (0,0), ":0", location=TileLocation( (0,840), relative=t13.uid ))
    m7 = MachineDesc( "am-mac7", tiles = [t13,t14], windows=[localWindow])
    c.addMachine(m7)

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

