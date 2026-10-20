"""Small command line interface: bcgs demo / validate / predict / explain / optimize / serve."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .data import BuildingGraph, FEATURE_NAMES, load_example
from .predict import EnergyPredictor


def _building(path):
    return BuildingGraph.from_excel(path) if Path(path).is_dir() else BuildingGraph.from_json(path)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="bcgs", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("demo", "validate", "predict", "explain", "optimize"):
        command = commands.add_parser(name)
        if name != "demo":
            command.add_argument("input", help="Building JSON or directory with node.xlsx / adjmatrix.xlsx.")
        if name != "validate":
            command.add_argument("--checkpoint", help="Optional checkpoint with the bundled Enhanced GAT architecture.")
            command.add_argument("--device", default="cpu")
        command.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout.")
        if name == "demo":
            command.add_argument("--export-input", type=Path, help="Save the bundled example for editing.")
        if name in ("explain", "optimize"):
            command.add_argument("--seed", type=int, default=42)
        if name == "explain":
            command.add_argument("--epochs", type=int, default=100)
        if name == "optimize":
            command.add_argument("--population-size", type=int, default=20)
            command.add_argument("--generations", type=int, default=5)
            command.add_argument("--wall-type", type=int, default=0, help="Zero-based row index in wall_select.xlsx.")
            command.add_argument("--materials-dir", type=Path)
    serve = commands.add_parser("serve", help="Start the optional HTTP API.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=5000, type=int)
    serve.add_argument("--checkpoint")
    serve.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)
    try:
        if args.command == "serve":
            from .server import create_app
            create_app(args.checkpoint, args.device).run(host=args.host, port=args.port, threaded=False)
            return 0
        building = load_example() if args.command == "demo" else _building(args.input)
        graph = building.to_pyg()
        result = {"nodes": graph.num_nodes, "directed_edges": graph.num_edges, "features": len(FEATURE_NAMES)}
        if args.command == "validate":
            result["valid"] = True
        else:
            predictor = EnergyPredictor(args.checkpoint, args.device)
            result["prediction"] = predictor.predict(building)
            result["target"] = "annual EUI"
            result["unit"] = "kWh/(m²·year)"
            if args.command == "demo" and args.export_input:
                args.export_input.parent.mkdir(parents=True, exist_ok=True)
                building.to_json(args.export_input)
            elif args.command == "explain":
                result["explanation"] = predictor.explain(building, args.epochs, args.seed)
            elif args.command == "optimize":
                from .optimization import MaterialOptimizer
                result["pareto_solutions"] = MaterialOptimizer(predictor, args.materials_dir).optimize(
                    building, wall_type=args.wall_type, population_size=args.population_size,
                    generations=args.generations, seed=args.seed,
                )
        text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            # Keep stdout portable on Windows consoles; exported files remain UTF-8.
            print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except ImportError as exc:
        print(f"bcgs: {exc}. Install optional features with: pip install '.[web]'", file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"bcgs: {exc}", file=sys.stderr)
        return 2
