import sys
import time
import argparse

from mpi4py import MPI
from firedrake import *

from firedrake_cahn_hilliard_problem import CahnHilliardProblem

parser = argparse.ArgumentParser(
        description="Invoke Cahn-Hilliard CFD problem")
parser.add_argument("mesh_size", type=int,
        help="Size of the unit square mesh along one dimension")
parser.add_argument("--solution-out",
        help="Output filename where to save solution (PVD)")
parser.add_argument("--elapsed-out",
        help="Output filename where to save measured times (CSV)")
parser.add_argument("--degree", type=int, default=1,
        help="Degree of the problem")
parser.add_argument("--steps", type=int, default=1,
        help="Number of timesteps to solve")
parser.add_argument("--preconditioner", default='fieldsplit',
        help="Preconditioner to use")
parser.add_argument("--ksp", default='gmres',
        help="Solver to use")
parser.add_argument("--inner-ksp", default='preonly',
        help="Inner solver to use")
parser.add_argument("--max-iterations", type=int, default=1,
        help="Inner solver to use")
parser.add_argument("--lmbda", type=float, default=1.0e-02,
        help="Surface parameter")
parser.add_argument("--dt", type=float, default=5.0e-06,
        help="Time step")
parser.add_argument("--theta", type=float, default=0.5,
        help="Time stepping family, e.g. theta=1 -> backward Euler, theta=0.5 -> Crank-Nicolson")
parser.add_argument("--compute-norms", action='store_true',
        help="Compute and print norms")
parser.add_argument("--verbose", action='store_true',
        help="Enable extra logging")
args = parser.parse_args()

comm = MPI.COMM_WORLD

params = CahnHilliardProblem.get_solve_params(
        pc=args.preconditioner, ksp=args.ksp, inner_ksp=args.inner_ksp,
        maxit=args.max_iterations, verbose=args.verbose)

time_mesh_begin = time.time()
mesh = CahnHilliardProblem.make_mesh(args.mesh_size)
time_mesh_end = time.time()

time_setup_begin = time.time()
u, u0, solver = CahnHilliardProblem.do_setup(mesh, args.preconditioner,
        degree=args.degree, dt=args.dt, theta=args.theta,
        lmbda=args.lmbda, params=params)
time_setup_end = time.time()

# Output file
if args.solution_out is not None:
    file = File(args.solution_out)
else:
    file = None

time_solve_begin = time.time()
CahnHilliardProblem.do_solve(u, u0, solver, args.steps,
        compute_norms=args.compute_norms, out_file=file)
time_solve_end = time.time()

if comm.rank == 0 and args.elapsed_out is not None:
    from collections import OrderedDict
    times = OrderedDict()
    times["mesh"] = args.mesh_size
    times["mesh_s"]  = time_mesh_end - time_mesh_begin
    times["setup_s"] = time_setup_end - time_setup_begin
    times["solve_s"] = time_solve_end - time_solve_begin

    # note: if you open this earlier, the FD breaks somehow (???)
    fout = open(args.elapsed_out, "w")
    print(",".join(times.keys()), file=fout)
    print(",".join([str(v) for v in times.values()]), file=fout)
    fout.close()

    for step, t in times.items():
        print("%20s: %8.2f" % (step, t))
