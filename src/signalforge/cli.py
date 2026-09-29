"""Command line workflows share exactly the same production modules as the API."""

import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(prog="signalforge")
    parser.add_argument(
        "command",
        choices=["train", "evaluate", "predict", "monitor", "retrain", "validate-data", "promote"],
    )
    parser.add_argument("--input", type=Path, default=Path("data/raw/churn.csv"))
    parser.add_argument("--output", type=Path, default=Path("predictions.csv"))
    parser.add_argument("--evaluation", type=Path)
    args = parser.parse_args()
    if args.command == "train":
        from signalforge.training import train

        result = train(data_path=args.input)
    elif args.command == "validate-data":
        from signalforge.data import ingest, load, validate

        result = validate(load(ingest(args.input)))
    elif args.command == "promote":
        from signalforge.registry import promote

        result = promote(
            Path("models/candidate"),
            evaluation=pd.read_csv(args.evaluation) if args.evaluation else None,
        )
    elif args.command == "retrain":
        from signalforge.retraining import retrain

        if args.evaluation is None:
            parser.error("retrain requires --evaluation with a disjoint labeled window")
        result = retrain(args.input, args.evaluation)
    else:
        from signalforge.inference import Predictor

        predictor = Predictor()
        if args.command == "evaluate":
            result = predictor.metadata
        elif args.command == "predict":
            frame = pd.read_csv(args.input)
            predictions = predictor.predict(frame)
            pd.json_normalize(predictions).to_csv(args.output, index=False)
            result = {"rows": len(predictions), "output": str(args.output)}
        else:
            from signalforge.monitoring import monitor

            result = monitor(predictor.reference, pd.read_csv(args.input))
    print(json.dumps(result, indent=2))
