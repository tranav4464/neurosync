"""Convert official BCI Competition III Dataset II training ASCII into NPZ."""

from __future__ import annotations

import argparse

from neurosync_p300.competition_data import load_competition_iii_train_ascii
from neurosync_p300.data import save_npz


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, help="folder containing Subject_*_Train_*.txt")
    parser.add_argument("--output", default="results/competition_iii_subject_a_train.npz")
    args = parser.parse_args()
    dataset = load_competition_iii_train_ascii(args.directory)
    save_npz(dataset, args.output)
    print({"epochs": len(dataset.epochs), "channels": dataset.channel_names, "trials": dataset.trial_count, "output": args.output})


if __name__ == "__main__":
    main()
