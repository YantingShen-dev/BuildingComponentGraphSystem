"""Optional single-port API used by the Vue interface."""

from threading import RLock

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from .data import ASSETS, BuildingGraph, load_example
from .predict import EnergyPredictor


def create_app(checkpoint=None, device="cpu"):
    app = Flask(__name__)
    CORS(app)
    predictor = EnergyPredictor(checkpoint, device)
    model_lock = RLock()  # PyG explanation hooks must not overlap other model calls.

    @app.errorhandler(ValueError)
    @app.errorhandler(BadRequest)
    def invalid_input(error):
        return jsonify(success=False, error=str(error)), 400

    @app.get("/health")
    def health():
        return jsonify(status="healthy", service="BCGS", device=str(predictor.device))

    @app.get("/example")
    def example():
        return jsonify(load_example().to_dict())

    @app.get("/materials/wall_select.xlsx")
    def wall_materials():
        return send_file(ASSETS / "materials" / "wall_select.xlsx")

    @app.post("/predict")
    def predict():
        payload = request.get_json()
        building = BuildingGraph.from_dict(payload)
        with model_lock:
            result = {"prediction": predictor.predict(building)}
            if payload.get("explain", False):
                result["explanation"] = predictor.explain(
                    building, epochs=payload.get("explainer_epochs", 100), seed=payload.get("seed", 42)
                )
        return jsonify(result)

    @app.post("/optimize")
    def optimize():
        from .optimization import MaterialOptimizer
        payload = request.get_json()
        building = BuildingGraph.from_dict(payload)
        if payload.get("stream", False):
            raise ValueError("This API returns JSON; set stream=false.")
        with model_lock:
            solutions = MaterialOptimizer(predictor).optimize(
                building, wall_type=payload.get("wall_type", 0),
                population_size=payload.get("population_size", 20),
                generations=payload.get("generations", 5), seed=payload.get("seed", 42),
            )
        return jsonify(success=True, pareto_solutions=solutions)

    return app
