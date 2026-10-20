"""CPU-first inference with the repository's original Enhanced GAT checkpoint."""

from pathlib import Path

import numpy as np
import torch

from .data import ASSETS, FEATURE_NAMES, BuildingGraph
from .model import GCN


class EnergyPredictor:
    """Load once, then predict or explain multiple buildings."""

    def __init__(self, checkpoint=None, device="cpu"):
        self.device = torch.device(device)
        self.checkpoint = Path(checkpoint) if checkpoint else ASSETS / "energy_merged_EUIGCN9.pth"
        self.model = GCN(num_node_features=len(FEATURE_NAMES)).to(self.device)
        state = torch.load(self.checkpoint, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.model.eval()

    def predict(self, building: BuildingGraph) -> float:
        graph = building.to_pyg().to(self.device)
        batch = torch.zeros(graph.num_nodes, dtype=torch.long, device=self.device)
        with torch.inference_mode():
            prediction = self.model(graph.x, graph.edge_index, batch).item()
        if not np.isfinite(prediction):
            raise ValueError("The model produced a non-finite prediction. Check the input ranges.")
        return float(prediction)

    def explain(self, building: BuildingGraph, epochs=100, seed=42):
        """Return unsigned feature/edge masks, not physical effects or causal estimates."""
        from torch_geometric.explain import Explainer, GNNExplainer

        if isinstance(epochs, bool) or not isinstance(epochs, int) or not 1 <= epochs <= 1000:
            raise ValueError("epochs must be an integer between 1 and 1000.")
        if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
            raise ValueError("seed must be an integer between 0 and 4294967295.")
        graph = building.to_pyg().to(self.device)
        if graph.edge_index.shape[1] == 0:
            raise ValueError("Edge explanations require at least one component connection.")
        batch = torch.zeros(graph.num_nodes, dtype=torch.long, device=self.device)
        cuda_devices = [self.device.index or 0] if self.device.type == "cuda" else []
        with torch.random.fork_rng(devices=cuda_devices):
            torch.manual_seed(seed)
            explainer = Explainer(
                model=self.model,
                algorithm=GNNExplainer(epochs=epochs),
                explanation_type="model",
                node_mask_type="attributes",
                edge_mask_type="object",
                model_config={"mode": "regression", "task_level": "graph", "return_type": "raw"},
            )
            explanation = explainer(graph.x, graph.edge_index, batch=batch)
        masks = explanation.node_mask.detach().cpu().numpy()
        edge_matrix = np.zeros((graph.num_nodes, graph.num_nodes))
        for (source, target), value in zip(
            graph.edge_index.cpu().T.tolist(), explanation.edge_mask.detach().cpu().tolist()
        ):
            edge_matrix[source, target] = value
        edge_matrix = (edge_matrix + edge_matrix.T) / 2
        return {
            "method": "GNNExplainer attribute and edge masks",
            "epochs": epochs,
            "seed": seed,
            "feature_names": list(FEATURE_NAMES),
            "node_importance": {
                "Node_ID": {str(i): i for i in range(graph.num_nodes)},
                **{
                    name: {str(i): float(masks[i, j]) for i in range(graph.num_nodes)}
                    for j, name in enumerate(FEATURE_NAMES)
                },
            },
            "feature_importance": dict(zip(FEATURE_NAMES, masks.mean(axis=0).astype(float).tolist())),
            "edge_matrix": edge_matrix.tolist(),
        }
