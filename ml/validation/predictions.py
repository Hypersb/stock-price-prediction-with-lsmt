"""Chronological out-of-sample prediction collection."""

import pandas as pd

from ml.validation.baselines import WalkForwardModelResult


def collect_predictions(results: list[WalkForwardModelResult]) -> pd.DataFrame:
    """Convert fold results to a date-sorted, fold-aware prediction table."""
    records: list[dict[str, object]] = []
    for result in results:
        if not (len(result.dates) == len(result.actual) == len(result.predicted)):
            raise ValueError("prediction dates, actuals, and predictions must align")
        for index, date in enumerate(result.dates):
            record = {
                "date": date,
                "fold": result.fold,
                "model": result.model_name,
                "task": result.task,
                "actual": result.actual[index],
                "predicted": result.predicted[index],
            }
            if result.probabilities is not None:
                record["probability"] = result.probabilities[index]
                record["predicted_class"] = int(result.predicted[index])
            records.append(record)
    frame = pd.DataFrame(records)
    if frame.empty:
        return frame
    frame["date"] = pd.to_datetime(frame["date"])
    if frame.duplicated(subset=["date", "fold", "model", "task"]).any():
        raise ValueError("duplicate prediction records are not allowed")
    return frame.sort_values(["date", "fold", "model"]).reset_index(drop=True)