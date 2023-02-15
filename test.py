from vnxtk.builders import (
    BifurcationBuilder,
    GridBuilder,
    VoronoiBuilder,
    ReanimateBuilder,
)
from vnxtk.flow_models import LinearModel
from vnxtk.alterations import RandomRemoval, RandomRewiring
from vnxtk.builders.bifurcation import BifurcationBoundaryConditions
from vnxtk.builders.grid import GridBoundaryConditions

builder = BifurcationBuilder(
    depth=5, thinned=False, boundary_conditions=BifurcationBoundaryConditions.USUAL
)
# builder = GridBuilder(size=5, boundary_conditions=GridBoundaryConditions.CROSS_LOAD)
# builder = VoronoiBuilder(n_points=50)
V = builder()
model = LinearModel()
V.model(model)
print(V.underlying.number_of_edges())
alt = RandomRewiring(1)
V2 = V.copy()
alt(V2)
V2.model(model)
print(V2.underlying.number_of_edges())
fig = V2.get_interactive_graph_viewer(cone_key="speed")
fig.show()
