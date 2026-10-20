"""Public BCGS API. No web server is needed for inference."""

from .data import BuildingGraph, FEATURE_NAMES, RAW_COLUMNS, load_example
from .predict import EnergyPredictor

__version__ = "0.2.1"
__all__ = ["BuildingGraph", "EnergyPredictor", "FEATURE_NAMES", "RAW_COLUMNS", "load_example"]
