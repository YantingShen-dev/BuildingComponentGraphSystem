"""Run after installing the package: python examples/quickstart.py"""

from bcgs import EnergyPredictor, load_example

building = load_example()
predictor = EnergyPredictor()
print(f"Components: {len(building.node_data)}")
print(f"Annual EUI: {predictor.predict(building):.4f} kWh/(m2*year)")

# Optional:
# explanation = predictor.explain(building, epochs=100)
# from bcgs.optimization import MaterialOptimizer
# solutions = MaterialOptimizer(predictor).optimize(building, population_size=20, generations=5)
