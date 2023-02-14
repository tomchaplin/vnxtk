from vnxtk.builders import BifurcationVNetBuilder, GridVNetBuilder, VoronoiVNetBuilder
from vnxtk.flow_models import LinearModel
from vnxtk.builders.bifurcation import BifurcationBoundaryConditions
from vnxtk.builders.grid import GridBoundaryConditions

# builder = BifurcationVNetBuilder(
#    depth=3, thinned=False, boundary_conditions=BifurcationBoundaryConditions.CROSS_LOAD
# )
# builder = GridVNetBuilder(size=5, boundary_conditions=GridBoundaryConditions.CROSS_LOAD)
builder = VoronoiVNetBuilder(n_points=50)
V = builder()
model = LinearModel()
V.model(model)
fig = V.get_interactive_graph_viewer(cone_key="speed")
fig.show()
