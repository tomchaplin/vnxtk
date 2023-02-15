import networkx as nx
import plotly.graph_objects as go
import numpy as np
from vnxtk.flow_models import VNetModel
from vnxtk.alterations import VNetAlteration


class VNet:
    def __init__(self, underlying: nx.Graph, modelled: nx.DiGraph | None = None):
        self.underlying = underlying
        self.modelled = modelled

    def model(self, model: VNetModel):
        self.modelled = model(self.underlying)
        return self

    def alter(self, alteration: VNetAlteration):
        alteration(self)
        return self

    def copy(self):
        return VNet(
            self.underlying.copy(),
            modelled=self.modelled.copy() if self.modelled is not None else None,
        )

    def get_interactive_graph_viewer(
        self, of="modelled", cone_key="weight", min_cone_size=0.5
    ):
        G = self.__getattribute__(of)

        def _format_edge_data(e_data):
            strings = [f"{key}: {value}" for key, value in e_data.items()]
            return "<br>".join(strings)

        def _format_node_data(node, ndt):
            strings = [f"Node: {node}"] + [
                f"{key}: {value}"
                for key, value in ndt.items()
                if key not in ["x", "y", "z"]
            ]
            return "<br>".join(strings)

        node_coords = {
            node: [ndt["x"], ndt["y"], ndt["z"], node]
            for node, ndt in G.nodes(data=True)
        }

        x_nodes = [ndt["x"] for _, ndt in G.nodes(data=True)]
        y_nodes = [ndt["y"] for _, ndt in G.nodes(data=True)]
        z_nodes = [ndt["z"] for _, ndt in G.nodes(data=True)]
        hover_nodes = [_format_node_data(node, ndt) for node, ndt in G.nodes(data=True)]
        max_w = max([e_data[cone_key] for _, _, e_data in G.edges(data=True)])
        x_edges = []
        y_edges = []
        z_edges = []
        cones = {"x": [], "y": [], "z": [], "u": [], "v": [], "w": [], "text": []}
        for u, v, e_data in G.edges(data=True):
            uc = node_coords[u]
            vc = node_coords[v]
            x_edges += [uc[0], vc[0], None]
            y_edges += [uc[1], vc[1], None]
            z_edges += [uc[2], vc[2], None]
            w_scale = min_cone_size * max_w + (1 - min_cone_size) * e_data[cone_key]
            # w_scale = e_data['weight']
            cones["x"] += [0.5 * (uc[0] + vc[0])]
            cones["y"] += [0.5 * (uc[1] + vc[1])]
            cones["z"] += [0.5 * (uc[2] + vc[2])]
            direction = np.array([vc[0] - uc[0], vc[1] - uc[1], vc[2] - uc[2]])
            direction = direction / np.linalg.norm(direction)
            vec = (w_scale * direction).tolist()
            cones["u"] += [vec[0]]
            cones["v"] += [vec[1]]
            cones["w"] += [vec[2]]
            cones["text"] += [_format_edge_data(e_data)]

        trace_cones = go.Cone(
            x=cones["x"],
            y=cones["y"],
            z=cones["z"],
            u=cones["u"],
            v=cones["v"],
            w=cones["w"],
            text=cones["text"],
            hoverinfo="text",
            sizemode="scaled",
            sizeref=0.7,
            showscale=False,
        )

        trace_edges = go.Scatter3d(
            x=x_edges,
            y=y_edges,
            z=z_edges,
            mode="lines",
            line=dict(color="black", width=2),
            hoverinfo="none",
        )
        trace_nodes = go.Scatter3d(
            x=x_nodes,
            y=y_nodes,
            z=z_nodes,
            text=hover_nodes,
            mode="markers",
            marker=dict(symbol="circle", size=2, color="skyblue"),
            hoverinfo="text",
        )
        underlying_traces = [trace_nodes, trace_edges, trace_cones]
        default_scene = {
            "xaxis": {"showspikes": False},
            "yaxis": {"showspikes": False},
            "zaxis": {"showspikes": False},
        }
        default_layout = {"scene": default_scene}
        fig = go.Figure(data=underlying_traces, layout=default_layout)
        return fig
