# Building input

A building has two arrays: `node_data` (N × 16) and `adj_matrix` (N × N).
Use [examples/building.json](../examples/building.json) as a complete example.
The graph is supplied by the caller; the Python package does not infer connections from arbitrary CAD/BIM geometry.
The optional web editor creates component data from its own geometry.

## Raw component columns

These names preserve the spelling and ordering of the original model inputs.

| Index | Name | Meaning / encoding |
|---:|---|---|
| 0 | Name | Component identifier; retained for callers, excluded from model features |
| 1 | ConstructionName | `exterior`, `interior`, `ground`, `roof` |
| 2 | ZoneName | Zone identifier; excluded from this building-level checkpoint |
| 3 | OutsideBoundaryCondiction | `Outdoors`, `Surface`, `Ground` (case-sensitive) |
| 4 | Area | Component area, m²; positive |
| 5 | SI | Dimensionless shape index; use the same definition as the ENB data generation |
| 6 | Subface | 0 none, 1 window, 2 door, 3 window and door |
| 7 | SubfaceArea | Total subface area, m²; positive when Subface is nonzero |
| 8 | SubRes | Legacy field name for the subface thermal property; web/material tables supply `SCon` (U-value, W/(m²·K)) |
| 9 | SubSHGC | Subface solar heat gain coefficient |
| 10 | Res | Legacy field name for the opaque material property; web/material tables supply `Con` (conductivity, W/(m·K)) |
| 11 | Thickness | Opaque construction thickness, m |
| 12 | ThermalAbsorptance | Long-wave absorptance |
| 13 | SolarAbsorptance | Solar absorptance |
| 14 | VisiblAbsorptance | Visible absorptance |
| 15 | Direction | 0 unspecified / horizontal, 1 east, 2 south, 3 west, 4 north |

The names `Res` and `SubRes` are historical: do **not** substitute thermal resistance solely because of the names. Match the training-data convention. The toolkit preserves values without rescaling or converting them.

All numerical inputs must be finite and non-negative. Category values must match the table. SI is not calculated by the package; do not switch between shape-index formulas when using an existing checkpoint.

## Connections

- Node row `i` corresponds to row and column `i` of the adjacency matrix.
- The matrix is binary and symmetric: `1` means a component connection.
- Self-connections in the input diagonal are ignored. GATConv adds its own self-loops.
- An undirected connection is encoded as two directed edges for PyTorch Geometric. The bundled example therefore has 102 undirected connections / 204 directed edges.
- Keep component names and ordering with exported results; explanation indices refer to this order.

## Encoded model input

16 raw columns become **26 model features**:

1. Ten numerical values, in order: Area, SI, SubfaceArea, SubRes, SubSHGC, Res, Thickness, ThermalAbsorptance, SolarAbsorptance, VisiblAbsorptance.
2. Four construction indicators: exterior, interior, ground, roof.
3. Three boundary indicators: Outdoors, Surface, Ground.
4. Four subface indicators: none, window, door, both.
5. Five direction indicators: unspecified, east, south, west, north.

The checkpoint depends on this exact order. `bcgs.FEATURE_NAMES` exposes it.

## Excel input

Place two files in a directory:

```text
my-building/
  node.xlsx          First worksheet, no header, first 16 columns in the order above
  adjmatrix.xlsx     First worksheet, no header, N × N
```

```bash
bcgs validate my-building
bcgs predict my-building
```

Additional hourly columns in `node.xlsx` are ignored. No `energy_sum.xlsx`, weather file, or reference energy label is needed for this checkpoint. Changes of climate require a separately trained and validated model, rather than an extra input to this checkpoint.
