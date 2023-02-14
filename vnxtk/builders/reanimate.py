from .abstract import VNetBuilder
from vnxtk import VNet
import networkx as nx
import re
import numpy as np
import math


def _compute_length(G, i, j):
    i_data = G.nodes[i]
    j_data = G.nodes[j]
    i_coords = np.array([i_data["x"], i_data["y"], i_data["z"]])
    j_coords = np.array([j_data["x"], j_data["y"], j_data["z"]])
    return np.linalg.norm(i_coords - j_coords)


def _compute_weight(G):
    for i, j, data in G.edges(data=True):
        edge_length = _compute_length(G, i, j)
        edge_flow = data["flow"]
        edge_diam = data["diam"]
        edge_speed = edge_flow / ((math.pi / 4) * edge_diam * edge_diam)
        edge_time = np.inf if edge_speed == 0 else edge_length / edge_speed
        edge_time = (
            edge_time / 1000000
        )  # conversion from (micron^3/nL) minutes to minutes
        edge_time = edge_time * 60  # conversion to seconds
        data["length"] = edge_length
        data["speed"] = edge_speed
        data["time"] = edge_time
        data["weight"] = edge_time
    return G


def _parse_lines(lines):
    as_numbers = map(
        lambda line: list(map(float, re.findall(r"[\+\-\d.]+", line))), lines
    )
    return as_numbers


def _add_node_lines(G, node_lines):
    G.add_nodes_from(
        [(line[0], {"x": line[1], "y": line[2], "z": line[3]}) for line in node_lines]
    )
    return G


def _seg_line_to_tuple(line):
    flow = line[5]
    if line[2] == line[3]:
        print(f"Self-loop detected on vertex {line[2]}")
        return None
    if flow > 0:
        return (line[2], line[3], {"diam": line[4], "flow": flow})
    else:
        return (line[3], line[2], {"diam": line[4], "flow": -flow})


def _add_segment_lines(G, segment_lines):
    segments_as_tuples = [_seg_line_to_tuple(line) for line in segment_lines]
    # Remove self loops
    segments_as_tuples = [tup for tup in segments_as_tuples if not tup is None]
    node_pairs = [(t[0], t[1]) for t in segments_as_tuples]
    counts = [node_pairs.count(x) for x in node_pairs]
    multiple_edge_exists = any([count > 1 for count in counts])
    if multiple_edge_exists:
        print(f"Input has multiple edges, last one provided will be used!")
    G.add_edges_from(segments_as_tuples)
    return G


class ReanimateBuilder(VNetBuilder):
    def __init__(self):
        pass

    def __call__(self, fname):
        with open(fname, "r") as file:
            # Read in file
            contents = file.read()
            lines = contents.splitlines()
            # Extract sections of file related to segments and nodes
            enumerated_lines = enumerate(lines)
            segment_lines = []
            node_lines = []
            segment_header_idx = next(
                idx for idx, line in enumerated_lines if line.startswith("Segname")
            )
            node_header_idx = next(
                idx for idx, line in enumerated_lines if line.startswith("Nodname")
            )
            bcnode_header_idx = next(
                idx for idx, line in enumerated_lines if line.startswith("Bcnodname")
            )
            segment_lines = lines[(segment_header_idx + 1) : (node_header_idx - 1)]
            node_lines = lines[(node_header_idx + 1) : (bcnode_header_idx - 1)]
            # Match numbers and convert to floats
            node_lines = _parse_lines(node_lines)
            segment_lines = _parse_lines(segment_lines)
            # Add all the data to a nx digraph
            G = nx.DiGraph()
            G = _add_node_lines(G, node_lines)
            G = _add_segment_lines(G, segment_lines)
            # Compute the weight we are interested in
            G = _compute_weight(G)
            G = nx.convert_node_labels_to_integers(G, label_attribute="reanimate_name")
            # Make copy of graph without modelling information
            underlying = G.to_undirected(reciprocal=False)
            for _, _, data in underlying.edges(data=True):
                del data["flow"]
                del data["speed"]
                del data["time"]
                del data["weight"]
            # Return graph
            return VNet(underlying, modelled=G)
