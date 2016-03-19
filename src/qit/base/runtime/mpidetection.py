mpi_available = False

try:
    from mpi4py import MPI
    if MPI.COMM_WORLD.Get_size() >= 2:
        mpi_available = True

except ImportError:
    pass
