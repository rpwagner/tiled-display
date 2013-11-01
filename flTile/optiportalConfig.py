import sys, os
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from tileConfig import TileConfig, TileDesc, MachineDesc, SaveConfig, LoadConfig, TileLocation, Rect, LocalWindow

def CreateOptIPortalConfig():
    c = TileConfig()

    #localWindow = LocalWindow(Rect(0,0,10240, 1600))
    localWindow0 = LocalWindow(Rect(0,0,5120, 1600), ":0")
    localWindow1 = LocalWindow(Rect(0,0,5120, 1600), ":1")


    # Currently config coordinates are based on bottom left origin, so we'll start with tile-0-3 
    t6 = TileDesc( (5120, 1600), (0,0), None)
    t7 = TileDesc( (5120, 1600), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (5120,0), relative=t6.uid ))
    avengerD0= MachineDesc( "tile-0-3", tiles = [t6], windows=[localWindow0])
    c.addMachine(avengerD0)
    avengerD1 = MachineDesc( "tile-0-3", tiles = [t7], windows=[localWindow1])
    c.addMachine(avengerD1)


    t4 = TileDesc( (5120, 1600), (0,0), None, location=TileLocation( (0,1600), relative=t6.uid))
    t5 = TileDesc( (5120, 1600), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (5120,0), relative=t4.uid ))
    avengerC0= MachineDesc( "tile-0-2", tiles = [t4], windows=[localWindow0])
    c.addMachine(avengerC0)
    avengerC1 = MachineDesc( "tile-0-2", tiles = [t5], windows=[localWindow1])
    c.addMachine(avengerC1)


    t2 = TileDesc( (5120, 1600), (0,0), None, location=TileLocation( (0,1600), relative=t4.uid))
    t3 = TileDesc( (5120, 1600), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (5120,0), relative=t2.uid ))
    wasp0 = MachineDesc( "tile-0-1", tiles = [t2], windows=[localWindow0])
    c.addMachine(wasp0)
    wasp1 = MachineDesc( "tile-0-1", tiles = [t3], windows=[localWindow1])
    c.addMachine(wasp1)


    t0 = TileDesc( (5120, 1600), (0,0), None, location=TileLocation( (0,1600), relative=t2.uid))
    t1 = TileDesc( (5120, 1600), (0,0), None, lrtbMullions=(0,0,0,0), location=TileLocation( (5120,0), relative=t0.uid ))
    ironman0= MachineDesc( "tile-0-0", tiles = [t0], windows=[localWindow0])
    c.addMachine(ironman0)
    ironman1 = MachineDesc( "tile-0-0", tiles = [t1], windows=[localWindow1])
    c.addMachine(ironman1)

    return c


if __name__ == "__main__":

    c = CreateOptIPortalConfig()
