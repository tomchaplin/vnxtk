from .abstract import VNetModel
import networkx as nx
import numpy as np
import math
import pdb


def _get_edge_idx(edge, edge_basis):
    sorted_edge = sorted(edge)
    idxs = [ idx for idx, (e, res) in enumerate(edge_basis) if e == sorted ]
    return idxs[0]

# Matrix of equations describing current in = current out at each node
def _build_first_law_eqs(underlying, edge_basis):
    M = np.array([
        [
            1 if edge[1] == node else -1 if edge[0] == node else 0
            for edge,res in edge_basis
        ]
        for node in underlying.nodes
    ])
    b = np.array([ data['external_current'] for node,data in underlying.nodes(data=True)])
    return M, b

def _build_cycle_row(cycle, edge_basis):
    cycle_in_edges = list(zip( cycle, cycle[1:]+[cycle[0]] ))
    row = np.array([
        res if edge in cycle_in_edges else -res if (edge[1], edge[0]) in cycle_in_edges else 0
        for edge, res in edge_basis
    ])
    return row

# Matrix of equations describing no voltage drop around any loop
def _build_second_law_eqs(underlying, edge_basis):
    cycle_basis = nx.cycle_basis(underlying)
    M = np.array([
        _build_cycle_row(cycle, edge_basis)
        for cycle in cycle_basis
        ])
    b = np.array([0 for _ in cycle_basis])
    return M, b

def _build_digraph(underlying, edge_basis, x):
    modelled = underlying.to_directed(as_view = False)
    for (edge,res), current in zip(edge_basis, x):
        if current > 0:
            modelled[edge[0]][edge[1]]['current'] = current
            modelled.remove_edge(edge[1], edge[0])
        else:
            modelled[edge[1]][edge[0]]['current'] = -current
            modelled.remove_edge(edge[0], edge[1])
    for _, _, data in modelled.edges(data=True):
        data['speed'] = data['current']/((math.pi/4.0)*data['diam']*data['diam'])
        data['time'] = data['length']/data['speed']
        data['weight'] = data['time']
    return modelled


class LinearModel(VNetModel):
    def __init__(self):
        pass

    def __call__(self, underlying: nx.Graph) -> nx.DiGraph:
        modelled = nx.DiGraph()
        # List of (edge, resistance) tuples
        edge_basis = [
            ((u, v), d['length']/((math.pi/4.0)*d['diam']*d['diam']))
            for u, v, d in underlying.edges(data=True)
        ]
        # Write down Kirchoff's laws
        M1, b1 = _build_first_law_eqs(underlying, edge_basis)
        M2, b2 = _build_second_law_eqs(underlying, edge_basis)
        M = np.vstack((M1, M2))
        b = np.hstack((b1, b2)).reshape(-1, 1)
        # Compute current in each edge
        x,_,_,_ = np.linalg.lstsq(M, b, rcond=None)
        # Build digraph
        return _build_digraph(underlying, edge_basis, x.flatten().tolist())

