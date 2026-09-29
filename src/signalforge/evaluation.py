"""Measured classification metrics and report figures."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def metrics(y, p, threshold: float = 0.5) -> dict:
    label = np.asarray(p) >= threshold
    return {
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "precision": float(precision_score(y, label, zero_division=0)),
        "recall": float(recall_score(y, label, zero_division=0)),
        "f1": float(f1_score(y, label, zero_division=0)),
        "accuracy": float(accuracy_score(y, label)),
        "log_loss": float(log_loss(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "confusion_matrix": confusion_matrix(y, label).tolist(),
    }


def choose_threshold(y, p) -> float:
    thresholds = np.linspace(0.05, 0.95, 91)
    return float(max(thresholds, key=lambda t: f1_score(y, p >= t, zero_division=0)))


def plots(y, probabilities: dict, selected: str, threshold: float, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    for kind in ["roc", "precision-recall"]:
        fig, ax = plt.subplots(figsize=(8, 5))
        for name, p in probabilities.items():
            if kind == "roc":
                x, values, _ = roc_curve(y, p)
            else:
                values, x, _ = precision_recall_curve(y, p)
            ax.plot(x, values, label=name, linewidth=2)
        ax.set(
            xlabel="False positive rate" if kind == "roc" else "Recall",
            ylabel="True positive rate" if kind == "roc" else "Precision",
            title=f"SignalForge • Held-out {kind}",
        )
        ax.legend()
        fig.tight_layout()
        fig.savefig(directory / f"{kind}.png", dpi=160)
        plt.close(fig)
    cm = confusion_matrix(y, probabilities[selected] >= threshold)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(cm, cmap="Blues")
    for (i, j), value in np.ndenumerate(cm):
        ax.text(
            j,
            i,
            str(value),
            ha="center",
            va="center",
            fontsize=20,
            color="white" if value > cm.max() / 2 else "black",
        )
    ax.set(
        xticks=[0, 1],
        yticks=[0, 1],
        xlabel="Predicted",
        ylabel="Actual",
        title=f"{selected} • Test confusion matrix",
    )
    fig.tight_layout()
    fig.savefig(directory / "confusion-matrix.png", dpi=160)
    plt.close(fig)
