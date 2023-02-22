from vnxtk.builders import (
    BifurcationBuilder,
    GridBuilder,
    VoronoiBuilder,
    ReanimateBuilder,
)
from vnxtk.flow_models import LinearModel
from vnxtk.alterations import RandomRemoval, RandomRewiring, RandomBoundary
from vnxtk.builders.bifurcation import BifurcationBoundaryConditions
from vnxtk.builders.grid import GridBoundaryConditions
from grpphati.pipelines.grounded import GrPPH
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

builder = BifurcationBuilder(
    depth=5, thinned=False, boundary_conditions=BifurcationBoundaryConditions.USUAL
)
# builder = GridBuilder(size=5, boundary_conditions=GridBoundaryConditions.CROSS_LOAD)
# builder = VoronoiBuilder(n_points=50)
V = builder()
model = LinearModel()
V.model(model)
res = GrPPH(V.modelled)
base = sum([bar[1] for bar in res.barcode])

alt = RandomBoundary()
other = []


for i in range(500):
    alt(V)
    V.model(model)
    other_res = GrPPH(V.modelled)
    other.append(min(sum([bar[1] for bar in other_res.barcode]), 2000))

print(base)
sns.histplot(data=other)
plt.show()
