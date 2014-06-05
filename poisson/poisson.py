from pybench import Benchmark

dim = 3
# Create a series of meshes that roughly double in number of DOFs
sizes = [int((1e4*2**x)**(1./dim)) + 1 for x in range(4)]
r0 = ['DOLFIN', 'Firedrake']
regions = ['matrix assembly', 'rhs assembly', 'solve']


class Poisson(Benchmark):

    params = [('dim', [dim]),
              ('degree', range(1, 4)),
              ('size', sizes)]
    meta = {'cells': [6*x**dim for x in sizes],
            'dofs': [(x+1)**dim for x in sizes]}
    plotstyle = {'total': {'marker': '*'},
                 'mesh': {'marker': '+'},
                 'setup': {'marker': 'x'},
                 'matrix assembly': {'marker': '>'},
                 'rhs assembly': {'marker': '<'},
                 'solve': {'marker': 'D'}}
    method = 'poisson'
    name = 'Poisson'
    profilegraph = {'format': 'svg,pdf',
                    'node_threshold': 2.0}
    profileregions = regions

if __name__ == '__main__':
    import sys
    b = Poisson()
    b.combine_series([('np', [1]), ('variant', ['Firedrake', 'DOLFIN'])])
    b.plot(xaxis='size', regions=regions, xlabel='mesh size (cells)',
           xvalues=b.meta['cells'], kinds='plot,loglog', groups=['variant'])
    b.plot(xaxis='degree', regions=regions, xlabel='Polynomial degree',
           kinds='bar,barlog', groups=['variant'])
    if len(sys.argv) > 1:
        np = map(int, sys.argv[1:])
        b = Poisson(name='PoissonParallel')
        b.combine_series([('np', np), ('variant', ['Firedrake', 'DOLFIN'])],
                         filename='Poisson')
        b.plot(xaxis='np', regions=regions, xlabel='Number of processors',
               kinds='plot,loglog', groups=['variant'])
        b.plot(xaxis='np', regions=regions, xlabel='Number of processors',
               kinds='plot', groups=['variant'], speedup=(1, 'DOLFIN'),
               ylabel='Speedup relative to DOLFIN on 1 core')
