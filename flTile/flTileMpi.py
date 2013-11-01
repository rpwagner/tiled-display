
class FakeMpi:
    # a placeholder used when there is only one node
    #  and mpi is not being used.
    def __init__(self):
        self.rank = 0
        self.procs = 1
    barrier=None

try:
    # When this app is started with pyMPI, "import mpi"
    # will work successfully.  When started with
    # plain "python", fakeMpi is used to show that
    # there is only one process.
    import mpi
except:
    print "WARNING: no mpi, assuming one node"
    #from fakeMpi import mpi
    mpi = FakeMpi()

