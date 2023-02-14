from vnxtk.builders import BifurcationVNetBuilder
from vnxtk.flow_models import LinearModel
from vnxtk.builders.bifurcation import BifurcationBoundaryConditions

builder = BifurcationVNetBuilder(depth=3, thinned=False, boundary_conditions=BifurcationBoundaryConditions.CROSS_LOAD)
V = builder()
model = LinearModel()
V.model(model)
