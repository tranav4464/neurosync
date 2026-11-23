"""Generate the publication figure from version-controlled public-data evidence."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "public_benchmark_summary.json"
OUTPUT = ROOT / "manuscript" / "figures" / "public_benchmark_confirmation.png"


def main() -> None:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    confirmation = payload["subject_results"][1:]
    subjects = [row["subject"] for row in confirmation]
    four = np.asarray([row["four"] for row in confirmation]) * 100
    six = np.asarray([row["six"] for row in confirmation]) * 100
    eight = np.asarray([row["eight"] for row in confirmation]) * 100

    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    figure, axes = plt.subplots(1, 2, figsize=(9.0, 3.7), constrained_layout=True)

    positions = np.asarray([4, 6, 8])
    for index, subject in enumerate(subjects):
        axes[0].plot(positions, [four[index], six[index], eight[index]], color="#90A4AE", alpha=0.7, lw=1)
    means = [four.mean(), six.mean(), eight.mean()]
    axes[0].plot(positions, means, "o-", color="#0D47A1", lw=2.5, label="Confirmation mean")
    axes[0].axhline(85, color="#2E7D32", ls="--", lw=1.2, label="85% target")
    axes[0].set(xticks=positions, xlabel="Selected EEG channels", ylabel="Held-out character accuracy (%)", ylim=(65, 102))
    axes[0].set_title("A. Channel-count ablation (A02–A08)", loc="left", fontweight="bold")
    axes[0].legend(frameon=False, loc="lower right")

    x = np.arange(len(subjects))
    axes[1].scatter(x - 0.10, six, color="#1565C0", label="6 channels", s=36)
    axes[1].scatter(x + 0.10, eight, color="#EF6C00", label="8 channels", s=36)
    for index in x:
        axes[1].plot([index - 0.10, index + 0.10], [six[index], eight[index]], color="#B0BEC5", lw=1)
    axes[1].axhline(85, color="#2E7D32", ls="--", lw=1.2)
    axes[1].set(xticks=x, xticklabels=subjects, xlabel="Locked confirmation participant", ylabel="Held-out character accuracy (%)", ylim=(80, 102))
    axes[1].set_title("B. Paired six- vs eight-channel result", loc="left", fontweight="bold")
    axes[1].legend(frameon=False, loc="lower right")

    figure.suptitle("NeuroSync public ALS-cohort confirmation at ten repetitions", fontweight="bold")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(figure)
    print(OUTPUT)


if __name__ == "__main__":
    main()
